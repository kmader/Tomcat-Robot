#Boa:Frame:SequencerLauncher

import wx,sys,os,thread
import wx.grid
sys.path.insert (0, os.path.expandvars ("$SLSBASE/sls/bin/"))
try:
    import X_ROBOT_X02DA_database
    import X_ROBOT_X02DA_logbook
    dbEnabled=1
    logbookEnabled=1
except:
    print('Logbook and Database have not been loaded successfully')
    dbEnabled=0
    logbookEnabled=0
    

    
def slCreate(parent,mainPtr):
    return SequencerLauncher(parent,mainPtr)

panelInfo={}
#panelInfo['Sequence Launcher']=slCreate

[wxID_SEQUENCERLAUNCHER, wxID_SEQUENCERLAUNCHERIGNOREBEAM, 
 wxID_SEQUENCERLAUNCHERITERCOUNT, wxID_SEQUENCERLAUNCHERLAUNCHBUT, 
 wxID_SEQUENCERLAUNCHERSEQUENCELIST, wxID_SEQUENCERLAUNCHERSTATICTEXT1, 
 wxID_SEQUENCERLAUNCHERSTATICTEXT2, wxID_SEQUENCERLAUNCHERSTATICTEXT3, 
 wxID_SEQUENCERLAUNCHERSTATICTEXT4, wxID_SEQUENCERLAUNCHERTRAYLIST, 
] = [wx.NewId() for _init_ctrls in range(10)]

class SequencerLauncher(wx.Frame):
    version=20100530
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_SEQUENCERLAUNCHER,
              name=u'SequencerLauncher', parent=prnt, pos=wx.Point(262, 336),
              size=wx.Size(1009, 390), style=wx.DEFAULT_FRAME_STYLE,
              title=u'Sequencer Launcher')
        self.SetClientSize(wx.Size(1009, 390))

        self.trayList = wx.ListBox(choices=[],
              id=wxID_SEQUENCERLAUNCHERTRAYLIST, name=u'trayList', parent=self,
              pos=wx.Point(40, 40), size=wx.Size(184, 280), style=0)
        self.trayList.Bind(wx.EVT_LISTBOX, self.OnTrayListListbox,
              id=wxID_SEQUENCERLAUNCHERTRAYLIST)

        self.staticText1 = wx.StaticText(id=wxID_SEQUENCERLAUNCHERSTATICTEXT1,
              label=u'Select Tray:', name='staticText1', parent=self,
              pos=wx.Point(40, 16), size=wx.Size(75, 17), style=0)

        self.staticText2 = wx.StaticText(id=wxID_SEQUENCERLAUNCHERSTATICTEXT2,
              label=u'Check Command to Skip It', name='staticText2',
              parent=self, pos=wx.Point(248, 16), size=wx.Size(171, 17),
              style=0)

        self.iterCount = wx.TextCtrl(id=wxID_SEQUENCERLAUNCHERITERCOUNT,
              name=u'iterCount', parent=self, pos=wx.Point(256, 328),
              size=wx.Size(72, 24), style=0, value=u'0')
        self.iterCount.SetToolTipString(u'If a loop based scan was running, the iterator counter needs to be set to a value higher than the last measurement otherwise samples will be overwritten')

        self.staticText3 = wx.StaticText(id=wxID_SEQUENCERLAUNCHERSTATICTEXT3,
              label=u'Iterator Starting Count:', name='staticText3',
              parent=self, pos=wx.Point(96, 336), size=wx.Size(145, 17),
              style=0)

        self.sequenceList = wx.CheckListBox(choices=[],
              id=wxID_SEQUENCERLAUNCHERSEQUENCELIST, name=u'sequenceList',
              parent=self, pos=wx.Point(240, 40), size=wx.Size(400, 280),
              style=1)
        self.sequenceList.SetBackgroundStyle(wx.BG_STYLE_COLOUR)
        self.sequenceList.SetMinSize(wx.Size(0, 0))
        self.sequenceList.SetToolTipString(u'The script being sent to the sequencer. Checking the checkbox means that line will be ignored. Samples that have already been scanned  are automatically checked')

        self.ignoreBeam = wx.CheckBox(id=wxID_SEQUENCERLAUNCHERIGNOREBEAM,
              label=u'Ignore Beam Status', name=u'ignoreBeam', parent=self,
              pos=wx.Point(96, 360), size=wx.Size(216, 22), style=0)
        self.ignoreBeam.SetValue(False)
        self.ignoreBeam.SetToolTipString(u'The sequencer will not check the beam status, useful for scanning during shutdowns or special beamtimes')

        self.launchBut = wx.Button(id=wxID_SEQUENCERLAUNCHERLAUNCHBUT,
              label=u'Launch!', name=u'launchBut', parent=self,
              pos=wx.Point(552, 336), size=wx.Size(96, 32), style=0)
        self.launchBut.Bind(wx.EVT_BUTTON, self.OnLaunchButButton,
              id=wxID_SEQUENCERLAUNCHERLAUNCHBUT)

        self.staticText4 = wx.StaticText(id=wxID_SEQUENCERLAUNCHERSTATICTEXT4,
              label=u'Sample Status', name='staticText4', parent=self,
              pos=wx.Point(648, 16), size=wx.Size(92, 17), style=0)
        self.staticText4.SetHelpText(u'')

    def __init__(self, parent,mainPtr=''):
        self._init_ctrls(parent)
        self.mainPtr=mainPtr
        try:
            tList=X_ROBOT_X02DA_database.xGetTrayList()
        except:
            print 'Tray List Empty!!!'
            tList=[]
        #
        #self.trayList.AppendItems(['Bob','The','Cat','Makes'])
        self.trayList.AppendItems(tList)

    
    def OnTrayListListbox(self, event):
        
        try:
            [cTray,scriptText]=X_ROBOT_X02DA_database.xGetWholeTray(event.GetString())
        except:
            print 'Tray '+event.GetString()+' Empty!!!!'
            scriptText=''
        cList=scriptText.split('\n')
        self.writeColorSequence(cList)
        #self.sequenceList.AppendItems([event.GetString()+'-'+str(j) for j in range(1,50)])
        #self.sequenceList.SetChecked(range(0,39))
        #print self.sequenceList
        event.Skip()
    def writeSampleStatus(self,samples):
        try:
            self.sampleGrid.Destroy()
        except:
            print 'Not there yet!'
            
        self.sampleGrid = wx.grid.Grid(
              name=u'sampleGrid', parent=self, pos=wx.Point(648, 48),
              size=wx.Size(248+(712-648), 264), style=0)
        self.sampleGrid.SetRowLabelSize(0)
        self.sampleGrid.EnableEditing(False)
        
        
        self.sampleGrid.CreateGrid(len(samples),2)
        self.sampleGrid.SetColLabelValue(0,'Sample')
        self.sampleGrid.SetColLabelValue(1,'Status')
        self.sampleGrid.SetColSize(0,150)
        self.sampleGrid.SetColSize(1,150)
        StatusText=['No ROI','ROI Saved','Measured','Reconstructed']
        bgcolor=['Red','Green','Yellow','Yellow']
        #bgcolor=[wx.BLUE,wx.GREEN,wx.RED,wx.BLACK]
        ij=0
        for (cName,cStat) in samples:
            self.sampleGrid.SetCellValue(ij,0,cName)
            self.sampleGrid.SetCellValue(ij,1,StatusText[cStat])
            self.sampleGrid.SetCellBackgroundColour(ij,1,bgcolor[cStat])
            ij+=1
        #self.sampleGrid.AutoSize()
        #self.sampleGrid.DisableDragColSize()
        #self.sampleGrid.DisableDragRowSize()
        self.sampleGrid.ForceRefresh()
        self.sampleGrid.SetToolTipString(u'The samples and their current status in the TOMCAT Database (green = Ready to Scan, Red = Missing information, yellow= Already Scanned)')
        
        self.sampleGrid.SetScrollLineY(15)
    def writeColorSequence(self,cList):
        
        self.sequenceList.Clear()
        
        alreadyScanned=[]
        sampleList=[]
        self.sequenceList.SetDoubleBuffered(False)
        for i in range(0,len(cList)):
            item = wx.ListItem() 

            #item.SetData(id) 
            #item.SetWidth(200) 
            cLine=cList[i]
            cStat=1
            if cLine.upper().find('IMSAMPLE')>-1:
                
                cSample=cLine.split('"')
                cSample=cSample[1]
                cStat=X_ROBOT_X02DA_database.xGetSampleStatus(cSample)
                print (cSample,cStat)
                sampleList+=[(cSample,cStat)]
                #if cStat==0: cLine='*NOPOS*'+cLine
                #if cStat==2: cLine='*MEASE*'+cLine
                #if cStat==3: cLine='*RECON*'+cLine
                
                #self.sequenceList.SetItemBackgroundColour(i,bgcolor[cStat])
                #print self.sequenceList.GetItemBackgroundColour(i)
                #self.sequenceList.SetItemForegroundColour(i,bgcolor[cStat])
                #self.sequenceList.DefaultAttributes.colBg=bgcolor[cStat]
                self.sequenceList.Refresh()
                #self.sequenceList.Show()
            item.SetText(cLine)
            #dir(item) 
            #self.sequenceList.Insert(i,item)
            self.sequenceList.Append(cLine)
            if cStat>1: alreadyScanned+=[i]
            
            #self.sequenceList.SetItemBackgroundColour(i,bgcolor[cStat])
        self.sequenceList.SetChecked(alreadyScanned)
        self.writeSampleStatus(sampleList)
    def buildLaunchCommand(self):
        toSkip=[str(cVal) for cVal in self.sequenceList.GetChecked()]
        launchCommand='python /work/sls/bin/X_ROBOT_X02DA_dbSequencer.py -L'
        #launchCommand='python X_ROBOT_X02DA_UserGUI_Sequencer_Settings.py '
        if len(toSkip)>0: launchCommand+=' --skiplines='+','.join(toSkip)
        launchCommand+=' -G'*self.ignoreBeam.Value
        launchCommand+=' --name='+self.trayList.StringSelection
        return launchCommand
    def OnLaunchButButton(self, event):
        thread.start_new_thread(os.system,(self.buildLaunchCommand(),))
        print self.buildLaunchCommand()
        event.Skip()
    def exportXML(self,doc,xmlNode):
        print 'Nothing'
    def importXML(self,xmlNodes):
        print 'Nothing'

class SSApp(wx.App):
    def OnInit(self):
        self.main = SequencerLauncher(None)
        self.main.Show()
        self.SetTopWindow(self.main)
        return True

def main():
    application = SSApp(0)
    application.MainLoop()

if __name__ == '__main__':
    main()
