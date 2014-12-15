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
from copy import deepcopy
#from epicsInterfaceLib import *
#from robotInterfaceLib import *
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
RSVersion=20081127
print "Using RobotScript Library Version : "+str(RSVersion)

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

# begin sequencer and stage control code


class RobotScript:
    def __init__(self,myRobot=0,debugMode=0,expertPresent=0):
        
        
        self.sequence=[]
    	self.sequenceFile=''
    	self.sequenceText=''
    	self.ScriptDict=[]
    	self.fatalError=0
        self.expertRequired=0
        self.isLooping=0
        self.debugMode=debugMode
        self.expertPresent=expertPresent
    	self.initializeValidCommands()
    	self.myRobot=myRobot
    	self.imageLog=[]
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
            
    
    def checkmotorstatus(self):
        while self.myRobot.stageMoving():
            print 'Stage Moving!'
            time.sleep(0.5)
            
    def Altcheckmotorstatus(self):
    
      time.sleep(3)
    
      print("checkmotorstatus")
      StatusXX=self.chStatusXX.getVal()
      StatusZZ=self.chStatusZZ.getVal()
      StatusZ=self.chStatusZ.getVal()
      StatusX=self.chStatusX.getVal()
      StatusY1=self.chStatusY1.getVal()
      StatusY2=self.chStatusY2.getVal()
      
      print "Status"
      print StatusXX 
      print StatusXX
      print StatusZ
      print StatusX
      print StatusY1
      print StatusY2
      
      while (StatusXX!=1 or StatusZZ!=1 or StatusZ!=1 or StatusX!=1 or StatusY1!=1 or StatusY2!=1):
      
        StatusXX=self.chStatusXX.getVal()
        StatusZZ=self.chStatusZZ.getVal()
        StatusZ=self.chStatusZ.getVal()
        StatusX=self.chStatusX.getVal()
        StatusY1=self.chStatusY1.getVal()
        StatusY2=self.chStatusY2.getVal()
        print "Wait moving motors"
        print StatusXX 
        print StatusXX
        print StatusZ
        print StatusX
        print StatusY1
        print StatusY2
        time.sleep(0.5)
         
    
    
    
    # Sequencer Code
    # function definition

    
    def parseCommand(self,inpStrR):
    	outCmd=[]
    	inpStr=inpStrR.strip()
    	oparen=inpStr.find('(')
    	cparen=inpStr.find(')')
    	if ((oparen>0) & (cparen>oparen)):
    		
    		outCmd.append(inpStr[0:oparen])
    		outParms=[]
    		args=inpStr[oparen+1:cparen]
    		if len(args)>1:
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
    	return outCmd
     
    		
    def cmd_PUTSTAGE(self,args):
        sName=args[0]
        cItem=self.ScriptDict[sName]
        self.chFeedback.putVal("Moving Stage to Position:"+sName)
        cStg=cItem[2]
        cKeys=cStg.keys()
        for i in range(0,len(cKeys)):
            tempChan=RoboEpicsChannel('X02DA-ES1-SMP1:'+cKeys[i])
            #cVal=tempChan.getVal()
            tempChan.putVal(cStg[cKeys[i]])
        self.checkmotorstatus()
    def cmd_IMMOUNT(self,args):
        sName=args[0]
        cItem=self.ScriptDict[sName]
        #self.chLoadPos.putVal(1)
        self.cmd_PUTSTAGE(['LoadPos'])
    	#self.chFeedback.putVal("Moving Stage to Loading Position")
    	
    	print "sending mount cmd"
        self.myRobot.mount(cItem[0],cItem[1])
        self.cmd_PUTSTAGE(args)
        
    def cmd_IMUNMOUNT(self,args):
        #self.chLoadPos.putVal(1)
        self.cmd_PUTSTAGE(['LoadPos'])     
        self.myRobot.unload()
    def cmd_IMAGESAMPLE(self,args):
        self.cmd_IMMOUNT(args)
        itrStr=''
    	if self.chIter.getVal()>=0:
    		itrStr='_'+self.chIter.getVal().__int__().__str__()
        self.chSampleOutName.putVal(args[0]+itrStr)
        self.cmd_ACQUIRE([])
        self.cmd_IMUNMOUNT([])    
    def cmd_MOUNT(self,args):
    	row=args[0]
    	col=args[1]
    	# input parms : row, col
    	self.chLoadPos.putVal(1)
    	self.chFeedback.putVal("Moving Stage to Loading Position")
    	self.checkmotorstatus()
    	self.myRobot.mount(row,col)
    	self.chMoveStage=RoboEpicsChannel(moveStagePre+(col+1).__int__().__str__()+".PROC")
    	self.chMoveStage.putVal(1)
    	self.chFeedback.putVal("Moving Stage to Imaging Position")
    	self.checkmotorstatus()
    	chCurName=RoboEpicsChannel(curNamePre+(col+1).__int__().__str__())
    	itrStr=''
    	if self.chIter.getVal()>=0:
    		itrStr='_'+self.chIter.getVal().__int__().__str__()
    	self.chSampleOutName.putVal(self.chCurName.getVal()+itrStr)
    	self.chFeedback.putVal("Named Output:"+self.chCurName.getVal()+itrStr)
    	time.sleep(1.0)
    def cmd_UNMOUNT(self,args):
    	self.chLoadPos.putVal(1)
    	self.chFeedback.putVal("Moving Stage to Loading Position")
    	self.checkmotorstatus()
    	self.myRobot.unload()
    def cmd_ACQUIRE(self,args):
    	self.chStartScan.putVal(1)
    	# sloppy busy waiting
    	self.chFeedback.putVal("Acquiring Tomogram")
    	while self.chStartScan.getVal():
    		time.sleep(.5)
    def cmd_WAIT(self,args):
    	time_len=args[0]
    	time.sleep(time_len) # input params time in seconds
    	self.chFeedback.putVal("Waiting "+time_len.__str__()+" seconds")
    def cmd_STARTROBOT(self,args):
    	self.myRobot.start()
    def cmd_STOPROBOT(self,args):
        self.myRobot.stop()
    	print "feature doesnt work so well yet"
    def cmd_PUTEPICS(self,args):
    	# input params epics channel name, value
        chTemp=RoboEpicsChannel(args[0])
    	chTemp.putVal(args[1])
    def cmd_DOSAMPLE(args):
    	self.cmd_MOUNT(args[0],args[1])
    	self.cmd_ACQUIRE([])
    	self.cmd_UNLOAD([])
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
        if len(self.ScriptDict)>0:
            self.ValidCommands['IMSAMPLE']=[0,1,[[tpStr]],[self.cmd_IMAGESAMPLE]]
            # do sample remains but is expert only, with new loadposition, it is completely disabled
            #self.ValidCommands['DOSAMPLE']=[1,2,[[tpInt],[tpInt]],[self.cmd_MOUNT,self.cmd_ACQUIRE,self.cmd_UNMOUNT]]
        else:
            self.ValidCommands['DOSAMPLE']=[0,2,[[tpInt],[tpInt]],[self.cmd_MOUNT,self.cmd_ACQUIRE,self.cmd_UNMOUNT]]
        #WAIT(timeSeconds)
        self.ValidCommands['WAIT']=[0,1,[[tpFlt,tpInt]],[self.cmd_WAIT]]
        #STARTROBOT()
        self.ValidCommands['STARTROBOT']=[0,0,[],[self.cmd_STARTROBOT]]
        #STOPROBOT()
        self.ValidCommands['STOPROBOT']=[0,0,[],[self.cmd_STOPROBOT]]
        # expert only commands
        if len(self.ScriptDict)>0:
            # Manually mount a sample using its name
            self.ValidCommands['MOUNT']=[1,2,[[tpStr]],[self.cmd_IMMOUNT]]
            # Manually unmount a sample
            self.ValidCommands['UNMOUNT']=[1,0,[],[self.cmd_IMUNMOUNT]]
        else:
            # Manually mount a sample using its tray position
            self.ValidCommands['MOUNT']=[1,2,[[tpInt],[tpInt]],[self.cmd_MOUNT]]
            # Manually unmount a sample
            self.ValidCommands['UNMOUNT']=[1,0,[],[self.cmd_UNMOUNT]]
            # Manually have the program run
        self.ValidCommands['ACQUIRE']=[1,0,[],[self.cmd_ACQUIRE]]
        self.ValidCommands['PUTEPICS']=[1,2,[[tpStr],[tpInt,tpFlt,tpStr,tpBol]],[self.cmd_PUTEPICS]]
    	
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
        
    def validateSequenceGUI(self):
        self.validateSequence()
        print self.fatalError.__str__()+" fatal error(s) found!"
        if self.fatalError>0:
        	tkMessageBox.showerror("Tomcat Sequencer",self.fatalError.__str__()+" fatal error(s) found in script! Halting Execution")
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
                            callback.__call__("Line #"+(ij+1).__str__()+":"+cName+" contains too many arguments!")	
                    for ikr in range(0,len(self.ValidCommands[cName][2])):
                        if self.ValidCommands[cName][2][ikr]!=0:
                                cmdMatch=0
                                for ikrs in range(0,len(self.ValidCommands[cName][2][ikr])):
                                    if (type(self.sequence[ij][1][ikr])==self.ValidCommands[cName][2][ikr][ikrs]):
                                        cmdMatch=1
                                if cmdMatch<1:
        							callback.__call__("Line #"+(ij+1).__str__()+" contains an argument "+self.sequence[ij][1][ikr].__str__()+" in the wrong format: "+cName)
        							self.fatalError+=1
        			if (self.ValidCommands[cName][0]==1): self.expertRequired=1
                    if cName=='IMSAMPLE': 
                        # ensure sample is in ScriptDict
                        if not self.ScriptDict.has_key(self.sequence[ij][1][0]):
                            callback.__call__("Line #"+(ij+1).__str__()+" contains an sample name "+self.sequence[ij][1][0].__str__()+" not in sample library "+self.ScriptDict.keys().__str__())
                            self.fatalError+=1
            else:
                callback.__call__("Line #"+(ij+1).__str__()+" contains the unrecognized command: "+cName) 	
                self.fatalError+=1
        #
        return self.fatalError
        
        
    	
    # provide feedback to user panel
    def guiChannels(self):
        self.chFeedback=RoboEpicsChannel("X02DA-ES1-ROBO:GUI-FEEDBACK")
        self.chRoboFeedback=RoboEpicsChannel("X02DA-ES1-ROBO:GUI-ROBOTSTATUS")
        self.chLineFeedback=RoboEpicsChannel("X02DA-ES1-ROBO:GUI-CODESTATUS")
        self.chBegin=RoboEpicsChannel("X02DA-ES1-ROBO:GUI-BEGIN")	
        self.chStop=RoboEpicsChannel("X02DA-ES1-ROBO:GUI-STOP")
        self.chPause=RoboEpicsChannel("X02DA-ES1-ROBO:GUI-PAUSE")
        self.chReset=RoboEpicsChannel("X02DA-ES1-ROBO:GUI-RESET")
        self.chSkip=RoboEpicsChannel("X02DA-ES1-ROBO:GUI-SKIPNEXT")
        self.chIter=RoboEpicsChannel("X02DA-ES1-ROBO:CM-ITER")
        self.chIterMax=RoboEpicsChannel("X02DA-ES1-ROBO:CM-ITERMAX")
        self.chCurrentCommand=RoboEpicsChannel("X02DA-ES1-ROBO:GUI-CCMD")	
        self.chFullStatus=RoboEpicsChannel("X02DA-ES1-ROBO:GUI-FULLSTATUS")	
    def executeScript(self,callback=tkMessageBox.showwarning,waitBegin=1,dbDelay=1):
        self.guiChannels()
        print "Waiting For Begin Command from Sequencer Panel..."
        self.chFeedback.putVal("Waiting for Begin...")
        if self.debugMode==1:
        	print "Debug Mode Enabled"
        while ((self.chBegin.getVal()==0) & (waitBegin)):
        	time.sleep(0.5)
        self.startTime=time.time()	
        	
        self.chBegin.putVal(0)
        self.chIterMax.putVal(0)
        self.chReset.putVal(0)
        self.chPause.putVal(0)
        self.chSkip.putVal(0)
        if self.debugMode==1:
        	print "Skipping Communications Routines"
        else:
        	self.InitializeStageChannels()
        	self.myRobot.start()
        
        
        if (self.isLooping) and (self.chIter.getVal()<0): self.chIter.putVal(0)
        # actually execute sequence
        
        
        ij=0
        self.sequence=deepcopy(self.sequenceBackup)
        while (ij<len(self.sequence)) and (self.chStop.getVal()!=1):
            while (self.chPause.getVal()==1) and (self.chBegin.getVal()==0):
                self.chFeedback.putVal("Currently Paused!")
                time.sleep(0.5)
            self.chPause.putVal(0)
            self.chBegin.putVal(0)
            if (self.chReset.getVal()==1):
                self.sequence=deepcopy(self.sequenceBackup)
                ij=0
                self.chReset.putVal(0)
            if (self.chSkip.getVal()==1):
        		ij+=1
            if ij>=len(self.sequence):
                cCmd=[]
            else:
                cCmd=self.sequence[ij]
            if len(cCmd)>0:
                cCmd[0]=cCmd[0].upper()
                cName=cCmd[0]
            
                if self.debugMode:
                    print cCmd
                
                self.chCurrentCommand.putVal(cCmd.__str__())
                self.chLineFeedback.putVal((ij+1).__str__()+" of "+(len(self.sequence)).__str__())
                if self.ValidCommands.has_key(cName):
                    # special logging
                    if (cName=='IMSAMPLE'): # or cName=='DOSAMPLE' or cName=='ACQUIRE')
                        itrStr=''
                        if self.chIter.getVal()>=0:
                            itrStr='_'+str(int(self.chIter.getVal()))
                        self.imageLog.append(cCmd[1][0]+itrStr)
                    if cName=='REPEAT' :
                        # input params line number, number of times
                        self.chIter.putVal(self.chIter.getVal()+1)
                        if cCmd[1][1]>0:
                            
                            self.sequence[ij][1][1]-=1
                            self.chIterMax.putVal(self.sequence[ij][1])
                            ij=self.sequence[ij][1][0]-2 #da spaeter 1 addiert wird, auch ist line number nicht index
                        else:
                            # restore the number to the original count to allow nested loops
                            self.sequence[ij][1][1]=deepcopy(self.sequenceBackup[ij][1][1])
                            print 'Count Restored to '+self.sequenceBackup[ij][1][1].__str__()
                            
                    elif cName=='REPEATFOR':
                        self.chIter.putVal(self.chIter.getVal()+1)
                        if (time.time()-self.startTime)<(60*cCmd[1][1]):
                            # time elapsed is less than number of minutes listed
                            
                            self.chIterMax.putVal(self.chIterMax.getVal()+1)
                            ij=self.sequence[ij][1][0]-2
                    else:
                        if self.debugMode:
    						#ignore commands
    						print "running "+cName
    						time.sleep(dbDelay)
                        else:
                            for ibCmd in range(0,len(self.ValidCommands[cName][3])):
                                self.ValidCommands[cName][3][ibCmd].__call__(self.sequence[ij][1])
    							# the only way I can figure out is to call each command listed with the same params
                else:
                    callback.__call__("Line #"+(ij+1).__str__()+" contains the unrecognized command: "+cName +", thus skipped")
            else:
                print "Empty Command, skipped"
            ij+=1
        				
        self.chCurrentCommand.putVal("Done!")
        self.chLineFeedback.putVal("Done!")
        self.chFeedback.putVal("Done!")
        print self.imageLog
    def InitializeStageChannels(self):
        if ((self.expertRequired==1) & (self.expertPresent==0)):
    		callback.__call__("Expert User is required to execute this script!")
    		code=tkSimpleDialog.askstring("Tomcat Sequencer","Enter Expert User Code:")
    		if (code=="expert724") or (code=="expert247"):
    			print "validated..."
    		else:
    			sys.exit(-1)				
    
    	#-------------------------robot part-------------------------------------------------------------------
    
    
    	self.chStartScan=RoboEpicsChannel("X02DA-SCAN-SCN1:GO")
    
    	# stage motors done moving
    	self.chStatusXX=RoboEpicsChannel("X02DA-ES1-SMP1:TRXX.DMOV")
    	self.chStatusZZ=RoboEpicsChannel("X02DA-ES1-SMP1:TRZZ.DMOV")
    	self.chStatusZ=RoboEpicsChannel("X02DA-ES1-SMP1:TRZ.DMOV")
    	self.chStatusX=RoboEpicsChannel("X02DA-ES1-SMP1:TRX.DMOV")
    	self.chStatusY1=RoboEpicsChannel("X02DA-ES1-SMP1:TRY1.DMOV")
    	self.chStatusY2=RoboEpicsChannel("X02DA-ES1-SMP1:TRY2.DMOV")
    	self.chStageUnterwegs=RoboEpicsChannel("X02DA-ES1-ROBO:MT-UNTERWEGS")
    
    	
    	
    	# move robot to loading position
    	self.chLoadPos=RoboEpicsChannel("X02DA-ES1-ROBO:PUTXX.PROC")
    
    	# current sample name
    	self.chSampleOutName=RoboEpicsChannel("X02DA-SCAN-CAM1:FILPRE")
    
    	#	record (ao, "$(ROBO):MMESXX$(N)")
    	self.moveStagePre="X02DA-ES1-ROBO:MMESXX"
    	self.curNamePre="X02DA-ES1-ROBO:CM-FILPRE"
    
    
    	if (type(self.myRobot)==type(0)) & (self.debugMode==0):
            print 'line removed'
            self.myRobot=TomcatRobot(self.chRoboFeedback)
    	
		
