// Simulation parameter definitions for the ControlPanel
export const SIMULATION_PARAMETERS = [
  {
    name: "nodes",
    label: "Number of Nodes",
    type: "number",
    min: 1,
    max: 200,
    step: 1,
    default: 50,
    explanation: "Total number of sensor nodes in the network",
    unit: "nodes"
  },
  {
    name: "rounds",
    label: "Max Simulation Rounds",
    type: "number",
    min: 1,
    max: 1000,
    step: 10,
    default: 200,
    explanation: "Maximum number of simulation rounds to run",
    unit: "rounds"
  },
  {
    name: "area",
    label: "Field Size",
    type: "number",
    min: 10,
    max: 500,
    step: 5,
    default: 100,
    explanation: "Width and height of the square deployment area",
    unit: "meters"
  },
  {
    name: "init_energy",
    label: "Initial Energy per Node",
    type: "number",
    min: 0.01,
    max: 10,
    step: 0.01,
    default: 1.0,
    explanation: "Starting energy level for each node",
    unit: "Joules"
  },
  {
    name: "max_capacity",
    label: "Max Battery Capacity",
    type: "number",
    min: 0.1,
    max: 20,
    step: 0.1,
    default: 2.0,
    explanation: "Maximum energy each node can store",
    unit: "Joules"
  },
  {
    name: "cluster_ratio",
    label: "Target Cluster Ratio",
    type: "number",
    min: 0.01,
    max: 0.5,
    step: 0.01,
    default: 0.06,
    explanation: "Desired percentage of nodes to become cluster heads",
    unit: "%"
  },
  {
    name: "bs_x",
    label: "Base Station X Position",
    type: "number",
    min: 0,
    max: 500,
    step: 1,
    default: 50,
    explanation: "X coordinate of the base station",
    unit: "meters"
  },
  {
    name: "bs_y",
    label: "Base Station Y Position",
    type: "number",
    min: 0,
    max: 500,
    step: 1,
    default: 50,
    explanation: "Y coordinate of the base station",
    unit: "meters"
  },
  {
    name: "harvesting_profile",
    label: "Energy Harvesting Profile",
    type: "select",
    options: [
      { value: "none", label: "None" },
      { value: "constant", label: "Constant" },
      { value: "solar", label: "Solar (Diurnal)" },
      { value: "stochastic", label: "Stochastic (Poisson)" }
    ],
    default: "solar",
    explanation: "Type of energy harvesting model to use",
    unit: ""
  },
  {
    name: "solar_peak",
    label: "Solar Peak Recharge Rate",
    type: "number",
    min: 0,
    max: 1,
    step: 0.001,
    default: 0.03,
    explanation: "Maximum energy a node can harvest per round under peak sunlight",
    unit: "Joules/round"
  },
  {
    name: "stoch_lambda",
    label: "Poisson Arrival Rate (λ)",
    type: "number",
    min: 0.1,
    max: 20,
    step: 0.1,
    default: 2.0,
    explanation: "Average number of energy arrivals per round",
    unit: "arrivals/round"
  },
  {
    name: "stoch_quantum",
    label: "Energy per Poisson Arrival",
    type: "number",
    min: 0.001,
    max: 0.1,
    step: 0.001,
    default: 0.005,
    explanation: "Amount of energy gained from each Poisson arrival",
    unit: "Joules"
  },
  {
    name: "disable_time_dp",
    label: "Disable Time-Augmented DP",
    type: "checkbox",
    default: false,
    explanation: "Use standard shortest-path routing instead of Time-Augmented DP",
    unit: ""
  },
  {
    name: "disable_harvesting_ch",
    label: "Disable Harvesting-Aware CH",
    type: "checkbox",
    default: false,
    explanation: "Use standard LEACH instead of harvesting-aware cluster head election",
    unit: ""
  },
  {
    name: "disable_live_reroute",
    label: "Disable Live Rerouting",
    type: "checkbox",
    default: false,
    explanation: "Disable DSU-based live rerouting when nodes fail",
    unit: ""
  },
  {
    name: "max_dp_hops",
    label: "Max DP Hop Horizon",
    type: "number",
    min: 1,
    max: 20,
    step: 1,
    default: 5,
    explanation: "Maximum number of hops to consider in DP routing",
    unit: "hops"
  },
  {
    name: "routing_algorithm",
    label: "Routing Algorithm",
    type: "select",
    options: [
      { value: "dijkstra", label: "Dijkstra" },
      { value: "astar", label: "A*" }
    ],
    default: "dijkstra",
    explanation: "Standard routing algorithm to use (when DP is disabled)",
    unit: ""
  },
  {
    name: "seed",
    label: "Random Seed",
    type: "number",
    min: 1,
    max: 9999,
    step: 1,
    default: 42,
    explanation: "Random seed for reproducible node placement",
    unit: ""
  }
];

// Helper function to get parameter by name
export const getParamByName = (name) => {
  return SIMULATION_PARAMETERS.find(param => param.name === name);
};

// Default configuration object
export const getDefaultConfig = () => {
  const config = {};
  SIMULATION_PARAMETERS.forEach(param => {
    config[param.name] = param.default;
  });
  return config;
};