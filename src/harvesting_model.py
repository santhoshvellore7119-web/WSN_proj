"""
Energy Harvesting Model for Wireless Sensor Networks.

Implements configurable recharge profiles:
- Constant-rate harvesting (e.g. baseline ambient background recharge)
- Periodic solar-cycle harvesting (diurnal sinusoidal day/night solar model)
- Stochastic Poisson-arrival harvesting (discrete random energy quanta arrivals)
- Heterogeneous spatial harvesting (different profiles per node or region)
"""

import math
import random
from abc import ABC, abstractmethod
from typing import Dict, Optional, Union, List


class HarvestingProfile(ABC):
    """Abstract base class for energy harvesting models."""

    @abstractmethod
    def sample_harvest(self, node_id: int, current_time: int, duration: float = 1.0) -> float:
        """
        Sample the actual energy harvested by a node during the time interval.

        Args:
            node_id: Unique identifier of the sensor node
            current_time: Current simulation round or timestamp
            duration: Duration of interval (default 1.0 round)

        Returns:
            Energy harvested in Joules (>= 0.0)
        """
        pass

    @abstractmethod
    def expected_harvest(self, node_id: int, start_time: int, end_time: int) -> float:
        """
        Compute expected (mathematical expectation) energy harvested between start_time and end_time.
        Used by the predictive time-augmented DP and harvesting-aware clustering.

        Args:
            node_id: Unique identifier of the sensor node
            start_time: Start round
            end_time: Target future round (end_time >= start_time)

        Returns:
            Expected energy in Joules (>= 0.0)
        """
        pass

    def project_energy(
        self,
        node_id: int,
        current_energy: float,
        current_time: int,
        target_time: int,
        battery_capacity: float = 2.0
    ) -> float:
        """
        Predict residual energy of a node at target_time factoring in expected harvest
        and battery capacity clipping.

        Args:
            node_id: Unique identifier of sensor node
            current_energy: Current residual energy in Joules
            current_time: Current round
            target_time: Future round to evaluate
            battery_capacity: Max battery storage capacity (Joules)

        Returns:
            Projected energy in Joules bounded by [0.0, battery_capacity]
        """
        if target_time <= current_time:
            return max(0.0, min(battery_capacity, current_energy))

        expected_gain = self.expected_harvest(node_id, current_time, target_time)
        projected = min(battery_capacity, current_energy + expected_gain)
        return max(0.0, projected)


class ConstantHarvesting(HarvestingProfile):
    """
    Constant rate energy harvesting model.
    Models continuous ambient harvesting (e.g. constant thermal or steady RF energy).
    """

    def __init__(self, rate: float = 0.01):
        """
        Args:
            rate: Constant energy harvested per round in Joules
        """
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
    """
    Periodic solar-cycle harvesting model.
    Models diurnal solar cycle: sinusoidal irradiance during daytime hours, zero at night.
    """

    def __init__(
        self,
        peak_rate: float = 0.05,
        period: int = 24,
        day_fraction: float = 0.5,
        solar_noise: float = 0.0,
        seed: Optional[int] = None
    ):
        """
        Args:
            peak_rate: Maximum energy harvested at solar noon (Joules/round)
            period: Number of rounds per diurnal cycle (e.g. 24 rounds = 24 hours)
            day_fraction: Fraction of cycle with sunlight (e.g. 0.5 = 12h day, 12h night)
            solar_noise: Standard deviation of fractional cloud variation (0.0 = deterministic)
            seed: Random seed for stochastic cloud variations
        """
        self.peak_rate = max(0.0, peak_rate)
        self.period = max(1, period)
        self.day_fraction = max(0.01, min(0.99, day_fraction))
        self.day_length = self.period * self.day_fraction
        self.solar_noise = max(0.0, solar_noise)
        self._rng = random.Random(seed) if seed is not None else random.Random()

    def _instantaneous_rate(self, t: float) -> float:
        """Calculate solar rate at continuous time t."""
        t_mod = t % self.period
        if t_mod < self.day_length:
            # Daytime: half-sine wave over [0, day_length]
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
        # Integrate round by round
        for t in range(start_time, end_time):
            total += self._instantaneous_rate(t)
        return total

    def __repr__(self):
        return f"SolarPeriodicHarvesting(peak={self.peak_rate:.4f}J, period={self.period}, day_frac={self.day_fraction})"


class StochasticHarvesting(HarvestingProfile):
    """
    Stochastic energy harvesting model.
    Models energy arrival as a Poisson process where discrete energy quanta
    arrive randomly over time (e.g. ambient RF bursts, intermittent vibration/wind, cloud-scattered solar).
    """

    def __init__(
        self,
        lambda_rate: float = 2.0,
        quantum: float = 0.015,
        seed: Optional[int] = None
    ):
        """
        Args:
            lambda_rate: Average number of Poisson energy arrivals per round (lambda)
            quantum: Energy delivered per arrival packet in Joules
            seed: Random seed for reproducibility
        """
        self.lambda_rate = max(0.0, lambda_rate)
        self.quantum = max(0.0, quantum)
        self._rng = random.Random(seed) if seed is not None else random.Random()

    def _sample_poisson(self, lam: float) -> int:
        """Sample from Poisson distribution using Knuth's algorithm or Gaussian approximation."""
        if lam <= 0.0:
            return 0
        if lam > 30:
            # Gaussian approximation for large lambda
            val = int(round(self._rng.gauss(lam, math.sqrt(lam))))
            return max(0, val)
        # Knuth's algorithm
        L = math.exp(-lam)
        k = 0
        p = 1.0
        while p > L:
            k += 1
            p *= self._rng.random()
        return k - 1

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
    """
    Spatial/Heterogeneous harvesting model.
    Maps distinct harvesting profiles to specific nodes or node groups.
    """

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
    """
    Factory function to instantiate harvesting profiles.

    Args:
        model_type: One of 'constant', 'solar', 'stochastic', 'heterogeneous', 'none'
        **kwargs: Arguments passed to specific profile constructor

    Returns:
        HarvestingProfile instance
    """
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
