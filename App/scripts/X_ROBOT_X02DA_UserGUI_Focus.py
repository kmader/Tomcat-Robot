#Boa:Frame:GUI_Focus

import wx
from X_ROBOT_X02DA_robotCommon import stageJumpPos
def create(parent,mainPtr):
    return GUI_Focus(parent,mainPtr)
panelInfo={}
#panelInfo['Microscope Controls']=create
[wxID_GUI_FOCUS, wxID_GUI_FOCUSPROCBUTTON1, wxID_GUI_FOCUSSTATICBOX1, 
 wxID_GUI_FOCUSSTATICBOX2, wxID_GUI_FOCUSSTATICBOX3, wxID_GUI_FOCUSSTATICBOX4, 
 wxID_GUI_FOCUSSTATICLINE1, wxID_GUI_FOCUSSTATICTEXT1, 
 wxID_GUI_FOCUSSTATICTEXT2, wxID_GUI_FOCUSSTATICTEXT3, 
 wxID_GUI_FOCUSSTATICTEXT4, wxID_GUI_FOCUSSTATUS1, wxID_GUI_FOCUSSTATUS2, 
 wxID_GUI_FOCUSSTATUS3, wxID_GUI_FOCUSSTATUS4, 
] = [wx.NewId() for _init_ctrls in range(15)]

class GUI_Focus(wx.Frame):
    version=20090203
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_GUI_FOCUS, name=u'GUI_Focus',
              parent=prnt, pos=wx.Point(358, 317), size=wx.Size(853, 616),
              style=wx.DEFAULT_FRAME_STYLE, title='Frame1')
        self.SetClientSize(wx.Size(853, 616))

        self.staticBox1 = wx.StaticBox(id=wxID_GUI_FOCUSSTATICBOX1,
              label=u'Lens Selection', name='staticBox1', parent=self,
              pos=wx.Point(8, 8), size=wx.Size(200, 120), style=0)

        self.staticText1 = wx.StaticText(id=wxID_GUI_FOCUSSTATICTEXT1,
              label=u'Magnification:', name='staticText1', parent=self,
              pos=wx.Point(48, 24), size=wx.Size(90, 17), style=0)

        self.staticText2 = wx.StaticText(id=wxID_GUI_FOCUSSTATICTEXT2,
              label=u'Lens 1:', name='staticText2', parent=self,
              pos=wx.Point(16, 40), size=wx.Size(48, 17), style=0)

        self.status1 = wx.StaticText(id=wxID_GUI_FOCUSSTATUS1,
              label='staticText3', name=u'status1', parent=self,
              pos=wx.Point(120, 40), size=wx.Size(69, 17), style=0)
        self.status1.SetToolTipString(u'X02DA-ES1-MS1:LNSSEL.ONST')

        self.staticText3 = wx.StaticText(id=wxID_GUI_FOCUSSTATICTEXT3,
              label=u'Lens 2:', name='staticText3', parent=self,
              pos=wx.Point(16, 56), size=wx.Size(48, 17), style=0)

        self.status2 = wx.StaticText(id=wxID_GUI_FOCUSSTATUS2,
              label=u'staticText4', name=u'status2', parent=self,
              pos=wx.Point(120, 56), size=wx.Size(69, 17), style=0)
        self.status2.SetToolTipString(u'X02DA-ES1-MS1:LNSSEL.TWST')

        self.staticText4 = wx.StaticText(id=wxID_GUI_FOCUSSTATICTEXT4,
              label=u'Lens 3:', name='staticText4', parent=self,
              pos=wx.Point(16, 72), size=wx.Size(48, 17), style=0)

        self.status3 = wx.StaticText(id=wxID_GUI_FOCUSSTATUS3,
              label='staticText5', name=u'status3', parent=self,
              pos=wx.Point(120, 72), size=wx.Size(69, 17), style=0)
        self.status3.SetToolTipString(u'X02DA-ES1-MS1:LNSSEL.THST')

        self.procButton1 = wx.Button(id=wxID_GUI_FOCUSPROCBUTTON1,
              label=u'Next', name=u'procButton1', parent=self, pos=wx.Point(16,
              96), size=wx.Size(64, 24), style=0)
        self.procButton1.SetToolTipString(u'X02DA-ES1-MS1:LNS+')

        self.status4 = wx.StaticText(id=wxID_GUI_FOCUSSTATUS4,
              label='staticText5', name=u'status4', parent=self,
              pos=wx.Point(120, 96), size=wx.Size(69, 17), style=0)
        self.status4.SetToolTipString(u'X02DA-ES1-MS1:LNSSEL')

        self.staticBox2 = wx.StaticBox(id=wxID_GUI_FOCUSSTATICBOX2,
              label=u'Slits', name='staticBox2', parent=self, pos=wx.Point(8,
              128), size=wx.Size(424, 232), style=0)

        self.staticBox3 = wx.StaticBox(id=wxID_GUI_FOCUSSTATICBOX3,
              label=u'Vertical', name='staticBox3', parent=self,
              pos=wx.Point(16, 144), size=wx.Size(200, 216), style=0)

        self.staticBox4 = wx.StaticBox(id=wxID_GUI_FOCUSSTATICBOX4,
              label=u'Horizontal', name='staticBox4', parent=self,
              pos=wx.Point(216, 144), size=wx.Size(200, 216), style=0)

        self.staticLine1 = wx.StaticLine(id=wxID_GUI_FOCUSSTATICLINE1,
              name='staticLine1', parent=self, pos=wx.Point(16, 88),
              size=wx.Size(184, 8), style=0)

    def __init__(self, parent,mainPtr):
        self._init_ctrls(parent)
        self.mainPtr=mainPtr
        
        
         # status labels/fields
        self.sjp=stageJumpPos(self,rPos=wx.Point(200+8,8),label='Focus Axis [ustep]',jumpSize=0.0001)
        self.sjp.SetToolTipString(u'X02DA-ES1-MS1:FOC_MovAbs')
        self.mainPtr.kRegisterCtrl(self.sjp)
        
        self.hSlitCent=stageJumpPos(self,rPos=wx.Point(216+8,144+16),label='Center [mm]',jumpSize=0.001)
        self.hSlitCent.SetToolTipString(u'X02DA-ES1-SHt2.D')
        self.mainPtr.kRegisterCtrl(self.hSlitCent)
        
        self.hSlitSize=stageJumpPos(self,rPos=wx.Point(216+8,88+144+16),label='Size [mm]',jumpSize=0.001)
        self.hSlitSize.SetToolTipString(u'X02DA-ES1-SHsize')
        self.mainPtr.kRegisterCtrl(self.hSlitSize)
        
        self.vSlitCent=stageJumpPos(self,rPos=wx.Point(16+8,144+16),label='Center [mm]',jumpSize=0.001)
        self.vSlitCent.SetToolTipString(u'X02DA-ES1-SVt2.D')
        self.mainPtr.kRegisterCtrl(self.vSlitCent)
        
        self.vSlitSize=stageJumpPos(self,rPos=wx.Point(16+8,88+144+16),label='Size [mm]',jumpSize=0.001)
        self.vSlitSize.SetToolTipString(u'X02DA-ES1-SVsize')
        self.mainPtr.kRegisterCtrl(self.vSlitSize)
        
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
