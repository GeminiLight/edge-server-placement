clear
clc
close all

param=100:100:1000;
pname='Number of Users';

global nclet user BS E p

iters=20;
p.ns=10;
p.nc=3;
p.tsRate=1/60;
p.tsExec=50e-3;
p.nprocs=16;
p.n1=75.85;
p.n2=3.73;
p.W=100;
p.L=100;
p.Atx=24.5;
p.Arx=2.15;
p.fading=-1.59175;
p.trxU=27;
p.noise=4e-19;
p.BW=1e12; %1 THz (Hz)
p.psize=128; % bits
p.Dbh= 10e9; % b/s
p.kiters=6;
p.psoiters=6;
p.psoN=7;
p.min_pow=10;
p.max_pow=200;
p.CostFunction=@Fitness_func;
cc=0;
all_test=iters*numel(param);
wt=waitbar(0,'Simulating');
for it=1:iters
    
    for ts=1:numel(param)
        cc=cc+1;
        waitbar(cc/all_test,wt,sprintf('Simulating... (Iteration %d of %d), [%s=%d]',it,iters,pname,param(ts)));
        Nu=param(ts);
        p.nu=Nu;
        Ns=p.ns;
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
title('Service Delay obtained by varying number of users')

