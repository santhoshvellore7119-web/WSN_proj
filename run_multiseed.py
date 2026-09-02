"""
Multi-Seed Statistical Significance Testing for WSN Energy Routing Configurations

Evaluates all configurations across N=30 independent random seeds:
- Reports Mean +/- Std for FND, HND, Alive Nodes, and Final Residual Energy.
- Computes Paired Differences (Delta_i = TimeDP_i - Baseline_i for each seed).
- Performs Paired Student's t-test (t-statistic, df, two-tailed p-value).
- Performs Wilcoxon Signed-Rank Test (non-parametric rank-sum test).
- Computes Effect Sizes (Cohen's d).
- Generates statistical boxplots in results/multiseed_boxplots.png and CSV summary.
"""

import sys
import os
import math
import csv
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

sys.path.append('src')

from simulator import Simulator

# 30 Independent random seeds for statistical power
SEEDS = [
    42, 7, 123, 256, 999, 101, 202, 303, 404, 505,
    11, 22, 33, 44, 55, 66, 77, 88, 99, 111,
    222, 333, 444, 555, 666, 777, 888, 9999, 1337, 2026
]

NUM_NODES      = 50
AREA           = 100.0
BS_POS         = (50.0, 50.0)
INIT_ENERGY    = 0.045
MAX_CAPACITY   = 0.50
CLUSTER_RATIO  = 0.08
MAX_ROUNDS     = 350
TX_RANGE       = 35.0


def run_config(seed, **kwargs):
    sim = Simulator(
        num_nodes=NUM_NODES,
        area_width=AREA,
        area_height=AREA,
        base_station_pos=BS_POS,
        initial_energy=INIT_ENERGY,
        max_battery_capacity=MAX_CAPACITY,
        desired_clusters_ratio=CLUSTER_RATIO,
        transmission_range=TX_RANGE,
        seed=seed,
        **kwargs
    )
    sim.run(max_rounds=MAX_ROUNDS, verbose=False)
    fnd   = sim.first_node_death_round if sim.first_node_death_round is not None else MAX_ROUNDS + 1
    hnd   = sim.half_nodes_dead_round  if sim.half_nodes_dead_round  is not None else MAX_ROUNDS + 1
    alive = sim.alive_nodes_history[-1]
    energy = sim.total_energy_history[-1]
    return fnd, hnd, alive, energy


CONFIGS = {
    '1. Baseline (No Harvest)': dict(
        harvesting_profile=None,
        enable_dp_routing=False,
        enable_time_dp=False,
        enable_harvesting_ch=False,
        enable_live_reroute=False
    ),
    '2. Solar (Unaware LEACH)': dict(
        harvesting_profile='solar',
        harvesting_kwargs={'peak_rate': 0.0012, 'period': 24, 'day_fraction': 0.5},
        enable_dp_routing=False,
        enable_time_dp=False,
        enable_harvesting_ch=False,
        enable_live_reroute=False
    ),
    '3. Solar (Adaptive Time-DP)': dict(
        harvesting_profile='solar',
        harvesting_kwargs={'peak_rate': 0.0012, 'period': 24, 'day_fraction': 0.5},
        enable_dp_routing=True,
        enable_time_dp=True,
        enable_harvesting_ch=True,
        enable_live_reroute=True
    ),
    '4. Stochastic (Unaware LEACH)': dict(
        harvesting_profile='stochastic',
        harvesting_kwargs={'lambda_rate': 2.0, 'quantum': 0.0006},
        enable_dp_routing=False,
        enable_time_dp=False,
        enable_harvesting_ch=False,
        enable_live_reroute=False
    ),
    '5. Stochastic (Adaptive Time-DP)': dict(
        harvesting_profile='stochastic',
        harvesting_kwargs={'lambda_rate': 2.0, 'quantum': 0.0006},
        enable_dp_routing=True,
        enable_time_dp=True,
        enable_harvesting_ch=True,
        enable_live_reroute=True
    ),
    '6. Shadowed Solar (Unaware LEACH)': dict(
        harvesting_profile='heterogeneous_shadowed',
        harvesting_kwargs={'peak_rate': 0.0012, 'shadow_fraction': 0.5, 'shadow_penalty': 0.1, 'period': 24, 'day_fraction': 0.5},
        enable_dp_routing=False,
        enable_time_dp=False,
        enable_harvesting_ch=False,
        enable_live_reroute=False
    ),
    '7. Shadowed Solar (Adaptive Time-DP)': dict(
        harvesting_profile='heterogeneous_shadowed',
        harvesting_kwargs={'peak_rate': 0.0012, 'shadow_fraction': 0.5, 'shadow_penalty': 0.1, 'period': 24, 'day_fraction': 0.5},
        enable_dp_routing=True,
        enable_time_dp=True,
        enable_harvesting_ch=True,
        enable_live_reroute=True
    )
}


def run_multiseed_evaluation(num_seeds: int = 30):
    active_seeds = SEEDS[:num_seeds]
    n = len(active_seeds)
    print("=" * 84)
    print(f"MULTI-SEED STATISTICAL SIGNIFICANCE EVALUATION (N = {n} SEEDS)")
    print("=" * 84)

    raw_results = {name: {'fnd': [], 'hnd': [], 'alive': [], 'energy': []} for name in CONFIGS}

    for seed_idx, seed in enumerate(active_seeds, 1):
        print(f"Running Seed {seed_idx:02d}/{n:02d} (seed={seed})...")
        for name, cfg in CONFIGS.items():
            fnd, hnd, alive, energy = run_config(seed, **cfg)
            raw_results[name]['fnd'].append(fnd)
            raw_results[name]['hnd'].append(hnd)
            raw_results[name]['alive'].append(alive)
            raw_results[name]['energy'].append(energy)

    print("\n" + "=" * 84)
    print(f"{'Configuration':<35} | {'FND (Rounds)':<15} | {'Alive (Round 350)':<17} | {'Residual Energy (J)':<20}")
    print("-" * 84)

    for name in CONFIGS:
        f_arr = raw_results[name]['fnd']
        a_arr = raw_results[name]['alive']
        e_arr = raw_results[name]['energy']

        f_str = f"{np.mean(f_arr):.1f} +/- {np.std(f_arr, ddof=1):.1f}"
        a_str = f"{np.mean(a_arr):.1f} +/- {np.std(a_arr, ddof=1):.1f}"
        e_str = f"{np.mean(e_arr):.4f} +/- {np.std(e_arr, ddof=1):.4f}"
        print(f"{name:<35} | {f_str:<15} | {a_str:<17} | {e_str:<20}")

    # Paired Significance Tests
    print("\n" + "=" * 84)
    print("PAIRED STATISTICAL SIGNIFICANCE TESTS (Time-DP vs. Unaware Baseline)")
    print("=" * 84)

    comparisons = [
        ('Solar', '2. Solar (Unaware LEACH)', '3. Solar (Adaptive Time-DP)'),
        ('Stochastic', '4. Stochastic (Unaware LEACH)', '5. Stochastic (Adaptive Time-DP)'),
        ('Shadowed Solar', '6. Shadowed Solar (Unaware LEACH)', '7. Shadowed Solar (Adaptive Time-DP)')
    ]

    for label, base_name, dp_name in comparisons:
        base_e = np.array(raw_results[base_name]['energy'])
        dp_e = np.array(raw_results[dp_name]['energy'])
        diff_e = dp_e - base_e

        base_a = np.array(raw_results[base_name]['alive'])
        dp_a = np.array(raw_results[dp_name]['alive'])
        diff_a = dp_a - base_a

        # Paired t-test
        t_stat, p_ttest = stats.ttest_rel(dp_e, base_e)
        # Wilcoxon signed-rank test
        try:
            w_stat, p_wilcoxon = stats.wilcoxon(dp_e, base_e)
        except Exception:
            w_stat, p_wilcoxon = 0.0, 1.0

        # Cohen's d effect size for paired samples
        std_diff = np.std(diff_e, ddof=1)
        cohen_d = (np.mean(diff_e) / std_diff) if std_diff > 1e-9 else 0.0

        ci_low = np.mean(diff_e) - 1.96 * stats.sem(diff_e) if len(diff_e) > 1 else 0.0
        ci_high = np.mean(diff_e) + 1.96 * stats.sem(diff_e) if len(diff_e) > 1 else 0.0

        print(f"\nScenario: {label.upper()}")
        print(f"  Mean Energy Difference (Delta_E): {np.mean(diff_e):+.4f} J (95% CI: [{ci_low:.4f}, {ci_high:.4f}])")
        print(f"  Mean Alive Node Difference (Delta_Alive): {np.mean(diff_a):+.2f} nodes")
        print(f"  Paired t-test: t({n-1}) = {t_stat:.3f}, p = {p_ttest:.4e}")
        print(f"  Wilcoxon Signed-Rank: W = {w_stat:.1f}, p = {p_wilcoxon:.4e}")
        print(f"  Effect Size (Cohen's d): {cohen_d:.3f} ({'Large' if abs(cohen_d) >= 0.8 else 'Medium' if abs(cohen_d) >= 0.5 else 'Small'})")

    # Generate Boxplot
    os.makedirs('results', exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    config_labels = [
        'No Harvest',
        'Solar (Unaware)', 'Solar (Time-DP)',
        'Stoch (Unaware)', 'Stoch (Time-DP)',
        'Shadow (Unaware)', 'Shadow (Time-DP)'
    ]
    colors = ['#a0aec0', '#fc8181', '#63b3ed', '#f6ad55', '#4fd1c5', '#b794f4', '#68d391']

    alive_data = [raw_results[name]['alive'] for name in CONFIGS]
    energy_data = [raw_results[name]['energy'] for name in CONFIGS]

    bplot1 = ax1.boxplot(alive_data, patch_artist=True)
    for patch, color in zip(bplot1['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.85)
    ax1.set_title(f'Active Nodes at Round 350 across {n} Seeds', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Active Nodes Count', fontsize=10)
    ax1.set_xticks(range(1, len(config_labels) + 1))
    ax1.set_xticklabels(config_labels, rotation=35, ha='right', fontsize=9)
    ax1.grid(True, linestyle=':', alpha=0.6)

    bplot2 = ax2.boxplot(energy_data, patch_artist=True)
    for patch, color in zip(bplot2['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.85)
    ax2.set_title(f'Final Network Residual Energy across {n} Seeds', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Residual Energy (Joules)', fontsize=10)
    ax2.set_xticks(range(1, len(config_labels) + 1))
    ax2.set_xticklabels(config_labels, rotation=35, ha='right', fontsize=9)
    ax2.grid(True, linestyle=':', alpha=0.6)

    plt.tight_layout()
    plot_path = os.path.join('results', 'multiseed_boxplots.png')
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"\nSaved statistical boxplots to: {plot_path}")


if __name__ == '__main__':
    # Default to 30 seeds for full statistical power; or accept CLI override
    seeds_count = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    run_multiseed_evaluation(num_seeds=seeds_count)
