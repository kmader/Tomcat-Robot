import wx
import wx.stc
import thread

def sqCreate(parent,mainPtr):
    return GUI_Sequencer(parent,mainPtr)
panelInfo={}
panelInfo['Sequencer']=sqCreate
#wx.Panel.__init__(self,parent=prnt)
def threadedRun(rCmd,rArgs):
    thread.start_new_thread(rCmd,rArgs)

[wxID_GUI_SEQUENCER, wxID_GUI_SEQUENCERBUTBEGIN, wxID_GUI_SEQUENCERBUTPAUSE, 
 wxID_GUI_SEQUENCERBUTRESET, wxID_GUI_SEQUENCERBUTSKIPNEXT, 
 wxID_GUI_SEQUENCERTXTROBOTSTATUS, wxID_GUI_SEQUENCERTXTSCRIPT, 
] = [wx.NewId() for _init_ctrls in range(7)]

class GUI_Sequencer(wx.Panel):
    version=20090331
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        #wx.Frame.__init__(self, id=wxID_GUI_SEQUENCER, name=u'GUI_Sequencer',
        #      parent=prnt, pos=wx.Point(320, 231), size=wx.Size(853, 616),
        #      style=wx.DEFAULT_FRAME_STYLE, title='Frame1')
        #self.SetClientSize(wx.Size(853, 616))
        wx.Panel.__init__(self,parent=prnt)
        self.txtScript = wx.stc.StyledTextCtrl(name=u'txtScript', parent=self,
              pos=wx.Point(5, 80), size=wx.Size(685, 390), style=0)
        self.txtScript.SetEdgeColumn(0)

        self.butBegin = wx.Button(id=wxID_GUI_SEQUENCERBUTBEGIN, label=u'Begin',
              name=u'butBegin', parent=self, pos=wx.Point(24, 0),
              size=wx.Size(85, 32), style=0)
        self.butBegin.Bind(wx.EVT_BUTTON, self.OnButBeginButton,
              id=wxID_GUI_SEQUENCERBUTBEGIN)

        self.butPause = wx.Button(id=wxID_GUI_SEQUENCERBUTPAUSE, label=u'Pause',
              name=u'butPause', parent=self, pos=wx.Point(112, 0),
              size=wx.Size(88, 32), style=0)
        self.butPause.Bind(wx.EVT_BUTTON, self.OnButPauseButton,
              id=wxID_GUI_SEQUENCERBUTPAUSE)

        self.txtRobotStatus = wx.TextCtrl(id=wxID_GUI_SEQUENCERTXTROBOTSTATUS,
              name=u'txtRobotStatus', parent=self, pos=wx.Point(392, 0),
              size=wx.Size(296, 24), style=0, value=u'Robot Status:')
        self.txtRobotStatus.SetToolTipString(u'X02DA-ES1-ROBO:GUI-FEEDBACK')
        self.butSkipNext = wx.Button(id=wxID_GUI_SEQUENCERBUTSKIPNEXT,
              label=u'Skip Line', name=u'butSkipNext', parent=self,
              pos=wx.Point(200, 0), size=wx.Size(80, 32), style=0)
        self.butSkipNext.Bind(wx.EVT_BUTTON, self.OnButSkipNextButton,
              id=wxID_GUI_SEQUENCERBUTSKIPNEXT)

        self.butReset = wx.Button(id=wxID_GUI_SEQUENCERBUTRESET, label=u'Reset',
              name=u'butReset', parent=self, pos=wx.Point(280, 0),
              size=wx.Size(50, 32), style=0)
        self.butReset.Bind(wx.EVT_BUTTON, self.OnButResetButton,
              id=wxID_GUI_SEQUENCERBUTRESET)
        self.butStop = wx.Button(label=u'Stop',
              name=u'butStop', parent=self, pos=wx.Point(330, 0),
              size=wx.Size(50, 32), style=0)
        self.butStop.Bind(wx.EVT_BUTTON, self.OnButStopButton)
        self.txtSampleName = wx.TextCtrl(
              name=u'txtSampleName', parent=self, pos=wx.Point(24, 40),
              size=wx.Size(100, 24), style=0, value=u'Sample Name:')
        self.txtSampleName.SetToolTipString(u'X02DA-SCAN-CAM1:FILPRE')
        self.txtCurrentCommand = wx.TextCtrl(
              name=u'txtCurrentCommand', parent=self, pos=wx.Point(124, 40),
              size=wx.Size(100, 24), style=0, value=u'Current Command:')
        self.txtCurrentCommand.SetToolTipString(u'X02DA-ES1-ROBO:GUI-CCMD')
    def __init__(self, parent,mainPtr):
        self._init_ctrls(parent)
        self.mainPtr=mainPtr
        self.txtScript.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
        self.txtScript.SetMarginWidth(1, 25)
        #self.txtScript.SetCaretForeground('green')
        self.txtScript.SetSelBackground(1,'green') 
        #self.txtScript.SetSelectionMode(1)
        self.txtScript.SetReadOnly(1)
        self.mainPtr.kRegisterEvent('robotScriptStart',self.robotScriptStart) # robotStatusUpdate
        self.mainPtr.kRegisterEvent('robotScriptBegin',self.robotScriptBegin)
        self.mainPtr.kRegisterEvent('robotScriptPause',self.robotScriptPause)
        self.mainPtr.kRegisterEvent('robotScriptStop',self.robotScriptStop)
        self.mainPtr.kRegisterEvent('robotScriptSkip',self.robotScriptSkip)
        self.mainPtr.kRegisterEvent('robotScriptReset',self.robotScriptReset)
        self.mainPtr.kRegisterPanelEvent(self.pullScript)
        self.mainPtr.kRegisterTimerEvent(self.robotScriptStatus)
        self.mainPtr.kRegisterCtrl(self.txtSampleName)
        self.mainPtr.kRegisterCtrl(self.txtRobotStatus)
        self.mainPtr.kRegisterCtrl(self.txtCurrentCommand)
    def pullScript(self,event):
        myRobotScript=event.myRobotScript
        self.txtScript.SetReadOnly(0)
        self.txtScript.SetText(myRobotScript.sequenceText)
        self.txtScript.SetReadOnly(1)    
    def robotScriptStart(self,event):
        event.myRobotScript.chBegin.putVal(1)
    def selLine(self,lineNum):
        self.txtScript.SetReadOnly(0)
        self.txtScript.GotoLine(lineNum-1)
        sPos=self.txtScript.GetCurrentPos() 
        ePos=self.txtScript.GetLineEndPosition(lineNum-1)
        self.txtScript.SetSelection(sPos,ePos) 
        self.txtScript.SetReadOnly(1)
    def robotScriptStatus(self,event):
        myRobotScript=event.myRobotScript
        statusText=str(myRobotScript.chFeedback.getVal())
        pauseVal=int(myRobotScript.chPause.getVal())
        linStatus=str(myRobotScript.chLineFeedback.getVal())
        
        #self.txtRobotStatus.SetValue(statusText)
        if pauseVal:
             self.txtScript.SetSelBackground(1,'red')
        else:
             self.txtScript.SetSelBackground(1,'green')  
        
        if type(linStatus)==type(' '):
            if linStatus.find('of')>0:
                linNum=int(linStatus[0:linStatus.find('of')])
                self.selLine(linNum)
            else:
                self.txtScript.SetSelection(0,0)
        else:
            self.txtScript.SetSelection(0,0)

    def OnButBeginButton(self, event):
        self.mainPtr.kPostEvent('robotScriptBegin',[])
        self.mainPtr.kPostEvent('robotScriptStart',[])
        event.Skip()
    def OnButPauseButton(self, event):
        self.butBegin.SetLabel('Resume')
        self.mainPtr.kPostEvent('robotScriptPause',[])
        event.Skip()
    def OnButSkipNextButton(self, event):
        self.mainPtr.kPostEvent('robotScriptSkip',[])
        event.Skip()
    def OnButResetButton(self, event):
        self.mainPtr.kPostEvent('robotScriptReset',[])
        self.butBegin.SetLabel('Begin')
        event.Skip()
    def OnButStopButton(self, event):
        self.mainPtr.kPostEvent('robotScriptStop',[])
        self.butBegin.SetLabel('Begin')
        event.Skip()
    def robotScriptBegin(self,event):
        event.myRobotScript.chBegin.putVal(1)
    def robotScriptPause(self,event):
        event.myRobotScript.chPause.putVal(1)
    def robotScriptStop(self,event):
        event.myRobotScript.chStop.putVal(1)
    def robotScriptSkip(self,event):
        event.myRobotScript.chSkip.putVal(1)
    def robotScriptReset(self,event):
        event.myRobotScript.chReset.putVal(1)
    def exportXML(self,doc,xmlNode):
        print 'Nothing'
    def importXML(self,xmlNodes):
        print 'Nothing'