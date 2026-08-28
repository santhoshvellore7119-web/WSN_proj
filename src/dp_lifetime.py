"""
Dynamic Programming module for WSN simulation.

Implements:
1. Classical Maximin Path DP (spatial hop-constrained bottleneck maximization):
   dp[v][h] = max_{u in nbr(v)} min(dp[u][h-1], residual_energy[v])
   Complexity: Time O(|E| * H), Space O(V * H)

2. Novel Time-Augmented Maximin DP (spacetime energy-harvesting-aware path optimization):
   dp[v][h][t] = max_{u in nbr(v)} min(dp[u][h-1][t - delta], E_proj(v, t_curr + t))
   Complexity: Time O(|E| * H * T), Space O(V * H * T)

The time-augmented DP enables routing packets through nodes that are currently depleted
but will harvest sufficient energy before packet arrival.
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
    Classical Maximin DP for finding a hop-constrained path from source to base station
    that maximizes the minimum residual energy along the path.

    State:
        dp[v][h] = maximum bottleneck value (minimum residual energy) achievable
                   from source to node v using exactly h hops.

    Recurrence:
        dp[source][0] = residual_energy[source]
        For h from 1 to max_hops:
            dp[v][h] = max over all neighbors u of v of { min(dp[u][h-1], residual_energy[v]) }
        For base station (-1), residual energy is infinity.

    Complexity:
        Time Complexity:  O(|E| * H) <= O(V^2 * H)
        Space Complexity: O(V * H)

    Args:
        nodes: dictionary of node_id -> Node object
        adj_list: adjacency list (node_id -> list of (neighbor_id, weight))
        source: starting cluster-head node ID
        base_station_pos: (x, y) coordinates of base station
        energy_model: EnergyModel instance
        alive_nodes: set of node IDs that are alive
        max_hops: maximum number of hops allowed
        k_bits: number of bits transmitted

    Returns:
        lifetime: the maximum bottleneck residual energy along the path
        path: list of node IDs from source to base station (including -1)
    """
    if source not in alive_nodes:
        return 0.0, []

    if max_hops is None:
        max_hops = len(alive_nodes) - 1
    if max_hops < 0:
        max_hops = 0

    dp: Dict[int, Dict[int, float]] = {}
    pred: Dict[int, Dict[int, Optional[int]]] = {}

    dp[source] = {0: nodes[source].residual_energy}
    pred[source] = {0: None}

    for h in range(1, max_hops + 1):
        for u in list(dp.keys()):
            if (h - 1) not in dp[u]:
                continue
            bottleneck_u = dp[u][h - 1]

            # Sensor node neighbors
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

            # Edge to base station (-1)
            if u in alive_nodes:
                can_reach_bs = True
                if transmission_range is not None:
                    u_node = nodes[u]
                    dist_to_bs = ((u_node.x - base_station_pos[0])**2 + (u_node.y - base_station_pos[1])**2)**0.5
                    if dist_to_bs > transmission_range:
                        can_reach_bs = False
                if can_reach_bs:
                    v = -1
                    candidate = bottleneck_u
                    if v not in dp:
                        dp[v] = {}
                        pred[v] = {}
                    if h not in dp[v] or candidate > dp[v][h]:
                        dp[v][h] = candidate
                        pred[v][h] = u

    best_lifetime = 0.0
    best_hops = -1
    if -1 in dp:
        for h, value in dp[-1].items():
            if value > best_lifetime:
                best_lifetime = value
                best_hops = h

    if best_lifetime <= 0.0:
        return 0.0, []

    path: List[int] = []
    cur: Optional[int] = -1
    hops = best_hops
    while cur is not None and hops >= 0:
        path.append(cur)
        cur = pred.get(cur, {}).get(hops)
        hops -= 1
    path.reverse()

    if len(path) == 0 or path[0] != source:
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
    Novel Time-Augmented Dynamic Programming Algorithm for Energy-Harvesting-Aware WSN Routing.

    Theoretical Formulation:
    -------------------------
    In energy harvesting sensor networks, node residual energy is dynamic and increases
    over time due to ambient replenishment (solar, RF, thermal). A node that currently
    has low energy at round t_0 may become fully viable at round t_0 + delta.
    Classical DP fails by rejecting such nodes prematurely.

    We augment the state space with a discrete future time-window dimension t in [0, T].

    State:
        dp[v][h][t] = Maximum bottleneck energy along any valid path from source s to node v
                      using exactly h hops, where node v is reached at time offset t.

    Energy Projection Function:
        E_proj(v, t_curr + t) = min(E_max[v], E_curr[v] + E_harvest(v, t_curr -> t_curr + t))
        For the Base Station (v = -1): E_proj(-1, *) = infinity.

    Base Case (h = 0, t = 0):
        dp[source][0][0] = E_proj(source, current_time) = nodes[source].residual_energy
        pred[source][0][0] = (None, None)

    Recurrence Relation (for h = 1..H, t = delta..T):
        For each directed edge (u -> v) in G:
            candidate = min( dp[u][h-1][t - delta],  E_proj(v, current_time + t) )
            dp[v][h][t] = max( dp[v][h][t], candidate )

    Objective Function:
        Bottleneck* = max_{1 <= h <= H, 1 <= t <= T} dp[-1][h][t]

    Complexity Analysis:
    --------------------
    - State Space Size: |V| * (H + 1) * (T + 1) states
    - Per State Transitions: sum_{v} deg(v) = 2|E| edges per (h, t) slice
    - Total Time Complexity:  O(|E| * H * T) <= O(V^2 * H * T) for dense graphs
    - Total Space Complexity: O(V * H * T) for DP and backpointer tables
    - Compared to original O(|E| * H), this introduces an exact factor of T (time horizon),
      providing optimal spacetime route planning with polynomial overhead.

    Args:
        nodes: dictionary mapping node_id -> Node object
        adj_list: adjacency list of the sensor network
        source: starting cluster-head node ID
        base_station_pos: (x, y) coordinates of base station
        energy_model: EnergyModel instance
        alive_nodes: set of active/alive node IDs
        harvesting_model: HarvestingProfile instance (if None, assumes static energy)
        current_time: current simulation round/time
        max_hops: maximum number of hops allowed (H)
        time_horizon: maximum future time offset to consider (T, default H * hop_delay)
        hop_delay: time offset cost per hop traversed (delta >= 1)
        k_bits: packet bit size

    Returns:
        lifetime: optimal bottleneck energy achieved along the path
        path: sequence of node IDs [source, ..., -1]
        schedule: arrival time offsets [0, t_1, t_2, ..., t_BS]
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

    # 3D DP table: dp[node_id][hop][time_offset] = bottleneck_value
    # 3D Pred table: pred[node_id][hop][time_offset] = (prev_node_id, prev_time_offset)
    dp: Dict[int, Dict[int, Dict[int, float]]] = {}
    pred: Dict[int, Dict[int, Dict[int, Tuple[Optional[int], Optional[int]]]]] = {}
    reached_at: Dict[Tuple[int, int], List[int]] = {}

    def set_dp(nid: int, h: int, t: int, val: float, p_node: Optional[int], p_t: Optional[int]):
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

    # Base case: source at h = 0, t = 0
    source_init_energy = get_projected_energy(source, 0)
    set_dp(source, 0, 0, source_init_energy, None, None)

    # Main DP iterations over hops h and time offsets t
    for h in range(1, max_hops + 1):
        for t in range(h * hop_delay, time_horizon + 1):
            prev_t = t - hop_delay
            candidates_u = reached_at.get((h - 1, prev_t), [])
            if not candidates_u:
                continue

            for u in candidates_u:
                bottleneck_u = dp[u][h - 1][prev_t]
                if bottleneck_u <= 0.0:
                    continue

                # Transitions to sensor neighbors v
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
                        candidate = min(bottleneck_u, e_proj_v)
                        set_dp(v, h, t, candidate, u, prev_t)

                # Transitions to Base Station (virtual node -1)
                if u in alive_nodes:
                    can_reach_bs = True
                    if transmission_range is not None:
                        dist_to_bs = ((nodes[u].x - base_station_pos[0])**2 + (nodes[u].y - base_station_pos[1])**2)**0.5
                        if dist_to_bs > transmission_range:
                            can_reach_bs = False
                    if can_reach_bs:
                        v = -1
                        candidate = bottleneck_u  # Base Station has infinite capacity
                        set_dp(v, h, t, candidate, u, prev_t)

    # Find the maximum bottleneck across all (h, t) reaching Base Station (-1)
    best_lifetime = 0.0
    best_h = -1
    best_t = -1

    if -1 in dp:
        for h, t_dict in dp[-1].items():
            for t, val in t_dict.items():
                if val > best_lifetime:
                    best_lifetime = val
                    best_h = h
                    best_t = t
                elif abs(val - best_lifetime) < 1e-9 and best_lifetime > 0.0:
                    # Tie-breaker: prefer fewer hops or earlier arrival
                    if h < best_h or (h == best_h and t < best_t):
                        best_h = h
                        best_t = t

    if best_lifetime <= 0.0 or best_h == -1:
        return 0.0, [], []

    # Backtrack to reconstruct path and schedule
    path: List[int] = []
    schedule: List[int] = []

    curr_node: Optional[int] = -1
    curr_h = best_h
    curr_t: Optional[int] = best_t

    while curr_node is not None and curr_h >= 0 and curr_t is not None:
        path.append(curr_node)
        schedule.append(curr_t)
        p_info = pred.get(curr_node, {}).get(curr_h, {}).get(curr_t)
        if p_info is None:
            break
        curr_node, curr_t = p_info
        curr_h -= 1

    path.reverse()
    schedule.reverse()

    if len(path) == 0 or path[0] != source or path[-1] != -1:
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
    """Wrapper that calls classical dp_lifetime_maximin_path with given max_hops."""
    return dp_lifetime_maximin_path(nodes, adj_list, source, base_station_pos, energy_model, alive_nodes, max_hops, k_bits)