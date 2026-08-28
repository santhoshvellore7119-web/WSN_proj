"""
Network topology and node representation for WSN simulation.
"""

import math
from typing import Dict, List, Tuple, Optional


class Node:
    """Represents a sensor node with position, battery state, and cluster role."""

    def __init__(
        self,
        node_id: int,
        x: float,
        y: float,
        initial_energy: float = 2.0,
        max_energy: Optional[float] = None
    ):
        self.node_id = node_id
        self.x = x
        self.y = y
        self.initial_energy = initial_energy
        self.max_energy = max_energy if max_energy is not None else max(initial_energy, 2.0)
        self.residual_energy = min(initial_energy, self.max_energy)
        self.role = 'member'  # 'CH' or 'member'
        self.cluster_id = -1
        self.is_alive = self.residual_energy > 0.0
        self.total_harvested_energy = 0.0
        self.total_consumed_energy = 0.0

    def distance_to(self, other: 'Node') -> float:
        """Euclidean distance to another node in meters."""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def consume_energy(self, amount: float):
        """Deducts energy for transmission/reception and updates alive status."""
        actual_consumed = min(self.residual_energy, max(0.0, amount))
        self.residual_energy = max(0.0, self.residual_energy - actual_consumed)
        self.total_consumed_energy += actual_consumed
        if self.residual_energy <= 0.0:
            self.is_alive = False
            self.residual_energy = 0.0

    def harvest_energy(self, amount: float) -> float:
        """Adds harvested energy up to maximum battery capacity."""
        if amount <= 0.0:
            return 0.0
        room = max(0.0, self.max_energy - self.residual_energy)
        actual_harvested = min(amount, room)
        self.residual_energy += actual_harvested
        self.total_harvested_energy += actual_harvested
        if self.residual_energy > 0.0:
            self.is_alive = True
        return actual_harvested

    def __repr__(self):
        return f"Node(id={self.node_id}, pos=({self.x:.1f},{self.y:.1f}), energy={self.residual_energy:.2f}/{self.max_energy:.2f}J, role={self.role}, alive={self.is_alive})"


class Graph:
    """Adjacency list representation of the sensor network."""

    def __init__(self, nodes: Dict[int, Node]):
        self.nodes = nodes
        self.adjacency_list: Dict[int, List[Tuple[int, float]]] = {node_id: [] for node_id in nodes}
        self._build_adjacency_list()

    def _build_adjacency_list(self):
        """Builds initial complete mesh between all nodes."""
        node_ids = list(self.nodes.keys())
        for i in range(len(node_ids)):
            for j in range(i + 1, len(node_ids)):
                id_i = node_ids[i]
                id_j = node_ids[j]
                dist = self.nodes[id_i].distance_to(self.nodes[id_j])
                self.adjacency_list[id_i].append((id_j, dist))
                self.adjacency_list[id_j].append((id_i, dist))

    def update_edge_weights(self, energy_model):
        """Updates edge weights to represent 1-bit radio transmission energy cost."""
        k = 1  # 1 bit normalized cost
        for node_id, neighbors in self.adjacency_list.items():
            updated_neighbors = []
            for neighbor_id, _ in neighbors:
                dist = self.nodes[node_id].distance_to(self.nodes[neighbor_id])
                energy_cost = energy_model.transmit_energy(k, dist)
                updated_neighbors.append((neighbor_id, energy_cost))
            self.adjacency_list[node_id] = updated_neighbors

    def get_neighbors(self, node_id: int) -> List[Tuple[int, float]]:
        return self.adjacency_list.get(node_id, [])

    def get_node(self, node_id: int) -> Optional[Node]:
        return self.nodes.get(node_id)

    def alive_nodes(self) -> List[int]:
        return [nid for nid, node in self.nodes.items() if node.is_alive]

    def __repr__(self):
        alive_count = len(self.alive_nodes())
        total_count = len(self.nodes)
        return f"Graph(nodes={total_count}, alive={alive_count})"
