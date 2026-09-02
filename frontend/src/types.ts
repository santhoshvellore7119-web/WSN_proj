export type HarvestingProfileType = 'none' | 'constant' | 'solar' | 'shadowed_solar' | 'stochastic' | 'trace';

export type RoutingAlgorithmType = 'dijkstra' | 'energy_dijkstra' | 'astar' | 'dp_maximin' | 'dp_time_augmented';

export type TopologyDistribution = 'uniform' | 'poisson_cluster' | 'grid';

export interface SimulationConfig {
  nodes: number;
  rounds: number;
  area: number; // area_width and area_height in meters
  init_energy: number; // Joules
  max_capacity: number; // Joules
  cluster_ratio: number; // e.g. 0.08
  bs_x: number;
  bs_y: number;
  harvesting_profile: HarvestingProfileType;
  solar_peak: number; // Peak recharge in J/round
  solar_period?: number; // Diurnal period in rounds (default 24)
  solar_day_fraction?: number; // Fraction of daytime (default 0.5)
  shadow_fraction?: number; // Fraction of nodes in shade (for shadowed_solar, default 0.3)
  stoch_lambda: number; // Poisson rate
  stoch_quantum: number; // Energy per arrival in Joules
  constant_rate?: number; // Constant recharge rate
  disable_time_dp: boolean;
  disable_harvesting_ch: boolean;
  disable_live_reroute: boolean;
  max_dp_hops: number;
  routing_algorithm: RoutingAlgorithmType;
  transmission_range?: number; // Max transmission range or null for unconstrained
  topology_distribution?: TopologyDistribution;
  seed: number;
  k_bits?: number;
  data_per_node_per_round?: number;
  aggregation_bits?: number;
}

export interface NodePosition {
  x: number;
  y: number;
}

export interface NodeSnapshot {
  id: number;
  x: number;
  y: number;
  residualEnergy: number;
  initialEnergy: number;
  maxEnergy: number;
  isAlive: boolean;
  role: 'CH' | 'member';
  clusterId: number;
  harvestedTotal: number;
  consumedTotal: number;
  harvestMultiplier: number;
}

export interface RoundSummary {
  round: number;
  aliveNodes: number;
  totalEnergy: number;
  harvestedEnergy: number;
  consumedEnergy: number;
  rerouteEvents: number;
  clusterHeadsCount: number;
  jainsFairnessIndex: number;
  deliveryRatio: number;
}

export interface SimulationSummary {
  completed_rounds: number;
  first_node_death_round: number | null; // FND
  half_nodes_dead_round: number | null; // HND
  last_node_death_round: number | null; // LND
  final_alive_nodes: number;
  total_nodes: number;
  final_total_energy: number;
  total_harvested_energy: number;
  total_consumed_energy: number;
  total_reroutes: number;
  network_lifetime_efficiency: number; // % alive at max rounds
  average_pdr: number; // Average Packet Delivery Ratio
  jains_fairness_final: number;
  execution_time_ms: number;
}

export interface TimeSeriesData {
  rounds: number[];
  alive_nodes: number[];
  total_energy: number[];
  harvested_energy: number[];
  consumed_energy: number[];
  reroute_events: number[];
  fairness_index: number[];
  pdr_history: number[];
}

export interface DetailedData {
  energy_matrix: number[][]; // [round][nodeIndex]
  cluster_heads_history: number[][]; // [round] -> list of CH node IDs
  cluster_assignments_history?: Record<number, number>[]; // [round] -> { nodeId: chId }
  routes_history: Record<number, [number[] | null, number]>[]; // [round] -> { chId: [path, cost] }
  node_positions: Record<string, NodePosition>;
  node_shadow_multipliers?: Record<string, number>;
  base_station_position: [number, number];
  fnd_round: number | null;
  hnd_round: number | null;
}

export interface SimulationResults {
  summary: SimulationSummary;
  time_series: TimeSeriesData;
  detailed_data: DetailedData;
  configuration: SimulationConfig;
}

export interface BenchmarkScenarioResult {
  id: string;
  name: string;
  category: 'Baseline' | 'Synchronous Solar' | 'Shadowed Solar' | 'Stochastic Poisson';
  strategy: 'Unaware' | 'Energy-Aware' | 'Adaptive (Time-DP + DSU)';
  fnd: number | null;
  hnd: number | null;
  lnd: number | null;
  finalAliveNodes: number;
  totalNodes: number;
  finalTotalEnergy: number;
  totalHarvested: number;
  rerouteCount: number;
  config: Partial<SimulationConfig>;
  timeSeriesSummary?: {
    rounds: number[];
    aliveNodes: number[];
    totalEnergy: number[];
  };
}

export interface BenchmarkResults {
  scenarios: BenchmarkScenarioResult[];
  timestamp: string;
  seed: number;
  nodesCount: number;
  maxRounds: number;
}

export interface ScalabilityResultPoint {
  nodes: number;
  baseline_fnd: number | null;
  baseline_alive: number;
  adaptive_fnd: number | null;
  adaptive_alive: number;
  computation_ms: number;
}

export interface HeterogeneityResultPoint {
  shadowFraction: number; // 0.0 to 1.0
  unaware_fnd: number | null;
  unaware_alive: number;
  adaptive_fnd: number | null;
  adaptive_alive: number;
  energyRetainedJ: number;
}

export interface SavedRun {
  id: string;
  name: string;
  createdAt: string;
  config: SimulationConfig;
  summary: SimulationSummary;
  results?: SimulationResults;
}
