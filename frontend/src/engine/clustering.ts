import { Node } from './network';
import { EnergyModel } from './energyModel';
import { HarvestingProfile } from './harvestingModel';

export interface ClusterRoundResult {
  clusterAssignment: Record<number, number>; // nodeId -> chId
  clusterHeads: number[];
  membersPerCH: Record<number, number[]>;
}

/**
 * Standard LEACH & Energy-Harvesting Aware EH-LEACH clustering.
 */
export function simulateClusteringRound(
  nodes: Map<number, Node>,
  _energyModel: EnergyModel,
  desiredRatio: number = 0.08,
  harvestingModel: HarvestingProfile | null = null,
  currentTime: number = 0,
  lookaheadRounds: number = 1,
  rng: () => number
): ClusterRoundResult {
  const aliveNodes = Array.from(nodes.values()).filter(n => n.isAlive);
  if (aliveNodes.length === 0) {
    return { clusterAssignment: {}, clusterHeads: [], membersPerCH: {} };
  }

  const numAlive = aliveNodes.length;
  const desiredNumCH = Math.max(1, Math.round(numAlive * desiredRatio));

  // Reset roles
  for (const node of aliveNodes) {
    node.role = 'member';
    node.clusterId = -1;
  }

  // Calculate election probabilities
  let clusterHeads: number[] = [];

  if (harvestingModel) {
    // EH-LEACH: Weight election probability by projected residual energy (current + expected harvest)
    const projectedEnergies: { id: number; projected: number }[] = [];
    let totalProjected = 0;

    for (const node of aliveNodes) {
      const proj = harvestingModel.projectEnergy(
        node.id,
        node.residualEnergy,
        currentTime,
        currentTime + lookaheadRounds,
        node.maxEnergy
      );
      projectedEnergies.push({ id: node.id, projected: proj });
      totalProjected += proj;
    }

    const avgProjected = totalProjected / numAlive;

    // Nodes with above-average projected energy get higher probability
    const candidates: { id: number; score: number }[] = [];
    for (const item of projectedEnergies) {
      const node = nodes.get(item.id)!;
      // Energy factor
      const factor = avgProjected > 1e-9 ? item.projected / avgProjected : 1.0;
      const prob = Math.min(0.95, desiredRatio * factor);
      const roll = rng();
      if (roll < prob) {
        candidates.push({ id: item.id, score: item.projected + (1 - roll) * 0.1 });
      }
    }

    // Sort by projected energy score and pick top desiredNumCH
    candidates.sort((a, b) => b.score - a.score);
    clusterHeads = candidates.slice(0, Math.max(1, desiredNumCH)).map(c => c.id);

    // Fallback if no candidate elected
    if (clusterHeads.length === 0) {
      projectedEnergies.sort((a, b) => b.projected - a.projected);
      clusterHeads = [projectedEnergies[0].id];
    }
  } else {
    // Standard LEACH probability
    const candidates: number[] = [];
    for (const node of aliveNodes) {
      const energyFraction = node.residualEnergy / node.initialEnergy;
      const prob = desiredRatio * Math.min(1.0, Math.max(0.05, energyFraction));
      if (rng() < prob) {
        candidates.push(node.id);
      }
    }

    if (candidates.length > 0) {
      clusterHeads = candidates.slice(0, Math.max(1, desiredNumCH));
    } else {
      // Pick random alive node
      const randomIdx = Math.floor(rng() * aliveNodes.length);
      clusterHeads = [aliveNodes[randomIdx].id];
    }
  }

  // Mark CH roles
  for (const chId of clusterHeads) {
    const chNode = nodes.get(chId);
    if (chNode) {
      chNode.role = 'CH';
      chNode.clusterId = chId;
    }
  }

  // Member association: join nearest cluster head
  const clusterAssignment: Record<number, number> = {};
  const membersPerCH: Record<number, number[]> = {};
  for (const chId of clusterHeads) {
    membersPerCH[chId] = [];
  }

  for (const node of aliveNodes) {
    if (node.role === 'CH') {
      clusterAssignment[node.id] = node.id;
      continue;
    }

    let nearestCH = clusterHeads[0];
    let minDist = Infinity;

    for (const chId of clusterHeads) {
      const chNode = nodes.get(chId)!;
      const dist = node.distanceTo(chNode);
      if (dist < minDist) {
        minDist = dist;
        nearestCH = chId;
      }
    }

    node.clusterId = nearestCH;
    clusterAssignment[node.id] = nearestCH;
    if (membersPerCH[nearestCH]) {
      membersPerCH[nearestCH].push(node.id);
    }
  }

  return {
    clusterAssignment,
    clusterHeads,
    membersPerCH
  };
}
