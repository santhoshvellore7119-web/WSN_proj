"""
First-order radio energy dissipation model (LEACH standard) with channel fading.
"""

import math
from typing import Optional, Any


class EnergyModel:
    """Computes radio transmitter and receiver energy costs."""

    def __init__(
        self,
        E_elec: float = 50e-9,      # 50 nJ/bit for tx/rx electronics
        E_amp: float = 100e-12,     # 100 pJ/bit/m^2 amplifier
        E_fs: float = 10e-12,       # 10 pJ/bit/m^2 free-space amplifier
        E_mp: float = 0.0013e-12,   # 0.0013 pJ/bit/m^4 multipath amplifier
        d0: Optional[float] = None,
        E_idle: float = 0.0,        # Idle listening drain per round
        E_sense: float = 0.0        # Sensing energy per measurement
    ):
        self.E_elec = E_elec
        self.E_amp = E_amp
        self.E_fs = E_fs
        self.E_mp = E_mp
        self.E_idle = E_idle
        self.E_sense = E_sense
        # Crossover threshold distance between free space (d^2) and multipath (d^4)
        self.d0 = d0 if d0 is not None else math.sqrt(E_fs / E_mp)

    def transmit_energy(self, k: int, distance: float) -> float:
        """Energy in Joules to transmit k bits over a distance in meters."""
        if distance < self.d0:
            # Free space model: d^2 path loss
            return k * self.E_elec + k * self.E_fs * (distance ** 2)
        else:
            # Multipath model: d^4 path loss
            return k * self.E_elec + k * self.E_mp * (distance ** 4)

    def receive_energy(self, k: int) -> float:
        """Energy in Joules to receive k bits."""
        return k * self.E_elec

    def idle_energy(self, duration: float = 1.0) -> float:
        """Energy in Joules consumed while idling/listening."""
        return self.E_idle * duration

    def sensing_energy(self) -> float:
        """Energy in Joules consumed acquiring a physical sensor sample."""
        return self.E_sense

    def compute_energy_cost(self, k: int, distance: float, is_transmit: bool = True) -> float:
        if is_transmit:
            return self.transmit_energy(k, distance)
        return self.receive_energy(k)

    def packet_success_probability(
        self,
        distance: float,
        transmission_range: Optional[float] = None,
        fading_sigma: float = 0.0,
        rng: Optional[Any] = None
    ) -> float:
        """
        Computes packet reception rate (PRR) under optional log-normal shadow fading.
        If fading_sigma == 0.0, PRR is 1.0 within transmission_range and 0.0 beyond.
        If fading_sigma > 0.0, models realistic transition zone with log-normal attenuation.
        """
        if transmission_range is not None and distance > transmission_range * 1.5:
            return 0.0
        if fading_sigma <= 0.0:
            if transmission_range is None or distance <= transmission_range:
                return 1.0
            return 0.0

        import random
        _rng = rng if rng is not None else random
        noise_db = _rng.gauss(0.0, fading_sigma)

        r_eff = transmission_range if transmission_range is not None else 35.0
        snr_proxy = (r_eff - distance) / (0.15 * r_eff) + (noise_db / 3.0)
        prr = 1.0 / (1.0 + math.exp(-max(-15.0, min(15.0, snr_proxy))))
        return max(0.0, min(1.0, prr))
