"""
Unit tests for EnergyView interfaces and implementations:
- Protocol conformance
- OracleView
- BlindView
- StaleView
- GaussianBeliefView
"""

import pytest
import math
from network import Node
from energy_view import EnergyView, OracleView, BlindView, StaleView, GaussianBeliefView


def test_energy_view_protocol_conformance():
    nodes = {0: Node(0, 0, 0, initial_energy=1.0)}
    oracle = OracleView(nodes)
    blind = BlindView(nodes)
    stale = StaleView(nodes)
    gaussian = GaussianBeliefView(nodes)

    assert isinstance(oracle, EnergyView)
    assert isinstance(blind, EnergyView)
    assert isinstance(stale, EnergyView)
    assert isinstance(gaussian, EnergyView)


def test_oracle_view_exactness():
    n = Node(0, 0, 0, initial_energy=0.5)
    nodes = {0: n}
    view = OracleView(nodes)

    assert view.mean(0) == 0.5
    assert view.variance(0) == 0.0
    assert view.p_afford(0, 0.4) == 1.0
    assert view.p_afford(0, 0.6) == 0.0
    assert view.is_available(0) is True

    # Deduct energy
    n.consume_energy(0.5)
    assert n.is_alive is False
    assert view.p_afford(0, 0.1) == 0.0
    assert view.is_available(0) is False


def test_blind_view():
    n = Node(0, 0, 0, initial_energy=0.5)
    nodes = {0: n}
    view = BlindView(nodes, default_energy=2.0)

    assert view.mean(0) == 2.0
    assert view.p_afford(0, 10.0) == 1.0
    assert view.is_available(0) is True

    n.consume_energy(0.5)
    assert view.p_afford(0, 10.0) == 0.0
    assert view.is_available(0) is False


def test_stale_view_and_censoring():
    n = Node(0, 0, 0, initial_energy=0.5)
    nodes = {0: n}
    view = StaleView(nodes, initial_energy=0.5)

    assert view.mean(0) == 0.5
    assert view.p_afford(0, 0.4) == 1.0
    assert view.p_afford(0, 0.6) == 0.0

    # True node energy decreases silently without report
    n.consume_energy(0.3)  # true energy is 0.2
    assert view.mean(0) == 0.5  # stale view doesn't know yet

    # Censored update on failure with cost 0.3
    view.on_failure(0, cost=0.3)
    assert view.mean(0) < 0.3
    assert view.p_afford(0, 0.3) == 0.0

    # Report update
    view.on_report(0, value=0.15, round_num=5)
    assert view.mean(0) == 0.15
    assert view.p_afford(0, 0.1) == 1.0
    assert view.p_afford(0, 0.2) == 0.0


def test_gaussian_belief_view():
    n = Node(0, 0, 0, initial_energy=0.5)
    nodes = {0: n}
    view = GaussianBeliefView(nodes, initial_mean=0.5, initial_var=0.01)

    # When cost == mean, P(E >= cost) should be 0.5
    p_half = view.p_afford(0, 0.5)
    assert math.isclose(p_half, 0.5, abs_tol=1e-3)

    # When cost is far below mean, probability near 1.0
    assert view.p_afford(0, 0.1) > 0.99
    # When cost is far above mean, probability near 0.0
    assert view.p_afford(0, 0.9) < 0.01

    # Predict step with harvest
    view.predict_step(
        node_id=0,
        harvest_mean=0.1,
        harvest_var=0.001,
        load_mean=0.05,
        load_var=0.0,
        leakage_rate=0.0,
        efficiency=1.0,
        max_capacity=1.0
    )
    # New mean should be 0.5 + 0.1 - 0.05 = 0.55
    assert math.isclose(view.mean(0), 0.55, abs_tol=1e-3)

    # Report update pulls mean towards reported value and reduces variance
    prior_var = view.variance(0)
    view.on_report(0, value=0.40, round_num=2)
    assert view.mean(0) < 0.55
    assert view.variance(0) < prior_var
