#Boa:Frame:GUI_ScanSettings

import wx
# initialize the plugin header dictionary

def create(parent):
    return GUI_ScanSettings(parent)

def ssCreate(parent,mainPtr):
    return GUI_ScanSettings(parent,mainPtr)
panelInfo={}
panelInfo['Scan Settings']=ssCreate
[wxID_GUI_SCANSETTINGS, wxID_GUI_SCANSETTINGSSPINSTATUS1, 
 wxID_GUI_SCANSETTINGSSPINSTATUS10, wxID_GUI_SCANSETTINGSSPINSTATUS2, 
 wxID_GUI_SCANSETTINGSSPINSTATUS3, wxID_GUI_SCANSETTINGSSPINSTATUS4, 
 wxID_GUI_SCANSETTINGSSPINSTATUS5, wxID_GUI_SCANSETTINGSSPINSTATUS6, 
 wxID_GUI_SCANSETTINGSSPINSTATUS7, wxID_GUI_SCANSETTINGSSPINSTATUS8, 
 wxID_GUI_SCANSETTINGSSPINSTATUS9, wxID_GUI_SCANSETTINGSSTATICBOX1, 
 wxID_GUI_SCANSETTINGSSTATICBOX2, wxID_GUI_SCANSETTINGSSTATICBOX3, 
 wxID_GUI_SCANSETTINGSSTATICBOX4, wxID_GUI_SCANSETTINGSSTATICTEXT1, 
 wxID_GUI_SCANSETTINGSSTATICTEXT10, wxID_GUI_SCANSETTINGSSTATICTEXT11, 
 wxID_GUI_SCANSETTINGSSTATICTEXT12, wxID_GUI_SCANSETTINGSSTATICTEXT13, 
 wxID_GUI_SCANSETTINGSSTATICTEXT14, wxID_GUI_SCANSETTINGSSTATICTEXT15, 
 wxID_GUI_SCANSETTINGSSTATICTEXT16, wxID_GUI_SCANSETTINGSSTATICTEXT17, 
 wxID_GUI_SCANSETTINGSSTATICTEXT18, wxID_GUI_SCANSETTINGSSTATICTEXT19, 
 wxID_GUI_SCANSETTINGSSTATICTEXT2, wxID_GUI_SCANSETTINGSSTATICTEXT20, 
 wxID_GUI_SCANSETTINGSSTATICTEXT21, wxID_GUI_SCANSETTINGSSTATICTEXT22, 
 wxID_GUI_SCANSETTINGSSTATICTEXT23, wxID_GUI_SCANSETTINGSSTATICTEXT24, 
 wxID_GUI_SCANSETTINGSSTATICTEXT25, wxID_GUI_SCANSETTINGSSTATICTEXT26, 
 wxID_GUI_SCANSETTINGSSTATICTEXT3, wxID_GUI_SCANSETTINGSSTATICTEXT4, 
 wxID_GUI_SCANSETTINGSSTATICTEXT5, wxID_GUI_SCANSETTINGSSTATICTEXT6, 
 wxID_GUI_SCANSETTINGSSTATUS1, wxID_GUI_SCANSETTINGSSTATUS10, 
 wxID_GUI_SCANSETTINGSSTATUS11, wxID_GUI_SCANSETTINGSSTATUS2, 
 wxID_GUI_SCANSETTINGSSTATUS3, wxID_GUI_SCANSETTINGSSTATUS4, 
 wxID_GUI_SCANSETTINGSSTATUS5, wxID_GUI_SCANSETTINGSSTATUS6, 
 wxID_GUI_SCANSETTINGSSTATUS7, wxID_GUI_SCANSETTINGSSTATUS8, 
 wxID_GUI_SCANSETTINGSSTATUS9, wxID_GUI_SCANSETTINGSSTATUSCHECK1, 
 wxID_GUI_SCANSETTINGSSTATUSCHECK2, wxID_GUI_SCANSETTINGSSTATUSTEXT1, 
 wxID_GUI_SCANSETTINGSSTATUSTEXT2, 
] = [wx.NewId() for _init_ctrls in range(53)]

class GUI_ScanSettings(wx.Panel):
    version=20090203
    #wx.Panel.__init__(self,parent=prnt)
    #
    def _init_ctrls(self, prnt):
        wx.Panel.__init__(self,parent=prnt)
        # generated method, don't edit
        #wx.Frame.__init__(self, id=wxID_GUI_SCANSETTINGS,
        #      name=u'GUI_ScanSettings', parent=prnt, pos=wx.Point(364, 110),
        #      size=wx.Size(608, 430), style=wx.DEFAULT_FRAME_STYLE,
        #      title=u'Frame1')
        self.SetClientSize(wx.Size(608, 430))

        self.staticBox1 = wx.StaticBox(id=wxID_GUI_SCANSETTINGSSTATICBOX1,
              label=u'SLS Status', name='staticBox1', parent=self,
              pos=wx.Point(8, 8), size=wx.Size(584, 56), style=0)
        self.staticBox1.SetMinSize(wx.Size(0, 0))

        self.staticBox2 = wx.StaticBox(id=wxID_GUI_SCANSETTINGSSTATICBOX2,
              label=u'Tomcat Status', name='staticBox2', parent=self,
              pos=wx.Point(8, 64), size=wx.Size(584, 72), style=0)
        self.staticBox2.SetMinSize(wx.Size(-1, -1))

        self.staticBox3 = wx.StaticBox(id=wxID_GUI_SCANSETTINGSSTATICBOX3,
              label=u'Experiment Status', name='staticBox3', parent=self,
              pos=wx.Point(8, 136), size=wx.Size(584, 136), style=0)
        self.staticBox3.SetMinSize(wx.Size(-1, 100))

        self.staticBox4 = wx.StaticBox(id=wxID_GUI_SCANSETTINGSSTATICBOX4,
              label=u'Acquisition Settings', name='staticBox4', parent=self,
              pos=wx.Point(8, 272), size=wx.Size(584, 144), style=0)
        self.staticBox4.SetMinSize(wx.Size(-1, 100))

        self.staticText1 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATICTEXT1,
              label=u'Machine Status:', name='staticText1', parent=self,
              pos=wx.Point(16, 32), size=wx.Size(102, 17), style=0)

        self.status1 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATUS1,
              label=u'ACOAU-ACCU:OP-MODE.VAL', name=u'status1', parent=self,
              pos=wx.Point(120, 32), size=wx.Size(158, 17), style=0)

        self.staticText2 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATICTEXT2,
              label=u'Ring Current:', name='staticText2', parent=self,
              pos=wx.Point(344, 32), size=wx.Size(86, 17), style=0)

        self.status2 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATUS2,
              label=u'ARIDI-PCT:CURRENT', name=u'status2', parent=self,
              pos=wx.Point(448, 32), size=wx.Size(131, 17), style=0)

        self.staticText3 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATICTEXT3,
              label=u'Beam Energy[keV]:', name='staticText3', parent=self,
              pos=wx.Point(16, 88), size=wx.Size(125, 17), style=0)

        self.status3 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATUS3,
              label=u'X02DA-OP-ENE:ACTUAL', name=u'status3', parent=self,
              pos=wx.Point(144, 88), size=wx.Size(155, 17), style=0)

        self.staticText4 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATICTEXT4,
              label=u'Scintillator: ', name='staticText4', parent=self,
              pos=wx.Point(16, 112), size=wx.Size(75, 17), style=0)

        self.status4 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATUS4,
              label=u'X02DA-SCAN-CAM1:SCINTIL', name=u'status4', parent=self,
              pos=wx.Point(144, 112), size=wx.Size(181, 17), style=0)

        self.staticText5 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATICTEXT5,
              label=u'Mono Stripe: ', name='staticText5', parent=self,
              pos=wx.Point(344, 88), size=wx.Size(84, 17), style=0)

        self.status5 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATUS5,
              label=u'X02DA-OP-MO1:ACT_STR', name=u'status5', parent=self,
              pos=wx.Point(440, 88), size=wx.Size(166, 17), style=0)

        self.staticText6 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATICTEXT6,
              label=u'Objective:', name='staticText6', parent=self,
              pos=wx.Point(344, 112), size=wx.Size(67, 17), style=0)

        self.status11 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATUS11,
              label=u'X02DA-ES1-MS1:LNSSEL', name=u'status11', parent=self,
              pos=wx.Point(440, 112), size=wx.Size(157, 17), style=0)

        self.staticText10 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATICTEXT10,
              label=u'Storage:', name='staticText10', parent=self,
              pos=wx.Point(16, 216), size=wx.Size(80, 17), style=0)

        self.statusText1 = wx.TextCtrl(id=wxID_GUI_SCANSETTINGSSTATUSTEXT1,
              name=u'statusText1', parent=self, pos=wx.Point(104, 216),
              size=wx.Size(200, 24), style=0, value=u'X02DA-SCAN-CAM1:STORAGE')

        self.staticText11 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATICTEXT11,
              label=u'File Prefix:', name='staticText11', parent=self,
              pos=wx.Point(16, 240), size=wx.Size(66, 17), style=0)

        self.statusText2 = wx.TextCtrl(id=wxID_GUI_SCANSETTINGSSTATUSTEXT2,
              name=u'statusText2', parent=self, pos=wx.Point(104, 240),
              size=wx.Size(200, 24), style=0, value=u'X02DA-SCAN-CAM1:FILPRE')

        self.staticText12 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATICTEXT12,
              label=u'Experiment Status:', name='staticText12', parent=self,
              pos=wx.Point(344, 160), size=wx.Size(122, 17), style=0)

        self.status6 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATUS6,
              label=u'X02DA-SCAN-SCN1:STATUS', name=u'status6', parent=self,
              pos=wx.Point(472, 160), size=wx.Size(179, 17), style=0)

        self.status7 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATUS7,
              label=u'X02DA-SCAN-CAM1:STATUS', name=u'status7', parent=self,
              pos=wx.Point(472, 184), size=wx.Size(181, 17), style=0)

        self.staticText13 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATICTEXT13,
              label=u'CCD Status:', name='staticText13', parent=self,
              pos=wx.Point(344, 184), size=wx.Size(79, 17), style=0)

        self.staticText14 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATICTEXT14,
              label=u'CCD-Trigger Status:', name='staticText14', parent=self,
              pos=wx.Point(344, 200), size=wx.Size(127, 17), style=0)

        self.status8 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATUS8,
              label=u'X02DA-SCAN-CAM1:SNAP', name=u'status8', parent=self,
              pos=wx.Point(472, 200), size=wx.Size(166, 17), style=0)

        self.staticText15 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATICTEXT15,
              label=u'Time to go:', name='staticText15', parent=self,
              pos=wx.Point(344, 224), size=wx.Size(74, 17), style=0)

        self.status9 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATUS9,
              label=u'X02DA-SCAN-SCN1:SCNFINTME', name=u'status9', parent=self,
              pos=wx.Point(472, 224), size=wx.Size(203, 17), style=0)

        self.staticText16 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATICTEXT16,
              label=u'Actual angular pos:', name='staticText16', parent=self,
              pos=wx.Point(344, 248), size=wx.Size(125, 17), style=0)

        self.status10 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATUS10,
              label=u'X02DA-SCAN-SCN1:ACTROT', name=u'status12', parent=self,
              pos=wx.Point(472, 248), size=wx.Size(185, 17), style=0)

        self.staticText17 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATICTEXT17,
              label=u'Number of Projections:', name='staticText17', parent=self,
              pos=wx.Point(16, 296), size=wx.Size(147, 17), style=0)

        self.spinStatus1 = wx.SpinCtrl(id=wxID_GUI_SCANSETTINGSSPINSTATUS1,
              initial=0, max=99999, min=1, name=u'spinStatus1', parent=self,
              pos=wx.Point(176, 288), size=wx.Size(64, 27),
              style=wx.SP_ARROW_KEYS)
        self.spinStatus1.SetToolTipString(u'X02DA-SCAN-SCN1:NPRJ')

        self.staticText18 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATICTEXT18,
              label=u'Flat checks frequency:', name='staticText18', parent=self,
              pos=wx.Point(16, 320), size=wx.Size(147, 17), style=0)

        self.spinStatus2 = wx.SpinCtrl(id=wxID_GUI_SCANSETTINGSSPINSTATUS2,
              initial=0, max=99999, min=0, name=u'spinStatus2', parent=self,
              pos=wx.Point(176, 312), size=wx.Size(64, 27),
              style=wx.SP_ARROW_KEYS)
        self.spinStatus2.SetToolTipString(u'X02DA-SCAN-SCN1:FLTFRQ')

        self.staticText19 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATICTEXT19,
              label=u'Num. flats during scan:', name='staticText19',
              parent=self, pos=wx.Point(16, 344), size=wx.Size(150, 17),
              style=0)

        self.spinStatus3 = wx.SpinCtrl(id=wxID_GUI_SCANSETTINGSSPINSTATUS3,
              initial=0, max=99999, min=0, name=u'spinStatus3', parent=self,
              pos=wx.Point(176, 336), size=wx.Size(64, 27),
              style=wx.SP_ARROW_KEYS)
        self.spinStatus3.SetToolTipString(u'X02DA-SCAN-SCN1:NINFLT')

        self.staticText20 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATICTEXT20,
              label=u'Num. flats before/after:', name='staticText20',
              parent=self, pos=wx.Point(16, 368), size=wx.Size(151, 17),
              style=0)

        self.spinStatus4 = wx.SpinCtrl(id=wxID_GUI_SCANSETTINGSSPINSTATUS4,
              initial=0, max=99999, min=0, name=u'spinStatus4', parent=self,
              pos=wx.Point(176, 360), size=wx.Size(64, 27),
              style=wx.SP_ARROW_KEYS)
        self.spinStatus4.SetToolTipString(u'X02DA-SCAN-SCN1:NPPFLT')

        self.staticText21 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATICTEXT21,
              label=u'Num. darks before/after:', name='staticText21',
              parent=self, pos=wx.Point(16, 392), size=wx.Size(159, 17),
              style=0)

        self.spinStatus5 = wx.SpinCtrl(id=wxID_GUI_SCANSETTINGSSPINSTATUS5,
              initial=0, max=99999, min=0, name=u'spinStatus5', parent=self,
              pos=wx.Point(176, 384), size=wx.Size(64, 27),
              style=wx.SP_ARROW_KEYS)
        self.spinStatus5.SetToolTipString(u'X02DA-SCAN-SCN1:NPPDRK')

        self.staticText22 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATICTEXT22,
              label=u'Rotation Start Angle [deg]:', name='staticText22',
              parent=self, pos=wx.Point(320, 296), size=wx.Size(168, 17),
              style=0)
        self.staticText22.SetToolTipString(u'staticText22')

        self.spinStatus6 = wx.SpinCtrl(id=wxID_GUI_SCANSETTINGSSPINSTATUS6,
              initial=0, max=100, min=0, name=u'spinStatus6', parent=self,
              pos=wx.Point(512, 288), size=wx.Size(72, 27),
              style=wx.SP_ARROW_KEYS)
        self.spinStatus6.SetToolTipString(u'X02DA-SCAN-SCN1:ROTSTA')

        self.staticText23 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATICTEXT23,
              label=u'Rotation End Angle [deg]:', name='staticText23',
              parent=self, pos=wx.Point(320, 320), size=wx.Size(163, 17),
              style=0)

        self.spinStatus7 = wx.SpinCtrl(id=wxID_GUI_SCANSETTINGSSPINSTATUS7,
              initial=0, max=100, min=0, name=u'spinStatus7', parent=self,
              pos=wx.Point(512, 312), size=wx.Size(72, 27),
              style=wx.SP_ARROW_KEYS)
        self.spinStatus7.SetToolTipString(u'X02DA-SCAN-SCN1:ROTSTO')

        self.staticText24 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATICTEXT24,
              label=u'Sample In-Beam Pos [um]:', name='staticText24',
              parent=self, pos=wx.Point(320, 344), size=wx.Size(172, 17),
              style=0)

        self.spinStatus8 = wx.SpinCtrl(id=wxID_GUI_SCANSETTINGSSPINSTATUS8,
              initial=0, max=100, min=0, name=u'spinStatus8', parent=self,
              pos=wx.Point(512, 336), size=wx.Size(72, 27),
              style=wx.SP_ARROW_KEYS)
        self.spinStatus8.SetToolTipString(u'X02DA-SCAN-SCN1:SMPIN')

        self.staticText25 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATICTEXT25,
              label=u'Sample Out-Beam Pos [um]:', name='staticText25',
              parent=self, pos=wx.Point(320, 368), size=wx.Size(183, 17),
              style=0)

        self.spinStatus9 = wx.SpinCtrl(id=wxID_GUI_SCANSETTINGSSPINSTATUS9,
              initial=0, max=100, min=0, name=u'spinStatus9', parent=self,
              pos=wx.Point(512, 360), size=wx.Size(72, 27),
              style=wx.SP_ARROW_KEYS)
        self.spinStatus9.SetToolTipString(u'X02DA-SCAN-SCN1:SMPOUT')

        self.staticText26 = wx.StaticText(id=wxID_GUI_SCANSETTINGSSTATICTEXT26,
              label=u'CCD Exposure Time [ms]:', name='staticText26',
              parent=self, pos=wx.Point(320, 392), size=wx.Size(169, 17),
              style=0)
        self.staticText26.SetToolTipString(u'staticText26')

        self.spinStatus10 = wx.SpinCtrl(id=wxID_GUI_SCANSETTINGSSPINSTATUS10,
              initial=0, max=100, min=0, name=u'spinStatus10', parent=self,
              pos=wx.Point(512, 384), size=wx.Size(72, 27),
              style=wx.SP_ARROW_KEYS)
        self.spinStatus10.SetToolTipString(u'X02DA-SCAN-CAM1:EXPTME')

        self.statusCheck1 = wx.CheckBox(id=wxID_GUI_SCANSETTINGSSTATUSCHECK1,
              label=u'Start Experiment', name=u'statusCheck1', parent=self,
              pos=wx.Point(16, 152), size=wx.Size(136, 16), style=0)
        self.statusCheck1.SetValue(False)
        self.statusCheck1.SetToolTipString(u'X02DA-SCAN-SCN1:GO')

        self.statusCheck2 = wx.CheckBox(id=wxID_GUI_SCANSETTINGSSTATUSCHECK2,
              label=u'Pause Experiment', name=u'statusCheck2', parent=self,
              pos=wx.Point(16, 168), size=wx.Size(136, 22), style=0)
        self.statusCheck2.SetValue(False)
        self.statusCheck2.SetToolTipString(u'X02DA-SCAN-SCN1:PAUSE')

    def __init__(self, parent,mainPtr=-1):
        self._init_ctrls(parent)
        self.mainPtr=mainPtr
        # status labels/fields
        stillMore=1
        cDex=1
        self.statusFields=[]
        
        while stillMore:
            try:
                curObj=eval('self.status'+str(cDex));
                curObjVal=curObj.GetLabel();
                curObj.SetToolTipString(curObjVal)
                
            except:
                stillMore=0
            if stillMore:
                self.mainPtr.kRegisterCtrl(curObj)
            cDex+=1

        # status textboxes
        stillMore=1
        cDex=1
        self.statusTexts=[]
        while stillMore:
            try:
                curObj=eval('self.statusText'+str(cDex))
                curObjVal=curObj.GetValue()
                curObj.SetToolTipString(curObjVal)
            except:
                stillMore=0
            if stillMore:
                self.mainPtr.kRegisterCtrl(curObj)
            cDex+=1

        # spin status
        stillMore=1
        cDex=1
        while stillMore:
            try:
                curObj=eval('self.spinStatus'+str(cDex))
            except:
                stillMore=0
            if stillMore:
                self.mainPtr.kRegisterCtrl(curObj)
            cDex+=1
        # check boxes
        stillMore=1
        cDex=1
        while stillMore:
            try:
                curObj=eval('self.statusCheck'+str(cDex))
            except:
                stillMore=0
            if stillMore:
                self.mainPtr.kRegisterCtrl(curObj)
            cDex+=1
        if self.mainPtr==-1:
            print 'Running in demo mode'
        
            


            
                   
    def exportXML(self,doc,xmlNode):
        print 'Nothing'
    def importXML(self,xmlNodes):
        print 'Nothing'




