function [ch_i, nV]=deploy_clet(nclet,ci,V,BS,user)

ux=nclet(ci).user;
U=user(ux,1:2);
nV=[V(:)' nclet(ci).deploy];
for i=1:numel(nV)
    vi=nV(i);
    mdist(i)= calcdist(BS(vi,1:2),U);
end
[~,ix]=min(mdist);
ch_i=nV(ix);
if ch_i~=nclet(ci).deploy
    nV=[nV nclet(ci).deploy];
end
end

function mdist=calcdist(B,U)
mdist=0;
for i=1:size(U,1)
    mdist=mdist+sqrt((B(1)-U(i,1))^2+(B(2)-U(i,2))^2);
end
mdist=mdist/size(U,1);
end