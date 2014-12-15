#!/usr/bin/env python
#Boa:PyApp:main
# Missing Slices by Kevin Mader
# 25 March 2009
# Missing slices searches through the directories matching sliceSearchList for reconstructions
# It then makes sure all the file names are sequential and prints a message when this is not so
import glob
import sys,os
sys.path.insert (0, os.path.expandvars ("$SLSBASE/sls/bin/"))
try:
    import X_ROBOT_X02DA_logbook
    logbookEnabled=1
except:
    print('Logbook has not been loaded successfully')
    logbookEnabled=0

modules ={}
projSearch='$HOME/*/*/*/tif/*.tif'
sliceSearchList=[]
sliceSearchList.append('$HOME/Data1/*/rec*/*.rec*')
sliceSearchList.append('$HOME/Data2/*/rec*/*.rec*')
sliceSearchList.append('$HOME/Data10/*/rec*/*.rec*')
sliceSearchList.append('$HOME/Data1/*/*/rec*/*.rec*')
sliceSearchList.append('$HOME/Data2/*/*/rec*/*.rec*')
sliceSearchList.append('$HOME/Data10/*/*/rec*/*.rec*')
isqSearchList=['$HOME/Data*/*/*/rec_ISQ']
isqStatusDict={}
isqStatusDict['.LCK']='Still Running'
isqStatusDict['.VERIFY']='verification running'
isqStatusDict['.ERROR']='Error During Conversion'
isqStatusDict['.MISSING;*']='Files not Readable From Disk'
isqStatusDict['.ERROR;*']='Error During Conversion'
isqStatusDict['.FAILED;*']='Verification Initialization Failed'
isqStatusDict['.CORRUPT;*']='Header is Corrupt'
isqStatusDict['.INVALID;*']='Data Missing'
isqStatusDict['.LIMITS;*']='Scaling Factor too large or low'
isqStatusDict['.SUSPECT;*']='Wrong Limits'
isqStatusDict['.VALID;*']='OK'

curSlices={}
def isOrdered(rN):
    r=rN
    r.sort()
    if r==range(min(r),max(r)+1):
        return (True,str(min(r))+'-'+str(max(r)))
    else:
        return (False,findMissingSlices(r))
def findMissingSlices(r):
    lastR=min(r)-1
    oStr=[]
    for i in r:
        if i==lastR:
            oStr.append('D'+str(i))
        elif i==(lastR+2):
            oStr.append(str(lastR+1))
        elif i>(lastR+2):
            oStr.append(str(lastR+1)+'-'+str(i-1))
        lastR=i
    return ';'.join(oStr)
def addValidSlice(qE):
    try:
        qStart=qE.rfind('/')+1
        qStart=0 # include whole path
        qEnd=qE.find('.rec')
        qAll=qE[qStart:qEnd]
        qI=int(qAll[-4:])
        qS=qAll[:-4]
        if not curSlices.has_key(qS):
            curSlices[qS]=[]
        curSlices[qS].append(qI)
    except:
        addValidSliceThree(qE)
def addValidSliceThree(qE):
    # this function is for files with only 3 digits
    try:
        qStart=qE.rfind('/')+1
        qStart=0 # include whole path
        qEnd=qE.find('.rec')
        qAll=qE[qStart:qEnd]
        qI=int(qAll[-3:])
        qS=qAll[:-3]
        if not curSlices.has_key(qS):
            curSlices[qS]=[]
        curSlices[qS].append(qI)
    except:
        print qE+' isnt valid'
def postLogbook(logbookName,logbookText,pCode): 
        logbookText='Tomcat MS Script:\n'+os.path.expandvars('$HOME')+'\n'+logbookText
        if logbookEnabled:
            X_ROBOT_X02DA_logbook.writeReconLog(logbookName,logbookText,pCode)
def main():
    logbookText='' 
    logbookName=''
    UserId=os.path.expandvars('$USER') 
    for sliceSearch in sliceSearchList:
        sDir=os.path.expandvars(sliceSearch)
        nList=glob.glob(sDir)
        nList.sort()
        map(addValidSlice,nList)

    dFail=0
    for cKey in curSlices.keys():
        (isR,isTxt)=isOrdered(curSlices[cKey])
        sampleName=cKey[cKey.rfind('/')+1:]
        if isR:
            print 'Valid : '+sampleName+' : '+isTxt
            logbookText+='Valid : '+cKey+'\n'
        else:
            print '!!!MISSING SLICES!!!'
            print '\t'+cKey
            print '\t\t'+isTxt
            logbookText+='Missing Slices :\n'+cKey+', Slice#: '+isTxt+'\n'
            dFail+=1
    for isqSearch in isqSearchList:
        isDir=os.path.expandvars(isqSearch)
        isnList=glob.glob(isDir)
        isnList.sort()
    if len(isnList)>0:
        print 'ISQ Reconstruction Status!!!'
    for cqDir in isnList:
        cqDirList=glob.glob(cqDir+'/*;*')
        maxVer=-1
        for nFile in cqDirList:
            tName=nFile.split(';')
            cVer=int(tName[1])
            if cVer>maxVer:
                maxVer=cVer
        cqDirList=glob.glob(cqDir+'/*')
        for nFile in cqDirList:
            for cDictItem in isqStatusDict.keys():
                cDist2=str(maxVer).join(cDictItem.split('*'))
                if nFile.find(cDist2)>-1:
                    print isqStatusDict[cDictItem]+' : '+nFile
        
    if dFail>0:
        print str(dFail)+' sample(s) are missing slices! Please Resolve!!'
        logbookName='Missing Slices : '+UserId
        pCode='C'
    else:
        print 'All Samples Appear to be OK'
        logbookName='OK : '+UserId
        pCode='N'
    postLogbook(logbookName,logbookText,pCode)
    if pCode=='C':
        os.system('/work/sls/bin/X_ROBOT_X02DA_sendEmail.pl andreas.isenegger@psi.ch "'+logbookName+'"')
    pass

if __name__ == '__main__':
    main()
