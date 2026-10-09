"""
Gate G1 Empirical Regime Sweep Script.

Sweeps solar harvest peak rates across multiple seeds to map the
harvest/consumption ratio against node brownout events and delivery ratio,
identifying the Poor, Balanced, and Rich regimes required for Gate G1.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from simulator import Simulator
import numpy as np


def run_regime_sweep():
    # Canonical parameters unified in P0
    num_nodes = 50
    area = 100.0
    bs_pos = (50.0, 50.0)
    init_energy = 0.020      # 20 mJ initial buffer to observe diurnal transition within 300 rounds
    max_capacity = 0.50      # 500 mJ
    cluster_ratio = 0.08
    tx_range = 35.0
    max_rounds = 300
    seeds = [42, 123, 999]

    # Test sweep of solar peak rates (J/round)
    # Covering severely energy-negative to energy-surplus conditions
    solar_peaks = [0.0001, 0.0003, 0.0006, 0.0015, 0.0040]

    print("=" * 95)
    print("GATE G1 REGIME MAP: HARVEST/CONSUMPTION RATIO VS BROWNOUTS (3 SEEDS AVERAGE)")
    print("=" * 95)
    header = f"{'Solar Peak (mJ)':<16} | {'H/L Ratio':<10} | {'Total Harv (J)':<15} | {'Brownout Node-Rounds':<22} | {'PDR (%)':<10} | {'Regime'}"
    print(header)
    print("-" * 95)

    results = []

    for peak in solar_peaks:
        hl_ratios = []
        harv_totals = []
        brownout_slots = []
        pdrs = []

        for s in seeds:
            sim = Simulator(
                num_nodes=num_nodes,
                area_width=area,
                area_height=area,
                base_station_pos=bs_pos,
                initial_energy=init_energy,
                max_battery_capacity=max_capacity,
                desired_clusters_ratio=cluster_ratio,
                transmission_range=tx_range,
                harvesting_profile='solar',
                harvesting_kwargs={'peak_rate': peak, 'period': 24, 'day_fraction': 0.5, 'seed': s},
                routing_algorithm='dijkstra',
                energy_view_type='oracle',
                seed=s
            )
            sim.run(max_rounds=max_rounds, verbose=False)

            tot_harv = sum(sim.harvested_energy_history)
            tot_cons = sum(sim.consumed_energy_history)
            hl = (tot_harv / max(1e-6, tot_cons))
            b_slots = sum(sim.brownout_history)
            pdr = (sum(sim.packets_delivered_history) / max(1, sum(sim.packets_generated_history))) * 100.0

            hl_ratios.append(hl)
            harv_totals.append(tot_harv)
            brownout_slots.append(b_slots)
            pdrs.append(pdr)

        avg_hl = float(np.mean(hl_ratios))
        avg_harv = float(np.mean(harv_totals))
        avg_brown = float(np.mean(brownout_slots))
        avg_pdr = float(np.mean(pdrs))

        # Regime classification criteria:
        # Poor: H/L < 0.65, widespread sustained brownouts
        # Balanced: 0.65 <= H/L <= 1.5, nodes brown out at night or during heavy routing load
        # Rich: H/L > 1.5, batteries remain replenished, near zero brownouts
        if avg_hl < 0.65:
            regime = "POOR (Heavy Brownouts)"
        elif avg_hl <= 1.50:
            regime = "BALANCED (Diurnal Brownouts)"
        else:
            regime = "RICH (Near Zero Brownouts)"

        results.append({
            'peak_mj': peak * 1000.0,
            'hl_ratio': avg_hl,
            'tot_harv': avg_harv,
            'brownout_slots': avg_brown,
            'pdr': avg_pdr,
            'regime': regime
        })

        print(f"{peak * 1000.0:<16.1f} | {avg_hl:<10.2f} | {avg_harv:<15.3f} | {avg_brown:<22.1f} | {avg_pdr:<10.1f} | {regime}")

    print("=" * 95)
    # Verify Gate G1 condition: at least 2 regimes where nodes brown out
    brownout_regimes = set(r['regime'].split()[0] for r in results if r['brownout_slots'] > 10.0)
    print(f"\nGate G1 Check: Regimes with verified brownouts: {sorted(list(brownout_regimes))}")
    if len(brownout_regimes) >= 2:
        print("[GATE G1 PASSED]: Confirmed at least two distinct regimes with brownouts (POOR and BALANCED).")
    else:
        print("[GATE G1 FAILED]: Less than 2 regimes with brownouts.")

    return results


if __name__ == "__main__":
    run_regime_sweep()
