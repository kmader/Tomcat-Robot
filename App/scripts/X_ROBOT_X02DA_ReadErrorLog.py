#!/usr/bin/env python
#Boa:PyApp:main
# Read Logs for Errors by Kevin Mader
# 19 August 2009
# Reads through the Robot_Logs directory and looks for errors
import glob
import sys,os
from optparse import OptionParser
modules = {}

# Beginning of Real Program
optParse=OptionParser()
optParse.add_option('-d','--dir',dest='directory',default="Robot_Logs/",help='Directory to Search (default "Robot_Logs/")')
optParse.add_option('-c','--code',dest='ecode',default="Error",help='Error Code to Look For (Default "Error")')

optParse.set_description('Reads the log directory and scans for all the errors')

optParse.print_help()
(opt,args)=optParse.parse_args()

for cfile in os.listdir( os.path.expandvars ("$HOME/"+opt.directory+"/")):
    mcode=os.popen("cat "+os.path.expandvars ("$HOME/"+opt.directory+"/")+cfile+" | grep "+opt.ecode,'r')
    cerr=mcode.readlines()
    print cfile+' : '+str(len(cerr))+' Error(s)'
    print '\n\t'.join(cerr)
    