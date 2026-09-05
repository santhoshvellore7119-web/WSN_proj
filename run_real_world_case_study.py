"""
Real-World Empirical Case Study: Great Duck Island WSN Deployment
==================================================================
Simulates and evaluates multi-protocol routing over the classic Great Duck Island
(GDI) habitat monitoring deployment scenario (Mainwaring et al., 2002; Szewczyk et al., 2004).

Scenario Parameters:
- Network Size: N = 32 Mica2/MicaDot sensor motes
- Field Dimensions: 200m x 100m coastal habitat strip
- Base Station: (10m, 50m) field station uplink
- Energy Harvesting: Heterogeneous solar profile modeling canopy-occluded petrel burrows
  (60% shaded spruce canopy vs. 40% open coastal perimeter)
- Duration: 500 rounds (modeling continuous diurnal cycles)
- Protocols Compared:
  1. Conventional LEACH (Energy-unaware)
  2. EH-LEACH (Harvest-aware heuristic clustering)
  3. Static Energy-Aware Dijkstra (Residual energy greedy metric)
  4. Time-Augmented DP + DSU Live Rerouting (Proposed)
"""

import sys
import os
import csv
import numpy as np
import matplotlib.pyplot as plt

sys.path.append('src')

from simulator import Simulator
from harvesting_model import create_shadowed_solar_profile


def run_great_duck_island_case_study(seed=42):
    print("=" * 80)
    print("EMPIRICAL CASE STUDY: GREAT DUCK ISLAND HABITAT MONITORING DEPLOYMENT")
    print("=" * 80)
    print("Topological Profile: N=32 nodes across 200m x 100m terrain")
    print("Harvesting Profile : Heterogeneous solar with spruce canopy occlusion (p_shadow=0.6)")
    print("Base Station Loc   : (10m, 50m) coastal uplink station")
    print("Simulation Horizon : 500 rounds\n")

    num_nodes = 32
    area_width = 200.0
    area_height = 100.0
    bs_pos = (10.0, 50.0)
    init_energy = 0.05
    max_cap = 0.50
    cluster_ratio = 0.08
    max_rounds = 500
    tx_range = 45.0
    p_shadow = 0.6
    shadow_factor = 0.20
    solar_peak = 0.0015

    harvest_kwargs = {
        'peak_rate': solar_peak,
        'shadow_fraction': p_shadow,
        'shadow_penalty': shadow_factor,
        'period': 24,
        'day_fraction': 0.5,
        'seed': seed
    }

    protocols = [
        {
            'name': 'Conventional LEACH',
            'short_name': 'LEACH',
            'color': '#e53e3e',
            'linestyle': ':',
            'enable_dp': False,
            'enable_time_dp': False,
            'enable_harvesting_ch': False,
            'enable_live_reroute': False
        },
        {
            'name': 'EH-LEACH (Harvesting Heuristic)',
            'short_name': 'EH-LEACH',
            'color': '#dd6b20',
            'linestyle': '-.',
            'enable_dp': False,
            'enable_time_dp': False,
            'enable_harvesting_ch': True,
            'enable_live_reroute': False
        },
        {
            'name': 'Energy-Aware Dijkstra',
            'short_name': 'EA-Dijkstra',
            'color': '#38a169',
            'linestyle': '--',
            'enable_dp': True,
            'enable_time_dp': False,
            'enable_harvesting_ch': True,
            'enable_live_reroute': False
        },
        {
            'name': 'Time-Augmented DP + DSU (Proposed)',
            'short_name': 'Time-DP + DSU',
            'color': '#2b6cb0',
            'linestyle': '-',
            'enable_dp': True,
            'enable_time_dp': True,
            'enable_harvesting_ch': True,
            'enable_live_reroute': True
        }
    ]

    results = []

    for proto in protocols:
        print(f"Executing simulation for: {proto['name']}...")
        sim = Simulator(
            num_nodes=num_nodes,
            area_width=area_width,
            area_height=area_height,
            base_station_pos=bs_pos,
            initial_energy=init_energy,
            max_battery_capacity=max_cap,
            desired_clusters_ratio=cluster_ratio,
            enable_dp_routing=proto['enable_dp'],
            enable_time_dp=proto['enable_time_dp'],
            enable_harvesting_ch=proto['enable_harvesting_ch'],
            enable_live_reroute=proto['enable_live_reroute'],
            harvesting_profile='heterogeneous_shadowed',
            harvesting_kwargs=harvest_kwargs,
            transmission_range=tx_range,
            seed=seed
        )
        sim.run(max_rounds=max_rounds, verbose=False)

        alive_hist = sim.alive_nodes_history
        energy_hist = sim.total_energy_history
        pdr_hist = sim.pdr_history if hasattr(sim, 'pdr_history') else [1.0] * len(alive_hist)
        
        fnd = sim.first_node_death_round if sim.first_node_death_round is not None else max_rounds
        hnd = next((r + 1 for r, count in enumerate(alive_hist) if count <= num_nodes // 2), max_rounds)
        lnd = next((r + 1 for r, count in enumerate(alive_hist) if count == 0), max_rounds)

        total_delivered = sum(int(round(pdr * alive)) for pdr, alive in zip(pdr_hist, alive_hist))
        final_energy = energy_hist[-1]
        final_alive = alive_hist[-1]

        results.append({
            'meta': proto,
            'sim': sim,
            'fnd': fnd,
            'hnd': hnd,
            'lnd': lnd,
            'final_alive': final_alive,
            'final_energy': final_energy,
            'total_delivered': total_delivered,
            'alive_history': alive_hist,
            'energy_history': energy_hist,
            'pdr_history': pdr_hist
        })

    print("\n" + "=" * 92)
    print(f"{'Protocol':<35} | {'FND':<6} | {'HND':<6} | {'LND':<6} | {'Alive':<6} | {'Residual (J)':<12} | {'Pkts Delivered'}")
    print("-" * 92)
    for r in results:
        p = r['meta']
        print(f"{p['name']:<35} | {r['fnd']:<6} | {r['hnd']:<6} | {r['lnd']:<6} | {r['final_alive']:<6} | {r['final_energy']:<12.4f} | {r['total_delivered']}")
    print("=" * 92)

    os.makedirs('results', exist_ok=True)
    csv_path = os.path.join('results', 'real_world_case_study.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Protocol', 'FND', 'HND', 'LND', 'FinalAlive', 'ResidualEnergyJoules', 'TotalPacketsDelivered'])
        for r in results:
            writer.writerow([
                r['meta']['name'],
                r['fnd'],
                r['hnd'],
                r['lnd'],
                r['final_alive'],
                f"{r['final_energy']:.6f}",
                r['total_delivered']
            ])
    print(f"\n[Saved CSV Data]: {csv_path}")

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Panel A: Node Survival vs Rounds
    ax0 = axes[0, 0]
    for r in results:
        p = r['meta']
        ax0.plot(r['alive_history'], label=p['short_name'], color=p['color'], linestyle=p['linestyle'], linewidth=2.2)
    ax0.set_title('(A) Network Survival Rate (Active Nodes vs. Round)', fontsize=11, fontweight='bold')
    ax0.set_xlabel('Simulation Round (Hours)', fontsize=10)
    ax0.set_ylabel('Active Sensor Nodes (N=32)', fontsize=10)
    ax0.grid(True, linestyle=':', alpha=0.6)
    ax0.legend(loc='lower left', fontsize=9)
    ax0.set_ylim(-1, 34)

    # Panel B: Total Network Energy vs Rounds
    ax1 = axes[0, 1]
    for r in results:
        p = r['meta']
        ax1.plot(r['energy_history'], label=p['short_name'], color=p['color'], linestyle=p['linestyle'], linewidth=2.2)
    ax1.set_title('(B) Aggregate Residual Energy (Joules)', fontsize=11, fontweight='bold')
    ax1.set_xlabel('Simulation Round (Hours)', fontsize=10)
    ax1.set_ylabel('Network Stored Energy (J)', fontsize=10)
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.legend(loc='upper right', fontsize=9)

    # Panel C: Packet Delivery Reliability
    ax2 = axes[1, 0]
    for r in results:
        p = r['meta']
        ax2.plot(r['pdr_history'], label=p['short_name'], color=p['color'], linestyle=p['linestyle'], linewidth=2.0)
    ax2.set_title('(C) Packet Delivery Reliability (PDR)', fontsize=11, fontweight='bold')
    ax2.set_xlabel('Simulation Round (Hours)', fontsize=10)
    ax2.set_ylabel('PDR (%)', fontsize=10)
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.legend(loc='lower left', fontsize=9)
    ax2.set_ylim(0.0, 1.05)

    # Panel D: Great Duck Island Topology & Field Deployment Layout
    ax3 = axes[1, 1]
    sample_sim = results[-1]['sim']
    node_objs = list(sample_sim.graph.nodes.values())
    
    # Identify shaded vs sunny nodes based on profile
    shaded_nodes = [n for n in node_objs if getattr(n, 'is_shaded', False) or (hasattr(n, 'harvesting_profile') and getattr(n.harvesting_profile, 'is_shaded', False))]
    sunny_nodes = [n for n in node_objs if n not in shaded_nodes]

    # Draw shaded canopy zone
    ax3.fill_between([40, 180], [15, 15], [85, 85], color='#cbd5e0', alpha=0.35, label='Spruce Canopy Occlusion (60% Shade)')
    
    # Plot Sunny Nodes
    if sunny_nodes:
        xs = [n.x for n in sunny_nodes]
        ys = [n.y for n in sunny_nodes]
        ax3.scatter(xs, ys, c='#d69e2e', marker='o', s=70, edgecolors='black', label='Sunny Mote (Coastal Perimeter)', zorder=4)

    # Plot Shaded Nodes
    if shaded_nodes:
        xs = [n.x for n in shaded_nodes]
        ys = [n.y for n in shaded_nodes]
        ax3.scatter(xs, ys, c='#4a5568', marker='s', s=70, edgecolors='black', label='Canopy Shaded Mote (Burrows)', zorder=4)

    ax3.scatter([bs_pos[0]], [bs_pos[1]], c='#e53e3e', marker='^', s=160, edgecolors='black', label='Field Uplink Station (Base)', zorder=5)

    ax3.set_xlim(-5, area_width + 5)
    ax3.set_ylim(-5, area_height + 5)
    ax3.set_title('(D) Great Duck Island Habitat Deployment Map', fontsize=11, fontweight='bold')
    ax3.set_xlabel('Terrain Width (m)', fontsize=10)
    ax3.set_ylabel('Terrain Height (m)', fontsize=10)
    ax3.grid(True, linestyle=':', alpha=0.6)
    ax3.legend(loc='upper right', fontsize=8)

    plt.tight_layout()
    plot_path = os.path.join('results', 'real_world_case_study.png')
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"[Saved Case Study Plot]: {plot_path}")
    print("=" * 80 + "\n")


if __name__ == '__main__':
    run_great_duck_island_case_study(seed=42)
