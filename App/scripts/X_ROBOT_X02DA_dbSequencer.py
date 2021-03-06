#! /usr/bin/env python

#-------------------------Import libraries---------------------------------------------------
import sys
import os.path
import string
import commands
import os
import time,datetime
import tkMessageBox

import thread
from optparse import OptionParser
import wx



class __LoggingPipe__:
    def __init__(self,logFileName='script',dirName='Robot_Logs'):
        try:
            os.listdir( os.path.expandvars ("$HOME/"+dirName+"/"))
        except:
            os.mkdir( os.path.expandvars ("$HOME/"+dirName+"/"))
        cday=datetime.date.today()
        
        self.logFileName=os.path.expandvars("$HOME/"+dirName+"/"+logFileName+"."+str(cday)+".log")
        self.write('\n'+time.asctime()+':'+logFileName+' freshly started'+'\n',0)
    def write(self,myStr,indent=1):
        tFile=open(self.logFileName,'a+')
        tFile.write('\t'*indent+myStr)
        tFile.close()
        
sys.path.insert (0, os.path.expandvars ("$SLSBASE/sls/bin/"))
try:
    import X_ROBOT_X02DA_robotCommon
    import X_ROBOT_X02DA_robotScript
except:
    print('RobotCommon and Database Python Library is needed to run this program!')
    sys.exit (1)
try:
    import X_ROBOT_X02DA_database
    import X_ROBOT_X02DA_logbook
    dbEnabled=1
    logbookEnabled=1
except:
    print('Logbook and Database have not been loaded successfully')
    dbEnabled=0
    logbookEnabled=0

logbookText='' 
logbookName=''   
# Important Init Functions        
class dbSequence:
    def __init__(self,debugMode,expertMode,checkBeam):
        self.myRobotScript=X_ROBOT_X02DA_robotScript.RobotScript(debugMode=debugMode,expertPresent=expertMode,checkBeam=checkBeam)
        self.scriptText=''
    
def xmlOneStep(aNodes,nodeName):
    # generic function to grab subnodes and avoid overly nested code
    outNode=[]
    for aNode in aNodes:
        for bNode in aNode.childNodes:
            if bNode.nodeName.upper()==nodeName.upper():
                outNode.append(bNode)
    return outNode
def sampToName(cTraySpot,cPos):
    cPosNSuffix=''
    spinLen=len(cTraySpot[3])
    if spinLen>1:
        cPosNSuffix='_P'+str(min([cPos,spinLen-1]))
    return cTraySpot[0]+cPosNSuffix
def trayToDict(cTray):
    ScriptDict={}
    for ik in range(0,len(cTray[0])):
        for ij in range(0,len(cTray)):
            if cTray[ij][ik][2]:
                for cPos in range(0,len(cTray[ij][ik][3])):
                    ScriptDict[sampToName(cTray[ij][ik],cPos)]=[ik,ij,cTray[ij][ik][3][cPos],cPos]
                if len(cTray[ij][ik][3])==0: # empty
                    ScriptDict[cTray[ij][ik][0]]=[ik,ij,{},0]
    return ScriptDict
# Beginning of Real Program
optParse=OptionParser()
optParse.add_option('-n','--name',dest='name',help='Name of file or tray',metavar='NAME')
optParse.add_option('-t','--tray',action='store_true',dest='usedb',help='Run in tray/database mode',default=True,metavar='TRAY')
optParse.add_option('-x','--xml',action='store_false',dest='usedb',help='Run in xml file mode',default=True,metavar='XML')
optParse.add_option('-p','--showpanel',action='store_true',dest='showpanel',help='Show MEDM Panel',default=False,metavar='SHOWPANEL')
optParse.add_option('-d','--debug',action='store_true',dest='debug',help='Run program in debug mode',default=False,metavar='DEBUG')
optParse.add_option('-E','--Expert',action='store_true',dest='expert',help='Run in Expert Mode',default=False,metavar='Expert')
optParse.add_option('-L','--LOG',action='store_true',dest='log',help='Pump screen output to a log',default=False,metavar='LOG')
optParse.add_option('-G','--ignorebeam',action='store_false',dest='checkbeam',help='Ignore Beam',default=True,metavar='IGNORE')
optParse.add_option('-k','--skiplines',dest='skiplines',help='Lines in tray to skip',default='',metavar='SKIPLINES')
optParse.set_description('This program coordinates and executes sequences on the tomcat robot\nthis allows after alignment complicated procedures to be conducted')

optParse.print_help()
(opt,args)=optParse.parse_args()
if opt.log:
    newPipe=__LoggingPipe__('dbSequencer')
    globals()['sys'].stdout=newPipe
    globals()['sys'].stderr=newPipe
if dbEnabled==0:
    opt.usedb=False
else:
    logbookText+='User Id:'+X_ROBOT_X02DA_database.UserId+'\n' 
    logbookName+=X_ROBOT_X02DA_database.UserId   
if opt.showpanel:
    thread.start_new_thread(os.system,('medm -x /work/sls/config/medm/X_ROBOT_X02DA_robotSequencer.adl',))
if opt.debug:
    debugMode=1
    logbookText+='DEBUG RUN\n' 
else:
    debugMode=0
if opt.usedb:
    if opt.name is None:
        tList=X_ROBOT_X02DA_database.xGetTrayList()
        import SimpleDialog
        root=SimpleDialog.Tk()
        cDlg=SimpleDialog.SimpleDialog(root,text='Which tray?',buttons=tList)
        tIndex=cDlg.go()
        cDlg.wm_delete_window()
        del(cDlg)
        root.destroy()
        del(root)
        if tIndex>=0:
            trayId=tList[tIndex]
        else:
            sys.exit(-1)
    else:
        trayId=opt.name
    logbookName+=', Tray: '+trayId
    logbookText+='Tray Name: '+trayId+'\n'
    try:
        [cTray,scriptText]=X_ROBOT_X02DA_database.xGetWholeTray(trayId)
    except:
        tkMessageBox.showerror('Database Sequencer','Database problem or tray does not exist!')
        sys.exit(-1)
else:
    if opt.name is None:
        import tkFileDialog       
        fileWin=tkFileDialog.Open()
        fileWin.options['initialdir']=os.path.expandvars('$HOME/UserGUI')

        fileWin.options['filetypes']=[('XML Files','*.xml')]

        fileWin.show()
        filename=fileWin.filename
    else:
        filename=opt.name
    logbookText+='Tray Filename: '+filename+'\n'
    from xml.dom import minidom
    cFile=minidom.parse(filename)
    filenameName=filename[filename.rfind('/')+1:]
    logbookName+=', Tray: '+filenameName
    mNodes=xmlOneStep([cFile],'UserGUITool')
    rPanel='Tray Setup'
    trayNodes=xmlOneStep(mNodes,'-'.join(rPanel.split(' ')))
    rPanel='Script Editor'
    scriptNodes=xmlOneStep(mNodes,'-'.join(rPanel.split(' ')))
    import X_ROBOT_X02DA_UserGUI_Robot
    cTray=X_ROBOT_X02DA_UserGUI_Robot.ReadTrayFromXML(trayNodes)
    import X_ROBOT_X02DA_UserGUI_Varia
    scriptText=X_ROBOT_X02DA_UserGUI_Varia.ReadScriptFromXML(scriptNodes)
# Process SkipLines
skiplines={}
for cline in opt.skiplines.split(','):
    if len(cline)>0:
        try:
            skiplines[float(cline)]=1
        except:
            print 'Input : '+str(cline)+' was not understood!'
            sys.exit(-1)

# Make sure no other instances are running
activeDBtasks=X_ROBOT_X02DA_robotCommon.CheckSequencer()
if activeDBtasks>0:
    print activeDBtasks
    print os.getpid()
if len(activeDBtasks)>1:
    print 'Error : Another instance of the sequencer is already running!!'
    X_ROBOT_X02DA_robotCommon.xWinMsg('Another sequencer is already running!')
    sys.exit(1)
    

        
            
                        
dbClass=dbSequence(debugMode,opt.expert,opt.checkbeam)


dbClass.myRobotScript.loadText(scriptText,trayToDict(cTray))
dbClass.myRobotScript.validateSequenceGUI()
dbClass.myRobotScript.skipList=skiplines
if (dbClass.myRobotScript.fatalError==0):
    logbookText+='Script:\n'+str(scriptText)+'\n'
    nDict=trayToDict(cTray)
    logbookText+='Tray Contents:\n'+'\n'.join(map(str,nDict.items()))+'\n'
    if logbookEnabled:
        X_ROBOT_X02DA_logbook.writeEntry(logbookName,logbookText)
    
    imageLog=dbClass.myRobotScript.executeScript(dbDelay=0)
    
    logbookText=str(imageLog)
    if logbookEnabled:
        X_ROBOT_X02DA_logbook.writeEntry('Completed : '+logbookName,logbookText)
