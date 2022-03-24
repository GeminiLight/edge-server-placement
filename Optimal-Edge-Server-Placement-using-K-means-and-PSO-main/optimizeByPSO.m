function [delay, P]=optimizeByPSO(nclet,user,BS,E,p,CostFunction,options) %#ok<*INUSL>
if nargin<7
    options.useParallel=0;
    options.showdetails=0;
    options.plot=1;
end
VarMax=p.max_pow;
VarMin=p.min_pow;
MaxIt=p.psoiters;
nPop=p.psoN;

nVar=size(BS,1);
% PSO Parameters
VarSize=[1 nVar];   % Size of Decision Variables Matrix
% Coefficients
phi1=2.05;
phi2=2.05;
phi=phi1+phi2;
chi=2/(phi-2+sqrt(phi^2-4*phi));
w=chi;          % Inertia Weight
wdamp=1;        % Inertia Weight Damping Ratio
c1=chi*phi1;    % Personal Learning Coefficient
c2=chi*phi2;    % Global Learning Coefficient

% Velocity Limits
VelMax=0.1.*(VarMax-VarMin);
VelMin=-VelMax;

%% Initialization

empty_particle.Position=[];
empty_particle.Cost=[];
empty_particle.Velocity=[];
empty_particle.Best.Position=[];
empty_particle.Best.Cost=[];

particle=repmat(empty_particle,nPop,1);

GlobalBest.Cost=inf;

if options.useParallel==0
    for i=1:nPop
        particle(i).Position=unifrnd(VarMin,VarMax,VarSize);
        particle(i).Velocity=zeros(VarSize);
        particle(i).Cost=CostFunction(particle(i).Position);
        particle(i).Best.Position=particle(i).Position;
        particle(i).Best.Cost=particle(i).Cost;
        if particle(i).Best.Cost<GlobalBest.Cost
            GlobalBest=particle(i).Best;
        end
    end
elseif options.useParallel==1
    parfor i=1:nPop
        particle(i).Position=unifrnd(VarMin,VarMax,VarSize);
        particle(i).Velocity=zeros(VarSize);
        particle(i).Cost=CostFunction(particle(i).Position);
        particle(i).Best.Position=particle(i).Position;
        particle(i).Best.Cost=particle(i).Cost;
    end
    for i=1:nPop
        if particle(i).Best.Cost<GlobalBest.Cost
            GlobalBest=particle(i).Best;
        end
    end
else
    error('Invalid parallelism options for PSO!')
end
BestCost=zeros(MaxIt,1);

%% PSO Main Loop

for it=1:MaxIt
    if options.useParallel==0
        for i=1:nPop
            particle(i).Velocity = w*particle(i).Velocity ...
                +c1*rand(VarSize).*(particle(i).Best.Position-particle(i).Position) ...
                +c2*rand(VarSize).*(GlobalBest.Position-particle(i).Position);
            particle(i).Velocity = max(particle(i).Velocity,VelMin);
            particle(i).Velocity = min(particle(i).Velocity,VelMax);
            particle(i).Position = particle(i).Position + particle(i).Velocity;
            IsOutside=(particle(i).Position<VarMin | particle(i).Position>VarMax);
            particle(i).Velocity(IsOutside)=-particle(i).Velocity(IsOutside);
            particle(i).Position = max(particle(i).Position,VarMin);
            particle(i).Position = min(particle(i).Position,VarMax);
            particle(i).Cost = CostFunction(particle(i).Position);
            if particle(i).Cost<particle(i).Best.Cost
                particle(i).Best.Position=particle(i).Position;
                particle(i).Best.Cost=particle(i).Cost;
                if particle(i).Best.Cost<GlobalBest.Cost
                    GlobalBest=particle(i).Best;
                end
            end
        end
    elseif options.useParallel==1
        temp=GlobalBest;
        for i=1:nPop
            particle(i).Velocity = w*particle(i).Velocity ...
                +c1*rand(VarSize).*(particle(i).Best.Position-particle(i).Position) ...
                +c2*rand(VarSize).*(temp.Position-particle(i).Position);
        end
        parfor i=1:nPop
            
            particle(i).Velocity = max(particle(i).Velocity,VelMin);
            particle(i).Velocity = min(particle(i).Velocity,VelMax);
            particle(i).Position = particle(i).Position + particle(i).Velocity;
            IsOutside=(particle(i).Position<VarMin | particle(i).Position>VarMax);
            particle(i).Velocity(IsOutside)=-particle(i).Velocity(IsOutside);
            particle(i).Position = max(particle(i).Position,VarMin);
            particle(i).Position = min(particle(i).Position,VarMax);
            particle(i).Cost = CostFunction(particle(i).Position); %#ok<*PFBNS>
            if particle(i).Cost<particle(i).Best.Cost
                particle(i).Best.Position=particle(i).Position;
                particle(i).Best.Cost=particle(i).Cost;
            end
        end
        for i=1:nPop
            if particle(i).Best.Cost<temp.Cost
                temp=particle(i).Best;
            end
        end
        GlobalBest=temp;
    else
        error('Invalid parallelism options for PSO!')
    end
    BestCost(it)=GlobalBest.Cost;
    if options.showdetails==1
        disp(['Iteration ' num2str(it) ': Best Cost = ' num2str(BestCost(it))]);
    end
    w=w*wdamp;
    
end

delay = GlobalBest.Cost;
P = GlobalBest.Position;
%% Results
% if options.plot==1
%     figure(99);
%     plot(BestCost,'LineWidth',2);
%     %semilogy(BestCost,'LineWidth',2);
%     xlabel('Iteration');
%     ylabel('Best Cost');
%     grid on;
%     drawnow;
% end
end