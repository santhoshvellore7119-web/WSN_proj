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

---

### Complexity
- **Table Size:** $V \times (H + 1) \times (T + 1)$
- **Time Complexity:** $O(|E| \cdot H \cdot T)$
- **Space Complexity:** $O(V \cdot H \cdot T)$

For typical sensor networks where max hops $H \le 10$ and time horizon $T \le 10$, the 3D table is small and lookups take $< 1\text{ ms}$ in Python.

---

### Benchmark Comparison (50 Nodes, 350 Rounds)

| Configuration | First Node Death (FND) | Half Nodes Dead (HND) | Alive Nodes (Round 350) | Total Energy (J) |
| :--- | :--- | :--- | :--- | :--- |
| **Baseline (No Harvesting)** | Round 78 | Round 109 | 0 / 50 | 0.0000 J |
| **Solar (Unaware LEACH + Dijkstra)** | Round 135 | Round 208 | 1 / 50 | 0.0197 J |
| **Solar (Adaptive Time-DP)** | Round 167 | Round 208 | 0 / 50 | 0.0000 J |
| **Stochastic Poisson (Unaware LEACH)** | Round 300 | N/A | 42 / 50 | 0.2224 J |
| **Stochastic Poisson (Adaptive Time-DP)** | Round 301 | N/A | **44 / 50** | **0.2296 J** |

### Conclusion
Factoring in future recharge prevents the algorithm from unnecessarily avoiding low-energy nodes that are actively harvesting, leading to better traffic distribution and higher overall energy retention.

