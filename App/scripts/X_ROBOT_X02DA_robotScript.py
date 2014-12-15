#! /usr/bin/env python

#-------------------------Import libraries---------------------------------------------------
import sys
import os.path
import string
import commands
import os
import time
import traceback
import readline
import signal
import getopt
import socket, select
import tkMessageBox
import tkSimpleDialog
import threading
import thread
import pdb
import re
from copy import deepcopy

try:
    from  X_ROBOT_X02DA_robotCommon import *
except:
    print "Initial robotCommon not found!"
    try:
        sys.path.insert (0, os.path.expandvars ("$SLSBASE/sls/bin/"))
        from  X_ROBOT_X02DA_robotCommon import *
    except:
        os.system ("xkbbell")
        os.system ("xmessage -nearmouse -timeout 30 -buttons '' RobotCommon Python Library is needed to run this program!")
        sys.exit (1)
# RobotScript Library
RSVersion=20101124
print "Using RobotScript Library Version : "+str(RSVersion)
tArray=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P']
# Disabled Positions on the Tray
DisabledTrayPositions=['H*','I*','J*']
def IsTrayPositionOpen(spotName='',row=-1,col=-1):
    if spotName=='':
        # use row and column
        spotName=tArray[col]+str(row)
    spotName=spotName.upper()
    for cdp in DisabledTrayPositions:
        cSearch='.'.join(cdp.split('*'))
        if re.search(cSearch,spotName)!=None:
            return False
    return True

#-------------------------Python versioncheck, at least version 2---------------------------

                          
if sys.version[0:1] == "1":
  python2 = commands.getoutput ("type -p python2")
  if python2 == "":
    print "\n\aThe default python version is", sys.version
    print     "and this script needs python level 2 or higher."
    print     " Python level 2 cannot be found."
    os.system ("xkbbell")
    os.system ("xmessage -nearmouse -timeout 30 -buttons '' Python level 2 cannot be found")
    sys.exit (1)
  #endif
  sys.argv.insert (0, python2)
  os.execv (python2, sys.argv)
#endif
if sys.version[0:1] == "1":
  print "\n\aThe loading of a higher level of python seems to have failed!"
  sys.exit (1)
#endif

# Begin RobotScript Events:
def rsPutStage(event):
    [cStgA]=event.argBundle
    event.myRobotScript.cmd_PUTSTAGE([],cStg=cStgA)


class fakeEvent:
    def __init__(self,kName,argBundle):
        self.kName=kName
        self.argBundle=argBundle
# begin sequencer and stage control code
class lockedVar:
    def __init__(self,iValue=0):
        self.value=iValue
        self.lock=thread.allocate_lock()
    def get(self):
        self.lock.acquire()
        out=self.value
        self.lock.release()
        return out
    def set(self,nv=[],ad=0):
        self.lock.acquire()
        self.value+=ad
        if nv!=[]:
            self.value=nv
        out=self.value
        self.lock.release()
        return out

class RobotScript:
    def __init__(self,myRobot=0,debugMode=0,expertPresent=0,mainPtr=0,checkBeam=True):
        self.sequence=[]
    	self.sequenceFile=''
    	self.sequenceText=''
    	self.ScriptDict={}
    	self.skipList={}
    	self.fatalError=0
        self.expertRequired=0
        self.isLooping=0
        
        # Check Beam Quality
        self.checkBeam=checkBeam
        if checkBeam==False:
            print "Warning :: Ignoring Beam Status, Only use for debugging or testing!!!!"
        
        self.ij=lockedVar(0)
        self.scriptRunning=lockedVar(0)
        self.waitEvent=lockedVar(0)
        self.pauseValue=lockedVar(0)
        self.stopValue=lockedVar(0)
        self.iterValue=lockedVar(0)
        self.beginValue=lockedVar(0)
        self.acquireValue=lockedVar(0)

        self.debugMode=debugMode
        self.EpicsDebugMode=globals()['DebugMode']
        self.mainPtr=mainPtr
        self.eList={}
        self.expertPresent=expertPresent
    	self.initializeValidCommands()
    	if (type(myRobot)==type(0)) & (debugMode==0):
            self.myRobot=TomcatRobot()
    	else:
            self.myRobot=myRobot
    	self.imageLog=[]
    	self.bufferedChannels={}
    	self.cFlags={}
    	globals()['tomcatRobotScriptLock']=thread.allocate_lock()
    	self.guiChannels()


    def loadFile(self,sequenceFile=''):
        if len(sequenceFile)>0:
            self.sequenceFile=sequenceFile
        if len(self.sequenceFile)>0:
            self.parseSequenceFile()
            
    def loadText(self,sequenceText='',ScriptDict=[]):    
        if len(sequenceText)>0:
            self.sequenceText=sequenceText
        if len(ScriptDict)>0:
            self.ScriptDict=ScriptDict
        if ((len(self.ScriptDict)>0) & (len(self.sequenceText)>0)):
            self.initializeValidCommands()
            self.parseSequenceText()
            
    def waitrobot(self,mode):
        while self.myRobot.mode()!=mode:
            time.sleep(0.75)
            if self.EpicsDebugMode==2: self.myRobot.modeCH.fakePut(mode)
    def checkloadpos(self):
        return (self.chStageDist.getVal()<10)
    def checkmotorstatus(self):
        if self.debugMode<1:
            time.sleep(1.3) # give the motors time to start moving
            while (self.myRobot.stageMoving()):
                print 'Stage Moving!'
                time.sleep(0.75)
        else:
            #print 'Waiting for fake motors'
            time.sleep(1)
    
    def parseCommand(self,inpStrR):
    	outCmd=[]
    	inpStr=inpStrR.strip()
    	oparen=inpStr.find('(')
    	cparen=inpStr.find(')')
    	print 'To Parse : '+inpStrR
    	if ((oparen>0) & (cparen>oparen)):
    		
    		outCmd.append(inpStr[0:oparen])
    		outParms=[]
    		args=inpStr[oparen+1:cparen]
    		if len(args)>0:
    			cComma=-1
    			for ij in range(0,args.count(',')):
    				nComma=args.find(',',cComma+1)
    				if nComma>(cComma+1): outParms.append(eval(args[cComma+1:nComma]))
    				#I know eval is not safe, but it is easy
    				cComma=nComma
    			if cComma+1<len(args): outParms.append(eval(args[cComma+1:]))
    		outCmd.append(outParms)
    	else:
    		outCmd.append(inpStr)
    		outCmd.append([])
        print 'As : '+str(outCmd)
    	return outCmd
     
    def cmd_SENDSMS(self,args):
        import os
        os.system('X_ROBOT_X02DA_robotSMS.pl '+args[0]+' "'+args[1]+'"')
    def cmd_WAITBEAMLINE(self,args):
        if self.checkBeam:
            CurrentStatus=self.chRingCurrent.getVal()
            AbsorberStatus=self.chAbsorberStatus.getVal()
            Interlock=self.chInterlock.getVal()
            if self.EpicsDebugMode==2:
                self.chRingCurrent.fakePut(400)
                self.chAbsorberStatus.fakePut(1)
                self.chInterlock.fakePut(0)
            while (CurrentStatus <= (self.CurrentStart-0.05*self.CurrentStart) or Interlock==1 or AbsorberStatus==0):
                self.chFeedback.putVal('Error : Beam is NOT ready!')
                time.sleep(0.5)
                CurrentStatus=self.chRingCurrent.getVal()
                AbsorberStatus=self.chAbsorberStatus.getVal()
                Interlock=self.chInterlock.getVal()
            if (CurrentStatus >= (self.CurrentStart-0.05*self.CurrentStart) and Interlock==0 and AbsorberStatus==0):
                self.chFeedback.putVal('Absorber has been closed')
                print "Error : The absorber has been closed by the interlock!!!"
                self.chAbsorberStatus.putVal(1)
                print "Waiting 60s for thermal compensation after the absorber has been closed ..."
                self.chFeedback.putVal("Waiting 60s for thermal compensation")
                time.sleep(60)
        self.myRobot.checkmotorstatus()
    def cmd_PUTSTAGE(self,args,cStg={}):
        globals()['tomcatRobotScriptLock'].acquire()
        if len(cStg)==0:
            sName=args[0]
            cItem=self.ScriptDict[sName]
            self.chFeedback.putVal("Moving Stage to Position:"+sName)
            if self.debugMode: print("Moving Stage to Position:"+sName)
            cStg=cItem[2]
        cKeys=cStg.keys()
        for i in range(0,len(cKeys)):
            tempChan=RoboEpicsChannel(cKeys[i])
            #cVal=tempChan.getVal()
            tempChan.putVal(cStg[cKeys[i]])
        time.sleep(1)
        self.myRobot.GotoImagePos()
        
        globals()['tomcatRobotScriptLock'].release()
    def cmd_DANCE(self,args):
        self.chFeedback.putVal("And were dancing")
        self.myRobot.checkmotorstatus()
        self.myRobot.rotAxisCH.putVal(90)
        self.myRobot.checkmotorstatus()
        self.myRobot.rotAxisCH.putVal(-90)
        self.myRobot.checkmotorstatus()
        self.myRobot.rotAxisCH.putVal(0)
        self.myRobot.checkmotorstatus()
    def cmd_IMMOUNT(self,args):
        
        sName=args[0]
        cItem=self.ScriptDict[sName]
    	print "sending mount cmd for "+sName
        globals()['tomcatRobotScriptLock'].acquire()
        if self.debugMode<1: self.myRobot.mount(cItem[0],cItem[1])
        self.waitrobot(2)
        globals()['tomcatRobotScriptLock'].release()
        self.cmd_PUTSTAGE(args)
        if self.cFlags.has_key('DANCE'):
            if self.cFlags['DANCE']>0:
                time.sleep(1)
                for i in range(0,self.cFlags['DANCE']):
                    self.cmd_DANCE(args)
                self.cmd_PUTSTAGE(args)
        return cItem
    def cmd_IMUNMOUNT(self,args):
        if self.cFlags.has_key('ALIGN'):
            if self.cFlags['ALIGN']>0:
                print 'verifying sample and goniometer status...'
                self.myRobot.MoveStageToLoadingPos()
                print 'Running GonioAlignment Tool'
                self.chFeedback.putVal("GAligning Sample")
                self.chGAlignment.putVal(1)
                # sloppy busy waiting
                while self.chGAlignment.getVal()>0:
                    time.sleep(2)
                    if self.EpicsDebugMode==2: self.chGAlignment.fakePut(1)
                if self.chGAlignment.getVal()<0:
                    self.chFeedback.putVal("GAligning Failed")
                    print 'Error : GAlignment Failed!!'
                    while self.chGAlignment.getVal()<0: time.sleep(2)
                    return -1 # DO not run scan
                else:
                    print 'Alignment Complete!'   
        print 'sending real unmount cmd'  
        globals()['tomcatRobotScriptLock'].acquire()
        if self.debugMode<1: self.myRobot.unload()
        self.waitrobot(1)
        globals()['tomcatRobotScriptLock'].release()
    def cmd_SETFLAG(self,args):
        self.cFlags[args[0]]=args[1]    
    def cmd_BRAINSAMPLE(self,args):
        self.brainFlag=args[0]
        self.cFlags['BRAIN']=args[0]
    def cmd_SETIMGNAME(self,args):
        print args
        itrStr=''
    	if self.chIter.getVal()>=0:
    		itrStr='_'+str(int(self.chIter.getVal()))
        #self.cmd_WAITBEAMLINE(args)
        self.chSampleOutName.putVal(args[0]+itrStr+args[1])
    def cmd_IMAGESAMPLE(self,args,doLoad=1,doUnload=1):
        if doLoad:
            self.cmd_IMMOUNT(args)
        else:
            self.cmd_PUTSTAGE(args)
        sName=args[0]
        cItem=self.ScriptDict[sName]
        errorStr=''
        beamWarGood=0
        while (not beamWarGood):
            #errorStr='' # xris modification
            self.cmd_SETIMGNAME([args[0],errorStr])
            self.cmd_WAITBEAMLINE(args)
            
            errRpt=self.myRobot.ValidateRobot(dMode=2,dStagePos=1,dRow=cItem[1],dCol=cItem[0])
            errMsg=','.join(errRpt)
            if errMsg.find('Stg')>0:
                print 'Error Detected : '+errMsg
                # Stage is not in the imaging position
                print 'Moving Stage to Imaging Position, again ...'
                self.myRobot.GotoImagePos()
                self.myRobot.checkmotorstatus()
                errRpt=self.myRobot.ValidateRobot(dMode=2,dStagePos=1,dRow=cItem[1],dCol=cItem[0])
                errMsg=','.join(errRpt)
            if len(errRpt)>0:
                print 'Error Detected : '+errMsg
                #print '\n'.join(errRpt)
                #errorStr=errorStr+'-BadSp'
                # xris modification
                self.cmd_SETIMGNAME([args[0],errorStr])
            self.cmd_ACQUIRE([])
            errorStr+='E'
            if self.chScanInterrupt.getVal()>0:
                beamWarGood=0
                self.chFeedback.putVal("Error Scan interrupted!")
                time.sleep(2)
            else:
                beamWarGood=1
        if doUnload:
            self.cmd_IMUNMOUNT([])    
    def cmd_ACQUIRE(self,args):
    	globals()['tomcatRobotScriptLock'].acquire()
    	if self.cFlags.has_key('BRAIN'):
            if self.cFlags['BRAIN']>0:
                #self.chZeroXX.putVal(1)
                #self.chZeroZZ.putVal(1)
                print 'Acquiring in Brain Mode'
                self.chFeedback.putVal("Acquiring BrainTomogram")
                
                self.chBrainScan.putVal(1)
                # sloppy busy waiting
                while self.chBrainScan.getVal()>0:
                    time.sleep(2)
                    if self.EpicsDebugMode==2: self.chBrainScan.fakePut(0)
                print 'Acquisition Complete!, Releasing Lock'
                globals()['tomcatRobotScriptLock'].release()   
                # Function is done after brain-scan
                return 0
        if self.cFlags.has_key('ALIGN'):
            if self.cFlags['ALIGN']>0:
                #self.chZeroXX.putVal(1)
                #self.chZeroZZ.putVal(1)
                print 'Running Alignment Tool'
                self.chFeedback.putVal("Aligning Sample")
                self.chAlignment.putVal(self.cFlags['ALIGN'])
                # sloppy busy waiting
                while self.chAlignment.getVal()>0:
                    time.sleep(2)
                    if self.EpicsDebugMode==2: self.chAlignment.fakePut(1)
                if self.chAlignment.getVal()<0:
                    self.chFeedback.putVal("Aligning Failed")
                    print 'Error : Alignment Failed!!'
                    globals()['tomcatRobotScriptLock'].release()   
                    return -1 # DO not run scan
                else:
                    print 'Alignment Complete!'             
    	self.chStartScan.putVal(1)
    	self.chFeedback.putVal("Scanning Sample")
    	print 'Waiting for scan to start...'
    	sTime=time.time()
    	while self.chScanStatus.getVal()<1:
    	   time.sleep(0.5)
    	   if (time.time()-sTime)>10:
    	       print 'Error: Scan has still not started, is camera server running?'
    	       xWinMsg("Error: Scan has still not started, is camera server running?")
    
    	   
    	# sloppy busy waiting
    	while (self.chScanStatus.getVal()>0) | (self.chStartScan.getVal()>0):
    	    time.sleep(2)
    	    if self.EpicsDebugMode==2: self.chScanStatus.fakePut(0)
    	time.sleep(5) # Spec macro cannot be trusted, it is a lil bastard
    	
    	globals()['tomcatRobotScriptLock'].release()       
    def cmd_WAIT(self,args):
    	time_len=args[0]
    	time.sleep(time_len) # input params time in seconds
    	self.chFeedback.putVal("Waiting "+time_len.__str__()+" seconds")
    def cmd_PAUSE(self,args):
        self.chPause.putVal(1)
        self.chFeedback.putVal("Pause Command Sent!")
    def cmd_STARTROBOT(self,args):
    	self.myRobot.start()
    def cmd_STOPROBOT(self,args):
        self.myRobot.stop()
    	print "feature doesnt work so well yet"
    def cmd_PUTEPICS(self,args):
    	# input params epics channel name, value
        chTemp=RoboEpicsChannel(args[0])
    	chTemp.putVal(args[1])
    def initializeValidCommands(self):
        tpInt=type(1)
        tpFlt=type(1.5)
        tpStr=type("test")
        tpBol=type(1==0)
        self.ValidCommands={}
        #REPEATFOR(lineNumber,minutesSinceStart)
        self.ValidCommands['REPEATFOR']=[0,2,[[tpInt],[tpInt,tpFlt]],[]]
        #REPEAT(lineNumber,numberOfTimes)
        self.ValidCommands['REPEAT']=[0,2,[[tpInt],[tpInt]],[]]
        # if a scriptdict is defined (then using new gui program)
        #if len(self.ScriptDict)>0:
        self.ValidCommands['IMSAMPLE']=[0,1,[[tpStr]],[self.cmd_IMAGESAMPLE]]
        self.ValidCommands['SETBRAIN']=[0,1,[[tpInt]],[self.cmd_BRAINSAMPLE]]
        self.ValidCommands['SETFLAG']=[0,2,[[tpStr],[tpInt]],[self.cmd_SETFLAG]]
            # do sample remains but is expert only, with new loadposition, it is completely disabled
            #self.ValidCommands['DOSAMPLE']=[1,2,[[tpInt],[tpInt]],[self.cmd_MOUNT,self.cmd_ACQUIRE,self.cmd_UNMOUNT]]
        #else:
        #    self.ValidCommands['DOSAMPLE']=[0,2,[[tpInt],[tpInt]],[self.cmd_MOUNT,self.cmd_ACQUIRE,self.cmd_UNMOUNT]]
        #WAIT(timeSeconds)
        self.ValidCommands['WAIT']=[0,1,[[tpFlt,tpInt]],[self.cmd_WAIT]]
        self.ValidCommands['SETIMGNAME']=[0,2,[[tpStr],[tpStr]],[self.cmd_SETIMGNAME]]
        #STARTROBOT()
        self.ValidCommands['STARTROBOT']=[0,0,[],[self.cmd_STARTROBOT]]
        # PAUSE()
        self.ValidCommands['PAUSE']=[0,0,[],[self.cmd_PAUSE]]
        #STOPROBOT()
        self.ValidCommands['STOPROBOT']=[0,0,[],[self.cmd_STOPROBOT]]
        # send sms when step is reached (number, text)
        self.ValidCommands['SENDSMS']=[0,2,[[tpStr],[tpStr]],[self.cmd_SENDSMS]]
        # expert only commands
        #if len(self.ScriptDict)>0:
            # Manually mount a sample using its name
        self.ValidCommands['MOUNT']=[1,1,[[tpStr]],[self.cmd_IMMOUNT]]
            # Manually unmount a sample
        self.ValidCommands['UNMOUNT']=[1,0,[],[self.cmd_IMUNMOUNT]]
        #else:
            # Manually mount a sample using its tray position
            #self.ValidCommands['MOUNT']=[1,2,[[tpInt],[tpInt]],[self.cmd_MOUNT]]
            # Manually unmount a sample
            #self.ValidCommands['UNMOUNT']=[1,0,[],[self.cmd_UNMOUNT]]
            # Manually have the program run
        self.ValidCommands['ACQUIRE']=[1,0,[],[self.cmd_ACQUIRE]]
        self.ValidCommands['PUTEPICS']=[1,2,[[tpStr],[tpInt,tpFlt,tpStr,tpBol]],[self.cmd_PUTEPICS]]
        self.ValidCommands['PUTSTAGE']=[1,1,[[tpStr]],[self.cmd_PUTSTAGE]]
        
         	
    def parseSequenceFile(self):
        if len(self.sequenceFile)>0:
            f=open(self.sequenceFile,'r');
            self.sequenceText=f.read()
            f.close()
            self.parseSequenceText()
    def parseSequenceText(self):    
        self.sequence=[]
        cText=self.sequenceText.split('\n')
        
        for ij in range(0,len(cText)):
            cLine=cText[ij].strip()
            # make sure its remotely long enough
            if len(cLine)>4:
                # make sure its not just a comment
                if not ((cLine.find('#')>-1) & (cLine.find('#')<4)):
                    self.sequence.append(self.parseCommand(cText[ij]))
        self.sequenceBackup=deepcopy(self.sequence) #backup
        print self.sequence
    def validateSequenceGUI(self):
        self.validateSequence()
        print str(self.fatalError)+" fatal error(s) found!"
        if self.fatalError>0:
            print "Error : "+str(self.fatalError)+" fatal error(s) found in script"
            tkMessageBox.showerror("Tomcat Sequencer",str(self.fatalError)+" fatal error(s) found in script! Halting Execution")
            sys.exit(0)
    def validateSequence(self,callback=tkMessageBox.showwarning):
        # validate sequence
        #type list
        # Here is the valid command table (command name, expOnly, arguments, argTable,execCmd)
        
        
        self.fatalError=0
        self.expertRequired=0
        self.isLooping=0
        for ij in range(0,len(self.sequence)):
            cName=self.sequence[ij][0].upper()
            if self.ValidCommands.has_key(cName):
                if cName=='REPEAT': self.isLooping=1
                
                if (len(self.sequence[ij][1])>=self.ValidCommands[cName][1]):
                    if (len(self.sequence[ij][1])>self.ValidCommands[cName][1]):
                            callback.__call__("Error : Line #"+str(ij+1)+":"+cName+" contains too many arguments!")	
                    for ikr in range(0,len(self.ValidCommands[cName][2])):
                        if self.ValidCommands[cName][2][ikr]!=0:
                                cmdMatch=0
                                for ikrs in range(0,len(self.ValidCommands[cName][2][ikr])):
                                    if (type(self.sequence[ij][1][ikr])==self.ValidCommands[cName][2][ikr][ikrs]):
                                        cmdMatch=1
                                if cmdMatch<1:
        							callback.__call__("Line #"+str(ij+1)+" contains an argument "+str(self.sequence[ij][1][ikr])+" in the wrong format: "+cName)
        							print "Line #"+str(ij+1)+" contains an argument "+str(self.sequence[ij][1][ikr])+" in the wrong format: "+cName
        							self.fatalError+=1
        			if (self.ValidCommands[cName][0]==1): self.expertRequired=1
                    if cName=='IMSAMPLE': 
                        # ensure sample is in ScriptDict
                        if not self.ScriptDict.has_key(self.sequence[ij][1][0]):
                            callback.__call__("Line #"+str(ij+1)+" contains an sample name "+str(self.sequence[ij][1][0])+" not in sample library "+str(self.ScriptDict.keys()))
                            print "Error : Line #"+(ij+1).__str__()+" contains an sample name "+str(self.sequence[ij][1][0])+" not in sample library "+str(self.ScriptDict.keys())
                            
                            self.fatalError+=1
            else:
                callback.__call__("Line #"+str(ij+1)+" contains the unrecognized command: "+cName) 
                print "Error : Line #"+str(ij+1)+" contains the unrecognized command: "+cName	
                self.fatalError+=1
        #
        return self.fatalError
        
        
    	
    # provide feedback to user panel
    def guiChannels(self):
        self.chFeedback=RoboEpicsChannel("X02DA-ES1-ROBO:GUI-FEEDBACK")
        self.chRoboFeedback=RoboEpicsChannel("X02DA-ES1-ROBO:GUI-ROBOTSTAT")
        self.chLineFeedback=RoboEpicsChannel("X02DA-ES1-ROBO:GUI-CODESTAT")
        self.chBegin=RoboEpicsChannel("X02DA-ES1-ROBO:GUI-BEGIN")	
        self.chStop=RoboEpicsChannel("X02DA-ES1-ROBO:GUI-STOP")
        self.chPause=RoboEpicsChannel("X02DA-ES1-ROBO:GUI-PAUSE")
        self.chReset=RoboEpicsChannel("X02DA-ES1-ROBO:GUI-RESET")
        self.chSkip=RoboEpicsChannel("X02DA-ES1-ROBO:GUI-SKIPNEXT")
        self.chIter=RoboEpicsChannel("X02DA-ES1-ROBO:CM-ITER")
        self.chIterMax=RoboEpicsChannel("X02DA-ES1-ROBO:CM-ITERMAX")
        self.chCurrentCommand=RoboEpicsChannel("X02DA-ES1-ROBO:GUI-CCMD")	
        self.chFullStatus=RoboEpicsChannel("X02DA-ES1-ROBO:GUI-FULLSTAT")
        self.chUserContact=RoboEpicsChannel('X02DA-ES1-ROBO:GUI-USERPH')
        self.chScriptRuns=RoboEpicsChannel('X02DA-ES1-ROBO:SEQ-GO')
    def scriptPrologue(self):
        self.guiChannels()
        self.chBegin.putVal(0)
        self.chIterMax.putVal(0)
        self.chReset.putVal(0)
        self.chPause.putVal(0)
        self.chSkip.putVal(0)
        self.chStop.putVal(0)
        self.chScriptRuns.putVal(1)
        self.InitializeStageChannels()
        self.chFeedback.putVal("Waiting for Begin...")
        if self.myRobot.mode()==2:
            xWinMsg('Robot is currently mounted!, please unmount before continuing!')
            sys.exit(-1)
        if self.chStartScan.getVal()==1:
            xWinMsg('Scan is already in progress please stop current scan before starting!')
            sys.exit(-1)
        
        if self.debugMode:
        	print "Debug Mode Enabled"
        if self.debugMode: # used to be ==1
        	print "Skipping Communications Routines"
        else:
        	self.myRobot.start()
        if (self.isLooping) and (self.chIter.getVal()<0): self.chIter.putVal(0)
        self.scriptRunning.set(1)
        
            
    def execEvent(self,cName,allArgs):
        self.chCurrentCommand.putVal(cName)
        dMode=0
        if len(allArgs)==3:
            [sseq,optModeDoMount,optModeDoUnmount]=allArgs
            dMode=3
        elif len(allArgs)==1:
            [sseq]=allArgs
            dMode=1
        if self.ValidCommands.has_key(cName):
            for ibCmd in range(0,len(self.ValidCommands[cName][3])):
                if self.debugMode==0:
                    if dMode==1:
                        self.ValidCommands[cName][3][ibCmd].__call__(sseq)
                    elif dMode==3:
                        self.ValidCommands[cName][3][ibCmd].__call__(sseq,optModeDoMount,optModeDoUnmount)
                    else:
                        print 'Error : Problem with arguments in '+str(cName)+' :'+str(allArgs)
                else:
                    print cName+':'+str(sseq)
        else:
            print 'Command '+cName+' not found!'           
    def stepIter(self):
        self.chIter.putVal(self.chIter.getVal()+1)
        self.chIterMax.putVal(self.sequence[self.ij.get()][1])
    def printDone(self):
        self.chCurrentCommand.putVal("Done!")
        self.chLineFeedback.putVal("Done!")
        self.chFeedback.putVal("Done!")
        self.chStop.putVal(0)
        self.chPause.putVal(0)
        self.chBegin.putVal(0)
        self.chReset.putVal(0)
        self.chBegin.putVal(0)
        self.scriptRunning.set(0)
    def executeScript(self,callback=tkMessageBox.showwarning,waitBegin=1,dbDelay=1):
        self.scriptPrologue()
        print "Waiting For Begin Command from Sequencer Panel..."
        # execute beginning events
        self.startTime=time.time()    
        self.imageLog=[]
        # for back-to-back samples in the same position
        optModeDoUnmount=1
        optModeDoMount=1
        
        # wait here for the 'go' command
        while (self.chBegin.getVal()==0):
            if (self.chStop.getVal()): sys.exit(-1)
            self.chFeedback.putVal("Script Waiting for Begin Command")
            time.sleep(0.5)
            if self.EpicsDebugMode==2: self.chBegin.fakePut(1)
            
        
        # actually execute sequence
        
        self.ij.set(0)
        
        while (self.ij.get()<len(self.sequence)) and (self.stopValue.get()==0):
            if (self.chStop.getVal()): sys.exit(-1)
            self.chLineFeedback.putVal((self.ij.get()+1).__str__()+" of "+(len(self.sequence)).__str__())
            while (self.chPause.getVal()==1) and (self.chBegin.getVal()==0):
                self.chFeedback.putVal("Currently Paused!")
                if (self.chSkip.getVal()==1):
                    self.ij.set(ad=1)
                    self.chSkip.putVal(0)
                    self.chLineFeedback.putVal((self.ij.get()+1).__str__()+" of "+(len(self.sequence)).__str__())
                if (self.chReset.getVal()==1):
                    self.sequence=deepcopy(self.sequenceBackup)
                    self.ij.set(0)
                    self.chReset.putVal(0)
                if (self.chSkip.getVal()==1):
            		self.ij.set(ad=1)
            		self.chSkip.putVal(0)
                if (self.chStop.getVal()): sys.exit(-1)
            else:
                self.chPause.putVal(0)
                self.chBegin.putVal(0)
            
            self.acquireValue.set(self.chStartScan.getVal())
            
            
            if self.ij.get()>=len(self.sequence):
                cCmd=[]
            else:
                cCmd=self.sequence[self.ij.get()]
            if self.skipList.has_key(self.ij.get()):
                cCmd=[]
                print 'Line #'+str(self.ij.get())+' is on the skip-list'
            if self.debugMode:
                print cCmd
            if len(cCmd)>0:
                cCmd[0]=cCmd[0].upper()
                cName=cCmd[0]
                if self.ValidCommands.has_key(cName):
                    # special logging
                    if (cName=='IMSAMPLE'): # or cName=='DOSAMPLE' or cName=='ACQUIRE')
                        itrStr=''
                        if self.iterValue.get()>=0:
                            itrStr='_'+str(int(self.iterValue.get()))
                        self.imageLog.append(cCmd[1][0]+itrStr)
                        print "added image to log"
                        if len(self.sequence)>(self.ij.get()+1):
                            if self.sequence[self.ij.get()+1][0].upper()=='IMSAMPLE':
                                cItemC=self.ScriptDict[self.sequence[self.ij.get()][1][0]]
                                cItemN=self.ScriptDict[self.sequence[self.ij.get()+1][1][0]]
                                if (cItemN[0]==cItemC[0]) & (cItemN[1]==cItemC[1]):
                                    optModeDoUnmount=0
                        # fix this, create pseudo event ...
                        print time.asctime()+": Beginning IMSAMPLE Loop"
                        self.execEvent(cName,[self.sequence[self.ij.get()][1],optModeDoMount,optModeDoUnmount])
                        print "sample successfully imaged"            
                        
                        # old execute command
                        #for ibCmd in range(0,len(self.ValidCommands[cName][3])):
                        #        self.ValidCommands[cName][3][ibCmd].__call__(self.sequence[ij][1],doLoad=optModeDoMount,doUnload=optModeDoUnmount)
                        
                        # if the sample wasnt mounted this time, then mount next time
                        if optModeDoMount==0:
                            optModeDoMount=1
                        # if you didnt unmount this time, then dont mount next time
                        if optModeDoUnmount==0:
                            optModeDoMount=0
                            optModeDoUnmount=1
                        
                    elif cName=='REPEAT' :
                        # input params line number, number of times
                        #
                        self.stepIter()
                        if cCmd[1][1]>0:
                            self.sequence[self.ij.get()][1][1]-=1
                            self.ij.set(self.sequence[self.ij.get()][1][0]-2) #da spaeter 1 addiert wird, auch ist line number nicht index
                        else:
                            # restore the number to the original count to allow nested loops
                            self.sequence[self.ij.get()][1][1]=deepcopy(self.sequenceBackup[self.ij.get()][1][1])
                            print 'Count Restored to '+self.sequenceBackup[self.ij.get()][1][1].__str__()
                            
                    elif cName=='REPEATFOR':
                        self.stepIter()
                        if (time.time()-self.startTime)<(60*cCmd[1][1]):
                            # time elapsed is less than number of minutes listed
                            self.ij.set(self.sequence[self.ij.get()][1][0]-2)
                    else:
                        if self.debugMode:
    						#ignore commands
    						print "running "+cName
    						time.sleep(dbDelay)
                        else:
                            print "halt 9"
                            self.execEvent(cName,[self.sequence[self.ij.get()][1]])
                            # the only way I can figure out is to call each command listed with the same params
                    print "finished cmd"
                else:
                    callback.__call__("Line #"+(self.ij.get()+1).__str__()+" contains the unrecognized command: "+cName +", thus skipped")
            else:
                print "Empty Command, skipped"
            self.ij.set(ad=1)
        				
        self.printDone()
        self.chScriptRuns.putVal(0) # Officially Done
        print self.imageLog
        return self.imageLog
    def InitializeStageChannels(self):
        if ((self.expertRequired==1) & (self.expertPresent==0)):
    		xWinMsg("Expert User is required to execute this script!")
    		code=tkSimpleDialog.askstring("Tomcat Sequencer","Enter Expert User Code:")
    		if (code=="expert724") or (code=="expert247"):
    			print "validated..."
    		else:
    			sys.exit(-1)				
    
    	#-------------------------robot part-------------------------------------------------------------------
    
    	self.chStartScan=RoboEpicsChannel('X02DA-SCAN-SCN1:GO')
    	self.chScanStatus=RoboEpicsChannel('X02DA-SCAN-SCN1:STATUS')
    	self.chBrainScan=RoboEpicsChannel('X02DA-SCAN-SCN1:IDL_GO')
    	self.chAlignment=RoboEpicsChannel('X02DA-ES1-BUMP:GO')
    	self.chGAlignment=RoboEpicsChannel('X02DA-ES1-BUMP:GGO')
    	self.chZeroXX=RoboEpicsChannel('X02DA-ES1-SMP1:TRXXset0.PROC')
    	self.chZeroZZ=RoboEpicsChannel('X02DA-ES1-SMP1:TRZZset0.PROC')
    	# warning channels
    	self.chRingCurrent=RoboEpicsChannel("ARIDI-PCT:CURRENT")
        self.chInterlock=RoboEpicsChannel("X02DA-FE-AB1:ILK-STATE")
        self.chAbsorberStatus=RoboEpicsChannel("X02DA-FE-AB1:CLOSE4BL")
        # channel set when tomography script is interrupted
    	self.chScanInterrupt=RoboEpicsChannel('X02DA-SCAN-SCN1:INTR')
    	self.CurrentStart=self.chRingCurrent.getVal()
    	
    	# stage motors done moving
    	self.chStageUnterwegs=RoboEpicsChannel("X02DA-ES1-ROBO:MT-UNTERWEGS")
    	self.chStageDist=RoboEpicsChannel("X02DA-ES1-ROBO:SLD_DIST")
    	self.chStageSampDist=RoboEpicsChannel("X02DA-ES1-ROBO:SIM_DIST")
        self.chStageDict={}
    	
    	
    	# move robot to loading position

        self.chImagePosRecord=RoboEpicsChannel("X02DA-ES1-ROBO:SIM_SET.PROC")
    	# current sample name
    	self.chSampleOutName=RoboEpicsChannel("X02DA-SCAN-CAM1:FILPRE")
        self.chSampleROI=RoboEpicsChannel("X02DA-SCAN-CAM1:ROI")
    	#	record (ao, "$(ROBO):MMESXX$(N)")
    	#self.moveStagePre="X02DA-ES1-ROBO:MMESXX"
    	#self.curNamePre="X02DA-ES1-ROBO:CM-FILPRE"
    
    
    	if (type(self.myRobot)==type(0)) & (self.debugMode==0):
            print 'line removed'
            self.myRobot=TomcatRobot(self.chRoboFeedback)
    	
		
