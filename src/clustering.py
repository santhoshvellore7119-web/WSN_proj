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
    lookahead_rounds: int = 1,
    rng: Optional[random.Random] = None
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
    _draw = rng.random if rng is not None else random.random
    candidates = []
    for nid, prob in node_probabilities.items():
        rand_val = _draw()
        if rand_val < prob:
            heapq.heappush(candidates, (-effective_energies[nid], rand_val, nid))

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
    lookahead_rounds: int = 1,
    rng: Optional[random.Random] = None
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
        lookahead_rounds=lookahead_rounds,
        rng=rng
    )

    debug_info = {
        "alive_nodes": alive_count,
        "num_cluster_heads": len(heads),
        "desired_num_heads": max(1, int(alive_count * desired_clusters_ratio)),
    }
    return assignment, heads, debug_info


def eh_leach_clustering(
    nodes: Dict[int, Node],
    energy_model: EnergyModel,
    desired_clusters_ratio: float = 0.05,
    harvesting_model: Optional[HarvestingProfile] = None,
    current_time: int = 0,
    round_num: int = 0,
    solar_beta: float = 0.5,
    rng: Optional[random.Random] = None
) -> Tuple[Dict[int, int], List[int]]:
    """
    EH-LEACH (Energy-Harvesting LEACH baseline from literature).
    
    Weights election threshold using both current residual battery and
    projected solar energy relative to average network energy:
    T(n) = [p / (1 - p * (r mod (1/p)))] * [(E_i + beta * E_harvest) / (E_avg + beta * E_avg_harvest)]
    """
    _rng = rng if rng is not None else random
    alive_nodes = {nid: node for nid, node in nodes.items() if node.is_alive}
    if not alive_nodes:
        return {}, []

    num_alive = len(alive_nodes)
    p = desired_clusters_ratio
    desired_num_ch = max(1, int(num_alive * p))

    # Reset roles
    for node in alive_nodes.values():
        node.role = 'member'
        node.cluster_id = -1

    # Base LEACH probability factor
    cycle = max(1, int(1.0 / p)) if p > 0 else 20
    r_mod = round_num % cycle
    denom = 1.0 - p * r_mod
    base_p = p / max(0.01, denom)

    # Estimate individual and average energy + harvest
    total_energy = sum(node.residual_energy for node in alive_nodes.values())
    avg_energy = total_energy / num_alive if num_alive > 0 else 1.0

    harvest_estimates = {}
    for nid, node in alive_nodes.items():
        if harvesting_model is not None:
            h_est = harvesting_model.expected_harvest(nid, current_time, current_time + 1)
        else:
            h_est = 0.0
        harvest_estimates[nid] = max(0.0, h_est)

    avg_harvest = sum(harvest_estimates.values()) / num_alive if num_alive > 0 else 0.0
    avg_composite = max(1e-6, avg_energy + solar_beta * avg_harvest)

    # Calculate threshold for each node
    selected_ch = []
    candidates = []
    for nid, node in alive_nodes.items():
        composite_energy = node.residual_energy + solar_beta * harvest_estimates[nid]
        threshold = base_p * (composite_energy / avg_composite)
        threshold = min(1.0, max(0.0, threshold))
        rand_val = _rng.random()
        if rand_val < threshold:
            candidates.append((composite_energy, nid))

    # Sort candidates by composite energy and pick cluster heads
    candidates.sort(reverse=True)
    for _, nid in candidates[:desired_num_ch]:
        selected_ch.append(nid)
        alive_nodes[nid].role = 'CH'

    # Fallback if none elected
    if not selected_ch:
        best_nid = max(alive_nodes.keys(), key=lambda i: alive_nodes[i].residual_energy + solar_beta * harvest_estimates[i])
        selected_ch.append(best_nid)
        alive_nodes[best_nid].role = 'CH'

    # Assign members to nearest CH
    cluster_assignment = {}
    for nid, node in alive_nodes.items():
        if node.role == 'CH':
            cluster_assignment[nid] = nid
            node.cluster_id = nid
        else:
            min_dist = float('inf')
            nearest_ch = selected_ch[0]
            for ch_id in selected_ch:
                dist = node.distance_to(alive_nodes[ch_id])
                if dist < min_dist:
                    min_dist = dist
                    nearest_ch = ch_id
            cluster_assignment[nid] = nearest_ch
            node.cluster_id = nearest_ch

    return cluster_assignment, selected_ch