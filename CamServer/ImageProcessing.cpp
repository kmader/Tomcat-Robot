/*
 *  ImageProcessing.cpp
 *  AlignServer
 *
 *  Created by Kevin Mader on 09.02.10
 *  Copyright 2010 4u33r3 g3173. All rights reserved.
 *
 */


#include "ImageProcessing.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <iostream>
//#include "stdafx.h"

using namespace::std;

kImage::kImage(WORD* image, WORD* flat,int wXi,int wYi,long icutoff,bool useFlat, bool useValsi, bool debugi) {
	// Images
	//bImage=image;
	//bFlat=flat;
	// Parameters

	wX=wXi;
	wY=wYi;
	
	debugVal=debugi;
	useVals=useValsi;
	cutoff=icutoff;
	corrFlat=useFlat;
	logData=true;
	threshd=false;
	threshScale=false;
	pseudoBW=false;
	tmean=0;
	tstd=0;
	rowAvg=10; // Number of rows to average
	minSamplePct=0.01; // Minimum percent to keep a row
	minTransmission=1e-5;
	maxTransmission=1;
	// Code to verify input is meaningful
	// Not yet implemented

	// Allocate Arrays
	correctedImage=(double*)malloc(sizeof(double)*wX*wY);
	sampleMask=(bool*)malloc(sizeof(bool)*wX*wY);


	// Use sums to calculate mean and standard deviation
	double vSum=0.0;
	double vsSum=0.0;
	long pixSaturated=0;
	long maxFlat=image[0];
	if (!corrFlat) for (int kk=0;kk<wX*wY;kk++) if (image[kk]>maxFlat) maxFlat=image[kk];
	for (int kk=0;kk<wX*wY;kk++) {
		if (image[kk]>cutoff) pixSaturated++;
		// Flat Field Correction
		if (corrFlat) correctedImage[kk]=((double) flat[kk])/((double) image[kk]);
		else correctedImage[kk]=((double) maxFlat)/((double) image[kk]);
		// Take Logarithm
		if (logData) correctedImage[kk]=log(correctedImage[kk]);
		vSum+=correctedImage[kk];
		vsSum+=((double) correctedImage[kk])*((double) correctedImage[kk]);
	}
	mean=vSum/((double) wX*wY);
	std=sqrt(vsSum/((double) wX*wY)-mean);
	pctsaturated=pixSaturated;
	pctsaturated/=(wX*wY)/100.0;
	if (debugVal) {
		cout<<"(Mean,Std) : ("<<mean<<","<<std<<")"<<endl;
		cout<<"Saturation  : "<<pctsaturated<<"%"<<endl;
	}

}
kImage::~kImage() {
	free(correctedImage);
	correctedImage=NULL;
	free(sampleMask);
	sampleMask=NULL;
}

void kImage::threshold(double imval,double irangval) {
	tmean=imval;
	tstd=irangval;

	if (irangval<0) {
		tmean=mean;
		tstd=std;
	}
	long pixInMask=0;
	long pixUnderMask=0;
	long pixOverMask=0;
	
	long pixInRow;
	int kk;
	for (int cy=0;cy<wY;cy++) {
		pixInRow=0;
		for (int cx=0;cx<wX;cx++) {
			kk=GCK(cx,cy,wX,wY);
			sampleMask[kk]=false;
			
			if (correctedImage[kk]>(tmean-tstd)) {
				if  (correctedImage[kk]<(tmean+tstd)) {
					sampleMask[kk]=true;
					pixInRow+=1;
				} else pixOverMask++;

			} else pixUnderMask++;

		}
		if (pixInRow<(wX*rowAvg*minSamplePct) && pixInRow>0) {
			// Clear Row if it is too empty
			pixInRow=0;
			for (int cx=0;cx<wX;cx++) {
				kk=GCK(cx,cy,wX,wY);
				sampleMask[kk]=false;
			}
		}
		pixInMask+=pixInRow;

	}
	pctover=pixOverMask;
	pctover/=(wX*wY)/100.0;
	pctunder=pixUnderMask;
	pctunder/=(wX*wY)/100.0;
	pctbetween=pixInMask;
	pctbetween/=(wX*wY)/100.0;
	threshd=true;
	if (debugVal) {

		cout<<"Masked Pixels : "<<pixInMask<<", Ratio "<<pctbetween<<"%"<<endl;
		cout<<"Under % : "<<pctunder<<", Over % : "<<pctover<<endl;
	}

}

long kImage::removeNoise(int edgeSize) {
	int kk;
	int ckk;
	long delPix=0;
	bool* tSampleMask=(bool*)malloc(sizeof(bool)*wX*wY);
	for (int cy=0;cy<(wY);cy++) {
		for (int cx=0;cx<(wX);cx++) {
			ckk=GCK(cx,cy,wX,wY);
			// if the point is part of the mask
			tSampleMask[ckk]=sampleMask[kk];
			if (sampleMask[ckk]) {
				if ((cx>=edgeSize) && (cx<wX-edgeSize) && (cy>=edgeSize) && (cy<wY-edgeSize)) {
					int pixInBox=0;
					for(int i=-edgeSize;i<edgeSize;i++) {
						for(int j=-edgeSize;j<edgeSize;j++) {
							kk=GCK(cx+i,cy+j,wX,wY);

							if (sampleMask[kk]) pixInBox++;
						}
					}
					// if the box has less than minSamplePct filled
					// the current pixel is turned off
					if (pixInBox<(minSamplePct*edgeSize*edgeSize)) {
						tSampleMask[ckk]=false;
						delPix++;
					}
				}
			}
		}
	}
	free(sampleMask);
	sampleMask=NULL;
	sampleMask=tSampleMask;
	return delPix;


}
void kImage::fitImage(bool* outImage) {
	// Returns an image with positive values at mid +/- std
    int nRows=wY/rowAvg;
	for (int crow=0;crow<nRows;crow++) {
		double ccom=comVals[crow];
		double cstd=sqrt(comSqVals[crow]-pow(ccom,2));
		for (int cyi=(crow*rowAvg);cyi<((crow+1)*rowAvg);cyi++) {
			int cy=GCR(cyi,wY);
			for (int cxi=0;cxi<(wX);cxi++) {
				int ckk=GCK(cxi,cyi,wX,wY);
				int cx=GCR(cxi,wX);
				outImage[ckk]=false;
				if ((cx<ccom+cstd) && (cx>ccom-cstd)) outImage[ckk]=true;
			}
		}
	}
}
	
WORD* kImage::corrImage() {
	WORD* outImage=(WORD*)malloc(sizeof(WORD)*wX*wY);
	corrImage(outImage);
	return outImage;
}
void kImage::corrImage(bool* outImage) {
	for (int kk=0;kk<(wX*wY);kk++) outImage[kk]=sampleMask[kk];
}
void kImage::corrImage(WORD* outImage) {
	double maxVal=1/minTransmission;
	double minVal=1/maxTransmission;
	double thMin=tmean-tstd;
	double thMax=tmean+tstd;

	if (logData) {
		minVal=log(minVal);
		maxVal=log(maxVal);
		thMin=log(thMin);
		thMax=log(thMax);
	}
	if (threshScale) {
		minVal=thMin;
		maxVal=thMax;
	}
	double wordMid=(WORD_MAX+WORD_MIN)/2.0;
	double wordRng=(WORD_MAX-WORD_MIN)/2.0;
	double dblRng=(maxVal-minVal)/2.0;
	double dblMid=(maxVal+minVal)/2.0;
	double thRng=(thMax-thMin)/2.0;
	double thMid=(thMax+thMin)/2.0;
	// Show Edges Better
	wordRng*=0.5;
//double scaleFactor=(wordRng)/dblRng;
	//if (debugVal) cout<<"CorrImage:"<<scaleFactor<<endl;
	for (int kk=0;kk<(wX*wY);kk++) {
		double cVal;
		// Color Pixels
		if (correctedImage[kk]<(thMin)) cVal=(correctedImage[kk]-thMin)/abs(thMax-minVal);
		else if (correctedImage[kk]>(thMax)) cVal=(correctedImage[kk]-thMax)/abs(maxVal-thMax);
		else cVal=(correctedImage[kk]-thMid)/thRng;

		//if (kk%800==0) cout<<kk<<"-"<<correctedImage[kk]<<"\t"<<cVal<<"\t"<<(WORD) cVal<<endl;
		if (cVal<-1) outImage[kk]=wordMid-wordRng;
		else if (cVal>1) outImage[kk]=wordMid+wordRng;
		else outImage[kk]=(WORD) (cVal*wordRng+wordMid);

		// outImage[kk]=0;
		if (pseudoBW) {
			if (correctedImage[kk]<(tmean-tstd)) outImage[kk]=0;
			else if (correctedImage[kk]>(tmean+tstd)) outImage[kk]=WORD_MAX;
			else outImage[kk]=32767;
		}
	}
}
void kImage::findBoundaries() {
	bool firstPoint=true;
	int kk;
	double cx,cy;
	int widRows=0;
	maxW=0;
	meanW=0;
	for (int cyi=0;cyi<wY;cyi++) {
		double crminX=0;
		double crmaxX=0;
		bool rowEmpty=true;
		for (int cxi=0;cxi<wX;cxi++) {
			kk=GCK(cxi,cyi,wX,wY);

			if (sampleMask[kk]) {
				cx=GCR(cxi,wX);
				cy=GCR(cyi,wY);

				// Determine the Width of Each Row
				if (rowEmpty) {
					crminX=cx;
					crmaxX=cx;
					rowEmpty=false;
					widRows++;
				}
				if (cx<crminX) crminX=cx;
				if (cx>crmaxX) crmaxX=cx;

				// Determine the Bounding Box of the Image
				if (firstPoint) {
					minX=cx;
					maxX=cx;
					minY=cy;
					maxY=cy;
					firstPoint=false;
				}
				if (cx<minX) minX=cx;
				if (cx>maxX) maxX=cx;
				if (cy<minY) minY=cy;
				if (cy>maxY) maxY=cy;
			}
		}
		meanW+=(crmaxX+1)-crminX;
		if (((crmaxX+1)-crminX)>maxW) maxW=(crmaxX+1)-crminX;
	}
	if (widRows>0) meanW/=widRows;
	else meanW=-1;
	cout<<"width(mean,max) = ("<<meanW<<", "<<maxW<<")"<<endl;
	cout<<"(x_min,x_max)   = ("<<minX<<", "<<maxX<<")"<<endl;
	cout<<"(y_min,y_max)   = ("<<minY<<", "<<maxY<<")"<<endl;

}
bool kImage::fitParameters() {
	bool out;
	if (pctbetween<0.1) {
		cout<<" Two Few Pixels ..."<<endl;
		out=false;
		a=0;
		b=0;
		xsmean=0;
		xmean=0;
		ysmean=0;
		ymean=0;
		angle=0;
		xoffset=0;
		yoffset=0;
	} else {
		out=getCyl();
		if (out) fitH();
	}
	cout<<" Image Parameters ..."<<endl;

	cout<<"A                : "<<a<<" - B :"<<b<<endl;
	angle=atan(a)*180.0/M_PI;
	xoffset=b;
	yoffset=ymean;
	cout<<"Theta            : "<<angle<<endl;
	// 3.46 is a heuristically determined factor to scale the standard deviation to a meaningful physical value
	cout<<"width(xstd,ystd) : ("<<3.46*sqrt(xsmean-xmean*xmean)<<", "<<3.46*sqrt(ysmean-ymean*ymean)<<")"<<endl;
	return out;
}

bool kImage::getCyl()
{
	int kk;
	int nRows=wY/rowAvg;
	comVals=(double*)malloc(sizeof(double)*nRows);
	comSqVals=(double*)malloc(sizeof(double)*nRows);
	comCounts=(int*)malloc(sizeof(int)*nRows);
	for (int crow=0;crow<nRows;crow++) {
		comVals[crow]=0.0;
		comCounts[crow]=0;
		double wCount=0;
		double wsCount=0;
		for (int cy=(crow*rowAvg);cy<((crow+1)*rowAvg);cy++) {
			for (int cx=0;cx<wX;cx++) {
				kk=GCK(cx,cy,wX,wY);
				if (sampleMask[kk]) {
					double dx=GCR(cx,wX);
					double tempVal=1;
					if (useVals) tempVal=((double) correctedImage[kk]);
					comVals[crow]+=tempVal*dx;
					comSqVals[crow]+=(tempVal*dx)*(tempVal*dx);
					wCount+=tempVal;
					wsCount+=tempVal*tempVal;
					comCounts[crow]+=1;
				}
			}
		}
		if (wCount>0) comVals[crow]/=wCount; // normalize by weights (or counts)
		if (wCount>0) comSqVals[crow]/=wsCount;
		//if (debugVal) cout<<"Row : "<<GCR((crow*rowAvg+0.5*(rowAvg-1)),wY)<<" - "<<comVals[crow]<<" with "<<comCounts[crow]<<endl;

		// Row end
	}

	// Calculate Moments of Data for Linear Fit

	int xcount;
	// Initialize Values
	xmean=0;
	xsmean=0;
	ymean=0;
	ysmean=0;
	xymean=0;
	xycorr=0;
	xcount=0;
	for (int crow=0;crow<nRows;crow++) {
		if (comCounts[crow]>(wX*rowAvg*minSamplePct)) {
			double txval,tyval;
			txval=comVals[crow];
			tyval=GCR((crow*rowAvg+0.0*(rowAvg-1)),wY);

			xmean+=txval;
			xsmean+=comSqVals[crow];

			ymean+=tyval;
			ysmean+=tyval*tyval;

			xymean+=txval*tyval;
			xcount++;
		}
	}
	xmean/=xcount;
	ymean/=xcount;
	xsmean/=xcount;
	ysmean/=xcount;
	xymean/=xcount;
	for (int crow=0;crow<nRows;crow++) {
		if (comCounts[crow]>(wX*rowAvg*minSamplePct)) {
			double txval,tyval;
			txval=comVals[crow];
			tyval=GCR((crow*rowAvg+0.5*(rowAvg-1)),wY);
			xycorr=(txval-xmean)*(tyval-ymean);
		}
	}
	xycorr/=xcount;
	if (debugVal) cout<<"X Distribution : mean-"<<xmean<<", std-"<<sqrt(xsmean-xmean*xmean)<<endl;
	if (debugVal) cout<<"Y Distribution : mean-"<<ymean<<", std-"<<sqrt(ysmean-ymean*ymean)<<endl;
	if (debugVal) cout<<"XY Distribution : jvar-"<<xymean<<", corr-"<<xycorr/(sqrt(xsmean-xmean*xmean)*sqrt(ysmean-ymean*ymean))<<endl;
	if (xcount>(nRows*minSamplePct)) return true;
	else return false;

}

void kImage::fitV() {
	// Linear Fitting Code for Horizontal Object
	a=(xymean-xmean*ymean)/(xsmean-xmean*xmean);
	b=ymean-a*xmean;
	if (debugVal) cout<<"A : "<<a<<" - B :"<<b<<endl;
}
void kImage::fitH() {
	// Linear Fitting Code for Vertical Object
	a=(xymean-xmean*ymean)/(ysmean-ymean*ymean);
	b=xmean-a*ymean;
	if (debugVal) cout<<"A : "<<a<<" - B :"<<b<<endl;
}

void kImage::printImage()
{
	int kk;
	cout<<"Mask Data"<<endl<<"["<<endl;
	for (int cy=0;cy<wY;cy++) {
		for (int cx=0;cx<wX;cx++) {
			kk=GCK(cx,cy,wX,wY);
			if (sampleMask[kk]) cout<<"x";
			else cout<<"o";
		}
		cout<<endl;
	}
	cout<<"]"<<endl;
	if (debugVal) {
		cout<<"Image Data"<<endl<<"["<<endl;
		for (int cy=0;cy<wY;cy++) {
			for (int cx=0;cx<wX;cx++) {
				cout<<cx<<","<<cy<<":";
				kk=GCK(cx,cy,wX,wY);
				if (sampleMask[kk]) cout<<correctedImage[kk];
				else cout<<"----";
				cout<<"\t";
			}
			cout<<endl;
		}
		cout<<"]"<<endl;
	}

}
