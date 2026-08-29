"""
Multi-seed statistical validation for WSN energy routing configurations.

Runs all 5 configurations across multiple random seeds and reports
mean +/- std for FND, HND, alive nodes, and residual energy.
This is the rigorous answer to "is the improvement real or seed-specific?"
"""

import sys
import math
sys.path.append('src')

from simulator import Simulator

SEEDS = [42, 7, 123, 256, 999]

NUM_NODES      = 50
AREA           = 100.0
BS_POS         = (50.0, 50.0)
INIT_ENERGY    = 0.045
MAX_CAPACITY   = 0.50
CLUSTER_RATIO  = 0.08
MAX_ROUNDS     = 350


def mean(vals):
    return sum(vals) / len(vals) if vals else 0.0


def std(vals):
    if len(vals) < 2:
        return 0.0
    m = mean(vals)
    return math.sqrt(sum((v - m) ** 2 for v in vals) / (len(vals) - 1))


def run_config(seed, **kwargs):
    sim = Simulator(
        num_nodes=NUM_NODES,
        area_width=AREA,
        area_height=AREA,
        base_station_pos=BS_POS,
        initial_energy=INIT_ENERGY,
        max_battery_capacity=MAX_CAPACITY,
        desired_clusters_ratio=CLUSTER_RATIO,
        enable_dp_routing=False,
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
    'Baseline (No Harvest)': dict(
        harvesting_profile=None,
        enable_time_dp=False, enable_harvesting_ch=False, enable_live_reroute=False,
    ),
    'Solar - Unaware': dict(
        harvesting_profile='solar',
        harvesting_kwargs={'peak_rate': 0.0006, 'period': 24, 'day_fraction': 0.5},
        enable_time_dp=False, enable_harvesting_ch=False, enable_live_reroute=False,
    ),
    'Solar - Adaptive (Time-DP)': dict(
        harvesting_profile='solar',
        harvesting_kwargs={'peak_rate': 0.0006, 'period': 24, 'day_fraction': 0.5},
        enable_time_dp=True, enable_harvesting_ch=True, enable_live_reroute=True,
        max_dp_hops=5,
    ),
    'Stochastic - Unaware': dict(
        harvesting_profile='stochastic',
        harvesting_kwargs={'lambda_rate': 2.0, 'quantum': 0.00015},
        enable_time_dp=False, enable_harvesting_ch=False, enable_live_reroute=False,
    ),
    'Stochastic - Adaptive (Time-DP)': dict(
        harvesting_profile='stochastic',
        harvesting_kwargs={'lambda_rate': 2.0, 'quantum': 0.00015},
        enable_time_dp=True, enable_harvesting_ch=True, enable_live_reroute=True,
        max_dp_hops=5,
    ),
}


def main():
    print("=" * 72)
    print(f"Multi-Seed Statistical Validation  (seeds = {SEEDS})")
    print(f"50 nodes | 350 rounds | 100x100 m | E0 = {INIT_ENERGY} J")
    print("=" * 72)

    results = {}

    for cfg_name, cfg_kwargs in CONFIGS.items():
        print(f"\n  {cfg_name}")
        fnd_list, hnd_list, alive_list, energy_list = [], [], [], []

        for seed in SEEDS:
            kw = dict(cfg_kwargs)
            if 'harvesting_kwargs' in kw and kw['harvesting_kwargs'] is not None:
                kw['harvesting_kwargs'] = dict(kw['harvesting_kwargs'], seed=seed)

            fnd, hnd, alive, energy = run_config(seed, **kw)
            fnd_list.append(fnd)
            hnd_list.append(hnd)
            alive_list.append(alive)
            energy_list.append(energy)
            print(f"    seed={seed:>4}: FND={fnd:>4}  HND={hnd:>4}  Alive={alive:>2}/50  E={energy:.4f}J")

        results[cfg_name] = dict(
            fnd=fnd_list, hnd=hnd_list, alive=alive_list, energy=energy_list
        )

    print("\n\n" + "=" * 72)
    print("Summary  (mean +/- std, N=" + str(len(SEEDS)) + ")")
    print("=" * 72)

    header = f"{'Configuration':<36} | {'FND (mean+/-std)':<18} | {'Alive (mean+/-std)':<18} | {'Energy (mean+/-std)':<20}"
    print(header)
    print("-" * len(header))

    for cfg_name, r in results.items():
        fnd_m,   fnd_s   = mean(r['fnd']),   std(r['fnd'])
        alive_m, alive_s = mean(r['alive']), std(r['alive'])
        e_m,     e_s     = mean(r['energy']), std(r['energy'])
        print(
            f"{cfg_name:<36} | "
            f"{fnd_m:>6.1f} +/- {fnd_s:>5.1f}  | "
            f"{alive_m:>5.1f} +/- {alive_s:>4.1f}     | "
            f"{e_m:.4f} +/- {e_s:.4f}"
        )

    print()
    su  = results['Stochastic - Unaware']
    sa  = results['Stochastic - Adaptive (Time-DP)']
    delta_fnd   = mean(sa['fnd'])   - mean(su['fnd'])
    delta_alive = mean(sa['alive']) - mean(su['alive'])
    print(f"Key comparison (Stochastic Adaptive vs Unaware):")
    print(f"  delta FND   = {delta_fnd:+.1f} rounds  (pooled std: {std(su['fnd'] + sa['fnd']):.1f})")
    print(f"  delta Alive = {delta_alive:+.2f} nodes   (pooled std: {std(su['alive'] + sa['alive']):.2f})")
    print()


if __name__ == '__main__':
    main()
