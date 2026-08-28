"""
Main entry point for the WSN Energy-Harvesting Adaptive Routing Protocol simulator.
Supports configurable CLI arguments for customized simulation runs and benchmarking.
"""

import sys
import argparse
import os

# Add src/ to python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from simulator import Simulator
from visualize import Visualizer
from run_experiments import run_all_experiments


def parse_args():
    parser = argparse.ArgumentParser(
        description="WSN Energy-Harvesting Adaptive Routing Protocol Simulator (DSA Project)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("--nodes", type=int, default=50, help="Number of sensor nodes in network")
    parser.add_argument("--rounds", type=int, default=200, help="Maximum simulation rounds")
    parser.add_argument("--area", type=float, default=100.0, help="Field area dimension (width and height in meters)")
    parser.add_argument("--bs-x", type=float, default=50.0, help="Base Station X-coordinate")
    parser.add_argument("--bs-y", type=float, default=50.0, help="Base Station Y-coordinate")
    parser.add_argument("--init-energy", type=float, default=1.0, help="Initial energy per node (Joules)")
    parser.add_argument("--max-capacity", type=float, default=2.0, help="Maximum battery capacity (Joules)")
    parser.add_argument("--cluster-ratio", type=float, default=0.06, help="Target fraction of cluster heads (LEACH p)")
    
    # Harvesting configuration
    parser.add_argument(
        "--harvesting-profile",
        type=str,
        default="solar",
        choices=["none", "constant", "solar", "stochastic"],
        help="Ambient energy harvesting model"
    )
    parser.add_argument("--solar-peak", type=float, default=0.03, help="Solar diurnal peak recharge rate (J/round)")
    parser.add_argument("--stoch-lambda", type=float, default=2.0, help="Poisson arrival rate for stochastic harvesting")
    parser.add_argument("--stoch-quantum", type=float, default=0.005, help="Energy quantum per Poisson arrival (Joules)")

    # Algorithmic switches
    parser.add_argument("--disable-time-dp", action="store_true", help="Disable Time-Augmented DP (use standard Dijkstra)")
    parser.add_argument("--disable-harvesting-ch", action="store_true", help="Disable projected energy in LEACH CH election")
    parser.add_argument("--disable-live-reroute", action="store_true", help="Disable DSU live rip-up and reroute")
    parser.add_argument("--max-dp-hops", type=int, default=5, help="Maximum routing hop horizon (H) for DP")
    parser.add_argument("--routing-algorithm", type=str, default="dijkstra", choices=["dijkstra", "astar"])
    parser.add_argument("--seed", type=int, default=42, help="Random seed for deterministic node deployment")

    # Output options
    parser.add_argument("--visualize", action="store_true", default=True, help="Generate lifetime and heatmap plots")
    parser.add_argument("--benchmark", action="store_true", help="Run full 5-scenario comparative benchmark suite")

    return parser.parse_args()


def main():
    args = parse_args()

    if args.benchmark:
        print("\n>>> Launching Full Multi-Scenario Benchmark Suite...")
        run_all_experiments()
        return

    # Map harvesting parameters
    harv_profile = None if args.harvesting_profile == "none" else args.harvesting_profile
    harv_kwargs = {}
    if harv_profile == "solar":
        harv_kwargs = {'peak_rate': args.solar_peak, 'period': 24, 'day_fraction': 0.5, 'seed': args.seed}
    elif harv_profile == "stochastic":
        harv_kwargs = {'lambda_rate': args.stoch_lambda, 'quantum': args.stoch_quantum, 'seed': args.seed}
    elif harv_profile == "constant":
        harv_kwargs = {'rate': 0.005}

    print("=" * 65)
    print("WSN Energy-Harvesting Adaptive Routing Simulation")
    print("=" * 65)

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
        print("\nGenerating visualization figures...")
        viz = Visualizer(sim)
        viz.plot_network_lifetime(save=True, filename="network_lifetime.png")
        if sim.energy_matrix:
            viz.plot_energy_heatmap_over_time(save=True, filename="energy_heatmap.png")
        if sim.alive_nodes_history:
            num_rounds = len(sim.alive_nodes_history)
            for r in [1, max(1, num_rounds // 2), num_rounds]:
                viz.plot_routing_tree(r, save=True)
        print("Visualizations saved to results/ directory.")


if __name__ == "__main__":
    main()