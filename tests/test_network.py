"""
Quick test for network.py
"""
import sys
sys.path.append('../src')

from network import Node, Graph

def test_node_creation():
    n = Node(0, 0.0, 0.0)
    assert n.node_id == 0
    assert n.x == 0.0
    assert n.y == 0.0
    assert n.residual_energy == 2.0
    assert n.is_alive == True
    print("Node creation: PASS")

def test_distance():
    n1 = Node(0, 0.0, 0.0)
    n2 = Node(1, 3.0, 4.0)
    dist = n1.distance_to(n2)
    assert abs(dist - 5.0) < 1e-9
    print("Distance calculation: PASS")

def test_energy_consumption():
    n = Node(0, 0.0, 0.0, initial_energy=1.0)
    n.consume_energy(0.3)
    assert abs(n.residual_energy - 0.7) < 1e-9
    assert n.is_alive == True
    n.consume_energy(0.8)
    assert abs(n.residual_energy - 0.0) < 1e-9
    assert n.is_alive == False
    print("Energy consumption: PASS")

def test_graph_build():
    nodes = {0: Node(0, 0, 0), 1: Node(1, 1, 0), 2: Node(2, 0, 1)}
    g = Graph(nodes)
    # Check adjacency list entries
    assert len(g.get_neighbors(0)) == 2
    assert len(g.get_neighbors(1)) == 2
    assert len(g.get_neighbors(2)) == 2
    # Check symmetry
    weights_01 = [w for nid, w in g.get_neighbors(0) if nid == 1][0]
    weights_10 = [w for nid, w in g.get_neighbors(1) if nid == 0][0]
    assert abs(weights_01 - weights_10) < 1e-9
    print("Graph building: PASS")

def test_alive_nodes():
    nodes = {0: Node(0, 0, 0), 1: Node(1, 1, 0), 2: Node(2, 0, 1)}
    nodes[1].consume_energy(2.0)  # kill node 1
    g = Graph(nodes)
    alive = g.alive_nodes()
    assert set(alive) == {0, 2}
    print("Alive nodes: PASS")

if __name__ == "__main__":
    test_node_creation()
    test_distance()
    test_energy_consumption()
    test_graph_build()
    test_alive_nodes()
    print("All tests passed!")
