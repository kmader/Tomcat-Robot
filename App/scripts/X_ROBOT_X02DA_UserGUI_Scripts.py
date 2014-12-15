#Boa:Frame:ScriptsPanel

import wx
import wx.stc
import os,thread
def csCreate(parent,mainPtr):
    return ScriptsPanel(parent,mainPtr)
panelInfo={}
panelInfo['Common Scripts']=csCreate
[wxID_SCRIPTSPANEL, wxID_SCRIPTSPANELBUTRUNSCRIPT, 
 wxID_SCRIPTSPANELSCRIPTLIST, wxID_SCRIPTSPANELSCRIPTOUTPUT, 
] = [wx.NewId() for _init_ctrls in range(4)]

class ScriptsPanel(wx.Panel):
    version=20090919
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Panel.__init__(self,prnt)
        #wx.Frame.__init__(self, id=wxID_SCRIPTSPANEL, name=u'ScriptsPanel',
        #      parent=prnt, pos=wx.Point(372, 386), size=wx.Size(514, 491),
        #      style=wx.DEFAULT_FRAME_STYLE, title=u'Tomcat Common Scripts')
        #self.SetClientSize(wx.Size(514, 491))

        self.ScriptOutput = wx.stc.StyledTextCtrl(id=wxID_SCRIPTSPANELSCRIPTOUTPUT,
              name=u'ScriptOutput', parent=self, pos=wx.Point(8, 176),
              size=wx.Size(514, 304), style=0)

        self.ScriptList = wx.ListBox(choices=[], id=wxID_SCRIPTSPANELSCRIPTLIST,
              name=u'ScriptList', parent=self, pos=wx.Point(8, 8),
              size=wx.Size(192, 144), style=0)
        self.ScriptList.Bind(wx.EVT_LISTBOX, self.OnScriptListListbox,
              id=wxID_SCRIPTSPANELSCRIPTLIST)

        self.butRunScript = wx.Button(id=wxID_SCRIPTSPANELBUTRUNSCRIPT,
              label=u'Execute', name=u'butRunScript', parent=self,
              pos=wx.Point(424, 16), size=wx.Size(125, 32), style=0)
        self.butRunScript.Bind(wx.EVT_BUTTON, self.OnButRunScriptButton,
              id=wxID_SCRIPTSPANELBUTRUNSCRIPT)

    def __init__(self, parent,mainPtr):
        self._init_ctrls(parent)
        self.scriptDatabase={};
        self.scriptDatabase['Missing Slices']={'Path':'python /work/sls/bin/X_ROBOT_X02DA_MissingSlices.py'}
        self.scriptDatabase['Show Errors in Logs']={'Path':'python /work/sls/bin/X_ROBOT_X02DA_ReadErrorLog.py'}
        self.scriptDatabase['Saturation Check']={'Path':'python /work/sls/bin/X_ROBOT_X02DA_AALib.py','Args':{'Scan':['-s'],'Directory':['-d "%"','$HOME/Data*/*/*/tif/*0007.tif'],'Last':['-l']}}
        self.scriptDatabase['Add DUO Account']={'Path':'python /work/sls/bin/X_ROBOT_X02DA_logbook.py -r'}
        self.scriptDatabase['Send SMS']={'Path':'X_ROBOT_X02DA_robotSMS.pl','Args':{'Number':['"%"','0787551438'],'zMessage':['"%"','Hey from SLS']}}
        self.scriptDatabase['List DB Samples']={'Path':'python /work/sls/bin/X_ROBOT_X02DA_database.py'}
        self.scriptButton={}
        self.argButtons={}
        xPos=8;
        for cEle in self.scriptDatabase.keys():
            self.ScriptList.Append(cEle)
            
        
    def runScript(self,sName):
        
        if self.scriptDatabase.has_key(sName):
            cScript=self.scriptDatabase[sName]
        else:
            cScript={}
        if cScript.has_key('Path'):
            basePath=cScript['Path']
            if cScript.has_key('Args'):
                for cArg in cScript['Args'].keys():
                    if self.argButtons.has_key(cArg):
                        cvArg=cScript['Args'][cArg]
                        if len(cvArg)==2:
                            basePath+=' '+self.argButtons[cArg].Value.join(cvArg[0].split('%'))
                        else:
                            if self.argButtons[cArg].Value:
                                basePath+=' '+cvArg[0]
            print basePath
            thread.start_new_thread(self.runScriptThread,(basePath,'$HOME/scriptBug.txt'))

    def runScriptThread(self,path,fileName='$HOME/scriptBug.txt'):
        outFile=os.path.expandvars(fileName)
        
        self.ScriptOutput.SetText(path+'\n'+' Running....')
        os.system(path+' > '+outFile)
        g=open(outFile,'r')
        myStr=g.read()
        g.close()
        os.remove(outFile)
        print myStr
        self.ScriptOutput.SetText(path+'\n'+myStr)   
    def exportXML(self,doc,xmlNode):
        print 'Nothing'
    def importXML(self,xmlNodes):
        print 'Nothing'
    

    def OnScriptListListbox(self, event):
        for nd in self.argButtons.keys():
            self.argButtons[nd].Visible=False
            self.argButtons[nd].Destroy()
            del(self.argButtons[nd])
            
        del(self.argButtons)
        self.argButtons={}
        if self.scriptDatabase.has_key(self.ScriptList.GetStringSelection()):
            cScript=self.scriptDatabase[self.ScriptList.GetStringSelection()]
        else:
            cScript={}
        if cScript.has_key('Args'):
            xPos=16+192
            yPos=8
            for cArg in cScript['Args'].keys():
                cvArg=cScript['Args'][cArg]
                if len(cvArg)==2:
                    self.argButtons[cArg] = wx.TextCtrl(name='textCtrl'+str(xPos+yPos), parent=self, pos=wx.Point(xPos, yPos),size=wx.Size(200, 28), style=0, value=cvArg[1])
                else:
                    self.argButtons[cArg] = wx.CheckBox(label=cArg, name='checkBox'+str(xPos+yPos), parent=self,pos=wx.Point(xPos, yPos), size=wx.Size(200, 28), style=0)
                yPos+=30
        event.Skip()

    def OnButRunScriptButton(self, event):
        self.runScript(self.ScriptList.GetStringSelection())
        event.Skip()

