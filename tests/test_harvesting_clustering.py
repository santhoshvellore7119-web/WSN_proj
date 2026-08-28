"""
Unit tests for harvesting-aware cluster-head rotation in clustering.py.
"""
import pytest
import random
from network import Node
from energy_model import EnergyModel
from harvesting_model import ConstantHarvesting, HeterogeneousHarvesting
from clustering import leach_clustering, simulate_clustering_round


def test_harvesting_aware_ch_rotation_priority():
    """
    Test scenario:
    - Node 0: current energy 0.3 J, but in high solar harvesting zone (+1.5 J projected)
    - Node 1: current energy 1.0 J, in dark zone (+0.0 J projected)
    - Node 2: current energy 0.2 J, in dark zone (+0.0 J projected)

    Under standard LEACH: Node 1 has highest current energy (1.0 vs 0.3) -> chosen as CH.
    Under Harvesting-Aware LEACH: Node 0 has highest projected energy (0.3 + 1.5 = 1.8 J vs 1.0 J) -> chosen as CH.
    """
    random.seed(42)
    nodes = {
        0: Node(0, 0, 0, initial_energy=0.3, max_energy=2.0),
        1: Node(1, 10, 0, initial_energy=1.0, max_energy=2.0),
        2: Node(2, 20, 0, initial_energy=0.2, max_energy=2.0)
    }
    for n in nodes.values():
        n.is_alive = True

    em = EnergyModel()
    het_harvest = HeterogeneousHarvesting(default_profile=ConstantHarvesting(rate=0.0))
    het_harvest.set_node_profile(0, ConstantHarvesting(rate=1.5))

    # 1. Test candidate priority in min-heap (threshold_multiplier=5.0 forces all nodes to be candidates)
    _, heads_std = leach_clustering(
        nodes, em, desired_clusters_ratio=0.34, threshold_multiplier=5.0, harvesting_model=None
    )
    # Under standard LEACH, highest residual energy is Node 1 (1.0 J)
    assert heads_std == [1]

    _, heads_harv = leach_clustering(
        nodes, em, desired_clusters_ratio=0.34, threshold_multiplier=5.0,
        harvesting_model=het_harvest, current_time=0, lookahead_rounds=1
    )
    # Under harvesting aware LEACH, highest projected energy is Node 0 (1.8 J)
    assert heads_harv == [0]

    # 2. Test statistical frequency over 200 rounds without forcing candidates
    ch_counts = {0: 0, 1: 0, 2: 0}
    for seed in range(200):
        random.seed(seed)
        _, heads = leach_clustering(
            nodes, em, desired_clusters_ratio=0.34,
            harvesting_model=het_harvest, current_time=0, lookahead_rounds=1
        )
        for h in heads:
            ch_counts[h] += 1

    # Node 0 (projected 1.8 J) should be chosen significantly more often than Node 1 (1.0 J)
    assert ch_counts[0] > ch_counts[1] > ch_counts[2]


def test_simulate_clustering_round_harvesting():
    nodes = {i: Node(i, i * 5.0, 0.0, initial_energy=1.5) for i in range(10)}
    em = EnergyModel()
    harvest = ConstantHarvesting(rate=0.05)

    assignment, heads, debug = simulate_clustering_round(
        nodes, em, desired_clusters_ratio=0.2, harvesting_model=harvest, current_time=5
    )

    assert len(heads) == 2
    assert debug['alive_nodes'] == 10
    assert len(assignment) == 10
