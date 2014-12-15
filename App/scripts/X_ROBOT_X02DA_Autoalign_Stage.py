#!/usr/bin/env python
#Boa:PyApp:main
bumpPrefix='X02DA-ES1-BUMP'
snapPrefix='X02DA-SCAN-SNAP'
specPrefix='X02DA-SCAN-SCN1'
camPrefix='X02DA-SCAN-CAM1'
roboPrefix='X02DA-ES1-ROBO'
stgPrefix='X02DA-ES1-SMP1'
gonioXX='ROTX'
gonioZZ='ROTZ'

VirtualYvalLimits=(-23000,-3000)
import time
from math import *
from optparse import OptionParser
import sys,os,socket
import glob 
try:
    #import X_ROBOT_X02DA_httpEpics as X_ROBOT_X02DA_robotCommon
    import X_ROBOT_X02DA_robotCommon
except:
    print "Initial robotCommon not found!"
    try:
        sys.path.insert (0, os.path.expandvars ("$SLSBASE/sls/bin/"))
        #import  X_ROBOT_X02DA_httpEpics as X_ROBOT_X02DA_robotCommon
        import X_ROBOT_X02DA_robotCommon
    except:
        wx.MessageBox('httpEpics Python Library is needed to run this program!')
        sys.exit (1)

modules ={}

class alignStage:
    def __init__(self):
        bumpPrefix='X02DA-ES1-BUMP'
        snapPrefix='X02DA-SCAN-SNAP'
        specPrefix='X02DA-SCAN-SCN1'
        camPrefix='X02DA-SCAN-CAM1'
        roboPrefix='X02DA-ES1-ROBO'
        stgPrefix='X02DA-ES1-SMP1'
        gonioXX='ROTX'
        gonioZZ='ROTZ'
        #self.rxBChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(bumpPrefix+':BUMPX.PROC')
        #self.zBChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(bumpPrefix+':BUMPZ.PROC')
        
        # Sequencer Control Channels
        self.pauseChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(roboPrefix+':GUI-PAUSE')
        self.startChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(roboPrefix+':GUI-BEGIN')
        # Read Stage Values
        self.RawYValue=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(stgPrefix+':TRY-VAL.VAL')
        self.RealXValue=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(stgPrefix+':TRX.VAL')
        self.RawXValue=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(stgPrefix+':TRXX.VAL')
        # Move stage and bump channels
        self.stepXBchan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(bumpPrefix+':BP-XPIX')
        self.stepYBchan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(bumpPrefix+':BP-YPIX')
        self.yBChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(bumpPrefix+':BUMPY.PROC')
        self.xxBChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(bumpPrefix+':BUMPXX.PROC')
        self.zzBChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(bumpPrefix+':BUMPZZ.PROC')
        self.xxnBChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(bumpPrefix+':NBUMPXX.PROC')
        self.zznBChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(bumpPrefix+':NBUMPZZ.PROC')
        self.rotChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(stgPrefix+':ROTYUSETP')
        self.movingChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(roboPrefix+":MT-UNTERWEGS")
        self.goXXChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(stgPrefix+':'+gonioXX+'.VAL')
        self.goZZChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(stgPrefix+':'+gonioZZ+'.VAL')
        # Alignment Server
        self.alignmentChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(bumpPrefix+':GO')
        self.gAlignmentChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(bumpPrefix+':GGO')
        self.killChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(bumpPrefix+':KILL')
        self.aliveChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(bumpPrefix+':ALIVE')
        # Snap Chanels
        self.snapChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(snapPrefix+':SNAP')
        self.flatChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(snapPrefix+':FLAT')
        self.snapDirChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(snapPrefix+':STORAGE')
        self.snapNameChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(snapPrefix+':IMGNME')
        self.snapExpTime=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(snapPrefix+':EXPTME')
        self.snapTiffBit=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(snapPrefix+':TIFF')
        self.snapFlatMoveOut=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(bumpPrefix+':SMPOUT.PROC')
        self.snapFlatMoveIn=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(bumpPrefix+':SMPIN.PROC')
        self.dimxChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(snapPrefix+':DIMX')
        self.dimyChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(snapPrefix+':DIMY')
        # SPEC Channels
        self.specDirChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(camPrefix+':STORAGE')
        self.specNameChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(camPrefix+':FILPRE')
        self.specExpTime=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(camPrefix+':EXPTME')
        self.specRotChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(specPrefix+':ROTSTA')
        self.specRotStopChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(specPrefix+':ROTSTO')
        # Save and Load Imaging Position
        self.savePosChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(roboPrefix+":SAM_SET.PROC")
        self.loadPosChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(roboPrefix+":SAM_LOAD-YV.PROC")
        
        # Movement and calibration parameters
        
        self.calXchan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(snapPrefix+':XCAL')
        self.calYchan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(snapPrefix+':YCAL')
        self.objChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(snapPrefix+':LNSDBL')
        #self.binChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(snapPrefix+':BIN')
        self.xBinChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(snapPrefix+':XBIN')
        self.yBinChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(snapPrefix+':YBIN')
        # Beamline Optics Control
        self.shutterChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel('X02DA-OP-FI4:TRY')
        
        # Goniometer Settings
        self.gonioCalib=1000 # epics values / degree
        self.gonioMin=-6000 # minimum value
        self.gonioMax=6000 # maximum value
        
        
        self.rotVal=0
        self.opMode=0 # 0 find object, 1 center object, 2 center object@90,180, 3 orient object
        
        # Objective/Detector Info
        self.Objective=self.objChan.getVal()        
        
        # Sample Name 
        
        self.dSnapName='Snap'
        self.dFlatName='Flat'
        self.tempFiles=[]
        self._updateSnapName('Snaps',self.dSnapName)
        
        #self._restoreNames()
        self.xPix=self.dimxChan.getVal()
        self.yPix=self.dimyChan.getVal()
        
        # Snap tiff bit settings
        self.snapTiffBit.putVal(8) # we only want 8 bit images
        
        # Object Info
        self.objXsize=0.2 # takes up 20% of the x-field of view
        self.objYsize=4 # takes up 400% of the y-field of view
        # The whole step business is change in the channel value for each pixel to correct
        
        self.searchThreshold=0.25 # percentage of full object to be in field of view before centering
        
        
        self._getCalibration() # load first values from epics

        self.tiltStep=100
    def SPECtoSNAP(self):
        self.snapDirChan.putVal(self.specDirChan.getVal())
        sampName=self.specNameChan.getVal()
        self.snapNameChan.putVal(sampName)
        self.snapExpTime.putVal(self.specExpTime.getVal())
        self.shutterChan.putVal(1)
        self.SetHomePos()
        
        time.sleep(0.5)
        return sampName
    def _objVpct(self):
        # volume fraction of object when centered in field of view
        
        return min(self.objXsize,1)*min(self.objYsize,1)
    
    def _getCalibration(self):
        return (self.calXchan.getVal(),self.calYchan.getVal())
    def _setCalibration(self,IxStep=0,IyStep=0):
        if not (IxStep==0):
            self.calXchan.putVal(-IxStep)
        if not (IyStep==0):
            self.calYchan.putVal(IyStep)
    def _restoreNames(self):
        self.snapDirChan.putVal(self.oldDirVal)
        self.snapNameChan.putVal(self.oldNameVal)
    def _updateSnapName(self,dirName='',fileName=''):
        #self.oldDirVal=self.snapDirChan.getVal()
        #self.oldNameVal=self.snapNameChan.getVal()
        if len(dirName)>0:
            self.snapDirChan.putVal(dirName)
        if len(fileName)>0:
            self.snapNameChan.putVal(fileName)
        self.snapFileName=os.path.expandvars ("$HOME/"+self.snapDirChan.getVal()+"/"+self.snapNameChan.getVal()+".8bit.tif")
            
    def SnapTemp(self):
        cuteName=os.tempnam().split('/')[-1];
        self.Snap(cuteName)
        self.tempFiles.append(self.snapFileName)
        return cuteName
    def Snap(self,spcName=''):
        if not (spcName==''):
            self._updateSnapName(fileName=spcName)
        else:
            self._updateSnapName(fileName=self.dSnapName)
        self.__snap__()
        
    def SnapFlatField(self):
        self.snapFlatMoveOut.putVal(1)
        self.waitMoving()
        self._updateSnapName(fileName=self.dFlatName)
        # Swap out snap channel for flat channel
        normSnap=self.snapChan
        self.snapChan=self.flatChan
        self.__snap__()
        self.snapChan=normSnap
        self.snapFlatMoveIn.putVal(1)
        
        #self.waitMoving()    
    def SetHomePos(self):
        print 'Set Home'
        self.waitMoving()
        self.savePosChan.putVal(1)
        time.sleep(0.75) # give epics 0.75 seconds to read everything    
        cStg={}
        for [dPrefix,cField] in X_ROBOT_X02DA_robotCommon.AlignChannels:
            tempChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel(dPrefix+cField)
            cVal=tempChan.getVal()
            cStg[cField]=cVal
        return cStg
    def PutHomePos(self):
        print 'Put Home'
        self.waitMoving()
        self.loadPosChan.putVal(1)
    def RotStage(self,rot=0,relValue=True):
        if relValue:
            if abs(rot)>0:
                self.rotChan.putVal(self.rotChan.getVal()+rot)
        else:
            self.rotChan.putVal(rot)
    def TiltImage(self,curAng=0,moveStage=True):
        movAng=float(curAng)
        if moveStage:
            (wChan,signVec)=self.GetWGoChan()
            movAng*=signVec*self.gonioCalib 
            movAng+=wChan.getVal()
            movAng=min(movAng,self.gonioMax) # Goniometer Limits
            movAng=max(movAng,self.gonioMin) # 
            if abs(movAng)>0:
                wChan.putVal(movAng)
    def BumpImage(self,xPixDist=0,yPixDist=0,moveStage=True):
        # Interface to move stage as a function of current displayed image
        xPixDist=float(xPixDist)
        yPixDist=float(yPixDist)
        self.stepXBchan.putVal(xPixDist)
        self.stepYBchan.putVal(yPixDist)
        ischGloff=False
        if moveStage:
            ischGloff=True
            wChan=self.GetWChan()
            
            if abs(yPixDist)>0:
                if self.RawYValue.getVal()<VirtualYvalLimits[1]:
                    if self.RawYValue.getVal()>VirtualYvalLimits[0]:
                        self.yBChan.putVal(1)
                    else:
                        print "StageY: "+str(self.RawYValue.getVal())+" Cannot Move Lower than "+str(VirtualYvalLimits[0])
                        ischGloff=False
                        return ischGloff
                else:
                    print "StageY "+str(self.RawYValue.getVal())+" Cannot Move Higher then "+str(VirtualYvalLimits[1])
                    ischGloff=False
                    return ischGloff
            if ischGloff:
                if abs(xPixDist)>0: wChan.putVal(1)
        return ischGloff
                    
            
    def BumpChan(self,Bchan):
        Bchan.putVal(1)
    def __snap__(self):
        # Nightmare of problems, network file systems are absolute shit
        #try:
        #    os.remove(self.snapFileName) #delete image before hand
        #except:
        #    print 'Image has not been taken before'
        
        self.waitMoving()
        
        self.snapChan.putVal(1)
        snaptime=time.time()
        while self.snapChan.getVal()>0:
            time.sleep(0.1)
            if (time.time()-snaptime)>15:
                print 'Snap Function is Broken'
                return 0
        snaptime=time.time()
        return 1
    def isMoving(self):
        return abs(self.movingChan.getVal())>0
    def waitMoving(self):
        print 'Waiting for Stage...'
        while self.isMoving():
            time.sleep(.1)
            #print 'Is Moving'
        print 'Done Waiting'
    def GetWGoChan(self):
        # Automatically give back primary w-channel( x on the image)
        
        # At the moment only sample alignment, not general calibration
        #if self.opMode<2:
        #    return (self.rxBchan,self.xStep)
        self.rotVal=self.rotChan.getVal()
        print 'Cur Rot Angle : '+str(self.rotVal)
        rotInt=round(self.rotVal/90.0)
        angVec=-1
        if rotInt==1:
            wChan=self.goZZChan
            angVec=1
        elif rotInt==3 or rotInt==-1:
            wChan=self.goZZChan
            angVec=-1
        elif rotInt==0:
            wChan=self.goXXChan
            angVec=-1
        elif rotInt==2 or rotInt==-2:
            wChan=self.goXXChan
            angVec=1
        else:
            print 'Invalid Angle!'
            return 0
        return (wChan,angVec)        
    def GetWChan(self):
        # Automatically give back primary w-channel( x on the image)
        
        # At the moment only sample alignment, not general calibration
        #if self.opMode<2:
        #    return (self.rxBchan,self.xStep)
        self.rotVal=self.rotChan.getVal()
        print 'Cur Rot Angle : '+str(self.rotVal)
        rotInt=round(self.rotVal/90.0)
        
        if rotInt==1:
            wChan=self.zznBChan
        elif rotInt==3 or rotInt==-1:
            wChan=self.zzBChan
        elif rotInt==0:
            wChan=self.xxBChan
        elif rotInt==2 or rotInt==-2:
            wChan=self.xxnBChan
        else:
            print 'Invalid Angle!'
            return 0
        return wChan
    def CorrectTile(self,a):
        # really a dummy function until we figure out what the hell we're doing
        print 'Not yet ready'
    # spiral is the beginning of a sample finding routine, maybe useful for nano
    def __spiraldir__(self,T=0,nStart=1):
        n=nStart
        nMode=-1
        cmdList=''
        while len(cmdList)<T:
            if nMode==-1:
                cmdList+='A'
            elif nMode==0:
                cmdList+='Q'*(n-1)
            elif nMode==1:
                cmdList+='E'*n
            elif nMode==2:
                cmdList+='C'*n
            elif nMode==3:
                cmdList+='Z'*n
                nMode=-2
                n+=1
            nMode+=1
        return cmdList[-1]
    def __spiral__(self,T=0,nStart=1):
        cMode=self.__spiraldir__(T,nStart)
        dX=self.xPix*self.objXscale
        dY=self.yPix*self.objYscale
        
        if cMode=='A':
            (x,y)=(-dX,0)
        elif cMode=='Q':
            (x,y)=(-dX,dY)
        elif cMode=='E':
            (x,y)=(dX,dY)
        elif cMode=='C':
            (x,y)=(dX,-dY)
        elif cMode=='Z':
            (x,y)=(-dX,-dY)
        return (x,y)
    def __spiralMaths__(self,T=0,steps=10):
        # Steps is steps per 360
        # x = xPixs*T/steps*sin(T*2*pi/steps)
        # y = yPixs=T/steps*cos(T*2*pi/steps)
        # Work with derivatives since we are only bumping
        x=self.xPix/steps*sin(T*2*pi/steps)+self.xPix/steps*2*pi/steps*T*cos(T*2*pi/steps)
        y=self.yPix/steps*cos(T*2*pi/steps)-self.yPix/steps*2*pi/steps*T*sin(T*2*pi/steps)
        return (x,y)
    def Search(self,readPictCallback,tSteps=100):
        self.SetHomePos()
        self.Snap()
        if oVal==0:
            (xChan,xStep)=self.GetXChan()
            for i in range(1,tSteps+1):
                (x,y)==self.__spiral__(i+0.0)
                self.BumpImage(x,y)
                self.Snap()
                oVal=readPictCallback.__call__(self.snapFileName)
                if oVal>=self._objVpct()*self.searchThreshold:
                    return 1
                elif oVal<0:
                    return oVal
        return oVal
    
    # Automatic Calibration Routine
    def Calibrate(self,imgCallback,mvPx=300.0):
        self.rotChan.putVal(0) # must have it correctly setup
        self.Snap('basePos')
        baseImg=imgCallback.__call__(self.snapFileName)
        self.opMode=0
        self.BumpImage(mvPx,0)
        self.Snap('move100-0')
        leftImg=imgCallback.__call__(self.snapFileName)
        self.BumpImage(-mvPx,mvPx)
        self.Snap('move0-100')
        upImg=imgCallback.__call__(self.snapFileName)
        self.BumpImage(0,-mvPx)
        
        baseImg.matchImage(leftImg)
        xMoved=baseImg.matchedPos[0]
        baseImg.matchImage(upImg)
        yMoved=baseImg.matchedPos[1]
        
        self._setCalibration(self.xStep,self.yStep)
        print 'Object Moved : '+str((xMoved,yMoved))
        print 'New Values: '+str((self.xStep,self.yStep))
         
        
def main():
    optParse=OptionParser()
    optParse.add_option('-A','--ADV',action='store_const',dest='userlevel',const=1,default=0,help='Set User to Advanced',metavar='USERLEVEL')
    optParse.add_option('-X','--EXP',action='store_const',dest='userlevel',const=2,default=0,help='Set User to Expert',metavar='USERLEVEL')
    optParse.add_option('-H','--HOST',dest='host',type='string',help='Override hostname for computer',default=socket.gethostname(),metavar='HOST')
    optParse.add_option('-D','--DEBUG',action='store_true',dest='debug',help='Run program in debug mode',default=False,metavar='DEBUG')
    optParse.add_option('-R','--RO',action='store_true',dest='readonly',help='Epics Variables are Read Only',default=False,metavar='READONLY')
    
    
    optParse.set_description('The graphical frontend for the Robot Control and Sample Alignment')
    
    optParse.print_help()
    (opt,args)=optParse.parse_args()
    pass

if __name__ == '__main__':
    main()
