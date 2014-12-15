/*
 *  ImageProcessing.h
 *  AlignServer
 *
 * Image processing module for the 
 *
 *  Created by Kevin Mader on 09.12.09.
 *  Copyright 2009 __MyCompanyName__. All rights reserved.
 *
 */
#define GCR(x,wX) (x-(wX-1)/2.0)
#define ABS(x)	(sqrt(pow(x,2)))
#define GCN(x,wX) (GCR(x,wX)/((wX-1)/2.0))
#define GCX(kk,wX,wY) (kk%wX)
#define GCY(kk,wX,wY) ((kk-kk%wX)/wX)
#define GCK(cx,cy,wX,wY) (cy*wX+cx)

#ifndef DWORD
typedef unsigned long DWORD;
#endif
#ifndef WORD
typedef unsigned short WORD;
#endif
#ifndef M_PI
#define M_PI 3.14159265358979
#endif
#define WORD_MAX 65536
#define WORD_MIN 0

//typedef WORD *PWORD,*LPWORD;
//typedef DWORD *PDWORD,*LPDWORD;

class kImage {
private:
	bool* sampleMask;
	//WORD* bImage;
	//WORD* bFlat;
	double* comVals;
	double* comSqVals;
	int* comCounts;
	bool getCyl();
	void fitV();
	void fitH();
	double a,b;
	double xmean,xsmean,ymean,ysmean,xymean,xycorr;
protected:
	
public: 
	//kImage(WORD*,WORD*,int,int,int=2,bool=false,double=0.20,bool=false);
	kImage(WORD*,WORD*,int,int,long,bool=true,bool=true,bool=true);
	~kImage();
	void threshold(double=0,double=-1);
	bool saturationCheck();
	bool fitParameters();
	long removeNoise(int);
	void printImage();
	void findBoundaries();
	WORD* corrImage();
	void corrImage(WORD*);
	void corrImage(bool*);
	void fitImage(bool*);
	// Parameters
	bool useVals;
	bool debugVal;
	bool corrFlat;
	bool logData;
	bool threshScale;
	bool pseudoBW;

	int maskmode; // keep values under thresh, between thresh or over thresh
	int readmode; // find com based on raw values, thresheld values, thesheld raw values
	
	int cutoff;
	
	int rowAvg; // Row binning parameter
	int wX,wY;
	double minTransmission,maxTransmission;
	
	
	double minSamplePct;
	// Stored Parameters
	bool threshd;
	double tmean,tstd;
	// Output Values
	double mean,std;
	double angle,xoffset,yoffset;
	double minY,maxY,minX,maxX;
	double meanW,maxW;
	double pctover,pctunder,pctbetween,pctsaturated;
	
	double* correctedImage;

	
};
