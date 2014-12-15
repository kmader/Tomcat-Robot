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
#import socket, select

import threading

DebugMode=0 # 0 is beamline, 1 is beamline but avoiding usage, 2 is offbeamline ohne epics
RCVersion=20081127
print "Using RobotCommon Library Version : "+str(RCVersion)+" debug mode:"+str(DebugMode)
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


if DebugMode<2:
    #-------------------------CaChannel import--------------------------------------------------
    
    try:
      from CaChannel import *
      from CaChannel import CaChannelException
    except:
      try:
        sys.path.insert (0, os.path.expandvars ("$SLSBASE/sls/lib/python22/CaChannel"))
        from CaChannel import *
        from CaChannel import CaChannelException
      except:
        os.system ("xkbbell")
        os.system ("xmessage -nearmouse -timeout 30 -buttons '' CaChannel module cannot be found, Program will run in simulation mode")
        DebugMode=2 # run without silly epics
      #endtry
    #endtryX_ROBOT_X02DA_lowlevel-cmd.template
    
    
    
if DebugMode<2:    
    #-------------------------Epics Channel Class--------------------------------------------------
    # KSM : I have modified this code to allow for a debug mode for off-beamline use
    # and better feedback to the user on what is going on
    class RoboEpicsChannel:
        def __init__(self,pvName,verbose=0):
            self.MAXPUTS=10
            self.pvName=pvName
            self.status=0 # no error
            self.severity=0
            self.statusReady=0 # has a command been executed
            self.waiting=0 # is the variable overbooked
            self.putAttempts=0 # the number of times it has tried to put a variable
            self.putSuccess=0 # if the last put command was successful
            self.verbose=verbose # if epics should print everything out for alarms and all
            self.CurrentText=""
            if ((self.pvName.upper().find("ROBO")<0) & DebugMode):
                self.rPrint("Variable "+pvName+" affects beamline and will not be altered")
            self.reconnect()
        def rPrint(self,cString):
            self.CurrentText=self.pvName+": "+cString
            print self.CurrentText
        def binaryClick(self): #specific method for dealing with the binary variables that return T/F based on success in robot
    		putOK=self.rPutVal(5)
    		robotOK=self.getVal()
    		if (robotOK==5):
    			time.sleep(.12)
    			robotOK=self.getVal()
    		return (putOK & robotOK)
        def getVal(self):
            try:
                val=self.chan.getw()
            except:
                try: #try one time to reconnect
                    self.rPrint("Variable "+self.pvName+" appears to be disconnected, attempting reconnect")
                    self.reconnect()
                    val=self.chan.getw()
                    self.statusReady=0
                except:
                    self.connected=0
                    val=""
                    self.rPrint("Variable "+self.pvName+" cannot be read after 1 reconnect attempt")
            return val
    
        def putVal(self,val): #direct putval without any retry features
            try:
                if (self.waiting):
                    time.sleep(2) # give 2 seconds rest while the system is queued
                if ((self.pvName.upper().find("ROBO")<0) & DebugMode):
                    self.rPrint("Debug Mode Enabled, thus not altered")
                else:
                    self.chan.putw(val)
    		
                self.statusReady=0
                time.sleep(0.12)
                # sleep 120 ms to wait for alarm callback
                if (self.statusReady==0):
                    self.alarmUpdate()
                return self.putSuccess
            except:
                self.connected=0
    	    return 0
    
    
        def rPutVal(self,val): # the safe put function that ensures the robot accepts the command, the CAChannel package makes this trickier than needed
            self.putSuccess=0
            self.putAttempts=0
            while ((self.putSuccess<>1) & (self.putAttempts<self.MAXPUTS)):
                self.putVal(val)	
                if (self.putSuccess==0):
                    self.rPrint("Ensure Robot is on and in correct Position! Attempt "+self.putAttempts.__str__()+" of "+self.MAXPUTS.__str__())
                    tempPA=self.putAttempts
                    self.reconnect()
                    time.sleep(5)
                    self.putAttempts=tempPA
    
            if (self.putSuccess):
                if (self.verbose):
        			print self.pvName+" was successfully put"
                return 1
            else:
                self.rPrint("Put was not successful")
                return 0
        
        def statusText(self):
        	return self.pvName+" is currently "+ca.alarmStatusString(self.status)
    	
        def alarmHandler(self,epics_args,user_args):
        	# a function to handle the alarm feedback from epics telling the user what has happened
            # the primary purpose is to not allow channels to get overbooked CALC and to know if a variable has been set or nto
            self.status=epics_args["pv_status"]
            self.severity=epics_args["pv_severity"]
            self.alarmUpdate()
    	
        def alarmUpdate(self):
            self.statusReady=1
            if ((self.status<>ca.AlarmStatus.NO_ALARM) & (self.status<>ca.AlarmStatus.CALC_ALARM)):
    		
                self.putSuccess=0
                self.putAttempts+=1
                if (self.verbose):
                    print self.statusText()
                print "Variable "+self.pvName+" not successfully written after "+str(self.putAttempts)+" try"
                
                print "Alarm Severity : "+ca.alarmSeverityString(self.severity)
            else:
                self.putSuccess=1
                self.putAttempts=0
    			
            if (self.status==ca.AlarmStatus.CALC_ALARM):
                self.waiting=1
                if (self.verbose):
                    print "Variable "+self.pvName+" is currently queued!"
            if ((self.waiting==1) & (self.status==ca.AlarmStatus.NO_ALARM)):
                self.waiting=0
                if (self.verbose):
                    print "Queue Cleared!"
        def reconnect(self):
            try:
                self.chan=CaChannel()
                self.chan.search(self.pvName)
                self.chan.pend_io()
                if (self.chan.element_count()<1):
                    self.rPrint("No channels named "+self.pvName+" found, is the SoftIOC running?")
                    self.connected=(self.chan.state()==ca.ch_state.cs_conn)
                self.chan.add_masked_array_event(ca.DBR_STRING,1,ca.DBE_ALARM | ca.DBE_VALUE,self.alarmHandler)
    	    
            except CaChannelException, status:
                print ca.message(status)
                self.connected=0
else:
    class RoboEpicsChannel:
        def __init__(self,pvName,verbose=0):
            self.MAXPUTS=10
            self.pvName=pvName
            self.val=0
            self.status=0 # no error
            self.severity=0
            self.statusReady=0 # has a command been executed
            self.waiting=0 # is the variable overbooked
            self.putAttempts=0 # the number of times it has tried to put a variable
            self.putSuccess=0 # if the last put command was successful
            self.verbose=verbose # if epics should print everything out for alarms and all
            self.CurrentText=""
            if ((self.pvName.upper().find("ROBO")<0) & DebugMode):
                self.rPrint("Variable "+pvName+" affects beamline and will not be altered")
            self.reconnect()
        def rPrint(self,cString):
            self.CurrentText=self.pvName+": "+cString
            print self.CurrentText
        def binaryClick(self): #specific method for dealing with the binary variables that return T/F based on success in robot
    		self.val=1
    		return 1
        def getVal(self):
            return self.val
    
        def putVal(self,val): #direct putval without any retry features
            self.val=val
    	    return val
    
    
        def rPutVal(self,val): # the safe put function that ensures the robot accepts the command, the CAChannel package makes this trickier than needed
        	self.putSuccess=1
        	self.value=val
    		return 1
        
        def statusText(self):
        	return self.pvName+" is currently jolly"
    			
    		
        def reconnect(self):
            return 1
	
#-------------------------Robot Class--------------------------------------------------
# the robot is now accessed through a class interface that treats the entire robot as a whole
# this allows all the functions to be put together under one class and for this class to imported into whatever function needs it      
class TomcatRobot: 
	def __init__(self,rChan='',robotName="X02DA-ES1-ROBO",verbose=0):
		self.ST_OFF=0
		self.ST_ON=1
		self.ST_MNT=2 # if a tray is mounted
		self.ST_ERR_START=-1 # there is an error starting
		self.ST_ERR_MNT=-2 # there is an error mounting
		self.ST_ERR_UNMNT=-3 # there is an error unmounting
		self.robotName=robotName
		self.status=self.ST_OFF
		self.CurrentText=""
		self.currentRow=-1
		self.currentCol=-1
		self.verbose=verbose
		self.rChan=rChan
		self.initEpics()
		
	def rPrint(self,cString):
		self.CurrentText=self.robotName+": "+cString
		if self.rChan=='':
			print self.CurrentText
		else:
			self.rChan.putVal(self.CurrentText)
	def initEpics(self):
		self.startCH=RoboEpicsChannel(self.robotName+":LL-ST",self.verbose)
		self.stopCH=RoboEpicsChannel(self.robotName+":LL-STOP",self.verbose)
		self.setrCH=RoboEpicsChannel(self.robotName+":LL-SETR",self.verbose)
		self.setsCH=RoboEpicsChannel(self.robotName+":LL-SETS",self.verbose)
		self.mountCH=RoboEpicsChannel(self.robotName+":LL-MNT",self.verbose)
		self.unlCH=RoboEpicsChannel(self.robotName+":LL-UNL",self.verbose)
		self.readyCH=RoboEpicsChannel(self.robotName+":LL-READY",self.verbose)
		self.modeCH=RoboEpicsChannel(self.robotName+":LL-MODE",self.verbose)
		self.unterwegsPCH=RoboEpicsChannel(self.robotName+":MT-UNTERWEGS.PROC",self.verbose)
		self.unterwegsCH=RoboEpicsChannel(self.robotName+":MT-UNTERWEGS",self.verbose)
	def start(self):
		if self.startCH.binaryClick():
			self.status=self.ST_ON
		else:
			self.status=self.ST_ERR_START
			self.rPrint("Error Starting Robot")
		return self.status
    
	def mode(self):
        	return self.modeCH.getVal().__int__()
	def ready(self):
        	return self.readyCH.getVal().__int__()
	def stageMoving(self):
        	self.unterwegsPCH.putVal(1)
        	return (self.unterwegsCH.getVal().__int__()<6)
	def stop(self):
		if self.stopCH.binaryClick():
			self.status=self.ST_OFF
		return self.status
	def rawMount(self,row,col):
		mountOK=self.setSpot(row,col)
		return mountOK & self.load()
	def mount(self,row,col):
		mountOK= self.rawMount(row,col)
		return  mountOK & self.waitReady(.5,30)
	def setSpot(self,row,col):
		self.currentRow=row
		self.currentCol=col
		return (self.setrCH.rPutVal(row) & self.setsCH.rPutVal(col))
	def load(self):
		if (self.mode()<>self.ST_OFF):
			
			if (self.mountCH.binaryClick()):
				self.status=self.ST_MNT
            		else:
				print 'Mounting Error'
				self.status=self.ST_ERR_MNT
		return self.status
	def rawUnload(self):
		if (self.mode()==self.ST_MNT):
			if (self.unlCH.binaryClick()):
				self.status=self.ST_ON
			else:
			    print 'Unmounting Error'
			    self.status=self.ST_ERR_UNMNT
		else:
			self.rPrint("Must have sample mounted to unmount!")
		return self.status
	def unload(self):
		self.rawUnload()
		return self.waitReady(0.5,30)	
	def fullStatus(self,bchl=-1):
		tStr=''
		if bchl==-1:
			tStr=self.startCH.CurrentText+", "+self.stopCH.CurrentText+", "+self.mountCH.CurrentText+", "+self.unlCH.CurrentText
		elif bchl==0:
			tStr=self.startCH.CurrentText
		elif bchl==1:
			tStr=self.stopCH.CurrentText
		elif bchl==2:
			tStr=self.mountCH.CurrentText
		elif bchl==3:
			tStr=self.unlCH.CurrentText
		elif bchl==4:
			tStr=self.setsCH.CurrentText
				
				
		return tStr
	def waitReady(self,minTime,maxTime):
		tCount=minTime*4
		time.sleep(minTime)
		while ((self.readyCH.getVal()<1) & (tCount<maxTime*4)):
			time.sleep(0.25)
			tCount+=1
		if (tCount>=maxTime*4):
			self.rPrint("Time Exceeded!")
			return 0
		return 1			
	def testCalibration(self,row,col,count): # function
		# function to test loading and unloading on the robot
		self.setSpot(row,col)
		self.waitReady(1,5)
		for i in range(1,count+1):
			self.rPrint(i.__str__()+" of "+count.__str__()) 
			self.load()
			self.waitReady(3,15)
			self.unload()
			self.waitReady(3,15)
	def testAll(self,count):
		for i in range(0,2):
			for j in range(0,10):
				self.rPrint("("+i.__str__()+","+j.__str__()+")")
				self.testCalibration(i,j,count)	
				
	def testOne(self,count):
		self.setSpot(0,0)
		self.waitReady(1,15)
		self.load()
		self.waitReady(3,15)
		for i in range(0,2):
			for j in range(0,10):
				self.rPrint("("+i.__str__()+","+j.__str__()+")")
				self.setSpot(i,j)
				self.waitReady(1,10)
				for k in range(1,count+1):
					self.rPrint(k.__str__()+" of "+count.__str__()) 
					self.unload()
					self.waitReady(3,15)
					self.load()
					self.waitReady(3,15)

class RobotMonitor(threading.Thread):
    def __init__(self,myRobot,reportFunc):
        self.myRobot=myRobot
        self.reportFunc=reportFunc
    def run(self):
        while 1:
            mode=self.myRobot.mode()
            ready=self.myRobot.ready()
            txtStat=''
            if mode==0:
                txtStat='Off'
            elif mode==1:
                txtStat='Unloaded'
            elif mode==2:
                txtStat='Loaded'
            else:
                txtStat='Err'
            txtStat+=', '
            if ready==1:
                txtStat+='Ready'
            elif ready==0:
                txtStat+='Not Ready'
            else:
                txtStat+='Err'
            print txtStat
            self.reportFunc.__call__(txtStat)
            time.sleep(1)
        

		
