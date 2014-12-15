proj1=imread('SC_003_F_Chimp_femur.jpg');
proj1g=double(rgb2gray(proj1));
proj180g=proj1g(:,end:-1:1);
xr=[156 230];
yr=[68 552];
[xg,yg]=meshgrid(1:size(proj1g,2),1:size(proj1g,1));
boneMask=(xg<xr(2) & xg>xr(1) & yg>yr(1) & yg<yr(2));
proj90g=double(proj1g)/2+150*circshift(double(proj1g>200).*boneMask,[0,-10]);
xRange=[1 size(proj1g,1)];
%yRange=[40 590];
yRange=[1 size(proj1g,2)];
%yRange=[50 250];
numProjs=80
prjTable=zeros(range(xRange),range(yRange),length([0:181/(numProjs):180]));
xVals=xRange(1):xRange(2);
yVals=yRange(1):yRange(2);

for ij=1:length(xVals)
    for ik=1:length(yVals)
        %hold off
        %plot([1 90 180],[proj1g(ij,ik),proj90g(ij,ik),proj180g(ij,ik)],'r.');
        %hold on
        int1=interp1([0,90,180],[proj1g(xVals(ij),yVals(ik)),proj90g(xVals(ij),yVals(ik)),proj180g(xVals(ij),yVals(ik))],[0 45 90 135 180],'cubic');
        %int2=interpft(int1,numProjs);
        int2=interp1([0 45 90 135 180],int1,[0:181/(numProjs):180],'cubic');
        prjTable(ij,ik,:)=int2;
        %plot(squeeze(prjTable(ij,ik,:)),'b-')
        %pause(.5)
    end
end