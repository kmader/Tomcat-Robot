# Varia 
# Extra panels and such for the main interface that are smaller

import wx
import wx.stc
import cStringIO
import urllib2
def uiCreate(parent,mainPtr):
    return GUI_UserInformation(parent,mainPtr)
def scriptCreate(parent,mainPtr):
    return GUI_Script(parent,mainPtr)
def ssCreate(parent,mainPtr):
    return GUI_ScanSettings(parent,mainPtr)
def bcCreate(parent,mainPtr):
    return GUI_BeamlineContact(parent,mainPtr)
def xmlOneStep(aNodes,nodeName):
    # generic function to grab subnodes and avoid overly nested code
    outNode=[]
    for aNode in aNodes:
        for bNode in aNode.childNodes:
            if bNode.nodeName.upper()==nodeName.upper():
                outNode.append(bNode)
    return outNode
def ReadScriptFromXML(xmlNodes):
    sNodes=xmlOneStep(xmlNodes,'scriptline')
    tempText=''
    if len(sNodes)>0:
        for sNode in sNodes:       
            tempText+=sNode.firstChild.nodeValue.strip()+'\n'
    return tempText
panelInfo={}
#panelInfo['User Information']=uiCreate
panelInfo['Script Editor']=scriptCreate
#panelInfo['Beamline Contact']=bcCreate
[wxID_GUI_ROBOTTXTUSERCONTACT, 
 wxID_GUI_ROBOTTXTUSERNAME, wxID_GUI_ROBOTSTATICTEXT4, 
 wxID_GUI_ROBOTSTATICTEXT5,wxID_GUI_ROBOTSTATICBOX1]= [wx.NewId() for altID in range(5)]
class GUI_UserInformation(wx.Panel):
    version=20090302
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        # return to frame to edit
        wx.Panel.__init__(self,prnt)
        self.staticBox1 = wx.StaticBox(id=wxID_GUI_ROBOTSTATICBOX1,
              label=u'User Information', name='staticBox1', parent=self,
              pos=wx.Point(552-552, 8), size=wx.Size(200, 112), style=0)

        self.staticText4 = wx.StaticText(id=wxID_GUI_ROBOTSTATICTEXT4,
              label=u'Name', name='staticText4', parent=self, pos=wx.Point(560-552,
              32), size=wx.Size(39, 17), style=0)

        self.staticText5 = wx.StaticText(id=wxID_GUI_ROBOTSTATICTEXT5,
              label=u'Contact Info', name='staticText5', parent=self,
              pos=wx.Point(560-552, 56), size=wx.Size(79, 17), style=0)

        self.txtUserName = wx.TextCtrl(id=wxID_GUI_ROBOTTXTUSERNAME,
              name=u'txtUserName', parent=self, pos=wx.Point(608-552, 24),
              size=wx.Size(128, 27), style=0, value=u'')
        #self.txtUserName.Bind(wx.EVT_TEXT, self.OnTxtUserNameText,
         #     id=wxID_GUI_ROBOTTXTUSERNAME)

        self.txtUserContact = wx.TextCtrl(id=wxID_GUI_ROBOTTXTUSERCONTACT,
              name=u'txtUserContact', parent=self, pos=wx.Point(640-552, 48),
              size=wx.Size(96, 27), style=0, value=u'')
        #self.txtUserContact.Bind(wx.EVT_TEXT, self.OnTxtUserNameText)
    
    def __init__(self, parent,mainPtr):
        self._init_ctrls(parent)
        
    def exportXML(self,doc,userEle):
        uField = doc.createElement('UserName')
        userEle.appendChild(uField)
        ptext = doc.createTextNode(self.txtUserName.GetValue())
        uField.appendChild(ptext)
        uField = doc.createElement('UserContact')
        userEle.appendChild(uField)
        ptext = doc.createTextNode(self.txtUserContact.GetValue())
        uField.appendChild(ptext)
    def importXML(self,xmlNodes):
        unNodes=xmlOneStep(xmlNodes,'username')
        ucNodes=xmlOneStep(xmlNodes,'usercontact')
        if len(unNodes)>0:
            self.txtUserName.SetValue(unNodes[0].firstChild.nodeValue.strip())
        if len(ucNodes)>0:
            self.txtUserContact.SetValue(ucNodes[0].firstChild.nodeValue.strip())               
class GUI_ScanSettings(wx.Panel):
    version=20090121
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        # return to frame to edit
        wx.Panel.__init__(self,prnt)
        self.staticBox1 = wx.StaticBox(label=u'Scan Settings', name='staticBox1', parent=self,
              pos=wx.Point(552-552, 8), size=wx.Size(200, 112), style=0)

        self.staticText4 = wx.StaticText(label=u'Projections', name='staticText4', parent=self, pos=wx.Point(560-552,
              32), size=wx.Size(39, 17), style=0)

        self.staticText5 = wx.StaticText(label=u'Exposure Time', name='staticText5', parent=self,
              pos=wx.Point(560-552, 56), size=wx.Size(79, 17), style=0)

        self.txtNumProjections = wx.TextCtrl(name=u'txtNumProjections', parent=self, pos=wx.Point(608-552, 24),
              size=wx.Size(128, 27), style=0, value=u'')


        self.txtExposureTime = wx.TextCtrl(name=u'txtExposureTime', parent=self, pos=wx.Point(640-552, 48),
              size=wx.Size(96, 27), style=0, value=u'')
        
    
    def __init__(self, parent,mainPtr):
        self._init_ctrls(parent)
        self.mainPtr=mainPtr
        self.mainPtr.kRegisterTimerEvent(self.timerEvent)
    def timerEvent(self,event):
        [robotPtr,robotScriptPtr,futureBnd]=event.argBundle
        robotScriptPtr.chUserContact.putVal(self.txtUserContact.GetValue())
            
    def exportXML(self,doc,userEle):
        uField = doc.createElement('NumberOfProjections')
        userEle.appendChild(uField)
        ptext = doc.createTextNode(self.txtNumProjections.GetValue())
        uField.appendChild(ptext)
        uField = doc.createElement('ExposureTime')
        userEle.appendChild(uField)
        ptext = doc.createTextNode(self.txtExposureTime.GetValue())
        uField.appendChild(ptext)
    def importXML(self,xmlNodes):
        unNodes=xmlOneStep(xmlNodes,'NumberOfProjections')
        ucNodes=xmlOneStep(xmlNodes,'ExposureTime')
        if len(unNodes)>0:
            self.txtNumProjections.SetValue(unNodes[0].firstChild.nodeValue.strip())
        if len(ucNodes)>0:
            self.txtExposureTime.SetValue(ucNodes[0].firstChild.nodeValue.strip()) 
class GUI_BeamlineContact(wx.Panel):
    version=20090219
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Panel.__init__(self,prnt)
        self.SetClientSize(wx.Size(853, 616))

        self.listCtrl1 = wx.ListCtrl(name='listCtrl1',
              parent=self, pos=wx.Point(8, 8), size=wx.Size(600, 600),
              style=wx.LC_ICON)
    def __init__(self, parent,mainPtr):
        self._init_ctrls(parent)
        self.mainPtr=mainPtr
        self.mainPtr.kRegisterEvent('bcInit',self.initEvent)
        self.mainPtr.kPostEvent('bcInit',[])
    def initEvent(self,event):
        baseUrl='http://sls.web.psi.ch/view.php/beamlines/tomcat/staff/'
        picList=[]
        picList.append('tn_stampanoni-marco_jpg.jpg')
        picList.append('tn_federica.png')
        picList.append('tn_christoph_hintermueller.jpg')
        picList.append('tn_Sam.jpg')
        picList.append('tn_rajmund_mokso.jpg')
        picList.append('tn_kevin_mader.jpg')
        picList.append('http://www.psi.ch/allgemeine_bilder/psi_logo.jpg')
        imgList = wx.ImageList(88,116, True)         
        for nPic in picList:
            if nPic.find(':')>=0:
                cUrl=nPic
            else:
                cUrl=baseUrl+nPic
            response = urllib2.urlopen(cUrl)
            data = response.read()
            stream = cStringIO.StringIO(data)        
            # convert to a bitmap        
            cImg = wx.ImageFromStream( stream )
            cImg.Rescale(88,116)
            print (cImg.GetHeight(),cImg.GetWidth())
            imgMax = imgList.Add(wx.BitmapFromImage(cImg))
        self.listCtrl1.AssignImageList(imgList, wx.IMAGE_LIST_NORMAL) 
        #self.listCtrl1.InsertColumn(0,'Name')
        #self.listCtrl1.InsertColumn(0,'Role')
        #self.listCtrl1.InsertColumn(0,'Number')
        self.addContact('PSI EMERGENCY','','X3333',6)
        self.addContact('Marco Stampanoni','Head of Tomcat','X4724',0,'+41 (0)76 4330574')
        self.addContact('Federica Marone','BL Scientist','X5318',1,'+41 (0)76 5024886')
        self.addContact('Chris Hintermueller','PostDoc','X5819',2,'+41 (0)78 7299960')
        self.addContact('Sam McDonald','PostDoc','X5840',3,'+41 (0)76 2387027')
        self.addContact('Rajmund Mosko','PostDoc','X5628',4)
        self.addContact('Kevin Mader','Robot','X5853',5,'+41 (0)78 7551438')
        #self.addContact('Kevin Mader','Robot','X5853',5)
        
        
    def addContact(self,name,role,phone,pic,cell=''):
        self.listCtrl1.InsertStringItem(1,name+'\r'+role+'\r'+phone+'\r'+cell,pic)
    def exportXML(self,doc,userEle):
        print 'empty'
    def importXML(self,xmlNodes):
        print 'empty'       
class GUI_Script(wx.Panel):
    version=20090213
    def _init_ctrls(self, prnt):
        
        # generated method, don't edit
        # return to frame to edit
        wx.Panel.__init__(self,prnt)
        #wx.Frame.__init__(self, name=u'Script Editor', parent=prnt),
              #pos=wx.Point(266, 275), size=wx.Size(606, 543),
              #style=wx.DEFAULT_FRAME_STYLE, title=u'X02DA User GUI')
        
        
        self.butWait = wx.Button(
              label=u'WAIT', name=u'butWait', parent=self,
              pos=wx.Point(100, 0), size=wx.Size(100, 32), style=0)
        self.butWait.Bind(wx.EVT_BUTTON, self.OnButWait)
        self.butRepeat = wx.Button(
              label=u'REPEAT', name=u'butRepeat', parent=self,
              pos=wx.Point(200, 0), size=wx.Size(100, 32), style=0)
        self.butRepeat.Bind(wx.EVT_BUTTON, self.OnButRepeat)
        self.butRegen = wx.Button(
              label=u'RECREATE', name=u'butRegen', parent=self,
              pos=wx.Point(300, 0), size=wx.Size(100, 32), style=0)
        self.butRegen.Bind(wx.EVT_BUTTON, self.OnButRegen)
        self.butRegen.SetToolTipString(u'This regenerates the simplist script that acquires each sample and position once. It will erase any changes you have made')
        
        self.butValidate = wx.Button(
              label=u'Validate', name=u'butValidate', parent=self,
              pos=wx.Point(450, 0), size=wx.Size(100, 32), style=0)
        self.butValidate.Bind(wx.EVT_BUTTON, self.OnButValidate)
        
        self.txtScript = wx.stc.StyledTextCtrl(
              name=u'txtScript', parent=self, pos=wx.Point(5, 40),
              size=wx.Size(685, 430), style=0)
        
        self.txtScript.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
        self.txtScript.SetMarginWidth(1, 25)
        self.txtScript.AutoCompSetIgnoreCase(True)
        self.txtScript.Bind(wx.EVT_KEY_UP, self.OnTestAutoComp)
        
        
    def ubrigInit(self,event):
        myRobot=event.myRobot
        myRobotScript=event.myRobotScript
        self.chSample = wx.Choice(choices=myRobotScript.ScriptDict.keys(),
              name=u'chSample', parent=self, pos=wx.Point(0, 0),
              size=wx.Size(100, 32), style=0)
        self.chSample.Bind(wx.EVT_CHOICE, self.OnChSampleChoice)
        
        myRobotScript.initializeValidCommands()
    
       
    
    def pushScript(self,event):
        event.myRobotScript.loadText(sequenceText=self.txtScript.GetText())
    def pullScript(self,event):
        myRobotScript=event.myRobotScript
        self.txtScript.SetText(myRobotScript.sequenceText)
        vCmds=[]
        for cmd in myRobotScript.ValidCommands.keys():
            if cmd=='IMSAMPLE':
                for cKey in myRobotScript.ScriptDict.keys():
                    vCmds.append(cmd+'("'+cKey+'")')
            else:
                vCmds.append(cmd+'('+','*(myRobotScript.ValidCommands[cmd][1]-1)+')')
        vCmds.sort()
        nCmds=''
        for cmd in vCmds:
            nCmds+=' '+cmd
        self.AutoCompCmd=nCmds
    def refreshSamples(self,event):
        self.chSample.Clear()
        self.chSample.AppendItems(event.myRobotScript.ScriptDict.keys())
        #print 'Samples Refreshed'
    def __init__(self, parent,mainPtr):
        self.mainPtr=mainPtr
        self._init_ctrls(parent)
        self.mainPtr.kRegisterEvent('gsInit',self.ubrigInit)
        self.mainPtr.kRegisterEvent('gsPullScript',self.pullScript)
        self.mainPtr.kRegisterEvent('gsPushScript',self.pushScript)
        self.mainPtr.kRegisterPanelEvent(self.pullScript)
        self.mainPtr.kRegisterEvent('gsValidateScript',self.OnButValidateEvent)
        self.mainPtr.kPostEvent('gsInit',[parent])
        self.mainPtr.kRegisterEvent('refreshSampleList',self.refreshSamples)
    def exportXML(self,doc,scriptEle):
        tBox=self.txtScript.GetText().split('\n')
        for ijk in range(0,len(tBox)):
            dLineE = doc.createElement("scriptLine")
            dLineT=doc.createTextNode(tBox[ijk])
            dLineE.appendChild(dLineT)
            scriptEle.appendChild(dLineE)
    def importXML(self,xmlNodes):
        tempText=ReadScriptFromXML(xmlNodes)
        self.txtScript.SetText(tempText)
        self.mainPtr.kPostEvent('gsPushScript',[])
# Edit Script Dialog Callbacks
    def OnButRegen(self, event):
        self.mainPtr.kPostEvent('generateScript',[1])
        event.Skip()

    def OnTestAutoComp(self,event):
        if event.GetKeyCode()!=27:
            if not self.txtScript.AutoCompActive(): self.txtScript.AutoCompShow(1,self.AutoCompCmd) 
        else:
            self.txtScript.AutoCompCancel()
        
    def OnButWait(self,event):
        self.txtScript.SetText(self.txtScript.GetText()+'\nWAIT(10) #wait 10 seconds')
    def OnButRepeat(self,event):
        #print event
        #print dir(event)
        self.txtScript.SetText(self.txtScript.GetText()+'\nREPEAT(5,4) #repeat from line 5, 4 more times')
    def OnButValidate(self,event):
        self.mainPtr.kPostEvent('gsValidateScript',[])
    def OnButValidateEvent(self,event):
        myRbS=event.myRobotScript
        failSafeScript=myRbS.sequenceText
        myRbS.loadText(sequenceText=self.txtScript.GetText())
        if (myRbS.validateSequence(wx.MessageBox)>0):
            self.butValidate.SetForegroundColour('red')
            myRbS.loadText(sequenceText=failSafeScript) # reload the original
        else:
            self.butValidate.SetForegroundColour('green')
        
    def OnChSampleChoice(self, event):
        #print event.String
        sName=self.chSample.StringSelection
        cmdStr='IMSAMPLE("'+sName+'")'
        self.txtScript.SetText(self.txtScript.GetText()+'\n'+cmdStr)#+'# tray pos '+tArray[self.scriptDict[sName][0]]+self.scriptDict[sName][1].__str__())
        event.Skip()
    def OnScriptEnd(self,event):
        globals()['myRobotScript'].loadText(self.txtScript.GetText(),self.scriptDict)
        vErrors=globals()['myRobotScript'].validateSequence(wx.MessageBox)
        while (vErrors>0):      
            wx.MessageBox(vErrors.__str__()+' fatal errors found')
            self.ShowModal()
            globals()['myRobotScript'].loadText(self.txtScript.GetText(),self.scriptDict)
            vErrors=globals()['myRobotScript'].validateSequence(wx.MessageBox)
            
        self.scriptText=self.txtScript.GetText()


