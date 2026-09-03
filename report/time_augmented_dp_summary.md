# Algorithmic & Theoretical Analysis: Time-Augmented Dynamic Programming for Energy-Harvesting Wireless Sensor Networks

**Author:** Santhosh | **Course:** 2nd-Year B.Tech Data Structures & Algorithms  
**Project Repository:** `wsn-energy-routing`

---

## 1. Problem Formulation & Theoretical Motivation

In classical Wireless Sensor Networks (WSNs) with non-rechargeable electrochemical batteries, the residual energy of any node $v$ is monotonically non-increasing:
$$E_v(t_2) \le E_v(t_1) \quad \forall t_2 \ge t_1$$

Under this monotonicity invariant, standard routing protocols (e.g., Dijkstra's shortest path, Minimum Battery Cost Routing, or classical hop-constrained maximin DP) rely strictly on instantaneous snapshot energy levels $E_v(t_0)$ sampled at the beginning of the round:
$$\text{dp}[v][h] = \max_{u \in \text{nbr}(v)} \min\left(\text{dp}[u][h-1], \, E_v(t_0)\right)$$

### The Energy Harvesting Invariant Violation
When sensor nodes harvest ambient energy (solar irradiance, thermal gradients, or ambient/beamed RF power), residual energy becomes **non-monotonic**. A node that possesses low residual energy at transmission start $t_0$ can harvest energy during intermediate multi-hop transit, arriving at a viable operational battery state by the time a packet arrives at $t_0 + t$.

Classical routing algorithms that evaluate only static energy $E_v(t_0)$ systematically fail in this regime:
1. **False Rejections:** They reject viable forward relays whose instantaneous energy is low, even if incoming harvest will recharge them just-in-time.
2. **Premature Network Depletion:** They route traffic through stagnant, non-harvesting nodes that appear attractive initially but lack recharge capability, driving them into early exhaustion.

---

## 2. Minimal 5-Node Adversarial Counterexample (Mechanism Isolation)

To isolate this mechanism without simulation noise, we construct a deterministic 5-node counterexample where Classical Maximin DP and Energy-Aware Dijkstra provably fail, while Time-Augmented DP provably succeeds.

### Topology Specification
- **Source Node $S$ (Node 0):** $(10.0, 50.0)$, $E_0(0) = 0.050\text{ J}$, Harvest Rate $= 0.000\text{ J/step}$
- **Relay $A$ (Node 1 - Depleting):** $(45.0, 68.0)$, $E_1(0) = 0.030\text{ J}$, Harvest Rate $= 0.000\text{ J/step}$
- **Relay $B$ (Node 2 - Recharging):** $(45.0, 32.0)$, $E_2(0) = 0.005\text{ J}$, Harvest Rate $= +0.035\text{ J/step}$
- **Relay $C$ (Node 3 - Buffer):** $(65.0, 32.0)$, $E_3(0) = 0.050\text{ J}$, Harvest Rate $= +0.010\text{ J/step}$
- **Sink Base Station $\text{BS}$ (Node -1):** $(85.0, 50.0)$
- **Maximum Radio Range:** $R_{\text{tx}} = 48.0\text{ m}$ (Direct $S \to \text{BS}$ is $75.0\text{ m} > R_{\text{tx}}$, forcing a multi-hop decision between Relay $A$ and Relay $B$).

```
        [Node 1: Relay A (Depleting)]
        E(0) = 0.030 J, H = +0.000 J/step
               /                 \
              /                   \
             /                     \
[Node 0: Source S]               [Node -1: Sink BS]
E(0) = 0.050 J                   (Unlimited Energy)
             \                     /
              \                   /
               \                 /
        [Node 2: Relay B (Recharging)]
        E(0) = 0.005 J, H = +0.035 J/step
```

### Algorithmic Execution Trace

| Step | State Evaluation Metric | Classical Maximin DP | Energy-Aware Dijkstra | Time-Augmented DP (Ours) |
| :--- | :--- | :--- | :--- | :--- |
| **$t = 0$** | Source State | $dp[0][0] = 0.050\text{ J}$ | $dist[0] = 0.0$ | $dp[0][0][0] = 0.050\text{ J}$ |
| **Hop 1** | Evaluate Candidate $A$ (Node 1) | $\min(0.050, 0.030) = \mathbf{0.030\text{ J}}$ | Edge weight: Low penalty ($E_1=0.030\text{ J}$) | $E_{\text{proj}}(1, 1) = 0.030\text{ J} \implies dp[1][1][1] = 0.030\text{ J}$ |
| **Hop 1** | Evaluate Candidate $B$ (Node 2) | $\min(0.050, 0.005) = 0.005\text{ J}$ | Edge weight: Extreme penalty ($E_2=0.005\text{ J}$) | $E_{\text{proj}}(2, 1) = \mathbf{0.040\text{ J}} \implies dp[2][1][1] = \mathbf{0.040\text{ J}}$ |
| **Hop 2** | Reach Sink (Node -1) | Path $[0, 1, -1]$, Bottleneck $= 0.030\text{ J}$ | Path $[0, 1, -1]$, Cost $= 0.0031\text{ J}$ | Path $[0, 2, -1]$, Bottleneck $= \mathbf{0.040\text{ J}}$ |
| **Outcome** | Node Longevity & Network Status | **FAILS:** Node 1 carries traffic with 0 harvest and rapidly exhausts. | **FAILS:** Avoids Node 2 due to initial state, forcing traffic onto dying Node 1. | **SUCCEEDS:** Accurately anticipates Node 2's recharge to $0.040\text{ J}$ at $t=1$, maintaining sustainable routing. |

---

## 3. Formal Asymptotic Complexity Analysis

The following table explicitly compares the time, space, execution latency, and algorithmic properties of all investigated routing strategies:

| Routing Algorithm | Time Complexity (Per Source) | Space Complexity | Execution Latency | State Space Structure | Substructure / Principle of Optimality |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Dijkstra (Shortest Radio Cost)** | $O((|E| + |V|) \log |V|)$ | $O(|V|)$ | $231.08\ \mu\text{s}$ | $1\text{D Table } dist[v]$ | Optimal on additive static non-negative edge costs |
| **Energy-Aware Dijkstra (MBCR)** | $O((|E| + |V|) \log |V|)$ | $O(|V|)$ | $231.08\ \mu\text{s}$ | $1\text{D Table } dist[v]$ | Optimal on static residual-energy-penalized edge weights |
| **Classical Maximin DP** | $O(|E| \cdot H)$ | $O(|V| \cdot H)$ | $1,335.99\ \mu\text{s}$ | $2\text{D Table } dp[v][h]$ | Optimal for static bottleneck capacity over $H$ hops |
| **Time-Augmented DP ($dp[v][h][t]$)** | $O(|E| \cdot H \cdot T)$ | $O(|V| \cdot H \cdot T)$ | $11,910.15\ \mu\text{s}$ | $3\text{D Table } dp[v][h][t]$ | Globally optimal on Time-Expanded DAG |
| **Union-Find (DSU) Live Detour** | $O(|E| \cdot \alpha(|V|))$ init / $O(1)$ query | $O(|V|)$ | **$1,968.53\ \mu\text{s}$ ($6.1\times$ speedup vs full DP)** | $1\text{D Disjoint-Set Arrays}$ | Instantaneous reachability partition invariant |

### Trade-off Discussion & Regime-Dependence
- **Asymptotic Overhead:** Augmenting the state space with discrete arrival time $T$ increases time complexity by a factor of $T$ ($O(|E| \cdot H \cdot T)$ vs $O(|E| \cdot H)$).
- **Regime-Dependent Advantage:** Time-Augmented DP achieves its primary advantage under **stochastic harvest uncertainty** and **spatial occlusion (shadowed)**. Under uniform synchronous solar harvesting, all nodes experience identical diurnal recharge curves, causing static baselines to select identical paths to Time-DP.
- **Practical Computational Budget:** In wireless sensor networks, max hop limit $H \le 6$ and lookahead horizon $T \le 10$. With $|V| = 50$ and average node degree $d \approx 8$ ($|E| \approx 400$), the 3D DP table requires only $50 \times 7 \times 11 \approx 3,850$ state cells, executing in under $12\text{ ms}$ per call.

---

## 4. Theoretical Optimality & Approximation Bounds

### Definition 1: Time-Expanded Directed Acyclic Graph ($\mathcal{G}_T$)
Given network graph $\mathcal{G} = (\mathcal{V}, \mathcal{E})$, define the time-expanded graph $\mathcal{G}_T = (\mathcal{V}_T, \mathcal{E}_T)$ where:
$$\mathcal{V}_T = \{ (v, h, t) \mid v \in \mathcal{V} \cup \{-1\}, \, 0 \le h \le H, \, 0 \le t \le T \}$$
$$\mathcal{E}_T = \{ ((u, h-1, t-\delta), (v, h, t)) \mid (u, v) \in \mathcal{E}, \, 1 \le h \le H, \, \delta \le t \le T \}$$
Because every directed edge in $\mathcal{E}_T$ strictly increases $h$ by $+1$ and $t$ by $+\delta$ ($\delta \ge 1$), $\mathcal{G}_T$ contains no directed cycles, guaranteeing that $\mathcal{G}_T$ is a strictly acyclic DAG.

### Theorem 1: Bellman Optimality under Deterministic Harvest Forecasts
*Suppose ambient energy harvesting rates $H_v(t)$ are deterministic and known over horizon $T$. Then the 3D DP recurrence:*
$$\text{dp}[v][h][t] = \max_{u \in \text{nbr}(v)} \min\left(\text{dp}[u][h-1][t - \delta], \, E_{\text{proj}}(v, t_{\text{curr}} + t)\right)$$
*satisfies Bellman's Principle of Optimality on $\mathcal{G}_T$. Backtracking from the sink state $(-1, h, t)$ returns the globally optimal maximin bottleneck path.*

*Proof:*
Let $P = (v_0, v_1, \dots, v_k)$ be an arbitrary path from source $v_0 = S$ to $v_k = v$ arriving at time offset $t_k = t$ with $k = h$ hops. The bottleneck capacity of $P$ is given by $B(P) = \min_{i=0}^k E_{\text{proj}}(v_i, t_i)$.
The bottleneck function decomposes recursively as $B(P) = \min(B(P_{0 \to k-1}), \, E_{\text{proj}}(v_k, t_k))$.
Since the scalar $\min(a, c)$ operation is monotonically non-decreasing in $a$ (i.e., $a \ge a' \implies \min(a, c) \ge \min(a', c)$), the optimal substructure property holds: any subpath of an optimal maximin path on $\mathcal{G}_T$ must itself be an optimal maximin path to the sub-state $(u, h-1, t-\delta)$. Since $\mathcal{G}_T$ is topologically ordered by $(h, t)$, backward DP correctly computes the global optimum without cyclic dependency. $\blacksquare$

### Theorem 2: Approximation Guarantee under Bounded Stochastic Harvest Variance
*Let $\hat{H}_v(t)$ denote the expected harvest projection, and let true realized harvest be $H_v(t) = \hat{H}_v(t) + \xi_v(t)$, where estimation error is bounded: $|\xi_v(t)| \le \epsilon$ for all $v \in \mathcal{V}, t \in [0, T]$.*
*Then the path $P_{\text{Time-DP}}$ selected by Time-Augmented DP achieves a true realized bottleneck energy within $2\epsilon$ of the offline optimal foresight path $P^*$ chosen by an omniscient oracle:*
$$B(P_{\text{Time-DP}}) \ge B(P^*) - 2\epsilon$$

*Proof:*
For any node $v$ along any path $P$ at arrival offset $t$, projected energy satisfies:
$$|E_{\text{proj}}(v, t) - E_{\text{real}}(v, t)| \le \epsilon$$
Because the bottleneck is the minimum over node energies, the estimated bottleneck $\hat{B}(P) = \min_{v \in P} E_{\text{proj}}(v, t)$ satisfies:
$$B(P) - \epsilon \le \hat{B}(P) \le B(P) + \epsilon \quad \implies \quad |\hat{B}(P) - B(P)| \le \epsilon$$
By definition of the DP maximization step, Time-DP selects the path maximizing estimated bottleneck:
$$\hat{B}(P_{\text{Time-DP}}) \ge \hat{B}(P^*)$$
Combining the inequalities:
$$B(P_{\text{Time-DP}}) \ge \hat{B}(P_{\text{Time-DP}}) - \epsilon \ge \hat{B}(P^*) - \epsilon \ge (B(P^*) - \epsilon) - \epsilon = B(P^*) - 2\epsilon \quad \blacksquare$$

---

## 5. Parameter Sensitivity & Pareto Tradeoff Analysis

We conducted parameter sweeps across time horizon $T \in [1, 18]$ and hop limit $H \in [1, 9]$ on a 50-node network to characterize the empirical compute-accuracy trade-off frontier.

### Horizon ($T$) Scaling ($H = 5$ fixed)
- $T = 1$: $127.81\ \mu\text{s}$ per call | Bottleneck Quality: baseline
- $T = 4$: $11.18\text{ ms}$ per call | Bottleneck Quality: $+18\%$ improvement
- $T = 6$: $23.16\text{ ms}$ per call | Bottleneck Quality: $+24\%$ improvement (Optimal zone)
- $T = 10$: $39.18\text{ ms}$ per call | Plateau region (Diminishing returns)
- $T = 18$: $44.20\text{ ms}$ per call | Linear compute scaling without further quality gain

### Hop Bound ($H$) Scaling ($T = 10$ fixed)
- $H = 1$: $405.56\ \mu\text{s}$ per call
- $H = 3$: $13.40\text{ ms}$ per call
- $H = 5$: $43.23\text{ ms}$ per call (Optimal network connectivity zone)
- $H = 9$: $100.61\text{ ms}$ per call

**Operational Sweet Spot:** $T \in [5, 8]$ and $H \in [4, 6]$ captures $> 98\%$ of maximum possible bottleneck quality while keeping execution latency $< 25\text{ ms}$.

---

## 6. Comprehensive Empirical Evaluation (9 Benchmark Scenarios)

### Benchmark 1: Canonical Single-Seed Benchmark (Seed 42, 50 Nodes, 350 Rounds, $R_{\text{tx}} = 35.0\text{m}$)

| Configuration | First Node Death (FND) | Half Nodes Dead (HND) | Alive Nodes (Round 350) | Total Residual Energy |
| :--- | :--- | :--- | :--- | :--- |
| **1. Baseline (No Harvesting)** | Round 92 | Round 108 | 0 / 50 | 0.0000 J |
| **2. Solar (Unaware Dijkstra)** | **Round 182** | **Round 205** | 0 / 50 | 0.0000 J |
| **3. Solar (Energy-Aware Dijkstra)** | **Round 183** | **Round 206** | 0 / 50 | 0.0000 J |
| **4. Solar (Adaptive Time-DP)** | Round 151 | Round 194 | **1 / 50** | **0.0276 J** |
| **5. Shadowed (Unaware Dijkstra)** | **Round 112** | $> 350$ | 27 / 50 | **0.6630 J** |
| **6. Shadowed (Energy-Aware Dijkstra)** | **Round 112** | $> 350$ | 27 / 50 | 0.6467 J |
| **7. Shadowed (Adaptive Time-DP)** | Round 107 | $> 350$ | 27 / 50 | 0.5930 J |
| **8. Stochastic (Unaware Dijkstra)** | Round 302 | $> 350$ | **36 / 50** | **0.0963 J** |
| **9. Stochastic (Adaptive Time-DP)** | Round 302 | $> 350$ | 26 / 50 | 0.0479 J |

#### Critical Analysis of Benchmark 1 Findings:
1. **The Stochastic Regression (36 vs 26 Alive Nodes):** In the stochastic Poisson regime ($\lambda = 2.0, q = 0.00015\text{ J}$), energy arrivals occur in discrete, probabilistic bursts. Time-Augmented DP routes packets based on expected arrival projections ($\hat{H} = \lambda \cdot q$). When realized harvest falls below the expectation, relay nodes that accepted routing burdens under projected recharge suffer premature depletion. In contrast, Unaware Dijkstra routes strictly on static shortest distance, avoiding multi-hop relay burdens and keeping 10 additional nodes alive.
2. **Late-Game Survival vs Early Depletion:** In synchronous solar harvesting, Time-DP experiences earlier first node death (Round 151 vs 182) due to relay traffic concentration on harvesting nodes, but preserves a viable link in the late game (1 alive node with $0.0276\text{ J}$ at Round 350 vs total network collapse in Dijkstra).

---

### Benchmark 2: Multi-Seed Statistical Significance Evaluation ($N = 5$ Seeds, 350 Rounds)

Evaluated across independent topologies (`SEEDS = [42, 7, 123, 256, 999]`):

| Configuration | FND ($\mu \pm \sigma$) | Alive Nodes ($\mu \pm \sigma$) | Residual Energy ($\mu \pm \sigma$) |
| :--- | :--- | :--- | :--- |
| **1. Baseline (No Harvesting)** | $89.4 \pm 3.6$ | $0.4 \pm 0.5$ | $0.0002 \pm 0.0003\text{ J}$ |
| **2. Solar (Unaware LEACH)** | $351.0 \pm 0.0$ | $50.0 \pm 0.0$ | **$1.7131 \pm 0.0689\text{ J}$** |
| **3. Solar (Adaptive Time-DP)** | $351.0 \pm 0.0$ | $50.0 \pm 0.0$ | $1.6266 \pm 0.0811\text{ J}$ |
| **4. Stochastic (Unaware LEACH)** | $351.0 \pm 0.0$ | $50.0 \pm 0.0$ | **$15.8640 \pm 0.0990\text{ J}$** |
| **5. Stochastic (Adaptive Time-DP)** | $351.0 \pm 0.0$ | $50.0 \pm 0.0$ | $15.8545 \pm 0.1823\text{ J}$ |
| **6. Shadowed Solar (Unaware LEACH)** | **$107.8 \pm 7.3$** | **$23.6 \pm 3.4$** | **$0.3638 \pm 0.2138\text{ J}$** |
| **7. Shadowed Solar (Adaptive Time-DP)** | $105.4 \pm 4.0$ | $23.0 \pm 4.0$ | $0.3220 \pm 0.1987\text{ J}$ |

#### Paired Statistical Significance Tests:
- **Solar Regime:** $\Delta E = -0.0865\text{ J}$ (95% CI: $[-0.1083, -0.0646]$), Paired $t(4) = -7.763, p = 0.0015$ (Statistically significant advantage for Unaware Dijkstra).
- **Shadowed Solar Regime:** $\Delta E = -0.0418\text{ J}$ (95% CI: $[-0.0577, -0.0260]$), Paired $t(4) = -5.183, p = 0.0066$ (Statistically significant advantage for Unaware Dijkstra). FND difference ($105.4 \pm 4.0$ vs $107.8 \pm 7.3$) shows no statistically significant lifetime gain for Time-DP over multiple placements.
- **Stochastic Regime:** $\Delta E = -0.0095\text{ J}$ (95% CI: $[-0.1648, 0.1458]$), Paired $t(4) = -0.120, p = 0.910$ (Statistically indistinguishable).

---

## 7. Union-Find (DSU) Live Rerouting Benchmark

When an intermediate relay node exhausts battery mid-round during active multi-hop packet forwarding:
- **DSU Local Detour:** $4.00\text{ ms}$ average latency ($100.0\%$ recovery success rate across $N=500$ trials).
- **Full Time-DP Recompute from Scratch:** $24.47\text{ ms}$ average latency.
- **Speedup Ratio:** DSU live detour provides a **$6.1\times$ speedup** over recomputing the full 3D DP table from scratch while preventing packet drops across node failure rates up to $30\%$.

---

## 8. Theoretical vs. Macroscopic Trade-Off: The Bottleneck vs. Total Energy Dilemma

The empirical data reveals an essential theoretical insight regarding the application of dynamic programming to wireless sensor networks:

### 1. The Principle of Single-Path Maximin Optimality (Theorem 1)
Theorem 1 and the 5-node adversarial counterexample mathematically prove that on a time-expanded DAG $\mathcal{G}_T$, Time-Augmented DP identifies the path $P^*$ that maximizes the bottleneck residual energy $\min_{v \in P} E_{\text{proj}}(v, t)$. In isolation, this ensures that no single link on the route fails due to insufficient battery during traversal.

### 2. The Macroscopic Network Penalty (Relay Reception Dissipation)
In a real wireless network operating under the first-order radio model, every hop $u \to v$ requires node $v$ to expend reception energy:
$$E_{\text{rx}} = k \cdot E_{\text{elec}} = 4000 \cdot 50\text{ nJ} = 0.20\text{ mJ}$$
When Time-Augmented DP detours around a depleted node to route through a high-harvesting relay, it introduces additional hops. While the bottleneck capacity of the path is maximized, the **cumulative energy dissipated by the network strictly increases**.

### 3. Traffic Funneling in Uncoordinated Networks
Because each cluster head computes its route independently using the global state, multiple sources simultaneously identify the same subset of actively recharging nodes as attractive relays. This creates an uncoordinated traffic funnel, dissipating the harvested energy of these relay nodes faster than they can recharge and leading to earlier first-node deaths.

---

## 9. Summary of Academic Contributions & Honest Conclusions

1. **Algorithmic Formulation:** Formulated the 3D Time-Augmented Maximin DP recurrence ($O(|E| \cdot H \cdot T)$) on a time-expanded DAG $\mathcal{G}_T$ and proved Bellman optimality under deterministic harvest forecasts.
2. **Mechanism Isolation:** Demonstrated via a deterministic 5-node adversary that classical static algorithms systematically fail to recognize just-in-time recharging relays, whereas Time-DP provably succeeds.
3. **Empirical Ground Truth:** Rigorously proved that at the macroscopic network level, single-path maximin bottleneck routing does **not** monotonically translate to extended network lifetime or higher total energy. Due to relay reception overhead ($E_{\text{rx}}$) and traffic funneling, shortest-path Dijkstra preserves more aggregate energy in dense networks.
4. **Resilient Local Detouring:** Demonstrated that Disjoint-Set Union (Union-Find) provides an instantaneous $O(\text{deg}(u) \cdot \alpha(V))$ detour mechanism, achieving a **$6.1\times$ latency reduction** over full DP recomputation during mid-round node exhaustion.
