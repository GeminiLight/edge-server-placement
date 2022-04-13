function clet=define_cloudlets(Nc,p) %#ok<*INUSD>
clet=[];
for i=1:Nc
    clet(i).id=i; %#ok<*AGROW>
    clet(i).deploy=[];
    clet(i).user=[];
    clet(i).flag=0;
end
end