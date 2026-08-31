"""
Test the 5-node deterministic counterexample where Classical DP and Energy-Aware Dijkstra
provably fail (routing through dying node) and Time-Augmented DP provably succeeds
(routing through recharging node).
"""

import pytest
import math
from network import Node, Graph
from energy_model import EnergyModel
from harvesting_model import HeterogeneousHarvesting, ConstantHarvesting
from dp_lifetime import dp_lifetime_maximin_path, dp_time_augmented_lifetime
from routing import energy_aware_dijkstra


def test_5node_adversarial_counterexample():
    # Node 0 (Source): (10, 50), E_0 = 0.050 J
    # Node 1 (Relay A - Depleting): (45, 68), E_1 = 0.030 J, Harvest = 0.000 J/step
    # Node 2 (Relay B - Recharging): (45, 32), E_2 = 0.005 J, Harvest = +0.035 J/step
    # Node 3 (Relay C - Buffer): (65, 32), E_3 = 0.050 J, Harvest = +0.010 J/step
    # Base Station (-1): (85, 50)
    tx_range = 48.0

    nodes = {
        0: Node(node_id=0, x=10.0, y=50.0, initial_energy=0.050, max_energy=0.100),
        1: Node(node_id=1, x=45.0, y=68.0, initial_energy=0.030, max_energy=0.100),
        2: Node(node_id=2, x=45.0, y=32.0, initial_energy=0.005, max_energy=0.100),
        3: Node(node_id=3, x=65.0, y=32.0, initial_energy=0.050, max_energy=0.100),
    }

    base_station_pos = (85.0, 50.0)
    energy_model = EnergyModel()
    alive_nodes = {0, 1, 2, 3}

    harvesting = HeterogeneousHarvesting(
        default_profile=ConstantHarvesting(rate=0.0),
        node_profiles={
            0: ConstantHarvesting(rate=0.0),
            1: ConstantHarvesting(rate=0.000),  # Stagnant
            2: ConstantHarvesting(rate=0.035),  # Recharging
            3: ConstantHarvesting(rate=0.010),
        }
    )

    graph = Graph(nodes)
    graph.update_edge_weights(energy_model)

    # 1. Classical Maximin DP
    dp_bottleneck, dp_path = dp_lifetime_maximin_path(
        nodes=nodes,
        adj_list=graph.adjacency_list,
        source=0,
        base_station_pos=base_station_pos,
        energy_model=energy_model,
        alive_nodes=alive_nodes,
        max_hops=4,
        transmission_range=tx_range
    )

    # 2. Energy-Aware Dijkstra
    ea_path, ea_cost = energy_aware_dijkstra(
        nodes=nodes,
        adj_list=graph.adjacency_list,
        start=0,
        base_station_pos=base_station_pos,
        energy_model=energy_model,
        alive_nodes=alive_nodes,
        transmission_range=tx_range
    )

    # 3. Time-Augmented DP
    time_bottleneck, time_path, schedule = dp_time_augmented_lifetime(
        nodes=nodes,
        adj_list=graph.adjacency_list,
        source=0,
        base_station_pos=base_station_pos,
        energy_model=energy_model,
        alive_nodes=alive_nodes,
        harvesting_model=harvesting,
        current_time=0,
        max_hops=4,
        hop_delay=1,
        transmission_range=tx_range
    )

    # Classical DP must choose Path via Node 1 because E1(0) = 0.030 > E2(0) = 0.005
    assert dp_path == [0, 1, -1]
    assert dp_bottleneck == pytest.approx(0.030, rel=1e-3)

    # Energy-Aware Dijkstra penalizes Node 2 due to low initial energy and chooses Node 1
    assert ea_path == [0, 1, -1]

    # Time-Augmented DP correctly projects Node 2's harvest and chooses Path via Node 2!
    assert time_path == [0, 2, -1]
    assert time_bottleneck == pytest.approx(0.040, rel=1e-3)
    assert schedule == [0, 1, 2]
