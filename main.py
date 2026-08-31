"""
Command-line interface for the WSN Energy-Harvesting Routing Simulator.
"""

import sys
import argparse
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from simulator import Simulator
from visualize import Visualizer
from run_experiments import run_all_experiments


def parse_args():
    parser = argparse.ArgumentParser(
        description="WSN Energy Routing Simulator (LEACH + Time-Augmented DP)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("--nodes", type=int, default=50, help="Number of sensor nodes")
    parser.add_argument("--rounds", type=int, default=200, help="Maximum rounds to simulate")
    parser.add_argument("--area", type=float, default=100.0, help="Field dimension (width & height in meters)")
    parser.add_argument("--bs-x", type=float, default=50.0, help="Base Station X position")
    parser.add_argument("--bs-y", type=float, default=50.0, help="Base Station Y position")
    parser.add_argument("--init-energy", type=float, default=1.0, help="Initial energy per node (Joules)")
    parser.add_argument("--max-capacity", type=float, default=2.0, help="Max battery capacity (Joules)")
    parser.add_argument("--cluster-ratio", type=float, default=0.06, help="Target cluster ratio (LEACH p)")

    # Harvesting configuration
    parser.add_argument(
        "--harvesting-profile",
        type=str,
        default="solar",
        choices=["none", "constant", "solar", "stochastic", "shadowed", "hotspot"],
        help="Energy harvesting profile"
    )
    parser.add_argument("--solar-peak", type=float, default=0.03, help="Solar peak recharge rate (J/round)")
    parser.add_argument("--stoch-lambda", type=float, default=2.0, help="Poisson lambda parameter")
    parser.add_argument("--stoch-quantum", type=float, default=0.005, help="Energy per Poisson arrival (Joules)")

    # Feature toggles
    parser.add_argument("--disable-time-dp", action="store_true", help="Use standard shortest-path routing instead of Time-DP")
    parser.add_argument("--disable-harvesting-ch", action="store_true", help="Disable harvest-weighted cluster head rotation")
    parser.add_argument("--disable-live-reroute", action="store_true", help="Disable DSU live rerouting")
    parser.add_argument("--max-dp-hops", type=int, default=5, help="Max hop horizon for DP")
    parser.add_argument("--routing-algorithm", type=str, default="dijkstra", choices=["dijkstra", "astar", "energy_dijkstra"])
    parser.add_argument("--seed", type=int, default=42, help="Random seed for node positions")

    # Outputs
    parser.add_argument("--visualize", action="store_true", default=True, help="Generate plots after simulation")
    parser.add_argument("--benchmark", action="store_true", help="Run comparative 5-scenario benchmark")

    return parser.parse_args()


def main():
    args = parse_args()

    if args.benchmark:
        print("\nStarting benchmark suite...")
        run_all_experiments()
        return

    harv_profile = None if args.harvesting_profile == "none" else args.harvesting_profile
    harv_kwargs = {}
    if harv_profile == "solar":
        harv_kwargs = {'peak_rate': args.solar_peak, 'period': 24, 'day_fraction': 0.5, 'seed': args.seed}
    elif harv_profile == "shadowed":
        harv_kwargs = {'peak_rate': args.solar_peak, 'shadow_fraction': 0.5, 'shadow_penalty': 0.1, 'seed': args.seed}
    elif harv_profile == "hotspot":
        harv_kwargs = {'hotspot_center': (args.area * 0.75, args.area * 0.75), 'hotspot_radius': args.area * 0.35, 'hotspot_rate': 0.0015}
    elif harv_profile == "stochastic":
        harv_kwargs = {'lambda_rate': args.stoch_lambda, 'quantum': args.stoch_quantum, 'seed': args.seed}
    elif harv_profile == "constant":
        harv_kwargs = {'rate': 0.005}

    print("=" * 60)
    print("WSN Energy-Harvesting Routing Simulation")
    print("=" * 60)

    sim = Simulator(
        num_nodes=args.nodes,
        area_width=args.area,
        area_height=args.area,
        base_station_pos=(args.bs_x, args.bs_y),
        initial_energy=args.init_energy,
        max_battery_capacity=args.max_capacity,
        desired_clusters_ratio=args.cluster_ratio,
        enable_time_dp=not args.disable_time_dp,
        enable_harvesting_ch=not args.disable_harvesting_ch,
        enable_live_reroute=not args.disable_live_reroute,
        harvesting_profile=harv_profile,
        harvesting_kwargs=harv_kwargs,
        max_dp_hops=args.max_dp_hops,
        routing_algorithm=args.routing_algorithm,
        seed=args.seed
    )

    sim.run(max_rounds=args.rounds, verbose=True)

    if args.visualize:
        print("\nGenerating figures...")
        viz = Visualizer(sim)
        viz.plot_network_lifetime(save=True, filename="network_lifetime.png")
        if sim.energy_matrix:
            viz.plot_energy_heatmap_over_time(save=True, filename="energy_heatmap.png")
        if sim.alive_nodes_history:
            num_rounds = len(sim.alive_nodes_history)
            for r in [1, max(1, num_rounds // 2), num_rounds]:
                viz.plot_routing_tree(r, save=True)
        print("Done! Plots saved to results/ directory.")


if __name__ == "__main__":
    main()