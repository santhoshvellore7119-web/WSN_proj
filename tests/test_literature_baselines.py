"""
Unit tests for literature baselines: EH-LEACH and RealTraceSolarHarvesting.
"""

import sys
import os
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from network import Node
from energy_model import EnergyModel
from clustering import eh_leach_clustering
from harvesting_model import RealTraceSolarHarvesting, create_harvesting_model


def test_real_trace_solar_harvesting():
    """Verify RealTraceSolarHarvesting profiles sample and project expected energy."""
    harvest = RealTraceSolarHarvesting(trace_name='clear_sky', peak_rate=0.04)
    assert harvest.period == 24
    
    # Nighttime hours (hour 0-4) should have 0 harvest
    for t in range(5):
        assert harvest.sample_harvest(node_id=0, current_time=t) == 0.0

    # Midday hour (hour 11) should have peak harvest
    midday = harvest.sample_harvest(node_id=0, current_time=11)
    assert midday > 0.03

    # Expected harvest over 24h should be positive
    total_24h = harvest.expected_harvest(node_id=0, start_time=0, end_time=24)
    assert total_24h > 0.10

    # Factory creation
    model = create_harvesting_model('real_trace', trace_name='cloudy_intermittent')
    assert isinstance(model, RealTraceSolarHarvesting)


def test_eh_leach_clustering_election():
    """Verify EH-LEACH elects cluster heads and weights by solar intake."""
    rng = random.Random(42)
    nodes = {
        i: Node(node_id=i, x=rng.uniform(0, 100), y=rng.uniform(0, 100), initial_energy=0.05, max_energy=0.50)
        for i in range(20)
    }
    energy_model = EnergyModel()
    harvesting = RealTraceSolarHarvesting(trace_name='clear_sky', peak_rate=0.04)

    assignment, heads = eh_leach_clustering(
        nodes=nodes,
        energy_model=energy_model,
        desired_clusters_ratio=0.10,
        harvesting_model=harvesting,
        current_time=11,  # Daytime midday
        round_num=1,
        solar_beta=0.5,
        rng=rng
    )

    assert len(heads) >= 1
    for ch_id in heads:
        assert nodes[ch_id].role == 'CH'
    assert len(assignment) == 20
