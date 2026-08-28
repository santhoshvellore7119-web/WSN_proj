"""
Quick test for energy_model.py
"""
import sys
sys.path.append('../src')

from energy_model import EnergyModel

def test_init():
    em = EnergyModel()
    assert em.E_elec == 50e-9
    assert em.E_amp == 100e-12
    assert em.E_fs == 10e-12
    assert em.E_mp == 0.0013e-12
    # d0 computed as sqrt(E_fs/E_mp)
    expected_d0 = (10e-12 / 0.0013e-12) ** 0.5
    assert abs(em.d0 - expected_d0) < 1e-9
    print("EnergyModel init: PASS")

def test_transmit_energy():
    em = EnergyModel()
    k = 100  # bits
    distance = 10.0  # meters
    # For distance < d0? Let's compute d0
    d0 = (10e-12 / 0.0013e-12) ** 0.5  # approx sqrt(7692.3) ~ 87.7
    # So 10m < d0, use free space model
    energy = em.transmit_energy(k, distance)
    expected = k * em.E_elec + k * em.E_fs * (distance ** 2)
    assert abs(energy - expected) < 1e-15
    print("Transmit energy (free space): PASS")

    # Test multipath model
    distance = 100.0  # > d0
    energy = em.transmit_energy(k, distance)
    expected = k * em.E_elec + k * em.E_mp * (distance ** 4)
    assert abs(energy - expected) < 1e-15
    print("Transmit energy (multipath): PASS")

def test_receive_energy():
    em = EnergyModel()
    k = 50
    energy = em.receive_energy(k)
    expected = k * em.E_elec
    assert abs(energy - expected) < 1e-15
    print("Receive energy: PASS")

def test_compute_energy_cost():
    em = EnergyModel()
    k = 200
    distance = 5.0
    # transmit
    energy_tx = em.compute_energy_cost(k, distance, is_transmit=True)
    expected_tx = em.transmit_energy(k, distance)
    assert abs(energy_tx - expected_tx) < 1e-15
    # receive
    energy_rx = em.compute_energy_cost(k, distance, is_transmit=False)
    expected_rx = em.receive_energy(k)
    assert abs(energy_rx - expected_rx) < 1e-15
    print("Compute energy cost: PASS")

if __name__ == "__main__":
    test_init()
    test_transmit_energy()
    test_receive_energy()
    test_compute_energy_cost()
    print("All energy model tests passed!")
