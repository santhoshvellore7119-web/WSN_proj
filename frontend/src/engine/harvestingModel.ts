/**
 * Energy Harvesting Models for Wireless Sensor Networks
 * 
 * Supports:
 * - Constant background ambient recharge
 * - Solar day/night periodic cycle with cloud stochasticity
 * - Heterogeneous spatial shadowing (canopy / building occlusion)
 * - Stochastic Poisson energy arrivals
 * - Real-trace solar irradiance replay (NREL GHI profile)
 */

export interface HarvestingProfile {
  sampleHarvest(nodeId: number, currentTime: number, duration?: number): number;
  expectedHarvest(nodeId: number, startTime: number, endTime: number): number;
  projectEnergy(
    nodeId: number,
    currentEnergy: number,
    currentTime: number,
    targetTime: number,
    batteryCapacity: number
  ): number;
}

// Seedable PRNG (Mulberry32)
export function createPRNG(seed: number) {
  let s = seed >>> 0;
  return function () {
    s = (s + 0x6D2B79F5) >>> 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export class ConstantHarvesting implements HarvestingProfile {
  private rate: number;

  constructor(rate: number = 0.005) {
    this.rate = rate;
  }

  sampleHarvest(_nodeId: number, _currentTime: number, duration: number = 1.0): number {
    return this.rate * duration;
  }

  expectedHarvest(_nodeId: number, startTime: number, endTime: number): number {
    const dur = Math.max(0, endTime - startTime);
    return this.rate * dur;
  }

  projectEnergy(
    nodeId: number,
    currentEnergy: number,
    currentTime: number,
    targetTime: number,
    batteryCapacity: number
  ): number {
    if (targetTime <= currentTime) return Math.min(batteryCapacity, Math.max(0, currentEnergy));
    const harvest = this.expectedHarvest(nodeId, currentTime, targetTime);
    return Math.min(batteryCapacity, currentEnergy + harvest);
  }
}

export class SolarHarvesting implements HarvestingProfile {
  public peakRate: number;
  public period: number;
  public dayFraction: number;
  public cloudVariability: number;
  private rng: () => number;
  private nodeMultipliers: Record<number, number> = {};

  constructor(
    peakRate: number = 0.03,
    period: number = 24,
    dayFraction: number = 0.5,
    seed: number = 42,
    cloudVariability: number = 0.15,
    nodeMultipliers?: Record<number, number>
  ) {
    this.peakRate = peakRate;
    this.period = period;
    this.dayFraction = dayFraction;
    this.cloudVariability = cloudVariability;
    this.rng = createPRNG(seed + 101);
    if (nodeMultipliers) {
      this.nodeMultipliers = { ...nodeMultipliers };
    }
  }

  public setNodeMultiplier(nodeId: number, multiplier: number) {
    this.nodeMultipliers[nodeId] = multiplier;
  }

  public getNodeMultiplier(nodeId: number): number {
    return this.nodeMultipliers[nodeId] !== undefined ? this.nodeMultipliers[nodeId] : 1.0;
  }

  private getIdealSolarRate(time: number): number {
    const tInDay = ((time % this.period) + this.period) % this.period;
    const dayLength = this.period * this.dayFraction;
    if (tInDay <= dayLength && dayLength > 0) {
      // Half-sine during sunlight hours
      const phase = (Math.PI * tInDay) / dayLength;
      return this.peakRate * Math.sin(phase);
    }
    return 0.0;
  }

  sampleHarvest(nodeId: number, currentTime: number, duration: number = 1.0): number {
    const ideal = this.getIdealSolarRate(currentTime);
    if (ideal <= 0) return 0.0;

    // Add mild stochastic cloud factor: (1 - cloudVariability + 2 * cloudVariability * random)
    const cloudNoise = (this.rng() - 0.5) * 2.0 * this.cloudVariability;
    const factor = Math.max(0.2, 1.0 + cloudNoise);
    const mult = this.getNodeMultiplier(nodeId);
    return ideal * factor * mult * duration;
  }

  expectedHarvest(nodeId: number, startTime: number, endTime: number): number {
    if (endTime <= startTime) return 0.0;
    const mult = this.getNodeMultiplier(nodeId);
    let total = 0.0;
    // Numerical integration across rounds
    for (let t = startTime; t < endTime; t++) {
      total += this.getIdealSolarRate(t) * mult;
    }
    return total;
  }

  projectEnergy(
    nodeId: number,
    currentEnergy: number,
    currentTime: number,
    targetTime: number,
    batteryCapacity: number
  ): number {
    if (targetTime <= currentTime) return Math.min(batteryCapacity, Math.max(0, currentEnergy));
    const harvest = this.expectedHarvest(nodeId, currentTime, targetTime);
    return Math.min(batteryCapacity, currentEnergy + harvest);
  }
}

export class StochasticPoissonHarvesting implements HarvestingProfile {
  public lambdaRate: number; // Avg arrivals per round
  public quantum: number; // Energy per arrival in Joules
  private rng: () => number;

  constructor(lambdaRate: number = 2.0, quantum: number = 0.005, seed: number = 42) {
    this.lambdaRate = lambdaRate;
    this.quantum = quantum;
    this.rng = createPRNG(seed + 202);
  }

  // Sample Poisson distribution via Knuth's algorithm
  private samplePoisson(lambda: number): number {
    const L = Math.exp(-lambda);
    let k = 0;
    let p = 1.0;
    do {
      k++;
      p *= this.rng();
    } while (p > L);
    return k - 1;
  }

  sampleHarvest(_nodeId: number, _currentTime: number, duration: number = 1.0): number {
    const arrivals = this.samplePoisson(this.lambdaRate * duration);
    return arrivals * this.quantum;
  }

  expectedHarvest(_nodeId: number, startTime: number, endTime: number): number {
    const dur = Math.max(0, endTime - startTime);
    return dur * this.lambdaRate * this.quantum;
  }

  projectEnergy(
    nodeId: number,
    currentEnergy: number,
    currentTime: number,
    targetTime: number,
    batteryCapacity: number
  ): number {
    if (targetTime <= currentTime) return Math.min(batteryCapacity, Math.max(0, currentEnergy));
    const harvest = this.expectedHarvest(nodeId, currentTime, targetTime);
    return Math.min(batteryCapacity, currentEnergy + harvest);
  }
}

// Normalized Real Solar Trace (Hourly GHI derived from NREL typical meteorological day)
const REAL_TRACE_HOURLY: number[] = [
  0.0, 0.0, 0.0, 0.0, 0.0, 0.02, 0.15, 0.38, 0.65, 0.85, 0.98, 1.0, 0.96, 0.82, 0.61, 0.35, 0.12, 0.01, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
];

export class RealTraceSolarHarvesting implements HarvestingProfile {
  public peakRate: number;
  public trace: number[];
  private rng: () => number;

  constructor(peakRate: number = 0.03, seed: number = 42) {
    this.peakRate = peakRate;
    this.trace = REAL_TRACE_HOURLY;
    this.rng = createPRNG(seed + 303);
  }

  sampleHarvest(_nodeId: number, currentTime: number, duration: number = 1.0): number {
    const hour = ((currentTime % 24) + 24) % 24;
    const traceVal = this.trace[hour] || 0.0;
    // Slight cloud shadow fluctuation
    const noise = (this.rng() - 0.5) * 0.1;
    const factor = Math.max(0, traceVal + noise);
    return factor * this.peakRate * duration;
  }

  expectedHarvest(_nodeId: number, startTime: number, endTime: number): number {
    if (endTime <= startTime) return 0.0;
    let total = 0.0;
    for (let t = startTime; t < endTime; t++) {
      const hour = ((t % 24) + 24) % 24;
      total += (this.trace[hour] || 0.0) * this.peakRate;
    }
    return total;
  }

  projectEnergy(
    nodeId: number,
    currentEnergy: number,
    currentTime: number,
    targetTime: number,
    batteryCapacity: number
  ): number {
    if (targetTime <= currentTime) return Math.min(batteryCapacity, Math.max(0, currentEnergy));
    const harvest = this.expectedHarvest(nodeId, currentTime, targetTime);
    return Math.min(batteryCapacity, currentEnergy + harvest);
  }
}
