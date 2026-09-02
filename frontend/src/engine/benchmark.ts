import { WsnSimulator } from './simulator';
import {
  SimulationConfig,
  BenchmarkResults,
  BenchmarkScenarioResult,
  ScalabilityResultPoint,
  HeterogeneityResultPoint
} from '../types';

export function runComprehensiveBenchmark(
  numNodes: number = 50,
  maxRounds: number = 300,
  seed: number = 42
): BenchmarkResults {
  const area = 100.0;
  const bs_x = 50.0;
  const bs_y = 50.0;
  const init_energy = 0.05; // 50 mJ so battery depletion and harvesting effects clearly manifest
  const max_capacity = 0.50;
  const cluster_ratio = 0.08;

  const baseConfig: SimulationConfig = {
    nodes: numNodes,
    rounds: maxRounds,
    area,
    init_energy,
    max_capacity,
    cluster_ratio,
    bs_x,
    bs_y,
    harvesting_profile: 'none',
    solar_peak: 0.0006,
    stoch_lambda: 2.0,
    stoch_quantum: 0.0003,
    disable_time_dp: false,
    disable_harvesting_ch: false,
    disable_live_reroute: false,
    max_dp_hops: 5,
    routing_algorithm: 'dijkstra',
    seed
  };

  const scenarioDefs: {
    id: string;
    name: string;
    category: BenchmarkScenarioResult['category'];
    strategy: BenchmarkScenarioResult['strategy'];
    override: Partial<SimulationConfig>;
  }[] = [
    // 1. Baseline
    {
      id: 'sc-1',
      name: 'Baseline: No Energy Harvesting',
      category: 'Baseline',
      strategy: 'Unaware',
      override: {
        harvesting_profile: 'none',
        disable_time_dp: true,
        disable_harvesting_ch: true,
        disable_live_reroute: true,
        routing_algorithm: 'dijkstra'
      }
    },
    // 2. Synchronous Solar - Unaware
    {
      id: 'sc-2',
      name: 'Solar: Unaware Dijkstra',
      category: 'Synchronous Solar',
      strategy: 'Unaware',
      override: {
        harvesting_profile: 'solar',
        solar_peak: 0.0006,
        disable_time_dp: true,
        disable_harvesting_ch: true,
        disable_live_reroute: true,
        routing_algorithm: 'dijkstra'
      }
    },
    // 3. Synchronous Solar - Energy Aware
    {
      id: 'sc-3',
      name: 'Solar: Energy-Aware Dijkstra',
      category: 'Synchronous Solar',
      strategy: 'Energy-Aware',
      override: {
        harvesting_profile: 'solar',
        solar_peak: 0.0006,
        disable_time_dp: true,
        disable_harvesting_ch: true,
        disable_live_reroute: true,
        routing_algorithm: 'energy_dijkstra'
      }
    },
    // 4. Synchronous Solar - Adaptive (Time DP + EH-LEACH + DSU)
    {
      id: 'sc-4',
      name: 'Solar: Time-DP + Harv-CH + DSU',
      category: 'Synchronous Solar',
      strategy: 'Adaptive (Time-DP + DSU)',
      override: {
        harvesting_profile: 'solar',
        solar_peak: 0.0006,
        disable_time_dp: false,
        disable_harvesting_ch: false,
        disable_live_reroute: false
      }
    },
    // 5. Heterogeneous Shadowed Solar - Unaware
    {
      id: 'sc-5',
      name: 'Shadowed Solar: Unaware Dijkstra',
      category: 'Shadowed Solar',
      strategy: 'Unaware',
      override: {
        harvesting_profile: 'shadowed_solar',
        shadow_fraction: 0.4,
        solar_peak: 0.0006,
        disable_time_dp: true,
        disable_harvesting_ch: true,
        disable_live_reroute: true,
        routing_algorithm: 'dijkstra'
      }
    },
    // 6. Heterogeneous Shadowed Solar - Energy-Aware
    {
      id: 'sc-6',
      name: 'Shadowed Solar: Energy-Aware Dijkstra',
      category: 'Shadowed Solar',
      strategy: 'Energy-Aware',
      override: {
        harvesting_profile: 'shadowed_solar',
        shadow_fraction: 0.4,
        solar_peak: 0.0006,
        disable_time_dp: true,
        disable_harvesting_ch: true,
        disable_live_reroute: true,
        routing_algorithm: 'energy_dijkstra'
      }
    },
    // 7. Heterogeneous Shadowed Solar - Adaptive
    {
      id: 'sc-7',
      name: 'Shadowed Solar: Time-DP + Harv-CH + DSU',
      category: 'Shadowed Solar',
      strategy: 'Adaptive (Time-DP + DSU)',
      override: {
        harvesting_profile: 'shadowed_solar',
        shadow_fraction: 0.4,
        solar_peak: 0.0006,
        disable_time_dp: false,
        disable_harvesting_ch: false,
        disable_live_reroute: false
      }
    },
    // 8. Stochastic Poisson - Unaware
    {
      id: 'sc-8',
      name: 'Stochastic Poisson: Unaware Dijkstra',
      category: 'Stochastic Poisson',
      strategy: 'Unaware',
      override: {
        harvesting_profile: 'stochastic',
        stoch_lambda: 2.0,
        stoch_quantum: 0.0003,
        disable_time_dp: true,
        disable_harvesting_ch: true,
        disable_live_reroute: true,
        routing_algorithm: 'dijkstra'
      }
    },
    // 9. Stochastic Poisson - Adaptive
    {
      id: 'sc-9',
      name: 'Stochastic Poisson: Time-DP + Harv-CH + DSU',
      category: 'Stochastic Poisson',
      strategy: 'Adaptive (Time-DP + DSU)',
      override: {
        harvesting_profile: 'stochastic',
        stoch_lambda: 2.0,
        stoch_quantum: 0.0003,
        disable_time_dp: false,
        disable_harvesting_ch: false,
        disable_live_reroute: false
      }
    }
  ];

  const results: BenchmarkScenarioResult[] = [];

  for (const def of scenarioDefs) {
    const config: SimulationConfig = { ...baseConfig, ...def.override };
    const sim = new WsnSimulator(config);
    const simResult = sim.run();

    results.push({
      id: def.id,
      name: def.name,
      category: def.category,
      strategy: def.strategy,
      fnd: simResult.summary.first_node_death_round,
      hnd: simResult.summary.half_nodes_dead_round,
      lnd: simResult.summary.last_node_death_round,
      finalAliveNodes: simResult.summary.final_alive_nodes,
      totalNodes: numNodes,
      finalTotalEnergy: simResult.summary.final_total_energy,
      totalHarvested: simResult.summary.total_harvested_energy,
      rerouteCount: simResult.summary.total_reroutes,
      config: def.override,
      timeSeriesSummary: {
        rounds: simResult.time_series.rounds,
        aliveNodes: simResult.time_series.alive_nodes,
        totalEnergy: simResult.time_series.total_energy
      }
    });
  }

  return {
    scenarios: results,
    timestamp: new Date().toISOString(),
    seed,
    nodesCount: numNodes,
    maxRounds
  };
}

export function runScalabilitySweep(
  nodeCounts: number[] = [20, 50, 80, 120, 160],
  maxRounds: number = 150,
  seed: number = 42
): ScalabilityResultPoint[] {
  const points: ScalabilityResultPoint[] = [];

  for (const n of nodeCounts) {
    const t0 = performance.now();

    // Baseline simulation
    const baseConfig: SimulationConfig = {
      nodes: n,
      rounds: maxRounds,
      area: 100,
      init_energy: 0.05,
      max_capacity: 0.5,
      cluster_ratio: 0.08,
      bs_x: 50,
      bs_y: 50,
      harvesting_profile: 'solar',
      solar_peak: 0.0006,
      stoch_lambda: 2.0,
      stoch_quantum: 0.0003,
      disable_time_dp: true,
      disable_harvesting_ch: true,
      disable_live_reroute: true,
      max_dp_hops: 5,
      routing_algorithm: 'dijkstra',
      seed
    };
    const simBase = new WsnSimulator(baseConfig).run();

    // Adaptive simulation
    const adaptConfig: SimulationConfig = {
      ...baseConfig,
      disable_time_dp: false,
      disable_harvesting_ch: false,
      disable_live_reroute: false
    };
    const simAdapt = new WsnSimulator(adaptConfig).run();

    const elapsed = performance.now() - t0;

    points.push({
      nodes: n,
      baseline_fnd: simBase.summary.first_node_death_round,
      baseline_alive: simBase.summary.final_alive_nodes,
      adaptive_fnd: simAdapt.summary.first_node_death_round,
      adaptive_alive: simAdapt.summary.final_alive_nodes,
      computation_ms: Math.round(elapsed)
    });
  }

  return points;
}

export function runHeterogeneitySweep(
  shadowFractions: number[] = [0.0, 0.2, 0.4, 0.6, 0.8],
  nodes: number = 50,
  maxRounds: number = 150,
  seed: number = 42
): HeterogeneityResultPoint[] {
  const points: HeterogeneityResultPoint[] = [];

  for (const sf of shadowFractions) {
    const config: SimulationConfig = {
      nodes,
      rounds: maxRounds,
      area: 100,
      init_energy: 0.05,
      max_capacity: 0.5,
      cluster_ratio: 0.08,
      bs_x: 50,
      bs_y: 50,
      harvesting_profile: 'shadowed_solar',
      shadow_fraction: sf,
      solar_peak: 0.0006,
      stoch_lambda: 2.0,
      stoch_quantum: 0.0003,
      disable_time_dp: true,
      disable_harvesting_ch: true,
      disable_live_reroute: true,
      max_dp_hops: 5,
      routing_algorithm: 'dijkstra',
      seed
    };

    const simUnaware = new WsnSimulator(config).run();
    const simAdaptive = new WsnSimulator({
      ...config,
      disable_time_dp: false,
      disable_harvesting_ch: false,
      disable_live_reroute: false
    }).run();

    points.push({
      shadowFraction: sf,
      unaware_fnd: simUnaware.summary.first_node_death_round,
      unaware_alive: simUnaware.summary.final_alive_nodes,
      adaptive_fnd: simAdaptive.summary.first_node_death_round,
      adaptive_alive: simAdaptive.summary.final_alive_nodes,
      energyRetainedJ: simAdaptive.summary.final_total_energy
    });
  }

  return points;
}
