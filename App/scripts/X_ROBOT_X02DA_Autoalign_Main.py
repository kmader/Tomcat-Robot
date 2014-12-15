#Boa:Frame:AAPanel

import wx
import wx.stc
import wx.lib.plot
import time
from math import *
import glob
from numpy import array
import Image
import os,sys,socket
import cPickle
from optparse import OptionParser
from X_ROBOT_X02DA_Autoalign_Stage import alignStage
sys.path.append (os.path.expandvars ("$SLSBASE/sls/bin/"))
modules ={u'X_ROBOT_X02DA_AALib': [1,
                         'Alignment Library',
                         u'XX_ROBOT_X02DA_AALib.py']}
import X_ROBOT_X02DA_AALib 
kImage=X_ROBOT_X02DA_AALib.kImage # Not sure exactly why I did this, but I'll leave it be

class __LoggingPipe__:
    def __init__(self,logFileName='script',dirName='Robot_Logs'):
        try:
            os.listdir( os.path.expandvars ("$HOME/"+dirName+"/"))
        except:
            os.mkdir( os.path.expandvars ("$HOME/"+dirName+"/"))
        
        self.logFileName=os.path.expandvars("$HOME/"+dirName+"/"+logFileName+".log")
        self.write('\n'+time.asctime()+':'+logFileName+' freshly started'+'\n',0)
    def write(self,myStr,indent=1):
        tFile=open(self.logFileName,'a+')
        tFile.write('\t'*indent+myStr)
        tFile.close()

def create(parent):
    return AAPanel(parent)
[wxID_AAPANEL, wxID_AAPANELBUTCALIBRATE, wxID_AAPANELBUTCENTER, 
 wxID_AAPANELBUTCORR, wxID_AAPANELBUTFINDROTX, wxID_AAPANELBUTPREVIEW, 
 wxID_AAPANELBUTSEARCH, wxID_AAPANELBUTSTOPSEARCH, wxID_AAPANELBUTTILT, 
 wxID_AAPANELCKCENTERCLICK, wxID_AAPANELCKSHOWIMAGES, wxID_AAPANELFLATSPIN, 
 wxID_AAPANELIMGSPIN, wxID_AAPANELKEYSELECTION, wxID_AAPANELLOADFLAT, 
 wxID_AAPANELLOADIMAGE, wxID_AAPANELLOADSNAP, wxID_AAPANELPREVIEWBOX, 
 wxID_AAPANELRUNBATCH, wxID_AAPANELSTATICBOX1, wxID_AAPANELSTATICBOX2, 
 wxID_AAPANELSTATICBOX3, wxID_AAPANELSTATICTEXT1, wxID_AAPANELSTATICTEXT2, 
 wxID_AAPANELSTATICTEXT3, wxID_AAPANELTHRESHVAL, wxID_AAPANELTXTGLOB, 
 wxID_AAPANELTXTIMPRESULTS, 
] = [wx.NewId() for _init_ctrls in range(28)]

class AAPanel(wx.Frame):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_AAPANEL, name=u'AAPanel', parent=prnt,
              pos=wx.Point(39, 318), size=wx.Size(1184, 846),
              style=wx.DEFAULT_FRAME_STYLE, title=u'Tomcat Alignment Tool')
        self.SetClientSize(wx.Size(1184, 846))

        self.staticBox1 = wx.StaticBox(id=wxID_AAPANELSTATICBOX1,
              label=u'Setup', name='staticBox1', parent=self, pos=wx.Point(16,
              0), size=wx.Size(360, 96), style=0)
        self.staticBox1.SetMinSize(wx.Size(-1, -1))

        self.PreviewBox = wx.StaticBitmap(bitmap=wx.NullBitmap,
              id=wxID_AAPANELPREVIEWBOX, name=u'PreviewBox', parent=self,
              pos=wx.Point(456, 112), size=wx.Size(464, 464), style=0)
        self.PreviewBox.Bind(wx.EVT_LEFT_DOWN, self.OnPreviewBoxLeftDown)

        self.threshVal = wx.SpinCtrl(id=wxID_AAPANELTHRESHVAL, initial=10,
              max=500, min=1, name=u'threshVal', parent=self, pos=wx.Point(120,
              24), size=wx.Size(80, 24), style=wx.SP_ARROW_KEYS)

        self.staticText1 = wx.StaticText(id=wxID_AAPANELSTATICTEXT1,
              label=u'Threshold ', name='staticText1', parent=self,
              pos=wx.Point(32, 28), size=wx.Size(117, 17), style=0)

        self.keySelection = wx.ComboBox(choices=[], id=wxID_AAPANELKEYSELECTION,
              name=u'keySelection', parent=self, pos=wx.Point(392, 48),
              size=wx.Size(240, 27), style=0, value=u'Select Prefix...')
        self.keySelection.SetLabel(u'')
        self.keySelection.Bind(wx.EVT_COMBOBOX, self.OnKeySelectionCombobox,
              id=wxID_AAPANELKEYSELECTION)

        self.flatSpin = wx.SpinCtrl(id=wxID_AAPANELFLATSPIN, initial=0, max=100,
              min=0, name=u'flatSpin', parent=self, pos=wx.Point(640, 32),
              size=wx.Size(95, 27), style=wx.SP_ARROW_KEYS)

        self.imgSpin = wx.SpinCtrl(id=wxID_AAPANELIMGSPIN, initial=0, max=100,
              min=0, name=u'imgSpin', parent=self, pos=wx.Point(744, 32),
              size=wx.Size(95, 27), style=wx.SP_ARROW_KEYS)

        self.staticText2 = wx.StaticText(id=wxID_AAPANELSTATICTEXT2,
              label=u'Flat Selection', name='staticText2', parent=self,
              pos=wx.Point(648, 16), size=wx.Size(85, 17), style=0)

        self.staticText3 = wx.StaticText(id=wxID_AAPANELSTATICTEXT3,
              label=u'Image Selection', name='staticText3', parent=self,
              pos=wx.Point(744, 16), size=wx.Size(103, 17), style=0)

        self.loadImage = wx.Button(id=wxID_AAPANELLOADIMAGE,
              label=u'Load Image', name=u'loadImage', parent=self,
              pos=wx.Point(856, 16), size=wx.Size(85, 24), style=0)
        self.loadImage.SetMinSize(wx.Size(85, 0))
        self.loadImage.Bind(wx.EVT_BUTTON, self.OnLoadImageButton,
              id=wxID_AAPANELLOADIMAGE)

        self.txtGlob = wx.TextCtrl(id=wxID_AAPANELTXTGLOB, name=u'txtGlob',
              parent=self, pos=wx.Point(392, 16), size=wx.Size(240, 27),
              style=0, value=u'$HOME/*/*/*/tif/*.tif')
        self.txtGlob.Bind(wx.EVT_TEXT, self.OnTxtGlobTextEnter,
              id=wxID_AAPANELTXTGLOB)

        self.runBatch = wx.Button(id=wxID_AAPANELRUNBATCH,
              label=u'Fit Directory', name=u'runBatch', parent=self,
              pos=wx.Point(856, 40), size=wx.Size(85, 24), style=0)
        self.runBatch.SetMinSize(wx.Size(85, 0))
        self.runBatch.Bind(wx.EVT_BUTTON, self.OnRunBatchButton,
              id=wxID_AAPANELRUNBATCH)

        self.loadSnap = wx.Button(id=wxID_AAPANELLOADSNAP, label=u'Take Snap',
              name=u'loadSnap', parent=self, pos=wx.Point(112, 48),
              size=wx.Size(96, 32), style=0)
        self.loadSnap.Bind(wx.EVT_BUTTON, self.OnLoadSnapButton,
              id=wxID_AAPANELLOADSNAP)

        self.loadFlat = wx.Button(id=wxID_AAPANELLOADFLAT, label=u'Take Flat',
              name=u'loadFlat', parent=self, pos=wx.Point(24, 48),
              size=wx.Size(72, 32), style=0)
        self.loadFlat.SetMinSize(wx.Size(-1, 32))
        self.loadFlat.Bind(wx.EVT_BUTTON, self.OnLoadFlatButton,
              id=wxID_AAPANELLOADFLAT)

        self.staticBox2 = wx.StaticBox(id=wxID_AAPANELSTATICBOX2,
              label=u'Offline', name='staticBox2', parent=self,
              pos=wx.Point(384, 0), size=wx.Size(560, 88), style=0)
        self.staticBox2.SetMinSize(wx.Size(0, 0))
        self.staticBox2.SetHelpText(u'')

        self.butPreview = wx.Button(id=wxID_AAPANELBUTPREVIEW, label=u'Preview',
              name=u'butPreview', parent=self, pos=wx.Point(224, 48),
              size=wx.Size(85, 32), style=0)
        self.butPreview.Bind(wx.EVT_BUTTON, self.OnButPreviewButton,
              id=wxID_AAPANELBUTPREVIEW)

        self.staticBox3 = wx.StaticBox(id=wxID_AAPANELSTATICBOX3,
              label=u'Alignment Panel', name='staticBox3', parent=self,
              pos=wx.Point(952, 8), size=wx.Size(232, 824), style=0)
        self.staticBox3.SetMinSize(wx.Size(-1, -1))

        self.butSearch = wx.Button(id=wxID_AAPANELBUTSEARCH, label=u'Search',
              name=u'butSearch', parent=self, pos=wx.Point(960, 24),
              size=wx.Size(72, 32), style=0)
        self.butSearch.SetForegroundColour(wx.Colour(0, 0, 0))
        self.butSearch.SetBackgroundColour(wx.Colour(0, 239, 0))
        self.butSearch.Bind(wx.EVT_BUTTON, self.OnButSearchButton,
              id=wxID_AAPANELBUTSEARCH)

        self.butStopSearch = wx.Button(id=wxID_AAPANELBUTSTOPSEARCH,
              label=u'Stop Search', name=u'butStopSearch', parent=self,
              pos=wx.Point(1032, 24), size=wx.Size(88, 32), style=0)
        self.butStopSearch.SetBackgroundColour(wx.Colour(239, 0, 0))
        self.butStopSearch.Bind(wx.EVT_BUTTON, self.OnButStopSearchButton,
              id=wxID_AAPANELBUTSTOPSEARCH)

        self.butCenter = wx.Button(id=wxID_AAPANELBUTCENTER, label=u'Center',
              name=u'butCenter', parent=self, pos=wx.Point(960, 56),
              size=wx.Size(72, 32), style=0)
        self.butCenter.Bind(wx.EVT_BUTTON, self.OnButCenterButton,
              id=wxID_AAPANELBUTCENTER)

        self.butCorr = wx.Button(id=wxID_AAPANELBUTCORR, label=u'Correlate',
              name=u'butCorr', parent=self, pos=wx.Point(856, 64),
              size=wx.Size(88, 24), style=0)
        self.butCorr.SetMinSize(wx.Size(0, 0))
        self.butCorr.Bind(wx.EVT_BUTTON, self.OnButCorrClick,
              id=wxID_AAPANELBUTCORR)

        self.ckCenterClick = wx.CheckBox(id=wxID_AAPANELCKCENTERCLICK,
              label=u'Click Centers', name=u'ckCenterClick', parent=self,
              pos=wx.Point(432, 88), size=wx.Size(136, 16), style=0)
        self.ckCenterClick.SetValue(False)

        self.butFindRotX = wx.Button(id=wxID_AAPANELBUTFINDROTX,
              label=u'Find Rot Axis', name=u'butFindRotX', parent=self,
              pos=wx.Point(960, 88), size=wx.Size(157, 32), style=0)
        self.butFindRotX.Bind(wx.EVT_BUTTON, self.OnButFindRotClick,
              id=wxID_AAPANELBUTFINDROTX)

        self.ckShowImages = wx.CheckBox(id=wxID_AAPANELCKSHOWIMAGES,
              label=u'Show Images', name=u'ckShowImages', parent=self,
              pos=wx.Point(984, 648), size=wx.Size(112, 22), style=0)
        self.ckShowImages.SetValue(False)

        self.butCalibrate = wx.Button(id=wxID_AAPANELBUTCALIBRATE,
              label=u'Calibrate', name=u'butCalibrate', parent=self,
              pos=wx.Point(968, 120), size=wx.Size(85, 32), style=0)
        self.butCalibrate.Bind(wx.EVT_BUTTON, self.OnButCalibrateButton,
              id=wxID_AAPANELBUTCALIBRATE)

        self.txtImpResults = wx.stc.StyledTextCtrl(id=wxID_AAPANELTXTIMPRESULTS,
              name=u'txtImpResults', parent=self, pos=wx.Point(960, 336),
              size=wx.Size(216, 272), style=0)
        self.txtImpResults.SetMinSize(wx.Size(2, 1))

        self.butTilt = wx.Button(id=wxID_AAPANELBUTTILT, label=u'Correct Tilt',
              name=u'butTilt', parent=self, pos=wx.Point(1040, 56),
              size=wx.Size(85, 32), style=0)
        self.butTilt.Bind(wx.EVT_BUTTON, self.OnButTiltButton,
              id=wxID_AAPANELBUTTILT)

    def __init__(self, parent):
        self._init_ctrls(parent)
        optParse=OptionParser()
        optParse.add_option('-A','--ADV',action='store_const',dest='userlevel',const=1,default=0,help='Set User to Advanced',metavar='USERLEVEL')
        optParse.add_option('-X','--EXP',action='store_const',dest='userlevel',const=2,default=0,help='Set User to Expert',metavar='USERLEVEL')
        optParse.add_option('-H','--HOST',dest='host',type='string',help='Override hostname for computer',default=socket.gethostname(),metavar='HOST')
        optParse.add_option('-D','--DEBUG',action='store_true',dest='debug',help='Run program in debug mode',default=False,metavar='DEBUG')
        optParse.add_option('-L','--LOG',action='store_true',dest='log',help='Pump screen output to a log',default=False,metavar='LOG')

        optParse.add_option('-R','--RO',action='store_true',dest='readonly',help='Epics Variables are Read Only',default=False,metavar='READONLY')
        
        
        optParse.set_description('The graphical tool for the sample alignment code')
        
        optParse.print_help()
        (opt,args)=optParse.parse_args()
        
        if opt.log:
            newPipe=__LoggingPipe__('Autoalign')
            globals()['sys'].stdout=newPipe
            globals()['sys'].stderr=newPipe
        
        
        dSize=(2048,2048)
        self.traceGraph = kPlot(name=u'traceGraph', parent=self, pos=wx.Point(16, 104),
         size=wx.Size(456-16*2, 464), style=0,xAxis=(-dSize[0]/2,dSize[0]/2),yAxis=(-dSize[1]/2,dSize[1]/2),title='Sample Alignment')
        self.histoPlot = kPlot(name=u'histoPlot', parent=self, pos=wx.Point(16, 104+16+464),
         size=wx.Size(464*2+16, 200), style=0,title='Histogram')
        self.cmbMaterial = dictComboBox(dict=X_ROBOT_X02DA_AALib.sampleThreshLib,
              name=u'cmbMaterial', parent=self, pos=wx.Point(224, 16),
              size=wx.Size(112, 27), style=0, value=u'Material...')
        self.cmbMaterial.SetLabel(u'')
        self.stime=time.time()
        self.txtGlob.SetValue('$HOME/*/*/tif/*.tif')
        # old search string '$HOME/Data10/disk2/*/tif/*.tif'
        self.graphTimer=wx.Timer(self,-1)
        self.timerCycle=5000
        self.graphTimer.Start(self.timerCycle)
        self.Bind(wx.EVT_TIMER,self.mainTimerEvent) 
        self.cImg=100
        self.cKey=''
        self.cThresh=self.threshVal.GetValue()/10.0
        self.cThresh=1.0
        self.OnTxtGlobTextEnter([])
        self.dRange=[]
        self.batchEye=-2
        self.previewMode=0
        self.myStage=alignStage()
        self.oldImageName=''
        self.oldFlatName=''
        self.oldThresh=[]
        self.oldMat=''
        self.searchRunning=0
        #self.fltSelection.SetItems(self.imgList.keys())
        #self.doLoadImage()	
        self.flatIsLoaded=False
        
    def UpdateImpResults(self):
        theQuays=self.kImageObj._impResults.keys()
        theQuays.sort()
        outText=''
        for cKey in theQuays:
            outText+=cKey+' : '+str(self.kImageObj._impResults[cKey])+'\n'
        self.txtImpResults.Text=outText
    def doBatchImage(self):
        self.batchEye+=1
        if self.batchEye>=len(self.dRange):
            self.batchEye=-2
            if self.keySelection.GetSelection()<len(self.imgList.keys()):
                self.keySelection.SetSelection(self.keySelection.GetSelection()+1)
                self.cKey=self.keySelection.Value
                self.OnRunBatchButton([])
            return 0
        i=self.dRange[self.batchEye]
        (offSet,slope)=self.doLoadImage(imValue=i)
        dEle=(self.kImageObj.fitOffset,self.kImageObj.fitOrientation)
        self.dOffset.append(dEle[0])
        self.dAng.append(dEle[1]*100)
        print (i,dEle)
        #self.doDrawResults()
        
        self.histoPlot.makeGraph('Offset',self.dRange,self.dOffset)
        self.histoPlot.makeGraph('Orientation',self.dRange,self.dAng)
        
        nFile=open(self.cKey[self.cKey.rfind('/')+1:]+'.pyg','w')
        cPickle.dump([self.dRange,self.dOffset,self.dAng],nFile)
        nFile.close()
    def doLoadSnap(self):
        if self.flatIsLoaded==False:
            #self.doLoadFlatSnap()
            self.doJustLoadFlat()
        self.myStage.Snap() # Should be SnapTemp
        self.kImageObj=kImage(self.myStage.snapFileName,flatdata=self.flatdata)
        self.clearCache()
        return self.doThreshImage(self.cThresh,self.cmbMaterial.Value)
    def doLoadFlatSnap(self):
        self.myStage.SnapFlatField()
        self.doJustLoadFlat()
    def doJustLoadFlat(self):
        # assume the last flat image is up to date
        self.myStage._updateSnapName(fileName=self.myStage.dFlatName)
        mTemp=kImage(self.myStage.snapFileName)
        self.flatdata=mTemp._imageData
        print 'Current Flat Mean Value : '+str(round(self.flatdata.mean()))
        self.flatDataLoaded()
        self.clearCache()
    def flatDataLoaded(self):
        self.threshVal.Bind(wx.EVT_SPINCTRL, self.OnThreshValSpin,
              id=wxID_AAPANELTHRESHVAL)
        self.cmbMaterial.Bind(wx.EVT_COMBOBOX, self.OnThreshValSpin)
        self.flatIsLoaded=True
    def doLoadFlatData(self,filename):
        if self.oldFlatName==filename:
            return 1
        mTemp=kImage(filename)
        self.flatdata=mTemp._imageData
        self.oldFlatName=filename
        print 'Current Flat Mean Value : '+str(round(self.flatdata.mean()))
        self.clearCache()
        return 0
    # Dummy functions for use by the alignment tool for feedback
    def __loadImageHandle(self,filename):
        self.clearCache()
        if self.flatIsLoaded==False:
            self.doLoadFlatSnap()
        self.doLoadImageData(filename)
        if self.ckShowImages.Value:
            self.doThreshImage(self.cThresh,self.cmbMaterial.Value)
            self.doDrawResults()
        return self.kImageObj
    def __loadImageObjCheck(self,filename):
        # returns the %percent of pixels above threshold
        if self.flatIsLoaded==False:
            self.doLoadFlatSnap()
        if self.searchRunning:
            self.__loadImageHandle(filename)
            self.doThreshImage(self.cThresh,self.cmbMaterial.Value)
            if self.ckShowImages.Value:
                self.doDrawResults()
            return self.kImageObj._imageMask.sum()/(self.kImageObj.size[0]*self.kImageObj.size[1]+0.0)
        else:
            return -1
        
    def doLoadImageData(self,filename):
        
        if self.oldImageName==filename:
            return 1
        self.kImageObj=kImage(filename,flatdata=self.flatdata)
        self.clearCache()
        self.oldImageName=filename
        self.UpdateImpResults()
        return 0
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
    def doDrawResults(self):
        dSize=self.kImageObj.size
        self.traceGraph.xAxis=(-dSize[0]/2,dSize[0]/2)
        self.traceGraph.yAxis=(-dSize[1]/2,dSize[1]/2)
        
        self.traceGraph.title=('Angle = '+str(round(self.kImageObj.fitOrientation*1000))+' mdeg, Offset='+str(round(self.kImageObj.fitA))+'px')
        
        self.traceGraph.makeGraph('Error Bars',list(self.kImageObj.x),list(self.kImageObj.y))
        ganzVerruckt=0
        if ganzVerruckt:
            (tempX,tempY)=self.kImageObj._asVector_()
            self.traceGraph.makeGraph('Raw',list(tempX),list(tempY))
        self.traceGraph.makeGraph('Fit',list(self.kImageObj.fitDx),list(self.kImageObj.fitDy))
        self.traceGraph.SetEnableZoom(False)
        self.traceGraph.SetEnableGrid(True)
        self.traceGraph.SetEnableLegend(True)
        g_Image=self.kImageObj.toImg()
        n=wx.ImageHistogram()
        g_Image.ComputeHistogram(n)
        myColorRange=range(50,255)
        #rtHstRange=range(0,255)
        #grHstRange=range(0,129)
        greenCounts=[log(n.GetCount(n.MakeKey(0,i,0))+1) for i in myColorRange]
        redCounts=[log(n.GetCount(n.MakeKey(i,0,0))+1) for i in myColorRange]
        blueCounts=[log(n.GetCount(n.MakeKey(0,0,i))+1) for i in myColorRange]
        self.histoPlot.makeGraph('Sample',self.kImageObj.uint8histo(myColorRange,'G'),greenCounts)
        self.histoPlot.makeGraph('Metal',self.kImageObj.uint8histo(myColorRange,'R'),redCounts)
        self.histoPlot.makeGraph('Air',self.kImageObj.uint8histo(myColorRange,'B'),blueCounts)
        self.histoPlot.SetEnableZoom(False)
        self.histoPlot.SetEnableGrid(True)
        self.histoPlot.SetEnableLegend(True)
        self.PreviewBox.SetBitmap(wx.BitmapFromImage(g_Image.Rescale(self.PreviewBox.GetSize()[0],self.PreviewBox.GetSize()[1],quality=wx.IMAGE_QUALITY_HIGH)))
        self.UpdateImpResults()
    def mainTimerEvent(self,event):
        if self.batchEye>-2: self.doBatchImage()
        if self.previewMode>0: self.OnLoadSnapButton(event)
        #self.traceGraph.addPoints('Test1',[nPt])
        
    def OnThreshValSpin(self, event):
        self.cThresh=self.threshVal.GetValue()/10.0
        print self.cThresh
        self.doLoadImage(False)
        self.doDrawResults()	
        event.Skip()

    def OnKeySelectionCombobox(self, event):
        self.cKey=self.keySelection.Value
        #self.imgSpin.SetRange(int(min(self.imgList[self.cKey])),int(max(self.imgList[self.cKey])))
        self.imgSpin.SetRange(0,len(self.imgList[self.cKey])-1)
        self.flatSpin.SetRange(0,len(self.imgList[self.cKey])-1)
        #self.flatSpin.SetRange(int(min(self.imgList[self.cKey])),int(max(self.imgList[self.cKey])))
        event.Skip()


    def OnFlatSpinSpinctrl(self, event):
        cflat=self.cKey+self.imgList[self.cKey][self.flatSpin.GetValue()]+'.tif'
        self.doLoadFlatData(cflat)
        self.flatDataLoaded()
        self.doLoadImage()
        
        self.doDrawResults()	

    def OnImgSpinSpinctrl(self, event):
        cimg=self.cKey+self.imgList[self.cKey][self.imgSpin.GetValue()]+'.tif'
        if cimg is not self.cImg:
            self.cImg=cimg
            self.doLoadImage()
            self.doDrawResults()	
        event.Skip()

    def OnLoadImageButton(self, event):
        self.threshVal.Bind(wx.EVT_SPINCTRL, self.OnThreshValSpin,
              id=wxID_AAPANELTHRESHVAL)
        self.imgSpin.Bind(wx.EVT_SPINCTRL, self.OnImgSpinSpinctrl,
              id=wxID_AAPANELIMGSPIN)
        self.flatSpin.Bind(wx.EVT_SPINCTRL, self.OnFlatSpinSpinctrl,
              id=wxID_AAPANELFLATSPIN)
        cflat=self.cKey+self.imgList[self.cKey][self.flatSpin.GetValue()]+'.tif'
        self.flatdata=kImage(cflat)._imageData
        self.flatDataLoaded()
        self.doLoadImage()    
        self.doDrawResults()	  
        event.Skip()

    def OnTxtGlobTextEnter(self, event):
        curImgs={}
        def isImg(qE):
            try:
                qI=int(qE[len(qE)-8:(len(qE)-4)])
                qS=qE[:len(qE)-8]
                qI=qE[len(qE)-8:(len(qE)-4)]
                if not curImgs.has_key(qS):
                    curImgs[qS]=[]
                curImgs[qS].append(qI)
            except:
                print qE+' isnt valid'
        sDir=os.path.expandvars(self.txtGlob.GetValue())
        nList=glob.glob(sDir)
        nList.sort()
        map(isImg,nList)
        self.imgList=curImgs
        #self.flatdata=kImage(self.imgList[8])._imageData
        self.keySelection.SetItems(self.imgList.keys())

    def OnRunBatchButton(self, event):
        self.dOffset=[]
        self.dAng=[]
        self.dRange=range(self.flatSpin.GetValue()+2,len(self.imgList[self.cKey]))
        self.batchEye=-1
        self.histoPlot.clearGraph()

    def OnLoadSnapButton(self, event):
        self.doLoadSnap()
        self.doDrawResults()	
        event.Skip()

    def OnLoadFlatButton(self, event):
        self.doLoadFlatSnap()
        event.Skip()

    def OnButPreviewButton(self, event):
        if self.previewMode:
            self.previewMode=0
        else:
            self.previewMode=1
        event.Skip()

    def OnButFindRotClick(self, event):
        if self.flatIsLoaded==False:
            self.doLoadFlatSnap()
        self.myStage.Snap()
        self.kImageObj=kImage(self.myStage.snapFileName,flatdata=self.flatdata)
        self.myStage.RotStage(180)
        self.myStage.Snap()
        self.myStage.RotStage(-180)
        self.kImageObj._imageData=self.kImageObj.matchImage(kImage(self.myStage.snapFileName,flatdata=self.flatdata))
        self.kImageObj.threshold(0.5).fitVcyl(5)
        self.doDrawResults()	
        event.Skip()

    def OnPreviewBoxLeftDown(self, event):
        dSize=self.PreviewBox.GetSize()
        xClick=(event.X-dSize[0]/2.0)/(dSize[0]+0.0)
        yClick=-(event.Y-dSize[1]/2.0)/(dSize[1]+0.0)
        xPix=xClick*self.myStage.xPix
        yPix=yClick*self.myStage.yPix
        print 'Move Stage : '+str((xPix,yPix))
        self.myStage.BumpImage(-xPix,-yPix,self.ckCenterClick.Value) # x,y are how far away the stage is from where it need be
        
        
        event.Skip()


        
    def OnButCorrClick(self, event):
        # test align code
        imVal=self.imgSpin.GetValue()
        minVal=int(min(self.imgList[self.cKey]))+15 # assume 15 flats/darks
        maxVal=int(max(self.imgList[self.cKey]))-15
        nImVal=imVal-minVal
        nImVal=maxVal-nImVal
        
        dcImg=self.cKey+self.imgList[self.cKey][nImVal]+'.tif'
        self.kImageObj._imageData=self.kImageObj.matchImage(kImage(dcImg,flatdata=self.flatdata))
        self.kImageObj.threshold(0.5)
        self.doDrawResults()	
        event.Skip()

    def OnButSearchButton(self, event):
        self.searchRunning=1
        self.myStage.Search(self.__loadImageObjCheck)
        event.Skip()

    def OnButStopSearchButton(self, event):
        self.searchRunning=0
        event.Skip()

    def OnButCalibrateButton(self, event):
        self.myStage.Calibrate(self.__loadImageHandle)
        event.Skip()

    def OnButCenterButton(self, event):
        self.myStage.BumpImage(self.kImageObj.fitA)
        event.Skip()

    def OnButTiltButton(self, event):
        self.myStage.TiltImage(self.kImageObj.fitOrientation)
        event.Skip()

class dictComboBox(wx.ComboBox):
    def __init__(self,dict={},id=-1,name='',parent='',pos=[],size=[],value='',style=0):
        self.myDict=dict
        if id==-1: 
            id=wx.NewId()
        wx.ComboBox.__init__(self,choices=self.myDict.keys(),
              name=name, parent=parent, pos=pos,
              size=size, style=style, value=value)
    def LoadDict(self,dict={}):
        self.myDict=dict
        self.SetItems(self.myDict.keys())
    def __call__(self):
        curKey=self.Value
        return self.myDict[curKey]
          
class kPlot(wx.lib.plot.PlotCanvas):
    def __init__(self,id=-1,name='',parent=None,pos=[],size=[],style=0,xAxis=None,yAxis=None,title='MyGraph'):
        if id==-1:
            id=wx.NewId()
        wx.lib.plot.PlotCanvas.__init__(self,id=id,name=name,parent=parent,pos=pos,size=size,style=style)
        self.SetMinSize(wx.Size(-1, -1))
        self.graphs={}
        self.points={}
        self.selGraph=''
        self.colorList=['red','green','blue','pink']
        self.offset=0
        self._lastGraphIndex=0
        self.SetSize(size)
        self.xAxis=xAxis
        self.yAxis=yAxis
        self.title=title
    def getColor(self):
        self.colorList.insert(0,self.colorList.pop())
        return self.colorList[0]
    def clearGraph(self):
        self.graphs={}
        self.Clear()
    def makeGraph(self,name='',time=[],value=[],chromolist=[]):
        if len(chromolist)>0:
            self.makeGraph(chromolist[0].filename+'-'+str(0),chromolist[0].time,chromolist[0].value)
            rng=self.GetYCurrentRange()
            self.offset=0.05*(rng[1]-rng[0])
            for i in range(1,len(chromolist)):
                self.makeGraph(chromolist[i].filename+'-'+str(i),chromolist[i].time,chromolist[i].value)
        else:    
            dRedraw=0
            if self.graphs.has_key(name):
                self.Clear()
                dRedraw=1    
            cDict={}
            cDict['Color']=self.getColor()
            cDict['GraphIndex']=self._lastGraphIndex
            cDict['PlotElement']=[]
            cDict['Time']=time
            cDict['Value']=value
            self._lastGraphIndex+=1
            self.selGraph=name
            self.graphs[name]=cDict
            self._generateData(name)
            self.redraw()#[name])
    def _generateData(self,name):
        if self.graphs.has_key(name):
            oVal=[]
            lstPt=0
            tme=self.graphs[name]['Time']
            vlu=self.graphs[name]['Value']
            cDex=self.graphs[name]['GraphIndex']
            timeLen=len(tme)
            for pt in range(0,len(vlu)):
                if pt<timeLen:
                    lstPt=tme[pt]
                else:
                    lstPt+=1
                oVal.append((lstPt,vlu[pt]+cDex*self.offset))
            self.graphs[name]['Data']=oVal
            del(tme)
            del(vlu)
    def identifyPoint(self,_pt):
        minDex=''
        minDexDex=0
        minSum=0
        (_time,_value)=_pt
        for cKey in self.graphs.keys():
            cDex=self.time2index(cKey,_time)
            cVal=self.graphs[cKey]['Value'][cDex]+self.graphs[cKey]['GraphIndex']*self.offset
            if (minDex=='') or (abs(cVal-_value)<minSum):
                minDex=cKey
                minDexDex=cDex
                minSum=abs(cVal-_value)
        return (minDex,minDexDex)
            
        self.traceGraph.offset
    def addPoints(self,name,data):
        if self.graphs.has_key(name):
            ourGraph=self.graphs[name]
            tData=data
            #tData.insert(0,ourGraph['Data'].pop())
            for ird in tData:
                ourGraph['Data'].append(ird)
            line=wx.lib.plot.PolyLine(ourGraph['Data'],legend=name,colour=ourGraph['Color'],width=1)
            
            ourGraph['PlotElement']=[line]
            self.redraw()#[name])#,len(ourGraph['PlotElement'])-1)
        else:
            self.makeGraph(name,data)       
    def redraw(self,ele=[],slc=-1):
        
        pList=[]
        if len(ele)<1:
            #self.Clear()
            ele=self.graphs.keys()
        for cKey in ele:
            
            #for pEle in self.graphs[cKey]['PlotElement']:
            #    pList.append(pEle)
            if cKey==self.selGraph:
                nWid=2
            else:
                nWid=2
            if len(self.graphs[cKey]['Data'])<2000:
                line=wx.lib.plot.PolyLine(self.graphs[cKey]['Data'],legend=cKey,colour=self.graphs[cKey]['Color'],width=nWid)        
            else:
                print len(self.graphs[cKey]['Data'])
                line=wx.lib.plot.PolyMarker(self.graphs[cKey]['Data'],legend=cKey,colour=self.graphs[cKey]['Color'],width=1,size=1)
            self.graphs[cKey]['PlotElement']=[line]
            pList.append(line)
        gc=wx.lib.plot.PlotGraphics(pList,self.title,'X','Y')
        self.Draw(gc,xAxis=self.yAxis,yAxis=self.yAxis)   
    def time2index(self,name,timeG):
        if len(self.graphs[name]['Time'])<1:
            theDex=int(timeG)
            if theDex>=len(self.graphs[name]['Value']): theDex=len(self.graphs[name]['Value'])-1
            if theDex<0: theDex=0
        else:
            theDex=self.__time2index(name,timeG)
        return theDex
    def __time2index(self,name,timeG,firstDex=0,lastDex=9e9,iter=0):
        tme=self.graphs[name]['Time']
        iter+=1

        if firstDex<0: firstDex=0
        if lastDex<=(firstDex-1): lastDex=firstDex+2
        if lastDex>=len(tme): lastDex=len(tme)-1
        if lastDex<=(firstDex-1): firstDex=lastDex-2
        startT=tme[firstDex]
        endT=tme[lastDex]
        #print 'Current Iteration : '+str(iter)+' : '+str((startT,timeG,endT))
        if lastDex==(len(tme)-1) and timeG>endT:
            return lastDex
        if firstDex==0 and timeG<startT:
            return firstDex
        if iter>1:
            if (timeG>=startT) and (timeG<=endT):
                return firstDex+1
        
        guessD=int(float(lastDex-firstDex)/(endT-startT)*(timeG-startT)+firstDex)
        
        if (guessD-1)==firstDex and (guessD+1)==lastDex: return guessD 
        return self.__time2index(name,timeG,guessD-1,guessD+1,iter)



