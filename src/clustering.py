"""
Clustering module for WSN simulation.
Implements LEACH-style clustering with energy-aware and harvesting-aware head selection.
"""

import heapq
import math
import random
from typing import Dict, List, Tuple, Optional
from network import Node, Graph
from energy_model import EnergyModel
try:
    from harvesting_model import HarvestingProfile
except ImportError:
    HarvestingProfile = None


def leach_clustering(
    nodes: Dict[int, Node],
    energy_model: EnergyModel,
    desired_clusters_ratio: float = 0.05,
    threshold_multiplier: float = 1.0,
    harvesting_model: Optional[HarvestingProfile] = None,
    current_time: int = 0,
    lookahead_rounds: int = 1
) -> Tuple[Dict[int, int], List[int]]:
    """
    Perform LEACH-style clustering for one round with optional energy-harvesting awareness.

    Harvesting-Aware Rotation Rule:
    -------------------------------
    Standard LEACH computes CH probability based on static instantaneous residual energy E_i.
    In energy-harvesting networks, a node currently depleted may receive substantial recharge
    during its cluster-head tenure, whereas a high-energy node in shade will only drain.
    We compute projected effective energy:
        E_eff[i] = project_energy(node_i, E_curr[i], current_time, current_time + lookahead_rounds)
    Probability for node i:
        P_i = min(1.0, (desired_num_ch * E_eff[i]) / sum(E_eff))

    Min-heap tiebreaker ranks candidates by (-E_eff[i], rand_val), selecting nodes
    with highest projected energy stability.

    Args:
        nodes: Dictionary of node_id -> Node object (only alive nodes considered)
        energy_model: EnergyModel instance
        desired_clusters_ratio: Desired fraction of nodes to become cluster heads (default 0.05 = 5%)
        threshold_multiplier: Multiplier for threshold adjustment
        harvesting_model: HarvestingProfile instance (if provided, uses projected energy)
        current_time: Current simulation round
        lookahead_rounds: Number of rounds to project energy forward (default 1)

    Returns:
        cluster_assignment: dict mapping node_id -> cluster_head_id
        cluster_heads: list of node IDs that are cluster heads
    """
    # Get alive nodes
    alive_nodes = {nid: node for nid, node in nodes.items() if node.is_alive}
    if not alive_nodes:
        return {}, []

    num_alive = len(alive_nodes)
    desired_num_ch = max(1, int(num_alive * desired_clusters_ratio))

    # Reset roles and cluster IDs for alive nodes
    for node in alive_nodes.values():
        node.role = 'member'
        node.cluster_id = -1

    # Step 1: Compute effective energy (projected harvest or current residual)
    effective_energies: Dict[int, float] = {}
    for nid, node in alive_nodes.items():
        if harvesting_model is not None:
            eff_e = harvesting_model.project_energy(
                node_id=nid,
                current_energy=node.residual_energy,
                current_time=current_time,
                target_time=current_time + lookahead_rounds,
                battery_capacity=node.max_energy
            )
        else:
            eff_e = node.residual_energy
        effective_energies[nid] = max(0.0, eff_e)

    total_effective_energy = sum(effective_energies.values())
    if total_effective_energy <= 0.0:
        return {}, []

    # Step 2: Probability weighted by effective/projected energy
    node_probabilities = {}
    for nid, eff_e in effective_energies.items():
        prob = (desired_num_ch * eff_e * threshold_multiplier) / total_effective_energy
        node_probabilities[nid] = min(prob, 1.0)

    # Step 3: Candidate selection via min-heap prioritizing higher projected energy
    candidates = []
    for nid, prob in node_probabilities.items():
        rand_val = random.random()
        if rand_val < prob:
            # Min-heap key: (random_val, -effective_energy, node_id)
            heapq.heappush(candidates, (rand_val, -effective_energies[nid], nid))

    # Step 4: Select up to desired_num_ch cluster heads
    selected_ch = []
    while candidates and len(selected_ch) < desired_num_ch:
        _, _, nid = heapq.heappop(candidates)
        selected_ch.append(nid)
        alive_nodes[nid].role = 'CH'

    # If fewer candidates than desired, fill from remaining alive nodes sorted by effective energy
    if len(selected_ch) < desired_num_ch:
        remaining = [(effective_energies[nid], nid) for nid, node in alive_nodes.items()
                     if node.role == 'member']
        remaining.sort(reverse=True)
        for energy, nid in remaining:
            if len(selected_ch) >= desired_num_ch:
                break
            selected_ch.append(nid)
            alive_nodes[nid].role = 'CH'

    # Step 5: Assign each member node to nearest cluster head
    cluster_assignment = {}
    for nid, node in alive_nodes.items():
        if node.role == 'CH':
            cluster_assignment[nid] = nid
            node.cluster_id = nid
        else:
            min_dist = float('inf')
            nearest_ch = -1
            for ch_id in selected_ch:
                ch_node = alive_nodes[ch_id]
                dist = node.distance_to(ch_node)
                if dist < min_dist:
                    min_dist = dist
                    nearest_ch = ch_id
            cluster_assignment[nid] = nearest_ch
            node.cluster_id = nearest_ch

    return cluster_assignment, selected_ch


def simulate_clustering_round(
    nodes: Dict[int, Node],
    energy_model: EnergyModel,
    desired_clusters_ratio: float = 0.05,
    harvesting_model: Optional[HarvestingProfile] = None,
    current_time: int = 0,
    lookahead_rounds: int = 1
) -> Tuple[Dict[int, int], List[int], Dict[int, float]]:
    """
    Simulate one round of clustering and return additional info for debugging.
    """
    alive_count = sum(1 for node in nodes.values() if node.is_alive)
    if alive_count == 0:
        return {}, [], {"alive_nodes": 0}

    assignment, heads = leach_clustering(
        nodes=nodes,
        energy_model=energy_model,
        desired_clusters_ratio=desired_clusters_ratio,
        harvesting_model=harvesting_model,
        current_time=current_time,
        lookahead_rounds=lookahead_rounds
    )

    debug_info = {
        "alive_nodes": alive_count,
        "num_cluster_heads": len(heads),
        "desired_num_heads": max(1, int(alive_count * desired_clusters_ratio)),
        "cluster_heads": heads.copy()
    }

    return assignment, heads, debug_info