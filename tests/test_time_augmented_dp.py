"""
Unit tests for Time-Augmented Dynamic Programming (dp_lifetime.py).
Tests hand-verifiable scenarios, edge cases, and comparisons with classical DP.
"""
import pytest
from network import Node, Graph
from energy_model import EnergyModel
from harvesting_model import ConstantHarvesting, SolarPeriodicHarvesting, HeterogeneousHarvesting
from dp_lifetime import dp_lifetime_maximin_path, dp_time_augmented_lifetime


def test_time_augmented_dp_harvesting_bridge():
    """
    Diamond Graph Verification:
           (Node 1: static 0.4 J, 0 harvest)
          /                                 \\
    Source (1.5 J)                           Base Station (-1)
          \\                                 /
           (Node 2: init 0.1 J, +0.8 J/step harvest)

    - At t=0: Node 1 has 0.4 J, Node 2 has 0.1 J.
    - Path via Node 1 bottleneck = min(1.5, 0.4) = 0.4 J.
    - Path via Node 2 at t=1: Node 2 harvests +0.8 J -> projected 0.9 J.
      Bottleneck = min(1.5, 0.9) = 0.9 J.

    Expected Result:
    - Classical DP picks Node 1 (bottleneck 0.4).
    - Time-Augmented DP picks Node 2 (bottleneck 0.9).
    """
    nodes = {
        0: Node(0, 0, 0, initial_energy=1.5),    # Source
        1: Node(1, 10, 10, initial_energy=0.4),  # Node 1
        2: Node(2, 10, -10, initial_energy=0.1)  # Node 2
    }
    for n in nodes.values():
        n.is_alive = True

    graph = Graph(nodes)
    em = EnergyModel()
    base_station = (20, 0)
    alive = {0, 1, 2}

    # 1. Classical DP without time awareness
    classical_lifetime, classical_path = dp_lifetime_maximin_path(
        nodes, graph.adjacency_list, source=0, base_station_pos=base_station,
        energy_model=em, alive_nodes=alive, max_hops=2, transmission_range=15.0
    )
    assert classical_path == [0, 1, -1]
    assert classical_lifetime == pytest.approx(0.4)

    # 2. Time-Augmented DP with Node 2 harvesting
    het_harvest = HeterogeneousHarvesting(default_profile=ConstantHarvesting(rate=0.0))
    het_harvest.set_node_profile(2, ConstantHarvesting(rate=0.8))

    time_lifetime, time_path, schedule = dp_time_augmented_lifetime(
        nodes, graph.adjacency_list, source=0, base_station_pos=base_station,
        energy_model=em, alive_nodes=alive, harvesting_model=het_harvest,
        current_time=0, max_hops=2, hop_delay=1, transmission_range=15.0
    )

    # Time-augmented DP should route through Node 2
    assert time_path == [0, 2, -1]
    assert time_lifetime == pytest.approx(0.9)
    assert schedule == [0, 1, 2]


def test_time_augmented_dp_dies_before_recharge():
    """
    Edge Case: Node 2 starts with 0.0 J (dead at t=0) and would only harvest later,
    or harvest is delayed until t=5 while packet arrives at t=1.
    Algorithm must NOT route through Node 2 and must choose the reliable alternative.
    """
    nodes = {
        0: Node(0, 0, 0, initial_energy=1.5),
        1: Node(1, 10, 10, initial_energy=0.4),
        2: Node(2, 10, -10, initial_energy=0.05)  # Very low, not enough to survive
    }
    for n in nodes.values():
        n.is_alive = True

    graph = Graph(nodes)
    em = EnergyModel()
    base_station = (20, 0)
    alive = {0, 1, 2}

    # Solar harvest is currently night (0 harvest for next 5 steps)
    solar_night = SolarPeriodicHarvesting(peak_rate=0.5, period=24, day_fraction=0.5)
    # Current time = 18 (night) -> 0 harvest at t=18 and t=19
    time_lifetime, time_path, schedule = dp_time_augmented_lifetime(
        nodes, graph.adjacency_list, source=0, base_station_pos=base_station,
        energy_model=em, alive_nodes=alive, harvesting_model=solar_night,
        current_time=18, max_hops=2, hop_delay=1, transmission_range=15.0
    )

    # At night, Node 2 remains at 0.05 J. Path via Node 1 (0.4 J) is superior.
    assert time_path == [0, 1, -1]
    assert time_lifetime == pytest.approx(0.4)


def test_time_augmented_dp_zero_harvest_equivalence():
    """
    When harvesting rate is 0 everywhere, Time-Augmented DP must produce
    identical bottleneck lifetime and path to Classical DP.
    """
    nodes = {
        0: Node(0, 0, 0, initial_energy=1.2),
        1: Node(1, 10, 0, initial_energy=0.8),
        2: Node(2, 20, 0, initial_energy=1.5),
        3: Node(3, 30, 0, initial_energy=0.6)
    }
    for n in nodes.values():
        n.is_alive = True

    graph = Graph(nodes)
    em = EnergyModel()
    base_station = (0, 0)
    alive = {0, 1, 2, 3}

    classical_lifetime, classical_path = dp_lifetime_maximin_path(
        nodes, graph.adjacency_list, source=3, base_station_pos=base_station,
        energy_model=em, alive_nodes=alive, max_hops=3
    )

    zero_harvest = ConstantHarvesting(rate=0.0)
    time_lifetime, time_path, schedule = dp_time_augmented_lifetime(
        nodes, graph.adjacency_list, source=3, base_station_pos=base_station,
        energy_model=em, alive_nodes=alive, harvesting_model=zero_harvest,
        current_time=0, max_hops=3
    )

    assert time_lifetime == pytest.approx(classical_lifetime)
    assert time_path == classical_path


def test_time_augmented_dp_multi_hop_timeline():
    """
    Test 4-hop linear chain with progressively increasing harvest over time:
    Source(0) -> Node 1 -> Node 2 -> Node 3 -> BS(-1)
    """
    nodes = {
        0: Node(0, 0, 0, initial_energy=2.0),
        1: Node(1, 10, 0, initial_energy=0.1),
        2: Node(2, 20, 0, initial_energy=0.1),
        3: Node(3, 30, 0, initial_energy=0.1)
    }
    for n in nodes.values():
        n.is_alive = True

    # Line graph topology (not fully connected for this test)
    adj = {
        0: [(1, 10.0)],
        1: [(2, 10.0)],
        2: [(3, 10.0)],
        3: []
    }
    em = EnergyModel()
    base_station = (40, 0)
    alive = {0, 1, 2, 3}

    # Constant harvest of 0.3 J per time step
    harvest = ConstantHarvesting(rate=0.3)

    # At t=1, Node 1 has 0.1 + 1*0.3 = 0.4 J
    # At t=2, Node 2 has 0.1 + 2*0.3 = 0.7 J
    # At t=3, Node 3 has 0.1 + 3*0.3 = 1.0 J
    # Bottleneck along chain = min(2.0, 0.4, 0.7, 1.0) = 0.4 J
    lifetime, path, schedule = dp_time_augmented_lifetime(
        nodes, adj, source=0, base_station_pos=base_station,
        energy_model=em, alive_nodes=alive, harvesting_model=harvest,
        current_time=0, max_hops=4, hop_delay=1, transmission_range=15.0
    )

    assert path == [0, 1, 2, 3, -1]
    assert schedule == [0, 1, 2, 3, 4]
    assert lifetime == pytest.approx(0.4)
