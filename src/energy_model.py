"""
First-order radio energy dissipation model (LEACH standard).
"""

import math
from typing import Optional


class EnergyModel:
    """Computes radio transmitter and receiver energy costs."""

    def __init__(
        self,
        E_elec: float = 50e-9,      # 50 nJ/bit for tx/rx electronics
        E_amp: float = 100e-12,     # 100 pJ/bit/m^2 amplifier
        E_fs: float = 10e-12,       # 10 pJ/bit/m^2 free-space amplifier
        E_mp: float = 0.0013e-12,   # 0.0013 pJ/bit/m^4 multipath amplifier
        d0: Optional[float] = None
    ):
        self.E_elec = E_elec
        self.E_amp = E_amp
        self.E_fs = E_fs
        self.E_mp = E_mp
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

    def compute_energy_cost(self, k: int, distance: float, is_transmit: bool = True) -> float:
        if is_transmit:
            return self.transmit_energy(k, distance)
        return self.receive_energy(k)