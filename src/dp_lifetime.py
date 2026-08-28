"""
Dynamic Programming algorithms for finding bottleneck-energy paths in WSNs.

Includes:
1. Classical Maximin DP: finds a hop-constrained path maximizing bottleneck energy.
2. Time-Augmented DP: adds a time dimension to account for energy harvesting
   recharge during packet travel.
"""

from typing import Dict, List, Tuple, Optional, Set
from network import Node, Graph
from energy_model import EnergyModel
try:
    from harvesting_model import HarvestingProfile
except ImportError:
    HarvestingProfile = None


def dp_lifetime_maximin_path(
    nodes: Dict[int, Node],
    adj_list: Dict[int, List[Tuple[int, float]]],
    source: int,
    base_station_pos: Tuple[float, float],
    energy_model: EnergyModel,
    alive_nodes: Set[int],
    max_hops: Optional[int] = None,
    k_bits: int = 1,
    transmission_range: Optional[float] = None
) -> Tuple[float, List[int]]:
    """
    Finds a path from source to base station (-1) that maximizes the bottleneck
    (minimum residual energy) along the route, with a hop limit.
    """
    if source not in alive_nodes:
        return 0.0, []

    if max_hops is None:
        max_hops = max(0, len(alive_nodes) - 1)
    elif max_hops < 0:
        max_hops = 0

    # dp[v][h]: max bottleneck energy to reach node v in h hops
    # pred[v][h]: previous node along the path
    dp: Dict[int, Dict[int, float]] = {}
    pred: Dict[int, Dict[int, Optional[int]]] = {}

    dp[source] = {0: nodes[source].residual_energy}
    pred[source] = {0: None}

    for h in range(1, max_hops + 1):
        for u in list(dp.keys()):
            if (h - 1) not in dp[u]:
                continue
            bottleneck_u = dp[u][h - 1]

            # Try routing to active sensor neighbors
            if u in adj_list:
                for v, _ in adj_list[u]:
                    if v not in alive_nodes:
                        continue
                    candidate = min(bottleneck_u, nodes[v].residual_energy)
                    if v not in dp:
                        dp[v] = {}
                        pred[v] = {}
                    if h not in dp[v] or candidate > dp[v][h]:
                        dp[v][h] = candidate
                        pred[v][h] = u

            # Check direct reachability to base station (-1)
            if u in alive_nodes:
                can_reach_bs = True
                if transmission_range is not None:
                    u_node = nodes[u]
                    dist_to_bs = ((u_node.x - base_station_pos[0])**2 + (u_node.y - base_station_pos[1])**2)**0.5
                    if dist_to_bs > transmission_range:
                        can_reach_bs = False

                if can_reach_bs:
                    v = -1
                    candidate = bottleneck_u  # base station has unlimited energy
                    if v not in dp:
                        dp[v] = {}
                        pred[v] = {}
                    if h not in dp[v] or candidate > dp[v][h]:
                        dp[v][h] = candidate
                        pred[v][h] = u

    # Look for the best bottleneck arriving at the base station
    best_lifetime = 0.0
    best_hops = -1
    if -1 in dp:
        for h, val in dp[-1].items():
            if val > best_lifetime:
                best_lifetime = val
                best_hops = h

    if best_lifetime <= 0.0 or best_hops == -1:
        return 0.0, []

    # Backtrack to reconstruct the route
    path: List[int] = []
    curr: Optional[int] = -1
    hops = best_hops
    while curr is not None and hops >= 0:
        path.append(curr)
        curr = pred.get(curr, {}).get(hops)
        hops -= 1
    path.reverse()

    if not path or path[0] != source:
        return 0.0, []

    return best_lifetime, path


def dp_time_augmented_lifetime(
    nodes: Dict[int, Node],
    adj_list: Dict[int, List[Tuple[int, float]]],
    source: int,
    base_station_pos: Tuple[float, float],
    energy_model: EnergyModel,
    alive_nodes: Set[int],
    harvesting_model: Optional[HarvestingProfile] = None,
    current_time: int = 0,
    max_hops: Optional[int] = None,
    time_horizon: Optional[int] = None,
    hop_delay: int = 1,
    k_bits: int = 1,
    transmission_range: Optional[float] = None
) -> Tuple[float, List[int], List[int]]:
    """
    Time-augmented DP routing that factors in projected ambient energy harvesting.
    
    Instead of assuming static residual energy, this projects what a node's battery
    will be when the packet actually reaches it at future time offset t.
    """
    if source not in alive_nodes:
        return 0.0, [], []

    num_alive = len(alive_nodes)
    if max_hops is None:
        max_hops = min(10, max(1, num_alive - 1))
    if max_hops < 1:
        return 0.0, [], []

    hop_delay = max(1, hop_delay)
    if time_horizon is None:
        time_horizon = max_hops * hop_delay
    time_horizon = max(hop_delay, time_horizon)

    def get_projected_energy(nid: int, time_offset: int) -> float:
        if nid == -1:
            return float('inf')
        node = nodes.get(nid)
        if node is None or not node.is_alive:
            return 0.0
        if harvesting_model is None:
            return node.residual_energy
        return harvesting_model.project_energy(
            node_id=nid,
            current_energy=node.residual_energy,
            current_time=current_time,
            target_time=current_time + time_offset,
            battery_capacity=node.max_energy
        )

    # 3D tables:
    # dp[node][hop][time_offset] = best bottleneck value
    # pred[node][hop][time_offset] = (prev_node, prev_time_offset)
    dp: Dict[int, Dict[int, Dict[int, float]]] = {}
    pred: Dict[int, Dict[int, Dict[int, Tuple[Optional[int], Optional[int]]]]] = {}
    reached_at: Dict[Tuple[int, int], List[int]] = {}

    def update_dp(nid: int, h: int, t: int, val: float, p_node: Optional[int], p_t: Optional[int]):
        if nid not in dp:
            dp[nid] = {}
            pred[nid] = {}
        if h not in dp[nid]:
            dp[nid][h] = {}
            pred[nid][h] = {}
        if t not in dp[nid][h] or val > dp[nid][h][t]:
            if t not in dp[nid][h]:
                reached_at.setdefault((h, t), []).append(nid)
            dp[nid][h][t] = val
            pred[nid][h][t] = (p_node, p_t)

    # Base case: packet starts at source at hop 0 and time offset 0
    source_energy = get_projected_energy(source, 0)
    update_dp(source, 0, 0, source_energy, None, None)

    # Propagate through hop and time dimensions
    for h in range(1, max_hops + 1):
        for t in range(h * hop_delay, time_horizon + 1):
            prev_t = t - hop_delay
            candidates = reached_at.get((h - 1, prev_t), [])
            if not candidates:
                continue

            for u in candidates:
                bottleneck_u = dp[u][h - 1][prev_t]
                if bottleneck_u <= 0.0:
                    continue

                # Forward to neighboring sensor nodes
                if u in adj_list:
                    for v, _ in adj_list[u]:
                        if v not in alive_nodes or v == source:
                            continue
                        if transmission_range is not None:
                            dist_uv = ((nodes[u].x - nodes[v].x)**2 + (nodes[u].y - nodes[v].y)**2)**0.5
                            if dist_uv > transmission_range:
                                continue
                        e_proj_v = get_projected_energy(v, t)
                        if e_proj_v <= 0.0:
                            continue
                        candidate_val = min(bottleneck_u, e_proj_v)
                        update_dp(v, h, t, candidate_val, u, prev_t)

                # Forward directly to base station (-1)
                if u in alive_nodes:
                    can_reach_bs = True
                    if transmission_range is not None:
                        dist_to_bs = ((nodes[u].x - base_station_pos[0])**2 + (nodes[u].y - base_station_pos[1])**2)**0.5
                        if dist_to_bs > transmission_range:
                            can_reach_bs = False
                    if can_reach_bs:
                        v = -1
                        candidate_val = bottleneck_u  # base station has no energy constraint
                        update_dp(v, h, t, candidate_val, u, prev_t)

    # Find the best route ending at the base station
    best_lifetime = 0.0
    best_h = -1
    best_t = -1

    if -1 in dp:
        for h, t_map in dp[-1].items():
            for t, val in t_map.items():
                if val > best_lifetime:
                    best_lifetime = val
                    best_h = h
                    best_t = t
                elif abs(val - best_lifetime) < 1e-9 and best_lifetime > 0.0:
                    # Prefer fewer hops and earlier arrival on tie
                    if h < best_h or (h == best_h and t < best_t):
                        best_h = h
                        best_t = t

    if best_lifetime <= 0.0 or best_h == -1:
        return 0.0, [], []

    # Backtrack path and schedule
    path: List[int] = []
    schedule: List[int] = []

    curr_node: Optional[int] = -1
    curr_h = best_h
    curr_t: Optional[int] = best_t

    while curr_node is not None and curr_h >= 0 and curr_t is not None:
        path.append(curr_node)
        schedule.append(curr_t)
        prev_info = pred.get(curr_node, {}).get(curr_h, {}).get(curr_t)
        if prev_info is None:
            break
        curr_node, curr_t = prev_info
        curr_h -= 1

    path.reverse()
    schedule.reverse()

    if not path or path[0] != source or path[-1] != -1:
        return 0.0, [], []

    return best_lifetime, path, schedule


def dp_lifetime_limited_hops(
    nodes: Dict[int, Node],
    adj_list: Dict[int, List[Tuple[int, float]]],
    source: int,
    base_station_pos: Tuple[float, float],
    energy_model: EnergyModel,
    alive_nodes: Set[int],
    max_hops: int,
    k_bits: int = 1
) -> Tuple[float, List[int]]:
    """Helper wrapper for classical DP with fixed hop limit."""
    return dp_lifetime_maximin_path(
        nodes, adj_list, source, base_station_pos, energy_model, alive_nodes, max_hops, k_bits
    )