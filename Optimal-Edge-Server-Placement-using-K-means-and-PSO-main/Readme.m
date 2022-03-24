%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%Through this model, we can find the ideal locations for placing the
%cloudlets so that end to end service delay is minimized.

%This algorithm uses backhaul delay, processing delay to find ideal 
%locations for placing the cloudlets. Serice delay is used to select
%the transmission powers for various base stations. In this way, end to
%service delay can be minimized through this model.


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%Optimal_Selection_of_Cloudlets_main.m - main function that should be
%executed to run the model. It consists of 3 scenarios as follows:

%Scenario 1 - Model is run considering for different number of base
%             stations where number of users and cloudlets are fixed

%Scenario 2 - Model is run considering for different number of cloudlets
%             where number of users and base stations are fixed

%Scenario 3 - Model is run considering for different number of users
%             where number of cloudlets and base stations are fixed

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%main_BS.m - This file is run for executing scenario 1

%Input - The number of base stations for which cloudlets will compute can
%be changed and number of users and cloudlets is a fixed value.

%Output - PSO and K-means clustering are run for various iterations to
%compute ideal transmission levels for base stations along with locations
%where cloudlets can be placed. The algorithm is run for multiple times and
%service delay is plotted with respect to iterations.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%main_cloudlet.m - This file is run for executing scenario 2

%Input - The number of cloudlets can be changed and number of users and
%base stations is a fixed value.

%Output - PSO and K-means clustering are run for various iterations to
%compute ideal transmission levels for base stations along with locations
%where cloudlets can be placed.The algorithm is run for multiple times and
%service delay is plotted with respect to iterations.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%main_Users.m - This file is run for executing scenario 3

%Input - The number of users for which cloudlets will compute can
%be changed and number of cloudlets and base stations is a fixed value.

%Output - PSO and K-means clustering are run for various iterations to
%compute ideal transmission levels for base stations along with locations
%where cloudlets can be placed.The algorithm is run for multiple times and
%service delay is plotted with respect to iterations.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%function define_bs.m

%Input - This file takes number of base stations and given ranges of
%dimensions as inputs.

%Output - Output consists of location of base stations
%randomly in a given search and assigns a default transmission power. The
%backhauls links between any two basestations are designed using minimum
%spanning tree for graphs

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%function define_users.m

%Input - This file takes number of users and given ranges of
%dimensions as inputs.

%Output - Output consists of location of users in x and y co-ordinates
%randomly in a given search and it initializes the assigned base stations
%and cloudlet indices as 0 initially

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%function define_cloudlets.m

%Input - This file takes number of cloudlets as input

%Output - A structure for maintaing the assigned users and location of base
%station at which cloudlets will be located is initialized with empty
%values.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%function deploy_clet.m

%Input - This file takes user details, available base stations, number of
%cloudlets and their current locations along with given parameters

%Output - After predicting the optimal cloudlet location for all users,
%cloudlet is further moved closer to the user (k-means) for k times and new
%optimal locations are obtained.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%function optimizeByPSO.m

%Input - This file takes user details, available base stations, number of
%cloudlets and their current locations along with given parameters

%Output - PSO(Particle Swarm Optimization) is run to find optimal powers 
%for all base stations such that total service delay is minimized.
