%% =========================================================================
%  MATLAB / SIMULINK INITIALIZATION SCRIPT: LQR vs FIXED STSMC vs ADAPTIVE STSMC
%  Execute this script before running the Simulink simulation model (.slx)
%  Department of Electrical and Computer Science Engineering, SELECT, VIT
%  Authors: Santhosh G (25BEL0016), Thilang T V (25BEL0036), Ananthakrishnan R (25BEL0005)
%% =========================================================================
clear; clc;

%% 1. PLANT MATRICES (Example: Linearized Inverted Pendulum on a Cart)
%  State vector: x = [position; velocity; angle; angular_velocity]
M = 1.0;    % Cart mass (kg)
m = 0.1;    % Pendulum bob mass (kg)
l = 0.5;    % Pendulum length to center of mass (m)
g = 9.81;   % Gravitational acceleration (m/s^2)

% Continuous-Time State Space Matrices
A = [0, 1, 0, 0;
     0, 0, -m*g/M, 0;
     0, 0, 0, 1;
     0, 0, (M+m)*g/(M*l), 0];
B = [0; 1/M; 0; -1/(M*l)];
C = eye(4);
D = zeros(4,1);

%% 2. LQR CONTROLLER TUNING PARAMETERS
% Q: State penalty matrix (Penalize position x(1) and angle x(3) heavily)
Q_lqr = diag([100.0, 1.0, 200.0, 1.0]); 
% R: Control effort penalty matrix (Lower R = faster response; Higher R = less actuator effort)
R_lqr = 0.1;

% Solve Continuous-Time Algebraic Riccati Equation
[K_lqr, P_lqr, E_lqr] = lqr(A, B, Q_lqr, R_lqr);
fprintf('[1] LQR Gain Matrix K successfully computed:\n');
disp(K_lqr);

%% 3. FIXED SUPER-TWISTING SMC (STSMC) TUNING PARAMETERS
lambda_smc  = 12.0;    % Sliding manifold bandwidth slope: s = e_dot + lambda*e
L_dist_est  = 15.0;    % Assumed upper bound on disturbance derivative: |d_dot(t)| <= L

% Theoretical Moreno-Osorio Lyapunov Gains:
k1_fixed    = 1.5 * sqrt(L_dist_est);  % Proportional fractional gain (~5.81)
k2_fixed    = 1.1 * L_dist_est;         % Integral switching gain (~16.50)
eps_smooth  = 1e-4;                     % Boundary layer smoothing factor: s / (|s| + eps)

fprintf('[2] Fixed STSMC Initialized: lambda=%.1f, k1=%.2f, k2=%.2f, eps=%.1e\n', ...
    lambda_smc, k1_fixed, k2_fixed, eps_smooth);

%% 4. ADAPTIVE SUPER-TWISTING SMC (ASTSMC) TUNING PARAMETERS
alpha_min   = 2.0;     % Minimum baseline proportional gain (lower bound)
alpha_init  = 2.5;     % Initial gain at t = 0
rho_adapt   = 10.0;    % Adaptation acceleration rate (gain increase speed when |s| > mu)
mu_deadband = 0.01;    % Deadband threshold (|s| <= mu triggers gain decay)
sigma_leak  = 1.2;     % Gain leakage/decay rate to prevent drift toward infinity
gamma_rel   = 2.0;     % Proportional-to-integral coupling ratio: beta(t) = gamma * alpha(t)

fprintf('[3] Adaptive STSMC Initialized: alpha_min=%.1f, rho=%.1f, mu=%.3f, sigma=%.1f\n', ...
    alpha_min, rho_adapt, mu_deadband, sigma_leak);
fprintf('=========================================================================\n');
fprintf(' Workspace ready! You can now launch your Simulink simulation.\n');
