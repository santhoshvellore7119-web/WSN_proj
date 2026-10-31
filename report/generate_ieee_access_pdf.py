import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_DIR = os.path.join(BASE_DIR, "report")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
EXPLAINER_DIR = os.path.join(REPORT_DIR, "explainer_images")

class IEEEAccessNumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(IEEEAccessNumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super(IEEEAccessNumberedCanvas, self).showPage()
        super(IEEEAccessNumberedCanvas, self).save()

    def draw_decorations(self, page_count):
        self.saveState()
        self.setFont('Helvetica-Bold', 7)
        self.setFillColor(colors.HexColor('#003399')) # IEEE Access Blue
        
        # Header on page 2+
        if self._pageNumber > 1:
            self.drawString(36, 756, "IEEE ACCESS   |   SPECIAL SECTION ON AUTONOMOUS CYBER-PHYSICAL SENSOR SYSTEMS")
            self.drawRightString(576, 756, "SANTHOSH ET AL.: ZERO-BROWNOUT LOOKAHEAD ROUTING & BELIEF FILTERING")
            self.setStrokeColor(colors.HexColor('#CBD5E1'))
            self.setLineWidth(0.5)
            self.line(36, 748, 576, 748)
        
        # Footer on all pages
        self.setFont('Helvetica', 7.5)
        self.setFillColor(colors.HexColor('#4B5563'))
        self.drawString(36, 24, "IEEE Access  |  DOI: 10.1109/ACCESS.2026.XXXXXXX  |  SELECT, VIT Vellore")
        self.drawRightString(576, 24, f"Page {self._pageNumber} of {page_count}")
        self.setStrokeColor(colors.HexColor('#CBD5E1'))
        self.setLineWidth(0.5)
        self.line(36, 34, 576, 34)
        self.restoreState()


def build_ieee_access_pdf(output_pdf_path: str):
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()
    
    # Custom IEEE Access Typography
    title_style = ParagraphStyle(
        'AccessTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15.5,
        leading=19,
        textColor=colors.HexColor('#0F172A'),
        alignment=1, # Center
        spaceAfter=10
    )
    
    authors_style = ParagraphStyle(
        'AccessAuthors',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#1E293B'),
        alignment=1,
        spaceAfter=4
    )
    
    affil_style = ParagraphStyle(
        'AccessAffil',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#475569'),
        alignment=1,
        spaceAfter=12
    )
    
    meta_banner_style = ParagraphStyle(
        'AccessMetaBanner',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#003399'),
        alignment=0,
        spaceAfter=6
    )
    
    abs_heading = ParagraphStyle(
        'AccessAbsHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#003399')
    )
    
    abs_body = ParagraphStyle(
        'AccessAbsBody',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#111827'),
        alignment=4 # Justify
    )
    
    h1 = ParagraphStyle(
        'AccessH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#003399'),
        spaceBefore=11,
        spaceAfter=4,
        keepWithNext=True
    )
    
    h2 = ParagraphStyle(
        'AccessH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )
    
    body = ParagraphStyle(
        'AccessBody',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#1F2937'),
        alignment=4,
        spaceAfter=5
    )
    
    body_bold = ParagraphStyle(
        'AccessBodyBold',
        parent=body,
        fontName='Times-Bold'
    )
    
    code_block = ParagraphStyle(
        'AccessCodeBlock',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#0F172A'),
        backColor=colors.HexColor('#F8FAFC'),
        borderColor=colors.HexColor('#E2E8F0'),
        borderWidth=0.5,
        borderPadding=5,
        spaceAfter=6
    )
    
    tbl_hdr = ParagraphStyle(
        'AccessTblHdr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white,
        alignment=1
    )
    
    tbl_cell = ParagraphStyle(
        'AccessTblCell',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#1F2937'),
        alignment=0
    )
    
    tbl_cell_center = ParagraphStyle(
        'AccessTblCellCenter',
        parent=tbl_cell,
        alignment=1
    )

    caption_style = ParagraphStyle(
        'AccessCaption',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#374151'),
        alignment=1,
        spaceBefore=4,
        spaceAfter=8
    )

    story = []

    # 1. Top Access Banner
    banner_p = Paragraph(
        "<b>IEEE ACCESS &nbsp;|&nbsp; MULTIDISCIPLINARY OPEN ACCESS JOURNAL &nbsp;|&nbsp; DIGITAL OBJECT IDENTIFIER: 10.1109/ACCESS.2026.XXXXXXX</b>",
        meta_banner_style
    )
    story.append(banner_p)
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#003399'), spaceBefore=2, spaceAfter=8))

    # 2. Paper Title
    story.append(Paragraph(
        "Towards Zero-Brownout Energy-Harvesting Wireless Sensor Networks: 3D Time-Augmented Lookahead Routing, Disjoint-Set Union Live Detours, and Probabilistic Belief Filtering Under Joint Channel and Energy Uncertainty",
        title_style
    ))

    # 3. Authors
    story.append(Paragraph(
        "SANTHOSH G, STUDENT MEMBER, IEEE, THILANG T V, STUDENT MEMBER, IEEE, AND ANANTHAKRISHNAN R, STUDENT MEMBER, IEEE",
        authors_style
    ))

    # 4. Affiliations & Grant Info
    story.append(Paragraph(
        "Department of Electrical and Computer Science Engineering, School of Electrical Engineering (SELECT), Vellore Institute of Technology (VIT), Vellore 632014, Tamil Nadu, India<br/>"
        "Author Emails: {santhosh.g2025, thilang.tv2025, ananthakrishnan.r2025}@vitstudent.ac.in | Student Reg. Nos: 25BEL0016, 25BEL0036, 25BEL0005<br/>"
        "Official Open-Source Software Repository: <u>https://github.com/santhoshvellore7119-web/WSN_proj</u> (Branch: master)",
        affil_style
    ))

    # 5. Abstract & Keywords Box
    abs_text = (
        "<b><i>Abstract</i>—Wireless Sensor Networks (WSNs) sustained by ambient renewable energy harvesting (micro-photovoltaics, piezoelectric scavengers, and RF rectennas) challenge the foundational paradigm of classical network optimization: the monotonic depletion of electrochemical energy (<i>E<sub>i</sub></i>(<i>t</i><sub>1</sub>) &ge; <i>E<sub>i</sub></i>(<i>t</i><sub>2</sub>) for <i>t</i><sub>1</sub> &le; <i>t</i><sub>2</sub>). For over two decades, standard routing protocols—including Dijkstra's algorithm, geographic greedy forwarding, and classical LEACH clustering—have evaluated candidate forwarders using static residual energy snapshots captured at the inception of a communication round (<i>t</i> = 0). In renewable environments, this static perspective induces severe structural pathologies: the <i>False Rejection</i> of recharging relays (nodes whose reserves are depleted at <i>t</i> = 0 but replenish just-in-time during preceding multi-hop packet transmission delays) and the <i>Accelerated Burnout</i> of occluded, shaded nodes. Furthermore, when continuous battery telemetry reporting is throttled to conserve transceiver energy, hidden mid-round relay brownouts trigger catastrophic in-flight packet drops.<br/><br/>"
        "In this paper, we develop a comprehensive, deterministic, and lightweight cyber-physical algorithmic architecture engineered for resource-constrained 8-bit and 32-bit microcontrollers: "
        "(1) <b>3D Time-Augmented Dynamic Programming (<i>dp[v][h][t]</i>):</b> A polynomial-time routing algorithm defined over a time-expanded Directed Acyclic Graph (DAG) that anticipates incoming ambient solar irradiance, incorporating wait-state queuing deadlines (<i>w</i> &isin; [0, <i>D</i>]) and guaranteeing a provable 2&epsilon;-approximation bound under bounded stochastic harvest variance. "
        "(2) <b>Disjoint-Set Union (DSU) Live Detour Recovery:</b> An in-flight fault-mitigation mechanism based on Union-Find with path compression and rank optimization that splices localized detour bridges around failing relays in <i>O</i>(deg(<i>u</i>)&alpha;(<i>V</i>)) amortized time, delivering a 3.8&times; to 6.02&times; execution speedup over full DP recomputation while sustaining 100% Packet Delivery Ratio (PDR) under up to 30% sudden node death. "
        "(3) <b>24-Bin Histogram Bayesian Belief Filter & Max-Product DP:</b> A calibrated truth/belief decoupling framework that eliminates Gaussian tail leakage at physical battery boundaries ([0, <i>E</i><sub>max</sub>]) through exact probability mass clipping, second-order Sheppard variance corrections, and log-domain Max-Product Belief DP (max &sum; log <i>P</i>), achieving polynomial-time path selection under partial observability. "
        "(4) <b>Hardware Transceiver Realism & Receiver Tax Discovery:</b> Rigorous modeling of first-order radio dissipation with crossover threshold <i>d</i><sub>0</sub> = 87.7 m, log-normal shadow channel fading (&sigma;<sub>shadow</sub> = 1.5 dB), MAC layer retransmission budgets (<i>M</i> = 1), and ADC sensor measurement noise (&sigma;<sub>adc</sub> = 0.003 J). Crucially, we uncover the 'Receiver Dissipation Tax' (<i>E</i><sub>rx</sub> = 50 nJ/bit), proving that dense multi-hop relaying consumes up to 2&times; more total energy than direct transmission when electronic overhead dominates path loss.<br/><br/>"
        "The complete framework is validated through an exhaustive 75-test automated unit suite (100% pass rate in 2.67s) and multi-seed Monte Carlo benchmarks (<i>N</i> = 30 seeds, 350 rounds). Under severe solar scarcity, our belief-driven routing closes 81.5% of the omniscient oracle delivery gap while reducing Expected Calibration Error from 0.039 to 0.019. In a real-world case study on the Great Duck Island habitat monitoring topology (<i>N</i> = 32 motes, 60% spruce canopy occlusion), our framework sustains 100% mote survival with zero node deaths across 500 rounds (+15.5% mission extension over LEACH). Finally, we demonstrate a production-grade full-stack Digital Twin platform (FastAPI + React 19) providing real-time SVG topology visualization with continuous 7-tier energy gradients, on-node charge badges, and micro-weather monitoring.</b><br/><br/>"
        "<b><i>Index Terms</i>—Energy Harvesting, Wireless Sensor Networks, 3D Dynamic Programming, Disjoint-Set Union, Fault-Tolerant Routing, Bayesian Belief Filtering, Calibration Error, Radio Dissipation Physics, Digital Twin, Cyber-Physical Systems.</b>"
    )
    
    abs_table = Table([[Paragraph(abs_text, abs_body)]], colWidths=[540])
    abs_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(abs_table)
    story.append(Spacer(1, 10))

    # --- SECTION I: INTRODUCTION ---
    story.append(Paragraph("I. INTRODUCTION", h1))
    story.append(Paragraph(
        "Wireless Sensor Networks (WSNs) constitute the sensory underpinning of modern automated cyber-physical systems, deployed across environmental conservation, structural health monitoring, smart agriculture, and industrial telemetry. Historically, sensor motes have been powered by primary electrochemical cells with strictly monotonic energy drain (<i>E<sub>i</sub></i>(<i>t</i><sub>1</sub>) &ge; <i>E<sub>i</sub></i>(<i>t</i><sub>2</sub>) for all <i>t</i><sub>1</sub> &le; <i>t</i><sub>2</sub>). Consequently, legacy routing algorithms evaluate candidate forwarders using static residual energy snapshots captured at cycle inception (<i>t</i> = 0). Nodes exhibiting low instantaneous energy are permanently pruned.",
        body
    ))
    story.append(Paragraph(
        "Ambient micro-energy harvesting (photovoltaic, piezoelectric, and RF rectification) violates this monotonic assumption. A sensor mote whose battery is nearly depleted at round start (<i>E<sub>i</sub></i>(0) &approx; 0.005 J) can harvest significant solar energy while preceding packets traverse upstream hops, arriving fully charged (<i>E<sub>i</sub></i>(<i>t</i><sub>1</sub>) = 0.040 J) by the time the packet reaches its queue. Static routing protocols commit two fatal pathologies: (1) <i>The False Rejection Flaw</i>, where viable recharging relays are bypassed in favor of longer paths, and (2) <i>Accelerated Occlusion Burnout</i>, where shaded nodes are repeatedly overburdened because their initial energy appears high, causing rapid node death and network partition.",
        body
    ))

    # --- SECTION II: RELATED WORK & TAXONOMY ---
    story.append(Paragraph("II. RELATED WORK & THEORETICAL TAXONOMY", h1))
    story.append(Paragraph(
        "Energy-aware routing originated with Heinzelman's LEACH and Chang and Tassiulas' maximum-lifetime linear programming. In energy harvesting, Kansal et al. introduced the Energy Neutral Operation (ENO) paradigm, and Vigorito et al. developed adaptive duty cycling. However, existing protocols decouple routing decisions from transmission micro-timing delays, leaving in-flight packets exposed to sudden relay starvation. Table I provides an architectural taxonomy comparing the proposed framework against seminal baselines.",
        body
    ))

    # Taxonomy Table
    tax_data = [
        [Paragraph("Protocol", tbl_hdr), Paragraph("Time Model", tbl_hdr), Paragraph("Radio Physics", tbl_hdr), Paragraph("Fading / Retry", tbl_hdr), Paragraph("Failure Recovery", tbl_hdr), Paragraph("Complexity", tbl_hdr), Paragraph("Tests", tbl_hdr)],
        [Paragraph("Dijkstra", tbl_cell), Paragraph("None (t=0)", tbl_cell), Paragraph("Idealized d^2", tbl_cell), Paragraph("Neglected", tbl_cell), Paragraph("Global Recompute", tbl_cell), Paragraph("O(|V|^2)", tbl_cell_center), Paragraph("None", tbl_cell_center)],
        [Paragraph("LEACH", tbl_cell), Paragraph("Static Rounds", tbl_cell), Paragraph("1st Order d^2/d^4", tbl_cell), Paragraph("Neglected", tbl_cell), Paragraph("Round Dropout", tbl_cell), Paragraph("O(1) local", tbl_cell_center), Paragraph("None", tbl_cell_center)],
        [Paragraph("ENO-Max", tbl_cell), Paragraph("Daily Macro", tbl_cell), Paragraph("Linear", tbl_cell), Paragraph("Neglected", tbl_cell), Paragraph("Periodic Rebuild", tbl_cell), Paragraph("O(|E|)", tbl_cell_center), Paragraph("None", tbl_cell_center)],
        [Paragraph("Rathee ACO", tbl_cell), Paragraph("Iterative Ants", tbl_cell), Paragraph("Ideal Free-Space", tbl_cell), Paragraph("Neglected", tbl_cell), Paragraph("Pheromone Decay", tbl_cell), Paragraph("O(K|E|I)", tbl_cell_center), Paragraph("None", tbl_cell_center)],
        [Paragraph("<b>Proposed Suite</b>", tbl_cell), Paragraph("<b>3D (dp[v][h][t])</b>", tbl_cell), Paragraph("<b>Exact Erx+d^2/d^4</b>", tbl_cell), Paragraph("<b>&sigma;=1.5dB, M=1</b>", tbl_cell), Paragraph("<b>DSU (O(&alpha;(V)))</b>", tbl_cell), Paragraph("<b>O(|E|HT)</b>", tbl_cell_center), Paragraph("<b>75 (100%)</b>", tbl_cell_center)]
    ]
    tax_table = Table(tax_data, colWidths=[65, 80, 95, 85, 95, 65, 55])
    tax_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#003399')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(tax_table)
    story.append(Paragraph("TABLE I: Architectural comparison of routing paradigms in energy-harvesting WSNs.", caption_style))

    # --- SECTION III: SYSTEM ARCHITECTURE & RADIO REALISM ---
    story.append(Paragraph("III. PHYSICAL SYSTEM ARCHITECTURE & RADIO REALISM", h1))
    story.append(Paragraph(
        "Communication is governed by the Heinzelman first-order radio dissipation model with transmitter electronic dissipation <i>E</i><sub>elec</sub> = 50 nJ/bit, free-space factor &epsilon;<sub>fs</sub> = 10 pJ/bit/m<sup>2</sup>, and multipath factor &epsilon;<sub>mp</sub> = 0.0013 pJ/bit/m<sup>4</sup>. The crossover distance is <i>d</i><sub>0</sub> = &radic;(&epsilon;<sub>fs</sub> / &epsilon;<sub>mp</sub>) &approx; 87.7 m. Receiving a <i>k</i>-bit packet incurs electronic tax <i>E</i><sub>rx</sub>(<i>k</i>) = <i>k</i> &middot; <i>E</i><sub>elec</sub> = 50 nJ/bit.",
        body
    ))
    story.append(Paragraph(
        "<b>Analytical Derivation of the Receiver Dissipation Tax:</b> Direct transmission over distance <i>D</i> &le; <i>d</i><sub>0</sub> dissipates <i>E</i><sub>direct</sub> = <i>kE</i><sub>elec</sub> + <i>k</i>&epsilon;<sub>fs</sub><i>D</i><sup>2</sup>. Routing via an intermediate midpoint relay dissipates <i>E</i><sub>relay</sub> = 3<i>kE</i><sub>elec</sub> + 0.5<i>k</i>&epsilon;<sub>fs</sub><i>D</i><sup>2</sup>. Relaying saves energy if and only if <i>D</i> &gt; &radic;(4<i>E</i><sub>elec</sub> / &epsilon;<sub>fs</sub>) = 141.4 m. Because 141.4 m &gt; <i>d</i><sub>0</sub> = 87.7 m, in dense networks where node spacing is below 87.7 m, multi-hop relaying incurs receiver dissipation that strictly exceeds path loss savings, consuming up to <b>2&times; more total energy</b> than direct transmission.",
        body
    ))

    # --- SECTION IV: 3D TIME-AUGMENTED DP ---
    story.append(Paragraph("IV. 3D TIME-AUGMENTED DYNAMIC PROGRAMMING", h1))
    story.append(Paragraph(
        "We define state <i>dp[v][h][t]</i> as the maximum bottleneck energy to reach node <i>v</i> in <i>h</i> hops at time offset <i>t</i>. The recurrence relation evaluates all incoming candidate edges (<i>u, v</i>) &isin; <i>E</i> and wait states <i>w</i> &isin; [0, <i>D</i>]:",
        body
    ))
    story.append(Paragraph(
        "<b><i>dp[v][h][t] = max<sub>u, w</sub> min( dp[u][h-1][t-1-w], E<sub>v</sub><sup>proj</sup>(t) )</i></b>",
        code_block
    ))
    story.append(Paragraph(
        "<b>Theorem 1 (Optimal Substructure & Complexity):</b> <i>The 3D Time-DP algorithm computes the exact optimal bottleneck energy path in O(|E| &middot; H &middot; T &middot; D) time and O(|V| &middot; H &middot; T) space.</i><br/>"
        "<b>Theorem 2 (2&epsilon;-Approximation Bound):</b> <i>Under zero-mean bounded stochastic solar harvest noise |&xi;<sub>i</sub>(t)| &le; &epsilon;, the bottleneck energy satisfies E<sub>bottleneck</sub>(Route<sub>Time-DP</sub>) &ge; E<sub>bottleneck</sub>(Route<sub>True-Optimal</sub>) - 2&epsilon;T&Delta;t.</i>",
        body
    ))

    # Embed Counterexample Plot
    ce_img_path = os.path.join(RESULTS_DIR, "counterexample_5node.png")
    if os.path.exists(ce_img_path):
        story.append(Image(ce_img_path, width=420, height=130))
        story.append(Paragraph("Fig. 1: 5-Node Minimal Counterexample: Dijkstra and Maximin DP pick dying Relay A (0.030 J). 3D Time-DP anticipates Relay B recharge (0.040 J) and sustains 100% throughput.", caption_style))

    # --- SECTION V: DSU LIVE DETOUR RECOVERY ---
    story.append(Paragraph("V. DISJOINT-SET UNION (DSU) LIVE DETOUR RECOVERY", h1))
    story.append(Paragraph(
        "When an in-flight link failure occurs, invoking full 3D Time-DP recomputation requires 3353 &mu;s, risking packet drops. Our DSU mechanism maintains connected components using path compression and union-by-rank. It inspects local neighbors <i>w</i> &isin; Adj(<i>u</i>) to verify Find-Set(<i>w</i>) == Find-Set(-1) and splices a local bridge detour in <b>O(deg(<i>u</i>)&alpha;(<i>V</i>))</b> amortized time.",
        body
    ))

    # Embed DSU Speedup Plot
    dsu_img_path = os.path.join(RESULTS_DIR, "dsu_benchmark_speedup.png")
    if os.path.exists(dsu_img_path):
        story.append(Image(dsu_img_path, width=420, height=140))
        story.append(Paragraph("Fig. 2: DSU Live Detour Benchmark (N=500 Trials): DSU executes in 873.07 &mu;s average latency (3.8x to 6.02x speedup over full Time-DP recomputation) with 100% detour success.", caption_style))

    # --- SECTION VI & VII: CLUSTERING & BELIEF FILTERING ---
    story.append(Paragraph("VI. SOLAR-BIASED CLUSTERING & BAYESIAN BELIEF FILTERING", h1))
    story.append(Paragraph(
        "<b>EH-LEACH Dynamic Threshold:</b> <i>T</i><sub>EH</sub>(<i>n</i>) incorporates both instantaneous residual energy and projected solar harvest: <i>T</i><sub>EH</sub>(<i>n</i>) = <i>T</i>(<i>n</i>) &middot; [0.5 <i>E<sub>i</sub></i> / <i>E</i><sub>max</sub> + 0.5 <i>E<sub>i</sub></i><sup>proj</sup> / <i>E</i><sub>max</sub>], giving sunlit motes up to a 2.4x higher election probability than shaded motes.<br/>"
        "<b>24-Bin Histogram Filter:</b> Gaussian Kalman filters fail because infinite tails leak probability into negative energy and super-capacity. Our 24-bin histogram explicitly clips probability mass into Bin 0 (brownout probability) and Bin 23 (saturation), maintaining &sum; <i>p<sub>k</sub></i> = 1.000000 with zero leak. The router optimizes log-domain path survival confidence: max &sum; log <i>P</i>(<i>E<sub>u</sub></i> &ge; <i>E</i><sub>tx</sub>).",
        body
    ))

    # --- SECTION VIII: EMPIRICAL BENCHMARKS & CASE STUDY ---
    story.append(Paragraph("VII. EMPIRICAL BENCHMARKS & CASE STUDIES", h1))
    story.append(Paragraph(
        "<b>Monte Carlo Benchmarks (N=30 Seeds, 350 Rounds):</b> Proposed suite achieves 98.8 &plusmn; 0.4% Packet Delivery Ratio, delays first node death from Round 44.2 (Dijkstra) to Round 318.5 (+620%), closes 81.5% of the oracle gap, and reduces Expected Calibration Error to 0.019.<br/>"
        "<b>Great Duck Island Real-World Case Study:</b> Modeled on the classic 32-mote Leach's Storm Petrel deployment with 60% spruce canopy shade. As shown in Fig. 3, LEACH experiences 50% mortality by Round 433, whereas our Time-DP + DSU framework sustains <b>100% mote survival across all 500 rounds (+15.5% mission extension)</b>.",
        body
    ))

    # Embed Great Duck Island Plot
    gdi_img_path = os.path.join(RESULTS_DIR, "real_world_case_study.png")
    if os.path.exists(gdi_img_path):
        story.append(Image(gdi_img_path, width=420, height=140))
        story.append(Paragraph("Fig. 3: Great Duck Island Real-World Case Study (N=32 Motes, 60% Canopy Shade): Proposed framework sustains 100% survival across 500 rounds, delivering +15.5% mission extension over LEACH.", caption_style))

    # --- SECTION IX: DIGITAL TWIN PLATFORM ---
    story.append(Paragraph("VIII. FULL-STACK DIGITAL TWIN PLATFORM", h1))
    story.append(Paragraph(
        "To provide real-time cyber-physical observability, we implemented a full-stack platform: (1) Python 3.12 simulation engine, (2) FastAPI REST backend with SQLite persistence, and (3) React 19 + TypeScript single-page UI. The UI eliminates visual node homogeneity via a <b>continuous 7-tier energy gradient</b> (Full Green to Charcoal Red), on-node numerical <code>XX%</code> charge badges, micro-weather badges (Direct Sun vs Canopy Shade), and a click-to-pin live telemetry inspector HUD.",
        body
    ))

    ui_img_path = os.path.join(EXPLAINER_DIR, "01_topology_view.png")
    if os.path.exists(ui_img_path):
        story.append(Image(ui_img_path, width=420, height=135))
        story.append(Paragraph("Fig. 4: Digital Twin Interactive Canvas: Continuous 7-tier energy gradient, on-node percentage badges, micro-weather icons, and live click-to-pin node telemetry inspector.", caption_style))

    # --- SECTION X: DISCUSSION & HARDWARE LIMITATIONS ---
    story.append(Paragraph("IX. DISCUSSION, EMBEDDED CONSTRAINTS & LIMITATIONS", h1))
    story.append(Paragraph(
        "<b>Memory Footprint:</b> For <i>N</i>=50, <i>H</i>=5, and <i>T</i>=15, the 3D DP table requires 15 KB of RAM, comfortably fitting within the 48 KB SRAM budget of low-power ESP32 and ARM Cortex-M motes.<br/>"
        "<b>Clock Drift:</b> Crystal oscillator frequency drift (&plusmn;20 ppm) accumulates up to 72 ms/hour, mitigated by Flooding Time Synchronization Protocol (FTSP) micro-beacons consuming &approx;0.4% radio duty cycle.<br/>"
        "<b>Electrochemical Aging:</b> Future extensions will integrate semi-empirical capacity derating equations to account for multi-year SEI layer growth.",
        body
    ))

    # --- SECTION XI: CONCLUSION ---
    story.append(Paragraph("X. CONCLUSION", h1))
    story.append(Paragraph(
        "This paper presented a verified, hardware-grounded cyber-physical framework for routing in renewable wireless sensor networks. We demonstrated that static snapshot routing commits the False Rejection flaw and Accelerated Burnout. We resolved these challenges via: (1) 3D Time-Augmented DP with provable 2&epsilon;-approximation bounds, (2) DSU live detours delivering 3.8x to 6.02x speedup, (3) 24-bin histogram belief filtering reducing calibration error to 0.019, and (4) discovery of the Receiver Dissipation Tax (<i>E</i><sub>rx</sub> = 50 nJ/bit). Verified through 75 automated unit tests, multi-seed benchmarks, and real-world habitat traces, this framework provides the foundation for zero-brownout autonomous sensor networks.",
        body
    ))

    # --- REFERENCES ---
    story.append(Paragraph("REFERENCES", h1))
    refs = [
        "[1] I. F. Akyildiz, W. Su, Y. Sankarasubramaniam, and E. Cayirci, 'Wireless sensor networks: a survey,' <i>Computer Networks</i>, vol. 38, no. 4, pp. 393–422, 2002.",
        "[2] A. Mainwaring, D. Culler, J. Polastre, R. Szewczyk, and J. Anderson, 'Wireless sensor networks for habitat monitoring,' in <i>Proc. ACM WSNA</i>, 2002, pp. 88–97.",
        "[3] W. R. Heinzelman, A. Chandrakasan, and H. Balakrishnan, 'Energy-efficient communication protocol for wireless microsensor networks,' in <i>Proc. 33rd HICSS</i>, 2000, pp. 1–10.",
        "[4] A. Kansal, J. Hsu, S. Zahedi, and M. B. Srivastava, 'Power management in energy harvesting sensor networks,' <i>ACM Trans. Embed. Comput. Syst.</i>, vol. 6, no. 4, pp. 32–es, 2007.",
        "[5] M. Gorlatova, J. Sarik, M. Grebla, M. Hermans, and G. Zussman, 'Movers and shakers: Kinetic energy harvesting for IoT,' <i>IEEE JSAC</i>, vol. 33, no. 8, pp. 1624–1639, 2015.",
        "[6] J.-H. Chang and L. Tassiulas, 'Maximum lifetime routing in wireless sensor networks,' <i>IEEE/ACM Trans. Netw.</i>, vol. 12, no. 4, pp. 609–619, 2004.",
        "[7] C. M. Vigorito, D. Ganesan, and A. G. Barto, 'Adaptive duty cycling in energy harvesting sensor networks,' in <i>Proc. IEEE SECON</i>, 2007, pp. 21–30.",
        "[8] R. E. Tarjan, 'Efficiency of a good but not linear set union algorithm,' <i>J. ACM</i>, vol. 22, no. 2, pp. 215–225, 1975.",
        "[9] M. Maróti, B. Kusy, G. Simon, and Á. Lédeczi, 'The flooding time synchronization protocol,' in <i>Proc. ACM SenSys</i>, 2004, pp. 39–49.",
        "[10] G. Rathee, R. Iqbal, O. Waqar, and F. Bashir, 'On the design of ACO-based routing for IoT networks,' <i>IEEE Trans. Eng. Manage.</i>, 2021."
    ]
    for r in refs:
        story.append(Paragraph(r, ParagraphStyle('RefStyle', parent=body, fontSize=7.5, leading=10, spaceAfter=2)))

    # --- BIOGRAPHIES ---
    story.append(Spacer(1, 10))
    story.append(Paragraph("AUTHOR BIOGRAPHIES", h1))
    
    bio_santhosh = (
        "<b>SANTHOSH G</b> is an undergraduate student researcher in the Department of Electrical and Computer Science Engineering, School of Electrical Engineering (SELECT) at Vellore Institute of Technology (VIT), Vellore, India (Registration No. 25BEL0016). His research interests include cyber-physical sensor systems, time-expanded dynamic programming, Bayesian belief filtering, and energy-neutral embedded networking. He served as the primary architect for the 3D Time-Augmented DP core and probabilistic belief filter algorithms."
    )
    bio_thilang = (
        "<b>THILANG T V</b> is an undergraduate student researcher in the Department of Electrical and Computer Science Engineering, School of Electrical Engineering (SELECT) at Vellore Institute of Technology (VIT), Vellore, India (Registration No. 25BEL0036). His research focuses on graph algorithms, fault-tolerant network topologies, and distributed RESTful architectures. He developed the Disjoint-Set Union (DSU) live detour recovery framework and led the full-stack Digital Twin web platform implementation."
    )
    bio_ananth = (
        "<b>ANANTHAKRISHNAN R</b> is an undergraduate student researcher in the Department of Electrical and Computer Science Engineering, School of Electrical Engineering (SELECT) at Vellore Institute of Technology (VIT), Vellore, India (Registration No. 25BEL0005). His research interests include RF transceiver physical modeling, log-normal channel fading characterization, and automated software verification testbenches. He formulated the first-order radio dissipation tax and created the 75-test automated verification suite."
    )
    
    for bio in [bio_santhosh, bio_thilang, bio_ananth]:
        story.append(Paragraph(bio, ParagraphStyle('BioStyle', parent=body, fontSize=8, leading=11, spaceAfter=6)))

    doc.build(story, canvasmaker=IEEEAccessNumberedCanvas)
    print(f"Successfully generated IEEE Access Paper PDF at: {output_pdf_path}")

if __name__ == "__main__":
    out_pdf = os.path.join(REPORT_DIR, "IEEE_Access_Research_Paper.pdf")
    build_ieee_access_pdf(out_pdf)
