# AALib
# 23022010
# Meant as a library for for the Automatic Alignment Too
# Handles Reading, Flatfield Correction, Thesholding, Fitting Cylindrical Objects,
# and Cross-correlation
snapPrefix='X02DA-SCAN-SNAP'
import wx
from math import atan,pi,sin
from numpy import vdot,array,fromstring,zeros,fliplr,flipud,sum,mean
from numpy.fft import *
from numpy import log as arrlog
from numpy import abs as arrabs
import Image
import pdb
from optparse import OptionParser
import glob,os,time
try:
    import X_ROBOT_X02DA_robotCommon
except:
    print "Initial robotCommon not found!"
    try:
        sys.path.insert (0, os.path.expandvars ("$SLSBASE/sls/bin/"))
        import  X_ROBOT_X02DA_robotCommon
    except:
        sys.exit (1)
sampleThreshLib={}
sampleThreshLib['From Image']=(-1,-1)
sampleThreshLib['Embedded Bone @ 28keV']=((3.61113315+3.04723031)/2,  (3.61113315-3.04723031)/2) # +1.5 std to isolate cortical bone
sampleThreshLib['Mouse Femur @ 20keV']=(1.1,0.8)
sampleThreshLib['Mouse Femur @ 20keV']=(1.2,.80)
sampleThreshLib['Metal Support @ 20keV']=(3.5,0.4)
sampleThreshLib['Rat Brain @ 20keV']=(1.0,0.5)


# Somewhat dated code to read the images
class kImage:
    def __init__(self,imfilename,flatfilename='',flatdata=[]):
        self._Image,self._imageData=self.parseImage2(imfilename)
        if flatfilename!='':
            self._flatImage,flatdata=self.parseImage2(flatfilename)
            del(self._flatImage)
        if len(flatdata)==len(self._imageData):
            self._imageData=arrlog(array(flatdata)/self._imageData)
        self._imageMask=arrabs(array(self._imageData))>-1
        self._opts={}
        self._opts['readMode']=1 # 0 is raw, 1 mask-values, 2 masked image
        self._opts['usingMat']=0
        self._opts['maskMode']=0 # 0 default, -1 values under thresh, 1 values overthresh
        self._impResults={}
		#self.com=(self._gcmx(),self._gcmy())
		
    def _waitFile(self,fileName,delayTime=10):
        # code to wait on a file being saved
        sTime=time.time()
        print 'Trying '+fileName+' : '+str(glob.glob(fileName))
        while len(glob.glob(fileName))<1:
            time.sleep(0.25)
            if (time.time()-sTime)>delayTime: 
                print 'Loading '+fileName+' failed!'
                return -1
        return 1
    def _waitParse(self,loadFun,fileName,delayTime=30):
        # Because glob seems to cause a bus error (no idea why)
        
        # sometimes running ls makes it work better?
        os.system('ls '+fileName)
        print 'Opening : '+fileName+' , '+str(delayTime)+' , Dir Count:'+str(len(glob.glob(fileName)))
        sTime=time.time()
        #pdb.set_trace()
        if delayTime>0:
            try:
                return loadFun.__call__(fileName)
            except:
                time.sleep(0.5)
                return self._waitParse(loadFun,fileName,delayTime-(time.time()-sTime))
        else:
            print fileName+' cannot be loaded!'
            return None
        
    def isCentered(self,cTol,useGonio=False):
        # Function to determine if the object is centered
        xyCentered=(abs(self._impResults['Sample Offset'])<cTol)
        if useGonio:
            # only count quarter as much (basically less than a deg isch guet)
            slantPixels=sin(self._impResults['Sample Orientation']*pi/180.0)*512
            rCentered=(abs(slantPixels)<cTol)
        else:
            rCentered=True
        return (xyCentered and rCentered)
    def parseImage2(self,imFileName):
        #if self._waitFile(imFileName):
        #    img=Image.open(imFileName)
        #else:
        #    return 0
        img=self._waitParse(Image.open,imFileName)
        #print img.size
        #print img.info
        data=array(img.getdata())
        self.size=img.size
        data=array(data.reshape(img.size[1],img.size[0]),dtype='float') # must be read in transposed? wtf
        self.size=data.shape
        return (img,data)
    def parseImage(self,imFileName):
        #if self._waitFile(imFileName):
        #    img=wx.Image(imFileName)
        #else:
        #    return 0
        img=self._waitParse(wx.Image,imFileName)
        data=self.parseimdata(img)
        self.size=img.GetSize()
        return (img,data)
    def parseimdata(self,img):
        return fromstring(img.GetData(),count=(img.GetSize()[0]*img.GetSize()[1]),dtype='uint8').reshape(img.GetSize()[0],img.GetSize()[1])
    def saturationCheck(self,cutOff=60000):
        self.meanValue=self._imageData.mean()
        self.stdValue=self._imageData.std()
        self._impResults['Mean']=self._imageData.mean()
        self._impResults['Std']=self._imageData.std()
        self._imageMask=array(self._imageData)>(cutOff)
        self._impResults['% Saturated']=self._imageMask.sum()/(self.size[0]*self.size[1]+0.0)*100
        return 'Percent Saturated:'+str(round(self._impResults['% Saturated']*100)/100.0)+'%'+' '+str((int(self.meanValue),int(self.stdValue)))
    def threshold(self,_stdR=1.5,useMat=''):
        stdValue=-1
        
        if sampleThreshLib.has_key(useMat):
            (mValue,stdValue)=sampleThreshLib[useMat]
            stdR=1 # Always 1 with materials
            self._opts['usingMat']=1
        else:
            stdR=_stdR
            self._opts['usingMat']=1
        if stdValue<0.0:
            mValue=self._imageData.mean()
            stdValue=self._imageData.std()
            stdR=_stdR
            print 'Mean Value:'+str(mValue)
            print 'Std:'+str(stdValue)
        self._lowerMask=array(self._imageData)<(mValue-stdR*stdValue)
        self._upperMask=array(self._imageData)>(mValue+stdR*stdValue)
        self._imageMask=(True-self._lowerMask) & (True-self._upperMask)
        self._impResults['% Air']=self._lowerMask.sum()/(self.size[0]*self.size[1]+0.0)*100
        self._impResults['% Metal']=self._upperMask.sum()/(self.size[0]*self.size[1]+0.0)*100
        self._impResults['% Bone']=self._imageMask.sum()/(self.size[0]*self.size[1]+0.0)*100
        self._impResults['Mean']=self._imageData.mean()
        self._impResults['Std']=self._imageData.std()
        self.meanValue=mValue
        self.stdValue=stdValue
        self.stdrValue=stdR
        return self
    def matchImage(self,otherImage,toFlip=True):
        # Does a correlation between two images
        if toFlip:
            tData=fliplr(otherImage._imageData)
        else:
            tData=otherImage._imageData
        
        tempData=ifftshift(abs(ifft2(fft2(self._imageData)*fft2(tData).conj())))
        del(tData)
        wArg=tempData.argmax()
        xOff=(wArg % tempData.shape[1])
        yOff=round((wArg-xOff)/tempData.shape[1])
        # find vector from center
        xOff-=tempData.shape[1]/2.0
        yOff-=tempData.shape[0]/2.0
        self.matchedPos=(xOff,yOff)
        self._impResults['Maximum Correlation']=(xOff,yOff)
        
        return arrlog(tempData) # easier to visualize
    def _getColorBounds(self,imgType='G'):
        if imgType=='G':
            return (self.uintRelMinVal,self.uintRelMaxVal)
        elif imgType=='R':
            return (self.uintRelMaxVal,self.uintAbsMaxVal)
        elif imgType=='B':
            return (self.uintAbsMinVal,self.uintRelMinVal)
        
    def uint8histo(self,values,imgType='G'):
        (minVal,maxVal)=self._getColorBounds(imgType)
        return list((array(values)-50)*(maxVal-minVal)/205+minVal)
    
    def array2uint8(self,myArray,imgType='G'):
        (rows,cols)=myArray.shape
        (minVal,maxVal)=self._getColorBounds(imgType)
        outArray=array(205.0*(myArray-minVal)/(maxVal-minVal)+50,dtype='uint8')
        return outArray
    def sync(self,nSizeX=512,nSizeY=512):
        self._Image=self.toImg()
    def toImg(self,nSizeX=512,nSizeY=512):
        
        self.uintAbsMinVal=self._imageData.min()
        self.uintRelMinVal=self.meanValue-self.stdrValue*self.stdValue
        self.uintRelMaxVal=self.meanValue+self.stdrValue*self.stdValue
        self.uintAbsMaxVal=self._imageData.max()
        outArray=self.array2uint8(self._imageData,'G')*(self._imageMask)
        underArray=self.array2uint8(self._imageData,'B')*(self._lowerMask)
        overArray=self.array2uint8(self._imageData,'R')*(self._upperMask)
        (rows,cols)=outArray.shape
        nwArr=zeros((rows, cols, 3), 'uint8')
        nwArr[:,:,0]=overArray
        nwArr[:,:,1]=outArray
        nwArr[:,:,2]=underArray
        g_Image = wx.EmptyImage(cols,rows)
        g_Image.SetData(nwArr.tostring())
        return g_Image

    def _wmean(self,tempSet):
        if sum(tempSet)==0:
            return (-1,0)
        else:
            sa=sum(tempSet)
            xr=range(0,len(tempSet))
            mval=vdot(tempSet,xr)/sa
            std=float(pow(sum(array(tempSet)*pow((array(xr)-mval),2)/sum(tempSet)),0.5))
            if std!=std: std=0
            return (mval,std)
        
    def _cmx(self,i,minPct=0):
        if i<self.size[0]:
            cOut=self._imageMask[i,:]
            if (sum(cOut>0)/(0.0+len(cOut))*100.0)<minPct:
                #print 'Too Few Pixels : '+str(sum(cOut>0)/(0.0+len(cOut))*100.0)
                return cOut*0
            else:
                return self[i,:]
        else:
            print 'Boundary Extension x:'+str(i)
            return self[self.size[0]-1,:]
        
    def _cmy(self,j,minPct=0):
        if j<self.size[1]:
            cOut=self._imageMask[:,j]
            if (sum(cOut>0)/(0.0+len(cOut))*100.0)<minPct:
                #print 'Too Few Pixels : '+str(sum(cOut>0)/(0.0+len(cOut))*100.0)
                return cOut*0
            else:
                return self[:,j]
        else:
            print 'Boundary Extension y:'+str(j)
            return self[:,self.size[1]-1]
    def cmx(self,defRng=-1,minPct=0.0):
        if defRng==-1: defRng=range(0,self.size[0])
        if type(defRng) is not list: defRng=range(defRng,defRng+1)
        tempSet=array(self._cmx(defRng[0]))*0
        for i in defRng:
            tempSet+=self._cmx(i,minPct)
        return self._wmean(tempSet)
    def cmy(self,defRng=-1,minPct=0.0):
        if defRng==0: defRng=range(0,self.size[1])
        if type(defRng) is not list: defRng=range(defRng,defRng+1)
        tempSet=array(self._cmy(defRng[0]))*0
        for j in defRng:
            tempSet+=self._cmy(j)
        return self._wmean(tempSet,minPct)

    def _asVector_(self,mStep=5):
        x=[]
        y=[]
        for val in range(0,self.size[0]-mStep+1,mStep):
            nOut=array(self._cmx(val))
            for i in range(val+1,val+mStep+1):
                nOut+=self._cmx(i)
            
            for valJ in range(0,len(nOut)-mStep+1,mStep):
                if nOut[valJ]>0:
                    x.append((valJ-self.size[1]/2.0))
                    y.append(-1*(val+mStep/2.0-self.size[0]/2.0))
        return (x,y)
    def CleanMask(self,mStep=3,minPct=8.0): 
        # Clean Mask clears rows if the neighboring rows are also empty
        clearedRows=0
        clearedCols=0
        for val in range(mStep,self.size[0]-mStep+1,1):
            cOut=array(self._imageMask[range(val-mStep,val+mStep),:])
            if (sum(cOut>0)/(0.0+cOut.size)*100.0)<minPct:
                self._imageMask[val,:]=0
                clearedRows+=1
        for val in range(mStep,self.size[1]-mStep+1,1):
            cOut=array(self._imageMask[:,range(val-mStep,val+mStep)])
            if (sum(cOut>0)/(0.0+cOut.size)*100.0)<minPct:
                self._imageMask[:,val]=0
                clearedCols+=1
        print 'Cleared : '+str((clearedRows,clearedCols))+' of '+str(self.size)
        self._impResults['% Bone']=self._imageMask.sum()/(self.size[0]*self.size[1]+0.0)*100        
    def fitVcyl(self,mStep=30):
        x=[]
        y=[]
        stdMat=[]
        # Store dummy values in case something goes wrong
        self._impResults['Sample Offset']=0
        self._impResults['Sample Orientation']=720
        self.CleanMask(mStep/2,5)
        #self.CleanMask(mStep,8.0)
        self._impResults['Sample Top']=-1
        self._impResults['Sample Bottom']=-1
        for val in range(mStep,self.size[0]-mStep+1,mStep):
            nOut=self.cmx(range(val,val+mStep+1),0)
            if nOut[0]>=0:
                if self._impResults['Sample Top']==-1: self._impResults['Sample Top']=val-1
                self._impResults['Sample Bottom']=val
                xVal=(nOut[0]-self.size[1]/2.0)
                
                yVal=-1*(val+mStep/2.0-self.size[0]/2.0)
                x.append(xVal)
                y.append(yVal)
                stdMat.append(nOut[1])
            
        self._impResults['Sample Mean Width']=mean(2*array(stdMat))        
        fitPars=self._fitit(x,y,0,True)
        nX=list(array(x)+array(stdMat))
        nY=list(array(y))
        x.reverse()
        y.reverse()
        nX.extend(array(x)-array(stdMat))
        nY.extend(array(y))
        self.x=array(nX)
        self.y=array(nY)
        self._impResults['Sample Top']*=round(2048.0/self.size[1])
        self._impResults['Sample Bottom']*=round(2048.0/self.size[1])
        return fitPars
    def _fitit(self,lX,lY,iterFit=0,flipAxes=False):
        if (len(lX)==0) or (len(lY)==0): return (-1,-1)
        if (max(lX)-min(lX))<(max(lY)-min(lY)): flipAxes=True
        if flipAxes:
            y=array(lX)
            x=array(lY)
        else:
            x=array(lX)
            y=array(lY)
        xm=x.mean()
        ym=y.mean()
        xy=(x*y).mean()
        n=len(x)
        xsm=(x*x).mean()
        b=sum((x-xm)*(y-ym))/(pow(x.std(),2)*n)
        a=ym-b*xm
        if iterFit<1:
            if flipAxes:
                self.fitDx=a+b*x 
                self.fitDy=x
                self.y=x
                self.x=y
            else:
                self.fitDx=range(-int(self.size[1]/2.0),+int(self.size[1]/2.0))
                self.fitDy=a+b*array(self.fitDx) 
                self.y=y
                self.x=x
            self.fitA=a
            self.fitB=b
            self.calcAngleOffset()
            print str(a)+'+x*'+str(b)
            
            return (a,b)
        else:
            bdPt=(abs(y-(a+b*x))).argmax()
            llx=list(x)
            lly=list(y)
            nVal=llx.pop(bdPt)
            lly.pop(bdPt)
			#print 'badx:'+str(lx.pop(bdPt))
			#print 'bady:'+str(ly.pop(bdPt))
            print '\t'*2+str(a)+'+x*'+str(b)
            if flipAxes:
                return self._fitit(lly,llx,iterFit-1,True)
            else:
                return self._fitit(llx,lly,iterFit-1)
    def calcAngleOffset(self):
        cAng=atan(1/self.fitB)*180/pi
        reOffset=0
        if cAng>45: 
            cAng-=90
        if cAng<-45: 
            cAng+=180-90
        self.fitOffset=self.fitA*round(2048/self.size[0])
        self.fitOrientation=cAng
        self._impResults['Sample Offset']=self.fitOffset
        self._impResults['Sample Orientation']=self.fitOrientation
        return cAng
    def __getattr__(self,name):
        return getattr(self._Image,name)	
    def __getitem__(self,giArgs):
        cMask=self._imageMask
        if self._opts.has_key('maskMode'): # enables getting stats for lower and upper
            if self._opts['maskMode']==-1:
                cMask=self._lowerMask
            elif self._opts['maskMode']==1:
                cMask=self._upperMask
        
        if self._opts['readMode']==0:
            return self._imageData[giArgs]
        elif self._opts['readMode']==1:
            return cMask[giArgs]
        elif self._opts['readMode']==2:
            return (cMask[giArgs]*self._imageData[giArgs])

if __name__ == '__main__':
    optParse=OptionParser()
    optParse.add_option('-s','--scan',action='store_true',dest='scan',help='Run scan saturation check',default=False)
    optParse.add_option('-d','--scandir',dest='scandir',help='Run stats on what directory (mean, std) on image or sets of images',default='$HOME/Data*/*/*/tif/*0007.tif')
    optParse.add_option('-c','--cutoff',dest='cutoff',help='Show percentage above',default='60000')
    optParse.add_option('-l','--last',action='store_true',dest='last',help='Check last image',default=False)
    
    optParse.set_description('The image processing library that can be used to check images for saturation, mean values and std')
    optParse.print_help()
    (opt,args)=optParse.parse_args()
    
    if opt.last:
        from X_ROBOT_X02DA_robotCommon import *
        filpre=RoboEpicsChannel('X02DA-SCAN-CAM1:FILPRE').getVal()
        storage=RoboEpicsChannel('X02DA-SCAN-CAM1:STORAGE').getVal()
        opt.scandir='$HOME/'+storage+'/'+filpre+'/tif/*0007.tif'
        opt.scan=True
        print 'Looking for...'+opt.scandir
    if opt.scan:
        #statList=opt.stat.split(';')
        #for statListEle in statList:
        #print opt.stat
        nList=glob.glob(os.path.expandvars(opt.scandir))
        nList.sort()
        print nList
        for nListEle in nList:
            oldJunk=kImage(nListEle)
            print nListEle+' : '+oldJunk.saturationCheck(int(opt.cutoff))
                #print 'Mean Value :'+str(int(oldJunk.meanValue))
                #print 'Std :'+str(int(oldJunk.stdValue))
    