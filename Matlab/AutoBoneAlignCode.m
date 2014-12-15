function [xEdges,yEdges]=AutoBoneAlignCode(sinogram0,xCoord,yCoord,thCoord)
modeS=0;
if modeS==1 
	flatX=interp2(thCoord,xCoord,sinogram0,[0],xCoord);
	flatY=interp2(thCoord,yCoord,sinogram0,[90],yCoord);

	xEdges=xCoord(findEdges(flatX));
	yEdges=yCoord(findEdges(flatY));
else
	xEdges=[];
	yEdges=[];
    rAngles=0:179;
	for i=rAngles
		xEdges=[xEdges;findEdges(interp2(thCoord,xCoord,sinogram0,[i],xCoord))];
    end
    bAngles=rAngles;
    bottomLip=xEdges(:,1);
    tAngles=rAngles;
    topLip=xEdges(:,2);
    bAngles(bottomLip==1 | bottomLip==size(sinogram0,1))=[];
    bottomLip(bottomLip==1 | bottomLip==size(sinogram0,1))=[];
    tAngles(topLip==1 | topLip==size(sinogram0,1))=[];
    topLip(topLip==1 | topLip==size(sinogram0,1))=[];
    bottomLip=interp1(bAngles,bottomLip,rAngles);
    topLip=interp1(tAngles,topLip,rAngles);
    xEdges=[bottomLip topLip];
end

function fEdges=findEdges(flatF)
% clean up the image, make it binary, and find the boundaries
% min and max points in obj
minPts=6;
maxPts=length(flatF)/3;

mu=mean(flatF);
stV=std(flatF);

stVrat=[-3:1/100:3]; % range of standard deviations to search

% this segment uses vector/matrix notation to calculate everything without for loops
% it is a little tricky to follow but basically 
% threshPts is a graph of the number of points in the bone as a function of the threshold
flatFGrid=meshgrid(flatF,ones(1,length(stVrat)));
stVgrid=meshgrid(mu+stVrat.*stV,ones(1,length(flatF)))';
global outGrid
outGrid=(flatFGrid>stVgrid);
outGrid=bwareaopen(outGrid,minPts,[zeros(1,3);ones(1,3);zeros(1,3)]);
threshPts=sum(outGrid');
threshPtsA=[length(flatF) threshPts(1:end-1) 0];
idx1=find(diff(threshPtsA<maxPts));
idx2=find(diff(threshPtsA>0));
threshPtsWindow=threshPts(idx1:idx2);
if length(threshPtsWindow)<1
	threshPtsWindow=threshPts;
else
	stVratWindow=[-1000 stVrat 1000];
	stVratWindow=stVratWindow(idx1:idx2);
end
threshTable=[1;abs(smooth(diff(threshPtsWindow),5))>0.4;0];

vals=find(abs(diff(threshTable)));
effVal=(1-threshPtsWindow/range(threshPtsWindow)).^2./(length(threshPtsWindow)/4+[1:length(threshPtsWindow)]);
[junk,nVal]=max(effVal(vals));
threshVal=mu+stV*stVratWindow(vals(nVal));

%plot(1:length(threshPtsWindow),threshPtsWindow,'b-',vals(nVal),threshPtsWindow(vals(nVal)),'r.');pause
threshFlat=bwareaopen(flatF>threshVal,minPts);
%plot(threshFlat);pause
threshdFlat=diff(threshFlat);
leftEdge=find(threshdFlat==1);
rightEdge=find(threshdFlat==-1);

if length(leftEdge)<1
	leftEdge=1;
end
if length(rightEdge)<1
	rightEdge=length(flatF);
end
fEdges=[max([1 leftEdge(1)]),min([rightEdge(end) length(flatF)])];
% ydata=flatF;
% xdata=[1:length(ydata)];
% a=lsqcurvefit(@(a,xdata) a(1)*exp(-(xdata-a(2)).^2/a(3)^2),[range(ydata);0;range(xdata)/4],xdata,ydata');
% fEdges=round(a(2)+[-2*a(3),+2*a(3)]);
% fEdges(1)=median([1 fEdges]);
% fEdges(2)=median([length(ydata) fEdges]);
% fEdges(1)=a(2);
% fEdges(2)=a(3);
