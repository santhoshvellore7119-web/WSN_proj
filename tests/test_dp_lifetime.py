"""
Test for dp_lifetime.py
"""
import sys
sys.path.append('../src')

from dp_lifetime import dp_lifetime_maximin_path
from network import Node, Graph
from energy_model import EnergyModel

def test_dp_lifetime_simple():
    # Create a simple line: 0-1-2-3, with base station at 0
    nodes = {
        0: Node(0, 0, 0, initial_energy=1.0),
        1: Node(1, 10, 0, initial_energy=0.5),
        2: Node(2, 20, 0, initial_energy=1.5),
        3: Node(3, 30, 0, initial_energy=0.8)
    }
    # Make all alive
    for node in nodes.values():
        node.is_alive = True

    graph = Graph(nodes)
    em = EnergyModel()
    graph.update_edge_weights(em)

    base_station = (0, 0)  # at node 0
    alive = {0, 1, 2, 3}
    source = 3  # node 3

    lifetime, path = dp_lifetime_maximin_path(
        nodes, graph.adjacency_list, source, base_station, em, alive, max_hops=3
    )
    print(f"Lifetime (bottleneck residual energy): {lifetime}")
    print(f"Path: {path}")
    # Expected: the path that maximizes the minimum residual energy.
    # Let's see:
    #   Path 3 -> BS: min(0.8, inf) = 0.8
    #   Path 3 -> 2 -> BS: min(0.8, 1.5, inf) = 0.8
    #   Path 3 -> 2 -> 1 -> BS: min(0.8, 1.5, 0.5, inf) = 0.5
    #   Path 3 -> 2 -> 1 -> 0 -> BS: min(0.8,1.5,0.5,1.0,inf)=0.5
    # So the best is 0.8 (direct or via node 2). Note that residual energy of node 3 is 0.8.
    # The algorithm should return lifetime 0.8 and a path that achieves it.
    # Check that lifetime is 0.8 (or close due to floating point)
    assert abs(lifetime - 0.8) < 1e-9, f"Expected lifetime 0.8, got {lifetime}"
    # Check that path starts with 3 and ends with -1
    assert path[0] == 3 and path[-1] == -1, f"Path should start with 3 and end with -1, got {path}"
    # Check that all nodes in path (except -1) are alive
    for nid in path:
        if nid != -1:
            assert nid in alive, f"Node {nid} in path is not alive"
    print("Simple test: PASS")

def test_dp_lifetime_all_dead_except_source():
    nodes = {
        0: Node(0, 0, 0, initial_energy=1.0),  # BS location
        1: Node(1, 10, 0, initial_energy=0.0), # dead
        2: Node(2, 20, 0, initial_energy=2.0)  # alive
    }
    nodes[0].is_alive = True  # base station is alive? We treat base station as always alive.
    nodes[1].is_alive = False
    nodes[2].is_alive = True

    graph = Graph(nodes)
    em = EnergyModel()
    graph.update_edge_weights(em)

    base_station = (0, 0)
    alive = {0, 2}  # only node 0 and 2 are alive (node 1 dead)
    source = 2

    lifetime, path = dp_lifetime_maximin_path(
        nodes, graph.adjacency_list, source, base_station, em, alive, max_hops=2
    )
    print(f"Lifetime: {lifetime}")
    print(f"Path: {path}")
    # Only possible path: 2 -> BS directly (since node 1 is dead)
    # Lifetime = min(residual_energy[2], inf) = 2.0
    assert abs(lifetime - 2.0) < 1e-9
    assert path == [2, -1]
    print("All dead except source: PASS")

def test_dp_lifetime_no_path():
    nodes = {
        0: Node(0, 0, 0, initial_energy=1.0),
        1: Node(1, 10, 0, initial_energy=1.0)
    }
    # Make node 1 alive
    nodes[1].is_alive = True
    # no edge in graph? Actually, the graph is fully connected, but let's see.
    graph = Graph(nodes)
    em = EnergyModel()
    graph.update_edge_weights(em)

    base_station = (0, 0)  # at node 0
    alive = {1}  # only node 1 alive, node 0 is considered alive? We'll set node 0 alive too.
    # Actually, base station is always considered alive, but in our alive set we include sensor nodes that are alive.
    # We'll set node 0 as alive (it's the base station, but we also have a node object for it).
    nodes[0].is_alive = True
    alive = {0, 1}

    # Now, if we remove the edge? But the graph is fully connected, so there is an edge.
    # Let's instead set max_hops=0, which means we cannot take any hops.
    # Then from source=1, with 0 hops we cannot reach base station (need at least 1 hop).
    source = 1
    lifetime, path = dp_lifetime_maximin_path(
        nodes, graph.adjacency_list, source, base_station, em, alive, max_hops=0
    )
    # Should be no path
    assert lifetime == 0.0
    assert path == []
    print("No path with max_hops=0: PASS")

if __name__ == "__main__":
    test_dp_lifetime_simple()
    test_dp_lifetime_all_dead_except_source()
    test_dp_lifetime_no_path()
    print("\nAll DP lifetime tests passed!")
