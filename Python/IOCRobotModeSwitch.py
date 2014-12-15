#! /usr/bin/env python
# The function designed to manage the robot softwares connection with the actual beamline
# List of changes automatically made
# X02DA-PC-ROBO_robot.subs :
#	under file X_ROBOT_X02DA_lowlevel...
#	change ES to ROBO   and   X02DA-ES1 to X02DA-ES1-ROBO
#	 Ex: The lowlevel never actually addresses anything but the robot so the template should be directly
#	     to the robot
#
# X_ROBOT_X02DA_lowlevel-cmd.template :
#	Find and replace : Find = $(ES)-ROBO    Replace = $(ROBO) 	
import sys
import re

# function definitions
def show_help():
	print "IOCRobotModeSwitch.py (28.10.08, Kevin Mader)"
        print "ABOUT"
        print " This program makes the changes to the subs file for the TOMCAT Robot"
	print " this allows for the robot to be tested without interfering with the"
	print " actual beamline"
        print "USAGE"
        print "Input parameters"
        print "   $1  = Debug mode (0 or 1)"
	print "	  $2  = Path (default is current directory)"
	

        print ""
        sys.exit(0)

def intArgv(i):
        try:
                return int(sys.argv[i])
        except:
                print "Parameter "+str(i)+" : is not an integer!"
                show_help()
                sys.exit(1)
basePath='../' #default assume code is in python directory ala subdirectory of actual subs file
if len(sys.argv)>2:
	basePath=sys.argv[2]


subs1=basePath+'X02DA-PC-ROBO_robot.subs'



# automatic changes to the subs file
f=open(subs1,'r');
d=f.read()
f.close()
lowlevelSearch=re.compile('ES\s*=\s*X02DA-ES1')
d=lowlevelSearch.sub('ROBO = X02DA-ES1-ROBO',d)
# mode sensitive changes to the subs file
dbgStr=('# robot control templates for ROBO at X02DA','#DEBUG robot control templates for ROBO at M02DA')
smpStr=('X02DA-ES1-SMP1','M02DA-ES1-SMP1')
debugSearch=re.compile(dbgStr[1]) # search for debug line
if debugSearch.search(d):
	oldMode=1 # debug mode
else:
	oldMode=0 #normal mode


newMode=intArgv(1) # read the desired mode
smpSearch=re.compile(smpStr[oldMode])
d=smpSearch.sub(smpStr[newMode],d)
debugSearch=re.compile(dbgStr[oldMode])
d=debugSearch.sub(dbgStr[newMode],d)

f=open(subs1,'w')
f.write(d)
f.close()

	



