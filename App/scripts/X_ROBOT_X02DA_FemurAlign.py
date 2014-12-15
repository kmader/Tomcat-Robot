# Femur Align
# 02232010
# Meant as a library/standalone tool for femur alignment
# Goes through centering, finding top, finding bottom

import wx
import wx.stc
import wx.lib.plot
import time
import datetime
from math import *
import glob
from numpy import *
from scipy.optimize import leastsq
import Image
import os,sys,socket
import cPickle
import pdb
from optparse import OptionParser

sys.path.append (os.path.expandvars ("$SLSBASE/sls/bin/"))
modules ={u'X_ROBOT_X02DA_AALib': [1,
                          'Alignment Library',
                          u'../../../../../../../../XX_ROBOT_X02DA_AALib.py']}

from X_ROBOT_X02DA_Autoalign_Stage import alignStage
import X_ROBOT_X02DA_database as tomcatDB
try:
    import X_ROBOT_X02DA_robotCommon
except:
    print "Initial robotCommon not found!"
    try:
        sys.path.insert (0, os.path.expandvars ("$SLSBASE/sls/bin/"))
        import  X_ROBOT_X02DA_robotCommon
    except:
        sys.exit (1)
        
sampleThreshLib={}
sampleThreshLib['From Image']=(-1,-1)
sampleThreshLib['Embedded Bone @ 28keV']=((3.61113315+3.04723031)/2,  (3.61113315-3.04723031)/2) # +1.5 std to isolate cortical bone

sampleThreshLib['Mouse Femur @ 20keV']=(1.4,.82)
sampleThreshLib['Mouse Femur @ 20keV']=(1.2,.80)
sampleThreshLib['Metal Support @ 20keV']=(3.25,1.0)
sampleThreshLib['Metal Support @ 20keV']=(25,22.5)
sampleThreshLib['Rat Brain @ 20keV']=(1.0,0.5)

class __LoggingPipe__:
    def __init__(self,logFileName='script',dirName='Robot_Logs'):
        try:
            os.listdir( os.path.expandvars ("$HOME/"+dirName+"/"))
        except:
            os.mkdir( os.path.expandvars ("$HOME/"+dirName+"/"))
        cday=datetime.date.today()
        
        self.logFileName=os.path.expandvars("$HOME/"+dirName+"/"+logFileName+"."+str(cday)+".log")
        self.write('\n'+time.asctime()+':'+logFileName+' freshly started'+'\n',0)
    def write(self,myStr,indent=1):
        tFile=open(self.logFileName,'a+')
        tFile.write('\t'*indent+myStr)
        tFile.close()


# Pretty clever if I don't say so myself, make epics channels look
# like a dictionary
class epicsDict:
    def __init__(self,nameMap,calculated=True):
        self._nameMap=nameMap
        self.epicsMap={}
        self.aktuell=True
        self.calculated=calculated # if values need to be recalculated after an 
        # an input channel is changed
        
        # Create Epics Channels
        for cName in self._nameMap.keys():
            if type(self._nameMap[cName])==type(''):
                self.epicsMap[cName]=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(self._nameMap[cName])
            else:
                self.epicsMap[cName]=X_ROBOT_X02DA_robotCommon.FakeRoboEpicsChannel(cName,0,0,None)
                self.epicsMap[cName].putVal(self._nameMap[cName])
            
    def keys(self):
        return self.epicsMap.keys()
    def has_key(self,cKey):
        return self.epicsMap.has_key(cKey)
    def __getitem__(self,gArgs):
        # handle [] requests
        if self.epicsMap.has_key(gArgs):
            # If a value has been changed, recalc
            # before reading outputs
            if (not self.aktuell) and self.calculated: self.recalc()
            return self.epicsMap[gArgs].getVal()
        else:
            print 'Error : EpicsDict Key-'+gArgs+' not found'
            return 0
    def __setitem__(self,gArgs,gVal):
        if self.epicsMap.has_key(gArgs):
            if (self.epicsMap[gArgs].getVal()!=gVal):
                self.epicsMap[gArgs].putVal(gVal)
                self.aktuell=False
        else:
            print 'Error :: KEY NOT FOUND '+str(gArgs)
    def aktuellize(self):
        self.aktuell=True
    def recalc(self):
        if self.has_key('calc'):
            self['calc']=1
            while self['calc']>0:
                time.sleep(0.1)
        else:
            print 'Missing ReCalc Field...'
        self.aktuellize()
        
    def __str__(self):
        cacheMap={}
        for cName in self.epicsMap.keys():
            cacheMap[cName]=self[cName]
        return str(cacheMap)

class kImage:
    # Image Processing Libarary Moved into Alignment Server
    def __init__(self):
        snapPrefix='X02DA-SCAN-SNAP'
        impMap={}
        impMap['readMode']=snapPrefix+':READMODE' # 0 is raw, 1 mask-values, 2 masked image
        impMap['maskMode']=snapPrefix+':MASKMODE' # 0 default, -1 values under thresh, 1 values overthresh
        impMap['minPCT']=snapPrefix+':MINPCT'
        impMap['cutoff']=snapPrefix+':CUTOFF'
        impMap['thavg']=snapPrefix+':THAVG'
        impMap['thstd']=snapPrefix+':THSTD'
        impMap['recalc']=snapPrefix+':RECALC'
        impMap['useMat']=1
        impMap['% Air']=snapPrefix+':PCTUND'
        impMap['% Metal']=snapPrefix+':PCTOVR'
        impMap['% Bone']=snapPrefix+':PCTBET'
        impMap['% Saturated']=snapPrefix+':PCTSAT'
        impMap['Mean']=snapPrefix+':IMAVG'
        impMap['Std']=snapPrefix+':IMSTD'
        impMap['Sample Mean Width']=snapPrefix+':WIDTH'
        impMap['Sample Top']=snapPrefix+':TOP'
        impMap['Sample Bottom']=snapPrefix+':BOTTOM'
        impMap['Sample Offset']=snapPrefix+':XOFFSET'
        impMap['Sample Y Position']=snapPrefix+':YOFFSET'
        impMap['Sample Orientation']=snapPrefix+':THETA'
        impMap['Sample Tilt']=snapPrefix+':THETAV'
        self._impResults=epicsDict(impMap)
        
        
    def isCentered(self,cTol,useGonio=False):
        # Function to determine if the object is centered

        xyCentered=(abs(self._impResults['Sample Offset'])<cTol)
        if useGonio:
            # only count quarter as much (basically less than a deg isch guet)
            slantPixels=sin(self._impResults['Sample Orientation']*pi/180.0)*512
            rCentered=(abs(slantPixels)<cTol)
        else:
            rCentered=True
        return (xyCentered and rCentered)
    def saturationCheck(self,cutOff=60000):
        self._impResults['cutoff']=cutOff
        return 'Percent Saturated:'+str(round(self._impResults['% Saturated']*100)/100.0)+'%'
    def threshold(self,_stdR=1.5,useMat=''):
        stdValue=-1
        if sampleThreshLib.has_key(useMat):
            (mValue,stdValue)=sampleThreshLib[useMat]
            stdR=1 # Always 1 with materials
            self._impResults['useMat']=1
            print 'Using Material :'+useMat
        else:
            stdR=_stdR
            self._impResults['useMat']=0
            print 'Not Using Material'
        
            
        self._impResults['thavg']=mValue
        self._impResults['thstd']=stdR*stdValue
        return self
    def matchImage(self,otherImage,toFlip=True):
        # Does a correlation between two images
        print 'Not yet Implemented'
        return 0
    
    def CleanMask(self,mStep=3,minPct=8.0): 
        # Clean Mask clears rows if the neighboring rows are also empty
        print 'Not yet implemented'    
    def fitVcyl(self,mStep=30):
        print 'Automatically Implemented'
    
    def calcAngleOffset(self):
        print 'Automatic'
        return cAng

    
faVersion=20101124
# Added code to check the goniometer alignment    
    
class FemurAlign:
    def __init__(self,opt=[]):
        print "Class Femur Align!!"
        
        self.cmbMaterial='Mouse Femur @ 20keV'
        
        self.myStage=alignStage()
        self.cImg=100
        self.cKey=''
        self.cThresh=1.0
        self.dRange=[]
        self.batchEye=-2
        self.previewMode=0
        self.myStage.SPECtoSNAP()
        self.xBin=self.myStage.xBinChan.getVal()
        self.yBin=self.myStage.yBinChan.getVal()
        self.oldImageName=''
        self.oldFlatName=''
        self.oldThresh=[]
        self.oldMat=''
        self.searchRunning=0
        self.flatLoadTime=-1
        self.flatLifetime=180
        self.dSize=(self.myStage.dimxChan.getVal(),self.myStage.dimyChan.getVal())
        if opt.exptime>0:
            nExpTime=float(opt.exptime)
            self.myStage.snapExpTime.putVal(nExpTime)
            print 'Exposure Time Updated: '+str(nExpTime)
        self.topTol=opt.toptol/self.yBin
        self.botTol=opt.bottol/self.yBin
        self.centTol=opt.centtol/self.xBin
        self.topIter=opt.topiter
        self.botIter=opt.botiter
        self.centIter=opt.centiter
        self.topJump=opt.topjump/self.yBin
        self.botJump=opt.botjump/self.yBin
        self.thickSteps=opt.thicksteps
        self.minPctBone=opt.minpctbone
        self.baseImage='Snap'
        self.AlignKeys={}
        self.debugMode=opt.debug
        self.saveMode=opt.save
        self.kImageObj=kImage()
        self.kImageObj.threshold(useMat=self.cmbMaterial)
        self.kImageObj._impResults['minPCT']=0.005 # 1% should be enough
        if opt.server>0:
            self.Server()
        #else:
        #    self.AlignFemur()
        #   ak=self.AlignKeys.keys()
##            ak.sort()
##            for cKey in ak:
##                print cKey+'\t'+str(self.AlignKeys[cKey])
        
    def Server(self):
        self.myStage.aliveChan.putVal(1)
        self.myStage.killChan.putVal(0)
        while self.myStage.killChan.getVal()<1:
            self.myStage.aliveChan.putVal(1)
            while self.myStage.alignmentChan.getVal()<1:
                self.myStage.aliveChan.putVal(1)
                if self.myStage.killChan.getVal()>0: 
                    self.myStage.aliveChan.putVal(0)
                    break
                
                time.sleep(0.5)
                # Code to Verify the Goniometer Alignment
                if self.myStage.gAlignmentChan.getVal()>0:
                    # Check Goniometer Alignment
                    # Zero is the top of the holder (the top of the holder is just above the top of the screen
                    self.myStage.RawYValue.putVal(0)
                    self.myStage.RealXValue.putVal(0)
                    self.myStage.shutterChan.putVal(1)
                    self.kImageObj.threshold(useMat='Metal Support @ 20keV')
                    self.myStage.waitMoving()
                    for cAng in range(0,91,90):
                        rootName=self.baseImage+'_GC%02d' % cAng
                        self.myStage.dSnapName=rootName
                        self.myStage.RotStage(cAng,False)
                        self.myStage.waitMoving()
                        self.doLoadSnap()
                        if (self.UpdateImpResults()==False):
                            X_ROBOT_X02DA_robotCommon.EMESSAGE('Stage Not Found')
                            self.myStage.pauseChan.putVal(1) # Pause the sequencer until the issue is resolved
                            break
                        if abs(self.kImageObj._impResults['Sample Tilt'])>2.0:
                            print 'ERROR:: Stage NOT FLAT!!!!'
                            X_ROBOT_X02DA_robotCommon.EMESSAGE('Stage Not Flat : '+str(self.kImageObj._impResults['Sample Tilt']))
                            self.myStage.gAlignmentChan.putVal(-2)
                            break
                        if abs(self.kImageObj._impResults['Sample Y Position']-54)>50:
                            print 'ERROR:: Stage Y Value too HIGH'
                            X_ROBOT_X02DA_robotCommon.EMESSAGE('Stage Y Value Too High: '+str(self.kImageObj._impResults['Sample Y Position']))
                            self.myStage.gAlignmentChan.putVal(-3)
                            break
                    self.myStage.shutterChan.putVal(0)
                    if self.myStage.gAlignmentChan.getVal()>0:
                        # if everything went well then continue
                        self.myStage.gAlignmentChan.putVal(0)
                        
            
            self.myStage.waitMoving()
            # Run alignment code
            cName=self.myStage.SPECtoSNAP()
            curSample=[cName,'',0,[]]
            try:
                #curSample=tomcatDB.xdGetSample(cName)
                print 'DATABASE NOCHMALS FUCKED'
            except:
                curSample=[cName,'',0,[]]
            isGuet=self.AlignFemur()
            self.myStage.RotStage(0,False)
            self.myStage.waitMoving()
            curSample[3]=[self.myStage.SetHomePos()]
            ak=self.AlignKeys.keys()
            ak.sort()
            curSample[1]=''
            
            ak=['0-BoneLength','XXGon','ZZGon','4-FemThickTime']
            for cKey in ak:
                if self.AlignKeys.has_key(cKey):
                    curSample[1]+='\n'+cKey+'\t'+str(self.AlignKeys[cKey])
            try:
                #tomcatDB.xCreateSample(curSample[0],curSample[1][0:254],curSample[3])
                print 'Temporarily Disabled TomcatDB'
            except:
                print 'Error : Writing to Tomcat Database Failed!'
            if self.saveMode:
                try:
                    os.listdir( os.path.expandvars ("$HOME/AlignedFemurs/"))
                except:
                    os.mkdir( os.path.expandvars ("$HOME/AlignedFemurs/"))
        
                outname=os.path.expandvars("$HOME/AlignedFemurs/"+self.baseImage+".log")
                tFile=open(outname,'w+')
                ak=self.AlignKeys.keys()
                ak.sort()
                for cKey in ak:
                    tFile.write('\n'+cKey+'\t'+str(self.AlignKeys[cKey]))
                tFile.close()
                
            self.PushSettings()
            self.myStage.alignmentChan.putVal(0)
            
    def PushSettings(self):
        nAng=self.AlignKeys['MeasurementAngle']
        self.myStage.specRotChan.putVal(nAng)
        self.myStage.specRotStopChan.putVal(nAng+180)
    def AlignFemur(self):
        print 'Starting Alignment of Femur'
        self.myStage.shutterChan.putVal(1)
        stime=time.time()
        self.myStage.RotStage(0,False)
        self.baseImage=self.myStage.snapNameChan.getVal()
        self.kImageObj.threshold(useMat=self.cmbMaterial)
        self.AlignKeys={}
        self.AlignKeys['FemurBackbone']={}
        # Start at 0 position
        
        print 'Rough Centering Femur in FOV'
        self.CenterFemur(self.centTol*10,self.centIter,useGonio=False)
        self.AlignKeys['1-CenterTime']=time.time()-stime
        self.FindTop()
        self.AlignKeys['2-FindTopTime']=time.time()-stime

        self.FindBottom()
        self.AlignKeys['2-FindBotTime']=time.time()-stime
        print self.AlignKeys['FemurBackbone']
        nVals=[self.AlignKeys['TopY_Val'],self.AlignKeys['BotY_Val']]
        boneLength=max(nVals)-min(nVals)
        imgRawY=boneLength*0.56+min(nVals)
        self.AlignKeys['0-BoneLength']=round(boneLength)
        self.AlignKeys['MeasurementYVal']=imgRawY
        self.myStage.RawYValue.putVal(imgRawY)
        # Set 56% to top of field of view (instead of center)
        # Bump the stage down
        self.myStage.BumpImage(0,-512) # 1024 pixels half field of view
        bPos=min([(abs(fbp-(imgRawY)),fbp) for fbp in self.AlignKeys['FemurBackbone'].keys()])[1]
        imgRawX=self.AlignKeys['FemurBackbone'][bPos]
        self.myStage.RawXValue.putVal(imgRawX)
        self.CenterFemur(self.centTol,self.centIter,useGonio=True)
        self.AlignKeys['3-CenterTime']=time.time()-stime
        self.AlignKeys['XXGon']=self.myStage.goXXChan.getVal()
        self.AlignKeys['ZZGon']=self.myStage.goZZChan.getVal()
        #self.FemurThickness(self.thickSteps)
        self.AlignKeys['MeasurementAngle']=0 # Faster
        self.AlignKeys['4-FemThickTime']=time.time()-stime
        print self.AlignKeys
        return 0
    def FindBone(self,steps=6,jumpSize=0.35):
        # Find the bone when nothing is inside the field of view
        # Use BotJump as bumping criteria
        print 'Bone Not Found!, Starting Looking Routine'
        for i in range(1,steps+1):
            print 'Jump Positive'
            self.myStage.BumpImage(self.botJump*steps*jumpSize)
            self.doLoadSnap()
            
            if self.UpdateImpResults(): break
            self.myStage.BumpImage(-self.botJump*steps*jumpSize)
            print 'Jump Negative'
            self.myStage.BumpImage(-self.botJump*steps*jumpSize)
            self.doLoadSnap()
            
            if self.UpdateImpResults(): break
            self.myStage.BumpImage(self.botJump*steps*0.6)
    def FemurThickness(self,stepSize=10):
        # Finds the thickest point by scanning angles at stepsize
        # and fitting a sinesoid to the data and then using the phase
        print 'Finding Thickness Map'
        rootName=self.baseImage+'_TH'
        outMat=[];
        for cAng in range(0,181,stepSize):
            self.myStage.RotStage(cAng,False)
            self.myStage.dSnapName=rootName+'_'+str(cAng)
            self.doLoadSnap()
            self.UpdateImpResults() 
            outMat.append([cAng,self.kImageObj._impResults['Sample Mean Width']])
        print outMat
        self.AlignKeys['ThicknessMap']=outMat
        bd=array(outMat)
        e = lambda v, x,y: (v[0]*cos((x+v[1])*pi/180)+v[2]-y)
        x=bd[:,0]
        y=bd[:,1]
        vo=[max(y)-mean(y),0,mean(y)]
        v, success = leastsq(e, vo, args=(x,y), maxfev=10000)
        nAng=v[1]%360
        while nAng>0: nAng+=-180
        # don't need anymore since the goniometer is well mounted
        #if nAng<-90: nAng=-90
        self.AlignKeys['MeasurementAngle']=nAng
        self.myStage.RotStage(nAng,False)
    def CenterFemur(self,cTol,cIter,useGonio=False):
        print 'Aligning Femur in XX and ZZ'
        
        
        for cAng in range(0,91,90):
            self.AlignKeys['CenterIterations']=0
            self.myStage.RotStage(cAng,False)
            rootName=self.baseImage+'_C'+str(cAng)
            self.CenterObj(rootName,cTol,cIter,useGonio=useGonio)
        self.myStage.SetHomePos()
    def CenterObj(self,rootName,cTol=10,cIter=20,useGonio=False,tiltMax=1.0):
        self.myStage.dSnapName=rootName
        self.doLoadSnap()
        if (self.UpdateImpResults()==False): self.FindBone() 
        while (not self.kImageObj.isCentered(cTol,useGonio)) and (self.AlignKeys['CenterIterations']<cIter):
            self.myStage.BumpImage(self.kImageObj._impResults['Sample Offset'])
            if useGonio:
                tiltAng=self.kImageObj._impResults['Sample Orientation']
                # Don't waste huge amounts of time tilting
                if tiltAng>tiltMax: tiltAng=tiltMax
                if tiltAng<-tiltMax:tiltAng=-tiltMax
                self.myStage.TiltImage(tiltAng)    
            self.doLoadSnap()
            if (self.UpdateImpResults()==False): self.FindBone() 
            self.AlignKeys['CenterIterations']+=1
            self.myStage.dSnapName=rootName
            if self.debugMode>0: self.myStage.dSnapName+='_'+str(self.AlignKeys['CenterIterations'])
            self.AlignKeys[self.myStage.GetWChan().pvName]=self.myStage.GetWChan().getVal()
    def FindTop(self):
        print 'Finding Top!'
        self.AlignKeys['TopIterations']=0
        rootName=self.baseImage+'_T'
        self.myStage.dSnapName=rootName
        self.myStage.RotStage(0,False)
        time.sleep(0.1)
        self.doLoadSnap()
        self.UpdateImpResults()
        while (self.kImageObj._impResults['Sample Top']<self.topTol) and (self.AlignKeys['TopIterations']<self.topIter):
            self.myStage.BumpImage(self.kImageObj._impResults['Sample Offset'],0)
            self.AlignKeys['FemurBackbone'][self.myStage.RawYValue.getVal()]=self.myStage.RawXValue.getVal()
            stageMoved=self.myStage.BumpImage(0,-self.topJump)
            if stageMoved:
                self.doLoadSnap()
            self.AlignKeys['TopIterations']+=1
            while (self.UpdateImpResults()!=True) & (self.AlignKeys['TopIterations']<self.topIter):
                print 'Error : Sample Lost, Backtracking'
                self.myStage.BumpImage(0,self.topJump/2)
                self.doLoadSnap()
                self.AlignKeys['TopIterations']+=1
            
            self.myStage.dSnapName=rootName
            if self.debugMode>0: self.myStage.dSnapName+='_'+str(self.AlignKeys['TopIterations'])
        if self.kImageObj._impResults['Sample Top']>=self.topTol:
            print 'Finding Top Successful!!!!!!!'
        else:
            print 'Finding Top Failed!!!!!!!'
            print 'Using Current Position as Top (works for large bones)'
            
        self.AlignKeys['TopY_Pix']=self.kImageObj._impResults['Sample Top']
        # Move the object to the center
        offsetPix=(self.AlignKeys['TopY_Pix']-self.dSize[1]/2.0)
        self.myStage.BumpImage(0,offsetPix)
        time.sleep(0.5)
        self.AlignKeys['TopY_Val']=self.myStage.RawYValue.getVal()
        print 'Finding Top Successful '+str(self.AlignKeys['TopY_Val'])+' offset of '+str(self.AlignKeys['TopY_Pix'])
        self.myStage.PutHomePos()
        
    def FindBottom(self):
        print 'Finding Bottom!'
        self.AlignKeys['BottomIterations']=0
        rootName=self.baseImage+'_B'
        self.myStage.dSnapName=rootName
        self.myStage.RotStage(0,False)
        time.sleep(0.5)
        self.doLoadSnap()
        self.UpdateImpResults()
        while (self.kImageObj._impResults['Sample Bottom']>self.botTol) and (self.AlignKeys['BottomIterations']<self.botIter):
            self.myStage.BumpImage(self.kImageObj._impResults['Sample Offset'],0)
            self.AlignKeys['FemurBackbone'][self.myStage.RawYValue.getVal()]=self.myStage.RawXValue.getVal()
            stageMoved=self.myStage.BumpImage(0,self.botJump)
            if stageMoved:
                self.doLoadSnap()
            self.AlignKeys['BottomIterations']+=1
            while (self.UpdateImpResults()!=True) & (self.AlignKeys['BottomIterations']<self.botIter):
                print 'Error : Sample Lost, Backtracking'
                self.myStage.BumpImage(0,-self.botJump/2)
                self.doLoadSnap()
                self.AlignKeys['BottomIterations']+=1
            self.myStage.dSnapName=rootName
            if self.debugMode>0: self.myStage.dSnapName+='_'+str(self.AlignKeys['BottomIterations'])
        if self.kImageObj._impResults['Sample Bottom']<=self.botTol:
            print 'Finding Bot Success!!!!!!!'
        else:
            print 'Finding Bot Failed!!!!!!!'
            print 'Using Current Position as Bottom (works for large bones)'
        self.AlignKeys['BotY_Pix']=self.kImageObj._impResults['Sample Bottom']
        offsetPix=(self.AlignKeys['BotY_Pix']-self.dSize[0]/2.0)
        self.myStage.BumpImage(0,offsetPix)
        time.sleep(0.5)
        
        self.AlignKeys['BotY_Val']=self.myStage.RawYValue.getVal()
        
        print 'Finding Bottom Successful '+str(self.AlignKeys['BotY_Val'])+' offset of '+str(self.AlignKeys['BotY_Pix'])
    
        self.myStage.PutHomePos()
        
    def UpdateImpResults(self):
        theQuays=self.kImageObj._impResults.keys()
        theQuays.sort()
        outText=''
        worked=True
        if self.kImageObj._impResults['Sample Orientation']==720:
            worked=False
        if self.kImageObj._impResults['% Bone']<self.minPctBone:
            worked=False
            print 'Failed, Too Little Bone : have '+str(self.kImageObj._impResults['% Bone'])+' need '+str(self.minPctBone)
        for cKey in theQuays:
            outText+=cKey+' : '+str(self.kImageObj._impResults[cKey])+'\n'
        
        print outText
        return worked
    def flatIsLoaded(self,lifetime=''):
        if lifetime=='': lifetime=self.flatLifetime
        if (time.time()-self.flatLoadTime)>lifetime: self.doLoadFlatSnap()
    def doLoadSnap(self):
        if self.flatIsLoaded()==False:
            self.doLoadFlatSnap()
            #self.doJustLoadFlat()    
        
        self.myStage.Snap() # Should be SnapTemp
        #pdb.set_trace()
        
        ## When using old camera server it is important to load the image 
        ## every time, but now not so much
        #self.kImageObj=kImage()
        self.clearCache()
    def doLoadFlatSnap(self):
        self.myStage.SnapFlatField()
        satPct=self.kImageObj._impResults['% Saturated']
        
        print 'Current Flat Mean Value : '+str(satPct)
        if satPct>1.0: X_ROBOT_X02DA_robotCommon.EMESSAGE('Flat Image Saturated::'+str(satPct))
        self.flatLoadTime=time.time()
   
    def clearCache(self):
        self.oldImageName=''
        self.oThresh=[]
        self.oMat=''
    def doThreshImage(self,cThresh,matName):
        if (cThresh==self.oThresh) and (matName==self.oMat):
            return 1
        self.kImageObj.threshold(cThresh,matName).fitVcyl(4)
        self.oThresh=cThresh
        self.oMat=matName
        self.UpdateImpResults()
        return 0
        
    def doLoadImage(self,reload=True,imValue=-1):	
        if imValue<0: imValue=self.imgSpin.GetValue()
        if reload:
            self.cImg=self.cKey+self.imgList[self.cKey][imValue]+'.tif'
            self.doLoadImageData(self.cImg)
        dSize=self.kImageObj.size
        self.myStage.xPix=dSize[0]
        self.myStage.yPix=dSize[1]    
        retVal=self.doThreshImage(self.cThresh,self.cmbMaterial.Value)
        self.UpdateImpResults()
        return retVal
    
    


if __name__ == '__main__':
    optParse=OptionParser()
    optParse.add_option('-B','--BOTTOMTOL',action='store',dest='bottol',default=475,help='Tolerance for bottom detection')
    optParse.add_option('-T','--TOPTOL',action='store',dest='toptol',default=-475,help='Tolerance for top detection')
    optParse.add_option('-C','--CENTTOL',action='store',dest='centtol',default=20,help='Tolerance for center detection')
    
    optParse.add_option('','--BOTTOMITER',action='store',dest='botiter',default=25,help='Iterations for bottom detection')
    optParse.add_option('','--TOPITER',action='store',dest='topiter',default=25,help='Iterations for top detection')
    optParse.add_option('','--CENTERITER',action='store',dest='centiter',default=15,help='Iterations for center detection')
    
    optParse.add_option('','--BOTTOMJUMP',action='store',dest='botjump',default=800,help='Pixels to jump for bottom detection')
    optParse.add_option('','--TOPJUMP',action='store',dest='topjump',default=800,help='Pixels to jump for top detection')
    
    optParse.add_option('','--MINBONE',action='store',dest='minpctbone',default=6,help='Minimum bone (in %) for image to be valid')
    
    optParse.add_option('','--THICKSTEP',action='store',dest='thicksteps',default=30,help='Step size in theta for evaluating thickness')
    
    optParse.add_option('-X','--EXP',action='store',dest='exptime',default=-1,help='Set Exposure Time (default read from server)',metavar='ExposureTime')
    
    optParse.add_option('-S','--SERVER',action='store',dest='server',default=0,help='Run alignment as service')
    
    optParse.add_option('-N','--NOSAVE',action='store_false',dest='save',help='Write outputs to text',default=True,metavar='LOG')

    
    optParse.add_option('-D','--DEBUG',action='store_true',dest='debug',help='Run program in debug mode',default=False,metavar='DEBUG')
    optParse.add_option('-L','--LOG',action='store_true',dest='log',help='Pump screen output to a log',default=False,metavar='LOG')

    optParse.add_option('-R','--RO',action='store_true',dest='readonly',help='Epics Variables are Read Only',default=False,metavar='READONLY')
    
    
    optParse.set_description('The command-line tool for alignment\n Version : '+str(faVersion))
    
    optParse.print_help()
    (opt,args)=optParse.parse_args()
    
    if opt.log:
        newPipe=__LoggingPipe__('FemurAlign')
        globals()['sys'].stdout=newPipe
        globals()['sys'].stderr=newPipe
    

    myFemur = FemurAlign(opt)
        
        
            
            