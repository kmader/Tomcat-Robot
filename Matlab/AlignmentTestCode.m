

% initial parameters
r0bone=97e-3; % radius
r0marrow=89e-3; % radius
xx0=-0e-3; % x-offset
yy0=-17e-3; % y-offset
xd0=1.1; % x-stretching
yd0=1; % y-stretching
noise0=.1; % 5 pecent noise?
if iter==0 
	xC=0;
	yC=0;
	xyThick=120*1e-3;
else
	xC=xEdges(2)-thickness/2
	yC=mean(yEdges)
	xyThick=40*1e-4
end
xySteps=100;
	
xyR=[-xyThick:xyThick/xySteps:xyThick];
xR=xyR+xC;
yR=xyR+yC;
projSet=[0:2*180/length(xR):180];
% setup dimension space
[xx,yy]=meshgrid(xR,yR);
% create sample
boneSlice=double(sqrt(((xx-xx0)/xd0).^2+((yy-yy0)/yd0).^2)<(r0bone^2));
boneSlice=boneSlice-double(sqrt(((xx-xx0)/xd0).^2+((yy-yy0)/yd0).^2)<(r0marrow^2));



desiredOut=100;
scaleDown=5;



outMat=[];
tic
for i=projSet
	curProj=imrotate(boneSlice,i,'bicubic','crop');
	curProj=curProj+abs(sqrt(curProj)).*rand(size(curProj,1),size(curProj,2)); % photon stat noise
	curProj=curProj+noise0*rand(size(curProj,1),size(curProj,2)); % dark noise
	
	oRow=sum(curProj);
	outMat=[outMat oRow'];
	
	if toc>5
		tic;
		disp([num2str(((max(projSet)-i)/range(projSet)*length(projSet)*5)/60) ' minutes remaining']);
	end
end

% outMat is output from the CT

[r,xp]=iradon(outMat,projSet); % the transform to get back the original
figure(1)
imagesc(xR,xR,boneSlice); colormap bone;
[xEdges,yEdges]=AutoBoneAlignCode(outMat,xR,yR,projSet);
thickness=(r0bone-r0marrow)/2;
line([mean(xEdges)-thickness/2,mean(xEdges)+thickness/2],[yEdges(1) yEdges(1)]);
line([mean(xEdges)-thickness/2,mean(xEdges)+thickness/2],[yEdges(1)+thickness yEdges(1)+thickness]);
line([mean(xEdges)-thickness/2,mean(xEdges)+thickness/2],[yEdges(2)-thickness yEdges(2)-thickness]);
line([mean(xEdges)-thickness/2,mean(xEdges)+thickness/2],[yEdges(2) yEdges(2)]);

line([xEdges(1),xEdges(1)],[mean(yEdges)-thickness/2 mean(yEdges)+thickness/2]);
line([xEdges(1)+thickness,xEdges(1)+thickness],[mean(yEdges)-thickness/2 mean(yEdges)+thickness/2]);
line([xEdges(2)-thickness,xEdges(2)-thickness],[mean(yEdges)-thickness/2 mean(yEdges)+thickness/2]);
line([xEdges(2),xEdges(2)],[mean(yEdges)-thickness/2 mean(yEdges)+thickness/2]);
figure(2)
imagesc(projSet,xR,outMat);
line([0 0],xEdges);
line([90 90],yEdges);
