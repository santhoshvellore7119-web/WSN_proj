"""
Quick test for clustering.py
"""
import sys
sys.path.append('../src')

from clustering import leach_clustering, simulate_clustering_round
from network import Node
from energy_model import EnergyModel

def test_leach_clustering_basic():
    # Create 5 nodes in a line
    nodes = {
        0: Node(0, 0, 0),
        1: Node(1, 10, 0),
        2: Node(2, 20, 0),
        3: Node(3, 30, 0),
        4: Node(4, 40, 0)
    }
    # Give them equal energy
    for node in nodes.values():
        node.residual_energy = 1.0

    em = EnergyModel()
    assignment, heads = leach_clustering(nodes, em, desired_clusters_ratio=0.4)  # expect ~2 heads
    # Check that we have some heads
    assert len(heads) > 0
    # Check that each node is assigned to a head (including itself if head)
    for nid in nodes:
        assert nid in assignment
        ch_id = assignment[nid]
        assert ch_id in heads or ch_id == nid  # if node is head, assigns to itself
        # If node is not head, its assigned head should be in heads list
        if nodes[nid].role == 'member':
            assert ch_id in heads
    print("Basic LEACH clustering: PASS")

def test_clustering_with_different_energies():
    nodes = {
        0: Node(0, 0, 0),
        1: Node(1, 10, 0),
        2: Node(2, 20, 0)
    }
    # Node 0 has high energy, others low
    nodes[0].residual_energy = 2.0
    nodes[1].residual_energy = 0.5
    nodes[2].residual_energy = 0.5

    em = EnergyModel()
    assignment, heads = leach_clustering(nodes, em, desired_clusters_ratio=0.33)  # expect 1 head
    # Likely node 0 will be head due to higher energy
    # But due to randomness, we just check that heads are valid
    assert len(heads) > 0
    for nid in heads:
        assert nodes[nid].is_alive
        assert nodes[nid].role == 'CH'
    print("Clustering with different energies: PASS")

def test_all_dead_nodes():
    nodes = {
        0: Node(0, 0, 0),
        1: Node(1, 10, 0)
    }
    nodes[0].consume_energy(2.0)  # kill
    nodes[1].consume_energy(2.0)  # kill

    em = EnergyModel()
    assignment, heads = leach_clustering(nodes, em, desired_clusters_ratio=0.1)
    assert len(heads) == 0
    assert len(assignment) == 0
    print("All dead nodes: PASS")

def test_simulate_clustering_round():
    nodes = {
        0: Node(0, 0, 0),
        1: Node(1, 10, 0),
        2: Node(2, 20, 0)
    }
    for node in nodes.values():
        node.residual_energy = 1.0

    em = EnergyModel()
    assignment, heads, debug = simulate_clustering_round(nodes, em, 0.33)
    assert isinstance(assignment, dict)
    assert isinstance(heads, list)
    assert isinstance(debug, dict)
    assert "alive_nodes" in debug
    print("Simulate clustering round: PASS")

if __name__ == "__main__":
    test_leach_clustering_basic()
    test_clustering_with_different_energies()
    test_all_dead_nodes()
    test_simulate_clustering_round()
    print("All clustering tests passed!")
