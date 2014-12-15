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
from threading import Thread
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

#-------------------------CaChannel import--------------------------------------------------
try:
  from CaChannel import *
except:
  try:
    sys.path.insert (0, os.path.expandvars ("$SLSBASE/sls/lib/python22/CaChannel"))
    from CaChannel import *
  except:
    os.system ("xkbbell")
    os.system ("xmessage -nearmouse -timeout 30 -buttons '' CaChannel module cannot be found")
    sys.exit (1)
  #endtry
#endtryX_ROBOT_X02DA_lowlevel-cmd.template

from CaChannel import CaChannelException

#-------------------------Epics Channel Class--------------------------------------------------

class EpicsChannel:
    def __init__(self,pvName):
        self.pvName=pvName
	if ((self.pvName.upper().find("ROBO")<0) & DebugMode):
		print "Variable "+pvName+" affects beamline and will not be altered"
	
        try:
            self.chan=CaChannel()
            self.chan.search(self.pvName)
            self.chan.pend_io()
            self.connected=1
        except CaChannelException, status:
            print ca.message(status)
            self.connected=0

    def getVal(self):
        try:
                val=self.chan.getw()
        except:
                self.connected=0
                val=""
        return val

    #def getValCHK(self, connected):X_ROBOT_X02DA_lowlevel-cmd.template
    #    if connected==1:
    #        return self.getVal()
    #    else:
    #        self.reconnect()

    def putVal(self,val):
        try:
		if ((self.pvName.upper().find("ROBO")<0) & DebugMode):
			print "Debug Mode Enabled, thus "+self.pvName+" not altered"
		else:
			self.chan.putw(val)
        except:
            self.connected=0

    def putValCHK(self, val, connected):
        if connected==1:
            self.putVal(val)
        else:
            self.reconnect()

    def reconnect(self):
        try:
            self.chan=CaChannel()
            self.chan.search(self.pvName)
            self.chan.pend_io()
            self.connected=1
        except CaChannelException, status:
            print ca.message(status)
            self.connected=0      
  
      
#-------------------------the connection from python/epics----------------------------------


    


# Debug Mode as in not on the actual beamline (only can write robo variables) 
DebugMode=1


