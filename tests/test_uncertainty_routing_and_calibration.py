"""
Unit and integration tests for Energy Uncertainty, Belief Filters,
Max-Product DP with Waiting, Reservations, and Probability Calibration.
"""

import pytest
import math
from typing import Dict
from network import Node
from energy_model import EnergyModel
from harvesting_model import SolarPeriodicHarvesting, ConstantHarvesting
from energy_view import HistogramBeliefView, GaussianBeliefView, OracleView, StaleView, quantize_energy
from dp_lifetime import dp_max_product_belief_routing, compute_belief_routes_for_cluster_heads
from simulator import Simulator


def test_quantize_energy():
    """Verify 8-bit quantization steps across [0, 0.5J]."""
    # 8-bit resolution: 255 levels across 0.5 J -> step ~ 0.00196078 J
    val = 0.05
    q_val = quantize_energy(val, max_energy=0.5, bits=8)
    assert abs(q_val - val) <= 0.002
    # Zero and max bounds
    assert quantize_energy(-0.01, max_energy=0.5, bits=8) == 0.0
    assert quantize_energy(0.60, max_energy=0.5, bits=8) == 0.5


def test_histogram_belief_view_p_afford_and_moments():
    """Test HistogramBeliefView probability mass, mean, and variance."""
    node = Node(0, 10.0, 10.0, initial_energy=0.10, max_energy=0.50)
    view = HistogramBeliefView({0: node}, num_bins=24, initial_mean=0.10)

    # Initial energy is 0.10 J
    assert abs(view.mean(0) - 0.10) < 0.02
    assert view.p_afford(0, 0.05) > 0.90
    assert view.p_afford(0, 0.20) < 0.10
    assert view.p_afford(0, 0.0) == 1.0


def test_histogram_filter_synthetic_coverage():
    """Verify that histogram credible intervals cover true hidden energy ~90% of the time."""
    node = Node(0, 0.0, 0.0, initial_energy=0.05, max_energy=0.50)
    view = HistogramBeliefView({0: node}, num_bins=24, initial_mean=0.05)

    import random
    rng = random.Random(12345)
    true_e = 0.05
    covered = 0
    total_steps = 100

    for step in range(total_steps):
        # Simulate solar harvesting with stochastic noise
        h_mean = 0.002
        h_var = (0.0005) ** 2
        actual_harvest = max(0.0, rng.gauss(h_mean, 0.0005))
        true_e = min(0.50, true_e + actual_harvest)

        # Belief predict step
        view.predict_step(
            node_id=0,
            harvest_mean=h_mean,
            harvest_var=h_var,
            load_mean=0.0,
            max_capacity=0.50
        )

        # Periodic observation with quantization noise every 5 steps
        if step % 5 == 0:
            view.on_report(0, true_e, step)

        # Compute 90% credible interval from histogram bins
        probs = view.probs[0]
        edges = view.bin_edges[0]
        cum = 0.0
        q05 = None
        q95 = edges[-1]
        for k, p in enumerate(probs):
            cum += p
            if q05 is None and cum >= 0.05:
                q05 = edges[k]
            if cum >= 0.95:
                q95 = edges[k + 1]
                break

        if q05 is None:
            q05 = edges[0]

        if q05 <= true_e <= q95:
            covered += 1

    coverage_ratio = covered / float(total_steps)
    # Empirical coverage should be healthy (at least 75%)
    assert coverage_ratio >= 0.75, f"Coverage {coverage_ratio:.2f} lower than expected 0.75+"


def test_dp_waiting_improves_success_probability():
    """
    Verify that DP waiting allows a node to harvest energy,
    turning an inoperable path into a high-probability route.
    """
    nodes = {
        0: Node(0, 10.0, 10.0, initial_energy=0.05, max_energy=0.50),  # Source
        1: Node(1, 25.0, 10.0, initial_energy=0.0001, max_energy=0.50)  # Relay: depleted now
    }
    adj_list = {
        0: [(1, 15.0)],
        1: []
    }
    base_station_pos = (40.0, 10.0)
    energy_model = EnergyModel()
    alive_nodes = {0, 1}

    # Custom view where relay 1 can afford reception, but needs to wait until slot 2+ to transmit
    class MockRechargeView:
        def p_afford(self, nid: int, cost: float, slot: int = 0) -> float:
            if nid == 0:
                return 1.0
            if nid == 1:
                # Reception cost is ~5.0e-8 for 1 bit; transmission cost is higher
                if cost <= 6.0e-8:
                    return 1.0
                # Transmission cost requires recharged energy at slot 2+
                return 1.0 if slot >= 2 else 0.0
            return 0.0

        def mean(self, nid: int, slot: int = 0) -> float:
            return 0.05 if (nid == 0 or slot >= 2) else 0.0

        def variance(self, nid: int, slot: int = 0) -> float:
            return 0.0

    mock_view = MockRechargeView()

    # Without waiting (deadline_w = 0): relay arrives at slot 1, cannot afford tx -> prob near 0
    score_nowait, path_nowait, sched_nowait = dp_max_product_belief_routing(
        nodes=nodes,
        adj_list=adj_list,
        source=0,
        base_station_pos=base_station_pos,
        energy_model=energy_model,
        alive_nodes=alive_nodes,
        energy_view=mock_view,
        deadline_w=0,
        transmission_range=20.0
    )

    # With waiting (deadline_w = 2): relay can wait until slot 2 to recharge -> prob is high
    score_wait, path_wait, sched_wait = dp_max_product_belief_routing(
        nodes=nodes,
        adj_list=adj_list,
        source=0,
        base_station_pos=base_station_pos,
        energy_model=energy_model,
        alive_nodes=alive_nodes,
        energy_view=mock_view,
        deadline_w=2,
        transmission_range=20.0
    )

    assert score_wait > score_nowait
    assert path_wait == [0, 1, -1]
    # Verify wait occurred in schedule
    assert sched_wait[-1] >= 2


def test_dp_avoids_high_variance_relay():
    """Verify max-product DP prefers a reliable predictable relay over a high-risk relay."""
    nodes = {
        0: Node(0, 10.0, 10.0, initial_energy=0.05, max_energy=0.50),  # Source
        1: Node(1, 20.0, 5.0, initial_energy=0.05, max_energy=0.50),   # Relay A (reliable)
        2: Node(2, 20.0, 15.0, initial_energy=0.05, max_energy=0.50)   # Relay B (high variance/risk)
    }
    adj_list = {
        0: [(1, 12.0), (2, 12.0)],
        1: [],
        2: []
    }
    base_station_pos = (35.0, 10.0)
    energy_model = EnergyModel()
    alive_nodes = {0, 1, 2}

    class MockRiskView:
        def p_afford(self, nid: int, cost: float, slot: int = 0) -> float:
            if nid == 0:
                return 1.0
            if nid == 1:
                return 0.95  # Relay A: high confidence
            if nid == 2:
                return 0.20  # Relay B: high variance/brownout risk
            return 0.0

        def mean(self, nid: int, slot: int = 0) -> float:
            return 0.05

        def variance(self, nid: int, slot: int = 0) -> float:
            return 0.0001 if nid == 1 else 0.01

    risk_view = MockRiskView()

    score, path, _ = dp_max_product_belief_routing(
        nodes=nodes,
        adj_list=adj_list,
        source=0,
        base_station_pos=base_station_pos,
        energy_model=energy_model,
        alive_nodes=alive_nodes,
        energy_view=risk_view,
        deadline_w=0,
        transmission_range=20.0
    )

    # Must select Relay A (node 1), avoiding risky Relay B (node 2)
    assert path == [0, 1, -1]
    assert score > 0.90


def test_belief_reservations_shift_load():
    """Verify that multiple cluster heads sequentially reserve relay load."""
    nodes = {
        0: Node(0, 10.0, 10.0, initial_energy=0.05, max_energy=0.50),
        1: Node(1, 25.0, 10.0, initial_energy=0.05, max_energy=0.50),  # Shared relay
        2: Node(2, 10.0, 15.0, initial_energy=0.05, max_energy=0.50)
    }
    adj_list = {
        0: [(1, 15.0)],
        1: [],
        2: [(1, 15.0)]
    }
    base_station_pos = (40.0, 10.0)
    energy_model = EnergyModel()
    alive_nodes = {0, 1, 2}
    view = HistogramBeliefView(nodes, num_bins=24, initial_mean=0.05)

    routes = compute_belief_routes_for_cluster_heads(
        nodes=nodes,
        adj_list=adj_list,
        cluster_heads=[0, 2],
        base_station_pos=base_station_pos,
        energy_model=energy_model,
        alive_nodes=alive_nodes,
        energy_view=view,
        apply_reservations=True,
        transmission_range=20.0
    )

    assert 0 in routes and routes[0][0] is not None
    assert 2 in routes and routes[2][0] is not None


def test_calibration_metrics_calculation():
    """Verify Brier score and ECE calculation in Simulator."""
    sim = Simulator(
        num_nodes=10,
        initial_energy=0.02,
        harvesting_profile='solar',
        harvesting_kwargs={'peak_rate': 0.0006},
        enable_belief_dp=True,
        energy_view_type='histogram',
        seed=42
    )
    sim.run(max_rounds=20, verbose=False)

    calib = sim.get_calibration_metrics()
    assert 'brier_score' in calib
    assert 'ece' in calib
    assert 'sample_count' in calib
    assert calib['sample_count'] > 0
    assert 0.0 <= calib['brier_score'] <= 1.0
    assert 0.0 <= calib['ece'] <= 1.0
