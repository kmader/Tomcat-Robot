steps=1
maxT=2;
cT=0;
T=[];
for cT=1:maxT
    T=[T cT-1:0.25^(cT):cT];
end
xPix=2000;
yPix=2000;
sizeX=0;
sizeY=0; % much bigger in y than x
dx=(1+sizeX)*xPix/steps*(sin(T*2*pi/steps)+2*pi/steps*T.*cos(T*2*pi/steps));
dy=(1+sizeY)*yPix/steps*(cos(T*2*pi/steps)-2*pi/steps*T.*sin(T*2*pi/steps));
x=cumsum(dx).*mean(diff(T));y=cumsum(dy).*mean(diff(T));




for i=[0:length(x)]
    if i==0
        hold off
        cX=0;cY=0;
        hold on
    else
        cX=x(i);
        cY=y(i);
    end
    plot(cX,cY,'r+')
    line([cX-xPix/2 cX+xPix/2],[cY-yPix/2 cY-yPix/2]);
    line([cX-xPix/2 cX+xPix/2],[cY+yPix/2 cY+yPix/2]);
    line([cX-xPix/2 cX-xPix/2],[cY-yPix/2 cY+yPix/2]);
    line([cX+xPix/2 cX+xPix/2],[cY-yPix/2 cY+yPix/2]);
end