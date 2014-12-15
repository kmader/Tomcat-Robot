#!/usr/bin/env python
#Boa:App:BoaApp

import wx

import X_ROBOT_X02DA_UserGUI_Main

modules ={u'X_ROBOT_X02DA_UserGUI_Main': [1,
                         'Main frame of Application',
                         u'X_ROBOT_X02DA_UserGUI_Main.py']}

class BoaApp(wx.App):
    def OnInit(self):
        self.main = X_ROBOT_X02DA_UserGUI_Main.create(None)
        self.main.Show()
        self.SetTopWindow(self.main)
        return True

def main():
    application = BoaApp(0)
    application.MainLoop()

if __name__ == '__main__':
    main()
