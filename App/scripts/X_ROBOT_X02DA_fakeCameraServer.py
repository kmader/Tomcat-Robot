import os,sys
from time import sleep
import datetime
from datetime import datetime as dt
try:
    import X_ROBOT_X02DA_robotCommon as RCLib 
except:
    print "Initial robotCommon not found!"
    try:
        sys.path.insert (0, os.path.expandvars ("$SLSBASE/sls/bin/"))
        import X_ROBOT_X02DA_robotCommon as RCLib
    except:
        os.system ("xkbbell")
        os.system ("xmessage -nearmouse -timeout 30 -buttons '' RobotCommon Python Library is needed to run this program!")
        sys.exit (1)

class LogPipe:
    def __init__(self,logFileName='script',dirName='Robot_Logs'):
        try:
            os.listdir( os.path.expandvars ("$HOME/"+dirName+"/"))
        except:
            os.mkdir( os.path.expandvars ("$HOME/"+dirName+"/"))
        cday=datetime.date.today()
        
        self.logFileName=os.path.expandvars("$HOME/"+dirName+"/"+logFileName+"."+str(cday)+".log")
        self.write('\n'+str(dt.now())+':'+logFileName+' freshly started'+'\n',0)
    def write(self,myStr,indent=1):
        tFile=open(self.logFileName,'a+')
        tFile.write('\t'*indent+myStr+'\n')
        tFile.close()
    def log(self,myStr,indent=1):
        self.write(str(dt.now())+'\t'*indent+myStr,0)
goCh=RCLib.RoboEpicsChannel('X02DA-SCAN-SCN1:GO')
nameCh=RCLib.RoboEpicsChannel('X02DA-SCAN-CAM1:FILPRE')
scanStatusCh=RCLib.RoboEpicsChannel('X02DA-SCAN-SCN1:STATUS')
newPipe=LogPipe('fakeCameraServer')
while True:
	if goCh.getVal()>0:
		scanStatusCh.putVal(1)
		newPipe.log('Scanning Sample : '+str(nameCh.getVal()))
		sleep(5)
		scanStatusCh.putVal(0)
		goCh.putVal(0)
	sleep(1)
	
		

