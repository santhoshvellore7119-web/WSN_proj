"""
Unit tests for harvesting_model.py
"""
import pytest
import math
from harvesting_model import (
    ConstantHarvesting,
    SolarPeriodicHarvesting,
    StochasticHarvesting,
    HeterogeneousHarvesting,
    create_harvesting_model
)


def test_constant_harvesting():
    ch = ConstantHarvesting(rate=0.05)
    assert ch.sample_harvest(node_id=0, current_time=10) == 0.05
    assert ch.sample_harvest(node_id=1, current_time=0, duration=2.5) == pytest.approx(0.125)
    assert ch.expected_harvest(node_id=0, start_time=5, end_time=10) == pytest.approx(0.25)
    assert ch.expected_harvest(node_id=0, start_time=10, end_time=5) == 0.0

    # Test projected energy with battery clipping
    proj = ch.project_energy(node_id=0, current_energy=1.9, current_time=0, target_time=5, battery_capacity=2.0)
    # 1.9 + 5 * 0.05 = 2.15 -> clipped to 2.0
    assert proj == 2.0

    proj2 = ch.project_energy(node_id=0, current_energy=0.5, current_time=0, target_time=4, battery_capacity=2.0)
    # 0.5 + 4 * 0.05 = 0.70
    assert proj2 == pytest.approx(0.70)


def test_solar_periodic_harvesting():
    # Period 24, day_fraction 0.5 -> day hours: [0..11], night hours: [12..23]
    solar = SolarPeriodicHarvesting(peak_rate=0.1, period=24, day_fraction=0.5, solar_noise=0.0)

    # Noon is at t = 6 (theta = pi * 6 / 12 = pi/2 -> sin(pi/2) = 1.0)
    noon_harvest = solar.sample_harvest(node_id=0, current_time=6)
    assert noon_harvest == pytest.approx(0.1)

    # Night is at t = 18 -> 0.0
    night_harvest = solar.sample_harvest(node_id=0, current_time=18)
    assert night_harvest == 0.0

    # Start of day t = 0 -> sin(0) = 0.0
    assert solar.sample_harvest(node_id=0, current_time=0) == pytest.approx(0.0)

    # Expected harvest over full day-night cycle
    exp_cycle = solar.expected_harvest(node_id=0, start_time=0, end_time=24)
    # Integral of 0.1 * sin(pi * t / 12) from 0 to 12
    # Analytical sum over discrete integer rounds 0 to 11:
    discrete_sum = sum(0.1 * math.sin(math.pi * t / 12.0) for t in range(12))
    assert exp_cycle == pytest.approx(discrete_sum)


def test_stochastic_poisson_harvesting():
    # Seeded stochastic profile
    stoch = StochasticHarvesting(lambda_rate=3.0, quantum=0.02, seed=42)

    # Deterministic expectation
    exp = stoch.expected_harvest(node_id=0, start_time=0, end_time=10)
    assert exp == pytest.approx(3.0 * 10 * 0.02)  # 0.60 J

    # Sample multiple rounds and check non-negativity and quantum alignment
    samples = [stoch.sample_harvest(node_id=0, current_time=t) for t in range(100)]
    assert all(s >= 0.0 for s in samples)
    assert all(abs(s % 0.02) < 1e-9 or abs((s % 0.02) - 0.02) < 1e-9 for s in samples)

    # Mean over 1000 samples should be close to lambda * quantum = 0.06
    stoch_large = StochasticHarvesting(lambda_rate=5.0, quantum=0.01, seed=123)
    many_samples = [stoch_large.sample_harvest(node_id=0, current_time=t) for t in range(2000)]
    mean_val = sum(many_samples) / len(many_samples)
    assert mean_val == pytest.approx(5.0 * 0.01, rel=0.15)


def test_heterogeneous_harvesting():
    default_p = ConstantHarvesting(rate=0.01)
    solar_p = SolarPeriodicHarvesting(peak_rate=0.08, period=24)
    stoch_p = StochasticHarvesting(lambda_rate=2.0, quantum=0.02, seed=1)

    het = HeterogeneousHarvesting(default_profile=default_p)
    het.set_node_profile(10, solar_p)
    het.set_node_profile(20, stoch_p)

    # Default node
    assert het.sample_harvest(node_id=0, current_time=6) == 0.01
    # Solar node at noon
    assert het.sample_harvest(node_id=10, current_time=6) == pytest.approx(0.08)
    # Stoch node
    assert het.expected_harvest(node_id=20, start_time=0, end_time=5) == pytest.approx(0.20)


def test_create_harvesting_model_factory():
    c = create_harvesting_model('constant', rate=0.03)
    assert isinstance(c, ConstantHarvesting)
    assert c.rate == 0.03

    s = create_harvesting_model('solar', peak_rate=0.05, period=24)
    assert isinstance(s, SolarPeriodicHarvesting)

    p = create_harvesting_model('stochastic', lambda_rate=4.0)
    assert isinstance(p, StochasticHarvesting)

    z = create_harvesting_model('none')
    assert isinstance(z, ConstantHarvesting)
    assert z.rate == 0.0
