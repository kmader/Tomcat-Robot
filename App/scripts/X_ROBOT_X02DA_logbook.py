#!/usr/bin/env python
import sys
import os
import stat
import time
import string
from optparse import OptionParser

class __LoggingPipe__:
    def __init__(self,logFileName='script',dirName='Robot_Logs'):
        try:
            os.listdir( os.path.expandvars ("$HOME/"+dirName+"/"))
        except:
            os.mkdir( os.path.expandvars ("$HOME/"+dirName+"/"))
        
        self.logFileName=os.path.expandvars("$HOME/"+dirName+"/"+logFileName+".log")
        self.write('\n'+time.asctime()+':'+logFileName+' freshly started'+'\n',0)
    def write(self,myStr,indent=1):
        tFile=open(self.logFileName,'a+')
        tFile.write('\t'*indent+myStr)
        tFile.close()
# Code to write robot and recon logbooks
robotLogID='AAVTH9066B13409799AAD7F39107FB262D226'
try:
    UserId=os.path.expandvars('$USER')
    sys.path.insert (0, "/work/sls/bin/")
    import logbook
except:
    print 'Logbook.py Not properly installed'
LGVersion=20090601
print "Using X02DA Logbook Library Version : "+str(LGVersion)+" with user:"+UserId

_loginSchonGelesen=0
benutzer=[]
passwort=[]
gruppeid=[]
def requestCredentials():
    from tkSimpleDialog import askstring
    from tkMessageBox import askyesno
    stillMore=askyesno('X02DA LogBook Interface','; '.join(globals()['benutzer'])+' have already been added, add another?')
    while stillMore:
        username=string.strip(askstring('Duo Information','DUO Username?'))
        password=string.strip(askstring('Duo Information','DUO Password?'))
        #groupid=tkSimpleDialog.askstring('Duo Information','DUO Group-Id?')
        #if groupid=='': 
        groupid='0'
        if logbook.testConn(username,password,groupid)==0:
            globals()['benutzer'].append(username)
            globals()['passwort'].append(password)
            globals()['gruppeid'].append(groupid)
            globals()['_loginSchonGelesen']=1
            _writeLogin(username,password,groupid)
        else:
            print 'Password Failed!'
        # insert dialog with current users and add another?
        stillMore=askyesno('X02DA LogBook Interface','; '.join(globals()['benutzer'])+' have already been added, add another?')
    #del(tkSimpleDialog.Tk)
def _clearLogin():
    f=open(os.environ['HOME']+"/.tomcatlogbook","w")
    f.write('')
    f.close()    
def _writeLogin(user,password,groupid):
    try:
        f=open(os.environ['HOME']+"/.tomcatlogbook","a+")
        f.write(user+","+password+","+groupid+"\n")
        f.close()
        os.chmod( os.environ['HOME']+"/.tomcatlogbook", stat.S_IWUSR|stat.S_IRUSR )
        return 1
    except:
        print 'Login Information Not Written Successfully!'
        return 0
def _readLogin():
    try:
        f=open(os.environ['HOME']+"/.tomcatlogbook","r")
        gString=' '
        while len(gString)>0:
            gString=string.strip(f.readline())
            try:
                gArr=gString.split(',')
                user=string.strip(gArr[0])
                password=string.strip(gArr[1])
                groupid=string.strip(gArr[2])
                if logbook.testConn(user,password,groupid)==0:
                    globals()['benutzer'].append(user)
                    globals()['passwort'].append(password)
                    globals()['gruppeid'].append(groupid)
                    globals()['_loginSchonGelesen']=1
            except:
                print gString+' not valid!'
        f.close()
        
    except:
        print 'Read Login Failed!'
        
def writeReconLog(logbookName,logbookText,priorCode='N'):
    writeEntry(logbookName,logbookText,logBookId='56',priorCode=priorCode)
def writeEntry(logbookName,logbookText,imageName='',logBookId='54',priorCode='N'):
    # Logbook Id (54=Robot Log, 56=Reconstruction Log)
    dtStr=time.strftime("%d/%m/%Y %H:%M",time.localtime(time.time()))
    if len(imageName)>0:
        f=open(imageName,'r')
        imagedata=f.read()
        print len(imagedata)
        f.close()
    else:
        imagedata=''    
    try:
        logbook.addEntry(robotLogID,'',logBookId,dtStr,priorCode,logbookName,logbookText)
        if len(imageName)>0:
            logbook.addAttachement(robotLogID,'',logbookName,imageName,imagedata)
    except:
        print 'Error writing robot log!'
    if globals()['_loginSchonGelesen']<1:
        _readLogin()
    if globals()['_loginSchonGelesen']==1:
        for cDex in range(0,len(globals()['benutzer'])):
            user=globals()['benutzer'][cDex]
            try:
                password=globals()['passwort'][cDex]
                groupid=globals()['gruppeid'][cDex]
                logbook.addEntry(user,password,groupid,dtStr,priorCode,logbookName,logbookText)
                if len(imageName)>0:
                    logbook.addAttachement(user,password,'IMG'+logbookName,imageName,imagedata)
            except:
                print 'Error writing to user log for '+user+'!'
    else:
        print 'User Log has not yet been defined!'
def logbook_main():
    optParse=OptionParser()
    optParse.add_option('-r','--request',action='store_true',dest='reqcred',help='GUI for getting DUO name and password',default=False)
    optParse.add_option('-n','--new',dest='scanfile',help='Create a new entry using this file as a basis')
    optParse.add_option('-c','--clear',action='store_true',dest='clear',help='Clear old login file',default=False)
    optParse.add_option('-L','--LOG',action='store_true',dest='log',help='Pump screen output to a log',default=False,metavar='LOG')

    optParse.set_description('This is the interface to the DUO Logbook, for tracking samples, beamline, and roboter usage')
    (opt,args)=optParse.parse_args()
    _readLogin()
    if opt.log:
        newPipe=__LoggingPipe__('logbook')
        globals()['sys'].stdout=newPipe
        globals()['sys'].stderr=newPipe
    print globals()['benutzer']
    if opt.reqcred:
        requestCredentials()
    if opt.scanfile is not None:
        writeEntry('KTest2','Junker',opt.scanfile)
    if globals()['_loginSchonGelesen']<1:
        requestCredentials() 
    if opt.clear:
        _clearLogin()
if __name__ == '__main__':
    logbook_main()