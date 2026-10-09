"""
Dynamic Programming algorithms for finding bottleneck-energy paths in WSNs.

Includes:
1. Classical Maximin DP: finds a hop-constrained path maximizing bottleneck energy.
2. Time-Augmented DP: adds a time dimension to account for energy harvesting
   recharge during packet travel.
"""

import math
from typing import Dict, List, Tuple, Optional, Set
from network import Node, Graph
from energy_model import EnergyModel
from energy_view import EnergyView, OracleView
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
    transmission_range: Optional[float] = None,
    energy_view: Optional[EnergyView] = None
) -> Tuple[float, List[int]]:
    """
    Finds a path from source to base station (-1) that maximizes the bottleneck
    (minimum residual energy) along the route, with a hop limit.
    """
    if source not in alive_nodes:
        return 0.0, []

    if energy_view is None:
        energy_view = OracleView(nodes)

    if max_hops is None:
        max_hops = max(0, len(alive_nodes) - 1)
    elif max_hops < 0:
        max_hops = 0

    # dp[v][h]: max bottleneck energy to reach node v in h hops
    # pred[v][h]: previous node along the path
    dp: Dict[int, Dict[int, float]] = {}
    pred: Dict[int, Dict[int, Optional[int]]] = {}

    dp[source] = {0: energy_view.mean(source)}
    pred[source] = {0: None}

    for h in range(1, max_hops + 1):
        for u in list(dp.keys()):
            if (h - 1) not in dp[u]:
                continue
            bottleneck_u = dp[u][h - 1]

            # Try routing to active sensor neighbors
            if u in adj_list:
                for v, _ in adj_list[u]:
                    if v not in alive_nodes or v == source:
                        continue
                    if transmission_range is not None:
                        dist_uv = nodes[u].distance_to(nodes[v])
                        if dist_uv > transmission_range:
                            continue
                    candidate = min(bottleneck_u, energy_view.mean(v))
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
    transmission_range: Optional[float] = None,
    energy_view: Optional[EnergyView] = None
) -> Tuple[float, List[int], List[int]]:
    """
    Time-augmented DP routing that factors in projected ambient energy harvesting.

    Instead of assuming static residual energy, this projects what a node's battery
    will be when the packet actually reaches it at future time offset t.

    Cost-Aware Tie-Breaking:
        Raw bottleneck-maximization alone is agnostic to how much physical
        transmission energy a path actually spends (distance-squared/quartic
        in the radio model). Two paths can have the same bottleneck value
        while one is far more expensive in aggregate. To avoid the DP
        drifting into needlessly long detours whenever several neighbors
        offer similar projected energy, each state additionally tracks the
        cumulative transmission+reception cost of the best path reaching it.
        When two candidate paths reach the same (v, h, t) with bottleneck
        values within a small relative tolerance, the lower-cost path wins.
        This keeps the primary objective (bottleneck survivability) intact
        while preventing the algorithm from being strictly worse than
        distance-minimizing routing (Dijkstra) whenever harvesting makes
        several nodes look equally safe.
    """
    if source not in alive_nodes:
        return 0.0, [], []

    if energy_view is None:
        energy_view = OracleView(nodes)

    num_alive = len(alive_nodes)
    if max_hops is None:
        max_hops = min(10, max(1, num_alive - 1))
    if max_hops < 1:
        return 0.0, [], []

    hop_delay = max(1, hop_delay)
    if time_horizon is None:
        time_horizon = max_hops * hop_delay
    time_horizon = max(hop_delay, time_horizon)

    # Memoization cache for projected energy to avoid redundant trigonometric/harvest calculations
    proj_cache: Dict[Tuple[int, int], float] = {}

    def get_projected_energy(nid: int, time_offset: int) -> float:
        if nid == -1:
            return float('inf')
        cache_key = (nid, time_offset)
        if cache_key in proj_cache:
            return proj_cache[cache_key]
        node = nodes.get(nid)
        if node is None or not node.is_alive:
            proj_cache[cache_key] = 0.0
            return 0.0
        curr_e = energy_view.mean(nid)
        if harvesting_model is None:
            val = curr_e
        else:
            val = harvesting_model.project_energy(
                node_id=nid,
                current_energy=curr_e,
                current_time=current_time,
                target_time=current_time + time_offset,
                battery_capacity=node.max_energy
            )
        proj_cache[cache_key] = val
        return val

    # Relative tolerance used to treat two bottleneck values as "tied" for
    # cost-aware tie-breaking (see Cost-Aware Tie-Breaking note above).
    TIE_REL_TOL = 0.01
    rx_cost_fixed = energy_model.receive_energy(k_bits)

    # Precompute base station distances and transmission reachability for all alive nodes
    bs_reach: Dict[int, Tuple[bool, float]] = {}
    for u in alive_nodes:
        dist_bs = ((nodes[u].x - base_station_pos[0]) ** 2 + (nodes[u].y - base_station_pos[1]) ** 2) ** 0.5
        can_bs = transmission_range is None or dist_bs <= transmission_range
        tx_bs = energy_model.transmit_energy(k_bits, dist_bs)
        bs_reach[u] = (can_bs, tx_bs)

    # 3D tables:
    # dp[node][hop][time_offset] = best bottleneck value
    # dp_cost[node][hop][time_offset] = cumulative physical energy cost of that best path
    # pred[node][hop][time_offset] = (prev_node, prev_time_offset)
    dp: Dict[int, Dict[int, Dict[int, float]]] = {}
    dp_cost: Dict[int, Dict[int, Dict[int, float]]] = {}
    pred: Dict[int, Dict[int, Dict[int, Tuple[Optional[int], Optional[int]]]]] = {}
    reached_at: Dict[Tuple[int, int], List[int]] = {}

    def update_dp(nid: int, h: int, t: int, val: float, cost: float, p_node: Optional[int], p_t: Optional[int]):
        if nid not in dp:
            dp[nid] = {}
            dp_cost[nid] = {}
            pred[nid] = {}
        if h not in dp[nid]:
            dp[nid][h] = {}
            dp_cost[nid][h] = {}
            pred[nid][h] = {}

        if t not in dp[nid][h]:
            reached_at.setdefault((h, t), []).append(nid)
            dp[nid][h][t] = val
            dp_cost[nid][h][t] = cost
            pred[nid][h][t] = (p_node, p_t)
            return

        existing_val = dp[nid][h][t]
        tol = max(1e-12, TIE_REL_TOL * max(existing_val, val))
        if val > existing_val + tol:
            accept = True
        elif val > existing_val - tol and cost < dp_cost[nid][h][t]:
            accept = True  # near-tied bottleneck: prefer the physically cheaper path
        else:
            accept = False

        if accept:
            dp[nid][h][t] = val
            dp_cost[nid][h][t] = cost
            pred[nid][h][t] = (p_node, p_t)

    # Base case: packet starts at source at hop 0 and time offset 0
    source_energy = get_projected_energy(source, 0)
    update_dp(source, 0, 0, source_energy, 0.0, None, None)

    # Propagate through hop and time dimensions
    for h in range(1, max_hops + 1):
        prev_t = (h - 1) * hop_delay
        t = h * hop_delay
        if t > time_horizon:
            break
        candidates = reached_at.get((h - 1, prev_t), [])
        if not candidates:
            continue

        for u in candidates:
            bottleneck_u = dp[u][h - 1][prev_t]
            if bottleneck_u <= 0.0:
                continue

            cost_u = dp_cost[u][h - 1][prev_t]

            # Forward to neighboring sensor nodes
            if u in adj_list:
                u_node = nodes[u]
                for v, _ in adj_list[u]:
                    if v not in alive_nodes or v == source:
                        continue
                    v_node = nodes[v]
                    dist_uv = u_node.distance_to(v_node)
                    if transmission_range is not None and dist_uv > transmission_range:
                        continue

                    # Physical energy check: u must afford transmission, v must afford reception
                    tx_cost_uv = energy_model.transmit_energy(k_bits, dist_uv)
                    if bottleneck_u <= tx_cost_uv:
                        continue

                    e_proj_v = get_projected_energy(v, t)
                    avail_v = e_proj_v - rx_cost_fixed
                    if avail_v <= rx_cost_fixed * 0.5:
                        continue

                    candidate_val = min(bottleneck_u, avail_v)
                    edge_cost = tx_cost_uv + rx_cost_fixed
                    candidate_cost = cost_u + edge_cost
                    update_dp(v, h, t, candidate_val, candidate_cost, u, prev_t)

            # Forward directly to base station (-1)
            can_reach_bs, tx_cost_bs = bs_reach.get(u, (False, 0.0))
            if can_reach_bs and bottleneck_u > tx_cost_bs:
                v = -1
                candidate_val = bottleneck_u  # base station has no energy constraint
                candidate_cost = cost_u + tx_cost_bs
                update_dp(v, h, t, candidate_val, candidate_cost, u, prev_t)

    # Find the best route ending at the base station, using the same
    # relative-tolerance cost tie-break as update_dp so the final pick is
    # never a needlessly expensive path when a cheaper one is essentially
    # as safe.
    best_lifetime = 0.0
    best_cost = float('inf')
    best_h = -1
    best_t = -1

    if -1 in dp:
        for h, t_map in dp[-1].items():
            for t, val in t_map.items():
                cost = dp_cost[-1][h][t]
                if best_h == -1:
                    accept = True
                else:
                    tol = max(1e-12, TIE_REL_TOL * max(best_lifetime, val))
                    if val > best_lifetime + tol:
                        accept = True
                    elif val > best_lifetime - tol and cost < best_cost:
                        accept = True
                    else:
                        accept = False
                if accept:
                    best_lifetime = val
                    best_cost = cost
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


def dp_max_product_belief_routing(
    nodes: Dict[int, Node],
    adj_list: Dict[int, List[Tuple[int, float]]],
    source: int,
    base_station_pos: Tuple[float, float],
    energy_model: EnergyModel,
    alive_nodes: Set[int],
    energy_view: EnergyView,
    harvesting_model: Optional[HarvestingProfile] = None,
    current_time: int = 0,
    max_hops: Optional[int] = None,
    time_horizon: Optional[int] = None,
    deadline_w: int = 2,
    k_bits: int = 1,
    transmission_range: Optional[float] = None,
    lcb_z: Optional[float] = None,
    reserved_load: Optional[Dict[int, float]] = None
) -> Tuple[float, List[int], List[int]]:
    """
    Max-Product Probabilistic Dynamic Programming Routing with Waiting under Energy Uncertainty.

    Finds a route and per-hop wait schedule from source to base station (-1) that maximizes
    the end-to-end delivery probability:
        P_path = prod_{hop (u, v)} P(afford hop)
    computed in log-domain:
        log P_path = sum_{hop (u, v)} log P(afford hop)

    Allows packet to wait w in [0, deadline_w] slots at intermediate nodes to recharge.
    Ties broken on expected physical transmission cost.
    Returns (path_success_prob, path, schedule_time_offsets).
    """
    import math

    if source not in alive_nodes:
        return 0.0, [], []

    num_alive = len(alive_nodes)
    if max_hops is None:
        max_hops = min(10, max(1, num_alive))
    if max_hops < 1:
        return 0.0, [], []

    deadline_w = max(0, deadline_w)
    if time_horizon is None:
        time_horizon = max_hops * (deadline_w + 1)
    time_horizon = max(1, time_horizon)

    reservations = reserved_load or {}
    rx_cost_fixed = energy_model.receive_energy(k_bits)

    # Precompute Base Station reachability and transmission costs
    bs_reach: Dict[int, Tuple[bool, float]] = {}
    for u in alive_nodes:
        dist_bs = math.sqrt((nodes[u].x - base_station_pos[0]) ** 2 + (nodes[u].y - base_station_pos[1]) ** 2)
        can_bs = transmission_range is None or dist_bs <= transmission_range
        tx_bs = energy_model.transmit_energy(k_bits, dist_bs)
        bs_reach[u] = (can_bs, tx_bs)

    # Tables:
    # dp[node][hop][time_offset] = metric (log_prob in max-product mode, or bottleneck LCB energy in LCB mode)
    # dp_cost[node][hop][time_offset] = cumulative transmission energy cost
    # pred[node][hop][time_offset] = (prev_node, prev_time_offset)
    dp: Dict[int, Dict[int, Dict[int, float]]] = {}
    dp_cost: Dict[int, Dict[int, Dict[int, float]]] = {}
    pred: Dict[int, Dict[int, Dict[int, Tuple[Optional[int], Optional[int]]]]] = {}
    reached_at: Dict[int, Dict[int, List[int]]] = {}

    def update_dp(nid: int, h: int, t: int, metric: float, cost: float, p_node: Optional[int], p_t: Optional[int]):
        if nid not in dp:
            dp[nid] = {}
            dp_cost[nid] = {}
            pred[nid] = {}
        if h not in dp[nid]:
            dp[nid][h] = {}
            dp_cost[nid][h] = {}
            pred[nid][h] = {}

        if t not in dp[nid][h]:
            reached_at.setdefault(h, {}).setdefault(t, []).append(nid)
            dp[nid][h][t] = metric
            dp_cost[nid][h][t] = cost
            pred[nid][h][t] = (p_node, p_t)
            return

        curr_metric = dp[nid][h][t]
        tol = 0.05 if lcb_z is None else max(1e-12, 0.01 * max(abs(curr_metric), abs(metric)))

        if metric > curr_metric + tol:
            accept = True
        elif metric > curr_metric - tol and cost < dp_cost[nid][h][t]:
            accept = True
        else:
            accept = False

        if accept:
            dp[nid][h][t] = metric
            dp_cost[nid][h][t] = cost
            pred[nid][h][t] = (p_node, p_t)

    # Base case: Source at h=0, t=0
    if lcb_z is not None:
        # LCB mode: E_LCB = mu - z * sigma
        s_mu = energy_view.mean(source, 0)
        s_var = energy_view.variance(source, 0)
        s_lcb = max(0.0, s_mu - lcb_z * math.sqrt(max(1e-9, s_var)) - reservations.get(source, 0.0))
        update_dp(source, 0, 0, s_lcb, 0.0, None, None)
    else:
        # Max-product mode: log(P=1.0) = 0.0
        update_dp(source, 0, 0, 0.0, 0.0, None, None)

    # Precompute distances to base station for directional progress
    dist_to_bs = {
        nid: math.sqrt((nodes[nid].x - base_station_pos[0]) ** 2 + (nodes[nid].y - base_station_pos[1]) ** 2)
        for nid in alive_nodes
    }
    dist_to_bs[-1] = 0.0

    # Dynamic Programming loop over hops
    for h in range(1, max_hops + 1):
        prev_states = reached_at.get(h - 1, {})
        if not prev_states:
            break

        for prev_t, candidates in prev_states.items():
            for u in candidates:
                if u == -1:
                    continue

                metric_u = dp[u][h - 1][prev_t]
                if lcb_z is None and metric_u <= -30.0:
                    continue  # log prob too low
                if lcb_z is not None and metric_u <= 0.0:
                    continue  # depleted bottleneck

                cost_u = dp_cost[u][h - 1][prev_t]
                u_dist_bs = dist_to_bs[u]

                # 1. Forward directly to Base Station (-1) if in range
                can_reach_bs, tx_cost_bs = bs_reach.get(u, (False, 0.0))
                bs_direct_confident = False

                for w in range(deadline_w + 1):
                    t_tx = prev_t + w
                    t_arrive = t_tx + 1
                    if t_arrive > time_horizon:
                        break

                    if can_reach_bs:
                        c_u = tx_cost_bs if u == source else (rx_cost_fixed + tx_cost_bs)
                        c_u_eff = c_u + reservations.get(u, 0.0)

                        if lcb_z is not None:
                            cand_metric = min(metric_u, metric_u - c_u)
                            if cand_metric > 0.0:
                                update_dp(-1, h, t_arrive, cand_metric, cost_u + tx_cost_bs, u, prev_t)
                        else:
                            p_tx = energy_view.p_afford(u, c_u_eff, slot=t_tx)
                            if p_tx > 1e-6:
                                cand_metric = metric_u + math.log(max(1e-6, p_tx))
                                update_dp(-1, h, t_arrive, cand_metric, cost_u + tx_cost_bs, u, prev_t)
                                if p_tx >= 0.90:
                                    bs_direct_confident = True
                                    break  # no need to wait extra slots if already confident

                # If node can reach BS directly with high confidence, skip detour relays
                if bs_direct_confident and u_dist_bs <= (transmission_range or 35.0) * 0.9:
                    continue

                # 2. Forward to neighboring sensor nodes
                if u in adj_list:
                    u_node = nodes[u]
                    for v, _ in adj_list[u]:
                        if v not in alive_nodes or v == source:
                            continue
                        # Prune paths that move backward away from base station
                        if dist_to_bs[v] > u_dist_bs + 10.0:
                            continue

                        v_node = nodes[v]
                        dist_uv = u_node.distance_to(v_node)
                        if transmission_range is not None and dist_uv > transmission_range:
                            continue

                        tx_cost_uv = energy_model.transmit_energy(k_bits, dist_uv)
                        c_u = tx_cost_uv if u == source else (rx_cost_fixed + tx_cost_uv)
                        c_v = rx_cost_fixed
                        c_u_eff = c_u + reservations.get(u, 0.0)
                        c_v_eff = c_v + reservations.get(v, 0.0)
                        edge_energy_cost = tx_cost_uv + rx_cost_fixed

                        # Check waiting options: only wait if immediate transmission has low confidence
                        p_tx_now = energy_view.p_afford(u, c_u_eff, slot=prev_t) if lcb_z is None else 1.0
                        wait_range = [0] if (p_tx_now >= 0.90 or deadline_w == 0) else range(deadline_w + 1)

                        for w in wait_range:
                            t_tx = prev_t + w
                            t_arrive = t_tx + 1
                            if t_arrive > time_horizon:
                                break

                            if lcb_z is not None:
                                v_mu = energy_view.mean(v, t_arrive)
                                v_var = energy_view.variance(v, t_arrive)
                                v_lcb = max(0.0, v_mu - lcb_z * math.sqrt(max(1e-9, v_var)) - reservations.get(v, 0.0))
                                cand_metric = min(metric_u, v_lcb - c_v)
                                if cand_metric <= 0.0:
                                    continue
                            else:
                                p_tx = energy_view.p_afford(u, c_u_eff, slot=t_tx)
                                p_rx = energy_view.p_afford(v, c_v_eff, slot=t_arrive)
                                p_hop = p_tx * p_rx
                                if p_hop <= 1e-5:
                                    continue
                                cand_metric = metric_u + math.log(max(1e-6, p_hop))

                            update_dp(v, h, t_arrive, cand_metric, cost_u + edge_energy_cost, u, prev_t)

    # Find the best route arriving at the base station
    best_metric = -float('inf')
    best_cost = float('inf')
    best_h = -1
    best_t = -1

    if -1 in dp:
        for h, t_dict in dp[-1].items():
            for t, val in t_dict.items():
                cost = dp_cost[-1][h][t]
                tol = 0.05 if lcb_z is None else max(1e-12, 0.01 * max(abs(best_metric), abs(val)))
                if val > best_metric + tol:
                    best_metric = val
                    best_cost = cost
                    best_h = h
                    best_t = t
                elif val > best_metric - tol and cost < best_cost:
                    best_metric = val
                    best_cost = cost
                    best_h = h
                    best_t = t

    if best_h == -1 or (lcb_z is None and best_metric <= -50.0) or (lcb_z is not None and best_metric <= 0.0):
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

    final_score = math.exp(best_metric) if lcb_z is None else best_metric
    return final_score, path, schedule


def compute_belief_routes_for_cluster_heads(
    nodes: Dict[int, Node],
    adj_list: Dict[int, List[Tuple[int, float]]],
    cluster_heads: List[int],
    base_station_pos: Tuple[float, float],
    energy_model: EnergyModel,
    alive_nodes: Set[int],
    energy_view: EnergyView,
    harvesting_model: Optional[HarvestingProfile] = None,
    current_time: int = 0,
    max_hops: int = 10,
    time_horizon: int = 20,
    deadline_w: int = 2,
    k_bits: int = 1,
    transmission_range: Optional[float] = None,
    lcb_z: Optional[float] = None,
    apply_reservations: bool = True
) -> Dict[int, Tuple[Optional[List[int]], float]]:
    """
    Computes routes sequentially for all cluster heads using belief DP,
    applying load reservations to prevent overloading shared bottleneck relays.
    """
    routes: Dict[int, Tuple[Optional[List[int]], float]] = {}
    reservations: Dict[int, float] = {}
    rx_cost = energy_model.receive_energy(k_bits)

    for ch in cluster_heads:
        if ch not in alive_nodes:
            routes[ch] = (None, 0.0)
            continue

        score, path, _ = dp_max_product_belief_routing(
            nodes=nodes,
            adj_list=adj_list,
            source=ch,
            base_station_pos=base_station_pos,
            energy_model=energy_model,
            alive_nodes=alive_nodes,
            energy_view=energy_view,
            harvesting_model=harvesting_model,
            current_time=current_time,
            max_hops=max_hops,
            time_horizon=time_horizon,
            deadline_w=deadline_w,
            k_bits=k_bits,
            transmission_range=transmission_range,
            lcb_z=lcb_z,
            reserved_load=reservations
        )

        routes[ch] = (path, score)

        # Apply reservations for intermediate relays along committed path
        if apply_reservations and path and len(path) > 2:
            for i in range(1, len(path) - 1):
                u = path[i]
                v = path[i + 1]
                if v == -1:
                    dist = math.sqrt((nodes[u].x - base_station_pos[0]) ** 2 + (nodes[u].y - base_station_pos[1]) ** 2)
                else:
                    dist = nodes[u].distance_to(nodes[v])
                tx_cost = energy_model.transmit_energy(k_bits, dist)
                commit_cost = rx_cost + tx_cost
                reservations[u] = reservations.get(u, 0.0) + commit_cost

    return routes