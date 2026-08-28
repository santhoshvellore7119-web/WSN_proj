"""
Test for routing.py
"""
import sys
sys.path.append('../src')

from routing import dijkstra, astar, compute_routes_for_cluster_heads, compare_dijkstra_astar
from network import Node, Graph
from energy_model import EnergyModel

def test_dijkstra_astar_simple():
    # Create a simple line: 0-1-2-3, with base station at 0
    nodes = {
        0: Node(0, 0, 0),
        1: Node(1, 10, 0),
        2: Node(2, 20, 0),
        3: Node(3, 30, 0)
    }
    # Set energies high enough to be alive
    for node in nodes.values():
        node.residual_energy = 2.0

    graph = Graph(nodes)
    em = EnergyModel()
    graph.update_edge_weights(em)  # sets weights as energy cost between adjacent nodes

    base_station = (0, 0)  # at node 0
    alive = {0, 1, 2, 3}

    # Test from node 3 to base station (should go 3->2->1->0->BS? Actually, our algorithm allows direct to BS from any node)
    # But note: the path may go through other nodes if that is cheaper.
    # Let's compute the cost of direct transmission from node 3 to BS:
    dist_3_bs = nodes[3].distance_to(Node(0,0,0))  # 30m
    cost_direct = em.transmit_energy(1, dist_3_bs)
    # Cost via 3->2->1->0: sum of edges between 3-2, 2-1, 1-0 plus transmit from 0 to BS? Actually, when we reach node 0, we then transmit to BS.
    # So the cost is: (cost 3-2) + (cost 2-1) + (cost 1-0) + (cost from 0 to BS)
    # But note: the edge weights in the graph are the transmission costs between those nodes.
    # So the path cost from 3 to BS via 0 is: dist(3,2) + dist(2,1) + dist(1,0) + dist(0,BS) but note dist(0,BS)=0 because BS is at (0,0) and node0 is at (0,0)? Actually, we placed BS at (0,0) and node0 at (0,0). So cost from 0 to BS is 0.
    # Let's compute using the algorithm.

    print("=== Test Dijkstra and A* on line network ===")
    path_dijk, cost_dijk = dijkstra(nodes, graph.adjacency_list, 3, base_station, em, alive)
    print(f"Dijkstra: path={path_dijk}, cost={cost_dijk}")

    path_astar, cost_astar, expanded = astar(nodes, graph.adjacency_list, 3, base_station, em, alive)
    print(f"A*: path={path_astar}, cost={cost_astar}, expanded={expanded}")

    # They should find the same path (or at least same cost)
    assert cost_dijk == cost_astar, "Costs should be equal"
    print("Costs match: PASS")

    # Test that the path is valid (starts with 3, ends with -1)
    assert path_dijk[0] == 3 and path_dijk[-1] == -1, "Dijkstra path invalid"
    assert path_astar[0] == 3 and path_astar[-1] == -1, "A* path invalid"
    print("Path format: PASS")

    # Test compute_routes_for_cluster_heads
    print("\n=== Test compute_routes_for_cluster_heads ===")
    routes = compute_routes_for_cluster_heads(nodes, graph, em, [1,2,3], base_station, alive, 'dijkstra')
    for ch, (path, cost) in routes.items():
        print(f"CH {ch}: path={path}, cost={cost}")
        assert path is not None and path[0] == ch and path[-1] == -1
    print("Cluster heads routing: PASS")

    # Test comparison function
    print("\n=== Test compare_dijkstra_astar ===")
    comp = compare_dijkstra_astar(nodes, graph, em, [1,2,3], base_station, alive)
    print(f"Dijkstra time: {comp['dijkstra']['time']:.6f}")
    print(f"A* time: {comp['astar']['time']:.6f}")
    print(f"Same path count: {comp['comparison']['same_path_count']}/{comp['comparison']['total_cluster_heads']}")
    # In this simple case, they should find the same paths
    assert comp['comparison']['same_path_count'] == comp['comparison']['total_cluster_heads']
    print("Comparison: PASS")

    print("\nAll routing tests passed!")

if __name__ == "__main__":
    test_dijkstra_astar_simple()
