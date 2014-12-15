function [img]=kradon(p,theta)
%kradon Soft-IRadon Transform
% This calculates the inverse radon transform
% for light that has only traveled around an object not through (binary!)
% Basically it takes out the fft code, making the procedure faster.
interp='spline';
N = 2*floor( size(p,1)/(2*sqrt(2)) ); 
img = zeros(N,class(p));        % Allocate memory for the image.
len=size(p,1);   
% Define the x & y axes for the reconstructed image so that the origin     
% (center) is in the spot which RADON would choose.                        
center = floor((N + 1)/2);                                                 
xleft = -center + 1;                                                       
x = (1:N) - 1 + xleft;                                                     
x = repmat(x, N, 1);                                                       
                                                                          
ytop = center - 1;                                                         
y = (N:-1:1).' - N + ytop;                                                 
y = repmat(y, 1, N);           

costheta = cos(theta);
sintheta = sin(theta);
ctrIdx = ceil(len/2);     % index of the center of the projections

% Zero pad the projections to size 1+2*ceil(N/sqrt(2)) if this
% quantity is greater than the length of the projections
imgDiag = 2*ceil(N/sqrt(2))+1;  % largest distance through image.
if size(p,1) < imgDiag 
   rz = imgDiag - size(p,1);  % how many rows of zeros
   p = [zeros(ceil(rz/2),size(p,2)); p; zeros(floor(rz/2),size(p,2))];
   ctrIdx = ctrIdx+ceil(rz/2);
end

% Backprojection - vectorized in (x,y), looping over theta
switch interp
    case 'nearest neighbor'

      for i=1:length(theta)   
          proj = p(:,i);
          t = round(x*costheta(i) + y*sintheta(i));
          img = img + proj(t+ctrIdx);
      end
   
  case 'linear'

    for i=1:length(theta)  
        proj = p(:,i);
        t = x.*costheta(i) + y.*sintheta(i); 
        a = floor(t);  
        img = img + (t-a).*proj(a+1+ctrIdx) + (a+1-t).*proj(a+ctrIdx);
    end
    
  case {'spline','pchip','cubic','v5cubic'}

    interp_method = sprintf('*%s',interp); % Add asterisk to assert
                                           % even-spacing of taxis
    
    for i=1:length(theta)
        proj = p(:,i);
        taxis = (1:size(p,1)) - ctrIdx;
        t = x.*costheta(i) + y.*sintheta(i);
        projContrib = interp1(taxis,proj,t(:),interp_method);
        img = img + reshape(projContrib,N,N);
    end
    
end

img = img*pi/(2*length(theta));






function garbage
circFact=1/pi*sum(sum(edge(double(bwData))))/(2*sqrt(sum(sum(bwData))/pi));
cenP=round(size(sinogram,2)/2);
posSinogram=sinogram(:,cenP:end);
negSinogram=sinogram(:,1:(cenP-1));
[xx,yy]=meshgrid([-cenP:cenP],[-cenP:cenP]);
r=sqrt(xx.^2+yy.^2);
newImage=abs(xx)<0;
for ij=1:length(xx,1)
    for ik=1:length(xx,2)
        
        if yy(ij,ik)>0
            newImage(ij,ik)=estValue(xx(ij,ik),yy(ij,ik),posSinogram,theta);
        else
            newImage(ij,ik)=estValue(xx(ij,ik),yy(ij,ik),negSinogram,theta);
        end
    end
end

function val=estValue(x,y,sinogram,theta)
