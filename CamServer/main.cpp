#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include "ImageProcessing.h"
#include <ctime>


#ifndef DWORD
typedef unsigned long DWORD;
#endif
#ifndef WORD
typedef unsigned short WORD;
#endif

using namespace::std;
int main (int argc, char * const argv[]) {
    // insert code here...
	cout << "Hello, World!\n";
	WORD *imageTest,*flatTest;
	int wX=2*1024;
	int wY=2*1024;
	int maxVal=2*wX;
	double xVal,yVal,tempVal;
	imageTest =(WORD*)malloc(sizeof(WORD)*wX*wY);
	flatTest =(WORD*)malloc(sizeof(WORD)*wX*wY);
	
	// Generate testing images
	for (int kk=0;kk<wX*wY;kk++) {
		xVal=GCX(kk,wX,wY)-1;
		xVal=GCN(xVal,wX);
		yVal=GCY(kk,wX,wY);
		yVal=GCN(yVal,wY);
		
		//imageTest[kk]=1+abs(tempVal-(wX*wY+(slopeVal))/(2*wY));
		tempVal=xVal+0.1*yVal;
		tempVal=(maxVal*(1+3.0*ABS(2-tempVal))/10.0);
		imageTest[kk]=tempVal;
		//cout<<xVal<<","<<yVal<<","<<imageTest[kk]<<","<<tempVal<<endl;
		//if (imageTest[kk]>maxVal) maxVal=imageTest[kk];
	}
	
	for (int kk=0;kk<wX*wY;kk++) {
		flatTest[kk]=maxVal;
	}
	clock_t start,finish;
	double time;
	start = clock();
	kImage* curImage;
	int imTest=20;
	for(int k=0;k<imTest;k++) {
		curImage=new kImage(imageTest,flatTest,wX,wX);
		curImage->threshold(1/0.7,.3);
		cout<<"Deleted Pixels : "<<curImage->removeNoise(4)<<endl;
		curImage->findBoundaries();
		if (curImage->fitParameters()) cout<<"Successful!"<<endl;
		else cout<<"Failed.."<<endl;
		
		free(curImage);
		curImage=NULL;
	}
	finish = clock();
	
	time = (double(finish)-double(start))/CLOCKS_PER_SEC;
	cout<<"Images Per Second  :"<<imTest/time<<endl;
	//curImage->printImage();
    return 0;
}
