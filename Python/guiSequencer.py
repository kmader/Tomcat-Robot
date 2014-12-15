#Boa:Frame:guiSequencer

import wx
import wx.stc
import thread
import time
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
 wxID_GUISEQUENCERTXTROBOTSTATUS, wxID_GUISEQUENCERTXTSCRIPT, 
] = [wx.NewId() for _init_ctrls in range(5)]

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
              name=u'txtRobotStatus', parent=self, pos=wx.Point(328, 8),
              size=wx.Size(216, 24), style=0, value=u'Robot Status:')

    def __init__(self, parent):
        self._init_ctrls(parent)
        self.dad=parent
        self.txtScript.SetText(parent.scriptText)
        
        self.txtScript.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
        self.txtScript.SetMarginWidth(1, 25)
        self.txtScript.SetCaretForeground('green')
        self.txtScript.SetSelectionMode(2)
        self.txtScript.SetReadOnly(1)
        
        EVT_DATA_EVENT (self, self.dispSequencerStatus)
        #thread.start_new_thread ( self.getRobotStatus,() )
        thread.start_new_thread ( self.threadSequencerStatus,() )
        thread.start_new_thread(self.dad.myRobotScript.executeScript,())
        
    def threadSequencerStatus(self):
        while 1:
            de=DataEvent()
            wx.PostEvent(self,de)
            time.sleep(0.25)
    def dispSequencerStatus(self,event):
        self.txtRobotStatus.SetValue(self.dad.myRobotScript.chFeedback.getVal())
        linStatus=self.dad.myRobotScript.chLineFeedback.getVal()
        if linStatus.find('of')>0:
            linNum=int(linStatus[0:linStatus.find('of')])
            self.txtScript.SetSelection(linNum,linNum)
        
    def OnButBeginButton(self, event):
        self.dad.myRobotScript.chLineFeedback.putVal('4 of 5')
        #self.dad.myRobotScript.chBegin.putVal(1)
        
        event.Skip()

    def OnButPauseButton(self, event):
        self.dad.myRobotScript.chPause.putVal(1)
        event.Skip()
