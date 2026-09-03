import { Node, NetworkGraph } from './network';
import { EnergyModel } from './energyModel';
import { HarvestingProfile } from './harvestingModel';
import { UnionFind } from './dsu';

export interface RouteResult {
  path: number[] | null; // Sequence of node IDs terminating at -1 (Base Station)
  cost: number;
}

/**
 * Dijkstra's Shortest / Minimum-Energy Path from source to Base Station (-1).
 * If energyAware is true, edge weights are penalized by the inverse of the transmitter's residual energy.
 */
export function dijkstra(
  nodes: Map<number, Node>,
  _graph: NetworkGraph,
  source: number,
  baseStationPos: [number, number],
  energyModel: EnergyModel,
  aliveNodesSet: Set<number>,
  energyAware: boolean = false,
  kBits: number = 4000,
  transmissionRange?: number
): RouteResult {
  if (!aliveNodesSet.has(source)) {
    return { path: null, cost: Infinity };
  }

  const distances: Map<number, number> = new Map();
  const previous: Map<number, number | null> = new Map();
  const unvisited: Set<number> = new Set();

  for (const nid of aliveNodesSet) {
    distances.set(nid, Infinity);
    previous.set(nid, null);
    unvisited.add(nid);
  }
  // -1 represents Base Station
  distances.set(-1, Infinity);
  previous.set(-1, null);
  unvisited.add(-1);

  distances.set(source, 0);

  while (unvisited.size > 0) {
    // Find min distance unvisited node
    let current: number | null = null;
    let minDist = Infinity;
    for (const nid of unvisited) {
      const d = distances.get(nid)!;
      if (d < minDist) {
        minDist = d;
        current = nid;
      }
    }

    if (current === null || minDist === Infinity) break;
    if (current === -1) break; // Reached Base Station!

    unvisited.delete(current);
    const currNode = nodes.get(current)!;

    // 1. Consider direct link from current node to Base Station
    const distToBS = Math.sqrt(
      (currNode.x - baseStationPos[0]) ** 2 + (currNode.y - baseStationPos[1]) ** 2
    );
    if (!transmissionRange || distToBS <= transmissionRange) {
      let edgeCost = energyModel.transmitEnergy(kBits, distToBS);
      if (energyAware) {
        edgeCost /= Math.max(0.001, currNode.residualEnergy);
      }
      const alt = minDist + edgeCost;
      if (alt < distances.get(-1)!) {
        distances.set(-1, alt);
        previous.set(-1, current);
      }
    }

    // 2. Consider neighbor relays
    for (const neighborId of aliveNodesSet) {
      if (neighborId === current || !unvisited.has(neighborId)) continue;
      const nbrNode = nodes.get(neighborId)!;
      const dist = currNode.distanceTo(nbrNode);
      if (!transmissionRange || dist <= transmissionRange) {
        let edgeCost = energyModel.transmitEnergy(kBits, dist) + energyModel.receiveEnergy(kBits);
        if (energyAware) {
          edgeCost /= Math.max(0.001, currNode.residualEnergy);
        }
        const alt = minDist + edgeCost;
        if (alt < distances.get(neighborId)!) {
          distances.set(neighborId, alt);
          previous.set(neighborId, current);
        }
      }
    }
  }

  // Reconstruct path
  if (distances.get(-1) === Infinity) {
    return { path: null, cost: Infinity };
  }

  const path: number[] = [];
  let curr: number | null = -1;
  while (curr !== null) {
    path.unshift(curr);
    if (curr === source) break;
    curr = previous.get(curr) ?? null;
  }

  return { path, cost: distances.get(-1)! };
}

/**
 * A* Pathfinding using Euclidean distance heuristic to Base Station
 */
export function astar(
  nodes: Map<number, Node>,
  _graph: NetworkGraph,
  source: number,
  baseStationPos: [number, number],
  energyModel: EnergyModel,
  aliveNodesSet: Set<number>,
  kBits: number = 4000,
  transmissionRange?: number
): RouteResult {
  if (!aliveNodesSet.has(source)) {
    return { path: null, cost: Infinity };
  }

  const gScore: Map<number, number> = new Map();
  const fScore: Map<number, number> = new Map();
  const cameFrom: Map<number, number | null> = new Map();
  const openSet: Set<number> = new Set([source]);

  for (const nid of aliveNodesSet) {
    gScore.set(nid, Infinity);
    fScore.set(nid, Infinity);
  }
  gScore.set(-1, Infinity);
  fScore.set(-1, Infinity);

  const heuristic = (nid: number): number => {
    if (nid === -1) return 0;
    const n = nodes.get(nid)!;
    const dist = Math.sqrt((n.x - baseStationPos[0]) ** 2 + (n.y - baseStationPos[1]) ** 2);
    return energyModel.transmitEnergy(kBits, dist);
  };

  gScore.set(source, 0);
  fScore.set(source, heuristic(source));

  while (openSet.size > 0) {
    let current: number | null = null;
    let lowestF = Infinity;
    for (const nid of openSet) {
      const f = fScore.get(nid)!;
      if (f < lowestF) {
        lowestF = f;
        current = nid;
      }
    }

    if (current === null) break;
    if (current === -1) {
      // Reconstruct path
      const path: number[] = [];
      let curr: number | null = -1;
      while (curr !== null) {
        path.unshift(curr);
        if (curr === source) break;
        curr = cameFrom.get(curr) ?? null;
      }
      return { path, cost: gScore.get(-1)! };
    }

    openSet.delete(current);
    const currNode = nodes.get(current)!;

    // Direct link to BS
    const distToBS = Math.sqrt(
      (currNode.x - baseStationPos[0]) ** 2 + (currNode.y - baseStationPos[1]) ** 2
    );
    if (!transmissionRange || distToBS <= transmissionRange) {
      const tentativeG = gScore.get(current)! + energyModel.transmitEnergy(kBits, distToBS);
      if (tentativeG < gScore.get(-1)!) {
        cameFrom.set(-1, current);
        gScore.set(-1, tentativeG);
        fScore.set(-1, tentativeG);
        openSet.add(-1);
      }
    }

    // Neighbors
    for (const neighborId of aliveNodesSet) {
      if (neighborId === current) continue;
      const nbrNode = nodes.get(neighborId)!;
      const dist = currNode.distanceTo(nbrNode);
      if (!transmissionRange || dist <= transmissionRange) {
        const edgeCost = energyModel.transmitEnergy(kBits, dist) + energyModel.receiveEnergy(kBits);
        const tentativeG = gScore.get(current)! + edgeCost;
        if (tentativeG < gScore.get(neighborId)!) {
          cameFrom.set(neighborId, current);
          gScore.set(neighborId, tentativeG);
          fScore.set(neighborId, tentativeG + heuristic(neighborId));
          openSet.add(neighborId);
        }
      }
    }
  }

  return { path: null, cost: Infinity };
}

/**
 * Time-Augmented Dynamic Programming ($dp[v][h][t]$)
 * 
 * Takes incoming energy harvesting into account while packets traverse intermediate hops.
 * Maximizes bottleneck residual energy along hop horizon H and arrival time expansion T.
 */
export function dpTimeAugmentedLifetime(
  nodes: Map<number, Node>,
  source: number,
  baseStationPos: [number, number],
  energyModel: EnergyModel,
  aliveNodesSet: Set<number>,
  harvestingModel: HarvestingProfile | null,
  currentTime: number,
  maxHops: number = 5,
  hopDelay: number = 1,
  kBits: number = 4000,
  transmissionRange?: number
): { bottleneckEnergy: number; path: number[] | null } {
  if (!aliveNodesSet.has(source)) {
    return { bottleneckEnergy: 0, path: null };
  }

  const aliveArray = Array.from(aliveNodesSet);
  const H = Math.max(1, Math.min(maxHops, aliveArray.length + 1));

  // dp[v][h][t]: maximum bottleneck energy to reach node v at hop h and time offset t
  // Reconstruct optimal path and predecessor
  interface DPState {
    bottleneck: number;
    pred: number | null;
    prevH: number;
    prevT: number;
  }

  // Map: `${v}_${h}_${t}` -> DPState
  const dp: Map<string, DPState> = new Map();
  const key = (v: number, h: number, t: number) => `${v}_${h}_${t}`;

  const sourceNode = nodes.get(source)!;
  const initialEnergy = sourceNode.residualEnergy;

  dp.set(key(source, 0, 0), {
    bottleneck: initialEnergy,
    pred: null,
    prevH: 0,
    prevT: 0
  });

  // Direct BS transmission option
  const distToBS = Math.sqrt(
    (sourceNode.x - baseStationPos[0]) ** 2 + (sourceNode.y - baseStationPos[1]) ** 2
  );
  let bestBSBottleneck = 0;
  let bestBSState: { pred: number; prevH: number; prevT: number } | null = null;

  if (!transmissionRange || distToBS <= transmissionRange) {
    const txCost = energyModel.transmitEnergy(kBits, distToBS);
    if (initialEnergy >= txCost) {
      bestBSBottleneck = initialEnergy - txCost;
      bestBSState = { pred: source, prevH: 0, prevT: 0 };
    }
  }

  // Iterate over hop count h and time expansion t
  for (let h = 1; h <= H; h++) {
    for (const v of aliveArray) {
      const vNode = nodes.get(v)!;

      for (let t = h * hopDelay; t <= h * hopDelay + 2; t++) {
        let maxBottleneck = -1;
        let bestPred: { u: number; prevH: number; prevT: number } | null = null;

        // Try incoming neighbor u
        for (const u of aliveArray) {
          if (u === v) continue;
          const uNode = nodes.get(u)!;
          const dist = uNode.distanceTo(vNode);
          if (transmissionRange && dist > transmissionRange) continue;

          const prevT = t - hopDelay;
          const prevState = dp.get(key(u, h - 1, prevT));
          if (!prevState || prevState.bottleneck <= 0) continue;

          // Projected energy of relay node v at round arrival time (currentTime + t)
          let projectedV = vNode.residualEnergy;
          if (harvestingModel) {
            projectedV = harvestingModel.projectEnergy(
              v,
              vNode.residualEnergy,
              currentTime,
              currentTime + t,
              vNode.maxEnergy
            );
          }

          const txCost = energyModel.transmitEnergy(kBits, dist);
          const rxCost = energyModel.receiveEnergy(kBits);
          const availableRelay = projectedV - rxCost;

          if (availableRelay <= rxCost * 0.5 || prevState.bottleneck <= txCost) continue;

          const bottleneck = Math.min(prevState.bottleneck - txCost, availableRelay);
          if (bottleneck > maxBottleneck) {
            maxBottleneck = bottleneck;
            bestPred = { u, prevH: h - 1, prevT };
          }
        }

        if (bestPred && maxBottleneck > 0) {
          dp.set(key(v, h, t), {
            bottleneck: maxBottleneck,
            pred: bestPred.u,
            prevH: bestPred.prevH,
            prevT: bestPred.prevT
          });

          // Check if relay v can transmit to Base Station
          const distVtoBS = Math.sqrt(
            (vNode.x - baseStationPos[0]) ** 2 + (vNode.y - baseStationPos[1]) ** 2
          );
          if (!transmissionRange || distVtoBS <= transmissionRange) {
            const txToBS = energyModel.transmitEnergy(kBits, distVtoBS);
            if (maxBottleneck >= txToBS) {
              const finalBottleneck = maxBottleneck - txToBS;
              if (finalBottleneck > bestBSBottleneck) {
                bestBSBottleneck = finalBottleneck;
                bestBSState = { pred: v, prevH: h, prevT: t };
              }
            }
          }
        }
      }
    }
  }

  if (!bestBSState || bestBSBottleneck <= 0) {
    // Fallback to standard Dijkstra if DP finds no surviving path
    const fallback = dijkstra(nodes, null as any, source, baseStationPos, energyModel, aliveNodesSet, true, kBits, transmissionRange);
    return { bottleneckEnergy: 0.001, path: fallback.path };
  }

  // Reconstruct path
  const path: number[] = [-1];
  let currNode: number | null = bestBSState.pred;
  let currH = bestBSState.prevH;
  let currT = bestBSState.prevT;

  while (currNode !== null) {
    path.unshift(currNode);
    if (currNode === source) break;
    const state = dp.get(key(currNode, currH, currT));
    if (!state) break;
    currNode = state.pred;
    currH = state.prevH;
    currT = state.prevT;
  }

  return { bottleneckEnergy: bestBSBottleneck, path };
}

/**
 * Classical Maximin DP (Bottleneck Path without time augmentation)
 */
export function dpMaximinPath(
  nodes: Map<number, Node>,
  source: number,
  baseStationPos: [number, number],
  energyModel: EnergyModel,
  aliveNodesSet: Set<number>,
  maxHops: number = 5,
  kBits: number = 4000,
  transmissionRange?: number
): { bottleneckEnergy: number; path: number[] | null } {
  if (!aliveNodesSet.has(source)) {
    return { bottleneckEnergy: 0, path: null };
  }

  const aliveArray = Array.from(aliveNodesSet);
  const H = Math.max(1, Math.min(maxHops, aliveArray.length + 1));

  // dp[v][h]: max bottleneck energy to reach node v in h hops
  const dp: Map<string, { bottleneck: number; pred: number | null }> = new Map();
  const key = (v: number, h: number) => `${v}_${h}`;

  const sourceNode = nodes.get(source)!;
  dp.set(key(source, 0), { bottleneck: sourceNode.residualEnergy, pred: null });

  let bestBSBottleneck = 0;
  let bestBSState: { pred: number; prevH: number } | null = null;

  const distToBS = Math.sqrt(
    (sourceNode.x - baseStationPos[0]) ** 2 + (sourceNode.y - baseStationPos[1]) ** 2
  );
  if (!transmissionRange || distToBS <= transmissionRange) {
    const cost = energyModel.transmitEnergy(kBits, distToBS);
    if (sourceNode.residualEnergy >= cost) {
      bestBSBottleneck = sourceNode.residualEnergy - cost;
      bestBSState = { pred: source, prevH: 0 };
    }
  }

  for (let h = 1; h <= H; h++) {
    for (const v of aliveArray) {
      const vNode = nodes.get(v)!;
      let maxBottleneck = -1;
      let bestPred: number | null = null;

      for (const u of aliveArray) {
        if (u === v) continue;
        const uNode = nodes.get(u)!;
        const dist = uNode.distanceTo(vNode);
        if (transmissionRange && dist > transmissionRange) continue;

        const prevState = dp.get(key(u, h - 1));
        if (!prevState || prevState.bottleneck <= 0) continue;

        const txCost = energyModel.transmitEnergy(kBits, dist);
        const rxCost = energyModel.receiveEnergy(kBits);
        const availableRelay = vNode.residualEnergy - rxCost;

        if (availableRelay <= 0 || prevState.bottleneck < txCost) continue;

        const bottleneck = Math.min(prevState.bottleneck - txCost, availableRelay);
        if (bottleneck > maxBottleneck) {
          maxBottleneck = bottleneck;
          bestPred = u;
        }
      }

      if (bestPred !== null && maxBottleneck > 0) {
        dp.set(key(v, h), { bottleneck: maxBottleneck, pred: bestPred });

        const distVtoBS = Math.sqrt(
          (vNode.x - baseStationPos[0]) ** 2 + (vNode.y - baseStationPos[1]) ** 2
        );
        if (!transmissionRange || distVtoBS <= transmissionRange) {
          const txToBS = energyModel.transmitEnergy(kBits, distVtoBS);
          if (maxBottleneck >= txToBS) {
            const finalBottleneck = maxBottleneck - txToBS;
            if (finalBottleneck > bestBSBottleneck) {
              bestBSBottleneck = finalBottleneck;
              bestBSState = { pred: v, prevH: h };
            }
          }
        }
      }
    }
  }

  if (!bestBSState || bestBSBottleneck <= 0) {
    const fallback = dijkstra(nodes, null as any, source, baseStationPos, energyModel, aliveNodesSet, true, kBits, transmissionRange);
    return { bottleneckEnergy: 0.001, path: fallback.path };
  }

  const path: number[] = [-1];
  let currNode: number | null = bestBSState.pred;
  let currH = bestBSState.prevH;

  while (currNode !== null) {
    path.unshift(currNode);
    if (currNode === source) break;
    const state = dp.get(key(currNode, currH));
    if (!state) break;
    currNode = state.pred;
    currH--;
  }

  return { bottleneckEnergy: bestBSBottleneck, path };
}

/**
 * Disjoint-Set Union (DSU) Live Detour Rerouting:
 * When an intermediate relay node depletes battery mid-round, performs fast local detour recovery
 * finding an alternative relay from the predecessor node connected to the Base Station component.
 */
export function ripUpAndReroute(
  nodes: Map<number, Node>,
  failedNodeId: number,
  activePath: number[],
  baseStationPos: [number, number],
  energyModel: EnergyModel,
  aliveNodesSet: Set<number>,
  kBits: number = 4000,
  transmissionRange?: number
): { newPath: number[] | null; success: boolean } {
  // Find index of failed node in active path
  const failedIdx = activePath.indexOf(failedNodeId);
  if (failedIdx <= 0) {
    return { newPath: null, success: false };
  }

  const predecessorId = activePath[failedIdx - 1];
  const predNode = nodes.get(predecessorId);
  if (!predNode || !predNode.isAlive) {
    return { newPath: null, success: false };
  }

  // Construct Union-Find for alive nodes to test connectivity to BS
  const dsu = new UnionFind();
  for (const nid of aliveNodesSet) {
    if (nid !== failedNodeId) {
      dsu.add(nid);
    }
  }
  dsu.add(-1); // Base station

  // Connect BS to nearby nodes
  for (const nid of aliveNodesSet) {
    if (nid === failedNodeId) continue;
    const node = nodes.get(nid)!;
    const distToBS = Math.sqrt(
      (node.x - baseStationPos[0]) ** 2 + (node.y - baseStationPos[1]) ** 2
    );
    if (!transmissionRange || distToBS <= transmissionRange) {
      dsu.union(nid, -1);
    }
  }

  // Connect inter-node edges
  const aliveArray = Array.from(aliveNodesSet).filter(id => id !== failedNodeId);
  for (let i = 0; i < aliveArray.length; i++) {
    const u = aliveArray[i];
    const uNode = nodes.get(u)!;
    for (let j = i + 1; j < aliveArray.length; j++) {
      const v = aliveArray[j];
      const vNode = nodes.get(v)!;
      const dist = uNode.distanceTo(vNode);
      if (!transmissionRange || dist <= transmissionRange) {
        dsu.union(u, v);
      }
    }
  }

  // Option 1: Direct link from predecessor to Base Station
  const distPredToBS = Math.sqrt(
    (predNode.x - baseStationPos[0]) ** 2 + (predNode.y - baseStationPos[1]) ** 2
  );
  if (!transmissionRange || distPredToBS <= transmissionRange) {
    const txCost = energyModel.transmitEnergy(kBits, distPredToBS);
    if (predNode.residualEnergy >= txCost) {
      const prefix = activePath.slice(0, failedIdx);
      return { newPath: [...prefix, -1], success: true };
    }
  }

  // Option 2: Find best alternative alive neighbor relay of predecessor connected to BS
  let bestRelay: number | null = null;
  let maxResidualEnergy = -1;

  for (const nbrId of aliveArray) {
    if (nbrId === predecessorId) continue;
    if (!dsu.connected(nbrId, -1)) continue; // Must have path to Base Station

    const nbrNode = nodes.get(nbrId)!;
    const dist = predNode.distanceTo(nbrNode);
    if (transmissionRange && dist > transmissionRange) continue;

    const txCost = energyModel.transmitEnergy(kBits, dist);
    if (predNode.residualEnergy >= txCost && nbrNode.residualEnergy > maxResidualEnergy) {
      maxResidualEnergy = nbrNode.residualEnergy;
      bestRelay = nbrId;
    }
  }

  if (bestRelay !== null) {
    // Sub-route from bestRelay to BS
    const remainingSubRoute = dijkstra(
      nodes,
      null as any,
      bestRelay,
      baseStationPos,
      energyModel,
      new Set(aliveArray),
      true,
      kBits,
      transmissionRange
    );

    if (remainingSubRoute.path && remainingSubRoute.path.length >= 2) {
      const prefix = activePath.slice(0, failedIdx);
      return { newPath: [...prefix, ...remainingSubRoute.path], success: true };
    }
  }

  return { newPath: null, success: false };
}
