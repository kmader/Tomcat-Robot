#! /usr/bin/env python

#-------------------------Import libraries---------------------------------------------------
import sys
import os
import time
from optparse import OptionParser


optParse=OptionParser()
optParse.add_option('-p','--phone',dest='newcell',help='Phone number to send an SMS to in event of problem',default='')
optParse.add_option('-s','--scan',dest='scantime',help='Max Scan Time in minutes (Current: '+str(timeForScan)+')',default=timeForScan)
optParse.add_option('-r','--robot',dest='switchtime',help='Max Exchange (Robot) Time in minutes (Current: '+str(timeForSwitch)+')',default=timeForSwitch)
optParse.add_option('-d','--dead',dest='deadtime',help='Time to not send sms after one has been sent minutes (Current: '+str(afterTextDeadTime)+')',default=afterTextDeadTime)
optParse.add_option('-n','--noscript',action='store_true',dest='noscript',help='Is the sequencer script running on another computer? (otherwise it will be checked using ps)',default=False)
optParse.set_description('This program babysits the tomcat script\nand will send an sms when something takes more time than it should')

optParse.print_help()
(opt,args)=optParse.parse_args()
timeForScan=float(opt.scantime)*60
timeForSwitch=float(opt.switchtime)*60
afterTextDeadTime=float(opt.deadtime)*60
if opt.noscript:
    lastScriptCheck+=1e9 # never check for script
