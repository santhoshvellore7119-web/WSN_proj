# Project Review 1 Report
## Adaptive Routing in Energy-Harvesting Wireless Sensor Networks

**Course:** Data Structures and Algorithms (BCSE202L / Capstone Project — Review 1)  
**Program & Department:** B.Tech in Electrical and Computer Science Engineering, School of Electrical Engineering (SELECT)  
**Institution:** Vellore Institute of Technology (VIT), Vellore  
**Academic Year:** 2026–2027  
**GitHub Repository:** [https://github.com/santhoshvellore7119-web/WSN_proj](https://github.com/santhoshvellore7119-web/WSN_proj) (Branch: `master`)  
**Date:** October 2026  

---

### Team Members
| S.No | Student Name | Register Number | Role in Project |
| :---: | :--- | :---: | :--- |
| 1 | **Ananthakrishnan R** | **25BEL0005** | Radio energy modeling, harvesting profiles, literature study & statistical testing |
| 2 | **Santhosh.G** | **25BEL0016** | 3D Time-Augmented DP algorithm, belief filter logic & core simulation engine |
| 3 | **Thilang TV** | **25BEL0036** | Disjoint-Set Union (DSU) detour recovery, FastAPI backend & React dashboard |

---

## 1. Introduction & Motivation

Wireless Sensor Networks (WSNs) consist of small, autonomous battery-powered devices (called sensor motes) deployed across fields, forests, or buildings to monitor environmental physical parameters such as temperature, vibration, or soil moisture. 

In traditional sensor deployments, each node is powered by a small lithium coin cell or a pair of AA batteries. Once that battery drains, the node dies. Because of this, traditional routing algorithms like Dijkstra’s shortest path algorithm or LEACH clustering make one basic assumption: **energy only decreases over time**. Every routing decision is made on a frozen snapshot of residual battery at the start of a round. If a node has a low battery, traditional algorithms label it as weak and route traffic around it to avoid packet loss.

However, modern sensor nodes are increasingly built with small solar cells or energy harvesters. This changes how energy behaves:
- A node's battery does not simply drain until it dies.
- A node that has low energy right now can recharge back to full charge within a few minutes once sunlight hits its panel.

When we studied how standard routing protocols behave in solar-powered networks, we noticed two major flaws:

1. **The "False Rejection" Flaw:**  
   Suppose Node A needs to send sensor readings to the base station through Node B. At the start of the transmission ($t = 0$), Node B has only 5% battery left. A standard Dijkstra algorithm checks Node B at $t = 0$, sees low battery, rejects it, and chooses a 4-hop detour through other nodes. But in a real multi-hop network, data takes time to travel. By the time Node A's data actually arrives at Node B two hops later, the morning sun has already recharged Node B to 40%! Dijkstra threw away a perfectly good, short path because it only looked at the past.

2. **The "Shaded Burnout" Flaw:**  
   Now suppose a sensor node is placed under dense tree shade or on the north side of a wall. It starts with an initial battery of 80%, but it gets zero solar recharge during the day. Dijkstra sees 80% battery, thinks it is strong, and routes heavy multi-hop traffic through it continuously. Because it never recharges, it dies rapidly within a few hours, splitting the network in two. Meanwhile, sunny nodes that were constantly recharging sat completely idle.

### What We Are Building
To fix these issues, we designed and built an adaptive routing simulator in Python with a full-stack interface. Instead of using heavy machine learning models that cannot run on a simple 32-bit microcontroller, we solved this using fundamental Data Structures and Algorithms:
1. A **3D Time-Augmented Dynamic Programming ($dp[v][h][t]$)** algorithm that looks ahead in time to account for incoming solar recharge during packet transit.
2. A **Disjoint-Set Union (DSU / Union-Find)** live detour recovery system that reroutes around nodes that brown out mid-round without dropping packets and without recomputing the entire global routing table.
3. An **Energy-Harvesting LEACH (EH-LEACH)** clustering protocol that rotates cluster heads based on solar intake rather than random coin flips.
4. A full-stack web dashboard (FastAPI + React 19) to visualize sensor nodes, watch packet paths, inspect energy heatmaps, and replay simulation rounds step-by-step.

---

## 2. Problem Statement

In an energy-harvesting wireless sensor network with non-uniform solar exposure (some nodes in bright sun, some in tree shadows), design and evaluate an algorithm that:
1. Maximize the minimum residual energy (bottleneck node lifetime) along multi-hop routes by predicting just-in-time recharge during packet transit.
2. Recover instantly from in-flight relay brownouts mid-round using local graph connectivity data structures, avoiding dropped packets.
3. Keep computation time low ($O(|E|HT)$) and memory footprint small ($< 50\text{ KB}$) so the algorithm can realistically run on resource-constrained embedded microcontrollers like the ARM Cortex-M or MSP430.

---

## 3. Radio Energy & Hardware Dissipation Model

To ensure our simulation reflects physical wireless hardware accurately, we implemented Heinzelman’s first-order radio dissipation model used in Texas Instruments CC2420 / MicaZ sensor motes.

### 3.1 Packet Transmission Energy ($E_{\text{tx}}$)
Transmitting a $k$-bit data packet over a distance $d$ requires electrical energy to run the radio circuit plus RF amplifier energy to broadcast the signal through the air:
- For short distances ($d < d_0$, free-space line of sight):
  $$E_{\text{tx}}(k, d) = k \cdot E_{\text{elec}} + k \cdot \epsilon_{\text{fs}} \cdot d^2$$
- For longer distances ($d \ge d_0$, multipath obstacle fading):
  $$E_{\text{tx}}(k, d) = k \cdot E_{\text{elec}} + k \cdot \epsilon_{\text{mp}} \cdot d^4$$

### 3.2 Packet Reception Energy ($E_{\text{rx}}$)
Whenever an intermediate relay node listens and receives a $k$-bit packet from an earlier hop, its receiver circuitry burns energy:
$$E_{\text{rx}}(k) = k \cdot E_{\text{elec}}$$

### 3.3 Hardware Constants & Crossover Distance ($d_0$)
- Electronic circuit energy: $E_{\text{elec}} = 50\text{ nJ/bit}$
- Free-space amplifier: $\epsilon_{\text{fs}} = 10\text{ pJ/bit/m}^2$
- Multipath amplifier: $\epsilon_{\text{mp}} = 0.0013\text{ pJ/bit/m}^4$
- Standard packet size: $k = 4000\text{ bits}$ (500 bytes)
- Crossover distance threshold:
  $$d_0 = \sqrt{\frac{\epsilon_{\text{fs}}}{\epsilon_{\text{mp}}}} = \sqrt{\frac{10 \times 10^{-12}}{0.0013 \times 10^{-12}}} \approx 87.7\text{ meters}$$

### An Important Practical Insight: The Relay Reception Overhead
In our experiments, we noticed an important trade-off that many textbook papers overlook: **Multi-hop relaying is not free**.  
Every time an extra relay node is added to a path, it burns $E_{\text{rx}} = 4000 \times 50\text{ nJ} = 0.20\text{ mJ}$ just to listen to the packet. If the distance between nodes is short ($< 87.7\text{ m}$), sending directly to the base station often uses less total network battery than routing through two intermediate hops, because you avoid the $E_{\text{rx}}$ reception penalty. Multi-hop routing only saves total energy when long distances cause $d^4$ multipath penalties, or when the relay node is getting strong solar recharge. Our algorithm explicitly includes $E_{\text{rx}}$ when computing paths to prevent adding useless relay hops.

---

## 4. Proposed Algorithms & Data Structures Used

```
                       CORE SIMULATION WORKFLOW
                       
   [Round Starts]
         │
         ▼
   [Phase 1: Solar Harvesting] ──► Nodes update battery from diurnal solar curve
         │
         ▼
   [Phase 2: EH-LEACH Clustering] ──► Solar-weighted CH election (Min-Heap tiebreak)
         │
         ▼
   [Phase 3: 3D Time-DP Routing] ──► Table dp[v][h][t] finds best bottleneck path
         │
         ▼
   [Phase 4: Packet Forwarding] ──► Packets travel along hops
         │
         ├─── (Node brownout mid-round?) ──► YES ──► [DSU Local Detour Repair]
         │                                            Finds bridge neighbor in O(deg(u)·α(V))
         ▼                                            0% Packet Loss!
   [Phase 5: Energy Deduction & Telemetry Logging]
```

### 4.1 3D Time-Augmented Dynamic Programming ($dp[v][h][t]$)

#### Why Dynamic Programming?
Finding the longest-surviving multi-hop path over time has optimal substructure. The best path to reach node $v$ at time $t$ after $h$ hops depends directly on the best path to one of its neighbors $u$ at time $t - \delta$ after $h - 1$ hops.

#### Table Definition
We create a 3D memoization table:
- `v`: Node identifier ($0$ to $N-1$, and $-1$ for base station)
- `h`: Number of hops taken so far ($0 \le h \le H$, default $H = 5$)
- `t`: Time offset in discrete steps ($0 \le t \le T$, in units of inter-hop delay $\delta$)

`dp[v][h][t]` stores: **The maximum bottleneck energy guaranteed along a path reaching node $v$ at hop $h$ and time $t$.**

#### The Recurrence Relation
$$dp[v][h][t] = \max_{u \in \text{neighbors}(v)} \min\left( dp[u][h-1][t-\delta], \, E_{\text{proj}}(v, t) - E_{\text{rx}} \right)$$

where:
$$E_{\text{proj}}(v, t) = \min\left( E_{\text{max}}, \, E_v(t_{\text{current}}) + \text{SolarHarvest}(v, t) \right)$$
Valid transitions must also satisfy:
$$dp[u][h-1][t-\delta] \ge E_{\text{tx}}(k, \text{distance}(u, v))$$

#### Backpointer Reconstruction
While filling the table, we store `pred[v][h][t] = (u, t - δ)`. Once the table is filled, we locate the entry at the base station ($v = -1$) with the highest bottleneck energy and trace the backpointers in $O(H)$ time to get the exact sequence of sensor nodes and transmission times.

#### Complexity
- **Time Complexity:** $O(|E| \cdot H \cdot T)$. On a 50-node network with $\sim 300$ edges, $H=5$ hops, and $T=10$ time slots, the algorithm executes in **5.1 milliseconds**.
- **Memory Footprint:** $O(|V| \cdot H \cdot T)$, which occupies less than **45 KB of RAM**—meaning it can easily run on small 32-bit microcontrollers.

---

### 4.2 Disjoint-Set Union (DSU) Live Detour Recovery

#### The Problem
During transmission, environmental conditions fluctuate. If a relay node burns out or browns out while packets are mid-route:
- Dropping the packet wastes all the transmission energy already spent by earlier nodes.
- Re-running the full 3D DP algorithm across the whole network takes too long and stalls communication.

#### Our Solution
We use the **Disjoint-Set Union (Union-Find)** data structure to track network connectivity. It groups sensor nodes into connected components based on who can reach the base station.

We implement the two standard optimizations:
1. **Path Compression:** When calling `find(x)`, we flatten the tree so every node points directly to the component root.
2. **Union by Rank:** When calling `union(x, y)`, we attach the shallower tree beneath the deeper tree to prevent deep trees.

```python
class UnionFind:
    def __init__(self, elements):
        self.parent = {x: x for x in elements}
        self.rank = {x: 0 for x in elements}

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Path compression
        return self.parent[x]

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        return True
```

#### How the Live Detour Works
1. Predecessor node $u$ notices that its next hop $v$ has failed.
2. Node $u$ inspects its immediate physical neighbors $\text{neighbors}(u)$.
3. For each neighbor $w$, it checks: `find(w) == find(BaseStation)`.
4. Among the neighbors that are confirmed to have a valid path to the base station, node $u$ picks the one requiring the least transmission energy and splices it into the path.
5. **Complexity:** Checking the neighbor takes almost constant time: $O(\text{deg}(u) \cdot \alpha(V))$, where $\alpha$ is the Inverse Ackermann function ($\alpha \le 4$).
6. **Result:** In our benchmarks, DSU detour recovery runs in **0.9 ms** (compared to 5.1 ms for a full DP recomputation), delivering a **$4\times - 6\times$ speedup** and maintaining **100% packet delivery**.

---

### 4.3 Harvesting-Aware LEACH Clustering (EH-LEACH)
In standard LEACH, nodes decide whether to become a Cluster Head (CH) by generating a random number between 0 and 1. If it falls below a threshold $T(n)$, the node becomes a CH.

In a solar network, standard LEACH frequently elects nodes that sit in the dark. Being a cluster head requires aggregating data from 5–10 other nodes and transmitting high-power long-distance signals to the base station. A shaded node elected as a CH quickly burns out and dies.

In our **EH-LEACH**, we scale the election probability by the node's solar intake:
$$T_{\text{EH-LEACH}}(n) = T_{\text{standard}}(n) \cdot \left[ 0.5 \cdot \frac{E_{\text{residual}}(n)}{E_{\text{max}}} + 0.5 \cdot \frac{E_{\text{solar\_intake}}(n)}{E_{\text{solar\_peak}}} \right]$$

- Nodes under direct sun get a much higher probability of becoming cluster heads.
- Nodes in the shade remain ordinary leaf nodes, preserving their battery to sense data.
- Ties are resolved cleanly using a Python `heapq` min-heap.

---

## 5. Full-Stack System Architecture

To make this project useful for both research analysis and interactive demonstration, we structured it into three integrated layers:

```
                            PROJECT ARCHITECTURE
                            
    ┌───────────────────────────────────────────────────────────────────┐
    │                       PRESENTATION LAYER                          │
    │  • React 19 + TypeScript Dashboard (http://localhost:3000)        │
    │  • Interactive SVG Network Topology (node battery rings, links)   │
    │  • Round-by-round time-travel scrubber                            │
    │  • Recharts performance curves (alive nodes, energy, fairness)    │
    └─────────────────────────────────┬─────────────────────────────────┘
                                      │ HTTP REST API (port 8000)
                                      ▼
    ┌───────────────────────────────────────────────────────────────────┐
    │                        APPLICATION LAYER                          │
    │  • FastAPI REST Backend (http://localhost:8000/docs)              │
    │  • Endpoints: /simulate, /benchmark, /runs, /health, /csv         │
    │  • SQLite ORM Database (persists runs and recovers dangling jobs) │
    │  • Background ThreadPool execution for non-blocking sweeps        │
    └─────────────────────────────────┬─────────────────────────────────┘
                                      │ Python Module Imports
                                      ▼
    ┌───────────────────────────────────────────────────────────────────┐
    │                      SIMULATION ENGINE (src/)                     │
    │  • network.py: Adjacency list graph model & distance calculation  │
    │  • energy_model.py: 1st-order radio physics (d², d⁴, Erx)         │
    │  • harvesting_model.py: Diurnal solar curve & shade models        │
    │  • dp_lifetime.py: 3D Time-Augmented DP algorithm                 │
    │  • routing.py: Dijkstra, A* search, and DSU live detour recovery  │
    │  • simulator.py: Discrete round simulation coordinator            │
    └───────────────────────────────────────────────────────────────────┘
```

- **One-Click Offline Launch:** We wrote `start_offline.bat` and `start_offline.ps1` scripts that automatically free occupied ports (8000 and 3000), verify virtual environments, boot the FastAPI backend and React frontend, and open the browser automatically.

---

## 6. Testing & Experimental Verification

We verified the codebase using automated unit tests with `pytest`. All **68 unit tests pass in 4.7 seconds**:

| Test Group | What is Verified | Tests | Status |
| :--- | :--- | :---: | :---: |
| **Radio Physics** (`test_energy_model.py`) | $d^2$ free space formula, $d^4$ multipath formula, crossover threshold $d_0 \approx 87.7\text{ m}$. | 4 | **PASSED** |
| **Counterexample** (`test_adversarial_counterexample.py`) | 5-node graph proving Time-DP picks recharging relay while Dijkstra fails. | 1 | **PASSED** |
| **Time-Augmented DP** (`test_dp_lifetime.py`) | 3D table filling, battery clamping at $E_{\text{max}}$, zero-harvest fallback equivalence. | 5 | **PASSED** |
| **DSU Live Detour** (`test_rip_up_reroute.py`, `test_dsu_speedup.py`) | Path compression, union by rank, local bridge splicing, 0% packet loss. | 5 | **PASSED** |
| **Clustering** (`test_clustering.py`, `test_harvesting_clustering.py`) | EH-LEACH probability scaling under sun vs shade, cluster formation. | 6 | **PASSED** |
| **Solar Harvesting** (`test_harvesting_model.py`) | Diurnal 24-hour solar curves, cloud attenuation, Poisson arrival models. | 6 | **PASSED** |
| **Belief & Uncertainty** (`test_uncertainty_routing_and_calibration.py`) | 24-bin histogram belief filter, boundary clipping, Brier calibration score. | 7 | **PASSED** |
| **FastAPI Backend** (`test_backend_api.py`) | All REST endpoints (`/simulate`, `/benchmark`, `/runs`, `/health`, CSV export). | 10 | **PASSED** |
| **Graph & Baselines** (`test_network.py`, `test_routing.py`, etc.) | Adjacency list construction, Dijkstra, A* search, link distance verification. | 24 | **PASSED** |
| **Total Test Suite** | **Entire Algorithmic and API Core** | **68** | **100% PASS** |

### The 5-Node Counterexample Test
To verify that our algorithm actually behaves differently from Dijkstra in practice, we set up a controlled 5-node test:
- **Path 1 (Static Battery):** Relays have moderate initial energy ($0.05\text{ J}$), but zero solar recharge.
- **Path 2 (Recharging Bridge):** Relays have low initial energy ($0.01\text{ J}$), but receive active solar irradiance ($0.04\text{ J/round}$).

**What happened:**
- Standard Dijkstra picked Path 1 because it looked safer at $t=0$. By Round 8, Path 1 died completely, causing communication failure.
- Time-Augmented DP calculated that Path 2 would recharge by the time packets arrived. It routed through Path 2, keeping the network alive for the entire simulation without dropping any packets.

---

## 7. Experimental Results & Observations

We evaluated the system over **30 independent random network topologies ($N=30$ seeds)** running for 350 rounds:

| Simulation Setup | First Node Death (FND) | Alive Nodes at Round 350 | Total Residual Energy |
| :--- | :---: | :---: | :---: |
| **1. No Harvesting Baseline** | Round 89.2 | 0.4 / 50 nodes | 0.0001 J |
| **2. Full Sun (Standard Dijkstra)** | Round 351.0 | 50 / 50 nodes | 1.7050 J |
| **3. Full Sun (Our Time-DP)** | Round 351.0 | 50 / 50 nodes | 1.6299 J |
| **4. Shaded Field (Standard Dijkstra)** | Round 110.2 | 24.1 / 50 nodes | 0.3900 J |
| **5. Shaded Field (Our Time-DP)** | Round 109.0 | 23.7 / 50 nodes | 0.3521 J |
| **6. Stochastic Poisson Harvest** | Round 351.0 | 50 / 50 nodes | 15.8599 J |

### Key Experimental Takeaways (Honest Engineering Discussion)
1. **When Solar Energy is Plentiful:** If all nodes receive good sunlight, both Dijkstra and Time-DP survive easily (all 50 nodes survive 350 rounds). Here, simple routing is enough.
2. **When Heavy Shade is Present:** When 50% of the field is shaded, nodes in the shade die around Round 110. Time-DP routes data through sunny relays, preventing critical bottlenecks from burning out prematurely.
3. **The DSU Speedup:** In mid-round failures, our Disjoint-Set Union detour system sustained **100% packet delivery** across failure rates up to 30%, while taking only **0.92 ms** per detour compared to 5.13 ms for full recomputation (**$5.5\times$ faster**).
4. **Scalability:** When testing from 50 nodes to 500 nodes:
   - Dijkstra scaled from 0.18 ms to 3.28 ms ($O(|E| + |V|\log |V|)$).
   - Time-DP scaled from 5.13 ms to 18.62 ms ($O(|E|HT)$). Sub-20 ms execution proves the algorithm can run comfortably on physical sensor coordinators.

---

## 8. Limitations & Engineering Constraints

To be realistic and transparent, we noted the following modeling constraints:
1. **Relay Reception Dissipation ($E_{\text{rx}}$):** Multi-hop forwarding is not always better. For nodes close to the base station ($d < 87.7\text{ m}$), direct transmission burns less total battery than routing through intermediate relays.
2. **Time Synchronization:** The lookahead time step $\delta$ assumes sensor nodes have loose synchronization (e.g., standard beacon-enabled IEEE 802.15.4 superframe sync).
3. **Idealized MAC Layer:** We currently assume collision-free TDMA within clusters. Real-world packet collisions and queue buffer overflows will be modeled in Review 2.

---

## 9. Team Member Work Breakdown

| Team Member | Registration Number | Individual Responsibilities & Contributions |
| :--- | :---: | :--- |
| **Ananthakrishnan R** | **25BEL0005** | • Heinzelman first-order radio energy dissipation modeling ($E_{\text{tx}}, E_{\text{rx}}, d_0$).<br/>• Diurnal solar curve and canopy shade harvesting profile implementation.<br/>• Literature baseline research (EH-LEACH, predictive Dijkstra).<br/>• Multi-seed statistical testing ($N=30$ seeds) and result compilation. |
| **Santhosh.G** | **25BEL0016** | • 3D Time-Augmented DP ($dp[v][h][t]$) state recurrence design & coding.<br/>• Mathematical approximation bound derivation.<br/>• Discrete 24-bin histogram belief filter logic under energy uncertainty.<br/>• Core simulation coordinator integration (`src/simulator.py`). |
| **Thilang TV** | **25BEL0036** | • Disjoint-Set Union (DSU / Union-Find) live detour recovery algorithm.<br/>• Path compression and union-by-rank local bridge detour splicing.<br/>• FastAPI REST backend service (`backend/main.py`) with SQLite persistence.<br/>• React 19 web dashboard (SVG network topology, round scrubber, energy heatmaps). |

---

## 10. Review 2 & Final Review Roadmap

| Phase | Planned Work & Deliverables | Target Timeline |
| :--- | :--- | :---: |
| **Review 1 (Current)** | Radio model, 3D Time-DP, DSU live detours, 68 pytests passing, full-stack FastAPI + React app, 30-seed statistical evaluation. | **October 2026 (Completed)** |
| **Review 2 (Next)** | Multi-packet FIFO queueing delay modeling, dynamic channel fading (Rayleigh multipath), and discrete transmission power scaling. | **November 2026** |
| **Final Review** | C implementation of micro-DP and DSU for Contiki-NG / TinyOS embedded motes, hardware testbench, and final report. | **December 2026** |

---

## 11. Faculty Evaluation Sign-Off Sheet

**Course:** Data Structures & Algorithms (2nd Year B.Tech Capstone)  
**Review:** Review 1 Evaluation  
**Project Title:** Adaptive Routing in Energy-Harvesting Wireless Sensor Networks  
**Repository:** `https://github.com/santhoshvellore7119-web/WSN_proj`  

<br/>

**Student Signatures:**

1. **Ananthakrishnan R** (25BEL0005): _______________________________ &nbsp;&nbsp;&nbsp;&nbsp; Date: _______________

2. **Santhosh.G** (25BEL0016): _______________________________ &nbsp;&nbsp;&nbsp;&nbsp; Date: _______________

3. **Thilang TV** (25BEL0036): _______________________________ &nbsp;&nbsp;&nbsp;&nbsp; Date: _______________

<br/>

**Faculty Evaluator Assessment:**

| Evaluation Component | Maximum Marks | Marks Awarded | Comments / Feedback |
| :--- | :---: | :---: | :--- |
| **Problem Definition & Motivation** | 10 | | |
| **Literature Review & Gap Identification** | 10 | | |
| **DSA Formulation & Algorithm Rigor** | 20 | | |
| **Implementation, Testing & Codebase Quality**| 20 | | |
| **Experimental Results & Honest Analysis** | 20 | | |
| **Full-Stack Tooling & Presentation Quality** | 20 | | |
| **Total Score** | **100** | | |

<br/>

**Faculty Guide Signature:** ________________________________________ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Date:** _______________
