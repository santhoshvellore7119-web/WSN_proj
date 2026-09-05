"""
Wrapper around the existing WSN simulator to provide a clean API interface.
This wrapper does not modify any existing simulator code - it only imports and uses it.
"""
import sys
import os
from typing import Dict, Any, Optional, List
import numpy as np

# Add src directory and project root to path so we can import the simulator modules and run_experiments
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from simulator import Simulator
from visualize import Visualizer

class SimulatorWrapper:
    """
    Wrapper class that provides a clean interface to the existing WSN simulator.
    All simulator code remains untouched in the src/ directory.
    """

    def __init__(self):
        """Initialize the wrapper."""
        pass

    def run_simulation(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a single simulation with the given configuration.

        Args:
            config: Dictionary containing simulation parameters
                   (same as main.py CLI arguments)

        Returns:
            Dictionary containing simulation results and time-series data
        """
        # Extract parameters from config
        num_nodes = config.get('nodes', 50)
        area_width = config.get('area', 100.0)
        area_height = config.get('area', 100.0)
        base_station_pos = (
            config.get('bs_x', 50.0),
            config.get('bs_y', 50.0)
        )
        initial_energy = config.get('init_energy', 1.0)
        max_battery_capacity = config.get('max_capacity', 2.0)
        desired_clusters_ratio = config.get('cluster_ratio', 0.06)
        seed = config.get('seed', 42)

        # Harvesting configuration
        harvesting_profile = config.get('harvesting_profile')
        if harvesting_profile == "none":
            harvesting_profile = None
            harvesting_kwargs = {}
        elif harvesting_profile == "solar":
            harvesting_kwargs = {
                'peak_rate': config.get('solar_peak', 0.03),
                'period': 24,
                'day_fraction': 0.5,
                'seed': seed
            }
        elif harvesting_profile == "stochastic":
            harvesting_kwargs = {
                'lambda_rate': config.get('stoch_lambda', 2.0),
                'quantum': config.get('stoch_quantum', 0.005),
                'seed': seed
            }
        elif harvesting_profile == "constant":
            harvesting_kwargs = {'rate': 0.005}
        else:
            harvesting_profile = None
            harvesting_kwargs = {}

        # Feature toggles
        enable_time_dp = not config.get('disable_time_dp', False)
        enable_harvesting_ch = not config.get('disable_harvesting_ch', False)
        enable_live_reroute = not config.get('disable_live_reroute', False)
        max_dp_hops = config.get('max_dp_hops', 5)
        routing_algorithm = config.get('routing_algorithm', 'dijkstra')

        # Create simulator instance
        sim = Simulator(
            num_nodes=num_nodes,
            area_width=area_width,
            area_height=area_height,
            base_station_pos=base_station_pos,
            initial_energy=initial_energy,
            max_battery_capacity=max_battery_capacity,
            desired_clusters_ratio=desired_clusters_ratio,
            enable_time_dp=enable_time_dp,
            enable_harvesting_ch=enable_harvesting_ch,
            enable_live_reroute=enable_live_reroute,
            harvesting_profile=harvesting_profile,
            harvesting_kwargs=harvesting_kwargs,
            max_dp_hops=max_dp_hops,
            routing_algorithm=routing_algorithm,
            seed=seed
        )

        # Run simulation
        max_rounds = config.get('rounds', 200)
        sim.run(max_rounds=max_rounds, verbose=False)

        # Prepare results
        results = {
            # Summary statistics
            'summary': {
                'completed_rounds': sim.round_number,
                'first_node_death_round': sim.first_node_death_round,
                'half_nodes_dead_round': sim.half_nodes_dead_round,
                'final_alive_nodes': sim.alive_nodes_history[-1] if sim.alive_nodes_history else 0,
                'total_nodes': sim.num_nodes,
                'final_total_energy': sim.total_energy_history[-1] if sim.total_energy_history else 0.0,
                'simulation_time': 0.0  # Would need to track this in simulator
            },

            # Time-series data (sample every N rounds to keep payload manageable)
            'time_series': {
                'rounds': list(range(1, len(sim.alive_nodes_history) + 1)),
                'alive_nodes': sim.alive_nodes_history,
                'total_energy': sim.total_energy_history,
                'harvested_energy': sim.harvested_energy_history,
                'reroute_events': sim.reroute_events_history
            },

            # Detailed data for visualization (sampled)
            'detailed_data': {
                'energy_matrix': sim.energy_matrix,  # [round, node]
                'cluster_heads_history': sim.cluster_heads_history,
                'routes_history': sim.routes_history,
                'node_positions': {
                    str(node_id): {
                        'x': node.x,
                        'y': node.y
                    }
                    for node_id, node in sim.nodes.items()
                },
                'base_station_position': list(base_station_pos)
            },

            # Configuration used
            'configuration': config
        }

        return results

    def run_benchmark(self, num_nodes: int = 50, max_rounds: int = 300, seed: int = 42) -> Dict[str, Any]:
        """
        Run structured comparative benchmark scenarios using core Simulator.
        """
        from datetime import datetime

        scenarios_defs = [
            {
                'id': 'baseline',
                'name': 'Baseline (No Harvesting, LEACH + Dijkstra)',
                'category': 'Baseline',
                'strategy': 'Unaware',
                'kwargs': dict(harvesting_profile=None, enable_time_dp=False, enable_harvesting_ch=False, enable_live_reroute=False)
            },
            {
                'id': 'solar_unaware',
                'name': 'Solar Diurnal — Unaware (LEACH + Dijkstra)',
                'category': 'Synchronous Solar',
                'strategy': 'Unaware',
                'kwargs': dict(harvesting_profile='solar', harvesting_kwargs={'peak_rate': 0.0006, 'period': 24, 'day_fraction': 0.5, 'seed': seed}, enable_time_dp=False, enable_harvesting_ch=False, enable_live_reroute=False)
            },
            {
                'id': 'solar_adaptive',
                'name': 'Solar Diurnal — Adaptive (Time-DP + EH-LEACH + DSU)',
                'category': 'Synchronous Solar',
                'strategy': 'Adaptive (Time-DP + DSU)',
                'kwargs': dict(harvesting_profile='solar', harvesting_kwargs={'peak_rate': 0.0006, 'period': 24, 'day_fraction': 0.5, 'seed': seed}, enable_time_dp=True, enable_harvesting_ch=True, enable_live_reroute=True, max_dp_hops=5)
            },
            {
                'id': 'shadow_unaware',
                'name': 'Canopy Shade — Unaware (LEACH + Dijkstra)',
                'category': 'Shadowed Solar',
                'strategy': 'Unaware',
                'kwargs': dict(harvesting_profile='heterogeneous_shadowed', harvesting_kwargs={'shadow_fraction': 0.4, 'shadow_penalty': 0.1, 'peak_rate': 0.0012, 'seed': seed}, enable_time_dp=False, enable_harvesting_ch=False, enable_live_reroute=False)
            },
            {
                'id': 'shadow_adaptive',
                'name': 'Canopy Shade — Adaptive (Time-DP + EH-LEACH + DSU)',
                'category': 'Shadowed Solar',
                'strategy': 'Adaptive (Time-DP + DSU)',
                'kwargs': dict(harvesting_profile='heterogeneous_shadowed', harvesting_kwargs={'shadow_fraction': 0.4, 'shadow_penalty': 0.1, 'peak_rate': 0.0012, 'seed': seed}, enable_time_dp=True, enable_harvesting_ch=True, enable_live_reroute=True, max_dp_hops=5)
            },
            {
                'id': 'stoch_unaware',
                'name': 'Stochastic Poisson — Unaware (LEACH + Dijkstra)',
                'category': 'Stochastic Poisson',
                'strategy': 'Unaware',
                'kwargs': dict(harvesting_profile='stochastic', harvesting_kwargs={'lambda_rate': 2.0, 'quantum': 0.00015, 'seed': seed}, enable_time_dp=False, enable_harvesting_ch=False, enable_live_reroute=False)
            },
            {
                'id': 'stoch_adaptive',
                'name': 'Stochastic Poisson — Adaptive (Time-DP + EH-LEACH + DSU)',
                'category': 'Stochastic Poisson',
                'strategy': 'Adaptive (Time-DP + DSU)',
                'kwargs': dict(harvesting_profile='stochastic', harvesting_kwargs={'lambda_rate': 2.0, 'quantum': 0.00015, 'seed': seed}, enable_time_dp=True, enable_harvesting_ch=True, enable_live_reroute=True, max_dp_hops=5)
            }
        ]

        scenario_results = []
        for s in scenarios_defs:
            sim = Simulator(
                num_nodes=num_nodes,
                area_width=100.0,
                area_height=100.0,
                initial_energy=0.045,
                max_battery_capacity=0.50,
                desired_clusters_ratio=0.08,
                seed=seed,
                **s['kwargs']
            )
            sim.run(max_rounds=max_rounds, verbose=False)

            scenario_results.append({
                'id': s['id'],
                'name': s['name'],
                'category': s['category'],
                'strategy': s['strategy'],
                'fnd': sim.first_node_death_round,
                'hnd': sim.half_nodes_dead_round,
                'lnd': sim.last_node_death_round,
                'finalAliveNodes': sim.alive_nodes_history[-1] if sim.alive_nodes_history else 0,
                'totalNodes': num_nodes,
                'finalTotalEnergy': round(sim.total_energy_history[-1] if sim.total_energy_history else 0.0, 4),
                'totalHarvested': round(sum(sim.harvested_energy_history), 4),
                'rerouteCount': sum(sim.reroute_events_history),
                'config': s['kwargs'],
                'timeSeriesSummary': {
                    'rounds': list(range(1, len(sim.alive_nodes_history) + 1)),
                    'aliveNodes': sim.alive_nodes_history,
                    'totalEnergy': [round(e, 4) for e in sim.total_energy_history]
                }
            })

        from datetime import timezone
        return {
            'scenarios': scenario_results,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'seed': seed,
            'nodesCount': num_nodes,
            'maxRounds': max_rounds
        }

    def get_simulation_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract a summary from simulation results for storage/display.

        Args:
            results: Full simulation results from run_simulation

        Returns:
            Summary dictionary suitable for database storage
        """
        return results.get('summary', {})

# Example usage (for testing)
if __name__ == "__main__":
    wrapper = SimulatorWrapper()

    # Test configuration
    config = {
        'nodes': 10,
        'rounds': 50,
        'area': 50.0,
        'init_energy': 0.5,
        'max_capacity': 1.0,
        'harvesting_profile': 'solar',
        'solar_peak': 0.01,
        'seed': 42
    }

    results = wrapper.run_simulation(config)
    print(f"Simulation completed: {results['summary']['completed_rounds']} rounds")
    print(f"Final alive nodes: {results['summary']['final_alive_nodes']}/{results['summary']['total_nodes']}")