"""
Test simulation with DP routing enabled.
"""
import sys
sys.path.append('../src')

from simulator import Simulator

def main():
    print("Testing simulation with DP routing enabled...")
    sim = Simulator(
        num_nodes=20,  # smaller for quick test
        area_width=100.0,
        area_height=100.0,
        base_station_pos=(50.0, 50.0),
        initial_energy=2.0,
        desired_clusters_ratio=0.1,
        enable_dp_routing=True,  # Enable DP routing
        max_dp_hops=3,
        routing_algorithm='dijkstra'  # This is ignored when DP is enabled
    )
    sim.run(max_rounds=50)
    print("DP routing simulation completed successfully!")

if __name__ == "__main__":
    main()