import { Node, NetworkGraph, generateNodeTopology } from './network';
import { EnergyModel } from './energyModel';
import {
  HarvestingProfile,
  ConstantHarvesting,
  SolarHarvesting,
  StochasticPoissonHarvesting,
  RealTraceSolarHarvesting,
  createPRNG
} from './harvestingModel';
import { simulateClusteringRound } from './clustering';
import {
  dijkstra,
  astar,
  dpTimeAugmentedLifetime,
  dpMaximinPath,
  ripUpAndReroute
} from './routing';
import {
  SimulationConfig,
  SimulationResults,
  SimulationSummary,
  TimeSeriesData,
  DetailedData,
  NodePosition
} from '../types';

export class WsnSimulator {
  public config: SimulationConfig;
  public nodes: Map<number, Node>;
  public graph: NetworkGraph;
  public energyModel: EnergyModel;
  public harvestingModel: HarvestingProfile | null;
  private rng: () => number;

  public roundNumber: number = 0;
  public aliveNodesHistory: number[] = [];
  public totalEnergyHistory: number[] = [];
  public harvestedEnergyHistory: number[] = [];
  public consumedEnergyHistory: number[] = [];
  public rerouteEventsHistory: number[] = [];
  public fairnessIndexHistory: number[] = [];
  public pdrHistory: number[] = [];
  public clusterHeadsHistory: number[][] = [];
  public clusterAssignmentsHistory: Record<number, number>[] = [];
  public routesHistory: Record<number, [number[] | null, number]>[] = [];
  public energyMatrix: number[][] = []; // [round][nodeId]

  public firstNodeDeathRound: number | null = null;
  public halfNodesDeadRound: number | null = null;
  public lastNodeDeathRound: number | null = null;

  constructor(config: SimulationConfig) {
    this.config = { ...config };
    this.rng = createPRNG(this.config.seed + 1);
    this.energyModel = new EnergyModel();

    // 1. Generate node topology
    this.nodes = generateNodeTopology(
      this.config.nodes,
      this.config.area,
      this.config.area,
      this.config.init_energy,
      this.config.max_capacity,
      this.config.topology_distribution || 'uniform',
      this.config.harvesting_profile === 'shadowed_solar' ? (this.config.shadow_fraction || 0.35) : 0.0,
      this.config.seed
    );

    this.graph = new NetworkGraph(this.nodes);
    this.graph.buildGraph(this.config.transmission_range, this.energyModel);

    // 2. Initialize harvesting model
    this.harvestingModel = this.createHarvestingModel();
  }

  private createHarvestingModel(): HarvestingProfile | null {
    const profile = this.config.harvesting_profile;
    const seed = this.config.seed;

    if (profile === 'none') {
      return null;
    } else if (profile === 'constant') {
      return new ConstantHarvesting(this.config.constant_rate || 0.005);
    } else if (profile === 'solar') {
      return new SolarHarvesting(
        this.config.solar_peak || 0.03,
        this.config.solar_period || 24,
        this.config.solar_day_fraction || 0.5,
        seed
      );
    } else if (profile === 'shadowed_solar') {
      const solar = new SolarHarvesting(
        this.config.solar_peak || 0.03,
        this.config.solar_period || 24,
        this.config.solar_day_fraction || 0.5,
        seed
      );
      // Map spatial shadow multiplier onto nodes
      for (const [id, node] of this.nodes.entries()) {
        solar.setNodeMultiplier(id, node.shadowMultiplier);
      }
      return solar;
    } else if (profile === 'stochastic') {
      return new StochasticPoissonHarvesting(
        this.config.stoch_lambda || 2.0,
        this.config.stoch_quantum || 0.005,
        seed
      );
    } else if (profile === 'trace') {
      return new RealTraceSolarHarvesting(this.config.solar_peak || 0.03, seed);
    }
    return null;
  }

  /**
   * Jain's Fairness Index: J = (sum x_i)^2 / (n * sum x_i^2)
   */
  private calculateFairnessIndex(): number {
    const energies = Array.from(this.nodes.values()).map(n => n.residualEnergy);
    const n = energies.length;
    if (n === 0) return 1.0;
    const sum = energies.reduce((a, b) => a + b, 0);
    const sumSq = energies.reduce((a, b) => a + b * b, 0);
    if (sumSq <= 1e-9) return 1.0;
    return (sum * sum) / (n * sumSq);
  }

  public simulateRound(): boolean {
    this.roundNumber++;
    const kBits = this.config.k_bits || 4000;
    const dataPerNode = this.config.data_per_node_per_round || 4000;
    const aggBits = this.config.aggregation_bits || 1000;
    const baseStationPos: [number, number] = [this.config.bs_x, this.config.bs_y];

    // 1. Ambient Energy Harvesting Step
    let roundHarvestedTotal = 0;
    if (this.harvestingModel) {
      for (const node of this.nodes.values()) {
        if (node.isAlive) {
          const harvestAmt = this.harvestingModel.sampleHarvest(node.id, this.roundNumber, 1.0);
          const stored = node.harvestEnergy(harvestAmt);
          roundHarvestedTotal += stored;
        }
      }
    }
    this.harvestedEnergyHistory.push(roundHarvestedTotal);

    // Record energy matrix snapshot
    const energySnapshot: number[] = [];
    for (let i = 0; i < this.config.nodes; i++) {
      const node = this.nodes.get(i);
      energySnapshot.push(node ? node.residualEnergy : 0.0);
    }
    this.energyMatrix.push(energySnapshot);

    // 2. Clustering Step (LEACH or Harvesting-Aware EH-LEACH)
    const chHarvestModel = !this.config.disable_harvesting_ch ? this.harvestingModel : null;
    const { clusterAssignment, clusterHeads, membersPerCH } = simulateClusteringRound(
      this.nodes,
      this.energyModel,
      this.config.cluster_ratio,
      chHarvestModel,
      this.roundNumber,
      1,
      this.rng
    );

    this.clusterHeadsHistory.push([...clusterHeads]);
    this.clusterAssignmentsHistory.push({ ...clusterAssignment });

    // 3. Path Discovery to Base Station
    const aliveNodesSet = new Set<number>();
    for (const [id, node] of this.nodes.entries()) {
      if (node.isAlive) aliveNodesSet.add(id);
    }

    const routes: Record<number, [number[] | null, number]> = {};

    for (const ch of clusterHeads) {
      if (!aliveNodesSet.has(ch)) {
        routes[ch] = [null, Infinity];
        continue;
      }

      if (!this.config.disable_time_dp) {
        // Time-Augmented DP
        const { bottleneckEnergy, path } = dpTimeAugmentedLifetime(
          this.nodes,
          ch,
          baseStationPos,
          this.energyModel,
          aliveNodesSet,
          this.harvestingModel,
          this.roundNumber,
          this.config.max_dp_hops || 5,
          1,
          kBits,
          this.config.transmission_range
        );
        routes[ch] = [path, bottleneckEnergy];
      } else if (this.config.routing_algorithm === 'dp_maximin') {
        // Maximin DP
        const { bottleneckEnergy, path } = dpMaximinPath(
          this.nodes,
          ch,
          baseStationPos,
          this.energyModel,
          aliveNodesSet,
          this.config.max_dp_hops || 5,
          kBits,
          this.config.transmission_range
        );
        routes[ch] = [path, bottleneckEnergy];
      } else if (this.config.routing_algorithm === 'astar') {
        // A* Pathfinding
        const { cost, path } = astar(
          this.nodes,
          this.graph,
          ch,
          baseStationPos,
          this.energyModel,
          aliveNodesSet,
          kBits,
          this.config.transmission_range
        );
        routes[ch] = [path, cost];
      } else if (this.config.routing_algorithm === 'energy_dijkstra') {
        // Energy-Aware Dijkstra
        const { cost, path } = dijkstra(
          this.nodes,
          this.graph,
          ch,
          baseStationPos,
          this.energyModel,
          aliveNodesSet,
          true,
          kBits,
          this.config.transmission_range
        );
        routes[ch] = [path, cost];
      } else {
        // Standard Dijkstra (Min Energy)
        const { cost, path } = dijkstra(
          this.nodes,
          this.graph,
          ch,
          baseStationPos,
          this.energyModel,
          aliveNodesSet,
          false,
          kBits,
          this.config.transmission_range
        );
        routes[ch] = [path, cost];
      }
    }

    this.routesHistory.push(routes);

    // 4. Data Transmission & Energy Deductions
    let roundConsumedTotal = 0;
    let packetsDelivered = 0;
    let packetsGenerated = 0;

    // 4A: Member nodes transmit to their elected Cluster Head
    for (const [nid, node] of this.nodes.entries()) {
      if (!node.isAlive || node.role !== 'member') continue;
      const chId = node.clusterId;
      if (chId !== -1 && this.nodes.has(chId) && this.nodes.get(chId)!.isAlive) {
        const chNode = this.nodes.get(chId)!;
        const dist = node.distanceTo(chNode);
        const eTx = this.energyModel.transmitEnergy(dataPerNode, dist);
        roundConsumedTotal += node.consumeEnergy(eTx);
        packetsGenerated++;
      }
    }

    // 4B: Cluster Heads aggregate and forward packets along multi-hop routes
    let roundRerouteCount = 0;

    for (const chId of clusterHeads) {
      const chNode = this.nodes.get(chId);
      if (!chNode || !chNode.isAlive) continue;

      const memberCount = (membersPerCH[chId] || []).length;
      if (memberCount > 0) {
        // Aggregation and reception cost
        const eRx = this.energyModel.receiveEnergy(memberCount * dataPerNode);
        const eAgg = this.energyModel.aggregationEnergy(aggBits, memberCount);
        roundConsumedTotal += chNode.consumeEnergy(eRx + eAgg);
      }

      const routeInfo = routes[chId];
      if (!routeInfo || !routeInfo[0] || routeInfo[0].length < 2) {
        continue;
      }

      let path = [...routeInfo[0]];
      let hopIdx = 0;
      let pathSucceeded = false;

      while (hopIdx < path.length - 1) {
        const txId = path[hopIdx];
        const rxId = path[hopIdx + 1];

        if (txId === -1) break;
        const txNode = this.nodes.get(txId);
        if (!txNode || !txNode.isAlive) break;

        let dist = 0;
        if (rxId === -1) {
          // Transmission to Base Station
          dist = Math.sqrt((txNode.x - baseStationPos[0]) ** 2 + (txNode.y - baseStationPos[1]) ** 2);
        } else {
          const rxNode = this.nodes.get(rxId);
          if (!rxNode || !rxNode.isAlive || rxNode.residualEnergy <= 1e-9) {
            // Next-hop relay is dead mid-transmission! Attempt DSU live detour recovery
            if (!this.config.disable_live_reroute) {
              const currentAliveSet = new Set(this.graph.getAliveNodeIds());
              const detour = ripUpAndReroute(
                this.nodes,
                rxId,
                path,
                baseStationPos,
                this.energyModel,
                currentAliveSet,
                aggBits,
                this.config.transmission_range
              );

              if (detour.success && detour.newPath && detour.newPath.length >= 2) {
                path = detour.newPath;
                roundRerouteCount++;
                continue; // Retry transmission from current hop with updated detour path
              }
            }
            break; // Detour failed, packet dropped
          }
          dist = txNode.distanceTo(rxNode);
        }

        // Deduct transmission energy from transmitter
        const eTx = this.energyModel.transmitEnergy(aggBits, dist);
        roundConsumedTotal += txNode.consumeEnergy(eTx);

        // Deduct reception energy from receiver if not Base Station
        if (rxId !== -1) {
          const rxNode = this.nodes.get(rxId)!;
          const eRx = this.energyModel.receiveEnergy(aggBits);
          roundConsumedTotal += rxNode.consumeEnergy(eRx);
        } else {
          pathSucceeded = true;
        }

        hopIdx++;
      }

      if (pathSucceeded) {
        packetsDelivered += Math.max(1, memberCount);
      }
    }

    this.consumedEnergyHistory.push(roundConsumedTotal);
    this.rerouteEventsHistory.push(roundRerouteCount);

    // 5. Round Statistics and Milestone Tracking
    const aliveIds = this.graph.getAliveNodeIds();
    const numAlive = aliveIds.length;
    let totalEnergy = 0;
    for (const nid of aliveIds) {
      totalEnergy += this.nodes.get(nid)!.residualEnergy;
    }

    this.aliveNodesHistory.push(numAlive);
    this.totalEnergyHistory.push(totalEnergy);
    this.fairnessIndexHistory.push(this.calculateFairnessIndex());

    const pdr = packetsGenerated > 0 ? Math.min(1.0, packetsDelivered / packetsGenerated) : (numAlive > 0 ? 1.0 : 0.0);
    this.pdrHistory.push(pdr);

    if (this.firstNodeDeathRound === null && numAlive < this.config.nodes) {
      this.firstNodeDeathRound = this.roundNumber;
    }
    if (this.halfNodesDeadRound === null && numAlive <= Math.floor(this.config.nodes / 2)) {
      this.halfNodesDeadRound = this.roundNumber;
    }
    if (this.lastNodeDeathRound === null && numAlive === 0) {
      this.lastNodeDeathRound = this.roundNumber;
    }

    return numAlive > 0;
  }

  public run(): SimulationResults {
    const startTime = performance.now();
    const maxRounds = this.config.rounds || 200;

    for (let r = 0; r < maxRounds; r++) {
      const stillAlive = this.simulateRound();
      if (!stillAlive) break;
    }

    const executionTimeMs = performance.now() - startTime;

    // Compile summary
    const completedRounds = this.roundNumber;
    const finalAlive = this.aliveNodesHistory[this.aliveNodesHistory.length - 1] || 0;
    const finalEnergy = this.totalEnergyHistory[this.totalEnergyHistory.length - 1] || 0;
    const totalHarvested = this.harvestedEnergyHistory.reduce((a, b) => a + b, 0);
    const totalConsumed = this.consumedEnergyHistory.reduce((a, b) => a + b, 0);
    const totalReroutes = this.rerouteEventsHistory.reduce((a, b) => a + b, 0);
    const avgPdr = this.pdrHistory.length > 0 ? this.pdrHistory.reduce((a, b) => a + b, 0) / this.pdrHistory.length : 0;
    const finalFairness = this.fairnessIndexHistory[this.fairnessIndexHistory.length - 1] || 1.0;

    const summary: SimulationSummary = {
      completed_rounds: completedRounds,
      first_node_death_round: this.firstNodeDeathRound,
      half_nodes_dead_round: this.halfNodesDeadRound,
      last_node_death_round: this.lastNodeDeathRound,
      final_alive_nodes: finalAlive,
      total_nodes: this.config.nodes,
      final_total_energy: Number(finalEnergy.toFixed(5)),
      total_harvested_energy: Number(totalHarvested.toFixed(5)),
      total_consumed_energy: Number(totalConsumed.toFixed(5)),
      total_reroutes: totalReroutes,
      network_lifetime_efficiency: Number(((finalAlive / this.config.nodes) * 100).toFixed(1)),
      average_pdr: Number((avgPdr * 100).toFixed(1)),
      jains_fairness_final: Number(finalFairness.toFixed(3)),
      execution_time_ms: Math.round(executionTimeMs)
    };

    const timeSeries: TimeSeriesData = {
      rounds: Array.from({ length: completedRounds }, (_, i) => i + 1),
      alive_nodes: this.aliveNodesHistory,
      total_energy: this.totalEnergyHistory,
      harvested_energy: this.harvestedEnergyHistory,
      consumed_energy: this.consumedEnergyHistory,
      reroute_events: this.rerouteEventsHistory,
      fairness_index: this.fairnessIndexHistory,
      pdr_history: this.pdrHistory
    };

    const nodePositions: Record<string, NodePosition> = {};
    const nodeShadowMultipliers: Record<string, number> = {};
    for (const [id, node] of this.nodes.entries()) {
      nodePositions[String(id)] = { x: Number(node.x.toFixed(2)), y: Number(node.y.toFixed(2)) };
      nodeShadowMultipliers[String(id)] = node.shadowMultiplier;
    }

    const detailedData: DetailedData = {
      energy_matrix: this.energyMatrix,
      cluster_heads_history: this.clusterHeadsHistory,
      cluster_assignments_history: this.clusterAssignmentsHistory,
      routes_history: this.routesHistory,
      node_positions: nodePositions,
      node_shadow_multipliers: nodeShadowMultipliers,
      base_station_position: [this.config.bs_x, this.config.bs_y],
      fnd_round: this.firstNodeDeathRound,
      hnd_round: this.halfNodesDeadRound
    };

    return {
      summary,
      time_series: timeSeries,
      detailed_data: detailedData,
      configuration: this.config
    };
  }
}
