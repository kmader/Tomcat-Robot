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
#from epicsInterfaceLib import *
#from robotInterfaceLib import *
from X_ROBOT_X02DA_robotCommon import *
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

def specialStatusFunc():
	while 1:
		for ipz in range(0,4):
			chFullStatus.putVal(myRobot.fullStatus(ipz))
			time.sleep(2)
		
def checkmotorstatus():

  time.sleep(3)

  print("checkmotorstatus")
  StatusXX=chStatusXX.getVal()
  StatusZZ=chStatusZZ.getVal()
  StatusZ=chStatusZ.getVal()
  StatusX=chStatusX.getVal()
  StatusY1=chStatusY1.getVal()
  StatusY2=chStatusY2.getVal()
  
  print "Status"
  print StatusXX 
  print StatusXX
  print StatusZ
  print StatusX
  print StatusY1
  print StatusY2
  
  while (StatusXX!=1 or StatusZZ!=1 or StatusZ!=1 or StatusX!=1 or StatusY1!=1 or StatusY2!=1):
  
     StatusXX=chStatusXX.getVal()
     StatusZZ=chStatusZZ.getVal()
     StatusZ=chStatusZ.getVal()
     StatusX=chStatusX.getVal()
     StatusY1=chStatusY1.getVal()
     StatusY2=chStatusY2.getVal()
     print "Wait moving motors"
     print StatusXX 
     print StatusXX
     print StatusZ
     print StatusX
     print StatusY1
     print StatusY2
     time.sleep(0.5)
     



# Sequencer Code
# function definitions
def show_help():
	print "TomcatRobot (12.11.08, Kevin Mader)"
        print "ABOUT"
        print " This program coordinates and executes sequences on the tomcat robot"
	print " this allows after alignment complicated procedures to be conducted"
        print "USAGE"
        print "Input parameters"
	print "	  $1  = File to Execute"
	print "	  $2  = Debug Mode/Just Verify Code"
	

        print ""
        sys.exit(0)
debugMode=0
if len(sys.argv)>1:
	sequenceFile=sys.argv[1]
else:
	import tkFileDialog
	fileWin=tkFileDialog.Open()
	fileWin.show()
	sequenceFile=fileWin.filename
if len(sys.argv)>2:
	debugMode=1	

def parseCommand(inpStrR):
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
				outParms.append(eval(args[cComma+1:nComma]))
				# I know eval is not safe, but it is easy
				cComma=nComma
			outParms.append(eval(args[cComma+1:]))
		outCmd.append(outParms)
	else:
		outCmd.append(inpStr)
		outCmd.append([])
	return outCmd
 
		



f=open(sequenceFile,'r');
cLine=f.readline()
sequence=[]
while len(cLine)>0:
	sequence.append(parseCommand(cLine))
	cLine=f.readline()
f.close()
sequenceBackup=sequence #backup
# here are the command definitions since they must come before the commands
#list of possible commands
def cmd_MOUNT(args):
	row=args[0]
	col=args[1]
	# input parms : row, col
	chLoadPos.putVal(1)
	chFeedback.putVal("Moving Stage to Loading Position")
	checkmotorstatus()
	myRobot.mount(row,col)
	chMoveStage=RoboEpicsChannel(moveStagePre+(col+1).__int__().__str__()+".PROC")
	chMoveStage.putVal(1)
	chFeedback.putVal("Moving Stage to Imaging Position")
	checkmotorstatus()
	chCurName=RoboEpicsChannel(curNamePre+(col+1).__int__().__str__())
	itrStr=''
	if chIter.getVal()>=0:
		itrStr='_'+chIter.getVal().__int__().__str__()
	chSampleOutName.putVal(chCurName.getVal()+itrStr)
	chFeedback.putVal("Named Output:"+chCurName.getVal()+itrStr)
	time.sleep(1.0)
def cmd_UNMOUNT(args):
	chLoadPos.putVal(1)
	chFeedback.putVal("Moving Stage to Loading Position")
	checkmotorstatus()
	myRobot.unload()
def cmd_ACQUIRE(args):
	chStartScan.putVal(1)
	# sloppy busy waiting
	chFeedback.putVal("Acquiring Tomogram")
	while chStartScan.getVal():
		time.sleep(.5)
def cmd_WAIT(args):
	time_len=args[0]
	time.sleep(time_len) # input params time in seconds
	chFeedback.putVal("Waiting "+time_len.__str__()+" seconds")
def cmd_STARTROBOT(args):
	myRobot.start()
def cmd_STOPROBOT(args):
	#myRobot.stop()
	print "feature doesnt work so well yet"
def cmd_PUTEPICS(args):
	# input params epics channel name, value
	chTemp=RoboEpicsChannel(args[0])
	chTemp.putVal(args[1])
def cmd_DOSAMPLE(args):
	cmd_MOUNT(args[0],args[1])
	cmd_ACQUIRE()
	cmd_UNLOAD()

# validate sequence
#type list
tpInt=type(1)
tpFlt=type(1.5)
tpStr=type("test")
tpBol=type(1==0)
# Here is the valid command table (command name, expOnly, arguments, argTable,execCmd)


ValidCommands=[]
ValidCommands.append(['REPEAT',0,2,[[tpInt],[tpInt]],[]])
ValidCommands.append(['DOSAMPLE',0,2,[[tpInt],[tpInt]],[cmd_MOUNT,cmd_ACQUIRE,cmd_UNMOUNT]])
ValidCommands.append(['WAIT',0,1,[[tpFlt,tpInt]],[cmd_WAIT]])
ValidCommands.append(['STARTROBOT',0,0,[],[cmd_STARTROBOT]])
ValidCommands.append(['STOPROBOT',0,0,[],[cmd_STOPROBOT]])
# expert only commands
ValidCommands.append(['MOUNT',1,2,[[tpInt],[tpInt]],[cmd_MOUNT]])
ValidCommands.append(['UNMOUNT',1,0,[],[cmd_UNMOUNT]])
ValidCommands.append(['ACQUIRE',1,0,[],[cmd_ACQUIRE]])
ValidCommands.append(['PUTEPICS',1,2,[[tpStr],[tpInt,tpFlt,tpStr,tpBol]],[cmd_PUTEPICS]])
fatalError=0
expertRequired=0
isLooping=0
for ij in range(0,len(sequence)):
	ik=0
	while ik<=len(ValidCommands):
		if ik==len(ValidCommands):
			print "Line #"+(ij+1).__str__()+" contains the unrecognized command: "+sequence[ij][0].upper() 	
			fatalError+=1
		elif (sequence[ij][0].upper()==ValidCommands[ik][0].upper()):
			if sequence[ij][0].upper()=='REPEAT': isLooping=1
			if (len(sequence[ij][1])>=ValidCommands[ik][2]):
				if (len(sequence[ij][1])>ValidCommands[ik][2]):
					tkMessageBox.showwarning("Line #"+(ij+1).__str__()+":"+sequence[ij][0].upper()+" contains too many arguments!")	
				for ikr in range(0,len(ValidCommands[ik][3])):
					if ValidCommands[ik][3][ikr]!=0:
						cmdMatch=0
						for ikrs in range(0,len(ValidCommands[ik][3][ikr])):
							if (type(sequence[ij][1][ikr])==ValidCommands[ik][3][ikr][ikrs]):
								cmdMatch=1
						
						if cmdMatch<1:
							print "Line #"+(ij+1).__str__()+" contains an argument "+sequence[ij][1][ikr].__str__()+" in the wrong format: "+sequence[ij][0].upper() 	
							fatalError+=1
			if (ValidCommands[ik][1]==1): expertRequired=1
			break
		ik+=1

print fatalError.__str__()+" fatal error(s) found!"


if fatalError>0:
	tkMessageBox.showerror("Tomcat Sequencer",fatalError.__str__()+" fatal error(s) found in script! Halting Execution")
	sys.exit(0)
	
# provide feedback to user panel

chFeedback=RoboEpicsChannel("X02DA-ES1-ROBO:GUI-FEEDBACK")
chRoboFeedback=RoboEpicsChannel("X02DA-ES1-ROBO:GUI-ROBOTSTATUS")
chLineFeedback=RoboEpicsChannel("X02DA-ES1-ROBO:GUI-CODESTATUS")
chBegin=RoboEpicsChannel("X02DA-ES1-ROBO:GUI-BEGIN")	
chStop=RoboEpicsChannel("X02DA-ES1-ROBO:GUI-STOP")
chPause=RoboEpicsChannel("X02DA-ES1-ROBO:GUI-PAUSE")
chReset=RoboEpicsChannel("X02DA-ES1-ROBO:GUI-RESET")
chSkip=RoboEpicsChannel("X02DA-ES1-ROBO:GUI-SKIPNEXT")
chIter=RoboEpicsChannel("X02DA-ES1-ROBO:CM-ITER")
chIterMax=RoboEpicsChannel("X02DA-ES1-ROBO:CM-ITERMAX")
chCurrentCommand=RoboEpicsChannel("X02DA-ES1-ROBO:GUI-CCMD")	
chFullStatus=RoboEpicsChannel("X02DA-ES1-ROBO:GUI-FULLSTATUS")	
print "Waiting For Begin Command from Sequencer Panel..."
while chBegin.getVal()==0:
	time.sleep(0.5)
	chFeedback.putVal("Waiting for Begin...")
	
chBegin.putVal(0)
chIterMax.putVal(0)
chReset.putVal(0)
chPause.putVal(0)
chSkip.putVal(0)
if debugMode==1:
	print "Skipping Communications Routines"
else:
	if expertRequired==1:
		print "Expert User is required to execute this script!"
		code=tkSimpleDialog.askstring("Tomcat Sequencer","Enter Expert User Code:")
		if (code=="expert724") or (code=="expert247"):
			print "validated..."
		else:
			sys.exit(-1)				

	#-------------------------robot part-------------------------------------------------------------------


	chStartScan=RoboEpicsChannel("X02DA-SCAN-SCN1:GO")

	# stage motors done moving
	chStatusXX=RoboEpicsChannel("X02DA-ES1-SMP1:TRXX.DMOV")
	chStatusZZ=RoboEpicsChannel("X02DA-ES1-SMP1:TRZZ.DMOV")
	chStatusZ=RoboEpicsChannel("X02DA-ES1-SMP1:TRZ.DMOV")
	chStatusX=RoboEpicsChannel("X02DA-ES1-SMP1:TRX.DMOV")
	chStatusY1=RoboEpicsChannel("X02DA-ES1-SMP1:TRY1.DMOV")
	chStatusY2=RoboEpicsChannel("X02DA-ES1-SMP1:TRY2.DMOV")
	chStageUnterwegs=RoboEpicsChannel("X02DA-ES1-ROBO:MT-UNTERWEGS")

	
	
	# move robot to loading position
	chLoadPos=RoboEpicsChannel("X02DA-ES1-ROBO:PUTXX.PROC")

	# current sample name
	chSampleOutName=RoboEpicsChannel("X02DA-SCAN-CAM1:FILPRE")

	#	record (ao, "$(ROBO):MMESXX$(N)")
	moveStagePre="X02DA-ES1-ROBO:MMESXX"
	curNamePre="X02DA-ES1-ROBO:CM-FILPRE"


	myRobot=TomcatRobot(chRoboFeedback)
	myRobot.start()
	threading.Thread(target=specialStatusFunc).start()


if (isLooping) and (chIter.getVal()<0): chIter.putVal(0)
# actually execute sequence


ij=0

while (ij<len(sequence)) and (chStop.getVal()!=1):
	while (chPause.getVal()==1) and (chBegin.getVal()==0):
		chFeedback.putVal("Currently Paused!")
		time.sleep(0.5)
	chPause.putVal(0)
	chBegin.putVal(0)
	if (chReset.getVal()==1):
		sequence=sequenceBackup
		ij=0
		chReset.putVal(0)
	if (chSkip.getVal()==1):
		ij+=1
	if ij>=len(sequence):
		cCmd=[]
	else:
		cCmd=sequence[ij]
	if len(cCmd)>0:
		cCmd[0]=cCmd[0].upper()
		if debugMode:
			print cCmd
		else:
			chCurrentCommand.putVal(cCmd.__str__())
			
			chLineFeedback.putVal((ij+1).__str__()+" of "+(len(sequence)).__str__())
		ik=0
		while ik<=len(ValidCommands):
			if ik==len(ValidCommands):
				print "Line #"+(ij+1).__str__()+" contains the unrecognized command: "+sequence[ij][0].upper() +", thus skipped"
			elif (cCmd[0]==ValidCommands[ik][0].upper()):	
				if cCmd[0]=='REPEAT' :
					# input params line number, number of times
					chIter.putVal(chIter.getVal()+1)
					if cCmd[1][1]>0:
						sequence[ij][1][1]-=1
						chIterMax.putVal(sequence[ij][1])
						
						ij=sequence[ij][1][0]-2 #da spaeter 1 addiert wird, auch ist line number nicht index
						

					
				else:
					if debugMode:
						#ignore commands
						print "running "+cCmd[0]
					else:
					       for ibCmd in range(0,len(ValidCommands[ik][4])):
							ValidCommands[ik][4][ibCmd].__call__(sequence[ij][1])
							# the only way I can figure out is to call each command listed with the same params
				break
			ik+=1
		ij+=1
				
chCurrentCommand.putVal("Done!")
chLineFeedback.putVal("Done!")		
			
		
