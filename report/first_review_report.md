# Project Review 1 Report Summary
## Adaptive Routing in Energy-Harvesting Wireless Sensor Networks

**Course:** Data Structures & Algorithms (2nd Year B.Tech Capstone — Review 1)  
**Institution:** Vellore Institute of Technology (VIT), Vellore  
**Academic Year:** 2026–2027  
**Repository:** [https://github.com/santhoshvellore7119-web/WSN_proj](https://github.com/santhoshvellore7119-web/WSN_proj) (Branch: `master`)  
**Date:** October 2026  

---

### Team Members
- **Ananthakrishnan R** (Reg. No: **25BEL0005**) — B.Tech ECE (BEL)
- **Santhosh.G** (Reg. No: **25BEL0016**) — B.Tech ECE (BEL)
- **Thilang TV** (Reg. No: **25BEL0036**) — B.Tech ECE (BEL)

---

## 1. Project Summary & Key Ideas

In outdoor wireless sensor networks (like precision agriculture or forest monitoring), sensor nodes traditionally run on primary batteries that only deplete over time. Standard algorithms like Dijkstra's shortest path assume that any node with a low battery is about to die and avoid routing through it.

In solar energy-harvesting networks, **battery energy is non-monotonic**:
1. **The False Rejection Problem:** A node with 5% battery at $t=0$ might recharge back to 40% while a multi-hop packet travels toward it. Dijkstra rejects it anyway, forcing packets onto longer, wasteful routes.
2. **The Shaded Burnout Problem:** A node sitting in permanent tree shade starts with 80% battery but gets zero solar recharge. Dijkstra routes through it repeatedly until it burns out and severs network communication.
3. **Mid-Round Relay Brownouts:** Sudden cloud cover or transmission spikes cause nodes to brown out mid-round. Recomputing the full network routing table is too slow, and dropping the packet wastes already-spent energy.

---

## 2. What We Implemented (DSA Core)

1. **3D Time-Augmented Dynamic Programming ($dp[v][h][t]$):**
   - Recurrence: $dp[v][h][t] = \max_{u} \min(dp[u][h-1][t-\delta], E_{\text{proj}}(v, t) - E_{\text{rx}})$
   - Looks ahead across time slots to utilize recharging relays just-in-time.
   - Computes in $O(|E|HT)$ time (5.1 ms on 50 nodes) and uses $< 45\text{ KB}$ RAM.
2. **Disjoint-Set Union (DSU / Union-Find) Live Detour Recovery:**
   - Path compression and union-by-rank.
   - Slices local detours around mid-round failed nodes in $O(\text{deg}(u)\alpha(V))$ time.
   - **$4\times - 6\times$ faster** than full table recomputation (0.9 ms vs 5.1 ms) with **0% packet loss**.
3. **Harvesting-Aware Dynamic Clustering (EH-LEACH):**
   - Cluster head election probability scaled by solar intake and residual battery.
   - Min-heap priority queue tiebreaking.
4. **Full-Stack Engineering Platform:**
   - Modular simulation engine in Python (`src/`).
   - Asynchronous FastAPI backend (`backend/`) with SQLite job persistence.
   - React 19 web dashboard (`frontend/`) with live SVG network topology, round scrubber, and energy heatmaps.
   - 68 automated unit tests passing with pytest (100% pass rate in 4.7s).

---

## 3. Team Member Contributions

| Student Name | Register No. | Individual Responsibilities |
| :--- | :---: | :--- |
| **Ananthakrishnan R** | **25BEL0005** | Heinzelman radio model ($E_{\text{tx}}, E_{\text{rx}}, d_0$), solar harvesting profiles, literature survey, and multi-seed statistical evaluation ($N=30$ seeds). |
| **Santhosh.G** | **25BEL0016** | 3D Time-Augmented DP formulation, mathematical approximation derivation, 24-bin histogram belief filter, and core simulation engine. |
| **Thilang TV** | **25BEL0036** | Disjoint-Set Union (DSU) live detour recovery algorithm, FastAPI REST backend, SQLite database persistence, and React 19 dashboard. |

---

*For the complete detailed report with mathematical formulations, hardware physics, and benchmark tables, refer to [`project_review_1_report.md`](project_review_1_report.md) and [`project_review_1_report.pdf`](project_review_1_report.pdf).*
