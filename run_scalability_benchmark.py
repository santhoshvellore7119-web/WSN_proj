"""
Scalability Benchmark: Empirical Validation of Asymptotic Complexity (N = 50 -> 500 nodes)

Empirically measures per-call execution latency across expanding network topologies:
- Dijkstra: O(|E| + |V| log |V|)
- Classical Maximin DP: O(|E| H)
- Time-Augmented DP: O(|E| H T)
- Union-Find Live Detour Rerouting: O(deg(u) * alpha(V))

Demonstrates that Time-Augmented DP scales linearly with edges |E| and time horizon T,
and that DSU detour repair executes in microseconds regardless of network size.
"""

import sys
import os
import time
import math
import matplotlib.pyplot as plt
import numpy as np

sys.path.append('src')

from network import Node, Graph
from energy_model import EnergyModel
from harvesting_model import create_harvesting_model
from routing import dijkstra, astar, UnionFind, rip_up_and_reroute
from dp_lifetime import dp_lifetime_maximin_path, dp_time_augmented_lifetime


def run_scalability_benchmark():
    print("=" * 78)
    print("EMPIRICAL SCALABILITY BENCHMARK: N = 50 -> 500 NODES")
    print("=" * 78)

    node_counts = [50, 100, 200, 300, 500]
    fixed_hops = 5
    fixed_t = 10
    area_scale = 100.0
    bs_pos = (50.0, 50.0)
    tx_range = 35.0
    energy_model = EnergyModel()
    harvesting = create_harvesting_model('solar', peak_rate=0.0012, period=24)

    times_dijkstra = []
    times_classic_dp = []
    times_time_dp = []
    times_dsu_reroute = []

    for n in node_counts:
        print(f"\nBenchmarking Scale N = {n} Nodes...")
        # Scale area to maintain constant node density
        current_area = area_scale * math.sqrt(n / 50.0)
        current_bs = (current_area / 2.0, current_area / 2.0)

        # Place nodes uniformly
        import random
        rng = random.Random(42 + n)
        nodes = {
            i: Node(node_id=i, x=rng.uniform(0, current_area), y=rng.uniform(0, current_area), initial_energy=0.045, max_energy=0.50)
            for i in range(n)
        }
        graph = Graph(nodes)
        alive_nodes = set(nodes.keys())

        # Measure Dijkstra
        d_times = []
        for _ in range(5):
            src = rng.choice(list(alive_nodes))
            t0 = time.perf_counter()
            dijkstra(nodes, graph.adjacency_list, src, current_bs, energy_model, alive_nodes, transmission_range=tx_range)
            d_times.append((time.perf_counter() - t0) * 1e3)  # ms

        # Measure Classical DP
        c_times = []
        for _ in range(5):
            src = rng.choice(list(alive_nodes))
            t0 = time.perf_counter()
            dp_lifetime_maximin_path(nodes, graph.adjacency_list, src, current_bs, energy_model, alive_nodes, max_hops=fixed_hops, transmission_range=tx_range)
            c_times.append((time.perf_counter() - t0) * 1e3)

        # Measure Time-Augmented DP
        t_times = []
        for _ in range(5):
            src = rng.choice(list(alive_nodes))
            t0 = time.perf_counter()
            dp_time_augmented_lifetime(
                nodes, graph.adjacency_list, src, current_bs, energy_model, alive_nodes,
                harvesting_model=harvesting, current_time=12, max_hops=fixed_hops, time_horizon=fixed_t, transmission_range=tx_range
            )
            t_times.append((time.perf_counter() - t0) * 1e3)

        # Measure DSU Live Detour Repair
        dsu_times = []
        # Simulate active route with intermediate node failure
        sample_src = rng.choice(list(alive_nodes))
        sample_path, _ = dijkstra(nodes, graph.adjacency_list, sample_src, current_bs, energy_model, alive_nodes, transmission_range=tx_range)
        if sample_path and len(sample_path) >= 3:
            failed_node = sample_path[1]
            failed_idx = 1
        else:
            failed_node = sample_src
            failed_idx = 0
            sample_path = [sample_src, -1]

        for _ in range(10):
            t0 = time.perf_counter()
            rip_up_and_reroute(nodes, graph.adjacency_list, failed_node, sample_path, current_bs, energy_model, alive_nodes, transmission_range=tx_range)
            dsu_times.append((time.perf_counter() - t0) * 1e3)

        mean_d = np.mean(d_times)
        mean_c = np.mean(c_times)
        mean_t = np.mean(t_times)
        mean_dsu = np.mean(dsu_times)

        times_dijkstra.append(mean_d)
        times_classic_dp.append(mean_c)
        times_time_dp.append(mean_t)
        times_dsu_reroute.append(mean_dsu)

        print(f"  N={n:>3} | Dijkstra: {mean_d:>7.3f} ms | Classic DP: {mean_c:>7.3f} ms | Time-DP: {mean_t:>7.3f} ms | DSU Detour: {mean_dsu * 1000:>6.1f} us")

    # Generate Publication Scaling Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    ax1.plot(node_counts, times_dijkstra, 'o--', color='#38a169', label=r'Dijkstra $O(|E| + |V|\log |V|)$', linewidth=2)
    ax1.plot(node_counts, times_classic_dp, 's--', color='#dd6b20', label=r'Classical DP $O(|E| H)$', linewidth=2)
    ax1.plot(node_counts, times_time_dp, '^-', color='#3182ce', label=r'Time-Augmented DP $O(|E| H T)$', linewidth=2.5)
    ax1.set_xlabel('Network Size (Number of Sensor Nodes $N$)', fontsize=11)
    ax1.set_ylabel('Per-Route Computation Time (ms)', fontsize=11)
    ax1.set_title('(A) Path Planning Latency vs Scale', fontsize=12, fontweight='bold')
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.legend(loc='upper left', frameon=True)

    # Subplot 2: DSU Local Detour vs Global Reroute
    ax2.plot(node_counts, [t * 1000 for t in times_dsu_reroute], 'D-', color='#805ad5', label=r'DSU Local Detour $O(\mathrm{deg}(u)\cdot\alpha(V))$', linewidth=2.5)
    ax2.plot(node_counts, [t * 1000 for t in times_dijkstra], 'o--', color='#38a169', label='Full Dijkstra Recalculation (Global)', linewidth=2)
    ax2.set_xlabel('Network Size (Number of Sensor Nodes $N$)', fontsize=11)
    ax2.set_ylabel(r'Recovery Latency (microseconds $\mu$s)', fontsize=11)
    ax2.set_title('(B) Live Fault Recovery: DSU vs Global Recalculation', fontsize=12, fontweight='bold')
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.legend(loc='upper left', frameon=True)

    plt.tight_layout()
    os.makedirs('results', exist_ok=True)
    plot_path = os.path.join('results', 'scalability_empirical_curves.png')
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"\nSaved empirical scalability plot to: {plot_path}")


if __name__ == '__main__':
    run_scalability_benchmark()
