function [BS, E]=define_bs(Ns,p)
BS=zeros(Ns,4);
BS(:,1)=randi([0,p.W],Ns,1);
BS(:,2)=randi([0,p.L],Ns,1);
BS(:,3)=100; % initial transmmit power
BS(:,4)=0;

D=zeros(Ns);
for i=1:Ns
    for j=i+1:Ns
        D(i,j)=dista(BS(i,1:2),BS(j,1:2));
    end
end
D=D+D';
E=graphminspantree(sparse(D));
E=full(E);
E=E+E';
end

function D=dista(A,B)
D=sqrt((A(1)-B(1))^2+(A(2)-B(2))^2);
end