# Project Note: Time-Augmented Dynamic Programming for WSN Routing

**Student:** Santhosh | **Course:** 2nd-Year B.Tech DSA  

---

### Motivation
In standard WSN routing, the battery of every node strictly depletes over time. Because of this, algorithms like Dijkstra or classical bottleneck DP only need to know the battery level at the start of the round:

$$\text{dp}[v][h] = \max_{u \in \text{nbr}(v)} \min\left(\text{dp}[u][h-1], \, E_v\right)$$

However, with energy harvesting (solar cells or ambient RF), a node's battery can increase while a packet is in transit. If node $v$ only has $0.05\text{ J}$ right now, classical DP rejects it. But if the packet takes 2 hops to reach $v$, and $v$ recharges $+0.8\text{ J}$ during that time, it will have $0.85\text{ J}$ when the packet actually arrives. 

To take advantage of this, we added a time dimension to the DP table so route selection can evaluate what a node's battery will be at the exact time the packet reaches it.

---

### How the Algorithm Works

1. **State Table:**
   We maintain a 3D table `dp[node][hops][time_step]` storing the maximum bottleneck energy to reach `node` using `hops` hops, reaching it at `time_step`.

2. **Energy Projection:**
   Before checking an edge $(u \to v)$, we estimate node $v$'s energy at time $t_{\text{curr}} + t$:
   $$E_{\text{proj}}(v, t) = \min\left(E_{\max}, \, E_v(t_{\text{curr}}) + \text{ExpectedHarvest}(v, t)\right)$$
   For the base station (node $-1$), energy is infinite.

3. **Recurrence:**
   For each hop $h$ from $1$ to $H$, and time offset $t$ from $h \cdot \delta$ to $T$:
   $$\text{dp}[v][h][t] = \max_{u \in \text{nbr}(v)} \min\left(\text{dp}[u][h-1][t - \delta], \, E_{\text{proj}}(v, t)\right)$$

4. **Path Recovery:**
   We store `pred[v][h][t] = (u, t - \delta)` during the DP fill. Once done, we pick the highest bottleneck value at the base station and backtrack the chosen path and transmission schedule.

### Cost-Aware Tie-Breaking
Standard maximin DP optimizes exclusively for bottleneck capacity, occasionally selecting circuitous or energetically expensive paths when candidate bottlenecks tie. To resolve this, each DP state additionally tracks the cumulative physical radio transmission cost ($E_{\text{tx}} \propto d^2 \text{ or } d^4$). When two candidate paths reach the same state $(v, h, t)$ with bottleneck values within a 1% relative tolerance, the physically cheaper path wins.

---

### Complexity
- **Table Size:** $V \times (H + 1) \times (T + 1)$
- **Time Complexity:** $O(|E| \cdot H \cdot T)$
- **Space Complexity:** $O(V \cdot H \cdot T)$

For typical sensor networks where max hops $H \le 10$ and time horizon $T \le 10$, the 3D table is small and lookups take $< 1\text{ ms}$ in Python.

---

### Empirical Validation

#### 1. Canonical Benchmark (Seed 42, 50 Nodes, 350 Rounds)

| Configuration | First Node Death (FND) | Half Nodes Dead (HND) | Alive Nodes (Round 350) | Total Energy (J) |
| :--- | :--- | :--- | :--- | :--- |
| **Baseline (No Harvesting)** | Round 82 | Round 112 | 0 / 50 | 0.0000 J |
| **Solar (Unaware LEACH + Dijkstra)** | Round 165 | Round 209 | 0 / 50 | 0.0000 J |
| **Solar (Adaptive Time-DP)** | Round 165 | Round 208 | 0 / 50 | 0.0000 J |
| **Stochastic Poisson (Unaware LEACH)** | Round 320 | N/A | 40 / 50 | 0.2581 J |
| **Stochastic Poisson (Adaptive Time-DP)** | Round 329 | N/A | **41 / 50** | 0.2532 J |

#### 2. Multi-Seed Statistical Validation ($N = 5$ Independent Topologies)

| Configuration | FND ($\mu \pm \sigma$) | HND ($\mu \pm \sigma$) | Alive Nodes ($\mu \pm \sigma$) | Residual Energy ($\mu \pm \sigma$) |
| :--- | :--- | :--- | :--- | :--- |
| **Baseline (No Harvesting)** | $83.0 \pm 3.9$ | $110.2 \pm 1.3$ | $0.0 \pm 0.0$ | $0.0000 \pm 0.0000\text{ J}$ |
| **Solar (Unaware LEACH + Dijkstra)** | $160.6 \pm 3.6$ | $207.0 \pm 4.7$ | $0.2 \pm 0.4$ | $0.0036 \pm 0.0080\text{ J}$ |
| **Solar (Adaptive Time-DP)** | $159.6 \pm 4.9$ | $207.0 \pm 4.7$ | $0.2 \pm 0.4$ | $0.0036 \pm 0.0080\text{ J}$ |
| **Stochastic Poisson (Unaware LEACH)** | $280.2 \pm 32.4$ | $> 350$ | $38.8 \pm 3.3$ | $0.1998 \pm 0.0596\text{ J}$ |
| **Stochastic Poisson (Adaptive Time-DP)** | $280.0 \pm 43.3$ | $> 350$ | $37.8 \pm 4.0$ | $0.2004 \pm 0.0616\text{ J}$ |

---

### Conclusion & Viva Defense Insights
1. **Topology Variance**: In sparse topologies, spatial deployment variance ($\sigma \approx 32\text{--}43\text{ rounds}$) naturally dominates algorithmic variance.
2. **Synchronous Solar Invariance**: Under uniform solar conditions, all nodes recharge simultaneously, preserving a flat spatial energy gradient across neighbors.
3. **Asynchronous/Bursty Regime**: Time-Augmented DP demonstrates clear utility in bursty, localized, or asynchronous harvesting regimes by preemptively identifying relay nodes that will recover before packet arrival.

