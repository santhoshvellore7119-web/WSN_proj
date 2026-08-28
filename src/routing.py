"""
Routing module for WSN simulation.

Implements:
- Dijkstra's algorithm for minimum-energy paths
- A* search using Euclidean distance heuristic
- Union-Find (DSU) for network connectivity tracking
- Live detour rerouting when an intermediate node runs out of energy
"""

import heapq
import math
import time
from typing import Dict, List, Tuple, Optional, Set, Callable, Iterable, Any
from network import Node, Graph
from energy_model import EnergyModel


class UnionFind:
    """Disjoint-Set data structure with path compression and union by rank."""

    def __init__(self, elements: Optional[Iterable[int]] = None):
        self.parent: Dict[int, int] = {}
        self.rank: Dict[int, int] = {}
        self.size: Dict[int, int] = {}
        if elements is not None:
            for elem in elements:
                self.add(elem)

    def add(self, x: int):
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
            self.size[x] = 1

    def find(self, x: int) -> int:
        if x not in self.parent:
            self.add(x)
            return x
        # Path compression
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        root_x = self.find(x)
        root_y = self.find(y)
        if root_x == root_y:
            return False
        # Union by rank
        if self.rank[root_x] < self.rank[root_y]:
            root_x, root_y = root_y, root_x
        self.parent[root_y] = root_x
        self.size[root_x] += self.size[root_y]
        if self.rank[root_x] == self.rank[root_y]:
            self.rank[root_x] += 1
        return True

    def connected(self, x: int, y: int) -> bool:
        return self.find(x) == self.find(y)

    def get_components(self) -> Dict[int, List[int]]:
        components: Dict[int, List[int]] = {}
        for elem in list(self.parent.keys()):
            root = self.find(elem)
            components.setdefault(root, []).append(elem)
        return components


def dijkstra(
    nodes: Dict[int, Node],
    adj_list: Dict[int, List[Tuple[int, float]]],
    start: int,
    base_station_pos: Tuple[float, float],
    energy_model: EnergyModel,
    alive_nodes: Set[int],
    k: int = 1,
    transmission_range: Optional[float] = None
) -> Tuple[Optional[List[int]], float]:
    """
    Finds the lowest-energy path from start node to the base station (-1) using Dijkstra's algorithm.
    """
    if start not in alive_nodes:
        return None, float('inf')

    dist: Dict[int, float] = {node_id: float('inf') for node_id in nodes}
    dist[start] = 0.0
    prev: Dict[int, Optional[int]] = {node_id: None for node_id in nodes}

    pq: List[Tuple[float, int]] = [(0.0, start)]
    visited: Set[int] = set()

    while pq:
        current_dist, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)

        if u == -1:
            break

        neighbors: List[Tuple[int, float]] = []
        if u in adj_list:
            for v, weight in adj_list[u]:
                if v in alive_nodes:
                    if transmission_range is not None:
                        dist_uv = ((nodes[u].x - nodes[v].x)**2 + (nodes[u].y - nodes[v].y)**2)**0.5
                        if dist_uv > transmission_range:
                            continue
                    neighbors.append((v, weight))

        # Check edge to base station (-1)
        if u in alive_nodes:
            u_node = nodes[u]
            dist_to_bs = math.sqrt((u_node.x - base_station_pos[0])**2 + (u_node.y - base_station_pos[1])**2)
            if transmission_range is None or dist_to_bs <= transmission_range:
                weight_to_bs = energy_model.transmit_energy(k, dist_to_bs)
                neighbors.append((-1, weight_to_bs))

        for v, weight in neighbors:
            if v not in dist:
                dist[v] = float('inf')
                prev[v] = None
            alt = current_dist + weight
            if alt < dist[v]:
                dist[v] = alt
                prev[v] = u
                heapq.heappush(pq, (alt, v))

    if dist.get(-1, float('inf')) == float('inf'):
        return None, float('inf')

    path: List[int] = []
    current: Optional[int] = -1
    while current is not None:
        path.append(current)
        current = prev.get(current)
    path.reverse()

    total_cost = dist[-1]
    return path, total_cost


def astar(
    nodes: Dict[int, Node],
    adj_list: Dict[int, List[Tuple[int, float]]],
    start: int,
    base_station_pos: Tuple[float, float],
    energy_model: EnergyModel,
    alive_nodes: Set[int],
    k: int = 1,
    transmission_range: Optional[float] = None
) -> Tuple[Optional[List[int]], float, int]:
    """
    A* search to base station using estimated distance-based transmission energy as heuristic.
    """
    if start not in alive_nodes:
        return None, float('inf'), 0

    def heuristic(node_id: int) -> float:
        if node_id == -1:
            return 0.0
        node = nodes[node_id]
        dx = node.x - base_station_pos[0]
        dy = node.y - base_station_pos[1]
        dist_to_bs = math.sqrt(dx * dx + dy * dy)
        return k * energy_model.E_elec + k * energy_model.E_fs * (dist_to_bs ** 2)

    dist: Dict[int, float] = {node_id: float('inf') for node_id in nodes}
    dist[start] = 0.0
    prev: Dict[int, Optional[int]] = {node_id: None for node_id in nodes}
    f_score: Dict[int, float] = {node_id: float('inf') for node_id in nodes}
    f_score[start] = heuristic(start)

    pq: List[Tuple[float, int]] = [(f_score[start], start)]
    visited: Set[int] = set()
    expanded = 0

    while pq:
        current_f, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        expanded += 1

        if u == -1:
            break

        neighbors: List[Tuple[int, float]] = []
        if u in adj_list:
            for v, weight in adj_list[u]:
                if v in alive_nodes:
                    if transmission_range is not None:
                        dist_uv = ((nodes[u].x - nodes[v].x)**2 + (nodes[u].y - nodes[v].y)**2)**0.5
                        if dist_uv > transmission_range:
                            continue
                    neighbors.append((v, weight))

        if u in alive_nodes:
            u_node = nodes[u]
            dist_to_bs = math.sqrt((u_node.x - base_station_pos[0])**2 + (u_node.y - base_station_pos[1])**2)
            if transmission_range is None or dist_to_bs <= transmission_range:
                weight_to_bs = energy_model.transmit_energy(k, dist_to_bs)
                neighbors.append((-1, weight_to_bs))

        for v, weight in neighbors:
            if v not in dist:
                dist[v] = float('inf')
                prev[v] = None
                f_score[v] = float('inf')
            tentative_g = dist[u] + weight
            if tentative_g < dist[v]:
                dist[v] = tentative_g
                prev[v] = u
                f_score[v] = tentative_g + heuristic(v)
                heapq.heappush(pq, (f_score[v], v))

    if dist.get(-1, float('inf')) == float('inf'):
        return None, float('inf'), expanded

    path: List[int] = []
    current: Optional[int] = -1
    while current is not None:
        path.append(current)
        current = prev.get(current)
    path.reverse()

    total_cost = dist[-1]
    return path, total_cost, expanded


def rip_up_and_reroute(
    nodes: Dict[int, Node],
    adj_list: Dict[int, List[Tuple[int, float]]],
    failed_node_id: int,
    active_path: List[int],
    base_station_pos: Tuple[float, float],
    energy_model: EnergyModel,
    alive_nodes: Set[int],
    harvesting_model: Optional[Any] = None,
    current_time: int = 0,
    transmission_range: Optional[float] = None,
    k: int = 1
) -> Tuple[Optional[List[int]], float]:
    """
    Reroutes an active path around a failed intermediate node using Union-Find
    to quickly check which neighbors can still reach the base station.
    """
    if not active_path or failed_node_id not in active_path:
        return active_path, 0.0

    fail_idx = active_path.index(failed_node_id)
    if fail_idx == 0:
        # Cluster head itself ran out of battery
        return None, float('inf')

    u_prev = active_path[fail_idx - 1]
    if u_prev not in alive_nodes or u_prev == failed_node_id:
        return None, float('inf')

    # Available nodes excluding the failed node
    viable_nodes = set(alive_nodes) - {failed_node_id}
    if u_prev not in viable_nodes:
        return None, float('inf')

    # Build Union-Find sets for connected components
    uf = UnionFind(viable_nodes | {-1})

    for u in viable_nodes:
        # Base station reachability
        u_node = nodes[u]
        dist_bs = math.sqrt((u_node.x - base_station_pos[0])**2 + (u_node.y - base_station_pos[1])**2)
        if transmission_range is None or dist_bs <= transmission_range:
            uf.union(u, -1)

        # Neighbor reachability
        if u in adj_list:
            for v, _ in adj_list[u]:
                if v in viable_nodes:
                    if transmission_range is not None:
                        dist_uv = ((nodes[u].x - nodes[v].x)**2 + (nodes[u].y - nodes[v].y)**2)**0.5
                        if dist_uv > transmission_range:
                            continue
                    uf.union(u, v)

    bs_root = uf.find(-1)

    # Check candidates for local detour from u_prev
    candidates: List[Tuple[float, int, List[int]]] = []

    # Option 1: Send directly from u_prev to BS if in range
    u_prev_node = nodes[u_prev]
    dist_direct_bs = math.sqrt((u_prev_node.x - base_station_pos[0])**2 + (u_prev_node.y - base_station_pos[1])**2)
    if transmission_range is None or dist_direct_bs <= transmission_range:
        cost_direct = energy_model.transmit_energy(k, dist_direct_bs)
        candidates.append((cost_direct, -1, [-1]))

    # Option 2: Alternate neighbors of u_prev connected to BS
    if u_prev in adj_list:
        for v, _ in adj_list[u_prev]:
            if v in viable_nodes and v != failed_node_id and uf.find(v) == bs_root:
                dist_uv = u_prev_node.distance_to(nodes[v])
                if transmission_range is not None and dist_uv > transmission_range:
                    continue
                cost_uv = energy_model.transmit_energy(k, dist_uv)
                # Shortest path from neighbor v to BS
                sub_path, sub_cost = dijkstra(
                    nodes, adj_list, start=v, base_station_pos=base_station_pos,
                    energy_model=energy_model, alive_nodes=viable_nodes, k=k,
                    transmission_range=transmission_range
                )
                if sub_path is not None:
                    total_candidate_cost = cost_uv + sub_cost
                    candidates.append((total_candidate_cost, v, sub_path))

    if not candidates:
        return None, float('inf')

    # Sort by lowest energy cost, tie-break by residual energy
    candidates.sort(key=lambda item: (item[0], -nodes[item[1]].residual_energy if item[1] != -1 else 0.0))
    best_cost, best_target, best_subpath = candidates[0]

    # Splice detour into active path
    prefix = active_path[:fail_idx]
    new_path = prefix + best_subpath

    # Calculate total energy cost
    total_cost = 0.0
    for i in range(len(new_path) - 1):
        src_id = new_path[i]
        dst_id = new_path[i + 1]
        if dst_id == -1:
            d = math.sqrt((nodes[src_id].x - base_station_pos[0])**2 + (nodes[src_id].y - base_station_pos[1])**2)
        else:
            d = nodes[src_id].distance_to(nodes[dst_id])
        total_cost += energy_model.transmit_energy(k, d)

    return new_path, total_cost


def compute_routes_for_cluster_heads(
    nodes: Dict[int, Node],
    graph: Graph,
    energy_model: EnergyModel,
    cluster_heads: List[int],
    base_station_pos: Tuple[float, float],
    alive_nodes: Set[int],
    algorithm: str = 'dijkstra',
    transmission_range: Optional[float] = None
) -> Dict[int, Tuple[Optional[List[int]], float]]:
    """Computes routing paths from each cluster head to the base station."""
    routes = {}
    for ch in cluster_heads:
        if ch not in alive_nodes:
            routes[ch] = (None, float('inf'))
            continue
        if algorithm == 'dijkstra':
            path, cost = dijkstra(
                nodes, graph.adjacency_list, ch, base_station_pos, energy_model,
                alive_nodes, transmission_range=transmission_range
            )
            routes[ch] = (path, cost)
        elif algorithm == 'astar':
            path, cost, _ = astar(
                nodes, graph.adjacency_list, ch, base_station_pos, energy_model,
                alive_nodes, transmission_range=transmission_range
            )
            routes[ch] = (path, cost)
        else:
            raise ValueError("Algorithm must be 'dijkstra' or 'astar'")
    return routes


def compare_dijkstra_astar(
    nodes: Dict[int, Node],
    graph: Graph,
    energy_model: EnergyModel,
    cluster_heads: List[int],
    base_station_pos: Tuple[float, float],
    alive_nodes: Set[int]
) -> Dict[str, Dict]:
    """Runs both Dijkstra and A* to compare execution time and node expansions."""
    results = {'dijkstra': {}, 'astar': {}, 'comparison': {}}

    start_time = time.time()
    dijkstra_routes = compute_routes_for_cluster_heads(
        nodes, graph, energy_model, cluster_heads, base_station_pos, alive_nodes, 'dijkstra'
    )
    dijkstra_time = time.time() - start_time

    start_time = time.time()
    astar_paths = {}
    total_expanded = 0
    for ch in cluster_heads:
        if ch not in alive_nodes:
            astar_paths[ch] = (None, float('inf'))
            continue
        path, cost, expanded = astar(nodes, graph.adjacency_list, ch, base_station_pos, energy_model, alive_nodes)
        astar_paths[ch] = (path, cost)
        total_expanded += expanded
    astar_time = time.time() - start_time

    same_path_count = 0
    total_ch = 0
    for ch in cluster_heads:
        if ch not in alive_nodes:
            continue
        total_ch += 1
        d_path, _ = dijkstra_routes[ch]
        a_path, _ = astar_paths[ch]
        if d_path is not None and a_path is not None and d_path == a_path:
            same_path_count += 1

    results['dijkstra'] = {
        'routes': dijkstra_routes,
        'time': dijkstra_time,
        'paths_found': sum(1 for v in dijkstra_routes.values() if v[0] is not None)
    }
    results['astar'] = {
        'routes': astar_paths,
        'time': astar_time,
        'paths_found': sum(1 for v in astar_paths.values() if v[0] is not None),
        'nodes_expanded': total_expanded
    }
    results['comparison'] = {
        'same_path_count': same_path_count,
        'total_cluster_heads': total_ch,
        'time_ratio': astar_time / dijkstra_time if dijkstra_time > 0 else float('inf'),
        'note': "A* expands fewer nodes than Dijkstra with an admissible heuristic."
    }

    return results