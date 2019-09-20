%% create MPC controller object with sample time
mpc1 = mpc(plant_C, 1);
%% specify prediction horizon
mpc1.PredictionHorizon = 30;
%% specify control horizon
mpc1.ControlHorizon = 2;
%% specify nominal values for inputs and outputs
mpc1.Model.Nominal.U = [0;99];
mpc1.Model.Nominal.Y = 0;
%% specify overall adjustment factor applied to weights
beta = 0.26714;
%% specify weights
mpc1.Weights.MV = 0*beta;
mpc1.Weights.MVRate = 0.1/beta;
mpc1.Weights.OV = 1*beta;
mpc1.Weights.ECR = 100000;
%% specify overall adjustment factor applied to estimation model gains
alpha = 0.33113;
%% adjust default output disturbance model gains
setoutdist(mpc1, 'model', getoutdist(mpc1)*alpha);
%% adjust default measurement noise model gains
mpc1.Model.Noise = mpc1.Model.Noise/alpha;
%% specify simulation options
options = mpcsimopt();
options.RefLookAhead = 'off';
options.MDLookAhead = 'off';
options.Constraints = 'on';
options.OpenLoop = 'off';
%% run simulation
sim(mpc1, 14001, mpc1_RefSignal, mpc1_MDSignal, options);
