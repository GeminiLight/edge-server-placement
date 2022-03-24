%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%Select the switch based on the scenario that is to be run
%Scenario 1 - Model is run considering number of users 
%             and cloudlets do not change but number of base
%             stations are changing in every iteration

%Scenario 2 - Model is run considering number of users 
%             and base stations do not change but number of cloudlets
%             are changing in every iteration

%Scenario 3 - Model is run considering number of cloudlets 
%             and base stations do not change but number of users
%             are changing in every iteration

case_select = 3; %1 - vary number of base stations
                 %2 - vary number of cloudlets
                 %3 - vary number of users

if case_select == 1
    run('main_BS.m')
elseif case_select == 2
    run('main_cloudlet.m')
elseif case_select == 3
    run('main_Users.m')
else
    disp('Please select a valid case between 1 and 3 to run the model');
end

