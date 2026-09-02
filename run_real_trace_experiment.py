"""
Real Solar Trace Replay Experiment

Replays real empirical solar irradiance traces (calibrated from NREL NSRDB data)
across 3 distinct weather profiles:
1. Clear Sky (smooth daytime peak)
2. Cloudy Intermittent (sudden cloud attenuation dips)
3. Overcast (attenuated diffuse daylight)

Validates Time-Augmented DP under empirical weather conditions.
"""

import sys
import os
import matplotlib.pyplot as plt
import numpy as np

sys.path.append('src')

from simulator import Simulator


def run_real_trace_benchmark():
    print("=" * 78)
    print("REAL SOLAR TRACE REPLAY: EMPIRICAL WEATHER BENCHMARK")
    print("=" * 78)

    num_nodes = 50
    area = 100.0
    bs_pos = (50.0, 50.0)
    init_energy = 0.045
    max_cap = 0.50
    cluster_ratio = 0.08
    max_rounds = 350
    tx_range = 35.0
    seed = 42

    weather_profiles = ['clear_sky', 'cloudy_intermittent', 'overcast']
    summary_results = {}

    for weather in weather_profiles:
        print(f"\n--- Testing Empirical Weather Profile: {weather.upper()} ---")

        # 1. Unaware Baseline
        sim_unaware = Simulator(
            num_nodes=num_nodes,
            area_width=area,
            area_height=area,
            base_station_pos=bs_pos,
            initial_energy=init_energy,
            max_battery_capacity=max_cap,
            desired_clusters_ratio=cluster_ratio,
            enable_dp_routing=False,
            enable_time_dp=False,
            enable_harvesting_ch=False,
            harvesting_profile='real_trace',
            harvesting_kwargs={'trace_name': weather, 'peak_rate': 0.0012, 'solar_noise': 0.05, 'seed': seed},
            transmission_range=tx_range,
            seed=seed
        )
        sim_unaware.run(max_rounds=max_rounds, verbose=False)

        # 2. Time-Augmented DP
        sim_timedp = Simulator(
            num_nodes=num_nodes,
            area_width=area,
            area_height=area,
            base_station_pos=bs_pos,
            initial_energy=init_energy,
            max_battery_capacity=max_cap,
            desired_clusters_ratio=cluster_ratio,
            enable_dp_routing=True,
            enable_time_dp=True,
            enable_harvesting_ch=True,
            enable_live_reroute=True,
            harvesting_profile='real_trace',
            harvesting_kwargs={'trace_name': weather, 'peak_rate': 0.0012, 'solar_noise': 0.05, 'seed': seed},
            transmission_range=tx_range,
            seed=seed
        )
        sim_timedp.run(max_rounds=max_rounds, verbose=False)

        fnd_u = sim_unaware.first_node_death_round or max_rounds + 1
        fnd_dp = sim_timedp.first_node_death_round or max_rounds + 1
        alive_u = sim_unaware.alive_nodes_history[-1]
        alive_dp = sim_timedp.alive_nodes_history[-1]
        energy_u = sim_unaware.total_energy_history[-1]
        energy_dp = sim_timedp.total_energy_history[-1]

        summary_results[weather] = {
            'unaware': {'fnd': fnd_u, 'alive': alive_u, 'energy': energy_u, 'history': sim_unaware.alive_nodes_history},
            'timedp': {'fnd': fnd_dp, 'alive': alive_dp, 'energy': energy_dp, 'history': sim_timedp.alive_nodes_history}
        }

        print(f"  Unaware: FND={fnd_u:>3}, Alive={alive_u:>2}/50, Residual Energy={energy_u:.4f} J")
        print(f"  Time-DP: FND={fnd_dp:>3}, Alive={alive_dp:>2}/50, Residual Energy={energy_dp:.4f} J")

    # Generate Comparison Plot
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey=True)

    titles = {
        'clear_sky': 'Clear Sky (Smooth Solar Curve)',
        'cloudy_intermittent': 'Cloudy Intermittent (Variable Dips)',
        'overcast': 'Overcast (Low Diffuse Solar)'
    }

    for idx, weather in enumerate(weather_profiles):
        ax = axes[idx]
        u_hist = summary_results[weather]['unaware']['history']
        dp_hist = summary_results[weather]['timedp']['history']

        ax.plot(u_hist, label='Unaware LEACH + Dijkstra', color='#e53e3e', linestyle='--', linewidth=2)
        ax.plot(dp_hist, label='Time-Augmented DP', color='#3182ce', linewidth=2.5)
        ax.set_title(titles[weather], fontsize=11, fontweight='bold')
        ax.set_xlabel('Simulation Round', fontsize=10)
        if idx == 0:
            ax.set_ylabel('Active Sensor Nodes', fontsize=11)
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.legend(loc='lower left', fontsize=9)
        ax.set_ylim(-2, 53)

    plt.tight_layout()
    os.makedirs('results', exist_ok=True)
    plot_path = os.path.join('results', 'real_trace_comparison.png')
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"\nSaved real trace comparison plot to: {plot_path}")


if __name__ == '__main__':
    run_real_solar_trace_benchmark = run_real_trace_benchmark
    run_real_trace_benchmark()
