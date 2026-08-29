"""
DSU Live Detour Rerouting Benchmark vs Full Route Recomputation

Quantifies:
1. Execution speedup of Union-Find (DSU) local detours vs full Time-DP / Dijkstra recomputation.
2. Packet delivery preservation across varying intermediate node failure rates (1% - 30%).
"""

import sys
import os
import time
import random
import matplotlib.pyplot as plt
import numpy as np

sys.path.append('src')

from simulator import Simulator
from network import Node, Graph
from energy_model import EnergyModel
from routing import rip_up_and_reroute, dijkstra, benchmark_dsu_vs_recompute
from dp_lifetime import dp_time_augmented_lifetime
from harvesting_model import create_harvesting_model


def run_dsu_speedup_benchmark(num_trials: int = 500):
    print("=" * 75)
    print(f"DSU LIVE DETOUR BENCHMARK: SPEEDUP & RECOVERY ANALYSIS (N={num_trials} Trials)")
    print("=" * 75)

    num_nodes = 50
    area = 100.0
    bs_pos = (50.0, 50.0)
    tx_range = 35.0
    seed = 42

    # Instantiate Simulator to generate a realistic connected topology
    sim = Simulator(
        num_nodes=num_nodes,
        area_width=area,
        area_height=area,
        base_station_pos=bs_pos,
        initial_energy=0.50,
        enable_time_dp=True,
        harvesting_profile='solar',
        transmission_range=tx_range,
        seed=seed
    )

    nodes = sim.nodes
    graph = sim.graph
    energy_model = sim.energy_model
    alive_nodes = set(graph.alive_nodes())
    harvesting = sim.harvesting_model

    # Generate candidate multi-hop routes
    candidate_paths = []
    for src in alive_nodes:
        _, path, sched = dp_time_augmented_lifetime(
            nodes=nodes,
            adj_list=graph.adjacency_list,
            source=src,
            base_station_pos=bs_pos,
            energy_model=energy_model,
            alive_nodes=alive_nodes,
            harvesting_model=harvesting,
            current_time=10,
            max_hops=5,
            transmission_range=tx_range
        )
        if path and len(path) >= 3 and path[-1] == -1:
            candidate_paths.append(path)

    if not candidate_paths:
        # Fallback to Dijkstra paths if DP paths are short
        for src in alive_nodes:
            path, _ = dijkstra(nodes, graph.adjacency_list, src, bs_pos, energy_model, alive_nodes, transmission_range=tx_range)
            if path and len(path) >= 3 and path[-1] == -1:
                candidate_paths.append(path)

    print(f"Discovered {len(candidate_paths)} multi-hop candidate paths across {num_nodes}-node network.")

    # 1. Micro-benchmark timing across trials
    dsu_times = []
    dp_times = []
    dijk_times = []
    dsu_success = 0

    rng = random.Random(seed)
    for _ in range(num_trials):
        path = rng.choice(candidate_paths)
        # Select an intermediate hop to fail
        fail_idx = rng.randint(1, len(path) - 2)
        failed_node = path[fail_idx]
        viable_nodes = set(alive_nodes) - {failed_node}

        # DSU detour timing
        t0 = time.perf_counter()
        dsu_path, dsu_cost = rip_up_and_reroute(
            nodes=nodes,
            adj_list=graph.adjacency_list,
            failed_node_id=failed_node,
            active_path=path,
            base_station_pos=bs_pos,
            energy_model=energy_model,
            alive_nodes=alive_nodes,
            harvesting_model=harvesting,
            current_time=10,
            transmission_range=tx_range
        )
        t_dsu = time.perf_counter() - t0
        dsu_times.append(t_dsu * 1e6)  # microseconds

        if dsu_path is not None:
            dsu_success += 1

        # Full Dijkstra recompute timing
        t0 = time.perf_counter()
        dijk_path, _ = dijkstra(
            nodes=nodes,
            adj_list=graph.adjacency_list,
            start=path[0],
            base_station_pos=bs_pos,
            energy_model=energy_model,
            alive_nodes=viable_nodes,
            transmission_range=tx_range
        )
        t_dijk = time.perf_counter() - t0
        dijk_times.append(t_dijk * 1e6)

        # Full Time-DP recompute timing
        t0 = time.perf_counter()
        dp_path, _, _ = dp_time_augmented_lifetime(
            nodes=nodes,
            adj_list=graph.adjacency_list,
            source=path[0],
            base_station_pos=bs_pos,
            energy_model=energy_model,
            alive_nodes=viable_nodes,
            harvesting_model=harvesting,
            current_time=10,
            max_hops=5,
            transmission_range=tx_range
        )
        t_dp = time.perf_counter() - t0
        dp_times.append(t_dp * 1e6)

    mean_dsu = np.mean(dsu_times)
    mean_dijk = np.mean(dijk_times)
    mean_dp = np.mean(dp_times)
    speedup_dp = mean_dp / max(1e-9, mean_dsu)
    speedup_dijk = mean_dijk / max(1e-9, mean_dsu)

    print("\n--- Latency & Speedup Results ---")
    print(f"DSU Local Detour:        {mean_dsu:>8.2f} us / reroute  (Success Rate: {dsu_success / num_trials * 100:.1f}%)")
    print(f"Full Dijkstra Recompute: {mean_dijk:>8.2f} us / reroute  (Speedup vs Dijkstra: {speedup_dijk:.1f}x)")
    print(f"Full Time-DP Recompute:  {mean_dp:>8.2f} us / reroute  (Speedup vs Time-DP:  {speedup_dp:.1f}x)")

    # 2. Failure Rate vs Packet Delivery Stress Test
    failure_rates = [0.01, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30]
    unrepaired_loss = []
    dsu_recovered_delivery = []

    for p_fail in failure_rates:
        delivered_unrepaired = 0
        delivered_dsu = 0
        total_packets = 1000

        for _ in range(total_packets):
            path = rng.choice(candidate_paths)
            # Check if any intermediate node experiences dropout
            survived = True
            rerouted_success = True
            curr_path = list(path)

            for i in range(1, len(path) - 1):
                if rng.random() < p_fail:
                    survived = False
                    # Attempt DSU repair
                    new_p, _ = rip_up_and_reroute(
                        nodes=nodes,
                        adj_list=graph.adjacency_list,
                        failed_node_id=curr_path[i],
                        active_path=curr_path,
                        base_station_pos=bs_pos,
                        energy_model=energy_model,
                        alive_nodes=alive_nodes,
                        harvesting_model=harvesting,
                        current_time=10,
                        transmission_range=tx_range
                    )
                    if new_p is not None:
                        curr_path = new_p
                    else:
                        rerouted_success = False
                    break

            if survived:
                delivered_unrepaired += 1
                delivered_dsu += 1
            elif rerouted_success:
                delivered_dsu += 1

        unrepaired_loss.append(delivered_unrepaired / total_packets * 100.0)
        dsu_recovered_delivery.append(delivered_dsu / total_packets * 100.0)

    # 3. Generate Comparative Plots
    os.makedirs('results', exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))

    # Bar chart: Latency comparison
    methods = ['DSU Local Detour\n(O(\u03b1(V)))', 'Full Dijkstra\n(O(E log V))', 'Full Time-DP\n(O(E\u00b7H\u00b7T))']
    latencies = [mean_dsu, mean_dijk, mean_dp]
    colors = ['#2ca02c', '#1f77b4', '#d62728']

    bars = ax1.bar(methods, latencies, color=colors, edgecolor='black', width=0.55)
    ax1.set_ylabel('Execution Time (\u00b5s)', fontsize=11)
    ax1.set_title(f'Reroute Execution Latency\n(DSU is {speedup_dp:.1f}x faster than Full DP)', fontsize=12, fontweight='bold')
    ax1.grid(True, linestyle='--', alpha=0.5, axis='y')
    for bar in bars:
        height = bar.get_height()
        ax1.annotate(f'{height:.1f} us',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 4), textcoords="offset points",
                     ha='center', va='bottom', fontweight='bold')

    # Line chart: Packet delivery vs Failure Rate
    fail_pcts = [p * 100 for p in failure_rates]
    ax2.plot(fail_pcts, dsu_recovered_delivery, 'g-o', linewidth=2.5, label='With DSU Live Detour Rerouting')
    ax2.plot(fail_pcts, unrepaired_loss, 'r--x', linewidth=2.0, label='Without Live Reroute (Dropped Packets)')
    ax2.set_xlabel('Node Dropout / Failure Probability (%)', fontsize=11)
    ax2.set_ylabel('Successful Packet Delivery Rate (%)', fontsize=11)
    ax2.set_title('Packet Delivery Resilience under Random Dropouts', fontsize=12, fontweight='bold')
    ax2.grid(True, linestyle='--', alpha=0.6)
    ax2.legend(loc='lower left', fontsize=10)

    plt.tight_layout()
    filepath = 'results/dsu_benchmark_speedup.png'
    plt.savefig(filepath, dpi=150)
    plt.close()
    print(f"\nSaved DSU benchmark plot to {filepath}")


if __name__ == '__main__':
    run_dsu_speedup_benchmark()
