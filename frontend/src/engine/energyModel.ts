/**
 * First-Order Radio Energy Dissipation Model (LEACH Standard & Extended)
 * 
 * E_tx(k, d) = k * E_elec + k * E_fs * d^2  (for d < d0)
 * E_tx(k, d) = k * E_elec + k * E_mp * d^4  (for d >= d0)
 * E_rx(k)    = k * E_elec
 * E_da(k)    = k * E_da  (data aggregation cost per bit)
 */

export class EnergyModel {
  public E_elec: number; // Electronics energy (50 nJ/bit)
  public E_fs: number;   // Free space amplifier (10 pJ/bit/m^2)
  public E_mp: number;   // Multipath amplifier (0.0013 pJ/bit/m^4)
  public E_da: number;   // Data aggregation energy (5 nJ/bit/signal)
  public d0: number;     // Crossover distance threshold in meters

  constructor(
    E_elec: number = 50e-9,
    E_fs: number = 10e-12,
    E_mp: number = 0.0013e-12,
    E_da: number = 5e-9,
    d0?: number
  ) {
    this.E_elec = E_elec;
    this.E_fs = E_fs;
    this.E_mp = E_mp;
    this.E_da = E_da;
    this.d0 = d0 !== undefined ? d0 : Math.sqrt(E_fs / E_mp); // ~87.7058 meters
  }

  /**
   * Energy in Joules to transmit k bits across distance d in meters.
   */
  public transmitEnergy(k: number, distance: number): number {
    if (distance <= 0) return 0;
    if (distance < this.d0) {
      return k * this.E_elec + k * this.E_fs * (distance * distance);
    } else {
      return k * this.E_elec + k * this.E_mp * (distance * distance * distance * distance);
    }
  }

  /**
   * Energy in Joules to receive k bits.
   */
  public receiveEnergy(k: number): number {
    return k * this.E_elec;
  }

  /**
   * Energy in Joules to aggregate n signals of k bits.
   */
  public aggregationEnergy(k: number, signalsCount: number): number {
    return signalsCount * k * this.E_da;
  }
}
