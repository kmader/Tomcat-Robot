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
import thread
import pickle
from X_ROBOT_X02DA_robotScript import *
class cmdSequence:
    def __init__(self,debugMode):
        self.myRobotScript=RobotScript(debugMode=debugMode,expertPresent=0)
        self.scriptText=''
def show_help():
	print "TomcatRobot CommandLine Sequencer (27.11.08, Kevin Mader)"
        print "ABOUT"
        print " This program coordinates and executes sequences on the tomcat robot"
	print " this allows after alignment complicated procedures to be conducted"
        print "USAGE"
        print "Input parameters"
	print "	  $1  = File to Execute"
	print "	  $2  = Operation Mode"
debugMode=0
guiMode=0
if len(sys.argv)>1:
	sequenceFile=sys.argv[1]
else:
	import tkFileDialog
	fileWin=tkFileDialog.Open()
	fileWin.show()
	sequenceFile=fileWin.filename
if len(sys.argv)>2:
    if sys.argv[2].strip().upper()=='GUI':
        guiMode=1
    elif sys.argv[2].strip().upper()=='DEBUG':
        debugMode=1
    elif sys.argv[2].strip().upper()=='GUIDEBUG':
        debugMode=1
        guiMode=1
    elif sys.argv[2].strip().upper()=='SHOWPANEL':
        thread.start_new_thread(os.system,('medm -x /work/sls/config/medm/X_ROBOT_X02DA_robotSequencer.adl',))
cmdClass=cmdSequence(debugMode)
fileType=1
try:
	sFileIn=open(sequenceFile,'rb')
	(version,bundle)=pickle.load(sFileIn)
	fileType=1
	sFileIn.close()
except:
	sFileIn.close()
	cmdClass.myRobotScript.loadFile(sequenceFile)
	fileType=0
if fileType==1:
    (junk,junk2,scriptText,scriptDict)=bundle
    cmdClass.myRobotScript.loadText(scriptText,scriptDict)
	
cmdClass.myRobotScript.validateSequenceGUI()
if (cmdClass.myRobotScript.fatalError==0):
    if guiMode==0:
        cmdClass.myRobotScript.executeScript(dbDelay=0)
    else:
        cmdClass.scriptText=cmdClass.myRobotScript.sequenceText
        import wx,X_ROBOT_X02DA_guiSequencer
        class BoaApp(wx.App):
            
            def OnInit(self):
                self.main = X_ROBOT_X02DA_guiSequencer.create(globals()['cmdClass'])
                self.main.Show()
                self.SetTopWindow(self.main)
                return True
        
        bapp=BoaApp()
        #bapp.cmdClass=cmdClass
        bapp.MainLoop()
        #cmdClass.myRobotScript.executeScript(dbDelay=0)
