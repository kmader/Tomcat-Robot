// server.cpp : Defines the entry point for the console application.
/**********************************************************************
The following program runs either a fastscan or snap in Kevin's mode.
the option for saving the images in 8 or 16 bit TIFF has been implemented
Federica Marone, September 2009.
The program has been integrated with the ImageProcessing Library developed
by Kevin (translated from Python), this library
Kevin Mader, Feburary 2010
**********************************************************************/

#include "stdafx.h"
#include <stdio.h>
#include <math.h>
#include <string.h>
#include "C:\Program Files\GnuWin32\include\tiffio.h"

#include "..\..\include\sc2_SDKStructures.h"
#include "..\..\include\SC2_CamExport.h"
#include "..\..\include\sc2_SDKAddendum.h"
#include "..\..\include\sc2_defs.h"
#include "..\..\include\PCO_err.h"
#include "..\..\include\cadef.h"
#include "..\..\include\db_access.h"
#include "..\..\include\epicsStdlib.h"
#define PCO_ERRT_H_CREATE_OBJECT
#include "..\..\include\PCO_errt.h"
#include "load.h"
#include "ImageProcessing.h"

#define NOFILE	-100

typedef struct {
	SHORT sBufNr;
	DWORD size;
	WORD *wBuf;
	HANDLE hEvent;
} Picbuf;

bool AnalyzeImage(void);

static double dwExposure;
static short hbin, vbin;
static short roix1, roix2, roiy1, roiy2;
HINSTANCE SC2Lib = NULL;
HANDLE hCamera;
static int err;
PCO_Description caminfo;
PCO_CameraType strCamType;
WORD wStorageMode;
static unsigned short recstate;
static WORD expbase,wTimeBaseExposure,wTimeBaseDelay;
static SHORT sBufNr;
static DWORD imgsize;
static DWORD bufsize;
static WORD* wBuf;
static bool* bwBuf;
static bool* fitBuf;
static bool firstFlat;
static kImage* cSnapShot;
static WORD* flatBuf;
static WORD trigger_result;

WORD wCameraBusyState;
WORD wTriggered;
WORD wActSeg;
WORD wSensor;
DWORD dwStatusDll;
DWORD dwStatusDrv;
DWORD dwValidImageCnt;
DWORD dwMaxImageCnt;
DWORD dwRamSegSize[4];
DWORD dwRamSize;
WORD wPageSize;
DWORD dwExp,dwDelay;
DWORD dwTime_s,dwTime_ns;
WORD wXResAct; // Actual X Resolution
WORD wYResAct; // Actual Y Resolution
WORD wXResMax; // Maximum X Resolution
WORD wYResMax; // Maximum Y
short ccdtemp, camtemp, powtemp;
short recorder;
short ccdCoolingTemp;
short ccdCoolingDefault=-15;
unsigned long neededRAMprj,neededRAMdrk,neededRAMflt;
double nprj,exptime,ndrk,nflt,fps,rotsto,rotsta,tiff;
double angle=0.,angle_old;

HANDLE hEvent = NULL;
chid chan_nprj;
chid chan_ndrk;
chid chan_nflt;
chid chan_expt;
chid chan_go;
chid chan_snap;
chid chan_cimg;
chid chan_nimg;
chid chan_folder;
chid chan_sample;
chid chan_angle;
chid chan_frame;
chid chan_ccdx;
chid chan_ccdy;
chid chan_rotsto;
chid chan_rotsta;
// Snap Control Channels
chid chan_snap_snap;
chid chan_snap_multi;
chid chan_snap_flat;
chid chan_folder_snap;
chid chan_image_snap;
chid chan_expt_snap;
chid chan_tiff_snap;
chid chan_align_recalc;
// Snap Alignment Channels Input
chid chan_align_align;
chid chan_align_preview;
chid chan_align_thavg;
chid chan_align_thstd;
chid chan_align_saveimg;
chid chan_align_minpct;
chid chan_align_cutoff;
chid chan_align_rowavg;
chid chan_align_mintrans;
chid chan_align_maxtrans;
chid chan_align_maskmode;
chid chan_align_readmode;

// Snap Alignment Channels Output
chid chan_align_theta;
chid chan_align_dimx;
chid chan_align_dimy;
chid chan_align_xoffset;
chid chan_align_yoffset;
chid chan_align_imavg;
chid chan_align_imstd;
chid chan_align_width;
chid chan_align_top;
chid chan_align_bottom;
chid chan_align_height;
chid chan_align_pctover;
chid chan_align_pctunder;
chid chan_align_pctbetween;
chid chan_align_pctsaturated;

chid chan_align_good;
chid chan_align_flatloaded;
//
bool snapTaken;
bool validBW;

char string[1024];
char foldername[1024];
char samplename[1024];
char image[1024];
char ext[5];
int tomostart,snapstart,flatstart,saveimg,alignimg,isflat,trigger,cimg[4],scantime,recalcstart;
int ccdnADC,ccdnclock,ccdreadout;

unsigned int nimg[4],i,k,ii,n;
Picbuf picbuffer[4];
int x,nr_of_buffer=4,buflist_count=4,buflist_count_snap=1;
PCO_Buflist bl[4];
PCO_Buflist bl_snap;
int PicTimeOut=30000;

int getlib(void);
int ca_search_routine(char *channel_name, chid *chan);
double caget_double(chid chan);
int caget_char(chid chan, char *foldername);
int caput_double(chid chan, double value);
int store_b16(char *filename, int width, int height, void *buf);
void writeTIFF16(char *nameout, WORD *buf, int width, int height);
void writeTIFF8(char *nameout, WORD *buf, int width, int height);
void writeCTIFF(char *nameout, WORD *buf,bool* mask,bool* fitmask, int width, int height);
void writeTIFF2(char *nameout, WORD *buf, int width, int height);
void writeTIFF2(char *nameout, bool *buf, int width, int height);
//DWORD WaitForBuffer(HANDLE hCamera,int nr_of_buffer,Buflist *bl,int timeout);

int main(int argc, char* argv[])
{
  int errbuffer_size=400;
  char errbuffer[400];

  bool bbufferextern = TRUE;
  //; FALSE// Set to TRUE, if you want to allocate the buffer on your own.
  /************************************************************
  load SC2 library; please note SC2_Cam.dll has dependency on
  sc2_1394.dll, this dll must be present in your dll search path.
  ************************************************************/

  printf("ACQUISITION routine is alive.\n");
  printf("\r\n");
  err = getlib();
  if (err != 0)
  {
    sprintf_s(errbuffer, errbuffer_size*sizeof(char),"\nCan not load SC2 library. Error: %d\n", err);
    goto abnormal;
  }
  printf("Libraries loaded.\r\n");

  /* Channels for tomography */
  err = ca_search_routine("X02DA-SCAN-SCN1:GO",&chan_go);
  err = ca_search_routine("X02DA-SCAN-SCN1:NPRJ",&chan_nprj);
  err = ca_search_routine("X02DA-SCAN-SCN1:ROTSTO",&chan_rotsto);
  err = ca_search_routine("X02DA-SCAN-SCN1:ROTSTA",&chan_rotsta);
  err = ca_search_routine("X02DA-SCAN-SCN1:NPPFLT",&chan_nflt);
  err = ca_search_routine("X02DA-SCAN-SCN1:NPPDRK",&chan_ndrk);
  err = ca_search_routine("X02DA-SCAN-SCN1:ACTCNT",&chan_cimg);
  err = ca_search_routine("X02DA-SCAN-CAM1:SNAP",&chan_snap);
  err = ca_search_routine("X02DA-SCAN-SCN1:NPRJSTK",&chan_nimg);
  err = ca_search_routine("X02DA-SCAN-CAM1:FILDIR",&chan_folder);
  err = ca_search_routine("X02DA-SCAN-CAM1:FILPRE",&chan_sample);
  err = ca_search_routine("X02DA-SCAN-CAM1:EXPTME",&chan_expt);
  /*err = ca_search_routine("X02DA-ES1-MICOS:USR_POSN",&chan_angle);*/
  err = ca_search_routine("X02DA-ES1-SMP1:ROTYUGETP",&chan_angle);
  err = ca_search_routine("X02DA-SCAN-CAM1:CCDX",&chan_ccdx);
  err = ca_search_routine("X02DA-SCAN-CAM1:CCDY",&chan_ccdy);
  err = ca_search_routine("X02DA-SCAN-CAM1:FRAMETME",&chan_frame);

  /* Channels for snapping */
  err = ca_search_routine("X02DA-SCAN-SNAP:SNAP",&chan_snap_snap);
  err = ca_search_routine("X02DA-SCAN-SNAP:FLAT",&chan_snap_flat);
  err = ca_search_routine("X02DA-SCAN-SNAP:MULTI",&chan_snap_multi);
  err = ca_search_routine("X02DA-SCAN-SNAP:RECALC",&chan_align_recalc);
  err = ca_search_routine("X02DA-SCAN-SNAP:STORAGE",&chan_folder_snap);
  err = ca_search_routine("X02DA-SCAN-SNAP:IMGNME",&chan_image_snap);
  err = ca_search_routine("X02DA-SCAN-SNAP:EXPTME",&chan_expt_snap);
  err = ca_search_routine("X02DA-SCAN-SNAP:TIFF",&chan_tiff_snap);



// Snap Alignment Channels Input
  err = ca_search_routine("X02DA-SCAN-SNAP:ALIGN",&chan_align_align);
  err = ca_search_routine("X02DA-SCAN-SNAP:THAVG",&chan_align_thavg);
  err = ca_search_routine("X02DA-SCAN-SNAP:THSTD",&chan_align_thstd);
  err = ca_search_routine("X02DA-SCAN-SNAP:SAVE",&chan_align_saveimg);
  err = ca_search_routine("X02DA-SCAN-SNAP:PREVIEW",&chan_align_preview);
  err = ca_search_routine("X02DA-SCAN-SNAP:MINPCT",&chan_align_minpct);
  err = ca_search_routine("X02DA-SCAN-SNAP:CUTOFF",&chan_align_cutoff);

  err = ca_search_routine("X02DA-SCAN-SNAP:ROWAVG",&chan_align_rowavg);
  err = ca_search_routine("X02DA-SCAN-SNAP:MINTRANS",&chan_align_mintrans);
  err = ca_search_routine("X02DA-SCAN-SNAP:MAXTRANS",&chan_align_maxtrans);

  err = ca_search_routine("X02DA-SCAN-SNAP:MASKMODE",&chan_align_maskmode);
  err = ca_search_routine("X02DA-SCAN-SNAP:READMODE",&chan_align_readmode);
// Snap Alignment Channels Output
  err = ca_search_routine("X02DA-SCAN-SNAP:THETA",&chan_align_theta);
  err = ca_search_routine("X02DA-SCAN-SNAP:DIMX",&chan_align_dimx);
  err = ca_search_routine("X02DA-SCAN-SNAP:DIMY",&chan_align_dimy);
  err = ca_search_routine("X02DA-SCAN-SNAP:XOFFSET",&chan_align_xoffset);
  err = ca_search_routine("X02DA-SCAN-SNAP:YOFFSET",&chan_align_yoffset);
  err = ca_search_routine("X02DA-SCAN-SNAP:IMAVG",&chan_align_imavg);
  err = ca_search_routine("X02DA-SCAN-SNAP:IMSTD",&chan_align_imstd);
  err = ca_search_routine("X02DA-SCAN-SNAP:WIDTH",&chan_align_width);
  err = ca_search_routine("X02DA-SCAN-SNAP:TOP",&chan_align_top);
  err = ca_search_routine("X02DA-SCAN-SNAP:BOTTOM",&chan_align_bottom);
  err = ca_search_routine("X02DA-SCAN-SNAP:HEIGHT",&chan_align_height);
  err = ca_search_routine("X02DA-SCAN-SNAP:GOOD",&chan_align_good);
  err = ca_search_routine("X02DA-SCAN-SNAP:FTDONE",&chan_align_flatloaded);
  err = ca_search_routine("X02DA-SCAN-SNAP:PCTUND",&chan_align_pctunder);
  err = ca_search_routine("X02DA-SCAN-SNAP:PCTBET",&chan_align_pctbetween);
  err = ca_search_routine("X02DA-SCAN-SNAP:PCTOVR",&chan_align_pctover);
  err = ca_search_routine("X02DA-SCAN-SNAP:PCTSAT",&chan_align_pctsaturated);


  isflat=0;
  snapTaken=false;
  err=caput_double(chan_align_flatloaded,isflat);
  do {
     /*tomostart=(int)caget_double(chan_go);*/

	 printf("\nWaiting EPICS start ...\n");
	 /*printf("Tomostart %i\n",tomostart);*/

	 do {
		 Sleep(250);
		 tomostart=(int)caget_double(chan_go);
		 snapstart=(int)caget_double(chan_snap_snap);
		 flatstart=(int)caget_double(chan_snap_flat);
		 recalcstart=(int)caget_double(chan_align_recalc);
		 //if (recalcstart>0) {
		// 	printf("Recalculating Alignment Parameters...\n");
		// 	AnalyzeImage();
			
		//}
	 } while ((tomostart+snapstart+flatstart)==0);

	 if (tomostart!=0 && snapstart!=0) {
		 printf("Tomographic scan and snap function both running at the same time!\n");
		 goto abnormal;
	 }
     // Read Several Settings
	 saveimg=(int)caget_double(chan_align_saveimg);
	 alignimg=(int)caget_double(chan_align_align);

	 printf("Acquisition started!\n");

	 err = OpenCamera(&hCamera, 0);
     if (err != 0)
	 {
       sprintf_s(errbuffer, errbuffer_size*sizeof(char),"\nPCO_OpenCamera error (hex): %lx\n", err);
       goto abnormal;
	 }
     printf("Camera opened.\n");
	 err = GetCoolingSetpointTemperature(hCamera, &ccdCoolingTemp);
     if (err != 0)
	 {
        sprintf_s(errbuffer, errbuffer_size*sizeof(char),"\nPCO_GetCoolingSetpointTemperature error(hex): %lx\n", err);
        goto abnormal;
	 }
	 if (ccdCoolingTemp != ccdCoolingDefault) {
		 err = SetCoolingSetpointTemperature(hCamera,ccdCoolingDefault);
         if (err != 0)
		 {
            sprintf_s(errbuffer, errbuffer_size*sizeof(char),"\nPCO_SetCoolingSetpointTemperature error(hex): %lx\n", err);
            goto abnormal;
		 }
	 }
     err = GetTemperature(hCamera, &ccdtemp, &camtemp, &powtemp);
     printf("\nOperating temperatures: \nCCD: %d C \nElectronics: %d C \nPower: %d C\n", ccdtemp/10, camtemp, powtemp);
	 if ((ccdtemp/10)>-10) {
        printf("\nCCD temperature is too high: %d/10\n", ccdtemp/10);
        sprintf_s(errbuffer, errbuffer_size*sizeof(char),"\nCCD tempeeerature is too high: %d/10\n", ccdtemp/10);
        goto abnormal;
	 }
     err = GetRecordingState(hCamera, &recstate);
     if (err != 0)
	 {
       printf("\nPCO_GetRecordingState(hex): %lx\n", err);
	   sprintf_s(errbuffer, errbuffer_size*sizeof(char),"\nPCO_GetRecordingState(hex): %lx\n", err);
       goto abnormal;
	 }

     if (recstate>0)
	 {
       err = SetRecordingState(hCamera, 0x0000);
       if (err != 0)
	   {
         printf("\nPCO_SetRecordingState(hex): %lx\n", err);
         /*sprintf_s(errbuffer, errbuffer_size*sizeof(char),"\nPCO_SetRecordingState(hex): %lx\n", err);*/
         goto abnormal;
	   }
	 }

	 // sensor format (0x0000=standard, 0x0001=extended)
	 err = GetSensorFormat(hCamera, &wSensor);
	 if (wSensor!=0) {
		 printf("Sensor format extended: this option is not supported,\n");
		 printf("modify the format to standard and try again!\n");
		 Sleep(5000);
		 goto abnormal;
	 }
	 printf("\nSensor format standard\n");

	 // double image mode (0x0000=off, 0x0001=on)
	 printf("Double Image mode OFF\n");
	 err = SetDoubleImageMode(hCamera, 0x0000);
     if (err != 0)
	 {
       /*sprintf(errbuffer, "\nPCO_SetDoubleImageMode (hex): %lx\n", err);*/
       printf("\nPCO_SetDoubleImageMode (hex): %lx\n", err);
       goto abnormal;
	 }

	 // noise filter mode (0x0000=off, 0x0001=on, 0x0002=on+hotpixel correction)
	 printf("Noise filter mode OFF\n");
	 err = SetNoiseFilterMode(hCamera, 0x0000);
     if (err != 0)
	 {
       printf("\nPCO_SetNoiseFilterMode (hex): %lx\n", err);
       /*sprintf(errbuffer, "\nPCO_SetNoiseFilterMode (hex): %lx\n", err);*/
       goto abnormal;
	 }

	 // offset mode (0x0000=auto, 0x0001=off)
	 printf("Offset mode OFF\n");
	 err = SetOffsetMode(hCamera, 0x0001);
     if (err != 0)
	 {
       sprintf_s(errbuffer, errbuffer_size*sizeof(char), "\nPCO_SetOffsetMode (hex): %lx\n", err);
       goto abnormal;
	 }

	 /***************************  SNAP ROUTINE  ***************************/
	 if ((snapstart+flatstart)>0) {

		 err = GetSizes(hCamera, &wXResAct, &wYResAct, &wXResMax, &wYResMax);
		 if (err != 0)
	     {
			printf("\nPCO_GetSizes error(hex): %lx\n", err);
			/*sprintf_s(errbuffer,errbuffer_size*sizeof(char),"\nPCO_GetSizes error(hex): %lx\n", err);*/
			goto abnormal;
	     }

	     err = GetCameraRamSize(hCamera, &dwRamSize, &wPageSize);
         if (err != 0)
	     {
            sprintf_s(errbuffer,errbuffer_size*sizeof(char),"\nPCO_GetCameraRamSize error(hex): %lx\n", err);
            goto abnormal;
	     }
         else
	     {
		    dwRamSegSize[0]=dwRamSize;
            dwRamSegSize[1]=0;
            dwRamSegSize[3]=0;
            dwRamSegSize[2]=0;
 	     }

         caminfo.wSize =sizeof(PCO_Description);
         err = GetCameraDescription(hCamera, &caminfo);
	     if (err != 0)
	     {
            printf("\nPCO_GetCameraDescription error (hex): %lx\n", err);
            /*sprintf_s(errbuffer,errbuffer_size*sizeof(char),"\nPCO_GetCameraDescription error (hex): %lx\n", err);*/
            goto abnormal;
	     }

	     // auto trigger (0x0000=auto-sequence; 0x0001 software trigger)
         err = SetTriggerMode(hCamera, 0x0001);
         if (err != 0)
	     {
            printf("\nPCO_SetTriggerMode error (hex): %lx\n", err);
            /*sprintf_s(errbuffer,errbuffer_size*sizeof(char),"\nPCO_SetTriggerMode error (hex): %lx\n", err);*/
            goto abnormal;
	     }

         // recorder mode auto
         err = SetStorageMode(hCamera, 1); /* FIFO */
         recorder = 1;
         if (err != 0)
	     {
            printf("\nPCO_SetStorageMode error (hex): %lx\n", err);
            /*sprintf_s(errbuffer,errbuffer_size*sizeof(char),"\nPCO_SetStorageMode error (hex): %lx\n", err);*/
            goto abnormal;
	     }

         // recorder submode ---- sequence=0, ring=1
         err = SetRecorderSubmode(hCamera, 0);  /* FM, Oct 15 changed to ring , Oct 25 changed back*/
         if (err != 0)
	     {
            printf("\nPCO_SetRecorderSubmode (hex): %lx\n", err);
            /*sprintf_s(errbuffer,errbuffer_size*sizeof(char),"\nPCO_SetRecorderSubmode (hex): %lx\n", err);*/
            goto abnormal;
	     }

         // all the images taken be stored
         err = SetAcquireMode(hCamera, 0);

	     // define output format
	     tiff = caget_double(chan_tiff_snap);

         // prepare delay exposure time
         dwExposure = caget_double(chan_expt_snap);
         expbase = 2;
         err = SetDelayExposureTime(hCamera, // Timebase: 0-ns; 1-us; 2-ms
         0,		// DWORD dwDelay
         (DWORD)dwExposure,
         0,		// WORD wTimeBaseDelay,
         expbase);	// WORD wTimeBaseExposure

         if (err != 0)
	     {
            sprintf_s(errbuffer,errbuffer_size*sizeof(char),"\nPCO_SetDelayExposureTime (hex): %lx\n", err);
            goto abnormal;
	     }
         else
            printf("\nExposureTime-->%d ms\n", (int)dwExposure);


	     /***********************************************************
         Partition Camera RAM and set segment 1 to active.
         Recording state must be 0 (already done previously).
         *************************************************************/
		 printf("\n Partitioning Ram \n");
         err = SetCameraRamSegmentSize(hCamera, dwRamSegSize);
         if (err != 0)
	     {
            sprintf_s(errbuffer,errbuffer_size*sizeof(char),"\nSetCameraRamSegmentSize(hex): %lx\n", err);
            goto abnormal;
	     }
		 printf("\n Setting Segment to 1 \n");
         wActSeg=1;
         err = SetActiveRamSegment(hCamera, wActSeg);
         if (err != 0)
	     {
            sprintf_s(errbuffer,errbuffer_size*sizeof(char),"\nSetActiveRamSegment(hex): %lx\n", err);
            goto abnormal;
	     }

         /***********************************************************
         ArmCamera validates settings.
         (recorder must be turned off to ArmCamera)
         *************************************************************/

         err = ArmCamera(hCamera);
         if (err != 0)
	     {
            sprintf_s(errbuffer,errbuffer_size*sizeof(char),"\nPCO_ArmCamera(hex): %lx\n", err);
            goto abnormal;
	     }

         imgsize = wXResAct*wYResAct*2;
         bufsize = imgsize;
		 
         if (bbufferextern)
	     {
            if (bufsize % 0x1000)
	        {
               bufsize = imgsize / 0x1000;
               bufsize += 2;
               bufsize *= 0x1000;
	        }
            else
               bufsize += 0x1000;
			 
            
	     }
         else
            wBuf = NULL;

		if (!snapTaken) {
				 printf("Reallocating Buffers\r\n");
				 wBuf = (WORD*)malloc(bufsize);
				 bwBuf   =(bool*)malloc(sizeof(bool)*wXResAct*wYResAct);
				 fitBuf  =(bool*)malloc(sizeof(bool)*wXResAct*wYResAct);
				 flatBuf = (WORD*)malloc(bufsize);
				 snapTaken=true;
				 err=caput_double(chan_align_dimx,wXResAct);
				 err=caput_double(chan_align_dimy,wYResAct);
			 }
	     /*************************************************************
	     Preset buffer structure
	     **************************************************************/
         sBufNr=-1;
         err = AllocateBuffer(hCamera, &sBufNr, bufsize, &wBuf, &hEvent);
         if (err != 0)
	     {
            sprintf_s(errbuffer,errbuffer_size*sizeof(char),"\nPCO_AllocateBuffer error(hex): %lx\n", err);
            goto abnormal;
         }
	     bl_snap.sBufNr=sBufNr;

	     err = SetRecordingState(hCamera,0x0001);

         // Snap
         do {
	        Sleep(1);
	        GetCameraBusyStatus(hCamera,&wCameraBusyState);
	     } while (wCameraBusyState==0x0001);

	     ForceTrigger(hCamera,&wTriggered);
	     if (wTriggered==0x0001) {
		    printf("Trigger successful!\n");
	     } else {
		    printf("Trigger not successful!\n");
		    goto abnormal;
	     }

	     if (bbufferextern)
            err = AddBufferEx(hCamera, 0, 0, sBufNr, wXResAct, wYResAct, caminfo.wDynResDESC);
         else
            err = AddBuffer(hCamera, 0, 0, sBufNr);
         if (err != 0) {
            PCO_GetErrorText(err, errbuffer, 400);

            printf("Here you can see the error explanation:\r\n%s", errbuffer);
            sprintf_s(errbuffer,errbuffer_size*sizeof(char),"\nPCO_AddBuffer error(hex): %lx\n", err);
            goto abnormal;
	     }
		 err=WaitforBuffer(hCamera,buflist_count_snap,&bl_snap,PicTimeOut);
			 if (err != 0)
			 {
				printf("WaitforBuffer\n");
				PCO_GetErrorText(err, errbuffer, 400);
				sprintf_s(errbuffer,errbuffer_size*sizeof(char),"\nPCO_WaitforBuffer(hex): %lx\n", err);
				goto abnormal;
			 }


		 if (flatstart) {


			if (isflat==0) {
				 printf("No Flat Exists\r\n");

				 
			}
			// Copy image into flat buffer
			printf("Copying Flat from Buffer\r\n");
			for(int xxc=0;xxc<(wXResAct*wYResAct);xxc++) flatBuf[xxc]=wBuf[xxc];
			printf("Setting Epics Channels\r\n");
			isflat=1;
			err=caput_double(chan_align_flatloaded,isflat);
			alignimg=0; // Don't ever align a flat or save a flat
			saveimg=0;

		 } else {
			 if (alignimg) {
			 // Image Alignment Code
			 AnalyzeImage();

			}
			// Write the image out if needed
			if (saveimg) {
			 err=caget_char(chan_folder_snap,foldername);
			 err=caget_char(chan_image_snap,image);
			 err=caget_char(chan_image_snap,image);
			 

			 //if (bl_snap.dwStatusDll&0x00008000) {
			 int preview=(int)caget_double(chan_align_preview);
			 if (preview==1) {
				sprintf_s(string,1024*sizeof(char),"X://%s/%s.rgb.tif",foldername,image);
				if (validBW) {
					writeCTIFF(string,wBuf,bwBuf,fitBuf,wXResAct,wYResAct);
      				printf("Image %s stored\n",string);
				} else {
					printf("FAILED to store image %s\n",string);
				}
					// Sloppy
					char imgcmd[1024];
					char imgparm[1024];
					sprintf_s(string,1024*sizeof(char),"X:\\%s\\%s.rgb.tif",foldername,image);
					sprintf_s(imgcmd,1024*sizeof(char),"C:\\WINDOWS\\System32\\rundll32.exe");
					sprintf_s(imgparm,1024*sizeof(char),"C:\\WINDOWS\\System32\\shimgvw.dll,ImageView_Fullscreen %s",string);		
				 printf("Showing Image : %s %s\n",imgcmd,imgparm);
						//system(imgall);
						// Show Preview
						ShellExecute(NULL,NULL,imgcmd,imgparm,NULL,SW_SHOWNORMAL);
			} else if (tiff==8) {
				sprintf_s(string,1024*sizeof(char),"X://%s/%s.8bit.tif",foldername,image);
					writeTIFF8(string,wBuf,wXResAct,wYResAct);
      				printf("Image %s stored\n",string);
					// Sloppy
					char imgcmd[1024];
					char imgparm[1024];
					sprintf_s(string,1024*sizeof(char),"X:\\%s\\%s.8bit.tif",foldername,image);
					sprintf_s(imgcmd,1024*sizeof(char),"C:\\WINDOWS\\System32\\rundll32.exe");
					sprintf_s(imgparm,1024*sizeof(char),"C:\\WINDOWS\\System32\\shimgvw.dll,ImageView_Fullscreen %s",string);
					
					
			 } else if (tiff==16) {
				sprintf_s(string,1024*sizeof(char),"X://%s/%s.16bit.tif",foldername,image);
					writeTIFF16(string,wBuf,wXResAct,wYResAct);
      				printf("Image %s stored\n",string);
      		 } else if (tiff==2) {
				 // Schon geschribbe
				 printf("Writing Binary Tiff...\n");
				 sprintf_s(string,1024*sizeof(char),"X://%s/%s.bw.tif",foldername,image);
					if (validBW) writeTIFF2(string,bwBuf,wXResAct,wYResAct);
					else writeTIFF2(string,wBuf,wXResAct,wYResAct);
					printf("Image %s stored\n",string);
					
			 } else {
				printf("Invalid format!\n");
				goto abnormal;
			 }
		 }
		 }
		 
	     //}
		 // If multiple is selected then don't disable snap after taking a snap
		 int multi=(int)caget_double(chan_snap_multi);
	     if (multi==1) trigger=1;
		 else trigger=0;
	     err=caput_double(chan_snap_snap,trigger);
		 trigger=0;
		 err=caput_double(chan_snap_flat,trigger);
		 err = SetRecordingState(hCamera, 0x0000);
         if (err != 0)
         {
            sprintf_s(errbuffer,errbuffer_size*sizeof(char),"\nPCO_SetRecordingState(hex): %lx\n", err);
            goto abnormal;
	     }

	     err=CancelImages(hCamera);

         err = FreeBuffer(hCamera, sBufNr);
         if (err != 0) {
            sprintf_s(errbuffer, errbuffer_size*sizeof(char), "\nPCO_FreeBuffer error(hex): %lx\n", err);
            goto abnormal;
         }
		 //free(wBuf);
		 //free(bwBuf);
		 //free(fitBuf);
	 } else {

		 /************************************* TOMOGRAPHY ROUTINE ********************************/

		 nprj=caget_double(chan_nprj);
	     nflt=caget_double(chan_nflt);
	     ndrk=caget_double(chan_ndrk);
	     rotsto=caget_double(chan_rotsto);
	     rotsta=caget_double(chan_rotsta);

	     err = GetCameraRamSize(hCamera, &dwRamSize, &wPageSize);
         if (err != 0)
	     {
            sprintf_s(errbuffer, errbuffer_size*sizeof(char), "\nPCO_GetCameraRamSize error(hex): %lx\n", err);
            goto abnormal;
	     }
         /*printf("Camera RAM size: %d, Page size: %d\n",dwRamSize,wPageSize);*/

         err = GetSizes(hCamera, &wXResAct, &wYResAct, &wXResMax, &wYResMax);
         if (err != 0)
	     {
            printf("\nPCO_GetSizes error(hex): %lx\n", err);
            /*sprintf_s(errbuffer, errbuffer_size*sizeof(char), "\nPCO_GetSizes error(hex): %lx\n", err);*/
            goto abnormal;
	     }
         else
	     {
		    err=caput_double(chan_ccdx,wXResAct);
		    err=caput_double(chan_ccdy,wYResAct);

            printf("\nImage Size=%dx%d\n", wXResAct, wYResAct);
            printf("Number of projections %lf\n",nprj);
            printf("Number of flats %lf\n",nflt);
            printf("Number of darks %lf\n",ndrk);
            if (nprj>1) {
		       neededRAMprj=(long)(ceil((double)(wXResAct*wYResAct/1280.))*nprj);
		    } else if (nprj==1) {
		       neededRAMprj=(long)(ceil((double)(wXResAct*wYResAct/1280.))*nprj*2.);
		    }
		    if (ndrk>1) {
			   neededRAMdrk=(long)(ceil((double)(wXResAct*wYResAct/1280.))*ndrk);
		    } else if (ndrk==1) {
			   neededRAMdrk=(long)(ceil((double)(wXResAct*wYResAct/1280.))*ndrk*2.);
		    }
		    if (nflt>1) {
			   neededRAMflt=(long)(ceil((double)(wXResAct*wYResAct/1280.))*nflt);
		    } else if (nflt==1) {
			   neededRAMflt=(long)(ceil((double)(wXResAct*wYResAct/1280.))*nflt*2.);
		    }
		    if (neededRAMprj+neededRAMdrk+neededRAMflt*2>dwRamSize) {
               printf("\nNeeded RAM is larger than 4Gb\n");
               //sprintf_s(errbuffer, errbuffer_size*sizeof(char), "\nNeeded RAM is larger than 4Gb\n");
               //goto abnormal;
			}
         }
         dwRamSegSize[0]=neededRAMdrk;
         dwRamSegSize[1]=neededRAMflt;
         dwRamSegSize[3]=neededRAMflt;
         dwRamSegSize[2]=dwRamSize-dwRamSegSize[0]-dwRamSegSize[1]-dwRamSegSize[3];

         caminfo.wSize =sizeof(PCO_Description);
         err = GetCameraDescription(hCamera, &caminfo);
	     if (err != 0)
	     {
            printf("\nPCO_GetCameraDescription error (hex): %lx\n", err);
            /*sprintf_s(errbuffer, errbuffer_size*sizeof(char), "\nPCO_GetCameraDescription error (hex): %lx\n", err);*/
            goto abnormal;
	     }

	     // auto trigger (0x0000=auto-sequence; 0x0001 software trigger)
         err = SetTriggerMode(hCamera, 0x0000);
         if (err != 0)
	     {
            printf("\nPCO_SetTriggerMode error (hex): %lx\n", err);
            /*sprintf_s(errbuffer, errbuffer_size*sizeof(char), "\nPCO_SetTriggerMode error (hex): %lx\n", err);*/
            goto abnormal;
	     }

         // recorder mode auto
         err = SetStorageMode(hCamera, 1); /* FIFO */
         recorder = 1;
         if (err != 0)
	     {
            printf("\nPCO_SetStorageMode error (hex): %lx\n", err);
            /*sprintf_s(errbuffer, errbuffer_size*sizeof(char), "\nPCO_SetStorageMode error (hex): %lx\n", err);*/
            goto abnormal;
	     }

         // recorder submode ---- sequence=0, ring=1
         err = SetRecorderSubmode(hCamera, 0);  /* FM, Oct 15 changed to ring , Oct 25 changed back*/
         if (err != 0)
	     {
            printf("\nPCO_SetRecorderSubmode (hex): %lx\n", err);
            /*sprintf_s(errbuffer, errbuffer_size*sizeof(char), "\nPCO_SetRecorderSubmode (hex): %lx\n", err);*/
            goto abnormal;
	     }

         // all the images taken be stored
         err = SetAcquireMode(hCamera, 0);

         // prepare delay exposure time
         dwExposure = caget_double(chan_expt);
         expbase = 2;
         err = SetDelayExposureTime(hCamera, // Timebase: 0-ns; 1-us; 2-ms
         0,		// DWORD dwDelay
         (DWORD)dwExposure,
         0,		// WORD wTimeBaseDelay,
         expbase);	// WORD wTimeBaseExposure

         if (err != 0)
	     {
            sprintf_s(errbuffer, errbuffer_size*sizeof(char), "\nPCO_SetDelayExposureTime (hex): %lx\n", err);
            goto abnormal;
	     }
         else
            printf("\nExposureTime-->%d ms\n", (int)dwExposure);


	     /***********************************************************
         Partition Camera RAM and set segment 1 to active.
         Recording state must be 0 (already done previously).
         *************************************************************/

         err = SetCameraRamSegmentSize(hCamera, dwRamSegSize);
         if (err != 0)
	     {
            sprintf_s(errbuffer, errbuffer_size*sizeof(char), "\nSetCameraRamSegmentSize(hex): %lx\n", err);
            goto abnormal;
	     }

         err = GetCameraRamSegmentSize(hCamera,dwRamSegSize);
         if (err != 0)
	     {
            sprintf_s(errbuffer, errbuffer_size*sizeof(char), "\nGetCameraRamSegmentSize(hex): %lx\n", err);
            goto abnormal;
	     }
	     printf("Camera RAM segment sizes:\n");
	     for (i=0;i<4;i++) {
            printf("Segment %d: size %d\n",i+1,dwRamSegSize[i]);
	     }

         wActSeg=1;
         err = SetActiveRamSegment(hCamera, wActSeg);
         if (err != 0)
	     {
            sprintf_s(errbuffer, errbuffer_size*sizeof(char), "\nSetActiveRamSegment(hex): %lx\n", err);
            goto abnormal;
	     }

         /***********************************************************
         ArmCamera validates settings.
         (recorder must be turned off to ArmCamera)
         *************************************************************/

         err = ArmCamera(hCamera);
         if (err != 0)
	     {
            sprintf_s(errbuffer, errbuffer_size*sizeof(char), "\nPCO_ArmCamera(hex): %lx\n", err);
            goto abnormal;
	     }

         imgsize = wXResAct*wYResAct*2;
         bufsize = imgsize;

         if (bbufferextern)
	     {
            if (bufsize % 0x1000)
	        {
               bufsize = imgsize / 0x1000;
               bufsize += 2;
               bufsize *= 0x1000;
	        }
            else
               bufsize += 0x1000;

            wBuf = (WORD*)malloc(bufsize);
	     }
         else
            wBuf = NULL;

	     /*************************************************************
	     Preset buffer structure
	     **************************************************************/

	     for (x=0;x<nr_of_buffer;x++) {
		    picbuffer[x].sBufNr=-1;
		    picbuffer[x].size=bufsize;
		    picbuffer[x].wBuf=NULL;
		    picbuffer[x].hEvent=NULL;
            err = AllocateBuffer(hCamera, &picbuffer[x].sBufNr, picbuffer[x].size, &picbuffer[x].wBuf, &picbuffer[x].hEvent);
            if (err != 0)
		    {
				sprintf_s(errbuffer, errbuffer_size*sizeof(char), "\nPCO_AllocateBuffer #%i error(hex): %lx\n",x, err);
               goto abnormal;
		    }
		    bl[x].sBufNr=picbuffer[x].sBufNr;
         }

	     err = GetCOCRuntime(hCamera, &dwTime_s, &dwTime_ns);
         if (err != 0)
	     {
            sprintf_s(errbuffer, errbuffer_size*sizeof(char), "\nPCO_GetCOCRuntime error(hex): %lx\n", err);
            goto abnormal;
	     }
	     fps=(double)dwTime_s*1000.+((double)dwTime_ns/1000000.);
	     printf("Frametime %lf ms\n",fps);
	     caput_double(chan_frame,fps);

	     k=0;
	     ii=0;
	     do {
		    printf("Waiting for trigger ...\n");

		    do {
			   Sleep(1000);
		       trigger=(int)caget_double(chan_snap);
			   tomostart=(int)caget_double(chan_go);
		    } while (trigger==0 && tomostart==1);

		    k++;
		    if (k>5) {
			   sprintf_s(errbuffer, errbuffer_size*sizeof(char), "\nToo many triggers!!!\n");
			   goto abnormal;
		    }

		    if (tomostart==1) {
		       nimg[k-1]=(int)caget_double(chan_nimg);
		       if (k==2 || k==4)
			      nimg[k-1]=nimg[k-1]+1;
	           cimg[k-1]=(int)caget_double(chan_cimg);
		       Sleep(1000);
/*		   ccdnADC=1;
		   ccdnclock=10;
		   ccdreadout = (452*wYResAct*10)/(2048*ccdnADC*ccdnclock);
		   printf("Read out time %d\n",ccdreadout);

		   if (dwExposure>ccdreadout)
			 scantime=(int)dwExposure*nimg[k-1]*1.1;
		   else
			 scantime=ccdreadout*nimg[k-1]*1.1;*/

		       wActSeg=k;
               err = SetActiveRamSegment(hCamera, wActSeg);
               if (err != 0)
		       {
                  sprintf_s(errbuffer, errbuffer_size*sizeof(char), "\nSetActiveRamSegment(hex): %lx\n", err);
                  goto abnormal;
		       }
               err = ArmCamera(hCamera);
               if (err != 0)
		       {
                  sprintf_s(errbuffer, errbuffer_size*sizeof(char), "\nPCO_ArmCamera(hex): %lx\n", err);
                  goto abnormal;
		       }

		       // to turn recorder

		       err = SetRecordingState(hCamera, 0x0001);
	           for (x=0;x<nr_of_buffer;x++) {
		          if (bbufferextern)
                     err = AddBufferEx(hCamera, 0, 0, picbuffer[x].sBufNr, wXResAct, wYResAct, caminfo.wDynResDESC);
                  else
                     err = AddBuffer(hCamera, 0, 0, picbuffer[x].sBufNr);
                  if (err != 0) {
                     PCO_GetErrorText(err, errbuffer, 400);

                     printf("Here you can see the error explanation:\r\n%s", errbuffer);
                     sprintf_s(errbuffer, errbuffer_size*sizeof(char), "\nPCO_AddBuffer error(hex): %lx\n", err);
                     goto abnormal;
			      }
               }
		       /*printf("nimg[%d] %d\n",k-1,nimg[k-1]);*/


		       if (k==1) {
			      err=caget_char(chan_folder,foldername);
	              err=caget_char(chan_sample,samplename);
                  ext[0]='.';
	              ext[1]='t';
	              ext[2]='i';
	              ext[3]='f';
		       }

		       for (i=0;i<nimg[k-1];) {
			      err=WaitforBuffer(hCamera,buflist_count,bl,PicTimeOut);
                  if (err != 0)
			      {
                     PCO_GetErrorText(err, errbuffer, 400);

                     printf("Here you can see the error explanation:\r\n%s", errbuffer);
                     sprintf_s(errbuffer, errbuffer_size*sizeof(char), "\nPCO_WaitforBuffer(hex): %lx\n", err);
                     goto abnormal;
			      }

			   /*err = GetCOCRuntime(hCamera, &dwTime_s, &dwTime_ns);
               if (err != 0)
			   {
                  sprintf_s(errbuffer, errbuffer_size*sizeof(char), "\nPCO_GetCOCRuntime error(hex): %lx\n", err);
                  goto abnormal;
			   }
	           fps=(double)dwTime_s*1000.+((double)dwTime_ns/1000000.);
	           printf("Frametime %lf ms\n",fps);*/

                  for (x=0;x<nr_of_buffer;x++) {
				     if ((bl[x].dwStatusDll&0x00008000) && i<nimg[k-1]) {
					    i++;
					    //printf("buf %d done status %x\n",x,bl[x].dwStatusDrv);
					    if (k==2 || k==4) {
					 	   //printf("i %d cimg %d k %d\n",i,cimg[k-1],k);
					   	   if (i>1) {
							   sprintf(string,"%s%s%.4d%s",foldername,samplename,i+cimg[k-1]-2,ext);
                               writeTIFF16(string,picbuffer[x].wBuf,wXResAct,wYResAct);
							   printf("Image %s stored\n",string);

						   }
					    } else {
 					       sprintf(string,"%s%s%.4d%s",foldername,samplename,i+cimg[k-1]-1,ext);
                           writeTIFF16(string,picbuffer[x].wBuf,wXResAct,wYResAct);
                           printf("Image %s stored\n",string);
					    }

		                if (bbufferextern)
                           err = AddBufferEx(hCamera, 0, 0, picbuffer[x].sBufNr, wXResAct, wYResAct, caminfo.wDynResDESC);
                        else
                           err = AddBuffer(hCamera, 0, 0, picbuffer[x].sBufNr);
                        if (err != 0) {
                           PCO_GetErrorText(err, errbuffer, 400);

                           printf("Here you can see the error explanation:\r\n%s", errbuffer);
                           sprintf_s(errbuffer, errbuffer_size*sizeof(char), "\nPCO_AddBuffer error(hex): %lx\n", err);
                           goto abnormal;
					    }
				     }
			      }
			      if (((bl[0].dwStatusDll&0x00008000)==0) &&
				      ((bl[1].dwStatusDll&0x00008000)==0) &&
                      ((bl[2].dwStatusDll&0x00008000)==0) &&
				      ((bl[3].dwStatusDll&0x00008000)==0)) {
				      printf("Buffers have wrong status after waiting for return\n");
				      for (x=0;x<nr_of_buffer;x++) {
					     printf("Buffer %d: dll %x drv %x\n",x,bl[x].dwStatusDll,bl[x].dwStatusDrv);
				      }
                      goto abnormal;
			      }

			      angle_old=angle;
		          angle=caget_double(chan_angle);
			      /*if ((k==3) && (fabs(angle-angle_old)<0.001)) {
				      printf("Warning!!! Angle %f angle_old %f\n",angle,angle_old);
			      }*/
			      if ((k==3) && (fabs(angle-angle_old)<0.001) && (angle>rotsto) && (rotsto!=rotsta)) {
				     printf("Entering wait loop\n");
				     printf("angle %f angle_old %f\n",angle,angle_old);

				     // Wait until all buffers are done
		             do {
			            err=WaitforBuffer(hCamera,buflist_count,bl,50);
                        if (err != 0)
					    {
						  break;
			            }
                        for (x=0;x<nr_of_buffer;x++) {
				           if ((bl[x].dwStatusDll & 0x00008000) && (bl[x].dwStatusDrv==0)) {
					          i++;
					          //printf("buf %d done status %x\n",x,bl[x].dwStatusDrv);
 			                  sprintf(string,"%s%s%.4d%s",foldername,samplename,i+cimg[k-1]-1,ext);

                              writeTIFF16(string,picbuffer[x].wBuf,wXResAct,wYResAct);
                              if (!err)
                                 printf("Image %s stored\n",string);
                              else
                                 printf("Image not saved because of file error");
					          printf("buf %d done status %x\n",x,bl[x].dwStatusDrv);
                              ResetEvent(picbuffer[x].hEvent);
						   }
					    }
				     } while (err==0);

		             err = SetRecordingState(hCamera, 0x0000);
                     if (err != 0)
				     {
                        sprintf_s(errbuffer, errbuffer_size*sizeof(char), "\nPCO_SetRecordingState(hex): %lx\n", err);
                        goto abnormal;
				     }
				     err = GetNumberOfImagesInSegment(hCamera,wActSeg,&dwValidImageCnt,&dwMaxImageCnt);
				     printf("Remaining images %d\n",dwValidImageCnt);

				     printf("Reading remaining images %d\n",nimg[k-1]-i);
				     /*memset(bl,0,sizeof(bl));
				     bl[0].sBufNr=picbuffer[0].sBufNr;*/
				     n=1;
                     do {
					    i++;
                        //err = GetImage(hCamera, wActSeg, n, n, picbuffer[0].sBufNr);
					    printf("i %d n %d\n",i,n);
					    if (bbufferextern) {
                           err = AddBufferEx(hCamera, n, n, picbuffer[0].sBufNr, wXResAct, wYResAct, caminfo.wDynResDESC);
                        } else {
                           err = AddBuffer(hCamera, n, n, picbuffer[0].sBufNr);
                        }

                        if (err != 0) {
                           PCO_GetErrorText(err, errbuffer, 400);

                           printf("Here you can see the error explanation:\r\n%s", errbuffer);
                           sprintf_s(errbuffer, errbuffer_size*sizeof(char), "\nPCO_AddBuffer error(hex): %lx\n", err);
                           goto abnormal;
					    }
 			            sprintf(string,"%s%s%.4d%s",foldername,samplename,i+cimg[k-1]-1,ext);

                        writeTIFF16(string,picbuffer[0].wBuf,wXResAct,wYResAct);
                        if (!err)
                           printf("Image %s stored\n",string);
                        else
                           printf("Image not saved because of file error");
					    n++;

				     } while (i<nimg[k-1]);
			      }

			      tomostart=(int)caget_double(chan_go);
			      if (tomostart==0) {
				     printf("The scan has been interrupted!\n");
				     i=nimg[k-1];
			      }
		       }

			   err = SetRecordingState(hCamera, 0x0000);

		       err=CancelImages(hCamera);
               if (err != 0)
		       {
                  sprintf_s(errbuffer, errbuffer_size*sizeof(char), "\nPCO_CancelImages(hex): %lx\n", err);
                  goto abnormal;
		       }

		       trigger=0;
		       err=caput_double(chan_snap,trigger);

		    } /* End if */
	     } while (tomostart==1);

	     for (x=0;x<nr_of_buffer;x++) {
            err = FreeBuffer(hCamera, picbuffer[x].sBufNr);
            if (err != 0) {
               sprintf_s(errbuffer, errbuffer_size*sizeof(char), "\nPCO_FreeBuffer error(hex): %lx\n", err);
               goto abnormal;
		    }
	     }

		 // Clear and reset variables for buffers
		 free(wBuf);
		 free(bwBuf);
		 free(fitBuf);
		 free(flatBuf);
		 isflat=0;
		 snapTaken=false;
	 }

	 /* Resetting the camRAM to initial state to avoid problems with ImagePro */

	 dwRamSegSize[0]=dwRamSize;
     dwRamSegSize[1]=0;
     dwRamSegSize[2]=0;
     dwRamSegSize[3]=0;

	 err = SetCameraRamSegmentSize(hCamera, dwRamSegSize);
     if (err != 0)
	 {
       sprintf_s(errbuffer, errbuffer_size*sizeof(char), "\nSetCameraRamSegmentSize(hex): %lx\n", err);
       goto abnormal;
	 }

	 wActSeg=1;
     err = SetActiveRamSegment(hCamera, wActSeg);
     if (err != 0)
	 {
       sprintf_s(errbuffer, errbuffer_size*sizeof(char), "\nSetActiveRamSegment(hex): %lx\n", err);
       goto abnormal;
	 }

	 /*printf("Waiting for next scan ...\n");*/
     err = SetTriggerMode(hCamera, 0x0001);
     if (err != 0)
	 {
        sprintf_s(errbuffer, errbuffer_size*sizeof(char), "\nPCO_SetTriggerMode error (hex): %lx\n", err);
        goto abnormal;
	 }
	 
      
     if (hCamera != NULL)
		  err = CloseCamera(&hCamera);
  } while (1);

  printf("\r\nClosing program without error.");
  return 0;

abnormal:
  printf(errbuffer);
  printf("Refer to PCO_err.h for explanation of some error codes\n");
  for (x=0;x<nr_of_buffer;x++) {
     if (picbuffer[x].sBufNr >= 0)
	  	err = FreeBuffer(hCamera, picbuffer[x].sBufNr);
  }
  if (hCamera != NULL)
		  err = CloseCamera(&hCamera);
  do {
  Sleep(5000);
  } while (1);
  exit(-1);
  return -1;
}


bool AnalyzeImage(void) {
       double thavg,thstd;
	   long cutoff;
       bool isgood=false;
	   validBW=false;
       // kImage is ImageProcessing Library (selfishly named)
       if (snapTaken) {
		   // Turn on calculation field
		   recalcstart=1;
	       err=caput_double(chan_align_recalc,recalcstart);
		   cutoff=(double)caget_double(chan_align_cutoff);
	       cSnapShot=new kImage(wBuf,flatBuf,wXResAct,wYResAct,(long) cutoff,isflat);
		   // Set RowAvg
		   cSnapShot->rowAvg=(double)caget_double(chan_align_rowavg);
		   cSnapShot->minTransmission=(double)caget_double(chan_align_mintrans);
		   cSnapShot->maxTransmission=(double)caget_double(chan_align_maxtrans);

	       thavg=(double)caget_double(chan_align_thavg);
	       thstd=(double)caget_double(chan_align_thstd);

	       // Run Threshold
		   cSnapShot->minSamplePct=(double)caget_double(chan_align_minpct);
			

	       cSnapShot->maskmode=(double)caget_double(chan_align_maskmode);
	       cSnapShot->readmode=(double)caget_double(chan_align_readmode);
		   cSnapShot->threshold(thavg,thstd);

	       // Run Fitting Code

			isgood=cSnapShot->fitParameters();
			err=caput_double(chan_align_good,isgood);
			// Find Edges
			cSnapShot->findBoundaries();
			// Write to Epics Channels
			err=caput_double(chan_align_theta,cSnapShot->angle);
			err=caput_double(chan_align_xoffset,cSnapShot->xoffset);
			err=caput_double(chan_align_yoffset,cSnapShot->yoffset);
			err=caput_double(chan_align_width,cSnapShot->meanW);
		    err=caput_double(chan_align_imavg,cSnapShot->mean);
		    err=caput_double(chan_align_imstd,cSnapShot->std);

		    err=caput_double(chan_align_pctunder,cSnapShot->pctunder);
		    err=caput_double(chan_align_pctbetween,cSnapShot->pctbetween);
		    err=caput_double(chan_align_pctover,cSnapShot->pctover);
			err=caput_double(chan_align_pctsaturated,cSnapShot->pctsaturated);
			err=caput_double(chan_align_top,cSnapShot->minY);
			err=caput_double(chan_align_bottom,cSnapShot->maxY);
			err=caput_double(chan_align_height,cSnapShot->wY);

	       // Release Image
	       // This code isn't quite ready yet
	       //cSnapShot.corrImage(wBuf); // Save flat field corrected image
	       if (saveimg) {
					
					cSnapShot->corrImage(bwBuf);
					//cSnapShot->fitImage(fitBuf);
					cSnapShot->corrImage(wBuf); // Save flat field corrected image
					validBW=true;
			}
		   delete cSnapShot;
       } else {
       		printf("Problem Analyzing Snap Shot: FLAT:%i, SNAP:%i\n",isflat,snapTaken);
	}
	   // Turn off calculation field
		   recalcstart=0;
	       err=caput_double(chan_align_recalc,recalcstart);
       return isgood;
}

int getlib(void)
{
  DWORD liberror;
  SC2Lib = LoadLibrary("SC2_Cam");
  if (SC2Lib == NULL)
  {
	   liberror = GetLastError();
     return liberror;
  }

  if ((GetGeneral = (int(__stdcall *)(HANDLE ph, PCO_General *strGeneral))
    GetProcAddress(SC2Lib, "PCO_GetGeneral")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetCameraType = (int(__stdcall *)(HANDLE ph, PCO_CameraType *strCamType))
    GetProcAddress(SC2Lib, "PCO_GetCameraType")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetCameraHealthStatus = (int(__stdcall *)(HANDLE ph, DWORD* dwWarn, DWORD* dwErr, DWORD* dwStatus))
    GetProcAddress(SC2Lib, "PCO_GetCameraHealthStatus")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((ResetSettingsToDefault = (int(__stdcall *)(HANDLE ph))
    GetProcAddress(SC2Lib, "PCO_ResetSettingsToDefault")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((InitiateSelftestProcedure = (int(__stdcall *)(HANDLE ph))
    GetProcAddress(SC2Lib, "PCO_InitiateSelftestProcedure")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetTemperature = (int(__stdcall *)(HANDLE ph, SHORT* sCCDTemp, SHORT* sCamTemp, SHORT* sPowTemp))
    GetProcAddress(SC2Lib, "PCO_GetTemperature")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetSensorStruct = (int(__stdcall *)(HANDLE ph, PCO_Sensor *strSensor))
    GetProcAddress(SC2Lib, "PCO_GetSensorStruct")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((SetSensorStruct = (int(__stdcall *)(HANDLE ph, PCO_Sensor *strSensor))
    GetProcAddress(SC2Lib, "PCO_SetSensorStruct")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetCameraDescription = (int(__stdcall *)(HANDLE ph, PCO_Description *strDescription))
    GetProcAddress(SC2Lib, "PCO_GetCameraDescription")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetSensorFormat = (int(__stdcall *)(HANDLE ph, WORD* wSensor))
    GetProcAddress(SC2Lib, "PCO_GetSensorFormat")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((SetSensorFormat = (int(__stdcall *)(HANDLE ph, WORD wSensor))
    GetProcAddress(SC2Lib, "PCO_SetSensorFormat")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetSizes = (int(__stdcall *)(HANDLE ph, WORD *wXResAct, WORD *wYResAct, WORD *wXResMax, WORD *wYResMax))
    GetProcAddress(SC2Lib, "PCO_GetSizes")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetROI = (int(__stdcall *)(HANDLE ph, WORD *wRoiX0, WORD *wRoiY0, WORD *wRoiX1, WORD *wRoiY1))
    GetProcAddress(SC2Lib, "PCO_GetROI")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((SetROI = (int(__stdcall *)(HANDLE ph, WORD wRoiX0, WORD wRoiY0, WORD wRoiX1, WORD wRoiY1))
    GetProcAddress(SC2Lib, "PCO_SetROI")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetBinning = (int(__stdcall *)(HANDLE ph, WORD *wBinHorz, WORD *wBinVert))
    GetProcAddress(SC2Lib, "PCO_GetBinning")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((SetBinning = (int(__stdcall *)(HANDLE ph, WORD wBinHorz, WORD wBinVert))
    GetProcAddress(SC2Lib, "PCO_SetBinning")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetPixelRate = (int(__stdcall *)(HANDLE ph, DWORD *dwPixelRate))
    GetProcAddress(SC2Lib, "PCO_GetPixelRate")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((SetPixelRate = (int(__stdcall *)(HANDLE ph, DWORD dwPixelRate))
    GetProcAddress(SC2Lib, "PCO_SetPixelRate")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetConversionFactor = (int(__stdcall *)(HANDLE ph, WORD *wConvFact))
    GetProcAddress(SC2Lib, "PCO_GetConversionFactor")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((SetConversionFactor = (int(__stdcall *)(HANDLE ph, WORD wConvFact))
    GetProcAddress(SC2Lib, "PCO_SetConversionFactor")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetDoubleImageMode = (int(__stdcall *)(HANDLE ph, WORD *wDoubleImage))
    GetProcAddress(SC2Lib, "PCO_GetDoubleImageMode")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((SetDoubleImageMode = (int(__stdcall *)(HANDLE ph, WORD wDoubleImage))
    GetProcAddress(SC2Lib, "PCO_SetDoubleImageMode")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetADCOperation = (int(__stdcall *)(HANDLE ph, WORD *wADCOperation))
    GetProcAddress(SC2Lib, "PCO_GetADCOperation")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((SetADCOperation = (int(__stdcall *)(HANDLE ph, WORD wADCOperation))
    GetProcAddress(SC2Lib, "PCO_SetADCOperation")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetIRSensitivity = (int(__stdcall *)(HANDLE ph, WORD *wIR))
    GetProcAddress(SC2Lib, "PCO_GetIRSensitivity")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((SetIRSensitivity = (int(__stdcall *)(HANDLE ph, WORD wIR))
    GetProcAddress(SC2Lib, "PCO_SetIRSensitivity")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetCoolingSetpointTemperature = (int(__stdcall *)(HANDLE ph, SHORT *sCoolSet))
    GetProcAddress(SC2Lib, "PCO_GetCoolingSetpointTemperature")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((SetCoolingSetpointTemperature = (int(__stdcall *)(HANDLE ph, SHORT sCoolSet))
    GetProcAddress(SC2Lib, "PCO_SetCoolingSetpointTemperature")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetOffsetMode = (int(__stdcall *)(HANDLE ph, WORD *wOffsetRegulation))
    GetProcAddress(SC2Lib, "PCO_GetOffsetMode")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((SetOffsetMode = (int(__stdcall *)(HANDLE ph, WORD wOffsetRegulation))
    GetProcAddress(SC2Lib, "PCO_SetOffsetMode")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetNoiseFilterMode = (int(__stdcall *)(HANDLE ph, WORD *wNoiseFilterMode))
    GetProcAddress(SC2Lib, "PCO_GetNoiseFilterMode")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((SetNoiseFilterMode = (int(__stdcall *)(HANDLE ph, WORD wNoiseFilterMode))
    GetProcAddress(SC2Lib, "PCO_SetNoiseFilterMode")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetTimingStruct = (int(__stdcall *)(HANDLE ph, PCO_Timing *strTiming))
    GetProcAddress(SC2Lib, "PCO_GetTimingStruct")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((SetTimingStruct = (int(__stdcall *)(HANDLE ph, PCO_Timing *strTiming))
    GetProcAddress(SC2Lib, "PCO_SetTimingStruct")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetDelayExposureTime = (int(__stdcall *)(HANDLE ph, DWORD* dwDelay, DWORD* dwExposure, WORD* wTimeBaseDelay, WORD* wTimeBaseExposure))
    GetProcAddress(SC2Lib, "PCO_GetDelayExposureTime")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((SetDelayExposureTime = (int(__stdcall *)(HANDLE ph, DWORD dwDelay, DWORD dwExposure, WORD wTimeBaseDelay, WORD wTimeBaseExposure))
    GetProcAddress(SC2Lib, "PCO_SetDelayExposureTime")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetDelayExposureTimeTable = (int(__stdcall *)(HANDLE ph, DWORD* dwDelay, DWORD* dwExposure, WORD* wTimeBaseDelay, WORD* wTimeBaseExposure, WORD wCount))
    GetProcAddress(SC2Lib, "PCO_GetDelayExposureTimeTable")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((SetDelayExposureTimeTable = (int(__stdcall *)(HANDLE ph, DWORD* dwDelay, DWORD* dwExposure, WORD wTimeBaseDelay, WORD wTimeBaseExposure, WORD wCount))
    GetProcAddress(SC2Lib, "PCO_SetDelayExposureTimeTable")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetTriggerMode = (int(__stdcall *)(HANDLE ph, WORD* wTriggerMode))
    GetProcAddress(SC2Lib, "PCO_GetTriggerMode")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((SetTriggerMode = (int(__stdcall *)(HANDLE ph, WORD wTriggerMode))
    GetProcAddress(SC2Lib, "PCO_SetTriggerMode")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((ForceTrigger = (int(__stdcall *)(HANDLE ph, WORD *wTriggered))
    GetProcAddress(SC2Lib, "PCO_ForceTrigger")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetCameraBusyStatus = (int(__stdcall *)(HANDLE ph, WORD* wCameraBusyState))
    GetProcAddress(SC2Lib, "PCO_GetCameraBusyStatus")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetPowerDownMode = (int(__stdcall *)(HANDLE ph, WORD* wPowerDownMode))
    GetProcAddress(SC2Lib, "PCO_GetPowerDownMode")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((SetPowerDownMode = (int(__stdcall *)(HANDLE ph, WORD wPowerDownMode))
    GetProcAddress(SC2Lib, "PCO_SetPowerDownMode")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetUserPowerDownTime = (int(__stdcall *)(HANDLE ph, DWORD* dwPowerDownTime))
    GetProcAddress(SC2Lib, "PCO_GetUserPowerDownTime")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((SetUserPowerDownTime = (int(__stdcall *)(HANDLE ph, DWORD dwPowerDownTime))
    GetProcAddress(SC2Lib, "PCO_SetUserPowerDownTime")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetExpTrigSignalStatus = (int(__stdcall *)(HANDLE ph, WORD* wExpTrgSignal))
    GetProcAddress(SC2Lib, "PCO_GetExpTrigSignalStatus")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetCOCRuntime = (int(__stdcall *)(HANDLE ph, DWORD* dwTime_s, DWORD* dwTime_us))
    GetProcAddress(SC2Lib, "PCO_GetCOCRuntime")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetStorageStruct = (int(__stdcall *)(HANDLE ph, PCO_Storage *strStorage))
    GetProcAddress(SC2Lib, "PCO_GetStorageStruct")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((SetStorageStruct = (int(__stdcall *)(HANDLE ph, PCO_Storage *strStorage))
    GetProcAddress(SC2Lib, "PCO_SetStorageStruct")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetCameraRamSize = (int(__stdcall *)(HANDLE ph, DWORD* dwRamSize, WORD* wPageSize))
    GetProcAddress(SC2Lib, "PCO_GetCameraRamSize")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetCameraRamSegmentSize = (int(__stdcall *)(HANDLE ph, DWORD* dwRamSegSize))
    GetProcAddress(SC2Lib, "PCO_GetCameraRamSegmentSize")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((SetCameraRamSegmentSize = (int(__stdcall *)(HANDLE ph, DWORD* dwRamSegSize))
    GetProcAddress(SC2Lib, "PCO_SetCameraRamSegmentSize")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((ClearRamSegment = (int(__stdcall *)(HANDLE ph))
    GetProcAddress(SC2Lib, "PCO_ClearRamSegment")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetActiveRamSegment = (int(__stdcall *)(HANDLE ph, WORD* wActSeg))
    GetProcAddress(SC2Lib, "PCO_GetActiveRamSegment")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((SetActiveRamSegment = (int(__stdcall *)(HANDLE ph, WORD wActSeg))
    GetProcAddress(SC2Lib, "PCO_SetActiveRamSegment")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetRecordingStruct = (int(__stdcall *)(HANDLE ph, PCO_Recording *strRecording))
    GetProcAddress(SC2Lib, "PCO_GetRecordingStruct")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((SetRecordingStruct = (int(__stdcall *)(HANDLE ph, PCO_Recording *strRecording))
    GetProcAddress(SC2Lib, "PCO_SetRecordingStruct")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetStorageMode = (int(__stdcall *)(HANDLE ph, WORD* wStorageMode))
    GetProcAddress(SC2Lib, "PCO_GetStorageMode")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((SetStorageMode = (int(__stdcall *)(HANDLE ph, WORD wStorageMode))
    GetProcAddress(SC2Lib, "PCO_SetStorageMode")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetRecorderSubmode = (int(__stdcall *)(HANDLE ph, WORD* wRecSubmode))
    GetProcAddress(SC2Lib, "PCO_GetRecorderSubmode")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((SetRecorderSubmode = (int(__stdcall *)(HANDLE ph, WORD wRecSubmode))
    GetProcAddress(SC2Lib, "PCO_SetRecorderSubmode")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetRecordingState = (int(__stdcall *)(HANDLE ph, WORD* wRecState))
    GetProcAddress(SC2Lib, "PCO_GetRecordingState")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((SetRecordingState = (int(__stdcall *)(HANDLE ph, WORD wRecState))
    GetProcAddress(SC2Lib, "PCO_SetRecordingState")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((ArmCamera = (int(__stdcall *)(HANDLE ph))
    GetProcAddress(SC2Lib, "PCO_ArmCamera")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetAcquireMode = (int(__stdcall *)(HANDLE ph, WORD* wAcquMode))
    GetProcAddress(SC2Lib, "PCO_GetAcquireMode")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((SetAcquireMode = (int(__stdcall *)(HANDLE ph, WORD wAcquMode))
    GetProcAddress(SC2Lib, "PCO_SetAcquireMode")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetAcqEnblSignalStatus = (int(__stdcall *)(HANDLE ph, WORD* wAcquEnableState))
    GetProcAddress(SC2Lib, "PCO_GetAcqEnblSignalStatus")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((SetDateTime = (int(__stdcall *)(HANDLE ph, BYTE ucDay, BYTE ucMonth, WORD wYear, WORD wHour, BYTE ucMin, BYTE ucSec))
    GetProcAddress(SC2Lib, "PCO_SetDateTime")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetTimestampMode = (int(__stdcall *)(HANDLE ph, WORD* wTimeStampMode))
    GetProcAddress(SC2Lib, "PCO_GetTimestampMode")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((SetTimestampMode = (int(__stdcall *)(HANDLE ph, WORD wTimeStampMode))
    GetProcAddress(SC2Lib, "PCO_SetTimestampMode")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetImageStruct = (int(__stdcall *)(HANDLE ph, PCO_Image *strImage))
    GetProcAddress(SC2Lib, "PCO_GetImageStruct")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetSegmentStruct = (int(__stdcall *)(HANDLE ph, WORD wSegment, PCO_Segment *strSegment))
    GetProcAddress(SC2Lib, "PCO_GetSegmentStruct")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetSegmentImageSettings = (int(__stdcall *)(HANDLE ph, WORD wSegment, WORD* wXRes, WORD* wYRes, WORD* wBinHorz, WORD* wBinVert, WORD* wRoiX0, WORD* wRoiY0, WORD* wRoiX1, WORD* wRoiY1))
    GetProcAddress(SC2Lib, "PCO_GetSegmentImageSettings")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetNumberOfImagesInSegment = (int(__stdcall *)(HANDLE ph, WORD wSegment, DWORD* dwValidImageCnt, DWORD* dwMaxImageCnt))
    GetProcAddress(SC2Lib, "PCO_GetNumberOfImagesInSegment")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((OpenCamera = (int(__stdcall *)(HANDLE *ph, WORD wCamNum))
    GetProcAddress(SC2Lib, "PCO_OpenCamera")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((CloseCamera = (int(__stdcall *)(HANDLE ph))
    GetProcAddress(SC2Lib, "PCO_CloseCamera")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((AllocateBuffer = (int(__stdcall *)(HANDLE ph, SHORT* sBufNr, DWORD size, WORD** wBuf, HANDLE *hEvent))
    GetProcAddress(SC2Lib, "PCO_AllocateBuffer")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((FreeBuffer = (int(__stdcall *)(HANDLE ph, SHORT sBufNr))
    GetProcAddress(SC2Lib, "PCO_FreeBuffer")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((AddBuffer = (int(__stdcall *)(HANDLE ph, DWORD dw1stImage, DWORD dwLastImage, SHORT sBufNr))
    GetProcAddress(SC2Lib, "PCO_AddBuffer")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((AddBufferEx = (int(__stdcall *)(HANDLE ph, DWORD dw1stImage, DWORD dwLastImage, SHORT sBufNr, WORD wXRes, WORD wYRes, WORD wBitRes))
    GetProcAddress(SC2Lib, "PCO_AddBufferEx")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetBufferStatus = (int(__stdcall *)(HANDLE ph, SHORT sBufNr, DWORD *dwStatusDll, DWORD *dwStatusDrv))
    GetProcAddress(SC2Lib, "PCO_GetBufferStatus")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((WaitforBuffer = (int(__stdcall *)(HANDLE ph, int nr_of_buffer, PCO_Buflist *bl, int timeout))
    GetProcAddress(SC2Lib, "PCO_WaitforBuffer")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((RemoveBuffer = (int(__stdcall *)(HANDLE ph))
    GetProcAddress(SC2Lib, "PCO_RemoveBuffer")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetImage = (int(__stdcall *)(HANDLE ph, WORD dwSegment, DWORD dw1stImage, DWORD dwLastImage, SHORT sBufNr))
    GetProcAddress(SC2Lib, "PCO_GetImage")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((GetPendingBuffer = (int(__stdcall *)(HANDLE ph, int *count))
    GetProcAddress(SC2Lib, "PCO_GetPendingBuffer")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((CancelImages = (int(__stdcall *)(HANDLE ph))
    GetProcAddress(SC2Lib, "PCO_CancelImages")) == NULL)
    return SC2_ERROR_SDKDLL;
  if ((CheckDeviceAvailability = (int(__stdcall *)(HANDLE ph, WORD wNum))
    GetProcAddress(SC2Lib, "PCO_CheckDeviceAvailability")) == NULL)
    return SC2_ERROR_SDKDLL;
  return FALSE;
}


int store_b16(char *filename, int width, int height, void *buf)
{
  unsigned char *cptr;
  unsigned char *c1;
  int *b1;
  int e;

  HANDLE hfstore;
  unsigned long z, zz;
  DWORD headerl;
  //  char of[20];

  cptr = (unsigned char *)malloc(256);

  headerl = 128;

  c1 = cptr;
  *c1++ = 'P';                         // Begin PCO-Header PCO-
  *c1++ = 'C';
  *c1++ = 'O';
  *c1++ = '-';

  b1 = (int*)c1;

  // Data for Header
  *b1++ = (width*height*2) + headerl;
  *b1++ = headerl;
  *b1++ = width;
  *b1++ = height;

  // no special data
  *b1++ = 0;

  // Fill Header
  c1 = (unsigned char *)b1;
  for (; c1 < cptr + 128; )
    *c1++=0;

  hfstore = CreateFile(filename,
    GENERIC_WRITE,
    0,
    NULL,
    CREATE_ALWAYS,
    FILE_ATTRIBUTE_NORMAL | FILE_FLAG_SEQUENTIAL_SCAN,
    0);
  if (hfstore== INVALID_HANDLE_VALUE)
  {
    free(cptr);
    return (NOFILE);
  }


  z = headerl;
  e = WriteFile(hfstore, (void *)cptr, z, &zz, NULL);
  if ((e == 0) ||(z != zz))
  {
    CloseHandle(hfstore);
    DeleteFile(filename);
    free(cptr);
    return (NOFILE);
  }

  z = width*height*2;
  e = WriteFile(hfstore, (void *)buf, z, &zz, NULL);
  if ((e == 0) ||(z != zz))
  {
    CloseHandle(hfstore);
    DeleteFile(filename);
    free(cptr);
    return (NOFILE);
  }

  CloseHandle(hfstore);
  free(cptr);
  return 0;
}

int ca_search_routine(char *channel_name, chid *chan)
{
  int status;

  status=ca_search(channel_name,chan);
  SEVCHK(status,NULL);
  status = ca_pend_io(5.0);
  if (status != ECA_NORMAL) {
     SEVCHK(ca_clear_channel(*chan),NULL);
     printf("Not Found %s\n", channel_name);
     return -1;
  }

/*  printf("name:\t%s\n", ca_name(*chan));
  printf("native type:\t%d\n", ca_field_type(*chan));
  printf("native count:\t%lu\n", ca_element_count(*chan));*/
  return 0;
}

double caget_double(chid chan)
{
  int status;
  double value;

  status=ca_get(DBR_DOUBLE,chan,&value);
  SEVCHK(status,NULL);
  status = ca_pend_io(5.0);
  if (status != ECA_NORMAL) {
	  SEVCHK(ca_clear_channel(chan),NULL);
      printf("Not Found %s\n", chan);
     return -1;
  }
  return value;
}

int caget_char(chid chan, char *foldername)
{
  int status;

  status=ca_get(DBR_STRING,chan,foldername);
  SEVCHK(status,NULL);
  status = ca_pend_io(5.0);
  if (status != ECA_NORMAL) {
	  SEVCHK(ca_clear_channel(chan),NULL);
      printf("Not Found %s\n", chan);
     return -1;
  }
  return 0;
}

int caput_double(chid chan, double value)
{
  int status;

  status=ca_put(DBR_DOUBLE,chan,&value);
  SEVCHK(status,NULL);
  status = ca_pend_io(5.0);
  if (status != ECA_NORMAL) {
	  SEVCHK(ca_clear_channel(chan),NULL);
      printf("Not Found %s\n", chan);
     return -1;
  }
  return 0;
}

void writeTIFF16(char *nameout, WORD *buf, int width, int height)
{
       TIFF *image;
	   int totsize,i;

       /* Open the TIFF file */
       /*if ((image=TIFFOpen(nameout,"w")) == NULL) {
          printf("WriteTIFF: Could not open TIFF file for writing\n");
	   }*/
	   for (i=20; i>=0; i--) {
          if ((image=TIFFOpen(nameout,"w")) == NULL) {
             printf("WARNING: Could not open TIFF file for writing\n");
			 if (i!=0) {
				 Sleep(50);
			 } else {
				 printf("WriteTIFF: Could not open TIFF file for writing\n");
			 }
		  } else {
			  i=-1;
		  }
	   }
       /* We need to set some values for basic tags before we can add any data */
       TIFFSetField(image, TIFFTAG_IMAGEWIDTH, width);
       TIFFSetField(image, TIFFTAG_IMAGELENGTH, height);
       TIFFSetField(image, TIFFTAG_SAMPLESPERPIXEL, 1);
       TIFFSetField(image, TIFFTAG_BITSPERSAMPLE, 16);
       TIFFSetField(image, TIFFTAG_ROWSPERSTRIP, height);

       TIFFSetField(image, TIFFTAG_COMPRESSION, 1);
       TIFFSetField(image, TIFFTAG_PHOTOMETRIC, PHOTOMETRIC_MINISBLACK);
       TIFFSetField(image, TIFFTAG_FILLORDER, FILLORDER_MSB2LSB);
       TIFFSetField(image, TIFFTAG_PLANARCONFIG, 1);

       TIFFSetField(image, TIFFTAG_XRESOLUTION, 150.0);
       TIFFSetField(image, TIFFTAG_YRESOLUTION, 150.0);
       TIFFSetField(image, TIFFTAG_RESOLUTIONUNIT, RESUNIT_INCH);

       /* Write the information to the file */
       totsize=sizeof(unsigned short)*width*height;
       if (TIFFWriteEncodedStrip(image, 0, buf, totsize)!=totsize) {
	      printf("TIFFWriteEncodedStrip: Error\n");
	   }
	   /* Close the file */
	   TIFFClose(image);
}

void writeCTIFF(char *nameout, WORD *buf, bool *mask, bool *fitmask, int width, int height)
{
       TIFF *image;
       int totsize,i;
       unsigned char *tmp8;

       /* Open the TIFF file */
       /*if ((image=TIFFOpen(nameout,"w")) == NULL) {
          printf("WriteTIFF: Could not open TIFF file for writing\n");
	   }*/
       for (i=20; i>=0; i--) {
          if ((image=TIFFOpen(nameout,"w")) == NULL) {
             printf("WARNING: Could not open TIFF file for writing\n");
	     if (i!=0) {
		Sleep(50);
	     } else {
		printf("WriteTIFF: Could not open TIFF file for writing\n");
	     }
	  } else {
	     i=-1;
	  }
       }

       /* Conversion to 8 bit */
       tmp8=(unsigned char *) (malloc(sizeof(unsigned char)*width*height*3));
       for (i=0;i<(width*height);i++) {
		   
		   unsigned char cPix=(unsigned char)((float)buf[i]*255.0/65535.0);
		   tmp8[i*3]=0;
		   tmp8[i*3+1]=0;
		   tmp8[i*3+2]=0;
		   
		   if (!mask[i]) {
			   if (buf[i]>32676) {
				   //tmp8[i*3+1]=127;
				   tmp8[i*3]=cPix;
				   tmp8[i*3+2]=0;

				   
			   } else {
				   tmp8[i*3]=0;
				   tmp8[i*3+2]=127+cPix;
			   }
		   } else {
			   tmp8[i*3+1]=cPix;
		   }
		   //if (fitmask[i]) tmp8[i*3+2]=255;
       }

       /* We need to set some values for basic tags before we can add any data */
       TIFFSetField(image, TIFFTAG_IMAGEWIDTH, width);
       TIFFSetField(image, TIFFTAG_IMAGELENGTH, height);
       TIFFSetField(image, TIFFTAG_SAMPLESPERPIXEL, 3);
       TIFFSetField(image, TIFFTAG_BITSPERSAMPLE, 8);
       TIFFSetField(image, TIFFTAG_ROWSPERSTRIP, height);

       //TIFFSetField(image, TIFFTAG_COMPRESSION, COMPRESSION_DEFLATE);
	   TIFFSetField(image, TIFFTAG_COMPRESSION, COMPRESSION_LZW);
	   //TIFFSetField(image, TIFFTAG_COMPRESSION, 1);
	   TIFFSetField(image, TIFFTAG_PLANARCONFIG, PLANARCONFIG_CONTIG);
       TIFFSetField(image, TIFFTAG_PHOTOMETRIC, PHOTOMETRIC_RGB);
       TIFFSetField(image, TIFFTAG_FILLORDER, FILLORDER_MSB2LSB);

       TIFFSetField(image, TIFFTAG_XRESOLUTION, 150.0);
       TIFFSetField(image, TIFFTAG_YRESOLUTION, 150.0);
       TIFFSetField(image, TIFFTAG_RESOLUTIONUNIT, RESUNIT_INCH);

       /* Write the information to the file */
       totsize=sizeof(unsigned char)*width*height*3;
       if (TIFFWriteEncodedStrip(image, 0, tmp8, totsize)!=totsize) {
	   printf("TIFFWriteEncodedStrip: Error\n");
       }
       printf("Image written\n");
       /* Close the file */
       TIFFClose(image);
	   free(tmp8);
}

void writeTIFF8(char *nameout, WORD *buf, int width, int height)
{
       TIFF *image;
       int totsize,i;
       unsigned char *tmp8;

       /* Open the TIFF file */
       /*if ((image=TIFFOpen(nameout,"w")) == NULL) {
          printf("WriteTIFF: Could not open TIFF file for writing\n");
	   }*/
       for (i=20; i>=0; i--) {
          if ((image=TIFFOpen(nameout,"w")) == NULL) {
             printf("WARNING: Could not open TIFF file for writing\n");
	     if (i!=0) {
		Sleep(50);
	     } else {
		printf("WriteTIFF: Could not open TIFF file for writing\n");
	     }
	  } else {
	     i=-1;
	  }
       }

       /* Conversion to 8 bit */
       tmp8=(unsigned char *) (malloc(sizeof(unsigned char)*width*height));
       for (i=0;i<width*height;i++) {
	    tmp8[i]=(unsigned char)((float)buf[i]*255.0/65535.0);
       }

       /* We need to set some values for basic tags before we can add any data */
       TIFFSetField(image, TIFFTAG_IMAGEWIDTH, width);
       TIFFSetField(image, TIFFTAG_IMAGELENGTH, height);
       TIFFSetField(image, TIFFTAG_SAMPLESPERPIXEL, 1);
       TIFFSetField(image, TIFFTAG_BITSPERSAMPLE, 8);
       TIFFSetField(image, TIFFTAG_ROWSPERSTRIP, height);

       TIFFSetField(image, TIFFTAG_COMPRESSION, 1);
       TIFFSetField(image, TIFFTAG_PHOTOMETRIC, PHOTOMETRIC_MINISBLACK);
       TIFFSetField(image, TIFFTAG_FILLORDER, FILLORDER_MSB2LSB);
       TIFFSetField(image, TIFFTAG_PLANARCONFIG, 1);

       TIFFSetField(image, TIFFTAG_XRESOLUTION, 150.0);
       TIFFSetField(image, TIFFTAG_YRESOLUTION, 150.0);
       TIFFSetField(image, TIFFTAG_RESOLUTIONUNIT, RESUNIT_INCH);

       /* Write the information to the file */
       totsize=sizeof(unsigned char)*width*height;
       if (TIFFWriteEncodedStrip(image, 0, tmp8, totsize)!=totsize) {
	   printf("TIFFWriteEncodedStrip: Error\n");
       }
       printf("Image written\n");
       /* Close the file */
       TIFFClose(image);
	   free(tmp8);
}
void writeTIFF2(char *nameout, WORD *buf, int width, int height)
{
	   bool *tmp2;
	   tmp2=(bool *) (malloc(sizeof(bool)*width*height));
       double curVal;
	   for (i=0;i<width*height;i++) {
		   curVal=(double) 2.0*(buf[i]-WORD_MIN);
		   if (curVal>(WORD_MAX-WORD_MIN)) tmp2[i]=true;
		   else tmp2[i]=false;
       }
	   writeTIFF2(nameout,tmp2,width,height);
	   free(tmp2);
}
void writeTIFF2(char *nameout, bool *buf, int width, int height)
{
       TIFF *image;
       int totsize,i;

       /* Open the TIFF file */
       /*if ((image=TIFFOpen(nameout,"w")) == NULL) {
          printf("WriteTIFF: Could not open TIFF file for writing\n");
	   }*/
       for (i=20; i>=0; i--) {
          if ((image=TIFFOpen(nameout,"w")) == NULL) {
             printf("WARNING: Could not open TIFF file for writing\n");
	     if (i!=0) {
		Sleep(50);
	     } else {
		printf("WriteTIFF: Could not open TIFF file for writing\n");
	     }
	  } else {
	     i=-1;
	  }
       }



       /* We need to set some values for basic tags before we can add any data */
       TIFFSetField(image, TIFFTAG_IMAGEWIDTH, width);
       TIFFSetField(image, TIFFTAG_IMAGELENGTH, height);
       TIFFSetField(image, TIFFTAG_SAMPLESPERPIXEL, 1);
       TIFFSetField(image, TIFFTAG_BITSPERSAMPLE, 2);
       TIFFSetField(image, TIFFTAG_ROWSPERSTRIP, height);

       TIFFSetField(image, TIFFTAG_COMPRESSION, 1);
       TIFFSetField(image, TIFFTAG_PHOTOMETRIC, PHOTOMETRIC_MINISBLACK);
       TIFFSetField(image, TIFFTAG_FILLORDER, FILLORDER_MSB2LSB);
       TIFFSetField(image, TIFFTAG_PLANARCONFIG, 1);

       TIFFSetField(image, TIFFTAG_XRESOLUTION, 150.0);
       TIFFSetField(image, TIFFTAG_YRESOLUTION, 150.0);
       TIFFSetField(image, TIFFTAG_RESOLUTIONUNIT, RESUNIT_INCH);

       /* Write the information to the file */
       totsize=sizeof(bool)*width*height;
       if (TIFFWriteEncodedStrip(image, 0, buf, totsize)!=totsize) {
	   printf("TIFFWriteEncodedStrip: Error\n");
       }
       printf("Image written\n");
       /* Close the file */
       TIFFClose(image);
}

//nr_of_buffer:    number of buffer(s) to watch
//struct buflist:  includes buffer numbers as input
//                 and status of dll and drv in return, wenn event gesetzt

//timeout in ms


/*DWORD WaitForBuffer(HANDLE hCamera,int nr_of_buffer,Buflist *bl,int timeout)
{
  int x,ret_val;
  DWORD err;
  WORD* adr;
  HANDLE*  ev;
  int num=0;

  err=PCO_NOERROR;

  ev=(HANDLE*)malloc(nr_of_buffer*sizeof(HANDLE));
  if(ev==NULL)
   return PCO_ERROR_NOMEMORY;
  printf("memory allocated\n");

  for(x=0;x<nr_of_buffer;x++)
  {
	  printf("x %d\n",x);
   err=GetBuffer(hCamera,bl[x].sBufNr,&adr,&ev[x]);
   if(err==PCO_NOERROR)
   {
    bl[x].dwStatusDll=0;
    bl[x].dwStatusDrv=0;
   }
   else
   {
    printf("PCO_GetBuffer(,%d) return error %x \n",bl[x].sBufNr,err);
    ev[x]=(HANDLE)-1;
   }
  }

  ret_val=WaitForMultipleObjects(nr_of_buffer,ev,FALSE,timeout);
  num=0;
  if (ret_val ==WAIT_FAILED)
  {
   printf("Error %d in WaitforMultipleObjects\n",ret_val);
   err=PCO_ERROR_SDKDLL_SYSERR;
  }
  else if (ret_val == WAIT_TIMEOUT)
  {
   printf("timeout WaitForMultipleObjects return %d\n",ret_val);
   err=PCO_ERROR_TIMEOUT;
  }
  else
  {
   for(x=0;x<nr_of_buffer;x++)
   {
    if(ev[x]>=0)
    {
     if(WaitForSingleObject(ev[x],0)==WAIT_OBJECT_0)
     {
      err=GetBufferStatus(hCamera,bl[x].sBufNr,&bl[x].dwStatusDll,&bl[x].dwStatusDrv);
      if(err!=PCO_NOERROR)
       printf("PCO_GetBufferStatus(,%d) return error %x \n",bl[x].sBufNr,err);
      num++;
     }
    }
   }
  }
  free(ev);

  return err;
}*/
