"""
Sensitivity Analysis on Time Horizon (T) and Max Hops (H) Parameters

Characterizes the algorithmic trade-off between lookahead accuracy and computational cost:
- Sweep time horizon T in [1, 2, 4, 6, 8, 10, 15, 20]
- Sweep max hops H in [1, 2, 3, 5, 8]
- Plots the compute vs quality Pareto frontier (results/sensitivity_time_horizon.png)
"""

import sys
import os
import time
import matplotlib.pyplot as plt
import numpy as np

sys.path.append('src')

from simulator import Simulator
from network import Node, Graph
from energy_model import EnergyModel
from dp_lifetime import dp_time_augmented_lifetime
from harvesting_model import create_harvesting_model


def run_sensitivity_analysis():
    print("=" * 75)
    print("SENSITIVITY ANALYSIS: TIME HORIZON (T) & HOP BOUND (H) TRADEOFF")
    print("=" * 75)

    num_nodes = 50
    area = 100.0
    bs_pos = (50.0, 50.0)
    tx_range = 35.0
    seed = 42

    # Instantiate topology
    sim = Simulator(
        num_nodes=num_nodes,
        area_width=area,
        area_height=area,
        base_station_pos=bs_pos,
        initial_energy=0.045,
        max_battery_capacity=0.50,
        enable_time_dp=True,
        harvesting_profile='solar',
        harvesting_kwargs={'peak_rate': 0.0006, 'period': 24, 'day_fraction': 0.5, 'seed': seed},
        transmission_range=tx_range,
        seed=seed
    )

    nodes = sim.nodes
    graph = sim.graph
    energy_model = sim.energy_model
    alive_nodes = set(graph.alive_nodes())
    harvesting = sim.harvesting_model

    time_horizons = [1, 2, 4, 6, 8, 10, 14, 18]
    fixed_h = 5

    latencies_t = []
    bottlenecks_t = []

    print(f"\n1. Sweeping Time Horizon T (with fixed H = {fixed_h}):")
    print(f"{'T (Lookahead)':<15} | {'Latency (us/call)':<18} | {'Mean Bottleneck (J)':<20}")
    print("-" * 60)

    for T in time_horizons:
        call_times = []
        found_bottlenecks = []

        for src in alive_nodes:
            t0 = time.perf_counter()
            bneck, path, _ = dp_time_augmented_lifetime(
                nodes=nodes,
                adj_list=graph.adjacency_list,
                source=src,
                base_station_pos=bs_pos,
                energy_model=energy_model,
                alive_nodes=alive_nodes,
                harvesting_model=harvesting,
                current_time=12,
                max_hops=fixed_h,
                time_horizon=T,
                transmission_range=tx_range
            )
            elapsed = (time.perf_counter() - t0) * 1e6
            call_times.append(elapsed)
            if bneck > 0.0:
                found_bottlenecks.append(bneck)

        mean_time = np.mean(call_times)
        mean_bneck = np.mean(found_bottlenecks) if found_bottlenecks else 0.0
        latencies_t.append(mean_time)
        bottlenecks_t.append(mean_bneck)
        print(f"{T:<15} | {mean_time:>14.2f} us   | {mean_bneck:>16.4f} J")

    # 2. Sweeping Max Hops H
    hops_list = [1, 2, 3, 5, 7, 9]
    fixed_t = 10
    latencies_h = []
    bottlenecks_h = []

    print(f"\n2. Sweeping Max Hops H (with fixed T = {fixed_t}):")
    print(f"{'H (Max Hops)':<15} | {'Latency (us/call)':<18} | {'Mean Bottleneck (J)':<20}")
    print("-" * 60)

    for H in hops_list:
        call_times = []
        found_bottlenecks = []

        for src in alive_nodes:
            t0 = time.perf_counter()
            bneck, path, _ = dp_time_augmented_lifetime(
                nodes=nodes,
                adj_list=graph.adjacency_list,
                source=src,
                base_station_pos=bs_pos,
                energy_model=energy_model,
                alive_nodes=alive_nodes,
                harvesting_model=harvesting,
                current_time=12,
                max_hops=H,
                time_horizon=fixed_t,
                transmission_range=tx_range
            )
            elapsed = (time.perf_counter() - t0) * 1e6
            call_times.append(elapsed)
            if bneck > 0.0:
                found_bottlenecks.append(bneck)

        mean_time = np.mean(call_times)
        mean_bneck = np.mean(found_bottlenecks) if found_bottlenecks else 0.0
        latencies_h.append(mean_time)
        bottlenecks_h.append(mean_bneck)
        print(f"{H:<15} | {mean_time:>14.2f} us   | {mean_bneck:>16.4f} J")

    # 3. Generate Trade-Off Curves Plot
    os.makedirs('results', exist_ok=True)
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(13, 10))

    # T vs Latency
    ax1.plot(time_horizons, latencies_t, 'b-o', linewidth=2)
    ax1.set_xlabel('Time Horizon (T steps)', fontsize=10)
    ax1.set_ylabel('Execution Time (us)', fontsize=10)
    ax1.set_title('Compute Cost Scaling with Time Horizon T', fontsize=11, fontweight='bold')
    ax1.grid(True, linestyle='--', alpha=0.6)

    # T vs Bottleneck Quality
    ax2.plot(time_horizons, bottlenecks_t, 'g-s', linewidth=2)
    ax2.set_xlabel('Time Horizon (T steps)', fontsize=10)
    ax2.set_ylabel('Mean Bottleneck Energy (J)', fontsize=10)
    ax2.set_title('Routing Bottleneck Quality vs Time Horizon T', fontsize=11, fontweight='bold')
    ax2.grid(True, linestyle='--', alpha=0.6)
    # Sweet spot highlight
    ax2.axvspan(5, 8, color='yellow', alpha=0.25, label='Optimal Trade-off Zone (T=5-8)')
    ax2.legend(loc='lower right', fontsize=9)

    # H vs Latency
    ax3.plot(hops_list, latencies_h, 'm-o', linewidth=2)
    ax3.set_xlabel('Max Hops (H)', fontsize=10)
    ax3.set_ylabel('Execution Time (us)', fontsize=10)
    ax3.set_title('Compute Cost Scaling with Max Hops H', fontsize=11, fontweight='bold')
    ax3.grid(True, linestyle='--', alpha=0.6)

    # H vs Bottleneck Quality
    ax4.plot(hops_list, bottlenecks_h, 'darkorange', marker='^', linewidth=2)
    ax4.set_xlabel('Max Hops (H)', fontsize=10)
    ax4.set_ylabel('Mean Bottleneck Energy (J)', fontsize=10)
    ax4.set_title('Routing Bottleneck Quality vs Max Hops H', fontsize=11, fontweight='bold')
    ax4.grid(True, linestyle='--', alpha=0.6)
    ax4.axvspan(4, 6, color='yellow', alpha=0.25, label='Optimal Trade-off Zone (H=4-6)')
    ax4.legend(loc='lower right', fontsize=9)

    plt.tight_layout()
    filepath = 'results/sensitivity_time_horizon.png'
    plt.savefig(filepath, dpi=150)
    plt.close()
    print(f"\nSaved Sensitivity Analysis trade-off plot to {filepath}")


if __name__ == '__main__':
    run_sensitivity_analysis()
