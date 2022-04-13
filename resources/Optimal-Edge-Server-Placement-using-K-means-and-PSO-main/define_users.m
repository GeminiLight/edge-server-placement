function user=define_users(Nu,p)
user=zeros(Nu,4);
user(:,1)=randi([0,p.W],Nu,1);
user(:,2)=randi([0,p.L],Nu,1);
user(:,3)=0; % (h_ui) physical association of user
user(:,4)=0; % (z_ui) base station colocated with the virtual association of user
user(:,5)=0; % (h_z_ui)
end