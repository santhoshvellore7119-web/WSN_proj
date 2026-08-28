"""
Comparison Experiments Runner for WSN Energy-Aware Routing Protocols.

Runs multi-profile simulations to demonstrate the effectiveness of:
1. Baseline LEACH + Dijkstra (No energy harvesting)
2. Harvesting-Unaware LEACH + Dijkstra (Passive harvesting without algorithmic awareness)
3. Novel Harvesting-Aware Adaptive Routing (Harvesting-Aware CH + Time-Augmented DP + DSU Rip-Up/Reroute)

Evaluates performance across:
- Periodic Solar-Cycle Harvesting (Diurnal day/night sinusoidal model)
- Stochastic Poisson-Arrival Harvesting (Discrete random energy quantum arrivals)

Outputs:
- results/network_lifetime_comparison.png
- results/energy_heatmap_solar.png
- results/energy_heatmap_stochastic.png
- results/network_lifetime.png
- results/routing_tree_round_*.png
"""

import sys
import os
sys.path.append('src')

from simulator import Simulator
from visualize import Visualizer, plot_comparison_lifetime


def run_all_experiments():
    print("=" * 70)
    print("WSN Energy-Harvesting Adaptive Routing: Comparison Experiments")
    print("=" * 70)

    # Common parameters for fair side-by-side comparison
    num_nodes = 50
    area = 100.0
    bs_pos = (50.0, 50.0)
    init_energy = 0.045  # 45 mJ initial energy to observe depletion and recharge dynamics
    max_capacity = 0.50
    cluster_ratio = 0.08
    max_rounds = 350
    seed = 42

    # -------------------------------------------------------------
    # 1. Baseline: No Energy Harvesting (Standard LEACH + Dijkstra)
    # -------------------------------------------------------------
    print("\n[1/5] Running Baseline (No Harvesting, LEACH + Dijkstra)...")
    sim_baseline = Simulator(
        num_nodes=num_nodes,
        area_width=area,
        area_height=area,
        base_station_pos=bs_pos,
        initial_energy=init_energy,
        max_battery_capacity=max_capacity,
        desired_clusters_ratio=cluster_ratio,
        enable_dp_routing=False,
        enable_time_dp=False,
        enable_harvesting_ch=False,
        enable_live_reroute=False,
        harvesting_profile=None,
        seed=seed
    )
    sim_baseline.run(max_rounds=max_rounds, verbose=False)
    print(f"  -> Baseline finished: FND={sim_baseline.first_node_death_round}, HND={sim_baseline.half_nodes_dead_round}, Final Alive={sim_baseline.alive_nodes_history[-1]}/{num_nodes}")

    # -------------------------------------------------------------
    # 2. Solar Harvesting: Unaware (LEACH + Dijkstra)
    # -------------------------------------------------------------
    print("\n[2/5] Running Solar Harvesting - Unaware (Standard LEACH + Dijkstra)...")
    sim_solar_unaware = Simulator(
        num_nodes=num_nodes,
        area_width=area,
        area_height=area,
        base_station_pos=bs_pos,
        initial_energy=init_energy,
        max_battery_capacity=max_capacity,
        desired_clusters_ratio=cluster_ratio,
        enable_dp_routing=False,
        enable_time_dp=False,
        enable_harvesting_ch=False,
        enable_live_reroute=False,
        harvesting_profile='solar',
        harvesting_kwargs={'peak_rate': 0.0006, 'period': 24, 'day_fraction': 0.5, 'seed': seed},
        seed=seed
    )
    sim_solar_unaware.run(max_rounds=max_rounds, verbose=False)
    print(f"  -> Solar Unaware finished: FND={sim_solar_unaware.first_node_death_round}, HND={sim_solar_unaware.half_nodes_dead_round}, Final Alive={sim_solar_unaware.alive_nodes_history[-1]}/{num_nodes}")

    # -------------------------------------------------------------
    # 3. Solar Harvesting: Novel Adaptive Routing (Time-DP + Harv-CH + DSU)
    # -------------------------------------------------------------
    print("\n[3/5] Running Solar Harvesting - Novel Adaptive (Time-Augmented DP + Harv-CH + DSU Reroute)...")
    sim_solar_adaptive = Simulator(
        num_nodes=num_nodes,
        area_width=area,
        area_height=area,
        base_station_pos=bs_pos,
        initial_energy=init_energy,
        max_battery_capacity=max_capacity,
        desired_clusters_ratio=cluster_ratio,
        enable_dp_routing=False,
        enable_time_dp=True,
        enable_harvesting_ch=True,
        enable_live_reroute=True,
        harvesting_profile='solar',
        harvesting_kwargs={'peak_rate': 0.0006, 'period': 24, 'day_fraction': 0.5, 'seed': seed},
        max_dp_hops=5,
        seed=seed
    )
    sim_solar_adaptive.run(max_rounds=max_rounds, verbose=False)
    print(f"  -> Solar Adaptive finished: FND={sim_solar_adaptive.first_node_death_round}, HND={sim_solar_adaptive.half_nodes_dead_round}, Final Alive={sim_solar_adaptive.alive_nodes_history[-1]}/{num_nodes}")

    # -------------------------------------------------------------
    # 4. Stochastic Poisson Harvesting: Unaware (LEACH + Dijkstra)
    # -------------------------------------------------------------
    print("\n[4/5] Running Stochastic Harvesting - Unaware (Standard LEACH + Dijkstra)...")
    sim_stoch_unaware = Simulator(
        num_nodes=num_nodes,
        area_width=area,
        area_height=area,
        base_station_pos=bs_pos,
        initial_energy=init_energy,
        max_battery_capacity=max_capacity,
        desired_clusters_ratio=cluster_ratio,
        enable_dp_routing=False,
        enable_time_dp=False,
        enable_harvesting_ch=False,
        enable_live_reroute=False,
        harvesting_profile='stochastic',
        harvesting_kwargs={'lambda_rate': 2.0, 'quantum': 0.00015, 'seed': seed},
        seed=seed
    )
    sim_stoch_unaware.run(max_rounds=max_rounds, verbose=False)
    print(f"  -> Stochastic Unaware finished: FND={sim_stoch_unaware.first_node_death_round}, HND={sim_stoch_unaware.half_nodes_dead_round}, Final Alive={sim_stoch_unaware.alive_nodes_history[-1]}/{num_nodes}")

    # -------------------------------------------------------------
    # 5. Stochastic Poisson Harvesting: Novel Adaptive Routing
    # -------------------------------------------------------------
    print("\n[5/5] Running Stochastic Harvesting - Novel Adaptive (Time-Augmented DP + Harv-CH + DSU Reroute)...")
    sim_stoch_adaptive = Simulator(
        num_nodes=num_nodes,
        area_width=area,
        area_height=area,
        base_station_pos=bs_pos,
        initial_energy=init_energy,
        max_battery_capacity=max_capacity,
        desired_clusters_ratio=cluster_ratio,
        enable_dp_routing=False,
        enable_time_dp=True,
        enable_harvesting_ch=True,
        enable_live_reroute=True,
        harvesting_profile='stochastic',
        harvesting_kwargs={'lambda_rate': 2.0, 'quantum': 0.00015, 'seed': seed},
        max_dp_hops=5,
        seed=seed
    )
    sim_stoch_adaptive.run(max_rounds=max_rounds, verbose=False)
    print(f"  -> Stochastic Adaptive finished: FND={sim_stoch_adaptive.first_node_death_round}, HND={sim_stoch_adaptive.half_nodes_dead_round}, Final Alive={sim_stoch_adaptive.alive_nodes_history[-1]}/{num_nodes}")

    # -------------------------------------------------------------
    # Visualization and Output Generation
    # -------------------------------------------------------------
    print("\n" + "=" * 70)
    print("Generating Comparative Plots and Heatmaps...")
    print("=" * 70)

    # 1. Comparative Multi-Curve Lifetime Plot
    comparison_dict = {
        'Baseline (No Harvest)': sim_baseline,
        'Solar (Unaware LEACH)': sim_solar_unaware,
        'Solar (Adaptive Time-DP)': sim_solar_adaptive,
        'Stochastic (Unaware LEACH)': sim_stoch_unaware,
        'Stochastic (Adaptive Time-DP)': sim_stoch_adaptive
    }
    plot_comparison_lifetime(comparison_dict, save=True, filename='network_lifetime_comparison.png')

    # 2. 2D Spatiotemporal Heatmap for Solar Periodic Profile
    viz_solar = Visualizer(sim_solar_adaptive)
    viz_solar.plot_energy_heatmap_over_time(
        save=True,
        filename='energy_heatmap_solar.png',
        title='Solar Diurnal Periodic Harvesting: Node Energy Heatmap over Rounds'
    )

    # 3. 2D Spatiotemporal Heatmap for Stochastic Poisson Profile
    viz_stoch = Visualizer(sim_stoch_adaptive)
    viz_stoch.plot_energy_heatmap_over_time(
        save=True,
        filename='energy_heatmap_stochastic.png',
        title='Stochastic Poisson Harvesting: Node Energy Heatmap over Rounds'
    )

    # 4. Standard Lifetime and Topology plots for the Solar Adaptive run
    viz_solar.plot_network_lifetime(save=True, filename='network_lifetime.png')
    for r in [1, 50, 100, min(200, len(sim_solar_adaptive.alive_nodes_history))]:
        viz_solar.plot_routing_tree(r, save=True)

    print("\n=== Summary Table ===")
    print(f"{'Configuration':<35} | {'FND':<8} | {'HND':<8} | {'Final Alive':<12} | {'Final Energy (J)':<15}")
    print("-" * 88)
    for label, sim in comparison_dict.items():
        fnd = str(sim.first_node_death_round or "N/A")
        hnd = str(sim.half_nodes_dead_round or "N/A")
        alive = f"{sim.alive_nodes_history[-1]}/{num_nodes}"
        energy = f"{sim.total_energy_history[-1]:.4f}"
        print(f"{label:<35} | {fnd:<8} | {hnd:<8} | {alive:<12} | {energy:<15}")

    print("\nExperiment run complete! All plots saved to results/ directory.")


if __name__ == "__main__":
    run_all_experiments()
