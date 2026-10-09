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
from dp_lifetime import (
    dp_lifetime_maximin_path, dp_time_augmented_lifetime,
    dp_max_product_belief_routing, compute_belief_routes_for_cluster_heads
)
from harvesting_model import HarvestingProfile, create_harvesting_model
from energy_view import (
    EnergyView, OracleView, BlindView, StaleView,
    GaussianBeliefView, HistogramBeliefView, create_energy_view, quantize_energy
)


class Simulator:
    """Discrete-round simulator for wireless sensor networks."""

    def __init__(
        self,
        num_nodes: int = 50,
        area_width: float = 100.0,
        area_height: float = 100.0,
        base_station_pos: Tuple[float, float] = (50.0, 50.0),
        initial_energy: float = 0.05,
        max_battery_capacity: Optional[float] = 0.50,
        desired_clusters_ratio: float = 0.08,
        k_bits: int = 4000,
        data_per_node_per_round: int = 4000,
        aggregation_bits: int = 1000,
        enable_dp_routing: bool = False,
        enable_time_dp: bool = False,
        enable_belief_dp: bool = False,
        belief_deadline_w: int = 2,
        belief_time_horizon: Optional[int] = None,
        belief_lcb_z: Optional[float] = None,
        belief_reservations: bool = True,
        enable_harvesting_ch: bool = False,
        enable_live_reroute: bool = False,
        harvesting_profile: Optional[Union[HarvestingProfile, str]] = None,
        harvesting_kwargs: Optional[Dict[str, Any]] = None,
        max_dp_hops: int = 5,
        routing_algorithm: str = 'dijkstra',
        transmission_range: Optional[float] = 35.0,
        seed: Optional[int] = None,
        energy_view: Optional[EnergyView] = None,
        energy_view_type: str = 'oracle',
        report_interval: int = 1
    ):
        self.num_nodes = num_nodes
        self.area_width = area_width
        self.area_height = area_height
        self.base_station_pos = base_station_pos
        self.initial_energy = initial_energy
        self.max_battery_capacity = max_battery_capacity if max_battery_capacity is not None else max(initial_energy, 0.50)
        self.desired_clusters_ratio = desired_clusters_ratio
        self.k_bits = k_bits
        self.data_per_node_per_round = data_per_node_per_round
        self.aggregation_bits = aggregation_bits
        self.enable_dp_routing = enable_dp_routing
        self.enable_time_dp = enable_time_dp
        self.enable_belief_dp = enable_belief_dp
        self.belief_deadline_w = belief_deadline_w
        self.belief_time_horizon = belief_time_horizon
        self.belief_lcb_z = belief_lcb_z
        self.belief_reservations = belief_reservations
        self.enable_harvesting_ch = enable_harvesting_ch
        self.enable_live_reroute = enable_live_reroute
        self.max_dp_hops = max_dp_hops
        self.routing_algorithm = routing_algorithm
        self.transmission_range = transmission_range
        self.seed = seed
        self.report_interval = report_interval
        self.energy_view_type = energy_view_type

        # Initialize nodes and network graph
        self.nodes: Dict[int, Node] = {}
        self._create_nodes()
        self.graph = Graph(self.nodes)
        self.energy_model = EnergyModel()

        # Initialize EnergyView
        if energy_view is not None:
            self.energy_view = energy_view
        else:
            self.energy_view = create_energy_view(
                energy_view_type,
                self.nodes,
                initial_energy=self.initial_energy,
                initial_mean=self.initial_energy,
                quantization_bits=8
            )

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
        self.brownout_history: List[int] = []
        self.total_energy_history: List[float] = []
        self.harvested_energy_history: List[float] = []
        self.consumed_energy_history: List[float] = []
        self.energy_wasted_history: List[float] = []
        self.cluster_heads_history: List[List[int]] = []
        self.cluster_assignments_history: List[Dict[int, int]] = []
        self.routes_history: List[Dict[int, Tuple[Optional[List[int]], float]]] = []
        self.reroute_events_history: List[int] = []
        self.fairness_history: List[float] = []
        self.pdr_history: List[float] = []
        self.latency_history: List[float] = []
        self.packets_generated_history: List[int] = []
        self.packets_delivered_history: List[int] = []
        self.energy_matrix: List[List[float]] = []  # shape: [round, node_index]
        self.belief_mean_history: List[List[float]] = []
        self.belief_variance_history: List[List[float]] = []
        self.calibration_samples: List[Tuple[float, int]] = []

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

        # 1. Apply internal battery leakage, harvest ambient energy, and advance belief
        round_harvested_total = 0.0
        for nid, node in self.nodes.items():
            node.apply_leakage()
            if self.harvesting_model is not None:
                harvest_amt = self.harvesting_model.sample_harvest(
                    node_id=nid,
                    current_time=self.round_number,
                    duration=1.0
                )
                stored = node.harvest_energy(harvest_amt)
                round_harvested_total += stored

            if hasattr(self.energy_view, 'predict_step'):
                h_mean = self.harvesting_model.expected_harvest(nid, self.round_number - 1, self.round_number) if self.harvesting_model else 0.0
                h_var = self.harvesting_model.variance_harvest(nid, self.round_number - 1, self.round_number) if self.harvesting_model else 0.0
                self.energy_view.predict_step(
                    node_id=nid,
                    harvest_mean=h_mean,
                    harvest_var=h_var,
                    load_mean=1e-6,
                    leakage_rate=node.battery_leakage_rate,
                    efficiency=node.charging_efficiency,
                    max_capacity=node.max_energy
                )

        self.harvested_energy_history.append(round_harvested_total)
        self.energy_matrix.append([self.nodes[i].residual_energy for i in range(self.num_nodes)])
        self.belief_mean_history.append([self.energy_view.mean(i) for i in range(self.num_nodes)])
        self.belief_variance_history.append([self.energy_view.variance(i) for i in range(self.num_nodes)])

        # 2. Cluster formation
        ch_model = self.harvesting_model if self.enable_harvesting_ch else None
        cluster_assignment, cluster_heads, _ = simulate_clustering_round(
            nodes=self.nodes,
            energy_model=self.energy_model,
            desired_clusters_ratio=self.desired_clusters_ratio,
            harvesting_model=ch_model,
            current_time=self.round_number,
            lookahead_rounds=1,
            rng=self._rng,
            energy_view=self.energy_view
        )
        self.cluster_assignments_history.append(dict(cluster_assignment))

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
        alive_nodes_set = {nid for nid in self.nodes if self.energy_view.is_available(nid)}
        routes: Dict[int, Tuple[Optional[List[int]], float]] = {}

        if self.enable_belief_dp:
            routes = compute_belief_routes_for_cluster_heads(
                nodes=self.nodes,
                adj_list=self.graph.adjacency_list,
                cluster_heads=cluster_heads,
                base_station_pos=self.base_station_pos,
                energy_model=self.energy_model,
                alive_nodes=alive_nodes_set,
                energy_view=self.energy_view,
                harvesting_model=self.harvesting_model,
                current_time=self.round_number,
                max_hops=self.max_dp_hops,
                time_horizon=self.belief_time_horizon or (self.max_dp_hops * (self.belief_deadline_w + 1)),
                deadline_w=self.belief_deadline_w,
                k_bits=self.k_bits,
                transmission_range=self.transmission_range,
                lcb_z=self.belief_lcb_z,
                apply_reservations=self.belief_reservations
            )

        elif self.enable_time_dp:
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
                    transmission_range=self.transmission_range,
                    energy_view=self.energy_view
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
                    transmission_range=self.transmission_range,
                    energy_view=self.energy_view
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
                transmission_range=self.transmission_range,
                energy_view=self.energy_view
            )

        # 4. Data transmission with realistic failure semantics
        packets_generated = 0
        packets_delivered = 0
        hop_latencies: List[int] = []
        energy_wasted = 0.0

        members_per_ch: Dict[int, List[int]] = {ch: [] for ch in cluster_heads}
        for nid, ch_id in cluster_assignment.items():
            if nid in self.nodes and self.nodes[nid].role == 'member':
                members_per_ch.setdefault(ch_id, []).append(nid)

        successful_member_packets: Dict[int, int] = {ch: 0 for ch in cluster_heads}

        # 4A: Member nodes transmit to their respective cluster head
        for nid, node in self.nodes.items():
            if not node.is_alive or node.role != 'member':
                continue

            packets_generated += 1
            ch_id = node.cluster_id
            if ch_id == -1 or ch_id not in self.nodes or not self.nodes[ch_id].is_alive:
                continue

            ch_node = self.nodes[ch_id]
            dist = node.distance_to(ch_node)
            if self.transmission_range is not None and dist > self.transmission_range:
                continue

            e_tx = self.energy_model.transmit_energy(self.data_per_node_per_round, dist)
            p_pred_tx = self.energy_view.p_afford(nid, e_tx)
            self.calibration_samples.append((p_pred_tx, 1 if node.residual_energy >= e_tx else 0))
            if node.residual_energy < e_tx:
                # In-flight depletion: brownout, energy wasted, packet dropped
                energy_wasted += node.residual_energy
                node.consume_energy(e_tx)
                self.energy_view.on_failure(nid, e_tx)
                continue

            node.consume_energy(e_tx)

            e_rx = self.energy_model.receive_energy(self.data_per_node_per_round)
            p_pred_rx = self.energy_view.p_afford(ch_id, e_rx)
            self.calibration_samples.append((p_pred_rx, 1 if ch_node.residual_energy >= e_rx else 0))
            if ch_node.residual_energy < e_rx:
                # CH cannot receive: CH browns out, packet dropped
                energy_wasted += (e_tx + ch_node.residual_energy)
                ch_node.consume_energy(e_rx)
                self.energy_view.on_failure(ch_id, e_rx)
                continue

            ch_node.consume_energy(e_rx)
            successful_member_packets[ch_id] = successful_member_packets.get(ch_id, 0) + 1

        # 4B: Cluster heads aggregate and forward data to base station
        round_reroute_count = 0

        for ch_id in cluster_heads:
            ch_node = self.nodes[ch_id]
            if not ch_node.is_alive:
                continue

            # Each active CH generates its own packet
            packets_generated += 1
            packets_in_flow = 1 + successful_member_packets.get(ch_id, 0)

            route_info = routes.get(ch_id)
            if not route_info or not route_info[0] or len(route_info[0]) < 2:
                continue

            path = list(route_info[0])
            hop_idx = 0
            flow_delivered = True
            hops_taken = 0
            flow_wasted = 0.0

            while hop_idx < len(path) - 1:
                tx_id = path[hop_idx]
                rx_id = path[hop_idx + 1]

                if tx_id == -1:
                    break

                tx_node = self.nodes[tx_id]
                if not tx_node.is_alive:
                    flow_delivered = False
                    break

                if rx_id == -1:
                    dist = math.sqrt((tx_node.x - self.base_station_pos[0])**2 + (tx_node.y - self.base_station_pos[1])**2)
                    if self.transmission_range is not None and dist > self.transmission_range:
                        flow_delivered = False
                        break
                else:
                    rx_node = self.nodes[rx_id]
                    dist = tx_node.distance_to(rx_node)
                    if self.transmission_range is not None and dist > self.transmission_range:
                        flow_delivered = False
                        break

                    # If next hop node died/browned out, attempt live reroute
                    if not rx_node.is_alive or rx_node.residual_energy <= 0.0:
                        if self.enable_live_reroute:
                            new_path, _ = rip_up_and_reroute(
                                nodes=self.nodes,
                                adj_list=self.graph.adjacency_list,
                                failed_node_id=rx_id,
                                active_path=path,
                                base_station_pos=self.base_station_pos,
                                energy_model=self.energy_model,
                                alive_nodes=alive_nodes_set,
                                harvesting_model=self.harvesting_model,
                                current_time=self.round_number,
                                transmission_range=self.transmission_range,
                                k=self.aggregation_bits,
                                energy_view=self.energy_view
                            )
                            if new_path is not None and len(new_path) >= 2:
                                path = new_path
                                round_reroute_count += 1
                                continue
                        flow_delivered = False
                        break

                # Deduct transmission cost
                e_tx = self.energy_model.transmit_energy(self.aggregation_bits, dist)
                p_pred_tx = self.energy_view.p_afford(tx_id, e_tx)
                self.calibration_samples.append((p_pred_tx, 1 if tx_node.residual_energy >= e_tx else 0))
                if tx_node.residual_energy < e_tx:
                    flow_wasted += tx_node.residual_energy
                    tx_node.consume_energy(e_tx)
                    self.energy_view.on_failure(tx_id, e_tx)
                    flow_delivered = False
                    break

                tx_node.consume_energy(e_tx)
                hops_taken += 1

                if rx_id != -1:
                    e_rx = self.energy_model.receive_energy(self.aggregation_bits)
                    p_pred_rx = self.energy_view.p_afford(rx_id, e_rx)
                    self.calibration_samples.append((p_pred_rx, 1 if self.nodes[rx_id].residual_energy >= e_rx else 0))
                    if self.nodes[rx_id].residual_energy < e_rx:
                        flow_wasted += self.nodes[rx_id].residual_energy
                        self.nodes[rx_id].consume_energy(e_rx)
                        self.energy_view.on_failure(rx_id, e_rx)
                        flow_delivered = False
                        break
                    self.nodes[rx_id].consume_energy(e_rx)

                hop_idx += 1

            if flow_delivered and path and path[-1] == -1:
                packets_delivered += packets_in_flow
                # Record hop count for each packet in this delivery
                for _ in range(packets_in_flow):
                    hop_latencies.append(hops_taken + 1)

                # Piggybacked telemetry updates on successful delivery
                if self.report_interval > 0 and (self.round_number % self.report_interval == 0):
                    for nid in path:
                        if nid != -1:
                            self.energy_view.on_report(nid, self.nodes[nid].residual_energy, self.round_number)
            else:
                energy_wasted += flow_wasted

        self.reroute_events_history.append(round_reroute_count)

        # 5. Record round statistics
        alive_nodes = self.graph.alive_nodes()
        num_alive = len(alive_nodes)
        brownout_count = self.num_nodes - num_alive
        total_energy = sum(self.nodes[nid].residual_energy for nid in alive_nodes)

        # Calculate energy consumed this round (from nodes)
        last_tot = self.total_energy_history[-1] if self.total_energy_history else (self.num_nodes * self.initial_energy)
        round_consumed = max(0.0, (last_tot + round_harvested_total) - total_energy)

        # Jain's fairness index across all nodes
        energies = [self.nodes[i].residual_energy for i in range(self.num_nodes)]
        sum_e = sum(energies)
        sum_sq = sum(e * e for e in energies)
        fairness = (sum_e ** 2) / (self.num_nodes * sum_sq) if sum_sq > 0 else 1.0

        pdr = (packets_delivered / packets_generated) if packets_generated > 0 else (1.0 if num_alive > 0 else 0.0)
        round_latency = (sum(hop_latencies) / len(hop_latencies)) if hop_latencies else 0.0

        self.alive_nodes_history.append(num_alive)
        self.brownout_history.append(brownout_count)
        self.total_energy_history.append(total_energy)
        self.consumed_energy_history.append(round_consumed)
        self.energy_wasted_history.append(energy_wasted)
        self.fairness_history.append(round(fairness, 4))
        self.pdr_history.append(round(pdr, 4))
        self.latency_history.append(round(round_latency, 2))
        self.packets_generated_history.append(packets_generated)
        self.packets_delivered_history.append(packets_delivered)
        self.cluster_heads_history.append(list(cluster_heads))
        self.routes_history.append(routes)

        if self.first_node_death_round is None and num_alive < self.num_nodes:
            self.first_node_death_round = self.round_number
        if self.half_nodes_dead_round is None and num_alive < (self.num_nodes / 2.0):
            self.half_nodes_dead_round = self.round_number
        if self.last_node_death_round is None and num_alive == 0:
            self.last_node_death_round = self.round_number

        return num_alive > 0

    def run(self, max_rounds: int = 1000, verbose: bool = True, save_log: bool = False):
        """Runs the simulation until maximum rounds reached or non-harvesting network dies."""
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
            # If no harvesting is configured and all nodes died, break early.
            # If harvesting is enabled, continue to max_rounds (nodes can recharge).
            if not alive and self.harvesting_model is None:
                if verbose:
                    print(f"Network depleted at round {self.round_number}")
                break
        elapsed = time.time() - start_time

        if save_log:
            self._save_simulation_log()

        if verbose:
            print("\n--- Simulation Summary ---")
            print(f"Completed rounds: {self.round_number} in {elapsed:.2f}s")
            print(f"First Node Death (FND): {self.first_node_death_round or 'None'}")
            print(f"Half Nodes Dead (HND):  {self.half_nodes_dead_round or 'None'}")
            print(f"Final Alive Nodes:      {self.alive_nodes_history[-1] if self.alive_nodes_history else 0}/{self.num_nodes}")
            print(f"Final Total Energy:     {self.total_energy_history[-1]:.4f} J" if self.total_energy_history else "0.0 J")

    def get_calibration_metrics(self) -> Dict[str, float]:
        """Calculates Brier Score and Expected Calibration Error (ECE)."""
        if not self.calibration_samples:
            return {'brier_score': 0.0, 'ece': 0.0, 'sample_count': 0, 'mean_confidence': 0.0, 'mean_accuracy': 0.0}

        n = len(self.calibration_samples)
        brier = sum((p - y) ** 2 for p, y in self.calibration_samples) / float(n)

        # 10 bins for ECE
        num_bins = 10
        bins = [[] for _ in range(num_bins)]
        for p, y in self.calibration_samples:
            idx = min(num_bins - 1, max(0, int(p * num_bins)))
            bins[idx].append((p, y))

        ece = 0.0
        for b in bins:
            if not b:
                continue
            bin_conf = sum(p for p, _ in b) / float(len(b))
            bin_acc = sum(y for _, y in b) / float(len(b))
            ece += (len(b) / float(n)) * abs(bin_acc - bin_conf)

        return {
            'brier_score': brier,
            'ece': ece,
            'sample_count': n,
            'mean_confidence': sum(p for p, _ in self.calibration_samples) / float(n),
            'mean_accuracy': sum(y for _, y in self.calibration_samples) / float(n)
        }

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
    parser.add_argument('--nodes', type=int, default=50, help='Number of nodes')
    parser.add_argument('--area', type=float, default=100.0, help='Area width/height')
    parser.add_argument('--bs-x', type=float, default=50.0, help='BS X coordinate')
    parser.add_argument('--bs-y', type=float, default=50.0, help='BS Y coordinate')
    parser.add_argument('--initial-energy', type=float, default=0.05, help='Initial energy per node (J)')
    parser.add_argument('--max-capacity', type=float, default=0.50, help='Max battery capacity (J)')
    parser.add_argument('--cluster-ratio', type=float, default=0.08, help='Cluster ratio')
    parser.add_argument('--tx-range', type=float, default=35.0, help='Transmission range in meters')
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
    parser.add_argument('--energy-view', type=str, choices=['oracle', 'stale', 'blind', 'belief'], default='oracle', help='Energy view type')
    parser.add_argument('--report-interval', type=int, default=1, help='Telemetry report interval in rounds')
    args = parser.parse_args()

    sim = Simulator(
        num_nodes=args.nodes,
        area_width=args.area,
        area_height=args.area,
        base_station_pos=(args.bs_x, args.bs_y),
        initial_energy=args.initial_energy,
        max_battery_capacity=args.max_capacity,
        desired_clusters_ratio=args.cluster_ratio,
        transmission_range=args.tx_range,
        k_bits=args.k_bits,
        data_per_node_per_round=args.data_per_node,
        aggregation_bits=args.aggregation_bits,
        enable_dp_routing=args.enable_dp,
        enable_time_dp=args.enable_time_dp,
        enable_harvesting_ch=args.enable_harvesting_ch,
        enable_live_reroute=args.enable_live_reroute,
        harvesting_profile=args.harvesting,
        routing_algorithm=args.routing,
        energy_view_type=args.energy_view,
        report_interval=args.report_interval
    )
    sim.run(max_rounds=args.max_rounds)


if __name__ == "__main__":
    main()