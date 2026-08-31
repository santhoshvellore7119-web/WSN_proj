"""
Unit test for DSU live detour rerouting and benchmark utility.
"""

import pytest
from network import Node, Graph
from energy_model import EnergyModel
from routing import rip_up_and_reroute, benchmark_dsu_vs_recompute


def test_dsu_live_detour_local_bridge():
    # Topology: 0 -> 1 -> 2 -> -1
    # Alternate bridge node 3 connects 0 to 2
    nodes = {
        0: Node(node_id=0, x=0.0, y=10.0, initial_energy=1.0),
        1: Node(node_id=1, x=10.0, y=10.0, initial_energy=0.0),  # Dead node
        2: Node(node_id=2, x=20.0, y=10.0, initial_energy=1.0),
        3: Node(node_id=3, x=10.0, y=0.0, initial_energy=1.0),   # Detour bridge
    }
    nodes[1].residual_energy = 0.0  # Node 1 fails

    base_station_pos = (30.0, 10.0)
    tx_range = 16.0
    energy_model = EnergyModel()
    alive_nodes = {0, 2, 3}

    graph = Graph(nodes)
    graph.update_edge_weights(energy_model)

    active_path = [0, 1, 2, -1]

    new_path, total_cost = rip_up_and_reroute(
        nodes=nodes,
        adj_list=graph.adjacency_list,
        failed_node_id=1,
        active_path=active_path,
        base_station_pos=base_station_pos,
        energy_model=energy_model,
        alive_nodes=alive_nodes,
        transmission_range=tx_range
    )

    # Detour must bridge around 1 through 3 to reach 2 and then BS
    assert new_path == [0, 3, 2, -1]
    assert total_cost > 0.0
