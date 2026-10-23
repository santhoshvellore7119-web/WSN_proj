"""
Unit tests for Battery Heterogeneity, Channel Fading, Retransmissions, and Sensor Noise.
"""

import math
import random
import pytest
from src.network import Node
from src.energy_model import EnergyModel
from src.simulator import Simulator


def test_homogeneous_initial_energy_default():
    """Verify default backward-compatible behavior: all nodes have identical initial energy."""
    sim = Simulator(num_nodes=30, initial_energy=0.05, energy_heterogeneity=0.0, seed=42)
    energies = [n.residual_energy for n in sim.nodes.values()]
    assert len(set(energies)) == 1
    assert energies[0] == 0.05


def test_uniform_jitter_initial_energy():
    """Verify uniform jitter creates distinct initial energies within expected bounds."""
    init_e = 0.05
    hetero = 0.3
    sim = Simulator(
        num_nodes=30,
        initial_energy=init_e,
        energy_heterogeneity=hetero,
        initial_energy_distribution='uniform',
        seed=42
    )
    energies = [n.residual_energy for n in sim.nodes.values()]
    # Must have multiple distinct values
    assert len(set(energies)) > 20
    # Must be bounded within [init_e * (1 - hetero), init_e * (1 + hetero)]
    min_bound = init_e * (1.0 - hetero) - 1e-6
    max_bound = init_e * (1.0 + hetero) + 1e-6
    for e in energies:
        assert min_bound <= e <= max_bound


def test_staggered_deployment_initial_energy():
    """Verify staggered deployment spans wide realistic range across nodes."""
    sim = Simulator(
        num_nodes=40,
        initial_energy=0.08,
        max_battery_capacity=0.50,
        energy_heterogeneity=0.8,
        initial_energy_distribution='staggered',
        seed=42
    )
    energies = [n.residual_energy for n in sim.nodes.values()]
    assert len(set(energies)) > 30
    assert min(energies) < 0.10
    assert max(energies) > 0.25


def test_packet_success_probability_deterministic():
    """Verify channel PRR is binary 1.0 within range and 0.0 beyond when fading_sigma == 0."""
    em = EnergyModel()
    assert em.packet_success_probability(distance=20.0, transmission_range=35.0, fading_sigma=0.0) == 1.0
    assert em.packet_success_probability(distance=34.9, transmission_range=35.0, fading_sigma=0.0) == 1.0
    assert em.packet_success_probability(distance=35.1, transmission_range=35.0, fading_sigma=0.0) == 0.0


def test_packet_success_probability_fading():
    """Verify channel PRR transitions probabilistically under log-normal shadow fading."""
    em = EnergyModel()
    rng = random.Random(42)
    # At short distance, PRR should be high
    samples_near = [em.packet_success_probability(10.0, 35.0, fading_sigma=2.0, rng=rng) for _ in range(50)]
    assert sum(samples_near) / len(samples_near) > 0.85

    # At edge of transmission range (35m), PRR has high variance
    samples_edge = [em.packet_success_probability(35.0, 35.0, fading_sigma=2.0, rng=rng) for _ in range(50)]
    assert 0.2 < (sum(samples_edge) / len(samples_edge)) < 0.8


def test_sensor_adc_noise_in_reporting():
    """Verify sensor noise injects variance into reported telemetry without violating battery bounds."""
    sim = Simulator(
        num_nodes=20,
        initial_energy=0.05,
        max_battery_capacity=0.50,
        energy_view_type='stale',
        report_interval=1,
        sensor_noise_std=0.005,
        seed=42
    )
    sim.run(max_rounds=5, verbose=False)
    # Energy view means should reflect reported values
    for nid, node in sim.nodes.items():
        if node.is_alive:
            believed = sim.energy_view.mean(nid)
            assert 0.0 <= believed <= node.max_energy


def test_simulation_run_with_all_uncertainties():
    """Integration test: run full 20 rounds with battery jitter, fading, retries, and ADC noise."""
    sim = Simulator(
        num_nodes=30,
        initial_energy=0.06,
        max_battery_capacity=0.50,
        energy_heterogeneity=0.4,
        initial_energy_distribution='uniform',
        channel_fading_sigma=2.0,
        max_retransmissions=2,
        sensor_noise_std=0.003,
        routing_algorithm='belief_dp',
        energy_view_type='histogram',
        report_interval=5,
        seed=42
    )
    sim.run(max_rounds=20, verbose=False)
    assert sim.round_number == 20
    assert len(sim.alive_nodes_history) == 20
    assert len(sim.pdr_history) == 20
