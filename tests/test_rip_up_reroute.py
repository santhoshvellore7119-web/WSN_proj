"""
Unit tests for Union-Find and Rip-Up-and-Reroute live fault recovery in routing.py.
"""
import pytest
from network import Node, Graph
from energy_model import EnergyModel
from routing import UnionFind, rip_up_and_reroute


def test_union_find_data_structure():
    uf = UnionFind([0, 1, 2, 3, 4, 5])
    assert not uf.connected(0, 1)

    uf.union(0, 1)
    uf.union(1, 2)
    assert uf.connected(0, 2)
    assert not uf.connected(0, 3)

    uf.union(3, 4)
    assert not uf.connected(2, 4)

    uf.union(2, 3)
    assert uf.connected(0, 4)

    comps = uf.get_components()
    # 0,1,2,3,4 are in one component, 5 is separate
    assert len(comps) == 2


def test_rip_up_and_reroute_detour():
    """
    Test topology:
    Source(0) -> Relay A(1) -> Relay B(2) -> BS(-1)
              -> Relay C(3) -> BS(-1)

    If planned path is [0, 1, 2, -1], and Relay B(2) experiences an unexpected recharge failure,
    rip_up_and_reroute should rip up edge (1 -> 2) and find detour via Node 3: [0, 1, 3, -1]
    or [0, 3, -1].
    """
    nodes = {
        0: Node(0, 0, 0, initial_energy=2.0),
        1: Node(1, 10, 0, initial_energy=1.8),
        2: Node(2, 20, 5, initial_energy=0.0),   # Failed / depleted node
        3: Node(3, 15, -5, initial_energy=1.5),  # Viable alternate neighbor
    }
    for n in nodes.values():
        n.is_alive = True
    nodes[2].is_alive = False  # Mark node 2 as dead/failed

    adj = {
        0: [(1, 10.0), (3, 15.0)],
        1: [(2, 10.0), (3, 10.0)],
        2: [],
        3: []
    }
    em = EnergyModel()
    base_station = (30, 0)
    alive = {0, 1, 3}
    active_path = [0, 1, 2, -1]

    new_path, cost = rip_up_and_reroute(
        nodes=nodes,
        adj_list=adj,
        failed_node_id=2,
        active_path=active_path,
        base_station_pos=base_station,
        energy_model=em,
        alive_nodes=alive,
        transmission_range=16.0
    )

    # Detour should splice Node 3 in place of failed Node 2
    assert new_path == [0, 1, 3, -1]
    assert cost > 0.0
    assert 2 not in new_path


def test_rip_up_and_reroute_direct_bs():
    """
    If u_prev is close enough to BS and node fails, direct transmission to BS is chosen.
    """
    nodes = {
        0: Node(0, 0, 0, initial_energy=2.0),
        1: Node(1, 10, 0, initial_energy=1.8),
        2: Node(2, 20, 0, initial_energy=0.0),  # Failed
    }
    nodes[0].is_alive = True
    nodes[1].is_alive = True
    nodes[2].is_alive = False

    adj = {
        0: [(1, 10.0)],
        1: [(2, 10.0)],
        2: []
    }
    em = EnergyModel()
    base_station = (15, 0)  # Node 1 is only 5m from BS
    alive = {0, 1}
    active_path = [0, 1, 2, -1]

    new_path, cost = rip_up_and_reroute(
        nodes=nodes,
        adj_list=adj,
        failed_node_id=2,
        active_path=active_path,
        base_station_pos=base_station,
        energy_model=em,
        alive_nodes=alive,
        transmission_range=10.0
    )

    assert new_path == [0, 1, -1]
    assert cost > 0.0
