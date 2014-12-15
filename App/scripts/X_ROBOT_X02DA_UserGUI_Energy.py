#Boa:Frame:GUI_Energy

import wx


def create(parent,mainPtr):
    return GUI_Energy(parent,mainPtr)
panelInfo={}
panelInfo['X-Ray Energy']=create

[wxID_GUI_ENERGY, wxID_GUI_ENERGYPROCBUTTON1, wxID_GUI_ENERGYPROCBUTTON2, 
 wxID_GUI_ENERGYPROCBUTTON3, wxID_GUI_ENERGYPROCBUTTON4, 
 wxID_GUI_ENERGYSTATICBOX1, wxID_GUI_ENERGYSTATICBOX2, 
 wxID_GUI_ENERGYSTATICBOX3, wxID_GUI_ENERGYSTATICBOX4, 
 wxID_GUI_ENERGYSTATICBOX5, wxID_GUI_ENERGYSTATICTEXT1, 
 wxID_GUI_ENERGYSTATICTEXT2, wxID_GUI_ENERGYSTATICTEXT3, 
 wxID_GUI_ENERGYSTATICTEXT5, wxID_GUI_ENERGYSTATICTEXT6, 
 wxID_GUI_ENERGYSTATICTEXT7, wxID_GUI_ENERGYSTATUS1, wxID_GUI_ENERGYSTATUS2, 
 wxID_GUI_ENERGYSTATUS3, wxID_GUI_ENERGYSTATUS4, wxID_GUI_ENERGYSTATUS5, 
 wxID_GUI_ENERGYSTATUS6, wxID_GUI_ENERGYSTATUS7, wxID_GUI_ENERGYSTATUS8, 
 wxID_GUI_ENERGYSTATUS9, wxID_GUI_ENERGYSTATUSTEXT1, 
 wxID_GUI_ENERGYSTATUSTEXT2, 
] = [wx.NewId() for _init_ctrls in range(27)]

class GUI_Energy(wx.Frame):
    version=20090203
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_GUI_ENERGY, name=u'GUI_Energy',
              parent=prnt, pos=wx.Point(418, 251), size=wx.Size(853, 616),
              style=wx.DEFAULT_FRAME_STYLE, title=u'Energy')
        self.SetClientSize(wx.Size(853, 616))

        self.staticText1 = wx.StaticText(id=wxID_GUI_ENERGYSTATICTEXT1,
              label=u'Desired Energy [keV]:', name='staticText1', parent=self,
              pos=wx.Point(16, 24), size=wx.Size(141, 17), style=0)

        self.staticText2 = wx.StaticText(id=wxID_GUI_ENERGYSTATICTEXT2,
              label=u'Actual Energy [keV]:', name='staticText2', parent=self,
              pos=wx.Point(16, 48), size=wx.Size(132, 17), style=0)

        self.staticText3 = wx.StaticText(id=wxID_GUI_ENERGYSTATICTEXT3,
              label=u'Ion Chamber Signal [V]:', name='staticText3', parent=self,
              pos=wx.Point(16, 72), size=wx.Size(154, 17), style=0)

        self.status1 = wx.StaticText(id=wxID_GUI_ENERGYSTATUS1,
              label='staticText4', name=u'status1', parent=self,
              pos=wx.Point(192, 48), size=wx.Size(69, 17), style=0)
        self.status1.SetToolTipString(u'#X02DA-OP-ENE:ACTUAL')

        self.status2 = wx.StaticText(id=wxID_GUI_ENERGYSTATUS2,
              label=u'staticText4', name=u'status2', parent=self,
              pos=wx.Point(192, 72), size=wx.Size(69, 17), style=0)
        self.status2.SetToolTipString(u'X02DA-ES1-IC1:VAL')

        self.statusText1 = wx.TextCtrl(id=wxID_GUI_ENERGYSTATUSTEXT1,
              name=u'statusText1', parent=self, pos=wx.Point(192, 16),
              size=wx.Size(80, 27), style=0, value='textCtrl1')
        self.statusText1.SetToolTipString(u'X02DA-OP-ENE:UI')

        self.staticBox1 = wx.StaticBox(id=wxID_GUI_ENERGYSTATICBOX1,
              label=u'Energy Control', name='staticBox1', parent=self,
              pos=wx.Point(8, 0), size=wx.Size(424, 100), style=0)

        self.staticBox2 = wx.StaticBox(id=wxID_GUI_ENERGYSTATICBOX2,
              label=u'Axis Control', name='staticBox2', parent=self,
              pos=wx.Point(8, 96), size=wx.Size(424, 136), style=0)

        self.staticBox3 = wx.StaticBox(id=wxID_GUI_ENERGYSTATICBOX3,
              label=u'Cr1 Pitch [urad]', name='staticBox3', parent=self,
              pos=wx.Point(96, 120), size=wx.Size(112, 72), style=0)
        self.staticBox3.SetMinSize(wx.Size(-1, -1))

        self.staticBox4 = wx.StaticBox(id=wxID_GUI_ENERGYSTATICBOX4,
              label=u'Cr2 Pitch [urad]', name='staticBox4', parent=self,
              pos=wx.Point(208, 120), size=wx.Size(112, 108), style=0)
        self.staticBox4.SetMinSize(wx.Size(-1, -1))

        self.staticBox5 = wx.StaticBox(id=wxID_GUI_ENERGYSTATICBOX5,
              label=u'Cr2 Z [mm]', name='staticBox5', parent=self,
              pos=wx.Point(320, 120), size=wx.Size(104, 72), style=0)
        self.staticBox5.SetMinSize(wx.Size(-1, -1))

        self.staticText5 = wx.StaticText(id=wxID_GUI_ENERGYSTATICTEXT5,
              label=u'Desired Pos', name='staticText5', parent=self,
              pos=wx.Point(16, 144), size=wx.Size(75, 17), style=0)

        self.staticText6 = wx.StaticText(id=wxID_GUI_ENERGYSTATICTEXT6,
              label=u'Actual Pos', name='staticText6', parent=self,
              pos=wx.Point(16, 168), size=wx.Size(66, 17), style=0)

        self.staticText7 = wx.StaticText(id=wxID_GUI_ENERGYSTATICTEXT7,
              label=u'Tweak Pos', name='staticText7', parent=self,
              pos=wx.Point(16, 208), size=wx.Size(66, 17), style=0)

        self.status3 = wx.StaticText(id=wxID_GUI_ENERGYSTATUS3,
              label='staticText8', name=u'status3', parent=self,
              pos=wx.Point(104, 144), size=wx.Size(69, 17), style=0)
        self.status3.SetToolTipString(u'#X02DA-OP-ENE:MAIN_SEQ1.DO1')

        self.status4 = wx.StaticText(id=wxID_GUI_ENERGYSTATUS4,
              label='staticText8', name=u'status4', parent=self,
              pos=wx.Point(104, 168), size=wx.Size(69, 17), style=0)
        self.status4.SetToolTipString(u'#X02DA-OP-MO1:C1THE.RBV')

        self.status5 = wx.StaticText(id=wxID_GUI_ENERGYSTATUS5,
              label='staticText8', name=u'status5', parent=self,
              pos=wx.Point(224, 144), size=wx.Size(69, 17), style=0)
        self.status5.SetToolTipString(u'#X02DA-OP-ENE:MAIN_SEQ1.DO2')

        self.status6 = wx.StaticText(id=wxID_GUI_ENERGYSTATUS6,
              label=u'staticText8', name=u'status6', parent=self,
              pos=wx.Point(224, 168), size=wx.Size(69, 17), style=0)
        self.status6.SetToolTipString(u'#X02DA-OP-MO1:C2THE.RBV')

        self.status7 = wx.StaticText(id=wxID_GUI_ENERGYSTATUS7,
              label='staticText4', name=u'status7', parent=self,
              pos=wx.Point(336, 144), size=wx.Size(69, 17), style=0)
        self.status7.SetToolTipString(u'#X02DA-OP-ENE:MAIN_SEQ1.DO3')

        self.status8 = wx.StaticText(id=wxID_GUI_ENERGYSTATUS8,
              label='staticText4', name=u'status8', parent=self,
              pos=wx.Point(336, 168), size=wx.Size(69, 17), style=0)
        self.status8.SetToolTipString(u'X02DA-OP-MO1:C2Z.RBV')

        self.procButton1 = wx.Button(id=wxID_GUI_ENERGYPROCBUTTON1, label=u'-',
              name=u'procButton1', parent=self, pos=wx.Point(216, 200),
              size=wx.Size(24, 24), style=0)
        self.procButton1.SetToolTipString(u'X02DA-OP-ENE:C2THE_TWR')

        self.procButton2 = wx.Button(id=wxID_GUI_ENERGYPROCBUTTON2, label=u'+',
              name=u'procButton2', parent=self, pos=wx.Point(288, 200),
              size=wx.Size(24, 24), style=0)
        self.procButton2.SetToolTipString(u'X02DA-OP-ENE:C2THE_TWF')

        self.statusText2 = wx.TextCtrl(id=wxID_GUI_ENERGYSTATUSTEXT2,
              name=u'statusText2', parent=self, pos=wx.Point(240, 200),
              size=wx.Size(48, 27), style=0, value='textCtrl1')
        self.statusText2.SetToolTipString(u'X02DA-OP-ENE:C2THE_TWV')

        self.procButton3 = wx.Button(id=wxID_GUI_ENERGYPROCBUTTON3,
              label=u'Start', name=u'procButton3', parent=self,
              pos=wx.Point(304, 16), size=wx.Size(120, 32), style=0)
        self.procButton3.SetToolTipString(u'X02DA-OP-ENE:STA_MOVE')

        self.procButton4 = wx.Button(id=wxID_GUI_ENERGYPROCBUTTON4,
              label=u'Abort', name=u'procButton4', parent=self,
              pos=wx.Point(304, 64), size=wx.Size(120, 32), style=0)
        self.procButton4.SetToolTipString(u'X02DA-OP-ENE:ABO_MOVE')

        self.status9 = wx.StaticText(id=wxID_GUI_ENERGYSTATUS9,
              label=u'staticText4', name=u'status9', parent=self,
              pos=wx.Point(304, 48), size=wx.Size(120, 17), style=0)
        self.status9.SetBackgroundColour(wx.Colour(0, 233, 28))
        self.status9.SetToolTipString(u'$X02DA-OP-ENE:MOV_DONE')

    def __init__(self, parent,mainPtr):
        self._init_ctrls(parent)
        self.mainPtr=mainPtr
        
        
        # status labels/fields
        
        objHeader=['status','statusText','procButton']
        for objType in objHeader:
            stillMore=1
            cDex=1 
            while stillMore:
                try:
                    curObj=eval('self.'+objType+str(cDex));
                except:
                    stillMore=0
                if stillMore:
                    self.mainPtr.kRegisterCtrl(curObj)
                cDex+=1
        
    def exportXML(self,doc,userEle):
        print 'empty'
    def importXML(self,xmlNodes):
        print 'empty'    
