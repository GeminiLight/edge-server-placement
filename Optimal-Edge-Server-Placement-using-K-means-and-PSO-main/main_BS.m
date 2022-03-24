clear
clc
close all

param=10:15;
pname='Number of Base Stations';

global nclet user BS E p

iters=50;
p.nu=100;  %number of users
p.nc=3;    %number of cloudlets
p.tsRate=1/60;  %User average task rate
p.tsExec=50e-3; %Avg task execution time
p.nprocs=16; %Number of processors per cloudlet
p.n1=75.85;  %Pathloss floating intercept
p.n2=3.73;   %Avg path loss exponent
p.W=100;     %
p.L=100;    
p.Atx=24.5;  %Base station antenna gain
p.Arx=2.15;  %User antenna gain
p.fading=-1.59175; %Rayleigh fading co-efficient
p.trxU=27;  %User transmission power
p.noise=4e-19; %Noise density
p.BW=1e12; %1 THz (Hz)
p.psize=128; % bits (Packet size)
p.Dbh= 10e9; % b/s (Data rate per backhaul link)
p.kiters=6;  %number of kMC iterations
p.psoiters=6; %number of PSO iterations
p.psoN=7;  %number of PSO particles
p.min_pow=10; %Range of search in PSO
p.max_pow=200;
p.CostFunction=@Fitness_func;
cc=0;
all_test=iters*numel(param);
wt=waitbar(0,'Simulating');
for it=1:iters
    
    for ts=1:numel(param)
        cc=cc+1;
        waitbar(cc/all_test,wt,sprintf('Simulating... (Iteration %d of %d), [%s=%d]',it,iters,pname,param(ts)));
        Ns=param(ts);
        p.ns=Ns;
        Nu=p.nu;
        Nc=p.nc;
        [BS, E]=define_bs(Ns,p);
        user=define_users(Nu,p);
        clet=define_cloudlets(Nc,p);
        delay=[];
        config=[];
        % for R^{kMC} iterations do
        for ki=1:p.kiters
            V=1:Ns; % (V) <-- V
            new_dep=randperm(Ns,Nc);
            % for all cloudlets k do
            for ci=1:Nc
                clet(ci).deploy=new_dep(ci);
                V(V==new_dep(ci))=[];
            end
            
            % repeat --> until no cloudlet changes location
            while true
                
                prev_dep=new_dep;
                nclet=clet; % (K) <-- all cloudlets
                % for all u_i in U do
                for ui=1:Nu
                   
                    % zui <--  K with min. propagation to hui, In case of ties, choose based on d
                    [Hui, Zui]=min_propagation(user,ui,BS,nclet,p,E);
                    user(ui,3)=Hui;
                    user(ui,4)=Zui;
                    nclet(Zui).user(end+1)=ui;
                    
                    % if zui has U/K users then remove zui from K
                    if numel(nclet(Zui).user)>=Nu/Nc
                        nclet(Zui).flag=1;
                    end
                end
                new_dep=[];
                V=1:Ns; % (V) <-- V
                % for all cloudlets k do
                for ci=1:Nc
                    % Move k to vi closest to its users
                    [ch_i, V]=deploy_clet(nclet,ci,V,BS,user);
                    nclet(ci).deploy=ch_i;
                    % Remove vi from V
                    V(V==ch_i)=[];
                    new_dep(ci)=ch_i; %#ok<*SAGROW>
                end
                
                if numel(find(prev_dep==new_dep))==Nc
                    break
                end
            end
            % Execute PSO for setting transmission power levels
            [delay(ki),config(ki).P]=optimizeByPSO(nclet,user,BS,E,p,p.CostFunction);
            BS(:,3)=config(ki).P(:);
        end
        service_delay_iter(it,ts)=min(delay);
    end
    
end
close(wt);

if iters>1
    serv_delay=mean(service_delay_iter,1);
else
    serv_delay=service_delay_iter;
end
figure
plot(param,serv_delay,'r+-','linewidth',1.5);
xlabel(pname);
ylabel('Service Delay (ms)');
grid on
xlim([param(1) param(end)]);
title('Service Delay obtained by varying number of base stations')


