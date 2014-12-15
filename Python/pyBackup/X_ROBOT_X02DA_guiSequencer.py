#Boa:Frame:X_ROBOT_X02DA_guiSequencer

import wx
import wx.stc
import thread
import time
GSVersion=20081127
print "Using GUISequencer Library Version : "+str(GSVersion)
wxDATA_EVENT=wx.NewEventType()
def EVT_DATA_EVENT(win,func):
    win.Connect(-1,-1,wxDATA_EVENT,func)
class DataEvent(wx.PyEvent):
    def __init__(self):
            wx.PyEvent.__init__(self)
            self.SetEventType(wxDATA_EVENT)
            #self.mode=mode
            #self.stagemoving=stagemoving
            #self.data=data
def create(parent):
    return guiSequencer(parent)

[wxID_GUISEQUENCER, wxID_GUISEQUENCERBUTBEGIN, wxID_GUISEQUENCERBUTPAUSE, 
 wxID_GUISEQUENCERBUTRESET, wxID_GUISEQUENCERBUTSKIPNEXT, 
 wxID_GUISEQUENCERTXTROBOTSTATUS, wxID_GUISEQUENCERTXTSCRIPT, 
] = [wx.NewId() for _init_ctrls in range(7)]

class guiSequencer(wx.Frame):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_GUISEQUENCER, name='', parent=prnt,
              pos=wx.Point(525, 248), size=wx.Size(699, 500),
              style=wx.DEFAULT_FRAME_STYLE, title='GUI Sequencer')
        self.SetClientSize(wx.Size(699, 500))

        self.txtScript = wx.stc.StyledTextCtrl(name=u'txtScript', parent=self,
              pos=wx.Point(5, 40), size=wx.Size(685, 430), style=0)
        self.txtScript.SetEdgeColumn(0)

        self.butBegin = wx.Button(id=wxID_GUISEQUENCERBUTBEGIN, label=u'Begin',
              name=u'butBegin', parent=self, pos=wx.Point(24, 0),
              size=wx.Size(85, 32), style=0)
        self.butBegin.Bind(wx.EVT_BUTTON, self.OnButBeginButton,
              id=wxID_GUISEQUENCERBUTBEGIN)

        self.butPause = wx.Button(id=wxID_GUISEQUENCERBUTPAUSE, label=u'Pause',
              name=u'butPause', parent=self, pos=wx.Point(112, 0),
              size=wx.Size(88, 32), style=0)
        self.butPause.Bind(wx.EVT_BUTTON, self.OnButPauseButton,
              id=wxID_GUISEQUENCERBUTPAUSE)

        self.txtRobotStatus = wx.TextCtrl(id=wxID_GUISEQUENCERTXTROBOTSTATUS,
              name=u'txtRobotStatus', parent=self, pos=wx.Point(392, 0),
              size=wx.Size(296, 24), style=0, value=u'Robot Status:')

        self.butSkipNext = wx.Button(id=wxID_GUISEQUENCERBUTSKIPNEXT,
              label=u'Skip Line', name=u'butSkipNext', parent=self,
              pos=wx.Point(200, 0), size=wx.Size(80, 32), style=0)
        self.butSkipNext.Bind(wx.EVT_BUTTON, self.OnButSkipNextButton,
              id=wxID_GUISEQUENCERBUTSKIPNEXT)

        self.butReset = wx.Button(id=wxID_GUISEQUENCERBUTRESET, label=u'Reset',
              name=u'butReset', parent=self, pos=wx.Point(280, 0),
              size=wx.Size(101, 32), style=0)
        self.butReset.Bind(wx.EVT_BUTTON, self.OnButResetButton,
              id=wxID_GUISEQUENCERBUTRESET)

    def __init__(self, parent):
        self._init_ctrls(None)
        self.dad=parent
        self.txtScript.SetText(parent.scriptText)
        
        self.txtScript.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
        self.txtScript.SetMarginWidth(1, 25)
        #self.txtScript.SetCaretForeground('green')
        self.txtScript.SetSelBackground(1,'green') 
        #self.txtScript.SetSelectionMode(1)
        self.txtScript.SetReadOnly(1)
        
        EVT_DATA_EVENT (self, self.dispSequencerStatus)
        #thread.start_new_thread ( self.getRobotStatus,() )
        thread.start_new_thread ( self.threadSequencerStatus,() )
        thread.start_new_thread(self.robotScriptThread,())
    def robotScriptThread(self):
        self.scriptDone=0
        self.dad.myRobotScript.executeScript()
        self.scriptDone=1
    def selLine(self,lineNum):
        self.txtScript.GotoLine(lineNum-1)
        sPos=self.txtScript.GetCurrentPos() 
        ePos=self.txtScript.GetLineEndPosition(lineNum-1)
        self.txtScript.SetSelection(sPos,ePos) 
    def threadSequencerStatus(self):
        while 1:
            de=DataEvent()
            wx.PostEvent(self,de)
            time.sleep(0.25)
    def dispSequencerStatus(self,event):
        self.txtRobotStatus.SetValue(self.dad.myRobotScript.chFeedback.getVal())
        if self.dad.myRobotScript.chPause.getVal():
             self.txtScript.SetSelBackground(1,'red')
        else:
             self.txtScript.SetSelBackground(1,'green')  
        linStatus=self.dad.myRobotScript.chLineFeedback.getVal()
        if type(linStatus)==type(' '):
            if linStatus.find('of')>0:
                linNum=int(linStatus[0:linStatus.find('of')])
                self.selLine(linNum)
            else:
                self.txtScript.SetSelection(0,0)
        else:
            self.txtScript.SetSelection(0,0)
    def OnButBeginButton(self, event):
        self.dad.myRobotScript.chBegin.putVal(1)
        
        event.Skip()

    def OnButPauseButton(self, event):
        self.butBegin.SetLabel('Resume')
        self.dad.myRobotScript.chPause.putVal(1)
        event.Skip()

    def OnButSkipNextButton(self, event):
        self.dad.myRobotScript.chSkip.putVal(1)
        event.Skip()

    def OnButResetButton(self, event):
        self.dad.myRobotScript.chReset.putVal(1)
        if self.scriptDone:
            # script has already finished running, leider
            thread.start_new_thread(self.robotScriptThread,())
            self.butBegin.SetLabel('Begin')
        event.Skip()
