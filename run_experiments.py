"""
Comprehensive Experimental Benchmark Suite for WSN Energy Routing

Evaluates 9 configurations across 4 harvesting regimes:
1. Baseline (No Harvesting)
2. Synchronous Solar - Unaware (Dijkstra)
3. Synchronous Solar - Energy-Aware (Energy-Aware Dijkstra)
4. Synchronous Solar - Adaptive (Time-Augmented DP + Harv-CH + DSU)
5. Heterogeneous Shadowed Solar - Unaware (Dijkstra)
6. Heterogeneous Shadowed Solar - Energy-Aware (Energy-Aware Dijkstra)
7. Heterogeneous Shadowed Solar - Adaptive (Time-Augmented DP + Harv-CH + DSU)
8. Stochastic Poisson - Unaware (Dijkstra)
9. Stochastic Poisson - Adaptive (Time-Augmented DP + Harv-CH + DSU)
"""

import sys
import os
sys.path.append('src')

from simulator import Simulator
from visualize import Visualizer, plot_comparison_lifetime


def run_all_experiments():
    print("=" * 75)
    print("WSN ENERGY ROUTING BENCHMARK SUITE (9 CONFIGURATIONS)")
    print("=" * 75)

    num_nodes = 50
    area = 100.0
    bs_pos = (50.0, 50.0)
    init_energy = 0.045  # 45 mJ to observe battery depletion and recharge behavior
    max_capacity = 0.50
    cluster_ratio = 0.08
    max_rounds = 350
    tx_range = 35.0
    seed = 42

    # 1. Baseline: No Energy Harvesting
    print("\n[1/9] Running Baseline (No Harvesting)...")
    sim_baseline = Simulator(
        num_nodes=num_nodes, area_width=area, area_height=area,
        base_station_pos=bs_pos, initial_energy=init_energy,
        max_battery_capacity=max_capacity, desired_clusters_ratio=cluster_ratio,
        enable_dp_routing=False, enable_time_dp=False,
        enable_harvesting_ch=False, enable_live_reroute=False,
        harvesting_profile=None, transmission_range=tx_range, seed=seed
    )
    sim_baseline.run(max_rounds=max_rounds, verbose=False)
    print(f"  Done: FND={sim_baseline.first_node_death_round}, HND={sim_baseline.half_nodes_dead_round}, Alive={sim_baseline.alive_nodes_history[-1]}/{num_nodes}")

    # 2. Solar Synchronous: Unaware Dijkstra
    print("\n[2/9] Running Synchronous Solar - Unaware (Dijkstra)...")
    sim_solar_unaware = Simulator(
        num_nodes=num_nodes, area_width=area, area_height=area,
        base_station_pos=bs_pos, initial_energy=init_energy,
        max_battery_capacity=max_capacity, desired_clusters_ratio=cluster_ratio,
        enable_dp_routing=False, enable_time_dp=False,
        enable_harvesting_ch=False, enable_live_reroute=False,
        harvesting_profile='solar',
        harvesting_kwargs={'peak_rate': 0.0006, 'period': 24, 'day_fraction': 0.5, 'seed': seed},
        routing_algorithm='dijkstra', transmission_range=tx_range, seed=seed
    )
    sim_solar_unaware.run(max_rounds=max_rounds, verbose=False)
    print(f"  Done: FND={sim_solar_unaware.first_node_death_round}, HND={sim_solar_unaware.half_nodes_dead_round}, Alive={sim_solar_unaware.alive_nodes_history[-1]}/{num_nodes}")

    # 3. Solar Synchronous: Energy-Aware Dijkstra
    print("\n[3/9] Running Synchronous Solar - Energy-Aware Dijkstra...")
    sim_solar_energy_dijk = Simulator(
        num_nodes=num_nodes, area_width=area, area_height=area,
        base_station_pos=bs_pos, initial_energy=init_energy,
        max_battery_capacity=max_capacity, desired_clusters_ratio=cluster_ratio,
        enable_dp_routing=False, enable_time_dp=False,
        enable_harvesting_ch=False, enable_live_reroute=False,
        harvesting_profile='solar',
        harvesting_kwargs={'peak_rate': 0.0006, 'period': 24, 'day_fraction': 0.5, 'seed': seed},
        routing_algorithm='energy_dijkstra', transmission_range=tx_range, seed=seed
    )
    sim_solar_energy_dijk.run(max_rounds=max_rounds, verbose=False)
    print(f"  Done: FND={sim_solar_energy_dijk.first_node_death_round}, HND={sim_solar_energy_dijk.half_nodes_dead_round}, Alive={sim_solar_energy_dijk.alive_nodes_history[-1]}/{num_nodes}")

    # 4. Solar Synchronous: Adaptive Time-DP
    print("\n[4/9] Running Synchronous Solar - Adaptive (Time-DP + Harv-CH + DSU)...")
    sim_solar_adaptive = Simulator(
        num_nodes=num_nodes, area_width=area, area_height=area,
        base_station_pos=bs_pos, initial_energy=init_energy,
        max_battery_capacity=max_capacity, desired_clusters_ratio=cluster_ratio,
        enable_dp_routing=True, enable_time_dp=True,
        enable_harvesting_ch=True, enable_live_reroute=True,
        harvesting_profile='solar',
        harvesting_kwargs={'peak_rate': 0.0006, 'period': 24, 'day_fraction': 0.5, 'seed': seed},
        max_dp_hops=5, transmission_range=tx_range, seed=seed
    )
    sim_solar_adaptive.run(max_rounds=max_rounds, verbose=False)
    print(f"  Done: FND={sim_solar_adaptive.first_node_death_round}, HND={sim_solar_adaptive.half_nodes_dead_round}, Alive={sim_solar_adaptive.alive_nodes_history[-1]}/{num_nodes}")

    # 5. Heterogeneous Shadowed Solar: Unaware Dijkstra
    print("\n[5/9] Running Heterogeneous Shadowed - Unaware (Dijkstra)...")
    sim_shadow_unaware = Simulator(
        num_nodes=num_nodes, area_width=area, area_height=area,
        base_station_pos=bs_pos, initial_energy=init_energy,
        max_battery_capacity=max_capacity, desired_clusters_ratio=cluster_ratio,
        enable_dp_routing=False, enable_time_dp=False,
        enable_harvesting_ch=False, enable_live_reroute=False,
        harvesting_profile='shadowed',
        harvesting_kwargs={'peak_rate': 0.0012, 'shadow_fraction': 0.5, 'shadow_penalty': 0.1, 'seed': seed},
        routing_algorithm='dijkstra', transmission_range=tx_range, seed=seed
    )
    sim_shadow_unaware.run(max_rounds=max_rounds, verbose=False)
    print(f"  Done: FND={sim_shadow_unaware.first_node_death_round}, HND={sim_shadow_unaware.half_nodes_dead_round}, Alive={sim_shadow_unaware.alive_nodes_history[-1]}/{num_nodes}")

    # 6. Heterogeneous Shadowed Solar: Energy-Aware Dijkstra
    print("\n[6/9] Running Heterogeneous Shadowed - Energy-Aware Dijkstra...")
    sim_shadow_energy_dijk = Simulator(
        num_nodes=num_nodes, area_width=area, area_height=area,
        base_station_pos=bs_pos, initial_energy=init_energy,
        max_battery_capacity=max_capacity, desired_clusters_ratio=cluster_ratio,
        enable_dp_routing=False, enable_time_dp=False,
        enable_harvesting_ch=False, enable_live_reroute=False,
        harvesting_profile='shadowed',
        harvesting_kwargs={'peak_rate': 0.0012, 'shadow_fraction': 0.5, 'shadow_penalty': 0.1, 'seed': seed},
        routing_algorithm='energy_dijkstra', transmission_range=tx_range, seed=seed
    )
    sim_shadow_energy_dijk.run(max_rounds=max_rounds, verbose=False)
    print(f"  Done: FND={sim_shadow_energy_dijk.first_node_death_round}, HND={sim_shadow_energy_dijk.half_nodes_dead_round}, Alive={sim_shadow_energy_dijk.alive_nodes_history[-1]}/{num_nodes}")

    # 7. Heterogeneous Shadowed Solar: Adaptive Time-DP
    print("\n[7/9] Running Heterogeneous Shadowed - Adaptive (Time-DP + Harv-CH + DSU)...")
    sim_shadow_adaptive = Simulator(
        num_nodes=num_nodes, area_width=area, area_height=area,
        base_station_pos=bs_pos, initial_energy=init_energy,
        max_battery_capacity=max_capacity, desired_clusters_ratio=cluster_ratio,
        enable_dp_routing=True, enable_time_dp=True,
        enable_harvesting_ch=True, enable_live_reroute=True,
        harvesting_profile='shadowed',
        harvesting_kwargs={'peak_rate': 0.0012, 'shadow_fraction': 0.5, 'shadow_penalty': 0.1, 'seed': seed},
        max_dp_hops=5, transmission_range=tx_range, seed=seed
    )
    sim_shadow_adaptive.run(max_rounds=max_rounds, verbose=False)
    print(f"  Done: FND={sim_shadow_adaptive.first_node_death_round}, HND={sim_shadow_adaptive.half_nodes_dead_round}, Alive={sim_shadow_adaptive.alive_nodes_history[-1]}/{num_nodes}")

    # 8. Stochastic Poisson: Unaware Dijkstra
    print("\n[8/9] Running Stochastic Poisson - Unaware (Dijkstra)...")
    sim_stoch_unaware = Simulator(
        num_nodes=num_nodes, area_width=area, area_height=area,
        base_station_pos=bs_pos, initial_energy=init_energy,
        max_battery_capacity=max_capacity, desired_clusters_ratio=cluster_ratio,
        enable_dp_routing=False, enable_time_dp=False,
        enable_harvesting_ch=False, enable_live_reroute=False,
        harvesting_profile='stochastic',
        harvesting_kwargs={'lambda_rate': 2.0, 'quantum': 0.00015, 'seed': seed},
        routing_algorithm='dijkstra', transmission_range=tx_range, seed=seed
    )
    sim_stoch_unaware.run(max_rounds=max_rounds, verbose=False)
    print(f"  Done: FND={sim_stoch_unaware.first_node_death_round}, HND={sim_stoch_unaware.half_nodes_dead_round}, Alive={sim_stoch_unaware.alive_nodes_history[-1]}/{num_nodes}")

    # 9. Stochastic Poisson: Adaptive Time-DP
    print("\n[9/9] Running Stochastic Poisson - Adaptive (Time-DP + Harv-CH + DSU)...")
    sim_stoch_adaptive = Simulator(
        num_nodes=num_nodes, area_width=area, area_height=area,
        base_station_pos=bs_pos, initial_energy=init_energy,
        max_battery_capacity=max_capacity, desired_clusters_ratio=cluster_ratio,
        enable_dp_routing=True, enable_time_dp=True,
        enable_harvesting_ch=True, enable_live_reroute=True,
        harvesting_profile='stochastic',
        harvesting_kwargs={'lambda_rate': 2.0, 'quantum': 0.00015, 'seed': seed},
        max_dp_hops=5, transmission_range=tx_range, seed=seed
    )
    sim_stoch_adaptive.run(max_rounds=max_rounds, verbose=False)
    print(f"  Done: FND={sim_stoch_adaptive.first_node_death_round}, HND={sim_stoch_adaptive.half_nodes_dead_round}, Alive={sim_stoch_adaptive.alive_nodes_history[-1]}/{num_nodes}")

    # Generate plots
    print("\n" + "=" * 75)
    print("Generating Comparative Plots...")
    print("=" * 75)

    comparison_dict = {
        'Baseline (No Harvest)': sim_baseline,
        'Solar (Unaware Dijkstra)': sim_solar_unaware,
        'Solar (Energy-Aware Dijkstra)': sim_solar_energy_dijk,
        'Solar (Adaptive Time-DP)': sim_solar_adaptive,
        'Shadowed (Unaware Dijkstra)': sim_shadow_unaware,
        'Shadowed (Energy-Aware Dijkstra)': sim_shadow_energy_dijk,
        'Shadowed (Adaptive Time-DP)': sim_shadow_adaptive,
        'Stochastic (Unaware Dijkstra)': sim_stoch_unaware,
        'Stochastic (Adaptive Time-DP)': sim_stoch_adaptive,
    }
    plot_comparison_lifetime(comparison_dict, save=True, filename='network_lifetime_comparison.png')

    # Dedicated Heterogeneous Comparison Plot
    shadow_dict = {
        'Shadowed (Unaware Dijkstra)': sim_shadow_unaware,
        'Shadowed (Energy-Aware Dijkstra)': sim_shadow_energy_dijk,
        'Shadowed (Adaptive Time-DP)': sim_shadow_adaptive,
    }
    plot_comparison_lifetime(shadow_dict, save=True, filename='network_lifetime_heterogeneous.png')

    viz_shadow = Visualizer(sim_shadow_adaptive)
    viz_shadow.plot_energy_heatmap_over_time(
        save=True,
        filename='energy_heatmap_heterogeneous.png',
        title='Heterogeneous (Shadowed): Per-Node Residual Energy Heatmap'
    )

    viz_solar = Visualizer(sim_solar_adaptive)
    viz_solar.plot_energy_heatmap_over_time(
        save=True,
        filename='energy_heatmap_solar.png',
        title='Solar Harvesting: Per-Node Residual Energy Heatmap'
    )

    viz_stoch = Visualizer(sim_stoch_adaptive)
    viz_stoch.plot_energy_heatmap_over_time(
        save=True,
        filename='energy_heatmap_stochastic.png',
        title='Stochastic Harvesting: Per-Node Residual Energy Heatmap'
    )

    print("\n=== Comprehensive Results Summary ===")
    header = f"{'Configuration':<38} | {'FND':<8} | {'HND':<8} | {'Alive Nodes':<12} | {'Total Energy (J)':<16}"
    print(header)
    print("-" * len(header))
    for label, sim in comparison_dict.items():
        fnd = str(sim.first_node_death_round or "N/A")
        hnd = str(sim.half_nodes_dead_round or "N/A")
        alive = f"{sim.alive_nodes_history[-1]}/{num_nodes}"
        energy = f"{sim.total_energy_history[-1]:.4f}"
        print(f"{label:<38} | {fnd:<8} | {hnd:<8} | {alive:<12} | {energy:<16}")

    print("\nFinished! Benchmark results saved to results/ directory.")


if __name__ == "__main__":
    run_all_experiments()
