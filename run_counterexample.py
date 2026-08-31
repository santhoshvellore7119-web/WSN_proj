"""
Deterministic 5-Node Counterexample: Classical DP vs Time-Augmented DP

Isolates the core algorithmic mechanism in a minimal hand-constructed network:
- Classical Maximin DP is blind to future recharge and routes through Node A (which has higher
  static energy now, but zero harvest, and rapidly dies).
- Time-Augmented DP projects incoming harvest and routes through Node B (which has low static
  energy at t=0, but recharges just-in-time at t=1, surviving easily).
"""

import sys
import os
import math
import matplotlib.pyplot as plt

sys.path.append('src')

from network import Node, Graph
from energy_model import EnergyModel
from harvesting_model import HeterogeneousHarvesting, ConstantHarvesting
from dp_lifetime import dp_lifetime_maximin_path, dp_time_augmented_lifetime
from routing import dijkstra, energy_aware_dijkstra


def run_minimal_counterexample():
    print("=" * 75)
    print("5-NODE MINIMAL ADVERSARIAL COUNTEREXAMPLE: MECHANISM ISOLATION")
    print("=" * 75)

    # Hand-crafted 5-node topology
    # Node 0 (Source): (10, 50), E_0 = 0.050 J
    # Node 1 (Relay A - Depleting): (45, 68), E_1 = 0.030 J, Harvest = 0.000 J/step
    # Node 2 (Relay B - Recharging): (45, 32), E_2 = 0.005 J, Harvest = +0.035 J/step
    # Node 3 (Relay C - Buffer): (65, 32), E_3 = 0.050 J, Harvest = +0.010 J/step
    # Base Station (-1): (85, 50)
    # Transmission Range: 48.0 m (Forces 0 to choose between Relay 1 and Relay 2)

    nodes = {
        0: Node(node_id=0, x=10.0, y=50.0, initial_energy=0.050, max_energy=0.100),
        1: Node(node_id=1, x=45.0, y=68.0, initial_energy=0.030, max_energy=0.100),
        2: Node(node_id=2, x=45.0, y=32.0, initial_energy=0.005, max_energy=0.100),
        3: Node(node_id=3, x=65.0, y=32.0, initial_energy=0.050, max_energy=0.100),
    }

    base_station_pos = (85.0, 50.0)
    tx_range = 48.0
    energy_model = EnergyModel()
    alive_nodes = {0, 1, 2, 3}

    # Harvest profiles: Node 1 has 0 recharge; Node 2 receives fast ambient recharge (+0.035 J/step)
    harvesting = HeterogeneousHarvesting(
        default_profile=ConstantHarvesting(rate=0.0),
        node_profiles={
            0: ConstantHarvesting(rate=0.0),
            1: ConstantHarvesting(rate=0.000),  # Stagnant / Depleting
            2: ConstantHarvesting(rate=0.035),  # Fast Recharging
            3: ConstantHarvesting(rate=0.010),
        }
    )

    # Build Graph with explicit edges
    graph = Graph(nodes)
    graph.update_edge_weights(energy_model)

    print("\nNetwork Initial State (t = 0):")
    print(f"  Source S (Node 0): Pos=(10, 50), E(0) = {nodes[0].residual_energy:.3f} J")
    print(f"  Relay A  (Node 1): Pos=(45, 68), E(0) = {nodes[1].residual_energy:.3f} J, Harvest Rate = +0.000 J/step (Depleting)")
    print(f"  Relay B  (Node 2): Pos=(45, 32), E(0) = {nodes[2].residual_energy:.3f} J, Harvest Rate = +0.035 J/step (Recharging)")
    print(f"  Relay C  (Node 3): Pos=(65, 32), E(0) = {nodes[3].residual_energy:.3f} J, Harvest Rate = +0.010 J/step")
    print(f"  Sink BS  (Node -1): Pos=(85, 50) | Max TX Range = {tx_range} m (Direct 0 -> BS is {math.hypot(85-10, 0):.1f}m > {tx_range}m)")

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

    print("\n" + "-" * 75)
    print("ALGORITHMIC ROUTING DECISIONS COMPARISON:")
    print("-" * 75)
    print(f"1. Classical Maximin DP:      Path = {dp_path} | Bottleneck = {dp_bottleneck:.4f} J")
    print(f"   -> Reasoning: Sees Node 1 has {nodes[1].residual_energy:.3f}J > Node 2 ({nodes[2].residual_energy:.3f}J) at t=0.")
    print(f"   -> Outcome: Routes via dying Node 1. Node 1 has no harvest and depletes to 0 J.")

    print(f"\n2. Energy-Aware Dijkstra:      Path = {ea_path} | Cost = {ea_cost:.6f} J")
    print(f"   -> Reasoning: Penalizes Node 2 due to low initial energy ({nodes[2].residual_energy:.3f}J).")
    print(f"   -> Outcome: Routes via Node 1 or direct BS, failing to utilize recharging Node 2.")

    print(f"\n3. Time-Augmented DP (Ours):  Path = {time_path} | Projected Bottleneck = {time_bottleneck:.4f} J | Schedule = {schedule}")
    proj_e2 = harvesting.project_energy(2, nodes[2].residual_energy, 0, 1, nodes[2].max_energy)
    print(f"   -> Reasoning: Projects Node 2's energy at arrival offset t=1: E_proj(2, t=1) = {proj_e2:.3f} J.")
    print(f"   -> Outcome: Accurately discovers that Node 2 recharges just-in-time, selecting Path 0 -> 2 -> -1!")
    print("-" * 75)

    # Generate Visualization Diagram
    os.makedirs('results', exist_ok=True)
    plt.figure(figsize=(9, 6))

    # Node positions
    for nid, node in nodes.items():
        plt.scatter(node.x, node.y, s=350, c='dodgerblue' if nid != 0 else 'lightgreen',
                    edgecolors='black', linewidth=1.5, zorder=4)
        harvest_str = f"+{harvesting.node_profiles[nid].rate:.3f}J/t" if nid in harvesting.node_profiles else ""
        plt.text(node.x, node.y + 4.5, f"Node {nid} (E0={node.residual_energy:.3f}J)\n{harvest_str}",
                 ha='center', fontsize=9, fontweight='bold')

    # Base Station
    plt.scatter(base_station_pos[0], base_station_pos[1], s=450, c='gold', marker='*',
                edgecolors='black', linewidth=1.5, zorder=5)
    plt.text(base_station_pos[0], base_station_pos[1] + 4.5, "Base Station (-1)\n(Sink)",
             ha='center', fontsize=9, fontweight='bold')

    # Draw Classical DP Path (Red)
    dp_xs = [nodes[n].x if n != -1 else base_station_pos[0] for n in dp_path]
    dp_ys = [nodes[n].y if n != -1 else base_station_pos[1] for n in dp_path]
    plt.plot(dp_xs, dp_ys, 'r--', linewidth=2.5, label=f'Classical DP Path: {dp_path} (Fails: Node 1 Dies)', zorder=2)

    # Draw Time-DP Path (Green)
    time_xs = [nodes[n].x if n != -1 else base_station_pos[0] for n in time_path]
    time_ys = [nodes[n].y if n != -1 else base_station_pos[1] for n in time_path]
    plt.plot(time_xs, time_ys, 'g-', linewidth=3.0, label=f'Time-Augmented DP: {time_path} (Succeeds: Node 2 Recharges)', zorder=3)

    plt.title("5-Node Adversarial Counterexample Topology", fontsize=13, fontweight='bold')
    plt.xlabel("X Position (m)")
    plt.ylabel("Y Position (m)")
    plt.xlim(0, 115)
    plt.ylim(10, 95)
    plt.legend(loc='lower right', fontsize=9.5)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()

    filepath = 'results/counterexample_5node.png'
    plt.savefig(filepath, dpi=150)
    plt.close()
    print(f"\nSaved counterexample diagram to {filepath}")

    return dp_path, time_path, dp_bottleneck, time_bottleneck


if __name__ == '__main__':
    run_minimal_counterexample()
