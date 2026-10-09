# Experimental Hypotheses: Routing Under Energy Uncertainty

Prior to running empirical benchmark experiments across common-random-number seeds, the following hypotheses are formally registered.

---

### Hypothesis 1 (H1: Delivery Performance Hierarchy)
**Statement:**
In energy-constrained regimes (Poor and Balanced with environmental variance), belief-driven probabilistic routing ($M_3$: Max-Product Time-DP) achieves strictly higher Packet Delivery Ratio (PDR) than stale-report routing ($M_1$) and energy-blind shortest path ($M_0$):
$$\text{PDR}(M_3) > \text{PDR}(M_1) > \text{PDR}(M_0)$$
Furthermore, as telemetry reporting frequency increases (report interval $R \to 1$), the performance gap between $M_3$ and the omniscient oracle upper-bound ($M_2$) contracts monotonically:
$$\lim_{R \to 1} [\text{PDR}(M_2) - \text{PDR}(M_3)] \approx 0$$

---

### Hypothesis 2 (H2: Boundary Calibration under Clipping)
**Statement:**
The $K$-bin discrete Histogram Belief Filter yields significantly superior calibration metrics—lower Brier score and lower Expected Calibration Error (ECE)—than a parametric Gaussian filter, especially near the boundary extremes of battery exhaustion ($E \to 0$, brownout) and solar saturation ($E \to C_i$):
$$\text{ECE}_{\text{histogram}} < \text{ECE}_{\text{gaussian}}, \quad \text{Brier}_{\text{histogram}} < \text{Brier}_{\text{gaussian}}$$
Synthetic credible intervals computed from the histogram distribution achieve empirical coverage within $\pm 10\%$ of nominal confidence ($1 - \alpha = 0.90$).

---

### Hypothesis 3 (H3: Value of Recharge Waiting Dimension)
**Statement:**
Augmenting dynamic programming with a time dimension and recharge waiting deadline $w \in [0, D]$ ($M_3$) provides statistically significant delivery gains over memoryless instantaneous routing ($M_5$, where $w = 0$), with the largest effect size observed under scarce harvest (Poor regime) and high weather variance ($\sigma_{\text{solar}} \ge 0.3$):
$$\text{PDR}(M_3 \mid D > 0) > \text{PDR}(M_5 \mid D = 0)$$

---

### Hypothesis 4 (H4: Hotspot Protection via Sequential Load Reservations)
**Statement:**
Sequential load reservations along committed paths shift relay energy beliefs by expected reception and transmission costs, mitigating contention collapse and reducing wasted transmission energy when multiple cluster heads contend for common bottleneck relays:
$$\text{EnergyWasted}_{\text{reservations}} < \text{EnergyWasted}_{\text{no-reservations}}$$
$$\text{PDR}_{\text{reservations}} \ge \text{PDR}_{\text{no-reservations}}$$

---

### Statistical Evaluation Protocol
- **Evaluation Metric:** True Packet Delivery Ratio ($\text{PDR} = \text{PacketsDelivered} / \text{PacketsGenerated}$), Hop Latency, Energy Wasted (Joules), Brier Score, ECE.
- **Sample Size:** 30 independent seeds per configuration with Common Random Numbers (CRN) for node topology and solar harvest realizations.
- **Hypothesis Testing:** Non-parametric Wilcoxon signed-rank paired tests with Holm-Bonferroni correction ($\alpha = 0.05$) and Cliff's Delta / Cohen's $d$ effect sizes.
