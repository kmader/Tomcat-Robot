#!/usr/bin/env python
#Boa:App:BoaApp

import wx

import AlignDisp


modules ={u'AlignDisp': [1, 'Main frame of Application', u'AlignDisp.py'],
 u'X_ROBOT_X02DA_robotCommon': [0, '', u'X_ROBOT_X02DA_robotCommon.py'],
 u'X_ROBOT_X02DA_robotScript': [0, '', u'X_ROBOT_X02DA_robotScript.py'],
 u'X_ROBOT_X02DA_guiSequencer': [0, '', u'X_ROBOT_X02DA_guiSequencer.py']}

class BoaApp(wx.App):
    def OnInit(self):
        self.main = AlignDisp.create(None)
        self.main.Show()
        self.SetTopWindow(self.main)
        return True

def main():
    application = BoaApp(0)
    application.MainLoop()

if __name__ == '__main__':
    main()
