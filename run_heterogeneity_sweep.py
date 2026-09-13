"""
Heterogeneity Sweep: Falsifiable Hypothesis Validation for Time-Augmented DP

Hypothesis:
"Time-Augmented DP's performance advantage over static and unaware baselines
scales monotonically with spatial harvesting heterogeneity."

Under uniform solar harvesting (p_shadow = 0.0), all nodes recharge at identical rates,
so lookahead yields negligible advantage over energy-aware heuristics.
As spatial heterogeneity increases (p_shadow in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]),
occluded nodes deplete rapidly if overused, while sunny nodes recharge just-in-time.
Time-Augmented DP dynamically discovers and routes through recharging energy bridges.
"""

import sys
import os
import math
import csv
import matplotlib.pyplot as plt
import numpy as np

sys.path.append('src')

from simulator import Simulator
from network import Node, Graph
from energy_model import EnergyModel
from harvesting_model import create_shadowed_solar_profile


def run_heterogeneity_experiment():
    print("=" * 78)
    print("HARVESTING HETEROGENEITY SWEEP: TESTING THE LOOKAHEAD ADVANTAGE HYPOTHESIS")
    print("=" * 78)

    num_nodes = 50
    area = 100.0
    bs_pos = (50.0, 50.0)
    init_energy = 0.045
    max_cap = 0.50
    cluster_ratio = 0.08
    max_rounds = 350
    tx_range = 35.0
    seed = 42

    shadow_probabilities = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]

    results_table = []

    # Metrics storage for plotting
    fnd_unaware = []
    fnd_time_dp = []
    energy_unaware = []
    energy_time_dp = []
    alive_unaware = []
    alive_time_dp = []
    advantage_margins = []

    for p_shadow in shadow_probabilities:
        print(f"\nEvaluating Shadow Fraction p = {p_shadow:.1f} (Seed {seed})...")

        # 1. Unaware LEACH + Dijkstra
        sim_unaware = Simulator(
            num_nodes=num_nodes,
            area_width=area,
            area_height=area,
            base_station_pos=bs_pos,
            initial_energy=init_energy,
            max_battery_capacity=max_cap,
            desired_clusters_ratio=cluster_ratio,
            enable_dp_routing=False,
            enable_time_dp=False,
            enable_harvesting_ch=False,
            harvesting_profile='heterogeneous_shadowed',
            harvesting_kwargs={
                'peak_rate': 0.0012,
                'shadow_fraction': p_shadow,
                'shadow_penalty': 0.10,
                'period': 24,
                'day_fraction': 0.5,
                'seed': seed
            },
            transmission_range=tx_range,
            seed=seed
        )
        sim_unaware.run(max_rounds=max_rounds, verbose=False)

        # 2. Time-Augmented DP
        sim_timedp = Simulator(
            num_nodes=num_nodes,
            area_width=area,
            area_height=area,
            base_station_pos=bs_pos,
            initial_energy=init_energy,
            max_battery_capacity=max_cap,
            desired_clusters_ratio=cluster_ratio,
            enable_dp_routing=True,
            enable_time_dp=True,
            enable_harvesting_ch=True,
            enable_live_reroute=True,
            harvesting_profile='heterogeneous_shadowed',
            harvesting_kwargs={
                'peak_rate': 0.0012,
                'shadow_fraction': p_shadow,
                'shadow_penalty': 0.10,
                'period': 24,
                'day_fraction': 0.5,
                'seed': seed
            },
            transmission_range=tx_range,
            seed=seed
        )
        sim_timedp.run(max_rounds=max_rounds, verbose=False)

        fnd_u = sim_unaware.first_node_death_round or max_rounds + 1
        fnd_dp = sim_timedp.first_node_death_round or max_rounds + 1
        e_u = sim_unaware.total_energy_history[-1]
        e_dp = sim_timedp.total_energy_history[-1]
        a_u = sim_unaware.alive_nodes_history[-1]
        a_dp = sim_timedp.alive_nodes_history[-1]

        # Margin advantage in residual energy percentage / Joules
        e_margin = (e_dp - e_u)
        e_gain_pct = ((e_dp - e_u) / max(1e-6, e_u)) * 100.0 if e_u > 0 else (100.0 if e_dp > 0 else 0.0)

        fnd_unaware.append(fnd_u)
        fnd_time_dp.append(fnd_dp)
        energy_unaware.append(e_u)
        energy_time_dp.append(e_dp)
        alive_unaware.append(a_u)
        alive_time_dp.append(a_dp)
        advantage_margins.append(e_gain_pct)

        results_table.append({
            'p_shadow': p_shadow,
            'fnd_unaware': fnd_u,
            'fnd_timedp': fnd_dp,
            'alive_unaware': a_u,
            'alive_timedp': a_dp,
            'energy_unaware': e_u,
            'energy_timedp': e_dp,
            'energy_gain_pct': e_gain_pct
        })

        print(f"  p_shadow = {p_shadow:.1f} | Unaware: FND={fnd_u:>3}, Alive={a_u:>2}/50, E={e_u:.4f}J | Time-DP: FND={fnd_dp:>3}, Alive={a_dp:>2}/50, E={e_dp:.4f}J | Gain = {e_gain_pct:>+6.1f}%")

    os.makedirs('results', exist_ok=True)

    # Save CSV
    csv_path = os.path.join('results', 'heterogeneity_sweep_results.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(results_table[0].keys()))
        writer.writeheader()
        writer.writerows(results_table)
    print(f"\nSaved CSV results to: {csv_path}")

    # Generate Publication Figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    # Subplot 1: Alive Nodes & FND as function of Heterogeneity
    p_arr = np.array(shadow_probabilities)
    ax1.plot(p_arr, alive_unaware, 'o--', color='#d9534f', label='Unaware LEACH + Dijkstra (Alive Nodes)', linewidth=2)
    ax1.plot(p_arr, alive_time_dp, 's-', color='#2b6cb0', label='Time-Augmented DP (Alive Nodes)', linewidth=2.5)
    ax1.set_xlabel(r'Spatial Heterogeneity (Shadow Occlusion Fraction $p_{\mathrm{shadow}}$)', fontsize=11)
    ax1.set_ylabel('Active Sensor Nodes at Round 350', fontsize=11)
    ax1.set_title('(A) Network Longevity vs. Harvesting Heterogeneity', fontsize=12, fontweight='bold')
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.legend(loc='upper right', frameon=True)
    ax1.set_ylim(-2, 52)

    # Subplot 2: Energy Advantage Margin
    ax2.bar(p_arr - 0.02, energy_unaware, width=0.04, label='Unaware Residual Energy (J)', color='#e57373', alpha=0.85)
    ax2.bar(p_arr + 0.02, energy_time_dp, width=0.04, label='Time-DP Residual Energy (J)', color='#4299e1', alpha=0.85)
    ax2.set_xlabel(r'Spatial Heterogeneity (Shadow Occlusion Fraction $p_{\mathrm{shadow}}$)', fontsize=11)
    ax2.set_ylabel('Total Residual Energy at Round 350 (Joules)', fontsize=11)
    ax2.set_title('(B) Residual Energy Advantage Margin', fontsize=12, fontweight='bold')
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.legend(loc='upper right', frameon=True)

    plt.tight_layout()
    plot_path = os.path.join('results', 'heterogeneity_advantage_sweep.png')
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"Saved heterogeneity sweep plot to: {plot_path}")

    print("\n" + "=" * 78)
    print("HETEROGENEITY EXPERIMENT COMPLETE: DATA AND PLOTS SAVED TO results/")
    print("=" * 78)


def run_multiseed_heterogeneity(num_seeds: int = 30, p_shadow: float = 1.0):
    """
    Evaluates extreme occlusion (p_shadow=1.0) across N independent seeds
    to compute paired statistical significance, Cohen's d effect size, and 95% CIs.
    """
    import scipy.stats as stats

    SEEDS = [
        42, 7, 123, 256, 999, 101, 202, 303, 404, 505,
        11, 22, 33, 44, 55, 66, 77, 88, 99, 111,
        222, 333, 444, 555, 666, 777, 888, 9999, 1337, 2026
    ]
    seeds = SEEDS[:num_seeds]

    print("=" * 78)
    print(f"MULTI-SEED HETEROGENEITY VALIDATION: p_shadow = {p_shadow:.1f} (N={len(seeds)} SEEDS)")
    print("=" * 78)

    num_nodes = 50
    area = 100.0
    bs_pos = (50.0, 50.0)
    init_energy = 0.045
    max_cap = 0.50
    cluster_ratio = 0.08
    max_rounds = 350
    tx_range = 35.0

    fnd_u_list, fnd_dp_list = [], []
    alive_u_list, alive_dp_list = [], []
    energy_u_list, energy_dp_list = [], []

    for idx, s in enumerate(seeds, 1):
        # 1. Unaware Baseline
        sim_u = Simulator(
            num_nodes=num_nodes, area_width=area, area_height=area,
            base_station_pos=bs_pos, initial_energy=init_energy,
            max_battery_capacity=max_cap, desired_clusters_ratio=cluster_ratio,
            enable_dp_routing=False, enable_time_dp=False, enable_harvesting_ch=False,
            harvesting_profile='heterogeneous_shadowed',
            harvesting_kwargs={'peak_rate': 0.0012, 'shadow_fraction': p_shadow, 'shadow_penalty': 0.10, 'period': 24, 'day_fraction': 0.5, 'seed': s},
            transmission_range=tx_range, seed=s
        )
        sim_u.run(max_rounds=max_rounds, verbose=False)
        fnd_u = sim_u.first_node_death_round if sim_u.first_node_death_round is not None else max_rounds + 1
        a_u = sim_u.alive_nodes_history[-1]
        e_u = sim_u.total_energy_history[-1]

        # 2. Adaptive Time-DP
        sim_dp = Simulator(
            num_nodes=num_nodes, area_width=area, area_height=area,
            base_station_pos=bs_pos, initial_energy=init_energy,
            max_battery_capacity=max_cap, desired_clusters_ratio=cluster_ratio,
            enable_dp_routing=False, enable_time_dp=True, enable_harvesting_ch=True,
            harvesting_profile='heterogeneous_shadowed',
            harvesting_kwargs={'peak_rate': 0.0012, 'shadow_fraction': p_shadow, 'shadow_penalty': 0.10, 'period': 24, 'day_fraction': 0.5, 'seed': s},
            transmission_range=tx_range, seed=s
        )
        sim_dp.run(max_rounds=max_rounds, verbose=False)
        fnd_dp = sim_dp.first_node_death_round if sim_dp.first_node_death_round is not None else max_rounds + 1
        a_dp = sim_dp.alive_nodes_history[-1]
        e_dp = sim_dp.total_energy_history[-1]

        fnd_u_list.append(fnd_u)
        fnd_dp_list.append(fnd_dp)
        alive_u_list.append(a_u)
        alive_dp_list.append(a_dp)
        energy_u_list.append(e_u)
        energy_dp_list.append(e_dp)

        print(f"  [{idx:>2}/{len(seeds)}] Seed {s:>4} | Unaware FND={fnd_u:>3}, E={e_u:.4f}J | Time-DP FND={fnd_dp:>3}, E={e_dp:.4f}J | Delta_FND = {fnd_dp - fnd_u:+d}")

    # Compute Statistics and 95% Confidence Intervals
    n = len(seeds)
    diff_fnd = np.array(fnd_dp_list) - np.array(fnd_u_list)
    diff_energy = np.array(energy_dp_list) - np.array(energy_u_list)
    diff_alive = np.array(alive_dp_list) - np.array(alive_u_list)

    def calc_stats(arr):
        mean = float(np.mean(arr))
        std = float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0
        sem = std / math.sqrt(len(arr)) if len(arr) > 1 else 0.0
        ci_low = mean - 1.96 * sem
        ci_high = mean + 1.96 * sem
        return mean, std, ci_low, ci_high

    m_fnd_u, s_fnd_u, ci_l_fnd_u, ci_h_fnd_u = calc_stats(fnd_u_list)
    m_fnd_dp, s_fnd_dp, ci_l_fnd_dp, ci_h_fnd_dp = calc_stats(fnd_dp_list)
    m_e_u, s_e_u, ci_l_e_u, ci_h_e_u = calc_stats(energy_u_list)
    m_e_dp, s_e_dp, ci_l_e_dp, ci_h_e_dp = calc_stats(energy_dp_list)

    # Paired hypothesis tests on FND
    t_stat_fnd, p_val_fnd = stats.ttest_rel(fnd_dp_list, fnd_u_list)
    try:
        w_stat_fnd, p_wilc_fnd = stats.wilcoxon(diff_fnd, zero_method='pratt')
    except Exception:
        w_stat_fnd, p_wilc_fnd = 0.0, 1.0

    std_diff_fnd = np.std(diff_fnd, ddof=1)
    cohen_d_fnd = (np.mean(diff_fnd) / std_diff_fnd) if std_diff_fnd > 1e-9 else 0.0

    print("\n" + "-" * 78)
    print(f"MULTI-SEED RESULTS SUMMARY (N={n} Seeds, p_shadow={p_shadow:.1f}):")
    print("-" * 78)
    print(f"  Unaware Baseline  : FND = {m_fnd_u:.1f} +/- {s_fnd_u:.1f} [95% CI: {ci_l_fnd_u:.1f}, {ci_h_fnd_u:.1f}] | Energy = {m_e_u:.4f} +/- {s_e_u:.4f} J [95% CI: {ci_l_e_u:.4f}, {ci_h_e_u:.4f}]")
    print(f"  Time-Augmented DP : FND = {m_fnd_dp:.1f} +/- {s_fnd_dp:.1f} [95% CI: {ci_l_fnd_dp:.1f}, {ci_h_fnd_dp:.1f}] | Energy = {m_e_dp:.4f} +/- {s_e_dp:.4f} J [95% CI: {ci_l_e_dp:.4f}, {ci_h_e_dp:.4f}]")
    print(f"  Mean Delta FND    : {np.mean(diff_fnd):+.2f} rounds (t({n-1}) = {t_stat_fnd:.3f}, p = {p_val_fnd:.4e}, Cohen's d = {cohen_d_fnd:.3f})")
    print(f"  Wilcoxon Test FND : W = {w_stat_fnd:.1f}, p = {p_wilc_fnd:.4e}")
    print(f"  Mean Delta Energy : {np.mean(diff_energy):+.4f} J")

    # Save to CSV
    os.makedirs('results', exist_ok=True)
    out_csv = os.path.join('results', f'multiseed_heterogeneity_p{int(p_shadow*10):02d}.csv')
    with open(out_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['seed', 'fnd_unaware', 'fnd_timedp', 'alive_unaware', 'alive_timedp', 'energy_unaware', 'energy_timedp'])
        for i in range(n):
            writer.writerow([seeds[i], fnd_u_list[i], fnd_dp_list[i], alive_u_list[i], alive_dp_list[i], energy_u_list[i], energy_dp_list[i]])
    print(f"\nSaved multi-seed data to: {out_csv}")
    return {
        'fnd_unaware_mean': m_fnd_u, 'fnd_unaware_ci': (ci_l_fnd_u, ci_h_fnd_u),
        'fnd_timedp_mean': m_fnd_dp, 'fnd_timedp_ci': (ci_l_fnd_dp, ci_h_fnd_dp),
        'energy_unaware_mean': m_e_u, 'energy_unaware_ci': (ci_l_e_u, ci_h_e_u),
        'energy_timedp_mean': m_e_dp, 'energy_timedp_ci': (ci_l_e_dp, ci_h_e_dp),
        'delta_fnd_mean': float(np.mean(diff_fnd)),
        'p_val_fnd': float(p_val_fnd),
        'cohen_d_fnd': float(cohen_d_fnd)
    }


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--multi-seed':
        seeds_cnt = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        run_multiseed_heterogeneity(num_seeds=seeds_cnt, p_shadow=1.0)
    else:
        run_heterogeneity_experiment()

