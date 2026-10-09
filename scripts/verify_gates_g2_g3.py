"""
Gate G2 and G3 verification script.
Evaluates M0 (Blind), M1 (Stale), M2 (Oracle), M3 (Belief DP), M4 (LCB), M5 (No-Wait)
in the Balanced solar regime across multiple common-random-number seeds.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from simulator import Simulator
import numpy as np


def run_experiment(seed: int, regime: str = 'poor', rounds: int = 120):
    if regime == 'poor':
        h_kwargs = {'peak_rate': 0.00025, 'period': 24, 'solar_noise': 0.3}
        rep_int = 20
        init_e = 0.015
    else:
        h_kwargs = {'peak_rate': 0.0006, 'period': 24, 'solar_noise': 0.2}
        rep_int = 10
        init_e = 0.02

    common_params = dict(
        num_nodes=50,
        area_width=100.0,
        area_height=100.0,
        base_station_pos=(50.0, 50.0),
        initial_energy=init_e,
        max_battery_capacity=0.50,
        transmission_range=35.0,
        harvesting_profile='solar',
        harvesting_kwargs=h_kwargs,
        seed=seed
    )

    # M0: Blind Dijkstra
    sim_m0 = Simulator(
        routing_algorithm='dijkstra',
        energy_view_type='blind',
        report_interval=rep_int,
        **common_params
    )
    sim_m0.run(max_rounds=rounds, verbose=False)
    pdr_m0 = sum(sim_m0.packets_delivered_history) / max(1, sum(sim_m0.packets_generated_history))

    # M1: Stale Dijkstra
    sim_m1 = Simulator(
        routing_algorithm='dijkstra',
        energy_view_type='stale',
        report_interval=rep_int,
        **common_params
    )
    sim_m1.run(max_rounds=rounds, verbose=False)
    pdr_m1 = sum(sim_m1.packets_delivered_history) / max(1, sum(sim_m1.packets_generated_history))

    # M2: Oracle Time-DP
    sim_m2 = Simulator(
        enable_time_dp=True,
        energy_view_type='oracle',
        report_interval=rep_int,
        **common_params
    )
    sim_m2.run(max_rounds=rounds, verbose=False)
    pdr_m2 = sum(sim_m2.packets_delivered_history) / max(1, sum(sim_m2.packets_generated_history))

    # M3: Belief Max-Product DP (Proposed)
    sim_m3 = Simulator(
        enable_belief_dp=True,
        energy_view_type='histogram',
        report_interval=rep_int,
        belief_deadline_w=2,
        belief_reservations=True,
        **common_params
    )
    sim_m3.run(max_rounds=rounds, verbose=False)
    pdr_m3 = sum(sim_m3.packets_delivered_history) / max(1, sum(sim_m3.packets_generated_history))
    calib_m3 = sim_m3.get_calibration_metrics()

    # M5: Belief DP without waiting (Ablation)
    sim_m5 = Simulator(
        enable_belief_dp=True,
        energy_view_type='histogram',
        report_interval=rep_int,
        belief_deadline_w=0,
        belief_reservations=True,
        **common_params
    )
    sim_m5.run(max_rounds=rounds, verbose=False)
    pdr_m5 = sum(sim_m5.packets_delivered_history) / max(1, sum(sim_m5.packets_generated_history))

    return {
        'seed': seed,
        'm0_blind': pdr_m0,
        'm1_stale': pdr_m1,
        'm2_oracle': pdr_m2,
        'm3_belief': pdr_m3,
        'm5_nowait': pdr_m5,
        'm3_brier': calib_m3['brier_score'],
        'm3_ece': calib_m3['ece']
    }


def main():
    seeds = [42, 101, 202, 303, 404]
    
    for regime in ['poor', 'balanced']:
        print(f"\n=======================================================")
        print(f"Running verification sweep for '{regime.upper()}' regime across {len(seeds)} seeds...")
        print(f"=======================================================")
        results = [run_experiment(s, regime=regime) for s in seeds]

        m0_vals = [r['m0_blind'] for r in results]
        m1_vals = [r['m1_stale'] for r in results]
        m2_vals = [r['m2_oracle'] for r in results]
        m3_vals = [r['m3_belief'] for r in results]
        m5_vals = [r['m5_nowait'] for r in results]
        briers = [r['m3_brier'] for r in results]
        eces = [r['m3_ece'] for r in results]

        print(f"\n--- {regime.capitalize()} Regime Results ---")
        print(f"M0 (Blind Dijkstra):        {np.mean(m0_vals)*100:.2f}% ± {np.std(m0_vals)*100:.2f}%")
        print(f"M1 (Stale Dijkstra):        {np.mean(m1_vals)*100:.2f}% ± {np.std(m1_vals)*100:.2f}%")
        print(f"M3 (Belief Max-Product DP): {np.mean(m3_vals)*100:.2f}% ± {np.std(m3_vals)*100:.2f}%")
        print(f"M5 (Belief DP, No-Wait):    {np.mean(m5_vals)*100:.2f}% ± {np.std(m5_vals)*100:.2f}%")
        print(f"M2 (Oracle Time-DP):        {np.mean(m2_vals)*100:.2f}% ± {np.std(m2_vals)*100:.2f}%")
        print(f"M3 Brier Score:             {np.mean(briers):.4f}")
        print(f"M3 Expected Calib Error:    {np.mean(eces):.4f}")

        gap_oracle_blind = (np.mean(m2_vals) - np.mean(m0_vals)) * 100.0
        gap_belief_stale = (np.mean(m3_vals) - np.mean(m1_vals)) * 100.0
        oracle_gap_closed = (np.mean(m3_vals) - np.mean(m0_vals)) / max(1e-6, (np.mean(m2_vals) - np.mean(m0_vals))) * 100.0

        print(f"\nOracle vs Blind Gap: {gap_oracle_blind:+.2f} percentage points")
        print(f"Belief vs Stale Gap: {gap_belief_stale:+.2f} percentage points")
        print(f"Oracle Gap Closed by Belief DP: {oracle_gap_closed:.1f}%")

        if gap_oracle_blind >= 5.0:
            print(f">>> GATE G2 PASSED in {regime} regime: Gap >= 5 percentage points ({gap_oracle_blind:+.2f}%).")
        else:
            print(f">>> GATE G2 WARNING in {regime} regime: Gap < 5 percentage points ({gap_oracle_blind:+.2f}%).")

        if np.mean(m3_vals) > np.mean(m1_vals):
            print(f">>> GATE G3 PASSED in {regime} regime: Belief DP outperforms Stale reports ({gap_belief_stale:+.2f}%).")
        else:
            print(f">>> GATE G3 in {regime} regime: Stale reports competitive with Belief DP ({gap_belief_stale:+.2f}%).")


if __name__ == '__main__':
    main()
