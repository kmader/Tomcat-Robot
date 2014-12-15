#Boa:Frame:GUI_ESControl

import wx
from X_ROBOT_X02DA_robotCommon import stageJumpPos
# initialize the plugin header dictionary

def create(parent):
    return GUI_ESControl(parent)

def esCreate(parent,mainPtr):
    return GUI_ESControl(parent,mainPtr)
panelInfo={}
panelInfo['End Station Control']=esCreate
[wxID_GUI_ESCONTROL, wxID_GUI_ESCONTROLSTATICBOX1, 
 wxID_GUI_ESCONTROLSTATICBOX2, wxID_GUI_ESCONTROLSTATICBOX3, 
 wxID_GUI_ESCONTROLSTATICBOX4, wxID_GUI_ESCONTROLSTATICBOX5, 
] = [wx.NewId() for _init_ctrls in range(6)]

[wxID_GUI_ESCONTROLTEXT, wxID_GUI_ESCONTROLTEXTSPINSTATUS1, 
 wxID_GUI_ESCONTROLTEXTSPINSTATUS10, wxID_GUI_ESCONTROLTEXTSPINSTATUS2, 
 wxID_GUI_ESCONTROLTEXTSPINSTATUS3, wxID_GUI_ESCONTROLTEXTSPINSTATUS4, 
 wxID_GUI_ESCONTROLTEXTSPINSTATUS5, wxID_GUI_ESCONTROLTEXTSPINSTATUS6, 
 wxID_GUI_ESCONTROLTEXTSPINSTATUS7, wxID_GUI_ESCONTROLTEXTSPINSTATUS8, 
 wxID_GUI_ESCONTROLTEXTSPINSTATUS9, wxID_GUI_ESCONTROLTEXTSTATICBOX1, 
 wxID_GUI_ESCONTROLTEXTSTATICBOX2, wxID_GUI_ESCONTROLTEXTSTATICBOX3, 
 wxID_GUI_ESCONTROLTEXTSTATICBOX4, wxID_GUI_ESCONTROLTEXTSTATICTEXT1, 
 wxID_GUI_ESCONTROLTEXTSTATICTEXT10, wxID_GUI_ESCONTROLTEXTSTATICTEXT11, 
 wxID_GUI_ESCONTROLTEXTSTATICTEXT12, wxID_GUI_ESCONTROLTEXTSTATICTEXT13, 
 wxID_GUI_ESCONTROLTEXTSTATICTEXT14, wxID_GUI_ESCONTROLTEXTSTATICTEXT15, 
 wxID_GUI_ESCONTROLTEXTSTATICTEXT16, wxID_GUI_ESCONTROLTEXTSTATICTEXT17, 
 wxID_GUI_ESCONTROLTEXTSTATICTEXT18, wxID_GUI_ESCONTROLTEXTSTATICTEXT19, 
 wxID_GUI_ESCONTROLTEXTSTATICTEXT2, wxID_GUI_ESCONTROLTEXTSTATICTEXT20, 
 wxID_GUI_ESCONTROLTEXTSTATICTEXT21, wxID_GUI_ESCONTROLTEXTSTATICTEXT22, 
 wxID_GUI_ESCONTROLTEXTSTATICTEXT23, wxID_GUI_ESCONTROLTEXTSTATICTEXT24, 
 wxID_GUI_ESCONTROLTEXTSTATICTEXT25, wxID_GUI_ESCONTROLTEXTSTATICTEXT26, 
 wxID_GUI_ESCONTROLTEXTSTATICTEXT3, wxID_GUI_ESCONTROLTEXTSTATICTEXT4, 
 wxID_GUI_ESCONTROLTEXTSTATICTEXT5, wxID_GUI_ESCONTROLTEXTSTATICTEXT6, 
 wxID_GUI_ESCONTROLTEXTSTATUS1, wxID_GUI_ESCONTROLTEXTSTATUS10, 
 wxID_GUI_ESCONTROLTEXTSTATUS11, wxID_GUI_ESCONTROLTEXTSTATUS12, 
 wxID_GUI_ESCONTROLTEXTSTATUS13, wxID_GUI_ESCONTROLTEXTSTATUS2, 
 wxID_GUI_ESCONTROLTEXTSTATUS3, wxID_GUI_ESCONTROLTEXTSTATUS4, 
 wxID_GUI_ESCONTROLTEXTSTATUS5, wxID_GUI_ESCONTROLTEXTSTATUS6, 
 wxID_GUI_ESCONTROLTEXTSTATUS7, wxID_GUI_ESCONTROLTEXTSTATUS8, 
 wxID_GUI_ESCONTROLTEXTSTATUS9, wxID_GUI_ESCONTROLTEXTSTATUSCHECK1, 
 wxID_GUI_ESCONTROLTEXTSTATUSCHECK2, wxID_GUI_ESCONTROLTEXTSTATUSTEXT1, 
 wxID_GUI_ESCONTROLTEXTSTATUSTEXT2, 
] = [wx.NewId() for _init_ctrls in range(55)]

class GUI_ESControl(wx.Panel):
    version=20090203
    #wx.Panel.__init__(self,parent=prnt)
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Panel.__init__(self,parent=prnt)
        #wx.Frame.__init__(self, id=wxID_GUI_ESCONTROLTEXT,
        #      name=u'GUI_ESControl', parent=prnt, pos=wx.Point(261, 238),
        #      size=wx.Size(608, 469), style=wx.DEFAULT_FRAME_STYLE,
        #      title=u'Frame1')
        #self.SetClientSize(wx.Size(608, 469))

        self.staticBox2 = wx.StaticBox(id=wxID_GUI_ESCONTROLTEXTSTATICBOX2,
              label=u'Sample Holder', name='staticBox2', parent=self,
              pos=wx.Point(0, 0), size=wx.Size(576, 280), style=0)
        self.staticBox2.SetMinSize(wx.Size(-1, -1))

        self.staticBox1 = wx.StaticBox(id=wxID_GUI_ESCONTROLSTATICBOX1,
              label=u'Center Stage', name='staticBox1', parent=self,
              pos=wx.Point(8, 16), size=wx.Size(336, 136), style=0)

        self.staticBox3 = wx.StaticBox(id=wxID_GUI_ESCONTROLSTATICBOX3,
              label=u'Rotation Stage', name='staticBox3', parent=self,
              pos=wx.Point(352, 16), size=wx.Size(200, 136), style=0)

        self.staticBox4 = wx.StaticBox(id=wxID_GUI_ESCONTROLSTATICBOX4,
              label=u'Sample Stage', name='staticBox4', parent=self,
              pos=wx.Point(8, 152), size=wx.Size(544, 120), style=0)

        self.staticBox5 = wx.StaticBox(id=wxID_GUI_ESCONTROLSTATICBOX5,
              label=u'Base Stage', name='staticBox5', parent=self,
              pos=wx.Point(0, 280), size=wx.Size(576, 136), style=0)

    def __init__(self, parent,mainPtr=-1):
        self._init_ctrls(parent)
        self.mainPtr=mainPtr
        #print dir(dir(self))
        # status labels/fields
        stillMore=1
        cDex=1
        

        self.sjp2=stageJumpPos(self,rPos=wx.Point(8+8,16+16),label='XX')
        self.sjp2.SetToolTipString(u'X02DA-ES1-SMP1:TRXX')
        self.mainPtr.kRegisterCtrl(self.sjp2)
        self.sjp3=stageJumpPos(self,rPos=wx.Point(16+170,32),label='ZZ')
        self.sjp3.SetToolTipString(u'X02DA-ES1-SMP1:TRZZ')
        self.mainPtr.kRegisterCtrl(self.sjp3)
        self.sjp1=stageJumpPos(self,rPos=wx.Point(352+8,32),label='Rot Y [deg]')
        self.sjp1.SetToolTipString(u'X02DA-ES1-SMP1:ROTYUSETP')
        #self.sjp1.SetToolTipString(u'X02DA-ES1-ROBO:CM-ITER')
        self.mainPtr.kRegisterCtrl(self.sjp1)
        
        self.sjpX=stageJumpPos(self,rPos=wx.Point(8+8,152+16),label='X [um]')
        self.sjpX.SetToolTipString(u'X02DA-ES1-SMP1:TRX')
        self.mainPtr.kRegisterCtrl(self.sjpX)
        
        self.sjpY=stageJumpPos(self,rPos=wx.Point(170+16,152+16),label='Y [um]')
        self.sjpY.SetToolTipString(u'X02DA-ES1-SMP1:TRY')
        self.mainPtr.kRegisterCtrl(self.sjpY)
        
        self.sjpZ=stageJumpPos(self,rPos=wx.Point(2*170+16,152+16),label='Z [um]')
        self.sjpZ.SetToolTipString(u'X02DA-ES1-SMP1:TRZ')
        self.mainPtr.kRegisterCtrl(self.sjpZ)
        
        self.sjpmX=stageJumpPos(self,rPos=wx.Point(8+8,280+16),label='X [um]')
        self.sjpmX.SetToolTipString(u'X02DA-ES1-MS1:TRX')
        self.mainPtr.kRegisterCtrl(self.sjpmX)
        
        self.sjpmY=stageJumpPos(self,rPos=wx.Point(170+16,280+16),label='Y [um]')
        self.sjpmY.SetToolTipString(u'X02DA-ES1-MS1:TRY')
        self.mainPtr.kRegisterCtrl(self.sjpmY)
        
        self.sjpmZ=stageJumpPos(self,rPos=wx.Point(2*170+16,280+16),label='Z [um]')
        self.sjpmZ.SetToolTipString(u'X02DA-ES1-MS1:TRZ')
        self.mainPtr.kRegisterCtrl(self.sjpmZ)
        
        while stillMore:
            try:
                curObj=eval('self.status'+str(cDex));
                curObjVal=curObj.GetLabel();
                curObj.SetToolTipString(curObjVal)
                print 'self.status'+str(cDex)
                
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






