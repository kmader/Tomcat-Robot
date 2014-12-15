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
import socket
#import socket, select
import thread
#import threading
import wx
import urllib
from cPickle import loads
from random import choice,randrange
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
DebugMode=0 # 0 is beamline, 1 is beamline but avoiding usage, 2 is offbeamline ohne epics
MachineDayMode=0 # 0 means it isnt, 1 means it is
EpicsWebMode=0 # Means Epics is running through a webserver
DoLaunchWebServer=0 # set to one if the parameter is correct
EpicsWebPort=7269 # which port the epicswebserver runs on
RCVersion=20130313
KEVINCONTACT='0787551438'
IGNORELOCKS=True # do not use locking (it just causes problems)
ReadOnly=0 # if =1 then variables cannot be written (putVal fails!)
# Channel Mapping since the stageJumpPos (motor control) goes to specific fields
#and some of the aspects (TRY-VAL and ROTY) are not structured as epics motors
MappedChannels={}

import os
EMESSAGE=lambda x: os.system('X_ROBOT_X02DA_robotSMS.pl '+KEVINCONTACT+' "'+str(x)+'"')







# For Script Debugging during shutdown the epics beam variables must be constants

if MachineDayMode:
    MappedChannels['ARIDI-PCT:CURRENT']=5000
    MappedChannels['X02DA-FE-AB1:CLOSE4BL']=1
    MappedChannels['X02DA-FE-AB1:ILK-STATE']=0
    
# Until Epics Channel is Installed

## These mapped channels are specific to the Robot Script and UserGUI, but 
## moving them could make new strange bugs, and so I leave them here

#MappedChannels['X02DA-ES1-SMP1:ROTYUSETP.DVAL']='X02DA-ES1-SMP1:ROTYUSETP.VAL'
MappedChannels['X02DA-ES1-SMP1:ROTYUSETP.LLM']='X02DA-ES1-SMP1:ROTYULOLM'
MappedChannels['X02DA-ES1-SMP1:ROTYUSETP.HLM']='X02DA-ES1-SMP1:ROTYUHILM'
MappedChannels['X02DA-ES1-SMP1:ROTYUSETP.DMOV']='X02DA-ES1-ROBO:SMP1-ROTYDMOV'
MappedChannels['X02DA-ES1-SMP1:TRY.DMOV']='X02DA-ES1-SMP1:TRY1.DMOV' # hopefully y2 doesnt move much without y1
#MappedChannels['X02DA-ES1-SMP1:TRY-VAL.DVAL']='X02DA-ES1-SMP1:TRY-VAL'
MappedChannels['X02DA-ES1-SMP1:TRY.LLM']='X02DA-ES1-ROBO:SMP1-YVALMIN'
MappedChannels['X02DA-ES1-SMP1:TRY']='X02DA-ES1-SMP1:TRY-VAL.VAL'
MappedChannels['X02DA-ES1-SMP1:TRY.VAL']='X02DA-ES1-SMP1:TRY-VAL.VAL'
MappedChannels['X02DA-ES1-SMP1:TRY.PROC']='X02DA-ES1-SMP1:TRY-VAL.PROC'
MappedChannels['X02DA-ES1-SMP1:TRY.HLM']='X02DA-ES1-ROBO:SMP1-YVALMAX'
MappedChannels['X02DA-ES1-MS1:FOC_MovAbs.LLM']='X02DA-ES1-MS1:FOC_MovAbs.DRVL'
MappedChannels['X02DA-ES1-MS1:FOC_MovAbs.HLM']='X02DA-ES1-MS1:FOC_MovAbs.DRVH'
MappedChannels['X02DA-ES1-MS1:FOC_MovAbs.DMOV']='X02DA-ES1-MS1:TRZ.DMOV'
MappedChannels['X02DA-ES1-SHsize.DMOV']='X02DA-ES1-MS1:TRZ.DMOV' # stand in for later
MappedChannels['X02DA-ES1-SHsize.LLM']='X02DA-ES1-SHsize.LOPR'
MappedChannels['X02DA-ES1-SHsize.HLM']='X02DA-ES1-SHsize.HOPR'
MappedChannels['X02DA-ES1-SVsize.DMOV']='X02DA-ES1-MS1:TRZ.DMOV' # stand-in for later
MappedChannels['X02DA-ES1-SVsize.LLM']='X02DA-ES1-SVsize.LOPR'
MappedChannels['X02DA-ES1-SVsize.HLM']='X02DA-ES1-SVsize.HOPR'
MappedChannels['X02DA-ES1-SVt2.D.HLM']=0
MappedChannels['X02DA-ES1-SVt2.D.LLM']=0
MappedChannels['X02DA-ES1-SHt2.D.HLM']=0
MappedChannels['X02DA-ES1-SHt2.D.LLM']=0

StageChannels=[['TRXX',1],['TRZZ',1],['TRX',1],['TRZ',1],['TRYV',0],['GOXX',0],['GOZZ',0]]   
AlignChannels=[['A_','TRXX'],['A_','TRZZ'],['A_','TRX'],['A_','TRZ'],['A_','TRYV'],['A_','GOXX'],['A_','GOZZ']] 

# PreMap Channels for Script Purposes
MappedChannels['TRX']='X02DA-ES1-ROBO:SIM_VAL-X'
MappedChannels['TRYV']='X02DA-ES1-ROBO:SIM_VAL-YV'
MappedChannels['TRZ']='X02DA-ES1-ROBO:SIM_VAL-Z'
MappedChannels['TRXX']='X02DA-ES1-ROBO:SIM_VAL-XX'
MappedChannels['TRZZ']='X02DA-ES1-ROBO:SIM_VAL-ZZ'
MappedChannels['GOXX']='X02DA-ES1-ROBO:SIM_VAL-GOXX'
MappedChannels['GOZZ']='X02DA-ES1-ROBO:SIM_VAL-GOZZ'

# Same Channels but Alignment Versions
MappedChannels['A_TRX']='X02DA-ES1-ROBO:SAM_VAL-X'
MappedChannels['A_TRYV']='X02DA-ES1-ROBO:SAM_VAL-YV'
MappedChannels['A_TRZ']='X02DA-ES1-ROBO:SAM_VAL-Z'
MappedChannels['A_TRXX']='X02DA-ES1-ROBO:SAM_VAL-XX'
MappedChannels['A_TRZZ']='X02DA-ES1-ROBO:SAM_VAL-ZZ'
MappedChannels['A_GOXX']='X02DA-ES1-ROBO:SAM_VAL-GOXX'
MappedChannels['A_GOZZ']='X02DA-ES1-ROBO:SAM_VAL-GOZZ'
# Finally some blocked control channels (to enable different user modes)
BlockedChannels={}




# Load position is currently being stored here, but will move soon to epics
#curLoadPos={'X02DA-ES1-SMP1:TRY1': -4067.4968596813715, 'X02DA-ES1-SMP1:TRY2': -3567.7960784313727, 'X02DA-ES1-SMP1:TRXX.DVAL': 2400.0999999999999, 'X02DA-ES1-SMP1:TRX.DVAL': -22456.5, 'X02DA-ES1-SMP1:TRZZ.DVAL': 16319.400000000001 , 'X02DA-ES1-SMP1:TRZ.DVAL': -62140.0}
        


def CheckEpicsServer():
    os.system('ps -Af | grep robotCommon | grep python > robotCommonTasks.txt')
    g=open('robotCommonTasks.txt','r')
    myStr=g.read()
    g.close()
    os.remove('robotCommonTasks.txt')   
    myProc=myStr.split('\n')
    
    def junkPrune(kArg):
        if kArg!='':
            junkList.append(kArg)
    activeDBtasks=[]
    pString='X_ROBOT_X02DA_robotCommon.py'
    for proc in myProc:
        jArgs=proc.split(' ')
        junkList=[]
        map(junkPrune,jArgs)
        if len(junkList)>7:
            if (junkList[7].find(pString)>-1) or (junkList[8].find(pString)>-1):
                activeDBtasks.append(junkList[0:2])
    return activeDBtasks
def killEpicsWeb():
    if EpicsWebMode==1:
        epicsWebServers=CheckEpicsServer()
        for eachServer in epicsWebServers:
            os.system('kill -9 '+eachServer[1])
print CheckEpicsServer()
def CheckSequencer():
    os.system('ps -Af | grep dbSequencer | grep python > dbTasks.txt')
    g=open('dbTasks.txt','r')
    myStr=g.read()
    g.close()
    os.remove('dbTasks.txt')   
    myProc=myStr.split('\n')
    
    def junkPrune(kArg):
        if kArg!='':
            junkList.append(kArg)
    activeDBtasks=[]
    print 'CheckSequencer Results:'+str(myProc)
    pString='X_ROBOT_X02DA_dbSequencer.py'
    for proc in myProc:
        jArgs=proc.split(' ')
        junkList=[]
        map(junkPrune,jArgs)
        if len(junkList)>7:
            if (junkList[7].find(pString)>-1) or (junkList[8].find(pString)>-1):
                activeDBtasks.append(junkList[0:2])
    return activeDBtasks
def tcSendSMS(msg='TOMCAT Alert!',beamcell='0787551438'):
    os.system('X_ROBOT_X02DA_robotSMS.pl "'+beamcell+'" "'+msg+'"')
                    
def xWinMsg(txtval):
    os.system ("xkbbell")
    os.system ("xmessage -nearmouse -timeout 30 -buttons '' "+txtval+"")

#-------------------------Python versioncheck, at least version 2---------------------------

                          
if sys.version[0:1] == "1":
  python2 = commands.getoutput ("type -p python2")
  if python2 == "":
    print "\n\aThe default python version is", sys.version
    print     "and this script needs python level 2 or higher."
    print     " Python level 2 cannot be found."
    xWinMsg('Python level 2 cannot be found')
    sys.exit (1)
  #endif
  sys.argv.insert (0, python2)
  os.execv (python2, sys.argv)
#endif
if sys.version[0:1] == "1":
  print "\n\aThe loading of a higher level of python seems to have failed!"
  sys.exit (1)
#endif

# Epics Web Server Code
if __name__ == '__main__':
    import sys
    import os
    import time
    #from X_ROBOT_X02DA_robotCommon import *
    from optparse import OptionParser
    
    import string,cgi,time
    from os import curdir, sep
    
    from cPickle import dumps,loads
    import urllib
    optParse=OptionParser()
    optParse.add_option('-R','--run',action='store_true',dest='run',default=False,help='Launch WebServer')
    optParse.add_option('-P','--port',dest='port',default=7269,help='Port to run server on')
    optParse.add_option('-N','--nofork',dest='fork',action='store_false',default=True,help='Fork off EpicsServer')
    optParse.add_option('-L','--LOG',action='store_true',dest='log',help='Pump screen output to a log',default=False,metavar='LOG')
    optParse.set_description('This program runs as a fork of the robot program allowing epics to be entirely distinct from the GUI')
    (opt,args)=optParse.parse_args()
    if opt.run:
        if opt.fork:
            pid=os.fork()
            if pid>0:
                print 'Fork Successfully Created'
                sys.exit(0)
        EpicsWebMode=0 # don't try to connect to yourself to read channels
        EpicsWebPort=int(opt.port)
        DoLaunchWebServer=1
print "Using RobotCommon Library Version : "+str(RCVersion)+" debug mode:"+str(DebugMode)+" WebService: "+str(EpicsWebMode)+" Machine Day: "+str(MachineDayMode)
    
if (DebugMode<2) and (EpicsWebMode==0):
    #-------------------------CaChannel import--------------------------------------------------
    try:
      #
      from CaChannel import *
      from CaChannel import CaChannelException
    except:
      try: 
        #sys.path.insert (0, os.path.expandvars ("$SLSBASE/sls/lib/python22/CaChannel"))
        sys.path.insert (0, os.path.expandvars ("/usr/local/epics/extensions/lib/SL5-x86/python2.4/"))
        from CaChannel import *
        from CaChannel import CaChannelException
        print 'Original Load Had Failed'
      except:
        xWinMsg('CaChannel module cannot be found, Program will run in simulation mode')
        DebugMode=2 # run without silly epics
      #endtry
    #endtryX_ROBOT_X02DA_lowlevel-cmd.template
    
  
    
  
#-------------------------Epics Channel Class--------------------------------------------------
# KSM : I have modified this code to allow for a debug mode for off-beamline use
# and better feedback to the user on what is going on
class RealRoboEpicsChannel:
    def __init__(self,pvName,verbose=0,asString=0,vcCallback=None):
        self.MAXPUTS=1000
        self.pvName=pvName
        self.asString=asString
        self.curValue=0
        self.lastPoll=0
        self.status=0 # no error
        self.severity=0
        self.statusReady=0 # has a command been executed
        self.waiting=0 # is the variable overbooked
        self.putAttempts=0 # the number of times it has tried to put a variable
        self.putSuccess=0 # if the last put command was successful
        self.verbose=verbose # if epics should print everything out for alarms and all
        self.CurrentText=""
        self.vcCallback=vcCallback # the callback should the value change feed with (chname,newVal,oldVal)
        
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
		if (ReadOnly):
			putOK=1
			robotOK=1
		return (putOK & robotOK)
    def getVal(self):
        
        try:
            cTime=time.time()
            if (cTime-self.lastPoll)>0.2: # prevent double polling
                
                val=self.chgetw()
                self.curValue=val
                self.lastPoll=cTime
            else:
                val=self.curValue
        except:
            try: #try one time to reconnect
                self.rPrint("Variable "+self.pvName+" appears to be disconnected, attempting reconnect")
                self.reconnect()
                val=self.chgetw()
                self.statusReady=0
            except:
                self.connected=0
                val=""
                self.rPrint("Variable "+self.pvName+" cannot be read after 1 reconnect attempt")
        return val
    def chgetw(self):
        if self.asString==1:
            return str(self.chan.getw(ca.DBF_STRING))
        else:
            return self.chan.getw()
    def putVal(self,iVal): #direct putval without any retry features
        self.lastPoll=0
        
        # crop string when it is too long
        val=iVal
        if type(iVal)==type(''):
            if len(iVal)>40:
                val=iVal[0:39]
                print 'String was cropped :'+str(val)
                
        try:
            if (self.waiting):
                time.sleep(2) # give 2 seconds rest while the system is queued
            if ((self.pvName.upper().find("ROBO")<0) & DebugMode):
                self.rPrint("Debug Mode Enabled, thus not altered")
            else:
                if not ReadOnly:
                    self.curValue=val # default assumption is the value will be loaded
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
        self.lastPoll=0
        while ((self.putSuccess<1) & (self.putAttempts<self.MAXPUTS)):
            self.putVal(val)	
            if (self.putSuccess==0):
                self.rPrint("Ensure Robot is on and in correct Position! Attempt "+str(self.putAttempts)+" of "+str(self.MAXPUTS))
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
	
    def vcHandler(self,epics_args,user_args):
        # A function to handle value change callbacks
        newValue=epics_args['pv_value']
        self.lastPoll=time.time() 
        if newValue!=self.curValue:
            # It is different from what we set it to, ick
            self.curValue=newValue
            self.vcCallback.__call__(self.pvName,newValue,self.curValue)
            
        
           
    def alarmHandler(self,epics_args,user_args):
    	# a function to handle the alarm feedback from epics telling the user what has happened
        # the primary purpose is to not allow channels to get overbooked CALC and to know if a variable has been set or nto
        curStatus=epics_args["pv_status"]
        CurSeverity=epics_args["pv_severity"]
        if curStatus==ca.AlarmStatus.READ_ALARM:
            print "alarmHandler: Read Alarm has been ignored for :"+self.pvName
            curStatus=ca.AlarmStatus.NO_ALARM
            curSeverity=ca.AlarmSeverity.NO_ALARM         
        self.status=curStatus
        self.severity=curSeverity
        self.alarmUpdate()
	
    def alarmUpdate(self):
        self.statusReady=1
        if self.status==ca.AlarmStatus.READ_ALARM:
            print "alarmUpdate: Read Alarm has been ignored for :"+self.pvName
            self.status=ca.AlarmStatus.NO_ALARM
            self.severity=ca.AlarmSeverity.NO_ALARM  
        if ((self.status<>ca.AlarmStatus.NO_ALARM) & (self.status<>ca.AlarmStatus.CALC_ALARM)):
		
            self.putSuccess=0
            self.putAttempts+=1
            if (self.verbose):
                print self.statusText()
            if not (self.pvName.upper()=='ARIDI-PCT:CURRENT'): 
                print "Variable "+self.pvName+" not successfully written after "+str(self.putAttempts)+" try"
                print "Alarm Status: "+ca.alarmStatusString(self.status)+", Severity: "+ca.alarmSeverityString(self.severity)
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
                self.rPrint("Error : No channels named "+self.pvName+" found, is the SoftIOC running?")
                self.connected=(self.chan.state()==ca.ch_state.cs_conn)
            #KSM NOV2010 - Remove callback bullshit
            self.chan.add_masked_array_event(ca.DBR_STRING,None,ca.DBE_ALARM,self.alarmHandler)
            self.rebind(self.vcCallback)
        except CaChannelException, status:
            print ca.message(status)
            self.connected=0
    def rebind(self,vcCallback):
        if (self.pvName=='ARIDI-PCT:CURRENT'): return -1 # current is updated to often
        if (vcCallback!=None): # otherwise the callback is a huge waste or processor time
            self.vcCallback=vcCallback
            #KSM NOV2010 - Remove callback bullshit
            #self.chan.add_masked_array_event(None,None,ca.DBE_VALUE,self.vcHandler)
    def __del__(self):
        self.connected=0
        self.chan.clear_channel()
        del self.chan
    def destroy(self):
        self.connected=0
            

class FakeRoboEpicsChannel:
    def __init__(self,pvName,verbose=0,asString=0,vcCallback=None):
        self.MAXPUTS=10
        self.pvName=pvName
        self.asString=asString
        self.val=0
        self.status=0 # no error
        self.severity=0
        self.statusReady=0 # has a command been executed
        self.waiting=0 # is the variable overbooked
        self.putAttempts=0 # the number of times it has tried to put a variable
        self.putSuccess=0 # if the last put command was successful
        self.verbose=verbose # if epics should print everything out for alarms and all
        self.CurrentText=""
        self.chan={}
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
        if self.asString==1:
            return str(self.val)
        else:
            return self.val

    def putVal(self,val): #direct putval without any retry features
        self.val=val
        return val
    def fakePut(self,val):
        self.val=val
        return val

    def rPutVal(self,val): # the safe put function that ensures the robot accepts the command, the CAChannel package makes this trickier than needed
    	self.putSuccess=1
    	self.value=val
        return 1
    
    def statusText(self):
    	return self.pvName+" is currently jolly"
			
		
    def rebind(self,vcCallback):
        return 1
    def reconnect(self):
        return 1
    def destroy(self):
        #print self.pvName+' wird zerstoert'
        return 1
    
class WebServerRoboEpicsChannel:
    def __init__(self,pvName,verbose=0,asString=0,vcCallback=None):
        self.MAXPUTS=10
        self.pvName=pvName
        self.asString=asString
        self.val=0
        self.status=0 # no error
        self.severity=0
        self.statusReady=0 # has a command been executed
        self.waiting=0 # is the variable overbooked
        self.putAttempts=0 # the number of times it has tried to put a variable
        self.putSuccess=0 # if the last put command was successful
        self.verbose=verbose # if epics should print everything out for alarms and all
        self.CurrentText=""
        self.chan={}
        if ((self.pvName.upper().find("ROBO")<0) & DebugMode):
            self.rPrint("Variable "+pvName+" affects beamline and will not be altered")
        self.reconnect()
    def rPrint(self,cString):
        self.CurrentText=self.pvName+": "+cString
        print self.CurrentText
    def binaryClick(self): #specific method for dealing with the binary variables that return T/F based on success in robot
		return self.rPutVal(1)
    def __webQuery__(self,req='GET',val='',_numRetry=0):
        if _numRetry>self.MAXPUTS:
            self.rPrint('TOO MANY FAILED WEBQUERIES, CHECK WEBSERVER, RESTART COMPUTER!!!')
            sys.exit(-1)
        
        try:
            rawString=urllib.urlopen('http://localhost:'+str(EpicsWebPort)+'/'+req+'_EPICS_PICKLE?'+urllib.urlencode({self.pvName:val})).read()
        except:
            self.rPrint('Probably the webserver is down!')
            self.rPrint('Restarting...')
            globals()['EpicsWebPort']=globals()['EpicsWebPort']+_numRetry
            print 'Other EpicWebServers Running:'+str(CheckEpicsServer())
            os.system('python /work/sls/bin/X_ROBOT_X02DA_robotCommon.py -R -P '+str(globals()['EpicsWebPort']))
            time.sleep(0.5)
            return self.__webQuery__(req,val,_numRetry+1)
        try:
            outDict=loads(urllib.unquote(rawString))
        except:
            self.rPrint('Not Read Correctly!')
            return self.__webQuery__(req,val,_numRetry+1)
        if outDict.has_key(self.pvName):
            return outDict[self.pvName]
        else:
            self.rPrint('Missing Field Value!')
            return self.__webQuery__(req,val,_numRetry+1)    
    def getVal(self):
            
        self.val=self.__webQuery__('GET')
        if self.asString==1:
            return str(self.val)
        else:
            return self.val

    def putVal(self,val): #direct putval without any retry features
        rawString='Not Run Yet'
        isGood=self.__webQuery__('PUT',val)
        if isGood=='GOOD':     
            self.putSuccess=1
            self.val=val
        else:
            self.rPrint('Put has failed')
            self.putSuccess=0
        return self.val
    def fakePut(self,val):
        self.val=val
        return val

    def rPutVal(self,val): # the safe put function that ensures the robot accepts the command, the CAChannel package makes this trickier than needed
    	
    	self.putVal(val)
        return self.putSuccess
    
    def statusText(self):
    	return self.pvName+" is currently jolly"
			
		
    def rebind(self,vcCallback):
        return 1
    def reconnect(self):
        return 1
    def destroy(self):
        #print self.pvName+' wird zerstoert'
        return 1
# Cache Channels!
CachedChannels={}
def RoboEpicsChannel(pvName,verbose=0,asString=0,vcCallback=None):
    # Provides a wrapper to the epics interface allowing for channel mapping and
    # easy switching into a debug mode

    if not CachedChannels.has_key(pvName):
        if MappedChannels.has_key(pvName):
            if type(MappedChannels[pvName])==type(''):
                CachedChannels[pvName]=RoboEpicsChannel(MappedChannels[pvName],verbose,asString,vcCallback)
            else:
                CachedChannels[pvName]=FakeRoboEpicsChannel(pvName,verbose,asString,vcCallback)
                CachedChannels[pvName].putVal(MappedChannels[pvName])
        else:
            if DebugMode<2:
                if EpicsWebMode==1:
                    CachedChannels[pvName]=WebServerRoboEpicsChannel(pvName,verbose,asString,vcCallback)
                else:
                    CachedChannels[pvName]=RealRoboEpicsChannel(pvName,verbose,asString,vcCallback)
            else:
                CachedChannels[pvName]=FakeRoboEpicsChannel(pvName,verbose,asString,vcCallback)
    return CachedChannels[pvName]
def ClearRECCache():
    print CachedChannels.keys()
    killEpicsWeb()
            
    for cName in CachedChannels.keys():
        CachedChannels[cName].chan.clear_channel()
        del(CachedChannels[cName].chan)
        del(CachedChannels[cName])
def RefreshRECCache():
    killEpicsWeb()
    if DebugMode<2:
        for cName in CachedChannels.keys():
            del(CachedChannels[cName].chan)
            CachedChannels[cName].reconnect()
def DisconnectRECCache(): # disconnects every channel from epics
    killEpicsWeb()
    if DebugMode<2:
        for cName in CachedChannels.keys():
            try:
                del(CachedChannels[cName].chan)
            except:
                print cName+' --'+str(dir(CachedChannels[cName]))
def ReconnectRECCache(): # reconnects every channel
    killEpicsWeb()
    if DebugMode<2:
        for cName in CachedChannels.keys():
            CachedChannels[cName].reconnect()
            
            
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
        self.RobotInterfaceMode=-1 # -1 means not yet loaded, 0 means off, 1 is running, 2 is read only
        self.initEpics()
        # Setup New Control Channel
        self._ctrlCode=socket.gethostname()+','
        self._ctrlCode+=''.join([choice('ADeEikMnRv') for i in range(len(self._ctrlCode),39)])
        if len(self._ctrlCode)>39:
            self._ctrlCode=self._ctrlCode[0:38]
        stillInUse=False
        if self.controlKeyCH.getVal()!='':
            stillInUse=True
            
            # if it is not empty then it wasnt properly dumped last time, wait 10s
        self.controlKeyCH.putVal(self._ctrlCode)
        self.RobotInterfaceMode=1
        if stillInUse:
            print 'Tomcat Robot was not properly closed last time, or is currently running'
            time.sleep(10)

        if not globals().has_key('tomcatRobotLock'):
            globals()['tomcatRobotLock']=roboLock() # make robot single threaded
        time.sleep(randrange(0,2))
        self.VerifyControlKey()
    def Enable(self):
        globals()['tomcatRobotLock'].enable()
        self.__init__(rChan=self.rChan,robotName=self.robotName,verbose=self.verbose)
    def Disable(self):
        self.controlKeyCH.putVal('')
        globals()['tomcatRobotLock'].disable()
    def TempAusdrucke(self,chName,newVal,oldVal):
        print chName+' was changed from '+str(oldVal)+' to '+str(newVal)
    def VerifyControlKey(self):
        self.ControlChange('Validate CTRLKEY ',self.controlKeyCH.getVal(),'')
    def StageMotorChange(self,chName,newVal,oldVal):
        if newVal>0:
            print 'STAGE MOVING!'
        else:
            print 'STAGE STILL'
    def ControlChange(self,chName,newVal,oldVal):
        print chName+' was changed from '+str(oldVal)+' to '+str(newVal)
        print 'Robot is currently '+'un'*(not globals()['tomcatRobotLock'].locked())+'locked'
        if (newVal=='EXPERT'):
            curSleepTime=randrange(0,15)
            print 'TomcatRobot expert reset rand delay '+str(curSleepTime)
            time.sleep(curSleepTime)
            self.Enable()
            return 0
        if ((newVal!=self._ctrlCode) and (self.RobotInterfaceMode>0)):
            xWinMsg('Another Program has Taken over Control of the Robot')
            print 'Another Program has Taken over Control of the Robot'
            globals()['tomcatRobotLock'].disable()
            globals()['tomcatRobotLock'].force_acquire() # once this is acquired nothing can run
            print 'Robot Locked, to prevent further use'
            self.RobotInterfaceMode=2
        else:
            print 'Robot Unlocking'
            globals()['tomcatRobotLock'].enable()
            globals()['tomcatRobotLock'].release()
            print 'Robot Unlocked'

    def rPrint(self,cString):
        self.CurrentText=self.robotName+": "+cString
        if self.rChan=='':
            print self.CurrentText
        else:
            self.rChan.putVal(self.CurrentText)
    def initEpics(self):
        # Channel Used for Robot Ownership
        self.controlKeyCH=RoboEpicsChannel(self.robotName+":CTRLKEY",self.verbose)
        # Low Level Robot Communication
        self.startCH=RoboEpicsChannel(self.robotName+":LL-ST",self.verbose)
        self.rstatusCH=RoboEpicsChannel(self.robotName+":LL-STAT",self.verbose)
        self.stopCH=RoboEpicsChannel(self.robotName+":LL-STOP",self.verbose)
        self.sleepCH=RoboEpicsChannel(self.robotName+":LL-SLEEP",self.verbose)
        # Column in Python is a Row in VAL3
        # Row in Python is Sample in VAL3 
        self.setColCH=RoboEpicsChannel(self.robotName+":LL-SETR",self.verbose)
        self.setRowCH=RoboEpicsChannel(self.robotName+":LL-SETS",self.verbose)
        self.mountCH=RoboEpicsChannel(self.robotName+":LL-MNT",self.verbose)
        self.unlCH=RoboEpicsChannel(self.robotName+":LL-UNL",self.verbose)
        self.readyCH=RoboEpicsChannel(self.robotName+":LL-READY",self.verbose)
        self.modeCH=RoboEpicsChannel(self.robotName+":LL-MODE",self.verbose)
        self.curColCH=RoboEpicsChannel(self.robotName+':LL-CROW',self.verbose)
        self.curRowCH=RoboEpicsChannel(self.robotName+':LL-CSAMPLE',self.verbose)
        # Stage Communication
        self.unterwegsPCH=RoboEpicsChannel(self.robotName+":MT-UNTERWEGS.PROC",self.verbose)
        self.unterwegsCH=RoboEpicsChannel(self.robotName+":MT-UNTERWEGS",self.verbose,vcCallback=self.StageMotorChange)
        self.stageLockedCH=RoboEpicsChannel(self.robotName+":SM-READY",self.verbose)
        self.rotAxisBCH=RoboEpicsChannel('X02DA-ES1-SMP1:ROTYASTAT',self.verbose)
        self.rotAxisCH=RoboEpicsChannel('X02DA-ES1-SMP1:ROTYUSETP',self.verbose)
        self.stageLoadDistPCH=RoboEpicsChannel("X02DA-ES1-ROBO:SLD_DISTGO.PROC",self.verbose)
        self.stageImageDistPCH=RoboEpicsChannel("X02DA-ES1-ROBO:SIM_DISTGO.PROC",self.verbose)
        self.stageLoadDistCH=RoboEpicsChannel("X02DA-ES1-ROBO:SLD_DIST",self.verbose)
        self.stageImageDistCH=RoboEpicsChannel("X02DA-ES1-ROBO:SIM_DISTYV",self.verbose)
        self.loadPosCH=RoboEpicsChannel("X02DA-ES1-ROBO:SLD_LOAD.PROC",self.verbose)
        self.imagePosCH=RoboEpicsChannel("X02DA-ES1-ROBO:SIM_LOAD-GO.PROC",self.verbose)
    def checkloadpos(self):
        self.stageLoadDistPCH.putVal(1)
        time.sleep(0.3)
        return (self.stageLoadDistCH.getVal()<1.0)
    def checkimagepos(self):
        self.stageImageDistPCH.putVal(1)
        time.sleep(0.3)
        return (self.stageImageDistCH.getVal()<2)
    def mode(self):
        return self.modeCH.getVal().__int__()
    def mode_str(self,cMode=None):
        if cMode==None: cMode=self.mode()
        if cMode==self.ST_OFF: return 'Off'
        if cMode==self.ST_ON: return 'Unmounted'
        if cMode==self.ST_MNT: return 'Mounted'
        if cMode==self.ST_ERR_MNT: return 'Error Starting'
        if cMode==self.ST_ERR_MNT: return 'Error Mounting'
        if cMode==self.ST_ERR_UNMNT: return 'Error Unmounting'
        return str(cMode)
    def setMode(self,modeVal):
        return self.modeCH.putVal(int(modeVal))
    def ready(self):
        return self.readyCH.getVal().__int__()
    def ValidateRobot(self,dMode=None,dStagePos=None,dRow=None,dCol=None):
        # For validating the robots status
        # Mode is the mode of the robot system (off, unmounted, mounted, errors)
        # StagePos is either 0 - load, 1 - imaging
        # dRow is desired row
        # dCol is desired col
        fErrStr=[]
        if (dRow!=None or dCol!=None): self.updateCurrentPos()
        if dMode!=None:
            if self.mode()!=dMode:
                fErrStr.append('Mode should be '+self.mode_str(dMode)+', but is '+self.mode_str())
        if dStagePos!=None:
            if dStagePos==0:
                if not self.checkloadpos():
                    fErrStr.append('Stg is '+str(self.stageLoadDistCH.getVal())+' units away from load')
            if dStagePos==1:
                if not self.checkimagepos():
                    fErrStr.append('Error : Stg is '+str(self.stageImageDistCH.getVal())+' units away from image')
        if dRow!=None:
            if self.currentRow!=dRow:
                fErrStr.append('Error : Row should be '+str(dRow)+', but is '+str(self.currentRow))
        if dCol!=None:
            if self.currentCol!=dCol:
                fErrStr.append('Error : Col should be '+str(dCol)+', but is '+str(self.currentCol))
        return fErrStr

    def checkmotorstatus(self):
        if DebugMode<1:
            time.sleep(1.3) # give the motors time to start moving
            while (self.stageMoving()):
                print 'Stage Moving!'
                time.sleep(0.75)
        else:
            #print 'Waiting for fake motors'
            time.sleep(1)
    def stageMoving(self):
        self.unterwegsPCH.putVal(1)
        stageMotors=(abs(self.unterwegsCH.getVal().__int__())>0)
        return (stageMotors) #or (self.rotAxisBCH.getVal())
    def MoveStageToLoadingPos(self,trys=1):
        self.loadPosCH.putVal(1)
        time.sleep(0.25)
        while not self.checkloadpos(): # wait for positions to be sent
            time.sleep(0.1)
            print 'Error : Stage isnt taking Loading Position!!'
            self.loadPosCH.putVal(1)
        time.sleep(0.5) # wait for motors to start moving
        self.checkmotorstatus()
        if not self.checkloadpos(): # wait for positions to be sent
            time.sleep(0.1)
            print 'Error : Stage Did NOT Move to Loading Position!!, Try '+str(trys)
            self.MoveStageToLoadingPos(trys+1)
    def updateCurrentPos(self):
        self.currentRow=self.curRowCH.getVal()
        self.currentCol=self.curColCH.getVal()
    def protectedLaunch(self,callback,args=None): # args and bund are the same
        # protectedLaunch serves to run the command and handle the locks and timeouts
        if globals()['tomcatRobotLock'].acquire():
            rtVal=callback.__call__(args)
            globals()['tomcatRobotLock'].release()
        else:
            print 'Error : Timeout or robot disabled, command will not be executed!'
            rtVal=-787551438 # this value means the command was never run
        return rtVal
    def stop(self):
        # Does not bother to acquire or release channels
        if self.stopCH.binaryClick():
            self.status=self.ST_OFF
        #self.protectedLaunch(self.__stop)
    def __stop(self,bund):
        globals()['tomcatRobotLock'].acquire()
        if self.stopCH.binaryClick():
            self.status=self.ST_OFF
        globals()['tomcatRobotLock'].release()
        return self.status
    def WaitLockStage(self):
        bTime=time.time();
        self.stageLockedCH.putVal(1) # locks stage and enables robot
        time.sleep(0.75)
        while self.stageLockedCH.getVal()<1:
            time.sleep(0.5)
            self.stageLockedCH.putVal(1)
            if (time.time()-bTime)>120:
                print 'Locking Error : Robot Timeout, Disabling (Robot Still Ready)'
                self.stageLockedCH.putVal(1) # free stage and disables robot
                time.sleep(0.1)
        # Not required when using old (2.4) version of Stream which uses old Asyn
        #self.sleepCH.putVal(1) # first command is just to reset the Asyn Device
        # as unlocking the stage stops the robot
        time.sleep(1)
    def WaitUnlockStage(self):
        bTime=time.time();
        while self.readyCH.getVal()>0:
            time.sleep(1.0)
            if (time.time()-bTime)>20:
                print 'Unlocking Error : Missed the Ready Drop, Continuing as if everything were normal'
                self.stageLockedCH.putVal(0) # free stage and disables robot
        bTime=time.time();
        while self.readyCH.getVal()<1:
            time.sleep(0.5)
            if (time.time()-bTime)>120:
                print 'Error : Robot Timeout Task Took over 120 seconds, Disabling and Continuing'
                #self.stageLockedCH.putVal(0) # free stage and disables robot
        
        self.stageLockedCH.putVal(0) # free stage and disables robot
	time.sleep(0.5)
    def GotoImagePos(self):
        return self.protectedLaunch(self.__GotoImagePos)
    def __GotoImagePos(self,bund):
        self.imagePosCH.putVal(1)
        time.sleep(0.3)
        while not self.checkimagepos():
            time.sleep(0.3)
            self.imagePosCH.putVal(1)
    def start(self):
        return self.protectedLaunch(self.__start)
    def __start(self,bund):
        self.WaitLockStage() # locks stage and enables robot
        if self.startCH.binaryClick():
            self.WaitUnlockStage()
            self.status=self.ST_ON
        else:
            self.status=self.ST_ERR_START
            self.rPrint("Error Starting Robot")
        if DebugMode==2:
            self.modeCH.putVal(1)
            self.readyCH.putVal(1)
            self.unterwegsCH.putVal(0)
            self.curRowCH.putVal(-1)
            self.curColCH.putVal(-1)
        return self.status
    def __rawMount(self,bund):
        (col,row)=bund
        self.loadPosCH.putVal(1) # starts the stage moving to load position
        self.MoveStageToLoadingPos()
	mountOK=False
        if (self.mode()==self.ST_ON):
            self.WaitLockStage() # locks stage and enables robot
            mountOK=self.setSpot(col,row)
            print ('Setting Spot Status...',mountOK)
            if (self.mountCH.binaryClick()):
                self.WaitUnlockStage()
                self.status=self.ST_MNT
            else:
                print 'Error : Mounting Error, Stage Will Remain Locked!'
                self.status=self.ST_ERR_MNT
        elif (self.mode()==self.ST_OFF):
            print 'Error : Robot must be on in order to load!'
        elif (self.mode()==self.ST_MNT):
            print 'Error : Robot is already mounted, please unmount first'
        else:
            print 'Error : Robot status is currently :'+str(self.mode())+', indicating an error, ensure everything is normal and then reset the robot and epics'
        return mountOK & self.status
    def mount(self,col,row):
        mountOK=self.protectedLaunch(self.__rawMount,(col,row))
        if mountOK!=-787551438:
            return  mountOK & self.waitReady(.5)
        else:
            return mountOK
    def setSpot(self,col,row):
        cmdFeedback=(self.setColCH.rPutVal(col) & self.setRowCH.rPutVal(row))
	time.sleep(0.7)
        self.updateCurrentPos()
        return ((self.currentRow==row) & (self.currentCol==col))

    def rawUnload(self):
        return self.protectedLaunch(self.__rawUnmount)
    def __rawUnmount(self,bund):
        self.MoveStageToLoadingPos()
        if (self.mode()==self.ST_MNT):
            self.WaitLockStage() # locks stage and enables robot
            
            if (self.unlCH.binaryClick()):
                self.status=self.ST_ON
                self.WaitUnlockStage()
            else:
                print 'Error : Unmounting Error, Stage Will Remain Locked!'
                self.status=self.ST_ERR_UNMNT
        else:
            self.rPrint("Error : Must have sample mounted to unmount! Mode:"+str(self.mode()))
        return self.status
    def unload(self):
        umountOK=self.rawUnload()
        if umountOK!=-787551438:
            return  umountOK & self.waitReady(.5)
        else:
            return umountOK
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
    def waitReady(self,minTime=0,maxTime=-1):
        tCount=minTime*4
        time.sleep(minTime)
        while ((self.readyCH.getVal()<1)):
            time.sleep(0.25)
            tCount+=1
            if ((maxTime>0) & (tCount>=maxTime*4)):
                self.rPrint("Error : Time Exceeded!")
                return 0
        return 1

class roboLock:
    def __init__(self,timeout=50): # timeout is 50 seconds
        self.__lock__=thread.allocate_lock()
        self.__aqlock__=thread.allocate_lock()
        self.__enabled__=True
        self._ignore_=IGNORELOCKS
        self.timeout=timeout
    def acquire(self):
        if self._ignore_: return 1
        sTime=time.time()
        if not self.__enabled__:
            print 'Robot has been disabled!'
            return 0
        self.__aqlock__.acquire() # only one task can be acquiring at a time
        while self.__lock__.locked():
            time.sleep(0.05)
            if (time.time()-sTime)>self.timeout:
                self.__aqlock__.release()
                return 0
        self.__lock__.acquire()
        self.__aqlock__.release()
        return 1
    def force_acquire(self):
        if self._ignore_: return 1
        self.__lock__.acquire()

    def release(self):
        if self._ignore_: return 1
        if not self.__enabled__:
            print 'Robot has been disabled!'
            return 0
        if self.__lock__.locked():
            self.__lock__.release()
        else:
            print 'Lock already released!'
        return 1
    def locked(self):
        if self._ignore_: return 0
        return self.__lock__.locked()
    def enable(self):
        self.__enabled__=True
    def disable(self):
        self.__enabled__=False
            
        


def pickleSave(cStr):
    fLength=38
    startChar=range(0,len(cStr),fLength)
    nVar=RoboEpicsChannel('X02DA-ES1-ROBO:GUI-PICKLECNT')
    lEndChar=0
    for i in range(0,len(startChar)):
        cVar=RoboEpicsChannel('X02DA-ES1-ROBO:GUI-PICKLE'+str(i))
        cVar.putVal(cStr[startChar[i]:startChar[i]+fLength])
        nVar.putVal(i)
        lEndChar=startChar[i]+fLength
    cVar=RoboEpicsChannel('X02DA-ES1-ROBO:GUI-PICKLE'+str(len(startChar)))
    cVar.putVal(cStr[lEndChar:])
    nVar.putVal(len(startChar))
    
def pickleRead(mOver=0):
    nVar=RoboEpicsChannel('X02DA-ES1-ROBO:GUI-PICKLECNT')
    cStr=''
    for i in range(0,int(nVar.getVal())):
        cVar=RoboEpicsChannel('X02DA-ES1-ROBO:GUI-PICKLE'+str(i))
        cStr+=cVar.getVal()
    return cStr 

class EpicsServerHttpHandler(BaseHTTPRequestHandler):
    def decodepath(self):
        d = {}
        myCmd=self.path[1:]
        myArgs=myCmd.split('?')[1:]
        a=[]
        if len(myArgs)>0: a=myArgs[0].split('&')
        for s in a:
            if s.find('='):
                k,v = map(urllib.unquote, s.split('='))
                try:
                    d[k].append(v)
                except KeyError:
                    d[k] = [v]
        return d

    def do_GET(self):
        try:
            self.send_response(200)
            self.send_header('Content-type',	'text/html')
            self.end_headers()
            
            myCmd=self.path[1:]
            myArgs=self.decodepath()
            isLocalHost=(self.client_address[0]=='127.0.0.1')
            if myCmd.startswith("GET_INFO"):
                infoStr='<html><body>EpicsWebServer Version:'+str(RCVersion)+'<br>Kevin Mader (kevin.mader@psi.ch)'
                infoStr+='<br>Your IP:'+str(self.client_address[0])
                infoStr+='<hr>Cached Channels<br><table><tr><td>Name</td><td>Current Value</td><td>Idle Time</td></tr>'
                for dChan in CachedChannels:
                    try:
                        infoStr+='<tr><td>'+dChan+'</td><td>'+str(CachedChannels[dChan].curValue)+'</td><td>'+str(time.time()-CachedChannels[dChan].lastPoll)+'s</td></tr>'
                        
                    except:
                        infoStr+='<tr><td>'+dChan+'</td><td>Error!</td><td></td></tr>'
                infoStr+='</table>'
                infoStr+='<hr>Mapped Channels<br><table><tr><td>Alias</td><td>Channel Name</td></tr>'
                
                for dChan in MappedChannels:
                    try:
                        infoStr+='<tr><td>'+dChan+'</td><td>'+str(MappedChannels[dChan])+'</td></tr>'
                        
                    except:
                        infoStr+='<tr><td>'+dChan+'</td><td>Error!</td></tr>'    
                infoStr+='</table>'    
                self.wfile.write(infoStr)
                return
            if myCmd.startswith("GET_EPICS_PICKLE"):
                outDict={}
                for cArg in myArgs.keys():
                    tempChan=RoboEpicsChannel(cArg)
                    outDict[cArg]=tempChan.getVal()
                self.wfile.write(urllib.quote(dumps(outDict)))
                return
            if myCmd.startswith("PUT_EPICS_PICKLE"):
                
                outDict={}
                for cItem in myArgs.keys():
                    try:
                        if isLocalHost:
                            tempChan=RoboEpicsChannel(cItem)
                            tempChan.rPutVal(myArgs[cItem][0])
                            outDict[cItem]='GOOD'
                        else:
                            outDict[cItem]='NOT-LOCAL-HOST'
                    except:
                        outDict[cItem]='FAIL'
                self.wfile.write(urllib.quote(dumps(outDict)))
                
            elif myCmd.find(".htm")>-1:
                self.wfile.write(self.path+'<br> ich verstoh ned ganz <br> i cha ned ihne holfe')
                return
            
            elif myCmd.endswith(".esp"):   #our dynamic content
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write("hey, today is the" + str(time.localtime()[7]))
                self.wfile.write(" day in the year " + str(time.localtime()[0]))
                return
                
            return
                
        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)
def EpicsWebServer():
    try:
        server = HTTPServer(('', globals()['EpicsWebPort']), EpicsServerHttpHandler)
        print 'started EpicsHttpServer...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()
if DoLaunchWebServer:
    # Sloppy, used to keep webserver below all other definitions
    #tempVal=RoboEpicsChannel('X02DA-ES1-ROBO:GUI-STAT')
    #print tempVal
    #print tempVal.getVal()
    EpicsWebServer()
       
class stageJumpPos:
    def __init__(self,prnt,rPos=wx.Point(0,0),label='Dummy',vMin=0,vMax=100,jumpSize=0.02,vStart=50):
        self.ctrlFocus={}
        self.parent=prnt
        self.jumpSize=jumpSize
        rOffset=rPos-wx.Point(152,40)
        self.staticBox1 = wx.StaticBox(label=label,
              name='staticBox1', parent=prnt,
              pos=wx.Point(152, 40)+rOffset, size=wx.Size(152, 88), style=0)
        self.staticBox1.SetMinSize(wx.Size(-1, -1))  
        self.slider1 = wx.Slider(maxValue=vMax,
              minValue=vMin, name='slider1', parent=prnt, pos=wx.Point(160, 80)+rOffset,
              size=wx.Size(136, 24), style=wx.SL_HORIZONTAL, value=vStart)
        self.textCtrl1 = wx.TextCtrl(
              name='textCtrl1', parent=prnt, pos=wx.Point(160, 56)+rOffset,
              size=wx.Size(120, 24), style=0, value=str(vStart))

        self.spinButton1 = wx.SpinButton(name='spinButton1', parent=prnt, pos=wx.Point(280, 56)+rOffset,
              size=wx.Size(15, 26), style=wx.SP_HORIZONTAL)
        self.spinButton1.SetRange(-65535,65535)
        # wx.SP_HORIZONTAL
        self.textCtrl2 = wx.TextCtrl(
              name='textCtrl2', parent=prnt, pos=wx.Point(200, 96)+rOffset,
              size=wx.Size(96, 24), style=0, value=str(.05*(vMax-vMin)))

        self.staticText1 = wx.StaticText(
              label=u'Step', name='staticText1', parent=prnt, pos=wx.Point(168,
              96)+rOffset, size=wx.Size(29, 17), style=0)
        self.slider1.Bind(wx.EVT_SCROLL_THUMBTRACK,
              self.OnSlider1ScrollThumbtrack)
        
        self.textCtrl1.Bind(wx.EVT_SET_FOCUS,self.setFocus)
        self.textCtrl1.Bind(wx.EVT_KILL_FOCUS,self.killFocus)
        self.slider1.Bind(wx.EVT_SET_FOCUS,self.setFocus)
        self.slider1.Bind(wx.EVT_KILL_FOCUS,self.killFocus)
        self.textCtrl1.Bind(wx.EVT_TEXT_ENTER, self.OnTextCtrl1TextEnter)
        self.spinButton1.Bind(wx.EVT_COMMAND_SCROLL_LINEUP,
              self.OnSpinButton1Up)
        self.spinButton1.Bind(wx.EVT_COMMAND_SCROLL_LINEDOWN,
              self.OnSpinButton1Down)
        self.Min=vMin
        self.Max=vMax
        self.deltaVal=0
        
        self.actuel = wx.TextCtrl(
              name='actuel', parent=prnt, pos=wx.Point(160, 56)+rOffset,
              size=wx.Size(0, 0), style=0, value=str(vStart))
    def Bind(self,evt,fcn):
        self.actuel.Bind(evt,fcn)
    def Enable(self,stat):
        self.actuel.Enable(stat)
        self.spinButton1.Enable(stat)
        self.slider1.Enable(stat)
        self.textCtrl1.Enable(stat)
        self.staticBox1.Enable(stat)
    def GetParent(self):
        return self.parent
    def GetToolTip(self):
        return self.textCtrl1.GetToolTip()
    def SetToolTipString(self,stv):
        self.staticBox1.SetToolTipString(stv)
        return self.textCtrl1.SetToolTipString(stv)
    def SetRange(self,minVal,maxVal):
        self.SetMin(minVal)
        self.SetMax(maxVal)
    def SetMin(self,mVal):
        if mVal>self.slider1.GetMax():
            self.slider1.SetMax(mVal+1)
        if mVal>self.slider1.GetValue():
            self.slider1.SetValue(mVal)
        self.slider1.SetMin(mVal)
        self.Min=mVal
    def SetMax(self,mVal):
        #print str(self.Min)+' -> '+str(mVal)
        if mVal<=self.Min:
            self.slider1.SetMax(128000)
            self.slider1.SetMin(-128000)
            self.Min=-128000
            self.Max=128000
            self.slider1.SetForegroundColour('red')
            self.slider1.SetBackgroundColour('red')
        else:
            if mVal<self.slider1.GetValue():
                self.slider1.SetValue(mVal)
            self.slider1.SetMax(mVal)
            self.Max=mVal
            self.textCtrl2.SetValue(str(self.jumpSize*(self.Max-self.Min)))
    def GetValue(self):
        return float(self.textCtrl1.GetValue())
    def SetColor(self,nVal):
        if nVal==1:
            self.staticBox1.SetForegroundColour('black')
        else:
            self.staticBox1.SetForegroundColour('green')
    def SetValue(self,ttVal):
        if sum(self.ctrlFocus.values())<1:
            tVal=ttVal
            if abs(self.deltaVal)>0:
                tVal+=self.deltaVal
                self.deltaVal=0
                pControl=1
            else:
                pControl=0
            if tVal>self.slider1.Max:
                self.SetMax(tVal+1)
            if tVal<self.slider1.Min:
                self.SetMin(tVal-1)
            self.iSetValue(tVal)
            if pControl:
                self.PostControl()
    def iSetValue(self,tVal):
        #print dir(self.slider1)
        if tVal>self.slider1.GetMax():
            val=self.slider1.GetMax()
        elif tVal<self.slider1.GetMin():
            val=self.slider1.GetMin()
        else:
            val=tVal  
        self.textCtrl1.SetValue(str(val))
        #self.actuel.SetValue(str(val))
        self.slider1.SetValue(val)

    def PostControl(self):
        if self.parent.mainPtr==-1:
            print 'demo mode'
        else:
            self.parent.mainPtr.kPostEvent('pushControlVal',[self.GetToolTip().GetTip(),self.GetValue()])
    def PostDelta(self,val):
        self.deltaVal+=val        
    def OnSlider1ScrollThumbtrack(self, event):
        self.textCtrl1.SetValue(str(self.slider1.GetValue()))
        self.PostControl()
        event.Skip()

    def OnTextCtrl1TextEnter(self, event):
        self.iSetValue(self.GetValue())
        self.PostControl()
        event.Skip()

    def OnSpinButton1Up(self, event):
        self.PostDelta(float(self.textCtrl2.GetValue()))
        #self.iSetValue(self.GetValue()+float(self.textCtrl2.GetValue()))
        #self.PostControl()
        event.Skip()

    def OnSpinButton1Down(self, event):
        self.PostDelta(-float(self.textCtrl2.GetValue()))
        #self.iSetValue(self.GetValue()-float(self.textCtrl2.GetValue()))
        #self.PostControl()
        event.Skip()
    def setFocus(self,event):
        self.ctrlFocus[event.GetEventObject()]=1
    def killFocus(self,event):
        self.ctrlFocus[event.GetEventObject()]=0
