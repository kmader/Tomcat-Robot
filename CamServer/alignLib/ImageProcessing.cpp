/*
 *  ImageProcessing.cpp
 *  AlignServer
 *
 *  Created by Kevin Mader on 09.12.09.
 *  Copyright 2009 __MyCompanyName__. All rights reserved.
 *
 */


#include "ImageProcessing.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include "stdafx.h"

using namespace::std;

kImage::kImage(WORD* image, WORD* flat,int wXi,int wYi, bool useValsi, bool debugi) {
	// Images
	bImage=image;
	bFlat=flat;
	// Parameters
	
	wX=wXi;
	wY=wYi;
	
	debugVal=debugi;
	useVals=useValsi;
	
	corrFlat=true;
	logData=false;
	rowAvg=1; // Number of rows to average
	minSamplePct=0.08; // Minimum percent to keep a row
	// Code to verify input is meaningful
	// Not yet implemented
	
	// Allocate Arrays
	correctedImage=(double*)malloc(sizeof(double)*wX*wY);
	sampleMask=(bool*)malloc(sizeof(bool)*wX*wY);
	
	// Use sums to calculate mean and standard deviation
	double vSum=0.0;
	double vsSum=0.0;
	for (int kk=0;kk<wX*wY;kk++) {
		// Flat Field Correction
		if (corrFlat) correctedImage[kk]=((double) flat[kk])/((double) image[kk]);
		else correctedImage[kk]=((double) image[kk]);
		// Take Logarithm
		if (logData) correctedImage[kk]=log(correctedImage[kk]);
		vSum+=correctedImage[kk];
		vsSum+=((double) correctedImage[kk])*((double) correctedImage[kk]);
	}
	mean=vSum/((double) wX*wY);
	std=sqrt(vsSum/((double) wX*wY)-mean);
	if (debugVal) {
		cout<<"Mean Value : "<<mean<<endl;
		cout<<"Std Value  : "<<std<<endl;
	}
	
}
void kImage::threshold(double imval,double irangval) {
	double mval=imval;
	double rangval=irangval;
	
	if (rangval<0) {
		mval=mean;
		rangval=std;
	}
	long pixInMask=0;
	long pixInRow;
	int kk;
	for (int cy=0;cy<wY;cy++) {
		pixInRow=0;
		for (int cx=0;cx<wX;cx++) {
			kk=GCK(cx,cy,wX,wY);
			if ((correctedImage[kk]>(mval-rangval)) && (correctedImage[kk]<(mval+rangval))) {
				sampleMask[kk]=true;
				pixInRow+=1;
			}
			else sampleMask[kk]=false;
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
	if (debugVal) {
		cout<<"Masked Pixels : "<<pixInMask<<" Ratio "<<(double) pixInMask/(wX*wY)*100<<"%"<<endl;
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
	bool out=getCyl();
	if (out) fitH();
	cout<<" Image Parameters ..."<<endl;
	
	cout<<"A                : "<<a<<" - B :"<<b<<endl;
	theta=atan(a)*180.0/M_PI;
	offset=b;

	cout<<"Theta            : "<<theta<<endl;
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
			tyval=GCR((crow*rowAvg+0.5*(rowAvg-1)),wY);
			
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