function z=Fitness_func(X)
global nclet user BS E p
z=zeros(1,size(X,1));
for N=1:size(X,1)
    x=X(N,:);
    Pdelay=calcPD(x,nclet,user,BS,E,p);
    Tdelay=calcTD(x,nclet,user,BS,E,p);
    Bdelay=calcBD(x,nclet,user,BS,E,p);
    z(N)=mean(Pdelay+Tdelay+Bdelay)*1e2; % milisec
end
end

function Pdelay=calcPD(x,nclet,user,BS,E,p)
U=size(user,1);
Pdelay=zeros(U,1);
Av=zeros(1,size(BS,1));
Pv=Av;
phi=Av;
PD=Av;
for i=1:size(BS,1)
    Av(i)=numel(find(user(:,3)==i))*p.tsRate;
    c=p.nprocs;
    mu=p.tsExec;
    Pv(i)=Av(i)*mu/c;
    SM=0;
    for j=0:c-1
        SM=SM+(((c*Pv(i))^(j))/factorial(j))+(((c*Pv(i))^c)/factorial(c)); %
    end
    phi(i)=( ((c*Pv(i))^c)/factorial(c)  )*((1-Pv(i))*(SM));
    PD(i)=(phi(i)*mu/((1-Pv(i))*c))+mu;
end
for i=1:U
    Pdelay(i)=PD(user(i,3));
end

end

function Tdelay=calcTD(x,nclet,user,BS,E,p)
U=size(user,1);
light=299792458; % m/s
Ns=size(BS,1);
% transmission
S_TRX=zeros(U,Ns);
dhu=zeros(U,1);
L=zeros(U,1);
for u=1:U
    tar=user(u,:);
    hu=tar(3);
    dhu(u)=dista(tar(1:2),BS(hu,1:2));
    if dhu(u)<=1e-2
        dhu(u)=1e-2;
    end
    L(u)=p.n1+p.n2*10*log10(dhu(u));
    S_TRX(u,hu)= 0.001*( 10^(0.1*(x(hu)+p.Atx+p.Arx+Ns-L(u))) );
end
Iv=zeros(Ns,1);
epsilon=0.001;
for i=1:Ns
    Iv(i)=0;
    for j=1:Ns
        if i~=j
            ujx=find(S_TRX(:,j)>0);
            %uix=find(S_TRX(:,i)>0);
            Iv(i)=Iv(i)+ sum(S_TRX(ujx,i))/(epsilon+numel(ujx));
        end
    end
end
Iu=zeros(U,1);
for i=1:U
    hui=user(i,3);
    Iu(i)=sum(S_TRX(i,:))-S_TRX(i,hui);
end
Dup=zeros(U,1);
Ddown=zeros(U,1);
for i=1:U
    hui=user(i,3);
    Dup(i)=p.BW*log2(1+S_TRX(i,hui)/(p.noise*p.BW+Iv(hui)));
    Ddown(i)=p.BW*log2(1+S_TRX(i,hui)/(p.noise*p.BW+Iu(i)));
end
Tdelay=(p.psize./Dup) + (0.5*p.psize./Ddown)+2*(dhu/light);
Tdelay=Tdelay.*1e6;
end

function Bdelay=calcBD(x,nclet,user,BS,E,p) %#ok<*INUSL>
U=size(user,1);
Bdelay=zeros(U,1);
for i=1:U
    f=user(i,3);
    t=nclet(user(i,4)).deploy;
    [~, us(i).pt]=graphshortestpath(sparse(E),f,t); %#ok<*AGROW>
end
for i=1:U
    khi=us(i).pt;
    Le=zeros(1,numel(khi));
    Oei=zeros(1,numel(khi));
    for j=1:numel(khi)
        Le(j)=numel(find([us.pt]==khi(j)));
        Oei(j)=p.Dbh/p.BW;
    end
    RLi=p.Dbh./Le;
    
    Bdelay(i)=1e4*(p.psize+0.5*p.psize)/min(RLi)+2*sum(Oei);
end
end

function D=dista(A,B)
D=sqrt((A(1)-B(1))^2+(A(2)-B(2))^2);
end