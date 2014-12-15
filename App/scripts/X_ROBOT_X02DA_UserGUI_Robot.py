#Boa:Frame:GUI_Robot

import wx
import wx.lib.masked.textctrl
import wx.stc
import wx.grid
import threading
import os
import pickle
import time
import X_ROBOT_X02DA_database
tSIZEROWS=10
tSIZECOLS=6
tArray=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P']



      
def create(parent,mainPtr):
    return GUI_Robot(parent,mainPtr)
def REcreate(parent,mainPtr):
    return GUI_RobotExpert(parent,mainPtr)
panelInfo={}
panelInfo['Tray Setup']=create
panelInfo['Robot Expert']=REcreate
[wxID_GUI_ROBOT, wxID_GUI_ROBOTBUTEDITSCRIPT, 
 wxID_GUI_ROBOTBUTGETSTGPOS, wxID_GUI_ROBOTBUTLOAD, 
 wxID_GUI_ROBOTBUTMOVELOAD, wxID_GUI_ROBOTBUTSEQUENCER, 
 wxID_GUI_ROBOTBUTSETLOAD, wxID_GUI_ROBOTBUTSETSTGPOS, 
 wxID_GUI_ROBOTBUTSTARTRBBOT, wxID_GUI_ROBOTBUTUNLOAD, wxID_GUI_ROBOTBXROBOT, 
 wxID_GUI_ROBOTBXSAMPLE, wxID_GUI_ROBOTBXSTAGE, wxID_GUI_ROBOTCHKTOOLTIPS, 
 wxID_GUI_ROBOTSPINSTAGEMEMORY, wxID_GUI_ROBOTSTACURPOS, 
 wxID_GUI_ROBOTSTAEMPTYCODE, wxID_GUI_ROBOTSTAROBOTSTATUS, 
 wxID_GUI_ROBOTSTAROTY, wxID_GUI_ROBOTSTASAMPLEERROR, 
 wxID_GUI_ROBOTSTASTAGESTATUS, wxID_GUI_ROBOTSTATICBOX2,
 wxID_GUI_ROBOTSTATICBOX4, 
 wxID_GUI_ROBOTSTATICBOX5, wxID_GUI_ROBOTSTATICTEXT1, 
 wxID_GUI_ROBOTSTATICTEXT2, wxID_GUI_ROBOTSTATICTEXT3, 
 wxID_GUI_ROBOTSTATRX, wxID_GUI_ROBOTSTATRXD, 
 wxID_GUI_ROBOTSTATRXXD, wxID_GUI_ROBOTSTATRYV, 
 wxID_GUI_ROBOTSTATRY2, wxID_GUI_ROBOTSTATRYVAL, wxID_GUI_ROBOTSTATRZ, 
 wxID_GUI_ROBOTSTATRZD, wxID_GUI_ROBOTSTATRZZ, wxID_GUI_ROBOTSTATRZZD, 
 wxID_GUI_ROBOTTXTEXPERTCODE, wxID_GUI_ROBOTTXTSAMPLEDESCRIPTION, 
 wxID_GUI_ROBOTTXTSAMPLENAME, wxID_GUI_ROBOTSTATICBOX1
] = [wx.NewId() for altID in range(41)]
def xmlOneStep(aNodes,nodeName):
    # generic function to grab subnodes and avoid overly nested code
    outNode=[]
    for aNode in aNodes:
        for bNode in aNode.childNodes:
            if bNode.nodeName.upper()==nodeName.upper():
                outNode.append(bNode)
    return outNode
def CreateBlankGrid(mRows=tSIZEROWS,mCols=tSIZECOLS):
    tray=[];
    for ij in range(0,mRows):
        curRow=[]
        for ik in range(0,mCols):
            # array outline (name,desc,toLoad,Pos)
            curRow.append([tArray[ik]+ij.__str__(),'',0,[]])
        tray.append(curRow)
    return tray
def ReadTrayFromXML(xmlNodes):
    # reads the tray from the xml file
    if len(xmlNodes)>0:
        xmlNode=xmlNodes[0]
        gRows=tSIZEROWS
        gCols=tSIZECOLS
        if xmlNodes[0].hasAttribute('rows'): gRows=int(xmlNode.getAttribute('rows'))
        if xmlNodes[0].hasAttribute('cols'): gCols=int(xmlNode.getAttribute('cols'))
        #print 'pre-init'+str(gRows)+','+str(gCols)
        tray=CreateBlankGrid(gRows,gCols)
        ctNodes=xmlOneStep([xmlNode],'sample')
        for ctNode in ctNodes:
            
            if (ctNode.hasAttribute('row-index') & ctNode.hasAttribute('col-index')):
                ij=int(ctNode.getAttribute('row-index'))
                ik=int(ctNode.getAttribute('col-index'))
                
                tray[ij][ik][2]=1
                for ctrNode in ctNode.childNodes:
                    ctrName=ctrNode.nodeName.upper().strip()
                    if ctrName=='NAME':
                        tray[ij][ik][0]=ctrNode.firstChild.nodeValue.strip()
                    elif ctrName=='DESC':
                        tray[ij][ik][1]=ctrNode.firstChild.nodeValue.strip()
                    elif ctrName=='STAGE_POSITION':
                        if ctrNode.hasAttribute('id'):
                            cId=int(ctrNode.getAttribute('id'))
                            while cId>=len(tray[ij][ik][3]):
                                tray[ij][ik][3].append({})
                            ctrsNodes=xmlOneStep([ctrNode],'stagechannel')
                            
                            for ctrsNode in ctrsNodes:
                                chanName=ctrsNode.getAttribute('name')
                                tray[ij][ik][3][cId][chanName]=float(ctrsNode.getAttribute('value'))
    else:
        tray=CreateBlankGrid()
    return tray
                                   
class GUI_Robot(wx.Panel):
    # define the size of the tray
    version=20100117
    #wx.Frame.__init__(self, id=wxID_GUI_ROBOT, name=u'GUI_Robot',
              #parent=prnt, size=wx.Size(745, 500), style=wx.DEFAULT_FRAME_STYLE,
              #title='Alignment Tool')
    #wx.Panel.__init__(self,prnt)
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Panel.__init__(self,prnt)


        self.bxSample = wx.StaticBox(id=wxID_GUI_ROBOTBXSAMPLE,
              label=u'Sample Selector', name=u'bxSample', parent=self,
              pos=wx.Point(0, 8), size=wx.Size(416, 288), style=0)
        self.bxSample.SetMinSize(wx.Size(0, 0))

        self.staticBox2 = wx.StaticBox(id=wxID_GUI_ROBOTSTATICBOX2,
              label=u'Sample Information', name='staticBox2', parent=self,
              pos=wx.Point(0, 296), size=wx.Size(416, 160), style=0)

        self.staticText1 = wx.StaticText(id=wxID_GUI_ROBOTSTATICTEXT1,
              label=u'Sample Name:', name='staticText1', parent=self,
              pos=wx.Point(8, 320), size=wx.Size(96, 17), style=0)

        self.staticText2 = wx.StaticText(id=wxID_GUI_ROBOTSTATICTEXT2,
              label=u'Sample Desc:', name='staticText2', parent=self,
              pos=wx.Point(8, 360), size=wx.Size(91, 17), style=0)

        self.txtSampleName = wx.TextCtrl(id=wxID_GUI_ROBOTTXTSAMPLENAME,
              name=u'txtSampleName', parent=self, pos=wx.Point(112, 320),
              size=wx.Size(216, 22), style=0, value=u'null')
        self.txtSampleName.SetToolTipString(u"The name that will be used in the images of the sample. Probably shouldn't have spaces, umlauts, accents, or weird characters. Additionally try to keep the name short as other elements are often added to the end")
        self.txtSampleName.Bind(wx.EVT_KEY_UP, self.OnTxtSampleNameText)
        self.txtSampleName.Bind(wx.EVT_KILL_FOCUS, self.OnTxtSampleNameText)
        self.txtSampleName.Bind(wx.EVT_TEXT_ENTER, self.OnTxtSampleNameText,
              id=wxID_GUI_ROBOTTXTSAMPLENAME)

        self.txtSampleDescription = wx.stc.StyledTextCtrl(id=wxID_GUI_ROBOTTXTSAMPLEDESCRIPTION,
              name=u'txtSampleDescription', parent=self, pos=wx.Point(112, 344),
              size=wx.Size(208, 100), style=0)
        self.txtSampleDescription.SetWrapMode(1)
        self.txtSampleDescription.SetToolTipString(u'Enter a description of the sample for later use since the filename will probably be too short to allow for adaquate naming')
        self.txtSampleDescription.Bind(wx.EVT_KILL_FOCUS,
              self.OnTxtSampleNameText)
        self.txtSampleDescription.Bind(wx.EVT_KEY_UP, self.OnTxtSampleNameText)

        self.staCurPos = wx.StaticText(id=wxID_GUI_ROBOTSTACURPOS, label=u'',
              name=u'staCurPos', parent=self, pos=wx.Point(342, 363),
              size=wx.Size(58, 17), style=0)

        self.bxStage = wx.StaticBox(id=wxID_GUI_ROBOTBXSTAGE,
              label=u'Stage Control', name=u'bxStage', parent=self,
              pos=wx.Point(416, 8), size=wx.Size(136, 288), style=0)
        self.bxStage.SetMinSize(wx.Size(0, 0))
        self.bxStage.SetToolTipString(u'Green means stage moving, Red stage is stopped')

        self.bxRobot = wx.StaticBox(id=wxID_GUI_ROBOTBXROBOT,
              label=u'Robot Control', name=u'bxRobot', parent=self,
              pos=wx.Point(416, 296), size=wx.Size(136, 160), style=0)
        self.bxRobot.SetMinSize(wx.Size(0, 0))



        self.butLoad = wx.Button(id=wxID_GUI_ROBOTBUTLOAD, label=u'Load Sample',
              name=u'butLoad', parent=self, pos=wx.Point(424, 352),
              size=wx.Size(120, 32), style=0)
        self.butLoad.SetToolTipString(u'Command to load the highlighted sample on the stage. This is disabled when the robot has not been started or once a sample is already loaded')
        self.butLoad.Bind(wx.EVT_BUTTON, self.OnButLoadButton,
              id=wxID_GUI_ROBOTBUTLOAD)

        self.butUnload = wx.Button(id=wxID_GUI_ROBOTBUTUNLOAD, label=u'Unload',
              name=u'butUnload', parent=self, pos=wx.Point(424, 384),
              size=wx.Size(120, 32), style=0)
        self.butUnload.SetToolTipString(u'Click to remove a sample from the stage and return it to its original place on the sample tray. This button is disabled when the robot is off or no sample is mounted')
        self.butUnload.Bind(wx.EVT_BUTTON, self.OnButUnloadButton,
              id=wxID_GUI_ROBOTBUTUNLOAD)

        self.butGetStgPos = wx.Button(id=wxID_GUI_ROBOTBUTGETSTGPOS,
              label=u'Record', name=u'butGetStgPos', parent=self,
              pos=wx.Point(424, 48), size=wx.Size(80, 32), style=0)
        self.butGetStgPos.SetMinSize(wx.Size(0, 0))
        self.butGetStgPos.SetToolTipString(u'Records the current position of the stage for the hightighted sample on the left')
        self.butGetStgPos.Bind(wx.EVT_BUTTON, self.OnButGetStgPosButton,
              id=wxID_GUI_ROBOTBUTGETSTGPOS)

        self.butSetStgPos = wx.Button(id=wxID_GUI_ROBOTBUTSETSTGPOS,
              label=u'Move Stage', name=u'butSetStgPos', parent=self,
              pos=wx.Point(424, 256), size=wx.Size(120, 32), style=0)
        self.butSetStgPos.Bind(wx.EVT_BUTTON, self.OnButSetStgPosButton,
              id=wxID_GUI_ROBOTBUTSETSTGPOS)

        self.staTRXX = wx.StaticText(id=wxID_GUI_ROBOTSTATRXXD,
              label=u'TRXXd:', name=u'staTRXX', parent=self, pos=wx.Point(424,
              96), size=wx.Size(49, 17), style=0)

        self.staTRZZ = wx.StaticText(id=wxID_GUI_ROBOTSTATRZZD,
              label=u'TRZZd:', name=u'staTRZZ', parent=self, pos=wx.Point(424,
              112), size=wx.Size(51, 17), style=0)

        self.staTRYV = wx.StaticText(id=wxID_GUI_ROBOTSTATRYV, label=u'TRY:',
              name=u'staTRYV', parent=self, pos=wx.Point(424, 224),
              size=wx.Size(39, 17), style=0)

        self.staTRX = wx.StaticText(id=wxID_GUI_ROBOTSTATRXD, label=u'TRXd:',
              name=u'staTRX', parent=self, pos=wx.Point(424, 144),
              size=wx.Size(40, 17), style=0)

        self.staTRZ = wx.StaticText(id=wxID_GUI_ROBOTSTATRZD, label=u'TRZd:',
              name=u'staTRZ', parent=self, pos=wx.Point(424, 144+16),
              size=wx.Size(41, 17), style=0)
        self.staGOXX = wx.StaticText(label=u'GOXX:',
              name=u'staGOXX', parent=self, pos=wx.Point(424, 144+32),
              size=wx.Size(40, 17), style=0)

        self.staGOZZ = wx.StaticText(label=u'GOZZ:',
              name=u'staGOZZ', parent=self, pos=wx.Point(424, 144+48),
              size=wx.Size(41, 17), style=0)
        

        self.staticText3 = wx.StaticText(id=wxID_GUI_ROBOTSTATICTEXT3,
              label=u'Sample Pos:', name='staticText3', parent=self,
              pos=wx.Point(328, 344), size=wx.Size(80, 17), style=0)

        self.staRobotStatus = wx.StaticText(id=wxID_GUI_ROBOTSTAROBOTSTATUS,
              label=u'System Status', name=u'staRobotStatus', parent=self,
              pos=wx.Point(7, 473), size=wx.Size(92, 17), style=0)
        self.staRobotStatus.SetToolTipString(u'Status of Robot and availability to accept a command')

        self.staSampleError = wx.StaticText(id=wxID_GUI_ROBOTSTASAMPLEERROR,
              label=u'Error', name=u'staSampleError', parent=self,
              pos=wx.Point(328, 392), size=wx.Size(32, 17), style=0)


        self.spinStageMemory = wx.SpinCtrl(id=wxID_GUI_ROBOTSPINSTAGEMEMORY,
              initial=0, max=1, min=0, name=u'spinStageMemory', parent=self,
              pos=wx.Point(512, 48), size=wx.Size(31, 27),
              style=wx.SP_ARROW_KEYS)
        self.spinStageMemory.SetRange(0, 0)
        self.spinStageMemory.SetHelpText(u'Allows multiple regions of interest per sample')
        self.spinStageMemory.SetToolTipString(u'Each sample can have multiple regions of interest use this in coordination with the Record button to set each. They are denoted by _P+number in the script')
        self.spinStageMemory.Bind(wx.EVT_SPINCTRL,
              self.OnSpinStageMemorySpinctrl, id=wxID_GUI_ROBOTSPINSTAGEMEMORY)

        self.staStageStatus = wx.StaticText(id=wxID_GUI_ROBOTSTASTAGESTATUS,
              label=u'', name=u'staStageStatus', parent=self, pos=wx.Point(440,
              26), size=wx.Size(80, 17), style=0)

        self.chkToolTips = wx.CheckBox(id=wxID_GUI_ROBOTCHKTOOLTIPS,
              label=u'Tooltips', name=u'chkToolTips', parent=self,
              pos=wx.Point(656, 144), size=wx.Size(88, 24), style=0)
        self.chkToolTips.SetValue(False)
        self.chkToolTips.Bind(wx.EVT_CHECKBOX, self.OnChkToolTipsCheckbox,
              id=wxID_GUI_ROBOTCHKTOOLTIPS)

        self.butSetLoad = wx.Button(id=wxID_GUI_ROBOTBUTSETLOAD,
              label=u'Record Load', name=u'butSetLoad', parent=self,
              pos=wx.Point(648, 168), size=wx.Size(96, 32), style=0)
        self.butSetLoad.Enable(False)
        self.butSetLoad.Bind(wx.EVT_BUTTON, self.OnButSetLoadButton,
              id=wxID_GUI_ROBOTBUTSETLOAD)

        self.butMoveLoad = wx.Button(id=wxID_GUI_ROBOTBUTMOVELOAD,
              label=u'Move Load', name=u'butMoveLoad', parent=self,
              pos=wx.Point(648, 200), size=wx.Size(88, 24), style=0)
        self.butMoveLoad.Enable(False)
        self.butMoveLoad.Bind(wx.EVT_BUTTON, self.OnButMoveLoad,
              id=wxID_GUI_ROBOTBUTMOVELOAD)
        self.butClearPos = wx.lib.buttons.GenButton(
              label=u'Clear', name=u'butClearPos', parent=self,
              pos=wx.Point(424, 48+32), size=wx.Size(48, 16), style=0)
        self.butClearPos.SetForegroundColour(wx.Colour(255, 0, 0))
        self.butClearPos.Bind(wx.EVT_BUTTON, self.OnButClearPosButton)
        
        self.butDBLoadPos = wx.lib.buttons.GenButton(
              label=u'Sample from DB', name=u'butDBLoadPos', parent=self,
              pos=wx.Point(424+48, 48+32), size=wx.Size(72, 16), style=0)
        self.butDBLoadPos.SetForegroundColour(wx.Colour(0, 255, 0))
        self.butDBLoadPos.Bind(wx.EVT_BUTTON, self.OnButDBLoadPosButton)
        

    def __init__(self, parent,mainPtr):
        self._init_ctrls(parent)
        self.mainPtr=mainPtr
        self.lockOutStage={}
        self.lockOutStage['RobotUnterwegs']=0
        self.lockOutStage['ButClicked']=0
        self.lockOutStage['ReadingStage']=0
        self.lockOutStage['StageUnterwegs']=0
        self.lockOutStage['RobotOff']=0
        self.mainPtr.kRegisterEvent('robotStageUpdate',self.dispRobotStatus) # robotStatusUpdate
        self.mainPtr.kRegisterEvent('dispControlsLock',self.dispControlsLock) # lock and unlock controls
        #self.mainPtr.kRegisterEvent('updatePositionFields',self.updatePositionFields)
        self.mainPtr.kRegisterEvent('robotLoad',self.OnButLoadEvent)
        self.mainPtr.kRegisterEvent('robotUnload',self.OnButUnloadEvent)
        
        self.mainPtr.kRegisterEvent('pollStage',self.pollStage)
        self.mainPtr.kRegisterEvent('updatePositionFields',self.updatePositionFieldsEvent)
        self.mainPtr.kRegisterEvent('rbSelectCell',self.selectCell)
        self.mainPtr.kRegisterEvent('pushTrayToDB',self.pushTrayToDB)
        self.mainPtr.kRegisterEvent('pullTrayFromDB',self.pullTrayFromDB)
        self.mainPtr.kRegisterEvent('generateScript',self.GenerateScriptEvent)
        self.mainPtr.kRegisterTimerEvent(self.robotQueryStatus)
        self.trayPosSelect=0
        self.DCLUp=self.mainPtr.DCLUp
        self.allesAus=0
        self.InitializeGrid()
        self.lastRobotAliveCheck=time.time()
        # this allows multiple factors to lock and unlock the stage and robot
        # controls
        
        
    # Handler Functions
    def OnTrayPosSelectGridCellLeftDclick(self, event):
        self.DCLUp('ButClicked',1)
        cRow=event.GetRow()
        cCol=event.GetCol()
        self.FlipLoaded(cRow,cCol)
        self.DCLUp('ButClicked',0)

    def OnTrayPosSelectGridSelectCell(self, event):
        self.DCLUp('ButClicked',1)
        cRow=event.GetRow()
        cCol=event.GetCol()
        self.mainPtr.kPostEvent('rbSelectCell',[cRow,cCol])
        event.Skip()
        self.DCLUp('ButClicked',0)
    def OnTxtSampleNameText(self, event):

        cCol=self.trayPosSelect.GetGridCursorCol()
        cRow=self.trayPosSelect.GetGridCursorRow()
        if (self.staCurPos.GetLabel()==self.trayPosSelect.GetCellValue(cRow,cCol)):
            self.mainPtr.CurTray[cRow][cCol][0]=self.txtSampleName.GetValue().strip().replace(' ','_')
            self.mainPtr.CurTray[cRow][cCol][1]=self.txtSampleDescription.GetText()
        self.redrawGrid()
        self.updateWarnings(cRow,cCol)
        event.Skip()
    

    def OnButLoadButton(self, event):
        self.DCLUp('ButClicked',1)
        cCol=self.trayPosSelect.GetGridCursorCol()
        cRow=self.trayPosSelect.GetGridCursorRow()
        sampleName=self.getSampleName(cRow,cCol,self.spinStageMemory.GetValue())
        # update dictionary so the command works
        oCgVal=self.mainPtr.CurTray[cRow][cCol][2]
        self.mainPtr.CurTray[cRow][cCol][2]=1
        self.mainPtr.kPostEvent('generateScript',[0])
        #self.mainPtr.CurTray[cRow][cCol][2]=oCgVal
        # post event
        self.mainPtr.kPostEvent('robotLoad',[cCol,cRow,sampleName])
        self.DCLUp('ButClicked',0)
    def OnButLoadEvent(self,event):
        myRobot=event.myRobot
        myRobotScript=event.myRobotScript  
        [cCol,cRow,sampleName]=event.argBundle  
        
        if (myRobot.mode()==2): # already loaded
            print 'Unloading Sample First!!'
            myRobotScript.cmd_IMUNMOUNT([]) # this command will run in real time
            time.sleep(4) # wait a bit after the unmount
        if (myRobot.mode()==1): # already loaded
            print "mounting:"+sampleName
            myRobotScript.cmd_IMMOUNT([sampleName])
            errRpt=myRobot.ValidateRobot(dMode=2,dStagePos=1,dRow=cRow,dCol=cCol)
            print 'Error Report ('+str(len(errRpt))+') : '+'\n'.join(errRpt)
        self.OnRefreshGridDisplay()
        event.Skip()

    def OnButUnloadButton(self, event):
        self.DCLUp('ButClicked',1)
        self.mainPtr.kPostEvent('generateScript',[0])
        self.mainPtr.kPostEvent('robotUnload',[])
        self.DCLUp('ButClicked',0)
    def OnButUnloadEvent(self,event):
        #myRobotScriptPtr.ScriptDict=myRobotScript.ScriptDict
        myRobot=event.myRobot
        myRobotScript=event.myRobotScript
        myRobotScript.cmd_IMUNMOUNT([])
        errRpt=myRobot.ValidateRobot(dMode=1,dStagePos=0)
        print 'Error Report ('+str(len(errRpt))+') : '+'\n'.join(errRpt)
        self.OnRefreshGridDisplay()
    def OnButGetStgPosButton(self, event):
        self.DCLUp('ButClicked',1)
        cCol=self.trayPosSelect.GetGridCursorCol()
        cRow=self.trayPosSelect.GetGridCursorRow()
        cStgMem=self.spinStageMemory.GetValue()
        self.DCLUp('ReadStage',1)
        self.mainPtr.kPostEvent('pollStage',[cRow,cCol,cStgMem])
        event.Skip()
        self.DCLUp('ButClicked',0)    
    def OnRefreshGridDisplay(self):
        cCol=self.trayPosSelect.GetGridCursorCol()
        cRow=self.trayPosSelect.GetGridCursorRow()
        self.mainPtr.kPostEvent('rbSelectCell',[cRow,cCol])
    def OnButSetStgPosButton(self, event):
        self.DCLUp('ButClicked',1)
        cCol=self.trayPosSelect.GetGridCursorCol()
        cRow=self.trayPosSelect.GetGridCursorRow()
        cStgMem=self.spinStageMemory.GetValue()
        if len(self.mainPtr.CurTray[cRow][cCol][3])>cStgMem:
            cStg=self.mainPtr.CurTray[cRow][cCol][3][cStgMem]
            self.mainPtr.kPostEvent('putStage',[cStg])
        else:
            wx.MessageBox('Position Not Correctly Loaded')
        
        event.Skip()
        self.DCLUp('ButClicked',0)
        

    def OnButClearPosButton(self, event):
        cCol=self.trayPosSelect.GetGridCursorCol()
        cRow=self.trayPosSelect.GetGridCursorRow()
        self.mainPtr.CurTray[cRow][cCol][3]=[]
        self.spinStageMemory.SetValue(0)
        self.OnSpinStageMemorySpinctrl(event)
        
        event.Skip()
    def OnButDBLoadPosButton(self, event):
        cCol=self.trayPosSelect.GetGridCursorCol()
        cRow=self.trayPosSelect.GetGridCursorRow()
        self.mainPtr.CurTray[cRow][cCol][3]=[]
        print 'pulling tray'
        # let user select TrayId
        #[trayId]=event.argBundle
        sList=X_ROBOT_X02DA_database.xdGetAllSamplesInTrays()
        sList.sort()
        sIndex=wx.GetSingleChoiceIndex('Select Sample to Load:','UserGUI_Robot',sList)
        if sIndex>=0:
            sampleName=sList[sIndex]
            unsereSampleIst=X_ROBOT_X02DA_database.xdGetSample(sampleName)
            print 'Before'
            print self.mainPtr.CurTray[cRow][cCol]
            print 'After'
            print unsereSampleIst
            self.mainPtr.CurTray[cRow][cCol]=unsereSampleIst
            self.OnRefreshGridDisplay()
        else:
            print 'User Cancelled Loading!'
        
        event.Skip()
    def OnSpinStageMemorySpinctrl(self, event):
        self.DCLUp('ButClicked',1)
        cCol=self.trayPosSelect.GetGridCursorCol()
        cRow=self.trayPosSelect.GetGridCursorRow()
        self.updatePositionFields(cRow,cCol,self.spinStageMemory.GetValue())
        self.updateWarnings(cRow,cCol)
        event.Skip()
        self.DCLUp('ButClicked',0)

    def OnChkToolTipsCheckbox(self, event):
        self.DCLUp('ButClicked',1)
        wx.ToolTip.Enable(self.chkToolTips.GetValue())
        event.Skip()
        self.DCLUp('ButClicked',0)
    def OnButSequencerButton(self, event):
        print 'nix'
    def OnButSetLoadButton(self, event):
        self.DCLUp('ButClicked',1)
        event.Skip()
        self.DCLUp('ButClicked',0)
    def OnButMoveLoad(self, event):
        self.DCLUp('ButClicked',1)
        event.Skip()
        self.DCLUp('ButClicked',0)
# Custom Functions
    def InitializeGrid(self,mRows=tSIZEROWS,mCols=tSIZECOLS):
        self.mainPtr.CurTray=CreateBlankGrid(mRows,mCols)
        self.createGrid()
    def FlipLoaded(self,cRow,cCol,repaint=1):
            
        if cRow<0:
            for ij in range(0,len(self.mainPtr.CurTray)): self.FlipLoaded(ij,cCol,0)
        elif cCol<0:
            for ij in range(0,len(self.mainPtr.CurTray[cRow])): self.FlipLoaded(cRow,ij,0)
        else:
            if self.mainPtr.CurTray[cRow][cCol][2]>0:
                self.mainPtr.CurTray[cRow][cCol][2]=0
            else:
                self.mainPtr.CurTray[cRow][cCol][2]=1
            
        if (repaint):
            self.redrawGrid()
    def selectCell(self,event):
        myRobot=event.myRobot
        [cRow,cCol]=event.argBundle
        if self.mainPtr.IsTrayPositionOpen(row=cRow,col=cCol):
        
            #cColR=self.trayPosSelect.GetGridCursorCol()
            #cRowR=self.trayPosSelect.GetGridCursorRow()
            #if ((cRow==cRowR) &(cCol==cColR)):
            self.txtSampleName.SetValue(self.mainPtr.CurTray[cRow][cCol][0])
            self.txtSampleDescription.SetText(self.mainPtr.CurTray[cRow][cCol][1])
            self.staCurPos.SetLabel(self.trayPosSelect.GetCellValue(cRow,cCol))
            self.spinStageMemory.SetValue(0)
            self.spinStageMemory.SetRange(0,len(self.mainPtr.CurTray[cRow][cCol][3]))
            self.updatePositionFields(cRow,cCol,0)
            self.updateWarnings(cRow,cCol)
            
            rRow=myRobot.currentRow
            rCol=myRobot.currentCol
            if ((cRow==rRow) & (cCol==rCol)) or (rRow<0 or rCol<0):
                self.butLoad.Shown=True
                self.butLoad.SetLabel('Load Sample')
                self.butUnload.Shown=True
            else:
                self.butLoad.Shown=True
                self.butLoad.SetLabel('Change Sample')
                self.butUnload.Shown=False
        else:
            
            for ij in range(0,tSIZECOLS):
                for ik in range(0,tSIZEROWS):
                    if self.mainPtr.IsTrayPositionOpen(row=ij,col=ik):
                        self.trayPosSelect.SetGridCursor(ij,ik)
                        self.mainPtr.kPostEvent('rbSelectCell',[ij,ik])
                        return 1
            return 0
    def updateWarnings(self,cRow,cCol):    
        cName=tArray[cCol]+cRow.__str__()
        erMsg=''
        if (len(self.mainPtr.CurTray[cRow][cCol][3])>self.spinStageMemory.GetValue()):
            if (len(self.mainPtr.CurTray[cRow][cCol][3][self.spinStageMemory.GetValue()])<1):
                erMsg+='Pos Empty\n'
        else:
            erMsg+='Pos Empty\n'
        if (self.mainPtr.CurTray[cRow][cCol][0]==cName):
            erMsg+='Name Wrong'
        self.staSampleError.SetForegroundColour('red')
        self.staSampleError.Shown=(len(erMsg)>0)
        self.staSampleError.SetLabel(erMsg)
        #else:
        #    self.trayPosSelect.SetGridCursor(cRow,cCol)
    def getSampleName(self,cRow,cCol,cSpin):
        cPosNSuffix=''
        spinLen=len(self.mainPtr.CurTray[cRow][cCol][3])
        if spinLen>1:
            cPosNSuffix='_P'+str(min([cSpin,spinLen-1]))
        return self.mainPtr.CurTray[cRow][cCol][0]+cPosNSuffix  
    def GenerateScriptEvent(self,event):
        #generates the script and dictionary to run on the sequencer
        # the saveScript option is so both programs can utilize the 
        # robotScript commands for mounting and unmounting reducing
        # the likelyhood of error
        if len(event.argBundle)>0:
            saveScript=event.argBundle[0]
        else:
            saveScript=1
        myRobotScript=event.myRobotScript
        oldScript=myRobotScript.sequenceText
        myRobotScript.ScriptDict={}
        # Add Load Position
        myRobotScript.sequenceText=''
        #myRobotScript.ScriptDict['LoadPos']=[-1,-1,self.mainPtr.curLoadPos]
        for ik in range(0,len(self.mainPtr.CurTray[0])):
            for ij in range(0,len(self.mainPtr.CurTray)):
                if self.mainPtr.CurTray[ij][ik][2]:
                    for cPos in range(0,len(self.mainPtr.CurTray[ij][ik][3])):
                        
                        cPosSuffix=''
                        if len(self.mainPtr.CurTray[ij][ik][3])>1:
                            cPosSuffix=', stage pos '+cPos.__str__()
                        commentSuffix='# tray pos '+tArray[ik]+ij.__str__()
                        myRobotScript.sequenceText+='IMSAMPLE("'+self.getSampleName(ij,ik,cPos)+'")'+commentSuffix+cPosSuffix+'\n'
                        myRobotScript.ScriptDict[self.getSampleName(ij,ik,cPos)]=[ik,ij,self.mainPtr.CurTray[ij][ik][3][cPos]]
                    if len(self.mainPtr.CurTray[ij][ik][3])==0:
                        commentSuffix='# tray pos '+tArray[ik]+ij.__str__()
                        myRobotScript.sequenceText+='IMSAMPLE("'+self.getSampleName(ij,ik,0)+'")'+commentSuffix+', empty/default stage pos\n'
                        myRobotScript.ScriptDict[self.mainPtr.CurTray[ij][ik][0]]=[ik,ij,{}]
        if not saveScript:
            myRobotScript.sequenceText=oldScript # replace script with old version
        else:
            self.mainPtr.kPostEvent('gsPullScript',[])
        self.mainPtr.kPostEvent('refreshSampleList',[])
    def pollStage(self,event):
        [cRow,cCol,cStgMem]=event.argBundle
        self.mainPtr.kPostEvent('readStage',[cRow,cCol,cStgMem])
        #eval('self.sta'+self.fields[i]+'.SetLabel("'+self.fields[i]+':'+cVal.__int__().__str__()+'")')
        
    
    def updatePositionFields(self,cRow=-1,cCol=-1,cStgMem=-1):
        if ((cRow<0) or (type(cRow)!=type(1))): cRow=self.trayPosSelect.GetGridCursorRow()
        if ((cCol<0) or (type(cRow)!=type(1))): cCol=self.trayPosSelect.GetGridCursorCol()
        if ((cStgMem<0) or (type(cRow)!=type(1))): cStgMem=self.spinStageMemory.GetValue()
        #print (cRow,cCol,cStgMem)
        # load in the current positions (if exist or blanks if not)
        
        if cStgMem<len(self.mainPtr.CurTray[cRow][cCol][3]):
            for [cVar,dVal] in self.mainPtr.StageChannels:
                eval('self.sta'+cVar+'.SetLabel("'+cVar+': _")')
        
            cItems=self.mainPtr.CurTray[cRow][cCol][3][cStgMem].items()
            for ijr in range(0,len(cItems)):
                cVar=cItems[ijr][0]
                eval('self.sta'+cVar+'.SetLabel("'+cVar+':'+str(int(cItems[ijr][1]))+'")')
        self.spinStageMemory.SetRange(0,len(self.mainPtr.CurTray[cRow][cCol][3]))
        self.redrawGrid()
        #self.butGetStgPos.Enable(True)
        self.updateWarnings(cRow,cCol)
    def redrawGrid(self):
        
        #print dir(self.trayPosSelect)
        #self.trayPosSelect.ResetView()
        #self.trayPosSelect.Destroy()
        goodValues=1
        errors=0
        
        
        for ij in range(0,len(self.mainPtr.CurTray)):
            curRow=[]
            for ik in range(0,len(self.mainPtr.CurTray[ij])):
                
                cName=tArray[ik]+ij.__str__()
                self.trayPosSelect.SetCellValue(ij,ik,cName)
                goodValues=self.mainPtr.IsTrayPositionOpen(cName)
                if not goodValues:
                    self.trayPosSelect.SetCellRenderer(ij,ik,wx.grid.GridCellBoolRenderer())
                    self.mainPtr.CurTray[ij][ik][2]=0
                if ((self.mainPtr.CurTray[ij][ik][2])):
                    if ((len(self.mainPtr.CurTray[ij][ik][3])>0) and (not (self.mainPtr.CurTray[ij][ik][0]==cName))):
                        # green=good to go
                        
                        self.trayPosSelect.SetCellBackgroundColour(ij,ik,'green')
                    else:
                        # yellow means no position yet, probably not good
                        errors+=1
                        self.trayPosSelect.SetCellBackgroundColour(ij,ik,'yellow')
                else:
                    self.trayPosSelect.SetCellBackgroundColour(ij,ik,'white')
                if len(self.mainPtr.CurTray[ij][ik][3])>0:
                    # blue means position loaded
                    self.trayPosSelect.SetCellTextColour(ij,ik,'blue')
                else:
                    self.trayPosSelect.SetCellTextColour(ij,ik,'black')
                    
                
        self.trayPosSelect.AutoSize()
        self.trayPosSelect.DisableDragColSize()
        self.trayPosSelect.DisableDragRowSize()
        self.trayPosSelect.ForceRefresh()
        if goodValues:
            if ((errors==0)):
                self.bxSample.SetForegroundColour('green')
            else:
                self.bxSample.SetForegroundColour('red')
        else:
            
            self.bxSample.SetForegroundColour('black')
        
        
        
        return errors    
    def createGrid(self):
        #id=wxID_FRAME1TRAYPOSSELECT,
        if not (type(self.trayPosSelect)==type(0)):
            self.trayPosSelect.Destroy()
        
        self.trayPosSelect = wx.grid.Grid(
              name=u'trayPosSelect', parent=self, pos=wx.Point(8, 24),
              size=wx.Size(392, 264), style=0)
        self.trayPosSelect.EnableEditing(False)
        self.trayPosSelect.SetMinSize(wx.Size(0, 0))
        #self.trayPosSelect.Bind(wx.EVT_ENTER_WINDOW,
        #      self.OnTrayPosSelGridEditorCreated)
        self.trayPosSelect.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK,
              self.OnTrayPosSelectGridCellLeftDclick)
        self.trayPosSelect.Bind(wx.grid.EVT_GRID_SELECT_CELL,
              self.OnTrayPosSelectGridSelectCell)
        self.trayPosSelect.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK,
              self.OnTrayPosSelectGridCellLeftDclick)
        self.trayPosSelect.Bind(wx.grid.EVT_GRID_LABEL_LEFT_DCLICK,
              self.OnTrayPosSelectGridCellLeftDclick)
        self.trayPosSelect.Bind(wx.grid.EVT_GRID_LABEL_RIGHT_CLICK,
              self.OnTrayPosSelectGridCellLeftDclick)
        self.trayPosSelect.SetToolTipString(u'Click to select tray location, right or double click to change loading status (white means no load, green = load, yellow=load but error)')
        self.trayPosSelect.CreateGrid(len(self.mainPtr.CurTray),len(self.mainPtr.CurTray[0]))
        
        for ik in range(0,len(self.mainPtr.CurTray[0])):
            self.trayPosSelect.SetColLabelValue(ik,tArray[ik])
        for ij in range(0,len(self.mainPtr.CurTray)):
            self.trayPosSelect.SetRowLabelValue(ij,ij.__str__())
        self.redrawGrid()
        self.trayPosSelect.SetGridCursor(0,0)
    def pushTrayToDB(self,event):
        print 'pushing tray'
        [trayId]=event.argBundle
        mbs=event.myRobotScript
        tList=X_ROBOT_X02DA_database.xGetTrayList()
        gAhead=1
        if sum([trayId.upper()==tEle for tEle in tList])>0:
            gAhead=wx.GetSingleChoiceIndex('Tray Already Exists, Overwrite?','UserGUI_Robot',['No','Yes'])
        if gAhead:
            X_ROBOT_X02DA_database.xCreateTray(trayId,self.mainPtr.CurTray,mbs.sequenceText)
        #X_ROBOT_X02DA_database.xCreateTray('debugTray',self.mainPtr.CurTray)
    def pullTrayFromDB(self,event):
        print 'pulling tray'
        # let user select TrayId
        #[trayId]=event.argBundle
        tList=X_ROBOT_X02DA_database.xGetTrayList()
        tIndex=wx.GetSingleChoiceIndex('Select Tray to Load:','UserGUI_Robot',tList)
        if tIndex>=0:
            trayId=tList[tIndex]
            [self.mainPtr.CurTray,event.myRobotScript.sequenceText]=X_ROBOT_X02DA_database.xGetWholeTray(trayId)
            self.mainPtr.kPostEvent('gsInit',[])
            self.createGrid()
        else:
            print 'User Cancelled Loading!'
    def exportXML(self,doc,tray):
        
        tray.setAttribute("cols", len(self.mainPtr.CurTray[0]).__str__())
        tray.setAttribute("rows", len(self.mainPtr.CurTray).__str__())
        
        
        # Create the main <card> element
        for ik in range(0,len(self.mainPtr.CurTray[0])):
            for ij in range(0,len(self.mainPtr.CurTray)):
                if self.mainPtr.CurTray[ij][ik][2]:
                    
                    sample = doc.createElement("Sample")
                    cPos=tArray[ik]+ij.__str__()
                    sample.setAttribute("position", cPos)
                    sample.setAttribute("row-index", str(ij))
                    sample.setAttribute("col-index", str(ik))
                    tray.appendChild(sample)
                    # create name field
                    sName = doc.createElement("name")
                    sample.appendChild(sName)
                    ptext = doc.createTextNode(self.mainPtr.CurTray[ij][ik][0])
                    sName.appendChild(ptext)
                    # Create description field
                    desc = doc.createElement("desc")
                    sample.appendChild(desc)
                    # Give the <p> elemenet some text
                    ptext = doc.createTextNode(self.mainPtr.CurTray[ij][ik][1])
                    desc.appendChild(ptext)
                    posLen=len(self.mainPtr.CurTray[ij][ik][3])
                    # add Saved Positions Array
                    for ijr in range(0,posLen):
                        pos = doc.createElement("stage_position")
                        pos.setAttribute("id", str(ijr))
                        pos.setAttribute("mode",str(self.mainPtr.operationMode))
                        appStr=''
                        if posLen>1: appStr='_P'+str(ijr)
                        pos.setAttribute("scriptID",self.mainPtr.CurTray[ij][ik][0]+appStr)
                        sample.appendChild(pos)
                        for ijk in range(0,len(self.mainPtr.CurTray[ij][ik][3][ijr])):
                            cItem=self.mainPtr.CurTray[ij][ik][3][ijr].items()[ijk]
                            posEle = doc.createElement("StageChannel")
                            posEle.setAttribute("name", cItem[0])
                            posEle.setAttribute("value", cItem[1].__str__())
                            pos.appendChild(posEle)
        return tray
    def importXML(self,xmlNodes):
        # reads the tray from the xml file
        self.mainPtr.CurTray=ReadTrayFromXML(xmlNodes)
        self.createGrid()

    # These two functions handle the updating of the display from the robot parameters
    # In a thread-safe fashion
    def DCLUp(self,node,val):
        self.mainPtr.kPostEvent('dispControlsLock',[node,val])
    def updatePositionFieldsEvent(self,event):
        self.updatePositionFields()
    def dispControlsLock(self,event):
        # this function handles events to lock and unlock stage elements
        [evtName,evtVal]=event.argBundle
        # getStgPos click
        oldStatus=0
        for losVal in self.lockOutStage.values():
            oldStatus+=losVal
        if self.lockOutStage.has_key(evtName):
            self.lockOutStage[evtName]=evtVal 
        # update robot and stage controls
        oStatus=0
        for losVal in self.lockOutStage.values():
            oStatus+=losVal
        if (oStatus>0)==(oldStatus>0): # nothing new
            if oStatus>0:
                # temporarily
                #self.butGetStgPos.Enable(False)
                #self.butSetStgPos.Enable(False)
                
                #self.butSaveFile.Enable(False)
                #self.butQuickSave.Enable(False)
                self.butMoveLoad.Enable(False)
                self.butSetLoad.Enable(False)
                #self.butSequencer.Enable(False)
                #self.butLoadFile.Enable(False)
                #self.butStartRbbot.Enable(False)
                self.butLoad.Enable(False)
                self.butUnload.Enable(False)
            else:
                self.butGetStgPos.Enable(True)
                self.butSetStgPos.Enable(True)
                #self.butStartRbbot.Enable(True)
                #self.butSaveFile.Enable(True)
                #self.butQuickSave.Enable(True)
                self.butMoveLoad.Enable(True)
                self.butSetLoad.Enable(True)
                #self.butSequencer.Enable(True)
                #self.butLoadFile.Enable(True)
                self.butLoad.Enable(True)
                self.butUnload.Enable(True)
        # robot off
        #if self.lockOutStage['RobotOff']==1: self.butStartRbbot.Enable(True)
        if evtName=='StageLoaded':
            if evtVal==0:
                self.butUnload.Enable(False)
    def robotQueryStatus(self,event):
        robotPtr=event.myRobot
        robotScriptPtr=event.myRobotScript
        [futureBnd]=event.argBundle
        #cStat=robotPtr.rstatusCH.getVal()
        mode=robotPtr.mode()
        if mode==-1:
            mode=-1
            ready=0
            stageMoving=robotPtr.stageMoving()
            currentRow=-1
            currentCol=-1
        else:
            ready=robotPtr.ready()
            stageMoving=robotPtr.stageMoving()
            robotPtr.updateCurrentPos()
            currentRow=robotPtr.currentRow
            currentCol=robotPtr.currentCol
        if (time.time()-self.lastRobotAliveCheck)>15: # check every 10 seconds
            if mode==0:
                print 'Disabled Mode Changing'
                #robotPtr.setMode(-1)
            else:
                print 'Disabled Mode Changing'
                #robotPtr.setMode(0) # simulate the robot being off
            self.lastRobotAliveCheck=time.time()
            # check every 15 seconds
        
            
        #print (currentRow,currentCol)
        
        self.mainPtr.kPostEvent('robotStageUpdate',[mode,ready,stageMoving,currentRow,currentCol])
        
    def dispRobotStatus(self,event):
            [mode,ready,stageMoving,cRow,cCol]=event.argBundle
            #[mode,ready,stageMoving]=event.argBundle
            txtStat=''
            if mode>-1:
                if self.allesAus:
                    self.allesAus=0
                    for dEl in self.__dict__.keys():
                        try:
                            self.__dict__[dEl].Enable(True)
                        except:
                            print 'Cant do that : '+dEl
            if mode==0:
                txtStat+='Roboter is Off'
                self.DCLUp('RobotOff',1)
                #self.butStartRbbot.SetBackgroundColour('green')
            elif mode==1:
                txtStat+='Roboter is Unloaded'
                self.DCLUp('RobotOff',0)
                self.DCLUp('StageLoaded',0)
                self.butLoad.SetLabel('Load Sample')
                #self.butStartRbbot.SetBackgroundColour('red')    
            elif mode==2:
                txtStat+='Roboter is Loaded'
                self.DCLUp('RobotOff',0)
                self.DCLUp('StageLoaded',1)
                #self.butStartRbbot.SetBackgroundColour('red')
                self.butLoad.SetLabel('Change Sample')
            else:
                txtStat+='Error in Roboter Status'
                #self.butStartRbbot.SetBackgroundColour('green')
                self.DCLUp('RobotOff',1)
                if self.allesAus<1:
                    self.allesAus=1
                    for dEl in self.__dict__.keys():
                        try:
                            if (dEl!='mainPtr'):
                                self.__dict__[dEl].Enable(False)
                        except:
                            print 'Cant do that : '+dEl
                            
                    
            if (cCol>=-1) & (cRow>=-1):
                self.trayPosSelect.SetCellTextColour(cRow,cCol,'red')
                self.trayPosSelect.ForceRefresh()
                if mode==2:
                    txtStat+=' in position '+str((cRow,cCol))
            if ready==1:
                txtStat+=', and READY for next command.'
                self.DCLUp('RobotUnterwegs',0)
            elif ready==0:
                txtStat+=', and NOT READY for next command.'
                self.DCLUp('RobotUnterwegs',1)
            else:
                txtStat+=', and has an unknown status.'
                self.DCLUp('RobotUnterwegs',1)
            #print txtStat
            if stageMoving:
                #self.bxStage.SetForegroundColour('green')
                self.staStageStatus.SetLabel('Stage Moving')
                txtStat+=' The stage is MOVING'
                self.staStageStatus.SetForegroundColour('red')
                self.DCLUp('StageUnterwegs',1)
            else:
                #self.bxStage.SetForegroundColour('red')
                self.staStageStatus.SetLabel('Stage Ready')
                txtStat+=' The stage is not moving and READY'
                self.staStageStatus.SetForegroundColour('green')
                self.DCLUp('StageUnterwegs',0)
            

            self.staRobotStatus.SetLabel(txtStat)
class GUI_RobotExpert(wx.Panel):
    version=20100204
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        # return to frame to edit
        wx.Panel.__init__(self,prnt)
        self.staticBox1 = wx.StaticBox(label=u'Scan Settings', name='staticBox1', parent=self,
              pos=wx.Point(552-552, 8), size=wx.Size(200, 112), style=0)
        
        self.butReStartRbbot = wx.Button(label=u'Restart EPICS', name=u'butReStartRbbot', parent=self,
              pos=wx.Point(400, 500), size=wx.Size(120, 32), style=0)
        self.butReStartRbbot.SetToolTipString(u'Restarts the Robots Epic Server (Use after robot has been turned off and on again)')
        self.butReStartRbbot.Bind(wx.EVT_BUTTON, self.OnButReStartRbbotButton)
        self.butStartRbbot = wx.Button(
              label=u'Start Robot', name=u'butStartRbbot', parent=self,
              pos=wx.Point(280, 500), size=wx.Size(120, 32), style=0)
        self.butStartRbbot.SetToolTipString(u'Command to start the robot. The robot will forget if a sample is mounted and move through its warmup routine')
        self.butStartRbbot.Bind(wx.EVT_BUTTON, self.OnButStartRbbotButton)
        self.butStartRbbot.SetBackgroundColour('green')
        self.butReStartRbbot.SetBackgroundColour('red')
        
        self.butKillSequencer = wx.Button(
              label=u'Kill Sequencer', name=u'butKillSequencer', parent=self,
              pos=wx.Point(280-120, 500), size=wx.Size(120, 32), style=0)
        self.butKillSequencer.SetToolTipString(u'Will kill all running dbSequencer commands')
        self.butKillSequencer.Bind(wx.EVT_BUTTON, self.OnButKillSequencer)
        self.butKillSequencer.SetBackgroundColour('yellow')
    def __init__(self, parent,mainPtr):
        self._init_ctrls(parent)
        self.mainPtr=mainPtr
        #self.mainPtr.kRegisterTimerEvent(self.timerEvent)
            
    def exportXML(self,doc,userEle):
        print 'None Written'
    def importXML(self,xmlNodes):
        print 'None Written'
    def OnButStartRbbotButton(self, event):
        self.mainPtr.kPostEvent('startRobot',[])
    def OnButReStartRbbotButton(self, event):
        self.mainPtr.kPostEvent('restartRobot',[])
    def OnButKillSequencer(self, event):
        self.mainPtr.kPostEvent('killSequencer',[])
    
        