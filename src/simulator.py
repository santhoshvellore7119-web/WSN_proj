"""
Simulation engine for WSN energy routing.

Handles the round-by-round lifecycle:
1. Ambient energy harvesting
2. Cluster head election (LEACH or harvesting-aware)
3. Route calculation (Dijkstra, A*, classical DP, or Time-Augmented DP)
4. Packet transmission, energy deduction, and live rerouting (DSU)
5. Statistics logging and lifetime milestone tracking
"""

import time
import csv
import os
import math
from typing import Dict, List, Tuple, Optional, Union, Any
from network import Node, Graph
from energy_model import EnergyModel
from clustering import leach_clustering, simulate_clustering_round
from routing import dijkstra, astar, compute_routes_for_cluster_heads, compare_dijkstra_astar, rip_up_and_reroute
from dp_lifetime import dp_lifetime_maximin_path, dp_time_augmented_lifetime
from harvesting_model import HarvestingProfile, create_harvesting_model


class Simulator:
    """Discrete-round simulator for wireless sensor networks."""

    def __init__(
        self,
        num_nodes: int = 100,
        area_width: float = 100.0,
        area_height: float = 100.0,
        base_station_pos: Tuple[float, float] = (50.0, 50.0),
        initial_energy: float = 2.0,
        max_battery_capacity: Optional[float] = None,
        desired_clusters_ratio: float = 0.05,
        k_bits: int = 4000,
        data_per_node_per_round: int = 4000,
        aggregation_bits: int = 1000,
        enable_dp_routing: bool = False,
        enable_time_dp: bool = False,
        enable_harvesting_ch: bool = False,
        enable_live_reroute: bool = False,
        harvesting_profile: Optional[Union[HarvestingProfile, str]] = None,
        harvesting_kwargs: Optional[Dict[str, Any]] = None,
        max_dp_hops: int = 5,
        routing_algorithm: str = 'dijkstra',
        transmission_range: Optional[float] = None,
        seed: Optional[int] = None
    ):
        self.num_nodes = num_nodes
        self.area_width = area_width
        self.area_height = area_height
        self.base_station_pos = base_station_pos
        self.initial_energy = initial_energy
        self.max_battery_capacity = max_battery_capacity if max_battery_capacity is not None else max(initial_energy, 2.0)
        self.desired_clusters_ratio = desired_clusters_ratio
        self.k_bits = k_bits
        self.data_per_node_per_round = data_per_node_per_round
        self.aggregation_bits = aggregation_bits
        self.enable_dp_routing = enable_dp_routing
        self.enable_time_dp = enable_time_dp
        self.enable_harvesting_ch = enable_harvesting_ch
        self.enable_live_reroute = enable_live_reroute
        self.max_dp_hops = max_dp_hops
        self.routing_algorithm = routing_algorithm
        self.transmission_range = transmission_range
        self.seed = seed

        # Initialize nodes and network graph
        self.nodes: Dict[int, Node] = {}
        self._create_nodes()
        self.graph = Graph(self.nodes)
        self.energy_model = EnergyModel()

        if isinstance(harvesting_profile, str):
            kwargs = dict(harvesting_kwargs or {})
            if 'nodes' not in kwargs:
                kwargs['nodes'] = self.nodes
            self.harvesting_model: Optional[HarvestingProfile] = create_harvesting_model(harvesting_profile, **kwargs)
        else:
            self.harvesting_model = harvesting_profile

        # Track history for plotting and metrics
        self.round_number = 0
        self.alive_nodes_history: List[int] = []
        self.total_energy_history: List[float] = []
        self.harvested_energy_history: List[float] = []
        self.cluster_heads_history: List[List[int]] = []
        self.routes_history: List[Dict[int, Tuple[Optional[List[int]], float]]] = []
        self.reroute_events_history: List[int] = []
        self.energy_matrix: List[List[float]] = []  # shape: [round, node_index]

        self.first_node_death_round: Optional[int] = None
        self.half_nodes_dead_round: Optional[int] = None
        self.last_node_death_round: Optional[int] = None

        os.makedirs('results', exist_ok=True)

    def _create_nodes(self):
        """Places sensor nodes uniformly in the simulation area."""
        import random
        # Two separate RNG streams seeded deterministically:
        # - placement_rng: controls node (x, y) coordinates
        # - self._rng: controls all per-round stochastic draws (CH election, etc.)
        # Using seed+1 for the second stream keeps them independent.
        placement_rng = random.Random(self.seed) if self.seed is not None else random.Random()
        self._rng: Optional[random.Random] = random.Random(self.seed + 1) if self.seed is not None else None
        for i in range(self.num_nodes):
            x = placement_rng.uniform(0, self.area_width)
            y = placement_rng.uniform(0, self.area_height)
            self.nodes[i] = Node(
                node_id=i,
                x=x,
                y=y,
                initial_energy=self.initial_energy,
                max_energy=self.max_battery_capacity
            )

    def _update_graph_edge_weights(self):
        self.graph.update_edge_weights(self.energy_model)

    def _simulate_round(self) -> bool:
        """Executes one round of harvesting, clustering, routing, and transmission."""
        self.round_number += 1

        # 1. Harvest ambient energy
        round_harvested_total = 0.0
        if self.harvesting_model is not None:
            for nid, node in self.nodes.items():
                if node.is_alive:
                    harvest_amt = self.harvesting_model.sample_harvest(
                        node_id=nid,
                        current_time=self.round_number,
                        duration=1.0
                    )
                    stored = node.harvest_energy(harvest_amt)
                    round_harvested_total += stored
        self.harvested_energy_history.append(round_harvested_total)

        # Record snapshot of current energies for heatmaps
        self.energy_matrix.append([self.nodes[i].residual_energy for i in range(self.num_nodes)])

        # 2. Cluster formation
        ch_model = self.harvesting_model if self.enable_harvesting_ch else None
        cluster_assignment, cluster_heads, _ = simulate_clustering_round(
            nodes=self.nodes,
            energy_model=self.energy_model,
            desired_clusters_ratio=self.desired_clusters_ratio,
            harvesting_model=ch_model,
            current_time=self.round_number,
            lookahead_rounds=1,
            rng=self._rng
        )

        for nid, node in self.nodes.items():
            if not node.is_alive:
                continue
            if nid in cluster_assignment:
                node.cluster_id = cluster_assignment[nid]
                node.role = 'CH' if nid in cluster_heads else 'member'
            else:
                node.role = 'member'
                node.cluster_id = -1

        # 3. Path discovery to base station
        alive_nodes_set = set(self.graph.alive_nodes())
        routes: Dict[int, Tuple[Optional[List[int]], float]] = {}

        if self.enable_time_dp:
            for ch in cluster_heads:
                if ch not in alive_nodes_set:
                    routes[ch] = (None, float('inf'))
                    continue
                lifetime, path, schedule = dp_time_augmented_lifetime(
                    nodes=self.nodes,
                    adj_list=self.graph.adjacency_list,
                    source=ch,
                    base_station_pos=self.base_station_pos,
                    energy_model=self.energy_model,
                    alive_nodes=alive_nodes_set,
                    harvesting_model=self.harvesting_model,
                    current_time=self.round_number,
                    max_hops=self.max_dp_hops,
                    hop_delay=1,
                    k_bits=self.k_bits,
                    transmission_range=self.transmission_range
                )
                routes[ch] = (path, lifetime)

        elif self.enable_dp_routing:
            for ch in cluster_heads:
                if ch not in alive_nodes_set:
                    routes[ch] = (None, float('inf'))
                    continue
                lifetime, path = dp_lifetime_maximin_path(
                    nodes=self.nodes,
                    adj_list=self.graph.adjacency_list,
                    source=ch,
                    base_station_pos=self.base_station_pos,
                    energy_model=self.energy_model,
                    alive_nodes=alive_nodes_set,
                    max_hops=self.max_dp_hops,
                    k_bits=self.k_bits,
                    transmission_range=self.transmission_range
                )
                routes[ch] = (path, lifetime)

        else:
            routes = compute_routes_for_cluster_heads(
                nodes=self.nodes,
                graph=self.graph,
                energy_model=self.energy_model,
                cluster_heads=cluster_heads,
                base_station_pos=self.base_station_pos,
                alive_nodes=alive_nodes_set,
                algorithm=self.routing_algorithm,
                transmission_range=self.transmission_range
            )

        # 4. Data transmission and energy consumption
        members_per_ch: Dict[int, List[int]] = {ch: [] for ch in cluster_heads}
        for nid, ch_id in cluster_assignment.items():
            if nid not in members_per_ch:
                members_per_ch.setdefault(ch_id, []).append(nid)

        # 4A: Member nodes transmit to their respective cluster head
        for nid, node in self.nodes.items():
            if not node.is_alive or node.role != 'member':
                continue
            ch_id = node.cluster_id
            if ch_id != -1 and ch_id in self.nodes and self.nodes[ch_id].is_alive:
                ch_node = self.nodes[ch_id]
                dist = node.distance_to(ch_node)
                e_tx = self.energy_model.transmit_energy(self.data_per_node_per_round, dist)
                node.consume_energy(e_tx)

        # 4B: Cluster heads aggregate and forward data to base station
        round_reroute_count = 0

        for ch_id in cluster_heads:
            ch_node = self.nodes[ch_id]
            if not ch_node.is_alive:
                continue

            num_members = len(members_per_ch.get(ch_id, []))
            if num_members > 0:
                e_rx = self.energy_model.receive_energy(num_members * self.data_per_node_per_round)
                ch_node.consume_energy(e_rx)

            route_info = routes.get(ch_id)
            if not route_info or not route_info[0] or len(route_info[0]) < 2:
                continue

            path = list(route_info[0])
            hop_idx = 0

            while hop_idx < len(path) - 1:
                tx_id = path[hop_idx]
                rx_id = path[hop_idx + 1]

                if tx_id == -1:
                    break

                tx_node = self.nodes[tx_id]
                if not tx_node.is_alive:
                    break

                if rx_id == -1:
                    dist = math.sqrt((tx_node.x - self.base_station_pos[0])**2 + (tx_node.y - self.base_station_pos[1])**2)
                else:
                    rx_node = self.nodes[rx_id]
                    dist = tx_node.distance_to(rx_node)

                    # If next hop node died, attempt local reroute
                    if not rx_node.is_alive or rx_node.residual_energy <= 0.0:
                        if self.enable_live_reroute:
                            new_path, _ = rip_up_and_reroute(
                                nodes=self.nodes,
                                adj_list=self.graph.adjacency_list,
                                failed_node_id=rx_id,
                                active_path=path,
                                base_station_pos=self.base_station_pos,
                                energy_model=self.energy_model,
                                alive_nodes=set(self.graph.alive_nodes()),
                                harvesting_model=self.harvesting_model,
                                current_time=self.round_number,
                                transmission_range=self.transmission_range,
                                k=self.aggregation_bits
                            )
                            if new_path is not None and len(new_path) >= 2:
                                path = new_path
                                round_reroute_count += 1
                                continue
                        break

                # Deduct transmission and reception costs
                e_tx = self.energy_model.transmit_energy(self.aggregation_bits, dist)
                tx_node.consume_energy(e_tx)

                if rx_id != -1:
                    e_rx = self.energy_model.receive_energy(self.aggregation_bits)
                    self.nodes[rx_id].consume_energy(e_rx)

                hop_idx += 1

        self.reroute_events_history.append(round_reroute_count)

        # 5. Record round statistics
        alive_nodes = self.graph.alive_nodes()
        num_alive = len(alive_nodes)
        total_energy = sum(self.nodes[nid].residual_energy for nid in alive_nodes)

        self.alive_nodes_history.append(num_alive)
        self.total_energy_history.append(total_energy)
        self.cluster_heads_history.append(list(cluster_heads))
        self.routes_history.append(routes)

        if self.first_node_death_round is None and num_alive < self.num_nodes:
            self.first_node_death_round = self.round_number
        if self.half_nodes_dead_round is None and num_alive < (self.num_nodes / 2.0):
            self.half_nodes_dead_round = self.round_number
        if self.last_node_death_round is None and num_alive == 0:
            self.last_node_death_round = self.round_number

        return num_alive > 0

    def run(self, max_rounds: int = 1000, verbose: bool = True):
        """Runs the simulation until maximum rounds reached or all nodes die."""
        if verbose:
            print(f"Starting simulation: {self.num_nodes} nodes, max {max_rounds} rounds.")
            print(f"Area: {self.area_width}x{self.area_height}m, Base Station at {self.base_station_pos}")
            harv_desc = str(self.harvesting_model) if self.harvesting_model else "None (No Harvesting)"
            print(f"Harvesting Profile: {harv_desc}")
            mode_desc = "Time-Augmented DP" if self.enable_time_dp else ("Maximin DP" if self.enable_dp_routing else self.routing_algorithm.upper())
            print(f"Routing Mode: {mode_desc} | Harv-Aware CH: {self.enable_harvesting_ch} | Live Reroute: {self.enable_live_reroute}")

        start_time = time.time()
        for _ in range(max_rounds):
            alive = self._simulate_round()
            if not alive:
                if verbose:
                    print(f"Network depleted at round {self.round_number}")
                break
        elapsed = time.time() - start_time

        self._save_simulation_log()

        if verbose:
            print("\n--- Simulation Summary ---")
            print(f"Completed rounds: {self.round_number} in {elapsed:.2f}s")
            print(f"First Node Death (FND): {self.first_node_death_round or 'None'}")
            print(f"Half Nodes Dead (HND):  {self.half_nodes_dead_round or 'None'}")
            print(f"Final Alive Nodes:      {self.alive_nodes_history[-1] if self.alive_nodes_history else 0}/{self.num_nodes}")
            print(f"Final Total Energy:     {self.total_energy_history[-1]:.4f} J" if self.total_energy_history else "0.0 J")

    def _save_simulation_log(self, filepath: str = 'results/simulation_log.csv'):
        """Saves simulation stats to CSV."""
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['round', 'alive_nodes', 'total_energy_joules', 'harvested_energy_joules', 'reroute_events'])
            for r in range(len(self.alive_nodes_history)):
                alive = self.alive_nodes_history[r]
                energy = self.total_energy_history[r]
                harvest = self.harvested_energy_history[r] if r < len(self.harvested_energy_history) else 0.0
                reroutes = self.reroute_events_history[r] if r < len(self.reroute_events_history) else 0
                writer.writerow([r + 1, alive, energy, harvest, reroutes])


def main():
    import argparse
    parser = argparse.ArgumentParser(description='WSN Energy-Harvesting Routing Simulator')
    parser.add_argument('--nodes', type=int, default=100, help='Number of nodes')
    parser.add_argument('--area', type=float, default=100.0, help='Area width/height')
    parser.add_argument('--bs-x', type=float, default=50.0, help='BS X coordinate')
    parser.add_argument('--bs-y', type=float, default=50.0, help='BS Y coordinate')
    parser.add_argument('--initial-energy', type=float, default=2.0, help='Initial energy per node (J)')
    parser.add_argument('--cluster-ratio', type=float, default=0.05, help='Cluster ratio')
    parser.add_argument('--max-rounds', type=int, default=500, help='Max rounds')
    parser.add_argument('--k-bits', type=int, default=4000, help='Bits per packet')
    parser.add_argument('--data-per-node', type=int, default=4000, help='Data bits per node')
    parser.add_argument('--aggregation-bits', type=int, default=1000, help='Aggregation bits')
    parser.add_argument('--enable-dp', action='store_true', help='Enable classical DP')
    parser.add_argument('--enable-time-dp', action='store_true', help='Enable Time-Augmented DP')
    parser.add_argument('--enable-harvesting-ch', action='store_true', help='Enable harvesting-aware CH rotation')
    parser.add_argument('--enable-live-reroute', action='store_true', help='Enable DSU live reroute')
    parser.add_argument('--harvesting', type=str, default='solar', choices=['solar', 'stochastic', 'constant', 'none', 'shadowed', 'hotspot'], help='Harvesting profile')
    parser.add_argument('--routing', type=str, choices=['dijkstra', 'astar', 'energy_dijkstra'], default='dijkstra', help='Routing algorithm')
    args = parser.parse_args()

    sim = Simulator(
        num_nodes=args.nodes,
        area_width=args.area,
        area_height=args.area,
        base_station_pos=(args.bs_x, args.bs_y),
        initial_energy=args.initial_energy,
        desired_clusters_ratio=args.cluster_ratio,
        k_bits=args.k_bits,
        data_per_node_per_round=args.data_per_node,
        aggregation_bits=args.aggregation_bits,
        enable_dp_routing=args.enable_dp,
        enable_time_dp=args.enable_time_dp,
        enable_harvesting_ch=args.enable_harvesting_ch,
        enable_live_reroute=args.enable_live_reroute,
        harvesting_profile=args.harvesting,
        routing_algorithm=args.routing
    )
    sim.run(max_rounds=args.max_rounds)


if __name__ == "__main__":
    main()