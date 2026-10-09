"""
Energy View and Belief Interfaces for WSN Energy Routing.

Decouples true hidden battery physics from the router's observable belief state.
Implements:
- EnergyView: Protocol defining the query and update interface for routing algorithms.
- OracleView: Omniscient view with perfect knowledge of true residual energy (upper bound).
- BlindView: Oblivious view that ignores residual energy (Dijkstra baseline).
- StaleView: Realistic baseline tracking last-reported energy without predictive updates.
- GaussianBeliefView: Calibrated probabilistic belief with Kalman/truncated Gaussian filtering.
"""

from typing import Dict, Optional, Protocol, runtime_checkable
import math
from network import Node


@runtime_checkable
class EnergyView(Protocol):
    """Protocol for querying and updating energy information."""

    def p_afford(self, node_id: int, cost: float, slot: int = 0) -> float:
        """Probability that node has at least `cost` energy at the given time/slot."""
        ...

    def mean(self, node_id: int, slot: int = 0) -> float:
        """Expected energy of node at the given time/slot in Joules."""
        ...

    def variance(self, node_id: int, slot: int = 0) -> float:
        """Variance of energy belief at the given time/slot in Joules^2."""
        ...

    def is_available(self, node_id: int, threshold_cost: float = 1e-6) -> bool:
        """Returns True if node is deemed operable/available for routing."""
        ...

    def on_report(self, node_id: int, value: float, round_num: int) -> None:
        """Updates belief when an explicit energy report is successfully delivered."""
        ...

    def on_failure(self, node_id: int, cost: float, slot: int = 0) -> None:
        """Updates belief upon packet drop/failure (censored: E < cost)."""
        ...


class OracleView:
    """
    Oracle (omniscient) view with instantaneous, zero-latency access to true battery state.
    Used as the theoretical upper bound and for backward compatibility with classical baselines.
    """

    def __init__(self, nodes: Dict[int, Node]):
        self.nodes = nodes

    def p_afford(self, node_id: int, cost: float, slot: int = 0) -> float:
        node = self.nodes.get(node_id)
        if node is None or not node.is_alive:
            return 0.0
        return 1.0 if node.residual_energy >= cost else 0.0

    def mean(self, node_id: int, slot: int = 0) -> float:
        node = self.nodes.get(node_id)
        if node is None:
            return 0.0
        return node.residual_energy

    def variance(self, node_id: int, slot: int = 0) -> float:
        return 0.0

    def is_available(self, node_id: int, threshold_cost: float = 1e-6) -> bool:
        node = self.nodes.get(node_id)
        if node is None:
            return False
        return node.is_alive and node.residual_energy >= threshold_cost

    def on_report(self, node_id: int, value: float, round_num: int) -> None:
        pass

    def on_failure(self, node_id: int, cost: float, slot: int = 0) -> None:
        pass


class BlindView:
    """
    Blind view that completely ignores node energy levels.
    Treats all structurally alive nodes as fully capable of transmission (shortest-path baseline).
    """

    def __init__(self, nodes: Dict[int, Node], default_energy: float = 1.0):
        self.nodes = nodes
        self.default_energy = default_energy

    def p_afford(self, node_id: int, cost: float, slot: int = 0) -> float:
        node = self.nodes.get(node_id)
        if node is None:
            return 0.0
        return 1.0 if node.is_alive else 0.0

    def mean(self, node_id: int, slot: int = 0) -> float:
        return self.default_energy

    def variance(self, node_id: int, slot: int = 0) -> float:
        return 0.0

    def is_available(self, node_id: int, threshold_cost: float = 1e-6) -> bool:
        node = self.nodes.get(node_id)
        if node is None:
            return False
        return node.is_alive

    def on_report(self, node_id: int, value: float, round_num: int) -> None:
        pass

    def on_failure(self, node_id: int, cost: float, slot: int = 0) -> None:
        pass


class StaleView:
    """
    Stale report view.
    Maintains the most recently received energy telemetry value for each node.
    Does not predict harvesting or load between telemetry reports.
    Incorporates censored updates on transmission failure.
    """

    def __init__(self, nodes: Dict[int, Node], initial_energy: float = 0.05):
        self.nodes = nodes
        self.last_reported: Dict[int, float] = {
            nid: getattr(node, 'initial_energy', initial_energy) for nid, node in nodes.items()
        }
        self.last_report_round: Dict[int, int] = {nid: 0 for nid in nodes}

    def p_afford(self, node_id: int, cost: float, slot: int = 0) -> float:
        val = self.last_reported.get(node_id, 0.0)
        return 1.0 if val >= cost else 0.0

    def mean(self, node_id: int, slot: int = 0) -> float:
        return self.last_reported.get(node_id, 0.0)

    def variance(self, node_id: int, slot: int = 0) -> float:
        return 0.0

    def is_available(self, node_id: int, threshold_cost: float = 1e-6) -> bool:
        return self.last_reported.get(node_id, 0.0) >= threshold_cost

    def on_report(self, node_id: int, value: float, round_num: int) -> None:
        self.last_reported[node_id] = max(0.0, value)
        self.last_report_round[node_id] = round_num

    def on_failure(self, node_id: int, cost: float, slot: int = 0) -> None:
        # Censored update: transmission failed, so node had strictly less than cost
        curr = self.last_reported.get(node_id, 0.0)
        self.last_reported[node_id] = min(curr, max(0.0, cost - 1e-6))


class GaussianBeliefView:
    """
    Gaussian belief view (Tier 1 MVP proposed method).
    Maintains mean mu_i and variance sigma_i^2 for each node.
    Evaluates P(E >= cost) via the Gaussian complementary cumulative distribution function.
    """

    def __init__(
        self,
        nodes: Dict[int, Node],
        initial_mean: float = 0.05,
        initial_var: float = 1e-6,
        quantization_bits: int = 8,
        measurement_var: float = 1e-6
    ):
        self.nodes = nodes
        self.mu: Dict[int, float] = {
            nid: getattr(node, 'residual_energy', initial_mean) for nid, node in nodes.items()
        }
        self.var: Dict[int, float] = {nid: initial_var for nid in nodes}
        self.quantization_bits = quantization_bits
        self.measurement_var = measurement_var

    def p_afford(self, node_id: int, cost: float, slot: int = 0) -> float:
        mu = self.mu.get(node_id, 0.0)
        var = self.var.get(node_id, 1e-6)
        sigma = math.sqrt(max(1e-9, var))
        if sigma < 1e-6:
            return 1.0 if mu >= cost else 0.0

        # Normal complementary CDF: Q((cost - mu) / sigma) = 0.5 * erfc((cost - mu) / (sigma * sqrt(2)))
        z = (cost - mu) / (sigma * math.sqrt(2.0))
        # Clamp z to avoid numerical errors
        if z > 5.0:
            return 0.0
        if z < -5.0:
            return 1.0
        return 0.5 * math.erfc(z)

    def mean(self, node_id: int, slot: int = 0) -> float:
        return self.mu.get(node_id, 0.0)

    def variance(self, node_id: int, slot: int = 0) -> float:
        return self.var.get(node_id, 0.0)

    def is_available(self, node_id: int, threshold_cost: float = 1e-6) -> bool:
        return self.p_afford(node_id, threshold_cost) > 0.05

    def predict_step(
        self,
        node_id: int,
        harvest_mean: float,
        harvest_var: float,
        load_mean: float,
        load_var: float = 0.0,
        leakage_rate: float = 0.0,
        efficiency: float = 1.0,
        max_capacity: Optional[float] = None
    ) -> None:
        """
        Advances belief state by one step under linear Gaussian approximation:
        mu_{t+1} = (1 - lambda) * mu_t + eta * H_mean - L_mean
        var_{t+1} = (1 - lambda)^2 * var_t + eta^2 * H_var + L_var
        """
        old_mu = self.mu.get(node_id, 0.0)
        old_var = self.var.get(node_id, 1e-6)

        c = 1.0 - leakage_rate
        new_mu = c * old_mu + efficiency * harvest_mean - load_mean
        new_var = (c ** 2) * old_var + (efficiency ** 2) * harvest_var + load_var

        cap = max_capacity
        if cap is None and node_id in self.nodes:
            cap = getattr(self.nodes[node_id], 'max_energy', None)

        if cap is not None:
            new_mu = min(cap, new_mu)

        self.mu[node_id] = max(0.0, new_mu)
        self.var[node_id] = max(1e-9, new_var)

    def on_report(self, node_id: int, value: float, round_num: int) -> None:
        """
        Bayesian Kalman measurement update on receiving quantized report:
        y = value + noise
        """
        prior_mu = self.mu.get(node_id, value)
        prior_var = self.var.get(node_id, 1e-4)
        meas_var = self.measurement_var

        kalman_gain = prior_var / (prior_var + meas_var)
        self.mu[node_id] = max(0.0, prior_mu + kalman_gain * (value - prior_mu))
        self.var[node_id] = max(1e-9, (1.0 - kalman_gain) * prior_var)

    def on_failure(self, node_id: int, cost: float, slot: int = 0) -> None:
        """
        Truncated Gaussian update on transmission failure (censored: E < cost).
        """
        old_mu = self.mu.get(node_id, 0.0)
        old_var = self.var.get(node_id, 1e-4)
        sigma = math.sqrt(max(1e-9, old_var))

        # Standardized truncation point alpha = (cost - mu) / sigma
        alpha = (cost - old_mu) / sigma
        if alpha < -4.0:
            # Extremely unlikely failure, pull mean down aggressively
            self.mu[node_id] = max(0.0, cost / 2.0)
            self.var[node_id] = max(1e-9, (cost / 4.0) ** 2)
            return

        # Inverse Mills ratio for upper truncation: lambda(alpha) = -phi(alpha) / Phi(alpha)
        # For X ~ N(0, 1) truncated to (-inf, alpha]:
        # E[X | X <= alpha] = -phi(alpha) / Phi(alpha)
        # Var[X | X <= alpha] = 1 - delta, delta = lambda(alpha) * (lambda(alpha) - alpha)
        phi_alpha = (1.0 / math.sqrt(2 * math.pi)) * math.exp(-0.5 * alpha * alpha)
        Phi_alpha = 0.5 * (1.0 + math.erf(alpha / math.sqrt(2.0)))
        Phi_alpha = max(1e-6, Phi_alpha)

        inv_mills = phi_alpha / Phi_alpha
        trunc_mean = old_mu - sigma * inv_mills
        delta = inv_mills * (inv_mills + alpha)
        trunc_var = old_var * max(0.05, 1.0 - delta)

        self.mu[node_id] = max(0.0, min(cost, trunc_mean))
        self.var[node_id] = max(1e-9, trunc_var)


def quantize_energy(value: float, max_energy: float = 0.5, bits: int = 8) -> float:
    """
    Simulates ADC quantization on telemetry readings with 2^bits discrete levels.
    For bits=8 and max_energy=0.5J, resolution is ~1.96 mJ.
    """
    if bits <= 0:
        return max(0.0, min(max_energy, value))
    num_levels = (1 << bits) - 1
    step = max_energy / float(num_levels)
    clamped = max(0.0, min(max_energy, value))
    level = round(clamped / step)
    return float(level * step)


class HistogramBeliefView:
    """
    Histogram (discrete grid) belief filter (Tier 2 full model).
    Maintains probability distributions over K discrete battery energy bins in [0, C_i].
    Accurately handles hard boundary clipping at 0 (empty/brownout) and C_i (full saturation).
    """

    def __init__(
        self,
        nodes: Dict[int, Node],
        num_bins: int = 24,
        initial_mean: float = 0.05,
        quantization_bits: int = 8,
        measurement_std: float = 0.005
    ):
        self.nodes = nodes
        self.num_bins = max(8, num_bins)
        self.quantization_bits = quantization_bits
        self.measurement_std = measurement_std

        self.bin_edges: Dict[int, List[float]] = {}
        self.bin_centers: Dict[int, List[float]] = {}
        self.delta: Dict[int, float] = {}
        self.probs: Dict[int, List[float]] = {}

        for nid, node in nodes.items():
            cap = getattr(node, 'max_energy', 0.5)
            if cap <= 0.0:
                cap = 0.5
            w = cap / float(self.num_bins)
            self.delta[nid] = w
            edges = [k * w for k in range(self.num_bins + 1)]
            edges[-1] = cap
            centers = [(k + 0.5) * w for k in range(self.num_bins)]
            self.bin_edges[nid] = edges
            self.bin_centers[nid] = centers

            # Initial probability mass: place near node.residual_energy
            init_e = getattr(node, 'residual_energy', initial_mean)
            init_e = max(0.0, min(cap, init_e))
            p_vec = [0.0] * self.num_bins
            # Distribute with small Gaussian blur or delta mass
            b_idx = min(self.num_bins - 1, int(init_e / w))
            p_vec[b_idx] = 1.0
            self.probs[nid] = p_vec

    def p_afford(self, node_id: int, cost: float, slot: int = 0) -> float:
        """P(E >= cost) under current histogram distribution."""
        if cost <= 0.0:
            return 1.0
        if node_id not in self.probs:
            return 0.0

        w = self.delta[node_id]
        k = int(cost / w)
        if k >= self.num_bins:
            return 0.0

        probs = self.probs[node_id]
        edges = self.bin_edges[node_id]
        e_high = edges[k + 1]
        frac = (e_high - cost) / w
        total_p = probs[k] * max(0.0, min(1.0, frac)) + sum(probs[k + 1:])
        return max(0.0, min(1.0, total_p))

    def mean(self, node_id: int, slot: int = 0) -> float:
        """Expected energy in Joules."""
        if node_id not in self.probs:
            return 0.0
        return sum(p * c for p, c in zip(self.probs[node_id], self.bin_centers[node_id]))

    def variance(self, node_id: int, slot: int = 0) -> float:
        """Variance of energy belief in Joules^2."""
        if node_id not in self.probs:
            return 0.0
        m = self.mean(node_id, slot)
        return sum(p * ((c - m) ** 2) for p, c in zip(self.probs[node_id], self.bin_centers[node_id]))

    def is_available(self, node_id: int, threshold_cost: float = 1e-6) -> bool:
        return self.p_afford(node_id, threshold_cost) > 0.05

    def predict_step(
        self,
        node_id: int,
        harvest_mean: float,
        harvest_var: float,
        load_mean: float,
        load_var: float = 0.0,
        leakage_rate: float = 0.0,
        efficiency: float = 1.0,
        max_capacity: Optional[float] = None
    ) -> None:
        """
        Transition belief one step forward using discrete convolution with exact boundary clipping.
        """
        if node_id not in self.probs:
            return

        current_p = self.probs[node_id]
        centers = self.bin_centers[node_id]
        edges = self.bin_edges[node_id]
        K = self.num_bins

        new_p = [0.0] * K
        w = self.delta[node_id]
        sigma_sq = (efficiency ** 2) * harvest_var + load_var + (w ** 2) / 12.0 + 1e-7
        sigma = math.sqrt(sigma_sq)
        sqrt2 = math.sqrt(2.0)
        c_leak = 1.0 - leakage_rate

        for j, p_j in enumerate(current_p):
            if p_j < 1e-8:
                continue

            # Deterministic/mean transition from bin center j
            mu_next = c_leak * centers[j] + efficiency * harvest_mean - load_mean

            # Distribution over target bins:
            # For bin 0: P(E' < edges[1]) (clipped at 0)
            z1 = (edges[1] - mu_next) / (sigma * sqrt2)
            phi_1 = 0.5 * (1.0 + math.erf(z1)) if abs(z1) < 5.0 else (0.0 if z1 <= -5.0 else 1.0)
            new_p[0] += p_j * phi_1

            # For bin K-1: P(E' >= edges[K-1]) (clipped at C_i)
            z_last = (edges[K - 1] - mu_next) / (sigma * sqrt2)
            phi_last = 0.5 * (1.0 + math.erf(z_last)) if abs(z_last) < 5.0 else (0.0 if z_last <= -5.0 else 1.0)
            new_p[K - 1] += p_j * (1.0 - phi_last)

            # Interior bins: P(edges[k] <= E' < edges[k+1])
            prev_phi = phi_1
            for k in range(1, K - 1):
                zk = (edges[k + 1] - mu_next) / (sigma * sqrt2)
                phi_k = 0.5 * (1.0 + math.erf(zk)) if abs(zk) < 5.0 else (0.0 if zk <= -5.0 else 1.0)
                prob_k = max(0.0, phi_k - prev_phi)
                new_p[k] += p_j * prob_k
                prev_phi = phi_k

        # Normalize
        tot = sum(new_p)
        if tot > 0.0:
            self.probs[node_id] = [val / tot for val in new_p]
        else:
            self.probs[node_id][0] = 1.0

    def on_report(self, node_id: int, value: float, round_num: int) -> None:
        """
        Bayesian observation update upon receiving quantized report.
        """
        if node_id not in self.probs:
            return

        cap = self.bin_edges[node_id][-1]
        quantized = quantize_energy(value, max_energy=cap, bits=self.quantization_bits)

        centers = self.bin_centers[node_id]
        meas_std = max(1e-4, self.delta[node_id] / math.sqrt(12.0))
        two_var = 2.0 * (meas_std ** 2)

        p = self.probs[node_id]
        unnorm = []
        for k, c in enumerate(centers):
            diff = c - quantized
            likelihood = math.exp(-(diff * diff) / two_var)
            unnorm.append(p[k] * likelihood)

        tot = sum(unnorm)
        if tot > 0.0:
            self.probs[node_id] = [val / tot for val in unnorm]
        else:
            # Nearest bin
            b_idx = min(self.num_bins - 1, int(quantized / self.delta[node_id]))
            vec = [0.0] * self.num_bins
            vec[b_idx] = 1.0
            self.probs[node_id] = vec

    def on_failure(self, node_id: int, cost: float, slot: int = 0) -> None:
        """
        Censored measurement update: node failed to transmit/receive cost, so E < cost.
        Zeroes or attenuates probability mass for bins above cost.
        """
        if node_id not in self.probs:
            return

        edges = self.bin_edges[node_id]
        p = self.probs[node_id]
        unnorm = []

        for k, p_k in enumerate(p):
            e_low = edges[k]
            e_high = edges[k + 1]
            if cost >= e_high:
                # Node has strictly less than cost, so this bin is 100% consistent with failure
                factor = 1.0
            elif cost <= e_low:
                # Bin is strictly greater than cost: impossible given failure
                factor = 0.0
            else:
                # Partial overlap: fraction of bin that is strictly below cost
                factor = (cost - e_low) / (e_high - e_low)
            unnorm.append(p_k * factor)

        tot = sum(unnorm)
        if tot > 0.0:
            self.probs[node_id] = [val / tot for val in unnorm]
        else:
            vec = [0.0] * self.num_bins
            vec[0] = 1.0
            self.probs[node_id] = vec


def create_energy_view(view_type: str, nodes: Dict[int, Node], **kwargs) -> EnergyView:
    """Factory function for creating EnergyView instances."""
    vt = view_type.lower()
    if vt == 'oracle':
        return OracleView(nodes)
    elif vt == 'blind':
        default_e = kwargs.get('default_energy', 0.05)
        return BlindView(nodes, default_energy=default_e)
    elif vt == 'stale':
        init_e = kwargs.get('initial_energy', 0.05)
        return StaleView(nodes, initial_energy=init_e)
    elif vt in ('gaussian', 'belief', 'belief_gaussian'):
        init_mean = kwargs.get('initial_mean', 0.05)
        q_bits = kwargs.get('quantization_bits', 8)
        return GaussianBeliefView(nodes, initial_mean=init_mean, quantization_bits=q_bits)
    elif vt in ('histogram', 'hist', 'belief_histogram'):
        num_bins = kwargs.get('num_bins', 24)
        init_mean = kwargs.get('initial_mean', 0.05)
        q_bits = kwargs.get('quantization_bits', 8)
        return HistogramBeliefView(nodes, num_bins=num_bins, initial_mean=init_mean, quantization_bits=q_bits)
    else:
        return OracleView(nodes)
