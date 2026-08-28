"""
Energy harvesting models for WSN simulation.

Supports:
- Constant background recharge
- Solar day/night periodic recharge
- Stochastic Poisson packet arrivals
- Heterogeneous profiles for individual nodes
"""

import math
import random
from abc import ABC, abstractmethod
from typing import Dict, Optional, Union, List


class HarvestingProfile(ABC):
    """Base class for energy harvesting sources."""

    @abstractmethod
    def sample_harvest(self, node_id: int, current_time: int, duration: float = 1.0) -> float:
        """Sample energy harvested (in Joules) by node during the time step."""
        pass

    @abstractmethod
    def expected_harvest(self, node_id: int, start_time: int, end_time: int) -> float:
        """Expected energy harvested between start_time and end_time."""
        pass

    def project_energy(
        self,
        node_id: int,
        current_energy: float,
        current_time: int,
        target_time: int,
        battery_capacity: float = 2.0
    ) -> float:
        """Estimate future battery level after harvesting up to battery capacity."""
        if target_time <= current_time:
            return max(0.0, min(battery_capacity, current_energy))

        expected_gain = self.expected_harvest(node_id, current_time, target_time)
        projected = min(battery_capacity, current_energy + expected_gain)
        return max(0.0, projected)


class ConstantHarvesting(HarvestingProfile):
    """Constant rate energy harvesting (e.g. steady RF or thermal gradient)."""

    def __init__(self, rate: float = 0.01):
        self.rate = max(0.0, rate)

    def sample_harvest(self, node_id: int, current_time: int, duration: float = 1.0) -> float:
        return self.rate * duration

    def expected_harvest(self, node_id: int, start_time: int, end_time: int) -> float:
        if end_time <= start_time:
            return 0.0
        return self.rate * (end_time - start_time)

    def __repr__(self):
        return f"ConstantHarvesting(rate={self.rate:.4f}J/round)"


class SolarPeriodicHarvesting(HarvestingProfile):
    """Day/night solar harvesting using a sinusoidal curve during daylight hours."""

    def __init__(
        self,
        peak_rate: float = 0.05,
        period: int = 24,
        day_fraction: float = 0.5,
        solar_noise: float = 0.0,
        seed: Optional[int] = None
    ):
        self.peak_rate = max(0.0, peak_rate)
        self.period = max(1, period)
        self.day_fraction = max(0.01, min(0.99, day_fraction))
        self.day_length = self.period * self.day_fraction
        self.solar_noise = max(0.0, solar_noise)
        self._rng = random.Random(seed) if seed is not None else random.Random()

    def _instantaneous_rate(self, t: float) -> float:
        t_mod = t % self.period
        if t_mod < self.day_length:
            # Daytime: half-sine wave
            theta = math.pi * (t_mod / self.day_length)
            return self.peak_rate * math.sin(theta)
        return 0.0

    def sample_harvest(self, node_id: int, current_time: int, duration: float = 1.0) -> float:
        base_rate = self._instantaneous_rate(current_time)
        if self.solar_noise > 0.0 and base_rate > 0.0:
            noise_factor = max(0.0, self._rng.gauss(1.0, self.solar_noise))
            actual = base_rate * noise_factor * duration
        else:
            actual = base_rate * duration
        return max(0.0, actual)

    def expected_harvest(self, node_id: int, start_time: int, end_time: int) -> float:
        if end_time <= start_time:
            return 0.0
        total = 0.0
        for t in range(start_time, end_time):
            total += self._instantaneous_rate(t)
        return total

    def __repr__(self):
        return f"SolarPeriodicHarvesting(peak={self.peak_rate:.4f}J, period={self.period}, day_frac={self.day_fraction})"


class StochasticHarvesting(HarvestingProfile):
    """Discrete energy arrivals modeled as a Poisson process."""

    def __init__(
        self,
        lambda_rate: float = 2.0,
        quantum: float = 0.015,
        seed: Optional[int] = None
    ):
        self.lambda_rate = max(0.0, lambda_rate)
        self.quantum = max(0.0, quantum)
        self._rng = random.Random(seed) if seed is not None else random.Random()

    def _sample_poisson(self, lam: float) -> int:
        if lam <= 0.0:
            return 0
        if lam > 30:
            val = int(round(self._rng.gauss(lam, math.sqrt(lam))))
            return max(0, val)
        # Knuth's Poisson sampling
        limit = math.exp(-lam)
        count = 0
        prob = 1.0
        while prob > limit:
            count += 1
            prob *= self._rng.random()
        return count - 1

    def sample_harvest(self, node_id: int, current_time: int, duration: float = 1.0) -> float:
        arrivals = self._sample_poisson(self.lambda_rate * duration)
        return arrivals * self.quantum

    def expected_harvest(self, node_id: int, start_time: int, end_time: int) -> float:
        if end_time <= start_time:
            return 0.0
        num_rounds = end_time - start_time
        return self.lambda_rate * num_rounds * self.quantum

    def __repr__(self):
        mean_power = self.lambda_rate * self.quantum
        return f"StochasticHarvesting(lambda={self.lambda_rate}, quantum={self.quantum:.4f}J, mean={mean_power:.4f}J/round)"


class HeterogeneousHarvesting(HarvestingProfile):
    """Allows assigning different harvesting profiles to different nodes."""

    def __init__(
        self,
        default_profile: HarvestingProfile,
        node_profiles: Optional[Dict[int, HarvestingProfile]] = None
    ):
        self.default_profile = default_profile
        self.node_profiles = node_profiles or {}

    def set_node_profile(self, node_id: int, profile: HarvestingProfile):
        self.node_profiles[node_id] = profile

    def get_profile(self, node_id: int) -> HarvestingProfile:
        return self.node_profiles.get(node_id, self.default_profile)

    def sample_harvest(self, node_id: int, current_time: int, duration: float = 1.0) -> float:
        return self.get_profile(node_id).sample_harvest(node_id, current_time, duration)

    def expected_harvest(self, node_id: int, start_time: int, end_time: int) -> float:
        return self.get_profile(node_id).expected_harvest(node_id, start_time, end_time)

    def __repr__(self):
        return f"HeterogeneousHarvesting(default={self.default_profile}, custom_nodes={len(self.node_profiles)})"


def create_harvesting_model(
    model_type: str = 'solar',
    **kwargs
) -> HarvestingProfile:
    """Helper to instantiate harvesting profile by name."""
    model_type = model_type.lower()
    if model_type in ('none', 'zero', 'off'):
        return ConstantHarvesting(rate=0.0)
    elif model_type in ('constant', 'const'):
        rate = kwargs.get('rate', 0.01)
        return ConstantHarvesting(rate=rate)
    elif model_type in ('solar', 'periodic'):
        peak = kwargs.get('peak_rate', 0.04)
        period = kwargs.get('period', 24)
        day_frac = kwargs.get('day_fraction', 0.5)
        noise = kwargs.get('solar_noise', 0.0)
        seed = kwargs.get('seed', None)
        return SolarPeriodicHarvesting(peak_rate=peak, period=period, day_fraction=day_frac, solar_noise=noise, seed=seed)
    elif model_type in ('stochastic', 'poisson', 'random'):
        lam = kwargs.get('lambda_rate', 2.0)
        quantum = kwargs.get('quantum', 0.015)
        seed = kwargs.get('seed', None)
        return StochasticHarvesting(lambda_rate=lam, quantum=quantum, seed=seed)
    else:
        raise ValueError(f"Unknown harvesting model type: {model_type}")
