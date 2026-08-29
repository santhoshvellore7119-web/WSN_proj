"""
Unit tests for heterogeneous harvesting profiles and spatial corridor routing.
"""

import pytest
from network import Node, Graph
from energy_model import EnergyModel
from harvesting_model import (
    create_shadowed_solar_profile,
    create_rf_hotspot_profile,
    HeterogeneousHarvesting,
    ConstantHarvesting,
    SolarPeriodicHarvesting
)
from dp_lifetime import dp_time_augmented_lifetime
from routing import dijkstra


def test_shadowed_solar_profile_creation():
    nodes = {
        0: Node(node_id=0, x=10.0, y=50.0),
        1: Node(node_id=1, x=20.0, y=50.0),
        2: Node(node_id=2, x=80.0, y=50.0),
        3: Node(node_id=3, x=90.0, y=50.0),
    }

    profile = create_shadowed_solar_profile(
        nodes=nodes,
        peak_rate=0.010,
        shadow_fraction=0.5,
        shadow_penalty=0.1
    )

    # Nodes 0 and 1 are in the shadowed region (x < 50)
    # Nodes 2 and 3 are in the sunny region (x >= 50)
    p0 = profile.get_profile(0)
    p3 = profile.get_profile(3)

    assert isinstance(p0, SolarPeriodicHarvesting)
    assert isinstance(p3, SolarPeriodicHarvesting)
    assert p0.peak_rate == pytest.approx(0.001, rel=1e-3)
    assert p3.peak_rate == pytest.approx(0.010, rel=1e-3)


def test_rf_hotspot_profile_creation():
    nodes = {
        0: Node(node_id=0, x=10.0, y=10.0),
        1: Node(node_id=1, x=70.0, y=70.0),
    }

    profile = create_rf_hotspot_profile(
        nodes=nodes,
        hotspot_center=(75.0, 75.0),
        hotspot_radius=20.0,
        hotspot_rate=0.05,
        background_rate=0.001
    )

    # Node 0 is far from hotspot; Node 1 is inside
    assert profile.get_profile(0).rate == pytest.approx(0.001, rel=1e-3)
    assert profile.get_profile(1).rate == pytest.approx(0.050, rel=1e-3)
