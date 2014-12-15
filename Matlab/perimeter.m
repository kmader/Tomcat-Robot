function p=perimeter(bwObj)
bwObjS=bwObj>0;
bwBounds=bwboundaries(bwObj);
p=0;
for i=1:length(bwBounds)
   p=p+size(bwBounds{i},1);
end