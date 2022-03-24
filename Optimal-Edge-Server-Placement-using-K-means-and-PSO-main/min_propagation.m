function [ix, Z]=min_propagation(user,ui,BS,nclet,p,E)
% zui <-- k in K with min. propagation to h_ui, 
% In case of ties, choose based on distance
tar=user(ui,:); % x, y, h_ui, z_ui
Ns=size(BS,1);
% transmission
for i=1:Ns
    d(i)=dista(tar(1:2),BS(i,1:2));
    L(i)=p.n1+p.n2*10*log10(d(i));
    S_TRX(i)= 0.001*( 10^(0.1*(BS(i,3)+p.Atx+p.Arx+Ns-L(i))) );
end
[~,ix]=max(S_TRX);
tar(3)=ix;

% backhaul
prp=ones(1,Ns).*inf;
for i=1:Ns
    clix=find([nclet.deploy]==i); % cloudlet which has been deployed in BS_i
    if numel(clix)>0 && nclet(clix).flag==0
        [prp(i)]=graphshortestpath(sparse(E),ix,i);
    end
end
[~,H]=min(prp);
Z=find([nclet.deploy]==H);
end

function D=dista(A,B)
D=sqrt((A(1)-B(1))^2+(A(2)-B(2))^2);
end