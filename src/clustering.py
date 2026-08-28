"""
Clustering module for WSN simulation.

Implements LEACH-style clustering with energy-weighted cluster head selection,
with support for projected energy harvesting when forming clusters.
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
    Elects cluster heads for the current round and assigns member nodes
    to the nearest cluster head.
    
    If a harvesting model is provided, election probabilities are weighted
    by the projected energy over the upcoming round.
    """
    alive_nodes = {nid: node for nid, node in nodes.items() if node.is_alive}
    if not alive_nodes:
        return {}, []

    num_alive = len(alive_nodes)
    desired_num_ch = max(1, int(num_alive * desired_clusters_ratio))

    # Reset roles for this round
    for node in alive_nodes.values():
        node.role = 'member'
        node.cluster_id = -1

    # 1. Compute effective energy (projected harvest or current battery)
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

    # 2. Probability weighted by effective energy
    node_probabilities = {}
    for nid, eff_e in effective_energies.items():
        prob = (desired_num_ch * eff_e * threshold_multiplier) / total_effective_energy
        node_probabilities[nid] = min(prob, 1.0)

    # 3. Candidate selection with min-heap tiebreaker
    candidates = []
    for nid, prob in node_probabilities.items():
        rand_val = random.random()
        if rand_val < prob:
            heapq.heappush(candidates, (rand_val, -effective_energies[nid], nid))

    # 4. Pick up to desired number of cluster heads
    selected_ch = []
    while candidates and len(selected_ch) < desired_num_ch:
        _, _, nid = heapq.heappop(candidates)
        selected_ch.append(nid)
        alive_nodes[nid].role = 'CH'

    # Fallback if fewer candidates were elected
    if len(selected_ch) < desired_num_ch:
        remaining = [
            (effective_energies[nid], nid)
            for nid, node in alive_nodes.items()
            if node.role == 'member'
        ]
        remaining.sort(reverse=True)
        for _, nid in remaining:
            if len(selected_ch) >= desired_num_ch:
                break
            selected_ch.append(nid)
            alive_nodes[nid].role = 'CH'

    # 5. Assign member nodes to closest CH
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
    """Runs a single round of clustering and returns cluster stats."""
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