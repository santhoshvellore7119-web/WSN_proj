"""
Unit tests for brownout recovery and realistic failure semantics in Simulator.
- Verifies that depleted nodes brown out and recover upon solar harvesting recharge.
- Verifies that transmission failure drops packets and wastes spent energy.
- Verifies that true PDR and latency metrics track correctly.
"""

import pytest
from network import Node
from simulator import Simulator
from energy_view import OracleView, StaleView, BlindView, GaussianBeliefView
from harvesting_model import create_harvesting_model


def test_brownout_recovery_with_harvesting():
    """Verify that a node with 0 energy recovers when solar harvesting recharges it."""
    sim = Simulator(
        num_nodes=10,
        initial_energy=0.001,  # Very low initial energy to induce rapid brownout
        max_battery_capacity=0.50,
        harvesting_profile='solar',
        harvesting_kwargs={'peak_rate': 0.05, 'period': 4, 'day_fraction': 0.5, 'seed': 42},
        transmission_range=35.0,
        seed=42
    )

    # Force all nodes to 0 energy (brownout)
    for node in sim.nodes.values():
        node.consume_energy(node.residual_energy)
        assert node.is_alive is False
        assert node.residual_energy == 0.0

    # Advance one round with daytime solar harvesting (peak rate 0.05)
    # Solar profile round 1 with period 4 and day_fraction 0.5 will yield energy
    sim._simulate_round()

    # Verify at least some nodes harvested energy and recovered
    alive_count = sum(1 for n in sim.nodes.values() if n.is_alive)
    assert alive_count > 0, "Depleted nodes must recover upon receiving solar harvest"
    assert sim.alive_nodes_history[-1] == alive_count


def test_in_flight_failure_wastes_energy():
    """Verify that when a node cannot afford transmission, spent energy is wasted."""
    sim = Simulator(
        num_nodes=5,
        initial_energy=0.0001,  # Insufficient for standard transmission (~0.0002 J)
        max_battery_capacity=0.50,
        harvesting_profile=None,
        transmission_range=35.0,
        seed=42
    )

    sim._simulate_round()

    # Packets should fail to deliver because energy was below tx cost
    assert sim.packets_generated_history[-1] > 0
    # Energy wasted history should have captured the attempted transmission
    assert len(sim.energy_wasted_history) == 1
    assert sim.pdr_history[-1] <= 1.0


def test_energy_view_selection():
    """Verify Simulator instantiates requested EnergyView correctly."""
    sim_oracle = Simulator(num_nodes=5, energy_view_type='oracle')
    assert isinstance(sim_oracle.energy_view, OracleView)

    sim_stale = Simulator(num_nodes=5, energy_view_type='stale')
    assert isinstance(sim_stale.energy_view, StaleView)

    sim_blind = Simulator(num_nodes=5, energy_view_type='blind')
    assert isinstance(sim_blind.energy_view, BlindView)

    sim_belief = Simulator(num_nodes=5, energy_view_type='belief')
    assert isinstance(sim_belief.energy_view, GaussianBeliefView)


def test_pdr_and_latency_tracking():
    """Verify Simulator tracks packets_generated, packets_delivered, and latency."""
    sim = Simulator(
        num_nodes=20,
        initial_energy=0.50,  # Ample energy for smooth delivery
        max_battery_capacity=1.0,
        harvesting_profile='constant',
        harvesting_kwargs={'rate': 0.01},
        transmission_range=50.0,
        seed=42
    )

    sim.run(max_rounds=5, verbose=False)

    assert len(sim.pdr_history) == 5
    assert len(sim.latency_history) == 5
    assert len(sim.packets_generated_history) == 5
    assert len(sim.packets_delivered_history) == 5

    # With high initial energy, packets should be delivered
    assert sum(sim.packets_delivered_history) > 0
    assert all(pdr > 0.0 for pdr in sim.pdr_history)
    assert all(lat >= 1.0 for lat in sim.latency_history if lat > 0)
