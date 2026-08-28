"""
Energy model for WSN simulation.
Implements the first-order radio model.
"""

import math
from typing import Optional


class EnergyModel:
    """
    First-order radio model for wireless sensor networks.
    Based on the LEACH protocol energy model.
    """

    def __init__(self,
                 E_elec: float = 50e-9,      # 50 nJ/bit
                 E_amp: float = 100e-12,     # 100 pJ/bit/m^2
                 E_fs: float = 10e-12,       # 10 pJ/bit/m^2 (free space)
                 E_mp: float = 0.0013e-12,   # 0.0013 pJ/bit/m^4 (multipath)
                 d0: float = math.sqrt(10e-12 / 0.0013e-12)):  # Threshold distance ~ sqrt(E_fs/E_mp)
        """
        Initialize energy model parameters.

        Args:
            E_elec: Electronics energy (J/bit)
            E_amp: Amplifier energy (J/bit/m^2)
            E_fs: Free space amplifier energy (J/bit/m^2)
            E_mp: Multipath amplifier energy (J/bit/m^4)
            d0: Distance threshold between free space and multipath models
        """
        self.E_elec = E_elec
        self.E_amp = E_amp
        self.E_fs = E_fs
        self.E_mp = E_mp
        self.d0 = d0

    def transmit_energy(self, k: int, distance: float) -> float:
        """
        Calculate energy consumed to transmit k bits over distance.

        Args:
            k: Number of bits to transmit
            distance: Transmission distance in meters

        Returns:
            Energy consumed in Joules
        """
        if distance < self.d0:
            # Free space model
            return k * self.E_elec + k * self.E_fs * (distance ** 2)
        else:
            # Multipath model
            return k * self.E_elec + k * self.E_mp * (distance ** 4)

    def receive_energy(self, k: int) -> float:
        """
        Calculate energy consumed to receive k bits.

        Args:
            k: Number of bits received

        Returns:
            Energy consumed in Joules
        """
        return k * self.E_elec

    def compute_energy_cost(self, k: int, distance: float, is_transmit: bool = True) -> float:
        """
        Compute energy cost for transmission or reception.

        Args:
            k: Number of bits
            distance: Distance in meters (for transmission)
            is_transmit: True for transmission, False for reception

        Returns:
            Energy consumed in Joules
        """
        if is_transmit:
            return self.transmit_energy(k, distance)
        else:
            return self.receive_energy(k)