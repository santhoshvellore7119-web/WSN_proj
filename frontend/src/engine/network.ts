import { EnergyModel } from './energyModel';
import { createPRNG } from './harvestingModel';
import { TopologyDistribution } from '../types';

export class Node {
  public id: number;
  public x: number;
  public y: number;
  public initialEnergy: number;
  public maxEnergy: number;
  public residualEnergy: number;
  public role: 'CH' | 'member';
  public clusterId: number;
  public isAlive: boolean;
  public totalHarvestedEnergy: number;
  public totalConsumedEnergy: number;
  public shadowMultiplier: number; // 1.0 = direct sunlight, 0.4 = partial shade, 0.1 = deep shade

  constructor(
    id: number,
    x: number,
    y: number,
    initialEnergy: number = 1.0,
    maxEnergy: number = 2.0,
    shadowMultiplier: number = 1.0
  ) {
    this.id = id;
    this.x = x;
    this.y = y;
    this.initialEnergy = initialEnergy;
    this.maxEnergy = Math.max(initialEnergy, maxEnergy);
    this.residualEnergy = Math.min(initialEnergy, this.maxEnergy);
    this.role = 'member';
    this.clusterId = -1;
    this.isAlive = this.residualEnergy > 0.0;
    this.totalHarvestedEnergy = 0.0;
    this.totalConsumedEnergy = 0.0;
    this.shadowMultiplier = shadowMultiplier;
  }

  public distanceTo(other: { x: number; y: number }): number {
    const dx = this.x - other.x;
    const dy = this.y - other.y;
    return Math.sqrt(dx * dx + dy * dy);
  }

  public consumeEnergy(amount: number): number {
    if (amount <= 0 || !this.isAlive) return 0;
    const actualConsumed = Math.min(this.residualEnergy, amount);
    this.residualEnergy -= actualConsumed;
    this.totalConsumedEnergy += actualConsumed;
    if (this.residualEnergy <= 1e-9) {
      this.residualEnergy = 0;
      this.isAlive = false;
    }
    return actualConsumed;
  }

  public harvestEnergy(amount: number): number {
    if (!this.isAlive || amount <= 0) return 0;
    const availableHeadroom = this.maxEnergy - this.residualEnergy;
    const actualHarvested = Math.min(availableHeadroom, amount);
    this.residualEnergy += actualHarvested;
    this.totalHarvestedEnergy += actualHarvested;
    return actualHarvested;
  }
}

export class NetworkGraph {
  public nodes: Map<number, Node>;
  public adjacencyList: Map<number, { neighborId: number; distance: number; weight: number }[]>;

  constructor(nodes: Map<number, Node>) {
    this.nodes = nodes;
    this.adjacencyList = new Map();
    this.buildGraph();
  }

  public buildGraph(transmissionRange?: number, energyModel?: EnergyModel) {
    this.adjacencyList.clear();
    const nodeIds = Array.from(this.nodes.keys());

    for (const uId of nodeIds) {
      this.adjacencyList.set(uId, []);
    }

    for (let i = 0; i < nodeIds.length; i++) {
      const uId = nodeIds[i];
      const uNode = this.nodes.get(uId)!;
      for (let j = i + 1; j < nodeIds.length; j++) {
        const vId = nodeIds[j];
        const vNode = this.nodes.get(vId)!;
        const dist = uNode.distanceTo(vNode);

        if (!transmissionRange || dist <= transmissionRange) {
          const weight = energyModel ? energyModel.transmitEnergy(4000, dist) : dist;
          this.adjacencyList.get(uId)!.push({ neighborId: vId, distance: dist, weight });
          this.adjacencyList.get(vId)!.push({ neighborId: uId, distance: dist, weight });
        }
      }
    }
  }

  public getAliveNodeIds(): number[] {
    const alive: number[] = [];
    for (const [id, node] of this.nodes.entries()) {
      if (node.isAlive) alive.push(id);
    }
    return alive;
  }
}

/**
 * Generates initial spatial topology of nodes
 */
export function generateNodeTopology(
  count: number,
  areaWidth: number,
  areaHeight: number,
  initialEnergy: number,
  maxCapacity: number,
  distribution: TopologyDistribution = 'uniform',
  shadowFraction: number = 0.0,
  seed: number = 42
): Map<number, Node> {
  const rng = createPRNG(seed);
  const nodes = new Map<number, Node>();

  if (distribution === 'grid') {
    const cols = Math.ceil(Math.sqrt(count));
    const rows = Math.ceil(count / cols);
    const cellW = areaWidth / (cols + 1);
    const cellH = areaHeight / (rows + 1);
    let id = 0;
    for (let r = 1; r <= rows && id < count; r++) {
      for (let c = 1; c <= cols && id < count; c++) {
        const jitterX = (rng() - 0.5) * (cellW * 0.3);
        const jitterY = (rng() - 0.5) * (cellH * 0.3);
        const isShadowed = rng() < shadowFraction;
        const shadowMult = isShadowed ? (rng() < 0.5 ? 0.3 : 0.1) : 1.0;
        nodes.set(
          id,
          new Node(id, c * cellW + jitterX, r * cellH + jitterY, initialEnergy, maxCapacity, shadowMult)
        );
        id++;
      }
    }
  } else if (distribution === 'poisson_cluster') {
    // 3 to 5 cluster centers
    const clusterCenters: { x: number; y: number }[] = [];
    const numClusters = 4;
    for (let k = 0; k < numClusters; k++) {
      clusterCenters.push({
        x: (0.2 + 0.6 * rng()) * areaWidth,
        y: (0.2 + 0.6 * rng()) * areaHeight
      });
    }

    for (let i = 0; i < count; i++) {
      const center = clusterCenters[Math.floor(rng() * numClusters)];
      const radius = rng() * (areaWidth * 0.2);
      const angle = rng() * 2 * Math.PI;
      const x = Math.max(5, Math.min(areaWidth - 5, center.x + radius * Math.cos(angle)));
      const y = Math.max(5, Math.min(areaHeight - 5, center.y + radius * Math.sin(angle)));
      const isShadowed = rng() < shadowFraction;
      const shadowMult = isShadowed ? 0.25 : 1.0;
      nodes.set(i, new Node(i, x, y, initialEnergy, maxCapacity, shadowMult));
    }
  } else {
    // Uniform random distribution
    for (let i = 0; i < count; i++) {
      const x = rng() * areaWidth;
      const y = rng() * areaHeight;
      const isShadowed = rng() < shadowFraction;
      const shadowMult = isShadowed ? 0.25 : 1.0;
      nodes.set(i, new Node(i, x, y, initialEnergy, maxCapacity, shadowMult));
    }
  }

  return nodes;
}
