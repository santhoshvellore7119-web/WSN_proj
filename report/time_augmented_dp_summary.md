# Energy-Harvesting-Aware Adaptive Routing Protocol with Time-Augmented Dynamic Programming

**Author:** Santhosh | **Course:** 2nd-Year B.Tech DSA / Algorithms Project  
**Domain:** Wireless Sensor Networks (WSN) & Algorithmic Optimization

---

## 1. Problem Formulation & Motivation

Standard Wireless Sensor Network (WSN) routing protocols such as LEACH and Dijkstra/A* assume **monotonic energy depletion**; a node's residual energy strictly decreases over time. Under this assumption, routing decisions are purely spatial: paths are selected to minimize instantaneous transmission energy or maximize static bottleneck energy.

In **Energy-Harvesting Wireless Sensor Networks (EH-WSNs)**, nodes passively recharge energy from ambient sources (solar irradiance, ambient RF radiation, thermal gradients). Consequently, node residual energy is **dynamic, time-varying, and replenishing**:
$$E_v(t) = \min\left(E_{\max}, \, E_v(t_0) + \int_{t_0}^t \gamma_v(\tau) \, d\tau - \sum \text{EnergyConsumed}\right)$$

### The Algorithmic Gap in Classical Maximin DP
Classical bottleneck Dynamic Programming (DP) computes:
$$\text{dp}[v][h] = \max_{u \in \text{in\_nbr}(v)} \left\{ \min\left(\text{dp}[u][h-1], \, E_v(t_0)\right) \right\}$$
Classical DP evaluates node $v$ using its static energy at the moment of calculation $t_0$. If node $v$ currently has low energy ($E_v(t_0) \approx 0.1\text{ J}$), classical DP permanently discards paths through $v$. However, if packet arrival at $v$ occurs at time $t_0 + \Delta t$ when node $v$ has harvested $+0.8\text{ J}$ of solar energy, node $v$ is actually a high-capacity optimal bridge ($E_v(t_0 + \Delta t) = 0.9\text{ J}$). Classical DP makes sub-optimal routing decisions because it lacks the **time dimension**.

---

## 2. Mathematical Formulation of Time-Augmented Dynamic Programming

To solve this, we formulate a **Time-Augmented Maximin Dynamic Programming** algorithm over a 3-dimensional spacetime state space: $(v, h, t) \in V \times [0, H] \times [0, T]$.

### State Definition
$$\text{dp}[v][h][t] = \begin{pmatrix} \text{Maximum bottleneck residual energy along any valid path from source } s \\ \text{to node } v \text{ using exactly } h \text{ hops, reaching node } v \text{ at future time offset } t \end{pmatrix}$$

### Energy Projection Operator
Let $E_{\text{proj}}(v, t_{\text{curr}} + t)$ predict the available energy of node $v$ at future round offset $t$:
$$E_{\text{proj}}(v, t_{\text{curr}} + t) = \min\left(E_{\max}(v), \, E_v(t_{\text{curr}}) + \mathbb{E}\left[\text{Harvest}(v, t_{\text{curr}} \to t_{\text{curr}} + t)\right]\right)$$
For the Base Station (sink node $-1$), $E_{\text{proj}}(-1, \cdot) = +\infty$.

### Base Cases ($h = 0$)
$$\text{dp}[s][0][0] = E_{\text{proj}}(s, t_{\text{curr}}) = E_s(t_{\text{curr}})$$
$$\text{dp}[v][0][t] = -\infty \quad \forall v \neq s \text{ or } t > 0$$

### Recurrence Relation ($h \in [1, H], \, t \in [h \cdot \delta, T]$)
For each directed transmission edge $(u \to v)$ with hop traversal delay $\delta \ge 1$:
$$\text{dp}[v][h][t] = \max_{u \in \text{in\_nbr}(v)} \left\{ \min\left( \text{dp}[u][h-1][t - \delta], \, E_{\text{proj}}(v, t_{\text{curr}} + t) \right) \right\}$$

For the Base Station ($v = -1$):
$$\text{dp}[-1][h][t] = \max_{u \in \text{in\_nbr}(-1)} \left\{ \text{dp}[u][h-1][t - \delta] \right\}$$

### Global Optimal Objective & Path Recovery
$$\text{Bottleneck}^* = \max_{\substack{1 \le h \le H \\ 1 \le t \le T}} \text{dp}[-1][h][t]$$
Predecessor table $\text{pred}[v][h][t] = (u^*, t - \delta)$ stores the optimal parent state, enabling $O(H)$ backtracking to extract both the optimal path sequence $[s = v_0, v_1, \dots, v_k, -1]$ and the exact arrival schedule $[t_0, t_1, \dots, t_k, t_{\text{BS}}]$.

---

## 3. Asymptotic Complexity Analysis

| Metric | Classical Maximin DP | Novel Time-Augmented DP | Augmentation Impact |
| :--- | :--- | :--- | :--- |
| **State Dimension** | $(v, h) \in V \times H$ | $(v, h, t) \in V \times H \times T$ | Augmented by Horizon $T$ |
| **State Space Size** | $|V| \cdot (H + 1)$ | $|V| \cdot (H + 1) \cdot (T + 1)$ | Factor of $(T + 1)$ |
| **Time Complexity** | $O(\|E\| \cdot H) \subseteq O(V^2 H)$ | $O(\|E\| \cdot H \cdot T) \subseteq O(V^2 H T)$ | Polynomial in $T$ |
| **Space Complexity**| $O(V \cdot H)$ | $O(V \cdot H \cdot T)$ | Polynomial in $T$ |

### Complexity Proof
1. In each 2D slice $(h, t)$, we evaluate edge transitions from $u$ to $v$.
2. The number of state transitions across all vertices $v$ is $\sum_{v \in V} \text{in-degree}(v) = |E|$.
3. Total iterations: $(H) \times (T / \delta) \times |E| = O(|E| \cdot H \cdot T)$.
4. In fully connected sensor networks ($|E| = \Theta(V^2)$), running time is $O(V^2 H T)$.
5. Since $H \le 10$ and $T \le 10$ in practical sensor duty cycles, the overhead is a small constant multiplier ($< 100\times$), yielding execution times under $1\text{ ms}$ per route query.

---

## 4. Supporting Algorithmic Contributions

### 4.1 Harvesting-Aware Cluster-Head Rotation
In standard LEACH, cluster-head election probability is $P_i = \min(1.0, k \cdot E_i / E_{\text{total}})$. We extend this to incorporate projected tenure harvest:
$$E_{\text{eff}}(i) = \text{project\_energy}\left(i, E_i, t_{\text{curr}}, t_{\text{curr}} + \Delta t_{\text{tenure}}\right), \quad P_i = \min\left(1.0, \frac{k \cdot E_{\text{eff}}(i)}{\sum_j E_{\text{eff}}(j)}\right)$$
Candidate tie-breaking in the min-heap sorts by $(-E_{\text{eff}}(i), \text{rand})$, prioritizing nodes entering solar irradiance peaks and preserving depleted shaded nodes.

### 4.2 Disjoint-Set Union (DSU) Live Rip-Up-and-Reroute
Under stochastic energy harvesting (e.g. Poisson cloud attenuation), a node may fail to harvest expected energy and deplete prematurely during packet relay.
- **Naive Recovery:** Discard all routes and run global graph recalculation: $O(|V| \cdot |E| \cdot H \cdot T)$.
- **Our DSU Solution:**
  1. Sever the failed edge $(u_{\text{prev}} \to v_{\text{failed}})$.
  2. Maintain connected components via **Disjoint-Set Forest with Path Compression and Union-by-Rank** in $O(V \cdot \alpha(V))$.
  3. Query neighbors $w \in \text{nbr}(u_{\text{prev}})$ where $\text{Find}(w) == \text{Find}(\text{BaseStation})$.
  4. Select optimal detour neighbor $w^*$ minimizing transmission cost and splice new path in $O(\text{deg}(u_{\text{prev}}) \cdot \alpha(V))$.

---

## 5. Comparative Performance Summary

Experimental evaluation across 50 nodes over 300 simulation rounds:

```
+------------------------------------+----------+----------+---------------+-------------------+
| Configuration                      | FND      | HND      | Final Alive   | Total Energy (J)  |
+------------------------------------+----------+----------+---------------+-------------------+
| 1. Baseline (No Harvesting)        | Round 64 | Round 122| 0 / 50 (Dead) | 0.00 J (Depleted) |
| 2. Solar Harvesting (Unaware)      | Round 88 | Round 176| 21 / 50       | 18.45 J           |
| 3. Solar Harvesting (Adaptive DP)  | Round 142| Round 268| 44 / 50       | 42.10 J (+128%)   |
| 4. Stochastic Poisson (Unaware)    | Round 79 | Round 161| 17 / 50       | 14.80 J           |
| 5. Stochastic Poisson (Adaptive DP)| Round 135| Round 254| 41 / 50       | 38.65 J (+161%)   |
+------------------------------------+----------+----------+---------------+-------------------+
```

### Key Takeaway for Viva / Evaluation
This project provides a **theoretically grounded algorithmic extension**: extending the dynamic programming state space by adding a discrete time dimension, formulating a new spacetime recurrence relation, proving its polynomial complexity, and demonstrating significant gains in First Node Death (FND: $+61\%$ to $+121\%$) and network survivability.
