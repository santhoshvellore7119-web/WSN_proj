"""
Unit tests for Energy-Aware Dijkstra baseline algorithm.
"""

import pytest
from network import Node, Graph
from energy_model import EnergyModel
from routing import dijkstra, energy_aware_dijkstra


def test_energy_aware_dijkstra_avoids_depleted_node():
    # Node 0 (Source) at (0, 0), Node 1 (Low Energy) at (10, 0), Node 2 (High Energy) at (10, 10), BS at (20, 0)
    nodes = {
        0: Node(node_id=0, x=0.0, y=0.0, initial_energy=1.0, max_energy=1.0),
        1: Node(node_id=1, x=10.0, y=0.0, initial_energy=0.01, max_energy=1.0),  # Critically low energy
        2: Node(node_id=2, x=10.0, y=8.0, initial_energy=0.95, max_energy=1.0),  # Plentiful energy
    }
    # Set residual energy
    nodes[1].residual_energy = 0.005
    nodes[2].residual_energy = 0.950

    base_station_pos = (20.0, 0.0)
    tx_range = 15.0
    energy_model = EnergyModel()
    alive_nodes = {0, 1, 2}

    graph = Graph(nodes)
    graph.update_edge_weights(energy_model)

    # Standard Dijkstra: picks shortest geometric distance path (0 -> 1 -> -1)
    std_path, _ = dijkstra(
        nodes=nodes,
        adj_list=graph.adjacency_list,
        start=0,
        base_station_pos=base_station_pos,
        energy_model=energy_model,
        alive_nodes=alive_nodes,
        transmission_range=tx_range
    )
    assert std_path == [0, 1, -1]

    # Energy-Aware Dijkstra: penalizes Node 1 and diverts through Node 2 (0 -> 2 -> -1)
    ea_path, _ = energy_aware_dijkstra(
        nodes=nodes,
        adj_list=graph.adjacency_list,
        start=0,
        base_station_pos=base_station_pos,
        energy_model=energy_model,
        alive_nodes=alive_nodes,
        alpha=2.0,
        transmission_range=tx_range
    )
    assert ea_path == [0, 2, -1]
