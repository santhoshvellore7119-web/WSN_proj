"""
Example script to run a single simulation with solar harvesting and plot results.
"""
import sys
sys.path.append('src')

from simulator import Simulator
from visualize import Visualizer


def main():
    print("Running WSN Energy-Harvesting Simulation (Solar + Time-Augmented DP)")
    print("-" * 65)

    sim = Simulator(
        num_nodes=50,
        area_width=100.0,
        area_height=100.0,
        base_station_pos=(50.0, 50.0),
        initial_energy=1.0,
        max_battery_capacity=2.0,
        desired_clusters_ratio=0.06,
        enable_time_dp=True,
        enable_harvesting_ch=True,
        enable_live_reroute=True,
        harvesting_profile='solar',
        harvesting_kwargs={'peak_rate': 0.03, 'period': 24, 'day_fraction': 0.5},
        max_dp_hops=5,
        routing_algorithm='dijkstra'
    )

    sim.run(max_rounds=200)

    print("\nGenerating output plots...")
    viz = Visualizer(sim)
    viz.plot_network_lifetime()
    viz.plot_energy_heatmap_over_time(save=True, filename='energy_heatmap.png')

    if sim.alive_nodes_history:
        num_rounds = len(sim.alive_nodes_history)
        rounds_to_plot = sorted(list(set([1, min(50, num_rounds), min(100, num_rounds), num_rounds])))
        for r in rounds_to_plot:
            viz.plot_routing_tree(r, save=True)

    print("Done! Plots saved to results/ folder.")


if __name__ == "__main__":
    main()