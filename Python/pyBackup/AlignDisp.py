#Boa:Frame:Frame1

import wx
import wx.lib.masked.textctrl
import wx.stc
import wx.grid
import threading
import os
import pickle
import time
import thread
try:
    import X_ROBOT_X02DA_robotCommon
except:
    print "Initial robotCommon not found!"
    try:
        sys.path.insert (0, os.path.expandvars ("$SLSBASE/sls/bin/"))
        import  X_ROBOT_X02DA_robotCommon
    except:
        wx.MessageBox('RobotCommon Python Library is needed to run this program!')
        sys.exit (1)
try:
    from  X_ROBOT_X02DA_robotScript import *
except:

    print "Initial robotScript not found!"
    try:
        sys.path.insert (0, os.path.expandvars ("$SLSBASE/sls/bin/"))
        from  X_ROBOT_X02DA_robotScript import *
    except:
        wx.MessageBox('RobotScript Python Library is needed to run this program!')
        sys.exit (1)


class DataEvent(wx.PyEvent):
    def __init__(self,threadType):
            wx.PyEvent.__init__(self)
            self.SetEventType(threadType)
            #self.mode=mode
            #self.stagemoving=stagemoving
            #self.data=data
            
tSIZEROWS=10
tSIZECOLS=2
tArray=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P']
def create(parent):
    return Frame1(parent)

[wxID_FRAME1, wxID_FRAME1BUTCREATESCRIPT, wxID_FRAME1BUTEDITSCRIPT, 
 wxID_FRAME1BUTGETSTGPOS, wxID_FRAME1BUTLOAD, wxID_FRAME1BUTLOADFILE, 
 wxID_FRAME1BUTMOVELOAD, wxID_FRAME1BUTSAVEFILE, wxID_FRAME1BUTSEQUENCER, 
 wxID_FRAME1BUTSETLOAD, wxID_FRAME1BUTSETSTGPOS, wxID_FRAME1BUTSTARTRBBOT, 
 wxID_FRAME1BUTUNLOAD, wxID_FRAME1BXROBOT, wxID_FRAME1BXSAMPLE, 
 wxID_FRAME1BXSTAGE, wxID_FRAME1CHKTOOLTIPS, wxID_FRAME1SPINSTAGEMEMORY, 
 wxID_FRAME1STACURPOS, wxID_FRAME1STAEMPTYCODE, wxID_FRAME1STAROBOTSTATUS, 
 wxID_FRAME1STASAMPLEERROR, wxID_FRAME1STASTAGESTATUS, wxID_FRAME1STATICBOX1, 
 wxID_FRAME1STATICBOX2, wxID_FRAME1STATICBOX3, wxID_FRAME1STATICBOX4, 
 wxID_FRAME1STATICBOX5, wxID_FRAME1STATICTEXT1, wxID_FRAME1STATICTEXT2, 
 wxID_FRAME1STATICTEXT3, wxID_FRAME1STATICTEXT4, wxID_FRAME1STATICTEXT5, 
 wxID_FRAME1STATRX, wxID_FRAME1STATRXD, wxID_FRAME1STATRXX, 
 wxID_FRAME1STATRXXD, wxID_FRAME1STATRY1, wxID_FRAME1STATRY2, 
 wxID_FRAME1STATRYVAL, wxID_FRAME1STATRZ, wxID_FRAME1STATRZD, 
 wxID_FRAME1STATRZZ, wxID_FRAME1STATRZZD, wxID_FRAME1TXTEXPERTCODE, 
 wxID_FRAME1TXTSAMPLEDESCRIPTION, wxID_FRAME1TXTSAMPLENAME, 
 wxID_FRAME1TXTUSERCONTACT, wxID_FRAME1TXTUSERNAME, 
] = [wx.NewId() for _init_ctrls in range(49)]

class Frame1(wx.Frame):
    # the channel suffixes ($(MOTOR) first) for the stage positions to be remembered
    channels=['TRXX.DVAL','TRXX.VAL','TRZZ.DVAL','TRZZ.VAL','TRX.DVAL','TRX.VAL','TRY-VAL.VAL','TRZ.DVAL','TRZ.VAL','TRY1','TRY2']
    # the static fields to display the motor values
    fields=['TRXXd','TRXX','TRZZd','TRZZ','TRXd','TRX','TRYVAL','TRZd','TRZ','TRY1','TRY2']
    # a simple dictionary to store the fields and channel mapping
    chMap={}
    for jjunk in range(0,len(channels)): chMap[channels[jjunk]]=fields[jjunk]
    # define the size of the tray
    version=20081126
    
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_FRAME1, name='', parent=prnt,
              size=wx.Size(745, 460), style=wx.DEFAULT_FRAME_STYLE,
              title='Alignment Tool ')

        self.bxSample = wx.StaticBox(id=wxID_FRAME1BXSAMPLE,
              label=u'Sample Selector', name=u'bxSample', parent=self,
              pos=wx.Point(0, 8), size=wx.Size(416, 288), style=0)
        self.bxSample.SetMinSize(wx.Size(0, 0))

        self.staticBox2 = wx.StaticBox(id=wxID_FRAME1STATICBOX2,
              label=u'Sample Information', name='staticBox2', parent=self,
              pos=wx.Point(0, 296), size=wx.Size(416, 160), style=0)

        self.staticText1 = wx.StaticText(id=wxID_FRAME1STATICTEXT1,
              label=u'Sample Name:', name='staticText1', parent=self,
              pos=wx.Point(8, 320), size=wx.Size(96, 17), style=0)

        self.staticText2 = wx.StaticText(id=wxID_FRAME1STATICTEXT2,
              label=u'Sample Desc:', name='staticText2', parent=self,
              pos=wx.Point(8, 360), size=wx.Size(91, 17), style=0)

        self.txtSampleName = wx.TextCtrl(id=wxID_FRAME1TXTSAMPLENAME,
              name=u'txtSampleName', parent=self, pos=wx.Point(112, 320),
              size=wx.Size(216, 22), style=0, value=u'null')
        self.txtSampleName.SetToolTipString(u"The name that will be used in the images of the sample. Probably shouldn't have spaces, umlauts, accents, or weird characters. Additionally try to keep the name short as other elements are often added to the end")
        self.txtSampleName.Bind(wx.EVT_KEY_UP, self.OnTxtSampleNameText)
        self.txtSampleName.Bind(wx.EVT_KILL_FOCUS, self.OnTxtSampleNameText)
        self.txtSampleName.Bind(wx.EVT_TEXT_ENTER, self.OnTxtSampleNameText,
              id=wxID_FRAME1TXTSAMPLENAME)

        self.txtSampleDescription = wx.stc.StyledTextCtrl(id=wxID_FRAME1TXTSAMPLEDESCRIPTION,
              name=u'txtSampleDescription', parent=self, pos=wx.Point(112, 344),
              size=wx.Size(208, 100), style=0)
        self.txtSampleDescription.SetWrapMode(1)
        self.txtSampleDescription.SetToolTipString(u'Enter a description of the sample for later use since the filename will probably be too short to allow for adaquate naming')
        self.txtSampleDescription.Bind(wx.EVT_KILL_FOCUS,
              self.OnTxtSampleNameText)
        self.txtSampleDescription.Bind(wx.EVT_KEY_UP, self.OnTxtSampleNameText)

        self.staCurPos = wx.StaticText(id=wxID_FRAME1STACURPOS, label=u'',
              name=u'staCurPos', parent=self, pos=wx.Point(342, 363),
              size=wx.Size(58, 17), style=0)

        self.bxStage = wx.StaticBox(id=wxID_FRAME1BXSTAGE,
              label=u'Stage Control', name=u'bxStage', parent=self,
              pos=wx.Point(416, 8), size=wx.Size(136, 288), style=0)
        self.bxStage.SetMinSize(wx.Size(0, 0))
        self.bxStage.SetToolTipString(u'Green means stage moving, Red stage is stopped')

        self.bxRobot = wx.StaticBox(id=wxID_FRAME1BXROBOT,
              label=u'Robot Control', name=u'bxRobot', parent=self,
              pos=wx.Point(416, 296), size=wx.Size(136, 160), style=0)
        self.bxRobot.SetMinSize(wx.Size(0, 0))

        self.butStartRbbot = wx.Button(id=wxID_FRAME1BUTSTARTRBBOT,
              label=u'Start Robot', name=u'butStartRbbot', parent=self,
              pos=wx.Point(424, 320), size=wx.Size(120, 32), style=0)
        self.butStartRbbot.SetToolTipString(u'Command to start or restart the robot. The robot will forget if a sample is mounted and move through its warmup routine')
        self.butStartRbbot.Bind(wx.EVT_BUTTON, self.OnButStartRbbotButton,
              id=wxID_FRAME1BUTSTARTRBBOT)

        self.butLoad = wx.Button(id=wxID_FRAME1BUTLOAD, label=u'Load Sample',
              name=u'butLoad', parent=self, pos=wx.Point(424, 352),
              size=wx.Size(120, 32), style=0)
        self.butLoad.SetToolTipString(u'Command to load the highlighted sample on the stage. This is disabled when the robot has not been started or once a sample is already loaded')
        self.butLoad.Bind(wx.EVT_BUTTON, self.OnButLoadButton,
              id=wxID_FRAME1BUTLOAD)

        self.butUnload = wx.Button(id=wxID_FRAME1BUTUNLOAD, label=u'Unload',
              name=u'butUnload', parent=self, pos=wx.Point(424, 384),
              size=wx.Size(120, 32), style=0)
        self.butUnload.SetToolTipString(u'Click to remove a sample from the stage and return it to its original place on the sample tray. This button is disabled when the robot is off or no sample is mounted')
        self.butUnload.Bind(wx.EVT_BUTTON, self.OnButUnloadButton,
              id=wxID_FRAME1BUTUNLOAD)

        self.butGetStgPos = wx.Button(id=wxID_FRAME1BUTGETSTGPOS,
              label=u'Record', name=u'butGetStgPos', parent=self,
              pos=wx.Point(424, 48), size=wx.Size(80, 32), style=0)
        self.butGetStgPos.SetMinSize(wx.Size(0, 0))
        self.butGetStgPos.SetToolTipString(u'Records the current position of the stage for the hightighted sample on the left')
        self.butGetStgPos.Bind(wx.EVT_BUTTON, self.OnButGetStgPosButton,
              id=wxID_FRAME1BUTGETSTGPOS)

        self.butSetStgPos = wx.Button(id=wxID_FRAME1BUTSETSTGPOS,
              label=u'Move Stage', name=u'butSetStgPos', parent=self,
              pos=wx.Point(424, 256), size=wx.Size(120, 32), style=0)
        self.butSetStgPos.Bind(wx.EVT_BUTTON, self.OnButSetStgPosButton,
              id=wxID_FRAME1BUTSETSTGPOS)

        self.staTRXXd = wx.StaticText(id=wxID_FRAME1STATRXXD, label=u'TRXXd:',
              name=u'staTRXXd', parent=self, pos=wx.Point(424, 80),
              size=wx.Size(49, 17), style=0)

        self.staTRZZd = wx.StaticText(id=wxID_FRAME1STATRZZD, label=u'TRZZd:',
              name=u'staTRZZd', parent=self, pos=wx.Point(424, 112),
              size=wx.Size(51, 17), style=0)

        self.staTRY1 = wx.StaticText(id=wxID_FRAME1STATRY1, label=u'TRY1:',
              name=u'staTRY1', parent=self, pos=wx.Point(424, 224),
              size=wx.Size(39, 17), style=0)

        self.staTRY2 = wx.StaticText(id=wxID_FRAME1STATRY2, label=u'TRY2:',
              name=u'staTRY2', parent=self, pos=wx.Point(424, 240),
              size=wx.Size(39, 17), style=0)

        self.staTRXd = wx.StaticText(id=wxID_FRAME1STATRXD, label=u'TRXd:',
              name=u'staTRXd', parent=self, pos=wx.Point(424, 144),
              size=wx.Size(40, 17), style=0)

        self.staTRZd = wx.StaticText(id=wxID_FRAME1STATRZD, label=u'TRZd:',
              name=u'staTRZd', parent=self, pos=wx.Point(424, 176),
              size=wx.Size(41, 17), style=0)

        self.staTRXX = wx.StaticText(id=wxID_FRAME1STATRXX, label=u'TRXX',
              name=u'staTRXX', parent=self, pos=wx.Point(440, 96),
              size=wx.Size(36, 17), style=0)

        self.staTRZZ = wx.StaticText(id=wxID_FRAME1STATRZZ, label=u'TRZZ:',
              name=u'staTRZZ', parent=self, pos=wx.Point(440, 128),
              size=wx.Size(43, 17), style=0)

        self.staTRX = wx.StaticText(id=wxID_FRAME1STATRX, label=u'TRX:',
              name=u'staTRX', parent=self, pos=wx.Point(440, 160),
              size=wx.Size(32, 17), style=0)

        self.staTRYVAL = wx.StaticText(id=wxID_FRAME1STATRYVAL,
              label=u'TRY-VAL:', name=u'staTRYVAL', parent=self,
              pos=wx.Point(424, 208), size=wx.Size(58, 17), style=0)

        self.staTRZ = wx.StaticText(id=wxID_FRAME1STATRZ, label=u'TRZ:',
              name=u'staTRZ', parent=self, pos=wx.Point(440, 192),
              size=wx.Size(33, 17), style=0)

        self.butSaveFile = wx.Button(id=wxID_FRAME1BUTSAVEFILE,
              label=u'Save File', name=u'butSaveFile', parent=self,
              pos=wx.Point(560, 312), size=wx.Size(96, 32), style=0)
        self.butSaveFile.SetToolTipString(u'To save the current tray and all the associated settings. This will also generate an older version script file and an XML file. The original file can be used with the sequencer program (cmdSequencer)')
        self.butSaveFile.Bind(wx.EVT_BUTTON, self.OnButSaveButton,
              id=wxID_FRAME1BUTSAVEFILE)

        self.butLoadFile = wx.Button(id=wxID_FRAME1BUTLOADFILE,
              label=u'Load File', name=u'butLoadFile', parent=self,
              pos=wx.Point(560, 344), size=wx.Size(96, 32), style=0)
        self.butLoadFile.SetToolTipString(u'Load a file created with this program to resume work on a tray')
        self.butLoadFile.Bind(wx.EVT_BUTTON, self.OnButLoadFileButton,
              id=wxID_FRAME1BUTLOADFILE)

        self.staticText3 = wx.StaticText(id=wxID_FRAME1STATICTEXT3,
              label=u'Sample Pos:', name='staticText3', parent=self,
              pos=wx.Point(328, 344), size=wx.Size(80, 17), style=0)

        self.staEmptyCode = wx.StaticText(id=wxID_FRAME1STAEMPTYCODE,
              label=u'Expert Code', name=u'staEmptyCode', parent=self,
              pos=wx.Point(560, 152), size=wx.Size(80, 17), style=0)
        self.staEmptyCode.SetToolTipString(u'Once the code has been entered one can click here to reset the mastercode')
        self.staEmptyCode.Bind(wx.EVT_LEFT_DOWN, self.OnStaEmptyCodeClick)

        self.staRobotStatus = wx.StaticText(id=wxID_FRAME1STAROBOTSTATUS,
              label=u'Robot Status', name=u'staRobotStatus', parent=self,
              pos=wx.Point(439, 417), size=wx.Size(80, 17), style=0)
        self.staRobotStatus.SetToolTipString(u'Status of Robot and availability to accept a command')

        self.staSampleError = wx.StaticText(id=wxID_FRAME1STASAMPLEERROR,
              label=u'Error', name=u'staSampleError', parent=self,
              pos=wx.Point(328, 392), size=wx.Size(32, 17), style=0)

        self.butCreateScript = wx.Button(id=wxID_FRAME1BUTCREATESCRIPT,
              label=u'Create Script', name=u'butCreateScript', parent=self,
              pos=wx.Point(560, 392), size=wx.Size(96, 32), style=0)
        self.butCreateScript.SetToolTipString(u'This regenerates the simplist script that acquires each sample and position once. It will erase any changes you have made')
        self.butCreateScript.Bind(wx.EVT_BUTTON, self.OnButCreateScriptButton,
              id=wxID_FRAME1BUTCREATESCRIPT)

        self.butEditScript = wx.Button(id=wxID_FRAME1BUTEDITSCRIPT,
              label=u'Edit Script', name=u'butEditScript', parent=self,
              pos=wx.Point(560, 424), size=wx.Size(96, 32), style=0)
        self.butEditScript.SetToolTipString(u'This allows one to edit the script and add repeats, waits, and other special commands, and to adjust the order of sample loading')
        self.butEditScript.Bind(wx.EVT_BUTTON, self.OnButEditScriptButton,
              id=wxID_FRAME1BUTEDITSCRIPT)

        self.txtExpertCode = wx.lib.masked.textctrl.TextCtrl(id=wxID_FRAME1TXTEXPERTCODE,
              name=u'txtExpertCode', parent=self, pos=wx.Point(560, 168),
              size=wx.Size(88, 27), style=0, value='code')
        self.txtExpertCode.SetMaxLength(10)
        self.txtExpertCode.SetToolTipString(u'Enter the code in order to execute expert only commands in the scripts.')
        self.txtExpertCode.Bind(wx.EVT_TEXT, self.OnTxtExpertCodeText,
              id=wxID_FRAME1TXTEXPERTCODE)

        self.spinStageMemory = wx.SpinCtrl(id=wxID_FRAME1SPINSTAGEMEMORY,
              initial=0, max=1, min=0, name=u'spinStageMemory', parent=self,
              pos=wx.Point(512, 48), size=wx.Size(31, 27),
              style=wx.SP_ARROW_KEYS)
        self.spinStageMemory.SetRange(0, 0)
        self.spinStageMemory.SetHelpText(u'Allows multiple regions of interest per sample')
        self.spinStageMemory.SetToolTipString(u'Each sample can have multiple regions of interest use this in coordination with the Record button to set each. They are denoted by _P+number in the script')
        self.spinStageMemory.Bind(wx.EVT_SPINCTRL,
              self.OnSpinStageMemorySpinctrl, id=wxID_FRAME1SPINSTAGEMEMORY)

        self.staStageStatus = wx.StaticText(id=wxID_FRAME1STASTAGESTATUS,
              label=u'', name=u'staStageStatus', parent=self, pos=wx.Point(440,
              26), size=wx.Size(80, 17), style=0)

        self.staticBox1 = wx.StaticBox(id=wxID_FRAME1STATICBOX1,
              label=u'User Information', name='staticBox1', parent=self,
              pos=wx.Point(552, 8), size=wx.Size(200, 112), style=0)

        self.staticText4 = wx.StaticText(id=wxID_FRAME1STATICTEXT4,
              label=u'Name', name='staticText4', parent=self, pos=wx.Point(560,
              32), size=wx.Size(39, 17), style=0)

        self.staticText5 = wx.StaticText(id=wxID_FRAME1STATICTEXT5,
              label=u'Contact Info', name='staticText5', parent=self,
              pos=wx.Point(560, 56), size=wx.Size(79, 17), style=0)

        self.txtUserName = wx.TextCtrl(id=wxID_FRAME1TXTUSERNAME,
              name=u'txtUserName', parent=self, pos=wx.Point(608, 24),
              size=wx.Size(128, 27), style=0, value=u'')
        self.txtUserName.Bind(wx.EVT_TEXT, self.OnTxtUserNameText,
              id=wxID_FRAME1TXTUSERNAME)

        self.txtUserContact = wx.TextCtrl(id=wxID_FRAME1TXTUSERCONTACT,
              name=u'txtUserContact', parent=self, pos=wx.Point(640, 48),
              size=wx.Size(96, 27), style=0, value=u'')
        self.txtUserContact.Bind(wx.EVT_TEXT, self.OnTxtUserNameText,
              id=wxID_FRAME1TXTUSERCONTACT)

        self.staticBox3 = wx.StaticBox(id=wxID_FRAME1STATICBOX3,
              label=u'File Managment', name='staticBox3', parent=self,
              pos=wx.Point(552, 296), size=wx.Size(112, 80), style=0)
        self.staticBox3.SetMinSize(wx.Size(0, 0))

        self.staticBox4 = wx.StaticBox(id=wxID_FRAME1STATICBOX4,
              label=u'Script Editing', name='staticBox4', parent=self,
              pos=wx.Point(552, 376), size=wx.Size(112, 80), style=0)
        self.staticBox4.SetMinSize(wx.Size(0, 0))

        self.staticBox5 = wx.StaticBox(id=wxID_FRAME1STATICBOX5, label=u'Varia',
              name='staticBox5', parent=self, pos=wx.Point(552, 128),
              size=wx.Size(200, 100), style=0)

        self.chkToolTips = wx.CheckBox(id=wxID_FRAME1CHKTOOLTIPS,
              label=u'Tooltips', name=u'chkToolTips', parent=self,
              pos=wx.Point(656, 144), size=wx.Size(88, 24), style=0)
        self.chkToolTips.SetValue(False)
        self.chkToolTips.Bind(wx.EVT_CHECKBOX, self.OnChkToolTipsCheckbox,
              id=wxID_FRAME1CHKTOOLTIPS)

        self.butSequencer = wx.Button(id=wxID_FRAME1BUTSEQUENCER,
              label=u'Sequencer...', name=u'butSequencer', parent=self,
              pos=wx.Point(568, 232), size=wx.Size(160, 32), style=0)
        self.butSequencer.SetToolTipString(u'Click here to start the gui based sequencer tool')
        self.butSequencer.Bind(wx.EVT_BUTTON, self.OnButSequencerButton,
              id=wxID_FRAME1BUTSEQUENCER)

        self.butSetLoad = wx.Button(id=wxID_FRAME1BUTSETLOAD,
              label=u'Record Load', name=u'butSetLoad', parent=self,
              pos=wx.Point(648, 168), size=wx.Size(96, 32), style=0)
        self.butSetLoad.Enable(False)
        self.butSetLoad.Bind(wx.EVT_BUTTON, self.OnButSetLoadButton,
              id=wxID_FRAME1BUTSETLOAD)

        self.butMoveLoad = wx.Button(id=wxID_FRAME1BUTMOVELOAD,
              label=u'Move Load', name=u'butMoveLoad', parent=self,
              pos=wx.Point(648, 200), size=wx.Size(88, 24), style=0)
        self.butMoveLoad.Enable(False)
        self.butMoveLoad.Bind(wx.EVT_BUTTON, self.OnButMoveLoad,
              id=wxID_FRAME1BUTMOVELOAD)

    def __init__(self, parent):
        self._init_ctrls(parent)
        self.trayPosSelect=0
        self.scriptText=''
        self.scriptDict={}
        
        #self.defLoadPos={'TRX.DVAL': -6504.0, 'TRXX.DVAL': -417.30000000000001, 'TRY-VAL.VAL': -20000.0, 'TRXX.VAL': -1028.0000000000002, 'TRZ.DVAL': -22293.0, 'TRY1': -20000.000781250001, 'TRY2': -20000.099999999999, 'TRZZ.DVAL': 1086.4000000000001, 'TRZ.VAL': -44257.0, 'TRX.VAL': -5075.0, 'TRZZ.VAL': 199.0}
        #self.defLoadPos={'TRX.DVAL': -26406.5, 'TRXX.DVAL': -1369.9000000000001, 'TRY-VAL.VAL': 6985.8039215686276, 'TRXX.VAL': 0.0, 'TRZ.DVAL': 2860.0, 'TRY1': 4497.4031403186273, 'TRY2': 4997.3539215686278, 'TRZZ.DVAL': 1609.4000000000001, 'TRZ.VAL': -69410.0, 'TRX.VAL': -25000.0, 'TRZZ.VAL': 0.0}
        #self.defLoadPos={'TRX.DVAL': -26406.5, 'TRXX.DVAL': -1369.9000000000001, 'TRY-VAL.VAL': -10214.196078431372, 'TRXX.VAL': 0.0, 'TRZ.DVAL': 2860.0, 'TRY1': -12702.596859681373, 'TRY2': -12202.646078431373, 'TRZZ.DVAL': 1609.4000000000001, 'TRZ.VAL': -69410.0, 'TRX.VAL': -25000.0, 'TRZZ.VAL': 0.0}
	self.defLoadPos={'TRX.DVAL': -26406.5, 'TRXX.DVAL': -1369.9000000000001, 'TRY-VAL.VAL': -10214.196078431372, 'TRXX.VAL': 0.0, 'TRZ.DVAL': -62140.0, 'TRY1': -12702.596859681373, 'TRY2': -12202.646078431373, 'TRZZ.DVAL': 11609.4, 'TRZ.VAL': -4410.0, 'TRX.VAL': -25000.0, 'TRZZ.VAL': -10000.0}

        self.curLoadPos=self.defLoadPos
        self.UserProfile={}
        self.InitializeGrid()
        
        if X_ROBOT_X02DA_robotCommon.DebugMode!=1:
            self.myRobot=X_ROBOT_X02DA_robotCommon.TomcatRobot()
        else:
            self.myRobot=0
        #threading.Thread(target=self.RobotStatus()).start()
        

        self.myRobotScript=RobotScript(myRobot=self.myRobot,debugMode=X_ROBOT_X02DA_robotCommon.DebugMode)
        self.myRobotScript.InitializeStageChannels()
        self.myRobotScript.guiChannels()
        
        wx.ToolTip.Enable(0)
        self.ksmThread={}
        self.ksmThread['robotStageUpdate']=[wx.NewEventType(),self.dispRobotStatus] # robotStatusUpdate
        self.ksmThread['pollStage']=[wx.NewEventType(),self.updatePositionFields] # pollStage
    
        self.ksmThreadBindEvents()
        #thread.start_new_thread ( self.getRobotStatus,() )
        self.robotStatusLock=thread.allocate_lock()
        thread.start_new_thread ( self.threadRobotStatus,() )
        
    # Handler Functions
    def OnTrayPosSelectGridCellLeftDclick(self, event):
        cRow=event.GetRow()
        cCol=event.GetCol()
        self.FlipLoaded(cRow,cCol)


    def OnTrayPosSelectGridSelectCell(self, event):
        cRow=event.GetRow()
        cCol=event.GetCol()
        self.selectCell(cRow,cCol)
        
        event.Skip()

    def OnTxtSampleNameText(self, event):
        cCol=self.trayPosSelect.GetGridCursorCol()
        cRow=self.trayPosSelect.GetGridCursorRow()
        if (self.staCurPos.GetLabel()==self.trayPosSelect.GetCellValue(cRow,cCol)):
            self.CurTray[cRow][cCol][0]=self.txtSampleName.GetValue().strip().replace(' ','_')
            self.CurTray[cRow][cCol][1]=self.txtSampleDescription.GetText()
        self.redrawGrid()
        self.updateWarnings(cRow,cCol)
        event.Skip()

    def OnButGetStgPosButton(self, event):
        cCol=self.trayPosSelect.GetGridCursorCol()
        cRow=self.trayPosSelect.GetGridCursorRow()
        #threading.Thread(target=self.pollStage(cRow,cCol,self.spinStageMemory.GetValue())).start()
        self.threadRobotCom(self.pollStage,(cRow,cCol,self.spinStageMemory.GetValue()))
        event.Skip()




    def OnButStartRbbotButton(self, event):
        
        #self.trayPosSelect.SetGridCursor(0,1)
        
        if (type(self.myRobot)==type(0)):
            print "In Debug Mode!"
        else:
            # reset the softioc, because it probably needs it
            self.myRobot=None
            self.threadRobotCom(os.system,('X_ROBOT_X02DA_restartIOC.sh',))
            time.sleep(5) # takes about 5 seconds to reboot
            self.myRobot=X_ROBOT_X02DA_robotCommon.TomcatRobot()
            self.myRobotScript.myRobot=self.myRobot
            self.threadRobotCom(self.myRobot.start,())
        event.Skip()

    def OnButLoadButton(self, event):
        cCol=self.trayPosSelect.GetGridCursorCol()
        cRow=self.trayPosSelect.GetGridCursorRow()
        print cCol
        #self.myRobot.rawMount(cCol,cRow)
        oCgVal=self.CurTray[cRow][cCol][2]
        self.CurTray[cRow][cCol][2]=1
        self.generateScript(0)
        self.CurTray[cRow][cCol][2]=oCgVal
        # update dictionary so the command works
        self.myRobotScript.ScriptDict=self.scriptDict
        
        #self.myRobotScript.cmd_IMMOUNT([self.getSampleName(cRow,cCol,self.spinStageMemory.GetValue())])
        self.threadRobotCom(self.myRobotScript.cmd_IMMOUNT,([self.getSampleName(cRow,cCol,self.spinStageMemory.GetValue())],))
        print "mounting:"+self.getSampleName(cRow,cCol,self.spinStageMemory.GetValue())
        event.Skip()

    def OnButUnloadButton(self, event):
        self.generateScript(0)
        self.myRobotScript.ScriptDict=self.scriptDict
        self.threadRobotCom(self.myRobotScript.cmd_IMUNMOUNT,([],))
        event.Skip()

    def OnButSetStgPosButton(self, event):
        cCol=self.trayPosSelect.GetGridCursorCol()
        cRow=self.trayPosSelect.GetGridCursorRow()
        self.threadRobotCom(self.putStage,(cRow,cCol,self.spinStageMemory.GetValue()))
        event.Skip()
    def OnButSaveButton(self, event):
        self.generateScript(0)
        t4f = wx.SAVE|wx.FD_OVERWRITE_PROMPT
        dlg = wx.FileDialog(self,"Save a file",os.getcwd(), "", "*.*", t4f)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
            dirname = dlg.GetDirectory()
            fleOut=open(dirname+'/'+filename,'w')
            self.writePickleFile(fleOut)
            fleOut.close()
            fleOut2=open(dirname+'/'+filename+'.altscript','w')
            for ik in range(0,len(self.CurTray[0])):
                for ij in range(0,len(self.CurTray)):
                    if self.CurTray[ij][ik][2]:
                        fleOut2.write('DOSAMPLE('+ik.__str__()+','+ij.__str__()+')\n')
            fleOut2.close()
            self.exportSampleXML(filename+'.xml')
            print(dirname+'/'+filename+' written successfully')
        dlg.Destroy()

        event.Skip()

    def OnButLoadFileButton(self, event):
        t4f = wx.OPEN
        dlg = wx.FileDialog(self,"Load a file",os.getcwd(), "", "*.*", t4f)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
            dirname = dlg.GetDirectory()
            if filename.upper().find('.XML')>0: # she's an xml file
                self.importSampleXML(dirname+'/'+filename)
            else: # she must be a pickle
                fleIn=open(dirname+'/'+filename,'rb')
                if self.loadPickleFile(fleIn):
                    self.butLoad.SetForegroundColour('green')
                    print(dirname+'/'+filename+' opened successfully')
                else:
                    self.butLoad.SetForegroundColour('red')
                    print(dirname+'/'+filename+' not opened')
                fleIn.close()
            self.txtUserName.SetValue(self.UserProfile['Name'])
            self.txtUserContact.SetValue(self.UserProfile['Contact'])
            self.createGrid()
                      
        dlg.Destroy()
        event.Skip()
    def OnButCreateScriptButton(self, event):
        self.generateScript()
        event.Skip()
    def OnTxtExpertCodeText(self, event):
        self.setExpert(self.txtExpertCode.GetValue().lower().strip())

        event.Skip()
    def OnStaEmptyCodeClick(self, event):
        self.setExpert('')
        event.Skip()
    def OnSpinStageMemorySpinctrl(self, event):
        cCol=self.trayPosSelect.GetGridCursorCol()
        cRow=self.trayPosSelect.GetGridCursorRow()
        self.updatePositionFields(cRow,cCol,self.spinStageMemory.GetValue())
        self.updateWarnings(cRow,cCol)
        event.Skip()
    def OnTxtUserNameText(self, event):
        self.UserProfile['Name']=self.txtUserName.GetValue()
        self.UserProfile['Contact']=self.txtUserContact.GetValue()
    def OnChkToolTipsCheckbox(self, event):
        wx.ToolTip.Enable(self.chkToolTips.GetValue())
        event.Skip()
    def OnButSequencerButton(self, event):
        import X_ROBOT_X02DA_guiSequencer
        self.generateScript(0)
        self.myRobotScript.loadText(self.scriptText,self.scriptDict)
        self.guiSequencer = X_ROBOT_X02DA_guiSequencer.create(self)
        self.guiSequencer.Show()
        event.Skip()
    def OnButSetLoadButton(self, event):
        self.pollStage(-1,-1,0) # load position command
        print self.curLoadPos
        event.Skip()
    def OnButEditScriptButton(self, event):
        self.EditScriptDialog = wx.Dialog(self, -1, 'Script Editor',size=wx.Size(695, 436))
        self.EditScriptDialog.chSample = wx.Choice(choices=self.scriptDict.keys(),
              name=u'chSample', parent=self.EditScriptDialog, pos=wx.Point(0, 0),
              size=wx.Size(100, 32), style=0)
        self.EditScriptDialog.chSample.Bind(wx.EVT_CHOICE, self.OnChSampleChoice)
        self.EditScriptDialog.butWait = wx.Button(
              label=u'WAIT', name=u'butWait', parent=self.EditScriptDialog,
              pos=wx.Point(100, 0), size=wx.Size(100, 32), style=0)
        self.EditScriptDialog.butWait.Bind(wx.EVT_BUTTON, self.OnButWait)
        self.EditScriptDialog.butRepeat = wx.Button(
              label=u'REPEAT', name=u'butRepeat', parent=self.EditScriptDialog,
              pos=wx.Point(200, 0), size=wx.Size(100, 32), style=0)
        self.EditScriptDialog.butRepeat.Bind(wx.EVT_BUTTON, self.OnButRepeat)
        self.EditScriptDialog.butValidate = wx.Button(
              label=u'Validate', name=u'butValidate', parent=self.EditScriptDialog,
              pos=wx.Point(590, 0), size=wx.Size(100, 32), style=0)
        self.EditScriptDialog.butValidate.Bind(wx.EVT_BUTTON, self.OnButValidate)
        
        self.EditScriptDialog.txtScript = wx.stc.StyledTextCtrl(
              name=u'txtScript', parent=self.EditScriptDialog, pos=wx.Point(5, 40),
              size=wx.Size(685, 430), style=0)
        self.EditScriptDialog.txtScript.SetText(self.scriptText)
        self.EditScriptDialog.txtScript.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
        self.EditScriptDialog.txtScript.SetMarginWidth(1, 25)
        self.EditScriptDialog.txtScript.AutoCompSetIgnoreCase(True)
        self.EditScriptDialog.txtScript.Bind(wx.EVT_KEY_UP, self.OnTestAutoComp)
        self.myRobotScript.ScriptDict=self.scriptDict
        self.myRobotScript.initializeValidCommands()
        vCmds=[]
        for cmd in self.myRobotScript.ValidCommands.keys():
            if cmd=='IMSAMPLE':
                for cKey in self.scriptDict.keys():
                    vCmds.append(cmd+'("'+cKey+'")')
            else:
                vCmds.append(cmd+'('+','*self.myRobotScript.ValidCommands[cmd][1]+')')
        vCmds.sort()
        nCmds=''
        for cmd in vCmds:
            nCmds+=' '+cmd
        self.EditScriptDialog.AutoCompCmd=nCmds
        
        #self.EditScriptDialog.auto=True
        self.EditScriptDialog.ShowModal()
        self.myRobotScript.loadText(self.EditScriptDialog.txtScript.GetText(),self.scriptDict)
        vErrors=self.myRobotScript.validateSequence(wx.MessageBox)
        while (vErrors>0):      
            wx.MessageBox(vErrors.__str__()+' fatal errors found')
            self.EditScriptDialog.ShowModal()
            self.myRobotScript.loadText(self.EditScriptDialog.txtScript.GetText(),self.scriptDict)
            vErrors=self.myRobotScript.validateSequence(wx.MessageBox)
            
        self.scriptText=self.EditScriptDialog.txtScript.GetText()
        self.EditScriptDialog.Destroy()       
        
        event.Skip()

# Edit Script Dialog Callbacks
    def OnTestAutoComp(self,event):
        if not self.EditScriptDialog.txtScript.AutoCompActive(): self.EditScriptDialog.txtScript.AutoCompShow(1,self.EditScriptDialog.AutoCompCmd) 
    def OnButWait(self,event):
        self.EditScriptDialog.txtScript.SetText(self.EditScriptDialog.txtScript.GetText()+'\nWAIT(10) #wait 10 seconds')
    def OnButRepeat(self,event):
        #print event
        #print dir(event)
        self.EditScriptDialog.txtScript.SetText(self.EditScriptDialog.txtScript.GetText()+'\nREPEAT(5,4) #repeat from line 5, 4 more times')
    def OnButValidate(self,event):
        self.myRobotScript.loadText(self.EditScriptDialog.txtScript.GetText(),self.scriptDict)
        #print self.myRobotScript.sequence
        if (self.myRobotScript.validateSequence(wx.MessageBox)>0):
            self.EditScriptDialog.butValidate.SetForegroundColour('red')
        else:
            self.EditScriptDialog.butValidate.SetForegroundColour('green')
    def OnChSampleChoice(self, event):
        #print event.String
        sName=self.EditScriptDialog.chSample.StringSelection
        cmdStr='IMSAMPLE("'+sName+'")'
        self.EditScriptDialog.txtScript.SetText(self.EditScriptDialog.txtScript.GetText()+'\n'+cmdStr+'# tray pos '+tArray[self.scriptDict[sName][0]]+self.scriptDict[sName][1].__str__())
        event.Skip()
# Custom Functions
    def InitializeGrid(self,mRows=tSIZEROWS,mCols=tSIZECOLS):
        

        self.CurTray=[];
        for ij in range(0,mRows):
            curRow=[]
            for ik in range(0,mCols):
                # array outline (name,desc,toLoad,Pos)
                curRow.append([tArray[ik]+ij.__str__(),'',0,[]])
            self.CurTray.append(curRow)

        self.createGrid()
    def FlipLoaded(self,cRow,cCol,repaint=1):
            
        if cRow<0:
            for ij in range(0,len(self.CurTray)): self.FlipLoaded(ij,cCol,0)
        elif cCol<0:
            for ij in range(0,len(self.CurTray[cRow])): self.FlipLoaded(cRow,ij,0)
        else:
            if self.CurTray[cRow][cCol][2]>0:
                self.CurTray[cRow][cCol][2]=0
            else:
                self.CurTray[cRow][cCol][2]=1
            
        if (repaint):
            self.redrawGrid()
    def selectCell(self,cRow,cCol):
        #cColR=self.trayPosSelect.GetGridCursorCol()
        #cRowR=self.trayPosSelect.GetGridCursorRow()
        #if ((cRow==cRowR) &(cCol==cColR)):
        self.txtSampleName.SetValue(self.CurTray[cRow][cCol][0])
        self.txtSampleDescription.SetText(self.CurTray[cRow][cCol][1])
        self.staCurPos.SetLabel(self.trayPosSelect.GetCellValue(cRow,cCol))
        self.spinStageMemory.SetValue(0)
        self.spinStageMemory.SetRange(0,len(self.CurTray[cRow][cCol][3]))
        self.updatePositionFields(cRow,cCol,0)
        self.updateWarnings(cRow,cCol)
    def updateWarnings(self,cRow,cCol):    
        cName=tArray[cCol]+cRow.__str__()
        erMsg=''
        if (len(self.CurTray[cRow][cCol][3])>self.spinStageMemory.GetValue()):
            if (len(self.CurTray[cRow][cCol][3][self.spinStageMemory.GetValue()])<1):
                erMsg+='Pos Empty\n'
        else:
            erMsg+='Pos Empty\n'
        if (self.CurTray[cRow][cCol][0]==cName):
            erMsg+='Name Wrong'
        self.staSampleError.SetForegroundColour('red')
        self.staSampleError.Shown=(len(erMsg)>0)
        self.staSampleError.SetLabel(erMsg)
        #else:
        #    self.trayPosSelect.SetGridCursor(cRow,cCol)
    def getSampleName(self,cRow,cCol,cSpin):
        cPosNSuffix=''
        spinLen=len(self.CurTray[cRow][cCol][3])
        if spinLen>1:
            cPosNSuffix='_P'+str(min([cSpin,spinLen-1]))
        return self.CurTray[cRow][cCol][0]+cPosNSuffix  
    def generateScript(self,saveScript=1):
        #generates the script and dictionary to run on the sequencer
        # the saveScript option is so both programs can utilize the 
        # robotScript commands for mounting and unmounting reducing
        # the likelyhood of error
        
        oldScript=self.scriptText
        self.scriptDict={}
        # Add Load Position
        self.scriptText=''
        self.scriptDict['LoadPos']=[-1,-1,self.curLoadPos]
        for ik in range(0,len(self.CurTray[0])):
            for ij in range(0,len(self.CurTray)):
                if self.CurTray[ij][ik][2]:
                    for cPos in range(0,len(self.CurTray[ij][ik][3])):
                        
                        cPosSuffix=''
                        if len(self.CurTray[ij][ik][3])>1:
                            cPosSuffix=', stage pos '+cPos.__str__()
                        commentSuffix='# tray pos '+tArray[ik]+ij.__str__()
                        self.scriptText+='IMSAMPLE("'+self.getSampleName(ij,ik,cPos)+'")'+commentSuffix+cPosSuffix+'\n'
                        self.scriptDict[self.getSampleName(ij,ik,cPos)]=[ik,ij,self.CurTray[ij][ik][3][cPos]]
                    if len(self.CurTray[ij][ik][3])==0:
                        commentSuffix='# tray pos '+tArray[ik]+ij.__str__()
                        self.scriptText+='IMSAMPLE("'+self.getSampleName(ij,ik,0)+'")'+commentSuffix+', empty/default stage pos\n'
                        self.scriptDict[self.CurTray[ij][ik][0]]=[ik,ij,{}]
        if not saveScript:
            self.scriptText=oldScript # replace script with old version
    def pollStage(self,cRow,cCol,cStgMem):
        cStg={}
        for i in range(0,len(self.channels)):
            tempChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel('X02DA-ES1-SMP1:'+self.channels[i])
            cVal=tempChan.getVal()
            cStg[self.channels[i]]=cVal
        
        #eval('self.sta'+self.fields[i]+'.SetLabel("'+self.fields[i]+':'+cVal.__int__().__str__()+'")')
        if (cRow>=0) & (cCol>=0):
            while cStgMem>=len(self.CurTray[cRow][cCol][3]):
                self.CurTray[cRow][cCol][3].append({})
            self.CurTray[cRow][cCol][3][cStgMem]=cStg
        else:
            self.curLoadPos=cStg
            print cStg
            self.generateScript(0)
        de=DataEvent(self.ksmThread['pollStage'][0]) # pollStage uses events since it is threaded
        wx.PostEvent(self,de)
        
        #self.trayPosSelect.ForceRefresh()
    def putStage(self,cRow,cCol,cStgMem):
        if len(self.CurTray[cRow][cCol][3])>cStgMem:
            cStg=self.CurTray[cRow][cCol][3][cStgMem]
            cKeys=cStg.keys()
            for i in range(0,len(cKeys)):
                tempChan=X_ROBOT_X02DA_robotCommon.RoboEpicsChannel('X02DA-ES1-SMP1:'+cKeys[i])
                #cVal=tempChan.getVal()
                tempChan.putVal(cStg[cKeys[i]])
        else:
            wx.MessageBox('Position Not Correctly Loaded')
        #self.trayPosSelect.ForceRefresh()
    def updatePositionFields(self,cRow=-1,cCol=-1,cStgMem=-1):
        if ((cRow<0) or (type(cRow)!=type(1))): cRow=self.trayPosSelect.GetGridCursorRow()
        if ((cCol<0) or (type(cRow)!=type(1))): cCol=self.trayPosSelect.GetGridCursorCol()
        if ((cStgMem<0) or (type(cRow)!=type(1))): cStgMem=self.spinStageMemory.GetValue()
        #print (cRow,cCol,cStgMem)
        # load in the current positions (if exist or blanks if not)
        bDict=self.chMap.copy()
        if cStgMem<len(self.CurTray[cRow][cCol][3]):
            cItems=self.CurTray[cRow][cCol][3][cStgMem].items()
            for ijr in range(0,len(cItems)):
                #print cItem[0]
                cVar=bDict.pop(cItems[ijr][0])
                eval('self.sta'+cVar+'.SetLabel("'+cVar+':'+cItems[ijr][1].__int__().__str__()+'")')
        bDict=bDict.items()
        for ijr in range(0,len(bDict)):
            cVar=bDict[ijr][1]
            eval('self.sta'+cVar+'.SetLabel("'+cVar+':")')
        self.spinStageMemory.SetRange(0,len(self.CurTray[cRow][cCol][3]))
        self.redrawGrid()
        self.updateWarnings(cRow,cCol)
    def redrawGrid(self):
        
        #print dir(self.trayPosSelect)
        #self.trayPosSelect.ResetView()
        #self.trayPosSelect.Destroy()
        goodValues=0
        errors=0
        for ij in range(0,len(self.CurTray)):
            curRow=[]
            for ik in range(0,len(self.CurTray[ij])):
                cName=tArray[ik]+ij.__str__()
                self.trayPosSelect.SetCellValue(ij,ik,cName)
                if ((self.CurTray[ij][ik][2])):
                    if ((len(self.CurTray[ij][ik][3])>0) and (not (self.CurTray[ij][ik][0]==cName))):
                        # green=good to go
                        goodValues+=1
                        self.trayPosSelect.SetCellBackgroundColour(ij,ik,'green')
                    else:
                        # yellow means no position yet, probably not good
                        errors+=1
                        self.trayPosSelect.SetCellBackgroundColour(ij,ik,'yellow')
                else:
                    self.trayPosSelect.SetCellBackgroundColour(ij,ik,'white')
                if len(self.CurTray[ij][ik][3])>0:
                    # blue means position loaded
                    self.trayPosSelect.SetCellTextColour(ij,ik,'blue')
                else:
                    self.trayPosSelect.SetCellTextColour(ij,ik,'black')
        self.trayPosSelect.AutoSize()
        self.trayPosSelect.DisableDragColSize()
        self.trayPosSelect.DisableDragRowSize()
        self.trayPosSelect.ForceRefresh()
        if ((goodValues>0) & (errors==0)):
            self.bxSample.SetForegroundColour('green')
        elif (errors>0):
            self.bxSample.SetForegroundColour('red')
        else:
            self.bxSample.SetForegroundColour('black')
        
        if self.UserProfile.has_key('Name'):
            self.txtUserName.value=self.UserProfile['Name']
        if self.UserProfile.has_key('Contact'):
            self.txtUserContact.value=self.UserProfile['Contact']
        self.txtUserName.SetValue(self.txtUserName.Value)
        self.txtUserContact.SetValue(self.txtUserContact.Value)
        
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
        self.trayPosSelect.CreateGrid(len(self.CurTray),len(self.CurTray[0]))
        
        for ik in range(0,len(self.CurTray[0])):
            self.trayPosSelect.SetColLabelValue(ik,tArray[ik])
        for ij in range(0,len(self.CurTray)):
            self.trayPosSelect.SetRowLabelValue(ij,ij.__str__())
        self.redrawGrid()
        self.trayPosSelect.SetGridCursor(0,0)
    def importSampleXML(self,fileName):
        # safely import all settings into an xml file since that seems to be what the db will want
        
        from xml.dom import minidom
        cFile=minidom.parse(fileName)
        self.OnTxtUserNameText(())
        for mNode in cFile.childNodes:
        
            # touch the user fields to make sure the profile has the right keys
            
            if mNode.nodeName.upper()=='USER':
                # probably a valid xml file
                for tNode in mNode.childNodes:
                    tName=tNode.nodeName.strip()
                    if self.UserProfile.has_key(tName):
                        self.UserProfile[tName]=str(tNode.firstChild.nodeValue.strip())
                        
                    elif tName.upper()=='TRAY':
                        #import the tray!
                        
                        
                    
                        gRows=tSIZEROWS
                        gCols=tSIZECOLS
                        if tNode.hasAttribute('rows'): gRows=int(tNode.getAttribute('rows'))
                        if tNode.hasAttribute('cols'): gCols=int(tNode.getAttribute('cols'))
                        #print 'pre-init'+str(gRows)+','+str(gCols)
                        self.InitializeGrid(gRows,gCols)
                        
                        
                        for ctNode in tNode.childNodes:
                            ctName=ctNode.nodeName.upper().strip()
                            
                            if ctName=='SAMPLE':
                                
                                if (ctNode.hasAttribute('row-index') & ctNode.hasAttribute('col-index')):
                                    ij=int(ctNode.getAttribute('row-index'))
                                    ik=int(ctNode.getAttribute('col-index'))
                                    
                                    self.CurTray[ij][ik][2]=1
                                    for ctrNode in ctNode.childNodes:
                                        ctrName=ctrNode.nodeName.upper().strip()
                                        if ctrName=='NAME':
                                            self.CurTray[ij][ik][0]=ctrNode.firstChild.nodeValue.strip()
                                        elif ctrName=='DESC':
                                            self.CurTray[ij][ik][1]=ctrNode.firstChild.nodeValue.strip()
                                        elif ctrName=='STAGE_POSITION':
                                            if ctrNode.hasAttribute('id'):
                                                cId=int(ctrNode.getAttribute('id'))
                                                while cId>=len(self.CurTray[ij][ik][3]):
                                                    self.CurTray[ij][ik][3].append({})
                                                for ctrsNode in ctrNode.childNodes:
                                                    ctrsName=ctrsNode.nodeName.upper().strip()
                                                    if ctrsName=='EPICSCHANNEL':
                                                        chanName=ctrsNode.getAttribute('channel')
                                                        chanName=chanName[chanName.find(':')+1:]
                                                        print chanName
                                                        self.CurTray[ij][ik][3][cId][chanName]=float(ctrsNode.getAttribute('value'))

                            elif ctName=='SCRIPT':
                                print ctNode.toxml()
                                self.scriptText=''
                                for ctrNode in ctNode.childNodes:
                                    if ctrNode.nodeName.upper()=='SCRIPTLINE':        
                                        self.scriptText+=ctrNode.firstChild.nodeValue.strip()+'\n'
                        # only generate the dictionary
                        bText=self.scriptText
                        self.generateScript()
                        self.scriptText=bText                
                                            
    def exportSampleXML(self,fileName):
        # export all the settings into a nice xml file
        from xml.dom.minidom import Document
        # Create the minidom document
        doc = Document()
        # Create the <wml> base element
        user = doc.createElement("User")
        user.setAttribute('AlignTool-version',str(self.version))
        user.setAttribute('RobotScript-version',str(RSVersion))
        user.setAttribute('RobotCommon-version',str(RCVersion))
        doc.appendChild(user)
        cKeys=self.UserProfile.keys()
        for ibr in range(0,len(cKeys)):
            uField = doc.createElement(cKeys[ibr])
            user.appendChild(uField)
            ptext = doc.createTextNode(self.UserProfile[cKeys[ibr]])
            uField.appendChild(ptext)
        
        tray = doc.createElement("Tray")
        tray.setAttribute("cols", len(self.CurTray[0]).__str__())
        tray.setAttribute("rows", len(self.CurTray).__str__())
        user.appendChild(tray)
        
        # Create the main <card> element
        for ik in range(0,len(self.CurTray[0])):
            for ij in range(0,len(self.CurTray)):
                if self.CurTray[ij][ik][2]:
                    
                    sample = doc.createElement("Sample")
                    cPos=tArray[ik]+ij.__str__()
                    sample.setAttribute("position", cPos)
                    sample.setAttribute("row-index", str(ij))
                    sample.setAttribute("col-index", str(ik))
                    tray.appendChild(sample)
                    # create name field
                    sName = doc.createElement("name")
                    sample.appendChild(sName)
                    ptext = doc.createTextNode(self.CurTray[ij][ik][0])
                    sName.appendChild(ptext)
                    # Create description field
                    desc = doc.createElement("desc")
                    sample.appendChild(desc)
                    # Give the <p> elemenet some text
                    ptext = doc.createTextNode(self.CurTray[ij][ik][1])
                    desc.appendChild(ptext)
                    posLen=len(self.CurTray[ij][ik][3])
                    # add Saved Positions Array
                    for ijr in range(0,posLen):
                        pos = doc.createElement("stage_position")
                        pos.setAttribute("id", str(ijr))
                        appStr=''
                        if posLen>1: appStr='_P'+str(ijr)
                        pos.setAttribute("scriptID",self.CurTray[ij][ik][0]+appStr)
                        sample.appendChild(pos)
                        for ijk in range(0,len(self.CurTray[ij][ik][3][ijr])):
                            cItem=self.CurTray[ij][ik][3][ijr].items()[ijk]
                            posEle = doc.createElement("EpicsChannel")
                            posEle.setAttribute("channel", 'X02DA-ES1-SMP1:'+cItem[0])
                            posEle.setAttribute("value", cItem[1].__str__())
                            pos.appendChild(posEle)
        # Append Script
        script=doc.createElement("Script")
        tray.appendChild(script)
        tBox=self.scriptText.split('\n')
        for ijk in range(0,len(tBox)):
            dLineE = doc.createElement("scriptLine")
            dLineT=doc.createTextNode(tBox[ijk])
            dLineE.appendChild(dLineT)
            script.appendChild(dLineE)
        # Print our newly created XML
        fleOut=open(fileName,'w')
        fleOut.write(doc.toprettyxml(indent="  "))
        fleOut.close()

    def writePickleFile(self,outFile):
        self.generateScript(0)
        bundle=(self.UserProfile,self.CurTray,self.scriptText,self.scriptDict)
        pickle.dump((self.version,bundle),outFile)
    def loadPickleFile(self,loadFile):
        try:
            dataIn=pickle.load(loadFile)
        except:
            wx.MessageBox('File was not saved using this program, or is corrupted!')
            return 0
        if (type(dataIn)==type(('a','b'))):
            if len(dataIn)==2:
                (version,bundle)=dataIn
                if version>self.version:
                    wx.MessageBox('File was created with a newer version of align tool, it is possible some features may not work')
                elif version<self.version:
                    wx.MessageBox('File was created with an older version of AlignTool, some features may not work')
                try:
                    (self.UserProfile,self.CurTray,self.scriptText,self.scriptDict)=bundle
                    return 1
                except:
                    wx.MessageBox('Data in unexpected format!')
        return 0
    def setExpert(self,expCode):
        if expCode.lower().strip()=='expert724':
            self.txtExpertCode.Shown=0
            self.myRobotScript.expertPresent=1
            self.butSetLoad.Enable(1)
            self.butMoveLoad.Enable(1)    
        elif expCode=='':
            self.txtExpertCode.SetValue('')
            self.txtExpertCode.Shown=1
            self.myRobotScript.expertPresent=0
            self.butSetLoad.Enable(0)
            self.butMoveLoad.Enable(0)

    # These two functions handle the updating of the display from the robot parameters
    # In a thread-safe fashion
    def ksmThreadBindEvents(self):
        for cTh in self.ksmThread.keys():
            self.Connect(-1,-1,self.ksmThread[cTh][0],self.ksmThread[cTh][1])
    def threadRobotCom(self,rCmd,rArgs):
        thread.start_new_thread(rCmd,rArgs)
    def threadRobotStatus(self):
        while self.robotStatusLock.acquire():
            de=DataEvent(self.ksmThread['robotStageUpdate'][0])
            wx.PostEvent(self,de)
            time.sleep(0.2)
            
    def dispRobotStatus(self,event):
            mode=self.myRobot.mode()
            ready=self.myRobot.ready()
            stageMoving=self.myRobot.stageMoving()
            txtStat=''
            bLoad=1
            buLoad=1
            if mode==0:
                txtStat='Off'
                bLoad=0
                buLoad=0
            elif mode==1:
                txtStat='Unloaded'
                bLoad=1
                buLoad=0
            elif mode==2:
                txtStat='Loaded'
                bLoad=0
                buLoad=1
            else:
                txtStat='Err'
            txtStat+=', '
            if ready==1:
                txtStat+='Ready'
            elif ready==0:
                txtStat+='Not Ready'
                bLoad=0
                buLoad=0
            else:
                txtStat+='Err'
            #print txtStat
            self.staRobotStatus.SetLabel(txtStat)
            if stageMoving:
                #self.bxStage.SetForegroundColour('green')
                self.staStageStatus.SetLabel('Stage Moving')
                self.staStageStatus.SetForegroundColour('green')
                bLoad=0
                buLoad=0
            else:
                #self.bxStage.SetForegroundColour('red')
                self.staStageStatus.SetLabel('Stage Stopped')
                self.staStageStatus.SetForegroundColour('red')
            self.butLoad.Enable(bLoad)
            self.butUnload.Enable(buLoad)
            self.robotStatusLock.release()
    def OnButMoveLoad(self, event):
        self.generateScript(0)
        self.myRobotScript.ScriptDict=self.scriptDict
        self.myRobotScript.cmd_PUTSTAGE(['LoadPos'])
        event.Skip()
    
    
        

            
    









    


    
