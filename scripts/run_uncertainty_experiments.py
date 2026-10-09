"""
Empirical Evaluation Script for Routing Under Energy Uncertainty in Renewable WSNs.

Benchmarks methods M0 to M5 across multiple regimes and common-random-number seeds:
- M0: Energy-blind Dijkstra (Shortest path baseline)
- M1: Energy-aware Dijkstra on Stale reports (Realistic baseline)
- M2: Oracle Time-DP (Omniscient theoretical upper bound)
- M3: Belief Max-Product Time-DP (Proposed method)
- M4: Belief LCB-Maximin DP (Ablation: conservative lower credible bound)
- M5: Belief Time-DP with No Waiting (Ablation: deadline w=0, isolates time dimension)

Computes:
- Packet Delivery Ratio (PDR), Latency, Energy Wasted, Brier Score, ECE, Oracle Gap Closed.
- Paired differences and Holm-corrected Wilcoxon signed-rank significance tests.
Outputs results to results/uncertainty_experiments.csv and generates a summary report.
"""

import argparse
import csv
import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from typing import Dict, List, Any, Tuple

import numpy as np

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from simulator import Simulator


REGIMES = {
    'poor': {
        'peak_rate': 0.00025,
        'solar_noise': 0.3,
        'report_interval': 20,
        'initial_energy': 0.015,
        'description': 'Severe solar scarcity, frequent brownouts, high telemetry delay'
    },
    'balanced': {
        'peak_rate': 0.0006,
        'solar_noise': 0.2,
        'report_interval': 10,
        'initial_energy': 0.02,
        'description': 'Balanced diurnal cycle, moderate brownout recovery'
    },
    'rich': {
        'peak_rate': 0.0020,
        'solar_noise': 0.1,
        'report_interval': 5,
        'initial_energy': 0.05,
        'description': 'Abundant solar harvesting, battery saturation common'
    }
}


def run_single_simulation(
    method_id: str,
    regime_name: str,
    seed: int,
    rounds: int = 100
) -> Dict[str, Any]:
    """Runs a single simulation instance for a specific method, regime, and seed."""
    cfg = REGIMES[regime_name]
    common_params = dict(
        num_nodes=50,
        area_width=100.0,
        area_height=100.0,
        base_station_pos=(50.0, 50.0),
        initial_energy=cfg['initial_energy'],
        max_battery_capacity=0.50,
        transmission_range=35.0,
        harvesting_profile='solar',
        harvesting_kwargs={'peak_rate': cfg['peak_rate'], 'period': 24, 'solar_noise': cfg['solar_noise']},
        seed=seed,
        report_interval=cfg['report_interval']
    )

    if method_id == 'M0':
        sim = Simulator(
            routing_algorithm='dijkstra',
            energy_view_type='blind',
            **common_params
        )
    elif method_id == 'M1':
        sim = Simulator(
            routing_algorithm='dijkstra',
            energy_view_type='stale',
            **common_params
        )
    elif method_id == 'M2':
        sim = Simulator(
            enable_time_dp=True,
            energy_view_type='oracle',
            **common_params
        )
    elif method_id == 'M3':
        sim = Simulator(
            enable_belief_dp=True,
            energy_view_type='histogram',
            belief_deadline_w=2,
            belief_reservations=True,
            **common_params
        )
    elif method_id == 'M4':
        sim = Simulator(
            enable_belief_dp=True,
            energy_view_type='histogram',
            belief_deadline_w=2,
            belief_lcb_z=1.0,
            belief_reservations=True,
            **common_params
        )
    elif method_id == 'M5':
        sim = Simulator(
            enable_belief_dp=True,
            energy_view_type='histogram',
            belief_deadline_w=0,
            belief_reservations=True,
            **common_params
        )
    else:
        raise ValueError(f"Unknown method {method_id}")

    sim.run(max_rounds=rounds, verbose=False)

    gen = sum(sim.packets_generated_history)
    deliv = sum(sim.packets_delivered_history)
    pdr = deliv / max(1, gen)
    latency = np.mean(sim.latency_history) if sim.latency_history else 1.0
    wasted = sum(sim.energy_wasted_history)
    calib = sim.get_calibration_metrics()

    return {
        'method': method_id,
        'regime': regime_name,
        'seed': seed,
        'rounds': rounds,
        'generated': gen,
        'delivered': deliv,
        'pdr': pdr,
        'latency': latency,
        'energy_wasted': wasted,
        'brier_score': calib['brier_score'],
        'ece': calib['ece']
    }


def wilcoxon_signed_rank_approx(diffs: List[float]) -> Tuple[float, float]:
    """Computes paired Wilcoxon signed rank test statistic and two-tailed p-value."""
    non_zero = [d for d in diffs if abs(d) > 1e-9]
    n = len(non_zero)
    if n < 5:
        # Fallback to sign test or paired t-test for very small samples
        mean_d = np.mean(diffs)
        se = np.std(diffs, ddof=1) / math.sqrt(max(1, len(diffs)))
        t_stat = mean_d / max(1e-9, se)
        # Approximate p-value
        p_val = 2.0 * (1.0 - 0.5 * (1.0 + math.erf(abs(t_stat) / math.sqrt(2.0))))
        return float(t_stat), float(max(1e-6, min(1.0, p_val)))

    ranks = np.argsort(np.abs(non_zero)) + 1
    w_pos = sum(r for r, d in zip(ranks, non_zero) if d > 0)
    w_neg = sum(r for r, d in zip(ranks, non_zero) if d < 0)
    w_stat = min(w_pos, w_neg)

    # Normal approximation for W
    mean_w = n * (n + 1) / 4.0
    var_w = n * (n + 1) * (2 * n + 1) / 24.0
    z = (w_stat - mean_w) / math.sqrt(var_w)
    p_val = 2.0 * 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))
    return float(w_stat), float(max(1e-6, min(1.0, p_val)))


def holm_bonferroni(p_values: List[float]) -> List[float]:
    """Applies Holm-Bonferroni correction to a list of p-values."""
    m = len(p_values)
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    adjusted = [0.0] * m
    cum_max = 0.0

    for rank, (orig_idx, p) in enumerate(indexed):
        adj = p * (m - rank)
        cum_max = max(cum_max, adj)
        adjusted[orig_idx] = min(1.0, cum_max)

    return adjusted


def main():
    parser = argparse.ArgumentParser(description="Run WSN Energy Routing Uncertainty Experiments.")
    parser.add_argument('--seeds', type=int, default=10, help="Number of CRN seeds (default: 10)")
    parser.add_argument('--rounds', type=int, default=100, help="Rounds per run (default: 100)")
    parser.add_argument('--workers', type=int, default=4, help="Parallel worker threads (default: 4)")
    parser.add_argument('--out', type=str, default="results/uncertainty_experiments.csv", help="Output CSV path")
    args = parser.parse_args()

    seeds = [42 + 97 * i for i in range(args.seeds)]
    methods = ['M0', 'M1', 'M2', 'M3', 'M4', 'M5']
    regimes = ['poor', 'balanced', 'rich']

    total_runs = len(regimes) * len(methods) * len(seeds)
    print(f"Starting Uncertainty Routing Benchmark Experiments...")
    print(f"Regimes: {regimes} | Methods: {methods} | Seeds: {len(seeds)} | Total runs: {total_runs}")

    tasks = [
        (m, reg, s, args.rounds)
        for reg in regimes
        for m in methods
        for s in seeds
    ]

    results = []
    # Execute with worker pool
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(run_single_simulation, *t) for t in tasks]
        for idx, fut in enumerate(futures):
            res = fut.result()
            results.append(res)
            if (idx + 1) % max(1, total_runs // 10) == 0 or (idx + 1) == total_runs:
                print(f"Progress: {idx + 1}/{total_runs} runs completed ({(idx + 1)/total_runs*100:.1f}%)")

    # Save to CSV
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    fieldnames = ['method', 'regime', 'seed', 'rounds', 'generated', 'delivered', 'pdr', 'latency', 'energy_wasted', 'brier_score', 'ece']
    with open(args.out, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    print(f"\nSaved detailed run results to {args.out}")

    # Aggregate Analysis & Statistical Reporting
    print("\n" + "="*80)
    print("EXPERIMENTAL SUMMARY REPORT: ROUTING UNDER ENERGY UNCERTAINTY")
    print("="*80)

    for reg in regimes:
        reg_results = [r for r in results if r['regime'] == reg]
        print(f"\n--- REGIME: {reg.upper()} ({REGIMES[reg]['description']}) ---")
        print(f"{'Method':<8} | {'PDR (%)':<18} | {'Latency':<8} | {'Wasted (J)':<10} | {'Brier':<8} | {'ECE':<8} | {'Oracle Gap Closed'}")
        print("-" * 88)

        reg_data = {}
        for m in methods:
            m_res = [r for r in reg_results if r['method'] == m]
            pdrs = [r['pdr'] * 100 for r in m_res]
            lats = [r['latency'] for r in m_res]
            wasts = [r['energy_wasted'] for r in m_res]
            briers = [r['brier_score'] for r in m_res]
            eces = [r['ece'] for r in m_res]
            reg_data[m] = {
                'pdrs': pdrs,
                'mean_pdr': np.mean(pdrs),
                'std_pdr': np.std(pdrs),
                'mean_lat': np.mean(lats),
                'mean_wast': np.mean(wasts),
                'mean_brier': np.mean(briers),
                'mean_ece': np.mean(eces)
            }

        m0_mean = reg_data['M0']['mean_pdr']
        m2_mean = reg_data['M2']['mean_pdr']
        oracle_spread = max(0.1, m2_mean - m0_mean)

        for m in methods:
            d = reg_data[m]
            gap_closed = (d['mean_pdr'] - m0_mean) / oracle_spread * 100.0
            gap_str = f"{gap_closed:+.1f}%" if m not in ('M0', 'M2') else ("--" if m == 'M0' else "100.0%")
            pdr_str = f"{d['mean_pdr']:.2f}% ± {d['std_pdr']:.2f}%"
            print(f"{m:<8} | {pdr_str:<18} | {d['mean_lat']:<8.2f} | {d['mean_wast']:<10.4f} | {d['mean_brier']:<8.4f} | {d['mean_ece']:<8.4f} | {gap_str}")

        # Statistical paired tests
        diffs_m3_m1 = [b - a for a, b in zip(reg_data['M1']['pdrs'], reg_data['M3']['pdrs'])]
        diffs_m3_m0 = [b - a for a, b in zip(reg_data['M0']['pdrs'], reg_data['M3']['pdrs'])]
        diffs_m3_m5 = [b - a for a, b in zip(reg_data['M5']['pdrs'], reg_data['M3']['pdrs'])]

        w1, p1 = wilcoxon_signed_rank_approx(diffs_m3_m1)
        w0, p0 = wilcoxon_signed_rank_approx(diffs_m3_m0)
        w5, p5 = wilcoxon_signed_rank_approx(diffs_m3_m5)

        raw_p = [p1, p0, p5]
        adj_p = holm_bonferroni(raw_p)

        print("\nPaired Statistical Significance Tests (Holm-corrected):")
        print(f"  M3 vs M1 (Belief vs Stale):   Delta = {np.mean(diffs_m3_m1):+.2f}%, raw p = {p1:.4f}, adj p = {adj_p[0]:.4f}")
        print(f"  M3 vs M0 (Belief vs Blind):   Delta = {np.mean(diffs_m3_m0):+.2f}%, raw p = {p0:.4f}, adj p = {adj_p[1]:.4f}")
        print(f"  M3 vs M5 (Wait vs No-Wait):   Delta = {np.mean(diffs_m3_m5):+.2f}%, raw p = {p5:.4f}, adj p = {adj_p[2]:.4f}")

    print("\n" + "="*80)
    print("Benchmark experiments successfully completed.")
    print("="*80)


if __name__ == '__main__':
    main()
