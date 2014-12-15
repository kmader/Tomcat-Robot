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
chGO=RoboEpicsChannel('X02DA-SCAN-SCN1:GO')
chAbsorber=RoboEpicsChannel('X02DA-FE-AB1:CLOSE4BL')
chInterlock=RoboEpicsChannel('X02DA-FE-AB1:ILK-STATE')
chRingCurrent=RoboEpicsChannel('ARIDI-PCT:CURRENT')

startCurrent=chRingCurrent.getVal()

def CHECKBEAMLINE():
	beamlineStatus=1
	while ((chInterlock.getVal()>0) or ((chRingCurrent.getVal()-startCurrent)/startCurrent>0.05):
		print "Beam is not ready!"
		beamlineStatus=0
		o
	if chAbsorber.getVal()<1:
		chAbsorber.putVal(1)
		beamlineStatus=0
