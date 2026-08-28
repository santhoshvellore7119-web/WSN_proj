"""
Visualization utilities for WSN simulation results.

Plots:
- Lifetime curves (alive nodes and residual energy over rounds)
- 2D heatmaps showing per-node energy levels over time
- Network topology and routing trees
- Side-by-side comparative lifetime curves
"""

import matplotlib.pyplot as plt
import numpy as np
import os
from typing import Dict, List, Tuple, Optional, Any
import math


class Visualizer:
    """Generates plots from a completed simulation run."""

    def __init__(self, simulator=None):
        self.sim = simulator
        self.results_dir = 'results'
        os.makedirs(self.results_dir, exist_ok=True)

    def plot_network_lifetime(self, save: bool = True, filename: str = 'network_lifetime.png'):
        """Plots alive nodes and total residual energy vs rounds."""
        if self.sim is None or not self.sim.alive_nodes_history:
            print("No simulation data to plot.")
            return

        rounds = list(range(1, len(self.sim.alive_nodes_history) + 1))
        alive_nodes = self.sim.alive_nodes_history
        total_energy = self.sim.total_energy_history

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

        # Alive nodes
        ax1.plot(rounds, alive_nodes, 'b-', linewidth=2, label='Alive Nodes')
        ax1.set_xlabel('Round')
        ax1.set_ylabel('Number of Alive Nodes')
        ax1.set_title('Network Lifetime: Alive Nodes vs Rounds')
        ax1.grid(True, linestyle='--', alpha=0.6)

        if self.sim.first_node_death_round:
            ax1.axvline(x=self.sim.first_node_death_round, color='r', linestyle='--',
                        label=f'FND (Round {self.sim.first_node_death_round})')
        if self.sim.half_nodes_dead_round:
            ax1.axvline(x=self.sim.half_nodes_dead_round, color='orange', linestyle='--',
                        label=f'HND (Round {self.sim.half_nodes_dead_round})')
        ax1.legend(loc='upper right')

        # Total energy
        ax2.plot(rounds, total_energy, 'm-', linewidth=2, label='Total Energy (J)')
        ax2.set_xlabel('Round')
        ax2.set_ylabel('Total Energy (Joules)')
        ax2.set_title('Total Residual Energy vs Rounds')
        ax2.grid(True, linestyle='--', alpha=0.6)
        ax2.legend(loc='upper right')

        plt.tight_layout()
        if save:
            filepath = os.path.join(self.results_dir, filename)
            plt.savefig(filepath, dpi=150)
            plt.close()
            print(f"Saved network lifetime plot to {filepath}")
        else:
            plt.show()

    def plot_energy_heatmap_over_time(
        self,
        save: bool = True,
        filename: str = 'energy_heatmap.png',
        title: Optional[str] = None
    ):
        """Plots 2D heatmap of per-node residual energy across all rounds."""
        if self.sim is None or not self.sim.energy_matrix:
            print("No energy matrix data available for heatmap.")
            return

        matrix = np.array(self.sim.energy_matrix).T
        num_nodes, num_rounds = matrix.shape
        max_val = float(matrix.max()) if matrix.size > 0 and matrix.max() > 0 else self.sim.max_battery_capacity

        plt.figure(figsize=(12, 6))
        im = plt.imshow(
            matrix,
            aspect='auto',
            cmap='plasma',
            origin='lower',
            extent=[1, num_rounds, 0, num_nodes - 1],
            vmin=0.0,
            vmax=max_val
        )

        cbar = plt.colorbar(im)
        cbar.set_label('Residual Energy (Joules)', rotation=270, labelpad=15)

        default_title = f'Node Residual Energy Over Time ({num_nodes} Nodes, {num_rounds} Rounds)'
        plt.title(title or default_title, fontsize=13, fontweight='bold')
        plt.xlabel('Simulation Round', fontsize=11)
        plt.ylabel('Node ID', fontsize=11)
        plt.grid(False)

        plt.tight_layout()
        if save:
            filepath = os.path.join(self.results_dir, filename)
            plt.savefig(filepath, dpi=150)
            plt.close()
            print(f"Saved energy heatmap to {filepath}")
        else:
            plt.show()

    def plot_routing_tree(self, round_num: int, save: bool = True):
        """Plots 2D sensor positions, elected cluster heads, and paths to base station."""
        if self.sim is None or round_num < 1 or round_num > len(self.sim.cluster_heads_history):
            return

        cluster_heads = self.sim.cluster_heads_history[round_num - 1]
        routes_dict = self.sim.routes_history[round_num - 1]

        plt.figure(figsize=(10, 8))

        xs = [node.x for node in self.sim.nodes.values()]
        ys = [node.y for node in self.sim.nodes.values()]
        colors = []
        for nid, node in self.sim.nodes.items():
            if self.sim.energy_matrix and round_num <= len(self.sim.energy_matrix):
                is_alive_at_round = self.sim.energy_matrix[round_num - 1][nid] > 0.0
            else:
                is_alive_at_round = node.is_alive

            if not is_alive_at_round:
                colors.append('lightgray')
            elif nid in cluster_heads:
                colors.append('crimson')
            else:
                colors.append('dodgerblue')

        plt.scatter(xs, ys, c=colors, s=60, edgecolors='black', linewidth=0.5, zorder=3)

        # Base Station
        bs_x, bs_y = self.sim.base_station_pos
        plt.scatter([bs_x], [bs_y], c='gold', s=250, marker='*', edgecolors='black', linewidth=1.5,
                    label='Base Station', zorder=4)

        # Routes from cluster heads to base station
        first_route = True
        for ch_id, route_info in routes_dict.items():
            if not route_info:
                continue
            path = route_info[0]
            if path is None or len(path) < 2:
                continue
            path_xs, path_ys = [], []
            for nid in path:
                if nid == -1:
                    path_xs.append(bs_x)
                    path_ys.append(bs_y)
                else:
                    path_xs.append(self.sim.nodes[nid].x)
                    path_ys.append(self.sim.nodes[nid].y)
            plt.plot(path_xs, path_ys, 'g--', linewidth=1.8, alpha=0.75,
                     label='Active Route to BS' if first_route else "", zorder=2)
            first_route = False

        plt.scatter([], [], c='crimson', s=60, edgecolors='black', label='Cluster Head (CH)')
        plt.scatter([], [], c='dodgerblue', s=60, edgecolors='black', label='Member Node')
        plt.scatter([], [], c='lightgray', s=60, edgecolors='black', label='Dead Node')

        plt.legend(loc='upper right')
        plt.title(f'WSN Topology & Routing Tree - Round {round_num}', fontsize=12, fontweight='bold')
        plt.xlabel('X Position (m)')
        plt.ylabel('Y Position (m)')
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.axis('equal')
        plt.xlim(0, self.sim.area_width)
        plt.ylim(0, self.sim.area_height)

        if save:
            filepath = os.path.join(self.results_dir, f'routing_tree_round_{round_num}.png')
            plt.savefig(filepath, dpi=150)
            plt.close()
        else:
            plt.show()

    def generate_all_plots(self):
        """Generates standard lifetime curves, heatmaps, and routing topology plots."""
        print("Generating network lifetime plot...")
        self.plot_network_lifetime()
        if self.sim and self.sim.energy_matrix:
            print("Generating energy heatmap...")
            self.plot_energy_heatmap_over_time()

        if self.sim and self.sim.alive_nodes_history:
            num_rounds = len(self.sim.alive_nodes_history)
            rounds_to_plot = sorted(list(set([1, max(1, num_rounds // 2), num_rounds])))
            for r in rounds_to_plot:
                self.plot_routing_tree(r, save=True)
        print("All plots generated successfully.")


def plot_comparison_lifetime(
    results_dict: Dict[str, Any],
    save: bool = True,
    filename: str = 'network_lifetime_comparison.png'
):
    """Generates comparative alive nodes and energy curves for multiple scenarios."""
    os.makedirs('results', exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 9))

    colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', '#a65628']
    styles = ['-', '--', '-.', ':', '-', '--']

    for idx, (label, sim) in enumerate(results_dict.items()):
        c = colors[idx % len(colors)]
        ls = styles[idx % len(styles)]

        if hasattr(sim, 'alive_nodes_history'):
            alive = sim.alive_nodes_history
            energy = sim.total_energy_history
            rounds = list(range(1, len(alive) + 1))
            fnd = sim.first_node_death_round
            hnd = sim.half_nodes_dead_round
        else:
            alive = sim['alive_nodes']
            energy = sim['total_energy']
            rounds = list(range(1, len(alive) + 1))
            fnd = sim.get('fnd')
            hnd = sim.get('hnd')

        fnd_str = f" (FND: {fnd})" if fnd else ""
        ax1.plot(rounds, alive, label=f"{label}{fnd_str}", color=c, linestyle=ls, linewidth=2)
        ax2.plot(rounds, energy, label=f"{label}", color=c, linestyle=ls, linewidth=2)

    ax1.set_xlabel('Simulation Round', fontsize=11)
    ax1.set_ylabel('Alive Nodes', fontsize=11)
    ax1.set_title('Network Lifetime Comparison: Alive Nodes vs Rounds', fontsize=12, fontweight='bold')
    ax1.grid(True, linestyle='--', alpha=0.6)
    ax1.legend(loc='lower left', fontsize=10)

    ax2.set_xlabel('Simulation Round', fontsize=11)
    ax2.set_ylabel('Total Residual Energy (Joules)', fontsize=11)
    ax2.set_title('Energy Depletion Comparison: Total Residual Energy vs Rounds', fontsize=12, fontweight='bold')
    ax2.grid(True, linestyle='--', alpha=0.6)
    ax2.legend(loc='upper right', fontsize=10)

    plt.tight_layout()
    if save:
        filepath = os.path.join('results', filename)
        plt.savefig(filepath, dpi=150)
        plt.close()
        print(f"Saved comparative lifetime plot to {filepath}")
    else:
        plt.show()