import { SimulationConfig } from './types';

export interface PresetScenario {
  id: string;
  name: string;
  description: string;
  config: SimulationConfig;
}

export const PRESET_SCENARIOS: PresetScenario[] = [
  {
    id: 'default',
    name: 'Standard Solar Diurnal',
    description: '50 nodes in a 100m² area with standard 24-round day/night solar cycle, Time-Augmented DP, EH-LEACH, and DSU live detours enabled.',
    config: {
      nodes: 50,
      rounds: 200,
      area: 100,
      init_energy: 0.15,
      max_capacity: 1.0,
      cluster_ratio: 0.08,
      bs_x: 50,
      bs_y: 50,
      harvesting_profile: 'solar',
      solar_peak: 0.003,
      solar_period: 24,
      solar_day_fraction: 0.5,
      stoch_lambda: 2.0,
      stoch_quantum: 0.005,
      disable_time_dp: false,
      disable_harvesting_ch: false,
      disable_live_reroute: false,
      max_dp_hops: 5,
      routing_algorithm: 'dijkstra',
      seed: 42
    }
  },
  {
    id: 'shadowed_canopy',
    name: 'Forest Canopy / Urban Shadow',
    description: '40% of nodes placed under deep canopy shade (10-30% solar yield). Demonstrates how Time-DP bypasses shaded bottlenecks.',
    config: {
      nodes: 60,
      rounds: 250,
      area: 120,
      init_energy: 0.12,
      max_capacity: 0.8,
      cluster_ratio: 0.08,
      bs_x: 60,
      bs_y: 60,
      harvesting_profile: 'shadowed_solar',
      shadow_fraction: 0.45,
      solar_peak: 0.0025,
      solar_period: 24,
      solar_day_fraction: 0.5,
      stoch_lambda: 2.0,
      stoch_quantum: 0.005,
      disable_time_dp: false,
      disable_harvesting_ch: false,
      disable_live_reroute: false,
      max_dp_hops: 6,
      routing_algorithm: 'dijkstra',
      seed: 108
    }
  },
  {
    id: 'stochastic_rf',
    name: 'Stochastic RF / Thermal Arrivals',
    description: 'Ambient energy arrives as Poisson process (λ = 3.5 arrivals/round). Tests dynamic energy adaptation under random fluctuations.',
    config: {
      nodes: 50,
      rounds: 200,
      area: 100,
      init_energy: 0.10,
      max_capacity: 0.6,
      cluster_ratio: 0.08,
      bs_x: 50,
      bs_y: 50,
      harvesting_profile: 'stochastic',
      solar_peak: 0.003,
      stoch_lambda: 3.5,
      stoch_quantum: 0.0015,
      disable_time_dp: false,
      disable_harvesting_ch: false,
      disable_live_reroute: false,
      max_dp_hops: 5,
      routing_algorithm: 'dijkstra',
      seed: 77
    }
  },
  {
    id: 'dense_mesh',
    name: 'Dense Mesh Scalability (100 Nodes)',
    description: '100 nodes deployed across 150m field. Demonstrates multi-hop routing paths and DSU live reroute resilience.',
    config: {
      nodes: 100,
      rounds: 200,
      area: 150,
      init_energy: 0.15,
      max_capacity: 1.0,
      cluster_ratio: 0.06,
      bs_x: 75,
      bs_y: 75,
      harvesting_profile: 'solar',
      solar_peak: 0.0025,
      solar_period: 24,
      solar_day_fraction: 0.5,
      stoch_lambda: 2.0,
      stoch_quantum: 0.005,
      disable_time_dp: false,
      disable_harvesting_ch: false,
      disable_live_reroute: false,
      max_dp_hops: 6,
      routing_algorithm: 'dijkstra',
      seed: 999
    }
  },
  {
    id: 'battery_depletion',
    name: 'Battery-Only Depletion (No Harvesting)',
    description: 'No ambient energy harvesting. Classic LEACH and shortest-path comparison to highlight baseline battery exhaustion (FND/HND/LND).',
    config: {
      nodes: 40,
      rounds: 150,
      area: 80,
      init_energy: 0.08,
      max_capacity: 0.5,
      cluster_ratio: 0.10,
      bs_x: 40,
      bs_y: 40,
      harvesting_profile: 'none',
      solar_peak: 0.0,
      stoch_lambda: 0.0,
      stoch_quantum: 0.0,
      disable_time_dp: true,
      disable_harvesting_ch: true,
      disable_live_reroute: true,
      max_dp_hops: 4,
      routing_algorithm: 'dijkstra',
      seed: 12
    }
  },
  {
    id: 'nrel_trace',
    name: 'Real-Trace Solar Replay (NREL)',
    description: 'Replays empirical solar irradiance time series with real diurnal curve and cloud attenuation.',
    config: {
      nodes: 50,
      rounds: 240,
      area: 100,
      init_energy: 0.10,
      max_capacity: 0.8,
      cluster_ratio: 0.08,
      bs_x: 50,
      bs_y: 50,
      harvesting_profile: 'trace',
      solar_peak: 0.003,
      stoch_lambda: 2.0,
      stoch_quantum: 0.005,
      disable_time_dp: false,
      disable_harvesting_ch: false,
      disable_live_reroute: false,
      max_dp_hops: 5,
      routing_algorithm: 'dijkstra',
      seed: 55
    }
  }
];

export const DEFAULT_CONFIG: SimulationConfig = PRESET_SCENARIOS[0].config;
