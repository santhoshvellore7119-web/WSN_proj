"""
Test the simulator wrapper directly.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from core.simulator_wrapper import SimulatorWrapper

def test_simulator_wrapper():
    """Test the simulator wrapper with a simple configuration."""
    wrapper = SimulatorWrapper()

    config = {
        'nodes': 5,
        'rounds': 10,
        'area': 50.0,
        'init_energy': 0.5,
        'max_capacity': 1.0,
        'harvesting_profile': 'solar',
        'solar_peak': 0.01,
        'seed': 42
    }

    print("Testing simulator wrapper...")
    results = wrapper.run_simulation(config)

    print(f"Simulation completed:")
    print(f"  Rounds: {results['summary']['completed_rounds']}")
    print(f"  Final alive nodes: {results['summary']['final_alive_nodes']}/{results['summary']['total_nodes']}")
    print(f"  Final energy: {results['summary']['final_total_energy']:.4f} J")

    # Check that we have time-series data
    assert 'time_series' in results
    assert len(results['time_series']['rounds']) == results['summary']['completed_rounds']
    assert len(results['time_series']['alive_nodes']) == results['summary']['completed_rounds']
    assert len(results['time_series']['total_energy']) == results['summary']['completed_rounds']

    # Check that we have detailed data
    assert 'detailed_data' in results
    assert 'energy_matrix' in results['detailed_data']
    assert 'cluster_heads_history' in results['detailed_data']
    assert 'routes_history' in results['detailed_data']
    assert 'node_positions' in results['detailed_data']
    assert 'base_station_position' in results['detailed_data']

    print("All tests passed!")
    return True

if __name__ == "__main__":
    test_simulator_wrapper()