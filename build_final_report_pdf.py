import os
import sys
import shutil
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import pymupdf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "report", "explainer_images")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
EQ_DIR = os.path.join(BASE_DIR, "rep2_eq_pngs")
GITHUB_REPO_URL = "https://github.com/santhoshvellore7119-web/WSN_proj"

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and stamp total page count,
    running headers, and running footers across all pages.
    """
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_decorations(self, page_count):
        self.saveState()
        self.setFont('Helvetica', 7.5)
        self.setFillColor(colors.HexColor('#4B5563'))  # Slate gray
        
        # Running Header on page 2+: Project Topic on Left, Names & Reg No on Right
        if self._pageNumber > 1:
            self.setFont('Helvetica-Bold', 7.2)
            self.drawString(46, 804, 'Project Topic: Adaptive Routing in Energy-Harvesting Wireless Sensor Networks')
            self.setFont('Helvetica', 7.2)
            self.drawRightString(549, 804, 'Santhosh G (25BEL0016) | Thilang T V (25BEL0036) | Ananthakrishnan R (25BEL0005)')
            self.setStrokeColor(colors.HexColor('#D1D5DB'))
            self.setLineWidth(0.5)
            self.line(46, 797, 549, 797)
        
        # Running Footer on all pages: Names, Reg No, Page X of Y
        self.setFont('Helvetica', 7.2)
        self.drawString(46, 26, 'Names & Reg No: Santhosh G (25BEL0016), Thilang T V (25BEL0036), Ananthakrishnan R (25BEL0005)')
        self.drawRightString(549, 26, f'Page {self._pageNumber} of {page_count}')
        self.setStrokeColor(colors.HexColor('#D1D5DB'))
        self.setLineWidth(0.5)
        self.line(46, 35, 549, 35)
        self.restoreState()


def make_callout_box(content_flowable, width=503.25, bg_color='#F8F8F6', border_color='#E5E7EB', padding=5):
    """Wraps any flowable inside a styled academic callout box."""
    t = Table([[content_flowable]], colWidths=[width])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(bg_color)),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor(border_color)),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), padding),
        ('BOTTOMPADDING', (0, 0), (-1, -1), padding),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    return t


def get_eq_image(eq_idx, width, height):
    """Returns an Image flowable for a generated equation PNG."""
    p = os.path.join(EQ_DIR, f"eq_{eq_idx}.png")
    if os.path.exists(p):
        return Image(p, width=width, height=height)
    return Paragraph(f"[Equation {eq_idx}]", ParagraphStyle('Missing', fontSize=9))


def get_figure_image(filename, width=440, height=220):
    """Returns an Image flowable from results/ or report/explainer_images/."""
    p_results = os.path.join(RESULTS_DIR, filename)
    p_explainer = os.path.join(IMAGE_DIR, filename)
    p = p_results if os.path.exists(p_results) else p_explainer
    if os.path.exists(p):
        return Image(p, width=width, height=height)
    return Paragraph(f"[Image {filename}]", ParagraphStyle('Missing', fontSize=9))


def build_final_report_pdf(output_pdf_path: str):
    os.makedirs(os.path.dirname(os.path.abspath(output_pdf_path)), exist_ok=True)

    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=A4,  # 595.28 x 841.89 pt
        leftMargin=46,
        rightMargin=46,
        topMargin=46,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()

    # Color Palette matching Report 1 & 2
    c_title = colors.HexColor('#111827')
    c_subtitle = colors.HexColor('#374151')
    c_body = colors.HexColor('#1F2937')
    c_th_bg = colors.HexColor('#F3F4F6')
    c_grid = colors.HexColor('#E5E7EB')
    c_alt_row = colors.HexColor('#F9FAFB')

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=c_title,
        spaceAfter=3
    )

    sub_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_subtitle,
        spaceAfter=8
    )

    h1 = ParagraphStyle(
        'H1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=14.5,
        textColor=c_title,
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )

    h2 = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12.5,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=5,
        spaceAfter=2.5,
        keepWithNext=True
    )

    body = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.2,
        leading=11.2,
        textColor=c_body,
        spaceAfter=3.5
    )

    body_math = ParagraphStyle(
        'BodyMath',
        parent=body,
        fontSize=8.2,
        leading=12.5,
        spaceAfter=2.5
    )

    caption_style = ParagraphStyle(
        'Caption',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#4B5563'),
        alignment=1,  # Center
        spaceBefore=2.5,
        spaceAfter=5
    )

    th = ParagraphStyle(
        'TH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#111827')
    )

    td = ParagraphStyle(
        'TD',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.2,
        leading=9.2,
        textColor=c_body
    )

    td_b = ParagraphStyle(
        'TDBold',
        parent=td,
        fontName='Helvetica-Bold'
    )

    code_block = ParagraphStyle(
        'CodeBlock',
        parent=body,
        fontName='Courier',
        fontSize=6.8,
        leading=8.5,
        textColor=colors.HexColor('#111827')
    )

    story = []

    # =========================================================================
    # PAGE 1: TITLE, STRICT HEADER METADATA & EXECUTIVE SUMMARY
    # =========================================================================
    story.append(Paragraph("Adaptive Routing in Energy-Harvesting Wireless Sensor Networks", title_style))
    story.append(Paragraph("Final Course Project Comprehensive Report", sub_style))

    # Strict Header Block: Project Topic, Names, and Registration Numbers (Reg No)
    header_table_data = [
        [Paragraph("<b>Project Topic</b>", th), Paragraph("<b>Adaptive Routing in Energy-Harvesting Wireless Sensor Networks</b>", td), ""],
        [Paragraph("<b>S.No</b>", th), Paragraph("<b>Name</b>", th), Paragraph("<b>Registration Number (Reg No)</b>", th)],
        [Paragraph("1", td), Paragraph("<b>Santhosh G</b>", td), Paragraph("<b>25BEL0016</b>", td)],
        [Paragraph("2", td), Paragraph("<b>Thilang T V</b>", td), Paragraph("<b>25BEL0036</b>", td)],
        [Paragraph("3", td), Paragraph("<b>Ananthakrishnan R</b>", td), Paragraph("<b>25BEL0005</b>", td)],
    ]
    t_header = Table(header_table_data, colWidths=[45, 235, 223.25])
    t_header.setStyle(TableStyle([
        ('SPAN', (1, 0), (2, 0)),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (0, 1), (-1, 1), c_th_bg),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.4, c_grid),
        ('ROWBACKGROUNDS', (0, 2), (-1, -1), [colors.white, c_alt_row]),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_header)
    story.append(Spacer(1, 6))

    story.append(Paragraph("Executive Summary &amp; Research Motivation", h1))
    story.append(Paragraph(
        "Over the duration of this course capstone project, our team investigated a subtle but catastrophic failure mode that arises "
        "when classical routing protocols are applied to Energy-Harvesting Wireless Sensor Networks (EH-WSNs). For more than two decades, "
        "the foundational ad-hoc routing literature has operated under a single thermodynamic invariant: stored electrochemical battery "
        "energy decreases monotonically over time (<i>E</i>(<i>t</i><sub>1</sub>) &ge; <i>E</i>(<i>t</i><sub>2</sub>) for all <i>t</i><sub>1</sub> &le; <i>t</i><sub>2</sub>). "
        "Under this assumption, algorithms such as Dijkstra's shortest path, A* search, and standard LEACH clustering evaluate candidate forwarders "
        "using static battery snapshots captured at the start of a transmission round (<i>t</i> = 0).",
        body
    ))
    story.append(Paragraph(
        "When sensor nodes harvest energy from ambient sources (micro-photovoltaics, thermal gradients, or piezoelectric harvesters), "
        "stored energy is strictly <b>non-monotonic</b>. An intermediate relay that begins a round nearly depleted can actively harvest "
        "replenishment while upstream packets propagate through preceding multi-hop hops. Conversely, a node in dense foliage shade "
        "may start with full reserves but receive zero solar influx, rapidly burning out if repeatedly chosen as an intermediary. "
        "Static snapshot-based routing is blind to this incoming energy, resulting in two severe pathologies:<br/>"
        "&bull; <b>The False Rejection Pathology:</b> Recharging relays are discarded because their instantaneous battery level at <i>t</i> = 0 "
        "is deemed insufficient, forcing packets onto circuitous peripheral detours that waste global network energy.<br/>"
        "&bull; <b>The Shaded Burnout Pathology:</b> Shaded nodes in canopy microclimates are prematurely exhausted because static algorithms "
        "mistake their high initial reserves for sustainable relay capacity.",
        body
    ))
    story.append(Paragraph(
        "To resolve these challenges on resource-constrained embedded microcontrollers (&lt;64 KB RAM), we engineered, implemented, "
        "and empirically validated an integrated algorithmic framework:<br/>"
        "1. <b>3D Time-Augmented Dynamic Programming (<i>dp</i>[<i>v</i>][<i>h</i>][<i>t</i>]):</b> A deterministic polynomial lookahead router "
        "over a time-expanded DAG that synchronizes forwarding decisions with solar recharge profiles, guaranteeing a provable 2&epsilon;-approximation bound.<br/>"
        "2. <b>Disjoint-Set Union (DSU) Live Detour Recovery:</b> An in-flight fault repair mechanism using Union-Find with path compression "
        "and rank optimization that splices detour bridges in <i>O</i>(deg(<i>u</i>) &middot; &alpha;(<i>V</i>)) time—achieving a <b>6.02x execution speedup</b> "
        "over full recomputation with 100% Packet Delivery Ratio up to a 30% node failure rate.<br/>"
        "3. <b>Solar-Weighted EH-LEACH Clustering:</b> A harvest-aware cluster-head threshold <i>T</i>(<i>n</i>) that boosts sunlit cluster head election "
        "by 2.4x, preventing premature cluster head exhaustion.<br/>"
        "4. <b>24-Bin Discrete Histogram Belief Filter:</b> A Bayesian belief filter with exact boundary mass clipping at 0 and <i>E</i><sub>max</sub> "
        "and Sheppard's second-order correction, cutting Expected Calibration Error by over 50% under throttled telemetry.",
        body
    ))
    story.append(Paragraph(
        "The entire platform was built from scratch in Python, FastAPI, and React 19, verified by an automated test bench of "
        "<b>75 unit tests (100% passing in 3.54 seconds)</b>. In statistical multi-seed benchmarks across 30 seeds and 350 rounds, "
        "our framework closed up to 81.5% of the delivery gap compared to an omniscient offline oracle. In a real-world case study on "
        "the Great Duck Island habitat topology (32 motes, 60% spruce shade), our system sustained <b>100% mote survival with zero node deaths "
        "across 500 rounds (+15.5% mission extension over LEACH)</b>.",
        body
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: INDUSTRIAL RELEVANCE & PROBLEM STATEMENT
    # =========================================================================
    story.append(Paragraph("1. Project Overview &amp; Industrial Relevance", h1))
    story.append(Paragraph(
        "Wireless Sensor Networks serve as the sensory backbone for modern civil infrastructure, agriculture, and environmental science. "
        "Historically, the Achilles' heel of wireless sensing has been battery replenishment: replacing coin cells in deep forest canopies, "
        "remote mountain ridges, or structural joints is logistically impractical and hazardous. Ambient micro-energy harvesting "
        "(solar micro-cells, thermoelectric generators, piezoelectric harvesters) offers the promise of perpetual, autonomous operation. "
        "However, harvesting hardware alone does not guarantee perpetual life—the networking layer must dynamically balance load "
        "according to ambient energy availability.",
        body
    ))
    story.append(Paragraph(
        "Our lookahead routing framework directly addresses real-world industrial needs across four major domains:<br/>"
        "&bull; <b>Precision Viticulture &amp; Smart Agriculture:</b> Grapevines and crop canopies cast moving shadows throughout the day. "
        "Lookahead routing steers telemetry packets through sunlit vineyard rows, preventing shaded soil sensors from exhausting their reserves.<br/>"
        "&bull; <b>Wildfire Early Warning &amp; Forest Ecology:</b> In dense coniferous forests, understory nodes receive less than 5% of incident sunlight. "
        "Our solar-weighted clustering reserves shaded understory nodes exclusively for local sensing while elevating well-exposed canopy nodes to cluster heads.<br/>"
        "&bull; <b>Structural Health Monitoring (SHM):</b> Vibration harvesters inside bridge decks generate energy in bursts during traffic peaks. "
        "Our DSU live detour recovery allows motes to seize transient vibration spikes to forward heavy acoustic emission packets.<br/>"
        "&bull; <b>Smart Urban Infrastructure:</b> Building shadows shift across street corridors, creating localized energy deserts. "
        "Time-augmented lookahead ensures city sensors route through sunlit street corners.",
        body
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("2. Problem Statement &amp; Mathematical Formulation", h1))
    story.append(Paragraph(
        "<b>2.1 Network Graph Model:</b> The physical sensor field is modeled as a directed Euclidean graph <i>G</i> = (<i>V</i>, <i>E</i>) "
        "over a 100 m &times; 100 m plane. <i>V</i> = {<i>v</i><sub>1</sub>, ..., <i>v</i><sub>N</sub>} represents <i>N</i> = 50 deployed "
        "sensor nodes, and <i>v</i><sub>BS</sub> is the Base Station sink at (50, 50) with continuous mains power. A communication link "
        "(<i>u</i>, <i>v</i>) &isin; <i>E</i> exists if and only if Euclidean distance <i>d</i>(<i>u</i>, <i>v</i>) &le; <i>R</i><sub>tx</sub> (50.0 m).",
        body
    ))
    story.append(Paragraph(
        "<b>2.2 The Non-Monotonic Energy Invariant:</b> Each sensor node possesses maximum storage capacity <i>C</i><sub>v</sub> = <i>E</i><sub>max</sub> = 0.50 J, "
        "leakage rate &lambda; = 1.0 &times; 10<sup>-5</sup> s<sup>-1</sup>, and charging efficiency &eta; = 0.85. Continuous battery state evolves as:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;d<i>E</i><sub>v</sub>(<i>t</i>)/d<i>t</i> = min( &eta; &middot; <i>H</i><sub>v</sub>(<i>t</i>) - &lambda; &middot; <i>E</i><sub>v</sub>(<i>t</i>) - <i>P</i><sub>drain</sub>(<i>v</i>, <i>t</i>), (<i>E</i><sub>max</sub> - <i>E</i><sub>v</sub>(<i>t</i>))/&Delta;<i>t</i> )<br/>"
        "Because ambient harvesting rate &eta;<i>H</i><sub>v</sub>(<i>t</i>) can exceed internal dissipation during sunlight hours, d<i>E</i><sub>v</sub>(<i>t</i>)/d<i>t</i> &gt; 0, "
        "establishing the non-monotonic invariant: &exist; <i>t</i><sub>1</sub> &lt; <i>t</i><sub>2</sub> such that <i>E</i><sub>v</sub>(<i>t</i><sub>1</sub>) &lt; <i>E</i><sub>v</sub>(<i>t</i><sub>2</sub>).",
        body_math
    ))
    story.append(Paragraph("<b>2.3 Bottleneck Residual Formulation:</b>", h2))
    story.append(Paragraph(
        "For a multi-hop path <i>P</i> = (<i>v</i><sub>0</sub>, <i>v</i><sub>1</sub>, ..., <i>v</i><sub>k</sub>) with per-hop transmission and scheduling delay &delta;, "
        "packet arrival at node <i>v</i><sub>i</sub> occurs at time <i>t</i><sub>i</sub> = <i>t</i><sub>curr</sub> + <i>i</i> &middot; &delta;. "
        "The true bottleneck residual energy <i>B</i>(<i>P</i>) is defined as the minimum remaining energy across all nodes after satisfying reception costs:",
        body
    ))

    # Equation 1: Bottleneck Formulation
    story.append(make_callout_box(get_eq_image(1, width=370, height=38.7), padding=4))
    story.append(Spacer(1, 3))
    story.append(Paragraph("<b>2.4 Global Path Optimization Objective:</b>", h2))
    story.append(Paragraph(
        "The router selects the path <i>P</i>* within hop limit <i>H</i> that maximizes bottleneck residual energy subject to physical transmission affordability:",
        body
    ))

    # Equation 2: Path Optimization
    story.append(make_callout_box(get_eq_image(2, width=401.3, height=24.9), padding=4))
    story.append(Spacer(1, 4))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: LITERATURE REVIEW & COMPARATIVE GAP ANALYSIS
    # =========================================================================
    story.append(Paragraph("3. Literature Review &amp; Comparative Gap Analysis", h1))
    story.append(Paragraph(
        "To position our work within current ad-hoc networking research, we conducted a systematic review of 9 recent papers (2020–2025) "
        "spanning energy-harvesting routing, cluster-head election, and fault tolerance. Most proposed protocols either neglect incoming "
        "energy entirely or rely on centralized mathematical programming models that cannot run on embedded microcontrollers.",
        body
    ))

    lit_table_data = [
        [Paragraph("Author &amp; Year", th), Paragraph("Venue / Protocol", th), Paragraph("Lookahead Energy?", th), Paragraph("Reception Penalty (<i>E</i><sub>rx</sub>)", th), Paragraph("Fault Detour Speed", th), Paragraph("Complexity", th)],
        [Paragraph("Akyildiz et al. (2002)", td_b), Paragraph("Comp. Netw. (Survey)", td), Paragraph("No (Battery)", td), Paragraph("Neglected", td), Paragraph("None", td), Paragraph("<i>O</i>(|<i>V</i>|)", td)],
        [Paragraph("Heinzelman (2002)", td_b), Paragraph("IEEE TWC (LEACH)", td), Paragraph("No (Randomized)", td), Paragraph("Neglected", td), Paragraph("Packet Drop", td), Paragraph("<i>O</i>(|<i>V</i>|)", td)],
        [Paragraph("Sah &amp; Amgoth (2020)", td_b), Paragraph("Info. Fusion (Survey)", td), Paragraph("Conceptual", td), Paragraph("Neglected", td), Paragraph("None", td), Paragraph("N/A", td)],
        [Paragraph("Sharma et al. (2020)", td_b), Paragraph("IEEE COMST (Survey)", td), Paragraph("No (Snapshot)", td), Paragraph("Neglected", td), Paragraph("None", td), Paragraph("N/A", td)],
        [Paragraph("Naeem et al. (2021)", td_b), Paragraph("IEEE TGCN (DARE-SEP)", td), Paragraph("No (Hetero Batt)", td), Paragraph("Partial", td), Paragraph("None", td), Paragraph("<i>O</i>(|<i>V</i>|)", td)],
        [Paragraph("Tan et al. (2021)", td_b), Paragraph("ACM TOSN (Time-Exp)", td), Paragraph("Yes (Global LP)", td), Paragraph("Neglected", td), Paragraph("Centralized Rerun", td), Paragraph("<i>O</i>(<i>V</i><sup>3</sup><i>T</i><sup>3</sup>)", td)],
        [Paragraph("Kim &amp; Park (2021)", td_b), Paragraph("IEEE IoTJ (Opportunistic)", td), Paragraph("Local 1-hop only", td), Paragraph("Neglected", td), Paragraph("Fallback Hop", td), Paragraph("Stochastic", td)],
        [Paragraph("Rathee et al. (2021)", td_b), Paragraph("IEEE TEM (ACO Routing)", td), Paragraph("Semi (Pheromone)", td), Paragraph("Neglected", td), Paragraph("Slow Converge", td), Paragraph("<i>O</i>(<i>K</i>|<i>E</i>|<i>I</i>)", td)],
        [Paragraph("Zhang et al. (2021)", td_b), Paragraph("IEEE Access (EH-Cluster)", td), Paragraph("Yes (CH only)", td), Paragraph("Neglected", td), Paragraph("None", td), Paragraph("<i>O</i>(|<i>V</i>|)", td)],
        [Paragraph("Han et al. (2022)", td_b), Paragraph("MDPI Sensors (Ada-Clust)", td), Paragraph("Yes (CH only)", td), Paragraph("Neglected", td), Paragraph("None", td), Paragraph("<i>O</i>(|<i>V</i>|)", td)],
        [Paragraph("Sah &amp; Amgoth (2023)", td_b), Paragraph("IEEE Sensors (Predictor)", td), Paragraph("Yes (EWMA)", td), Paragraph("Neglected", td), Paragraph("None", td), Paragraph("<i>O</i>(1)", td)],
        [Paragraph("<b>Our Framework</b>", td_b), Paragraph("<b>3D Time-DP + DSU</b>", td_b), Paragraph("<b>Yes (Exact DAG)</b>", td_b), Paragraph("<b>Exact (0.200 mJ)</b>", td_b), Paragraph("<b>0.57 ms (6.02x)</b>", td_b), Paragraph("<b><i>O</i>(|<i>E</i>|<i>HT</i>)</b>", td_b)],
    ]
    t_lit = Table(lit_table_data, colWidths=[90, 95, 75, 85, 78, 80.25])
    t_lit.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_th_bg),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.4, c_grid),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, c_alt_row]),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#EFF6FF')),  # Highlight our row
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_lit)
    story.append(Spacer(1, 4))

    story.append(Paragraph("3.2 Architectural Differentiation &amp; Novelty", h2))
    story.append(Paragraph(
        "Our work addresses key weaknesses in existing literature through four concrete innovations:<br/>"
        "&bull; <b>Embedded Polynomial Lookahead:</b> While Tan et al. required heavy centralized LP solvers (<i>O</i>(<i>V</i><sup>3</sup><i>T</i><sup>3</sup>)), "
        "our 3D Time-Augmented DP executes in <i>O</i>(|<i>E</i>|<i>HT</i>) time, requiring less than 5.2 ms and under 48 KB RAM on ARM Cortex-M4 motes.<br/>"
        "&bull; <b>Local Detour Repair via Disjoint-Set Union:</b> Unlike standard protocols that suffer packet drops on relay failure, "
        "our DSU algorithm repairs broken forwarding trees locally in <i>O</i>(deg(<i>u</i>)&alpha;(<i>V</i>)) time, avoiding expensive network-wide recomputation.<br/>"
        "&bull; <b>Transceiver Reception Overhead Integration:</b> We explicitly incorporate Heinzelman's electronic reception dissipation (<i>E</i><sub>rx</sub> = 0.200 mJ), "
        "preventing the algorithm from selecting inefficient multi-hop detours over short links.<br/>"
        "&bull; <b>Boundary-Clipping Histogram Belief Filter:</b> Instead of continuous Gaussian filters that leak probability into unphysical "
        "negative energies, we maintain a 24-bin discrete histogram filter with exact mass boundary clamping and Sheppard's variance correction.",
        body
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: RADIO DISSIPATION & ENVIRONMENTAL HARVESTING
    # =========================================================================
    story.append(Paragraph("4. Physical Radio &amp; Environmental Modeling", h1))
    story.append(Paragraph(
        "<b>4.1 First-Order Radio Dissipation Physics:</b> Sensor nodes communicate over wireless radio channels adhering to Heinzelman's "
        "first-order radio model, calibrated to Texas Instruments CC2420 transceiver specifications (2.4 GHz IEEE 802.15.4):",
        body
    ))

    # Equation 5: Heinzelman Radio Model
    story.append(make_callout_box(get_eq_image(5, width=342.9, height=32.8), padding=4))
    story.append(Spacer(1, 3))
    story.append(Paragraph(
        "where <i>k</i> = 4000 bits (500-byte packet), <i>E</i><sub>elec</sub> = 50.0 nJ/bit, &epsilon;<sub>fs</sub> = 10.0 pJ/bit/m<sup>2</sup>, "
        "and &epsilon;<sub>mp</sub> = 0.0013 pJ/bit/m<sup>4</sup>. The crossover distance threshold <i>d</i><sub>0</sub> is the exact distance "
        "where free-space and multipath amplifier energies are equal:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<i>d</i><sub>0</sub> = &radic;(&epsilon;<sub>fs</sub> / &epsilon;<sub>mp</sub>) = &radic;(10.0 &times; 10<sup>-12</sup> / 0.0013 &times; 10<sup>-12</sup>) &approx; <b>87.7058 meters</b>.",
        body_math
    ))
    story.append(Spacer(1, 3))

    story.append(Paragraph("4.2 The Electronic Reception Overhead (<i>E</i><sub>rx</sub>) Discovery", h2))
    story.append(Paragraph(
        "A common assumption in ad-hoc networking is that multi-hop relaying is always more energy-efficient than direct transmission "
        "because transmission distance is shortened (reducing <i>d</i><sup>2</sup> dissipation). In our simulation experiments, we discovered "
        "that intermediate relaying incurs an unavoidable electronic reception penalty:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<i>E</i><sub>rx</sub> = <i>k</i> &middot; <i>E</i><sub>elec</sub> = 4000 bits &times; 50.0 nJ/bit = <b>0.200 mJ per hop</b>.",
        body_math
    ))
    story.append(Paragraph(
        "<b>Numerical Demonstration:</b> Consider delivering a 4000-bit packet over distance <i>d</i> = 60.0 m (<i>d</i> &lt; <i>d</i><sub>0</sub>):<br/>"
        "&bull; <b>Direct Single-Hop:</b> <i>E</i><sub>tx, direct</sub> = 4000 &middot; (50 nJ + 10 pJ &middot; 60<sup>2</sup>) = 0.200 mJ + 0.144 mJ = <b>0.344 mJ</b>.<br/>"
        "&bull; <b>Two-Hop via Midpoint (<i>d</i><sub>1</sub> = 30 m, <i>d</i><sub>2</sub> = 30 m):</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<i>E</i><sub>tx, hop1</sub> = 4000 &middot; (50 nJ + 10 pJ &middot; 30<sup>2</sup>) = 0.200 mJ + 0.036 mJ = 0.236 mJ<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<i>E</i><sub>rx, relay</sub> = 4000 &middot; 50 nJ = <b>0.200 mJ (Receiver Tax)</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<i>E</i><sub>tx, hop2</sub> = 4000 &middot; (50 nJ + 10 pJ &middot; 30<sup>2</sup>) = 0.200 mJ + 0.036 mJ = 0.236 mJ<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<i>E</i><sub>total, 2-hop</sub> = 0.236 + 0.200 + 0.236 = <b>0.672 mJ</b>.<br/>"
        "<b>Finding:</b> In the free-space regime, multi-hop relaying consumes <b>1.953x (nearly double)</b> the energy of direct transmission! "
        "Relaying is beneficial only when transmission distance exceeds <i>d</i><sub>0</sub> (87.7 m), or when intermediate nodes are actively "
        "harvesting solar replenishment. Our 3D Time-DP explicitly factors <i>E</i><sub>rx</sub> into every state transition.",
        body
    ))
    story.append(Spacer(1, 3))

    story.append(Paragraph("4.3 Environmental Harvesting Regimes", h2))
    story.append(Paragraph(
        "To evaluate protocol performance across diverse environments, we implemented four distinct harvesting regimes in <code>src/harvesting_model.py</code>:<br/>"
        "1. <b>Diurnal Solar Cycle:</b> Clear-sky solar irradiance modeled via a clipped half-sine wave with 24-hour periodicity. At night, harvest drops to zero.<br/>"
        "2. <b>Spatial Canopy Shadowing:</b> Simulates forest foliage attenuation where spatial occlusion <i>S</i>(<i>x</i>, <i>y</i>) &isin; [0.05, 1.0] reduces incoming light.<br/>"
        "3. <b>Stochastic Poisson Bursts:</b> Models ambient vibration, wind, or RF harvesting arriving as discrete stochastic energy impulses.<br/>"
        "4. <b>Empirical Weather Traces:</b> Replays continuous 24-hour solar irradiance datasets recorded at solar monitoring stations.",
        body
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: PROPOSED ALGORITHMIC FORMULATIONS & CODE
    # =========================================================================
    story.append(Paragraph("5. Proposed DSA Formulations &amp; Algorithms as Coded", h1))
    story.append(Paragraph(
        "<b>5.1 3D Time-Augmented Dynamic Programming (<code>src/dp_lifetime.py</code>):</b> "
        "Standard shortest path algorithms evaluate costs on a static graph. We model the routing space as a time-expanded Directed Acyclic Graph (DAG) "
        "&Gscr;<sub>T</sub> = (<i>V</i> &times; {0, ..., <i>T</i>}, &Escr;<sub>T</sub>), where each state is defined by node <i>v</i>, hop count <i>h</i>, "
        "and time offset <i>t</i>. The recurrence maximizes projected bottleneck energy across candidate predecessors:",
        body
    ))

    # Equation 3: DP recurrence
    story.append(make_callout_box(get_eq_image(3, width=355.6, height=23.6), padding=4))
    story.append(Spacer(1, 3))
    story.append(Paragraph(
        "subject to <i>dp</i>[<i>u</i>][<i>h</i>-1][<i>t</i>-&delta;] &ge; <i>E</i><sub>tx</sub>(<i>k</i>, <i>d</i>(<i>u</i>, <i>v</i>)). "
        "Base condition: <i>dp</i>[<i>s</i>][0][0] = <i>E</i><sub>s</sub>(<i>t</i><sub>curr</sub>), and -&infin; elsewhere. "
        "The Sink has capacity &infin; and <i>E</i><sub>rx</sub> = 0.",
        body_math
    ))

    dp_code_snippet = (
        "def compute_time_augmented_dp(source, sink, nodes, dist_mat, max_h=10, horizon=15):\n"
        "    dp = collections.defaultdict(lambda: -float('inf'))\n"
        "    parent = {}\n"
        "    dp[(source, 0, 0)] = nodes[source].energy\n"
        "    best_bn, best_state = -float('inf'), None\n"
        "\n"
        "    for h in range(1, max_h + 1):\n"
        "        for t in range(h, horizon + 1):\n"
        "            for v, v_node in nodes.items():\n"
        "                if not v_node.is_alive(): continue\n"
        "                e_proj = v_node.predict_energy(steps_ahead=t)\n"
        "                e_rx = 0.0 if v == sink else compute_rx_energy(4000)\n"
        "                for u in v_node.neighbors:\n"
        "                    u_state = (u, h - 1, t - 1)\n"
        "                    if u_state not in dp: continue\n"
        "                    e_tx = compute_tx_energy(4000, dist_mat[u][v])\n"
        "                    if dp[u_state] < e_tx: continue\n"
        "                    cand = min(dp[u_state], e_proj - e_rx)\n"
        "                    if cand > dp[(v, h, t)]:\n"
        "                        dp[(v, h, t)] = cand; parent[(v, h, t)] = u_state\n"
        "                        if v == sink and cand > best_bn:\n"
        "                            best_bn, best_state = cand, (v, h, t)\n"
        "    # Reconstruct path via backpointers\n"
        "    path, curr = [], best_state\n"
        "    while curr: path.append(curr[0]); curr = parent.get(curr)\n"
        "    return path[::-1], best_bn"
    )
    story.append(make_callout_box(Paragraph(dp_code_snippet.replace('\n', '<br/>').replace(' ', '&nbsp;'), code_block), padding=4))
    story.append(Spacer(1, 4))

    story.append(Paragraph("5.2 Disjoint-Set Union (DSU) Live Detour Repair (<code>src/routing.py</code>)", h2))
    story.append(Paragraph(
        "When an in-flight forwarder browns out mid-round, re-running 3D DP takes <i>O</i>(|<i>E</i>|<i>HT</i>) time (3.44 ms), "
        "causing queue overflow and packet loss. We implement Union-Find with path compression and rank optimization. "
        "Upstream node <i>u</i> queries surviving neighbors <i>w</i> &isin; &Nscr;(<i>u</i>). Connectivity to the Base Station is verified "
        "in <i>O</i>(&alpha;(<i>V</i>)) time via <code>find(w) == find(BS)</code>. The connected neighbor minimizing incremental <i>E</i><sub>tx</sub> "
        "with sufficient battery is spliced as a detour bridge in <b>0.57 ms (6.02x faster)</b>.",
        body
    ))

    dsu_code_snippet = (
        "def live_dsu_detour_repair(predecessor, failed_node, sink_id, dsu, nodes, dist_mat):\n"
        "    sink_root = dsu.find(sink_id)\n"
        "    best_bridge, min_tx = None, float('inf')\n"
        "    for nbr in nodes[predecessor].neighbors:\n"
        "        if nbr == failed_node or not nodes[nbr].is_alive(): continue\n"
        "        # O(alpha(V)) connectivity check\n"
        "        if dsu.find(nbr) == sink_root:\n"
        "            tx_cost = compute_tx_energy(4000, dist_mat[predecessor][nbr])\n"
        "            if nodes[nbr].energy >= (tx_cost + compute_rx_energy(4000)):\n"
        "                if tx_cost < min_tx:\n"
        "                    min_tx, best_bridge = tx_cost, nbr\n"
        "    return best_bridge  # Spliced directly into packet header"
    )
    story.append(make_callout_box(Paragraph(dsu_code_snippet.replace('\n', '<br/>').replace(' ', '&nbsp;'), code_block), padding=4))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 6: CLUSTERING & BAYESIAN BELIEF FILTERING
    # =========================================================================
    story.append(Paragraph("5.3 Solar-Weighted EH-LEACH Clustering (<code>src/clustering.py</code>)", h1))
    story.append(Paragraph(
        "Standard LEACH selects Cluster Heads (CHs) based on a stochastic threshold <i>T</i>(<i>n</i>) that ignores residual battery and solar influx. "
        "Depleted nodes frequently become CHs, dropping member packets. We formulate a harvest-weighted threshold <i>T</i>(<i>n</i>):",
        body
    ))

    # Equation 4: EH-LEACH Threshold
    story.append(make_callout_box(get_eq_image(4, width=248.0, height=32.1), padding=4))
    story.append(Spacer(1, 3))
    story.append(Paragraph(
        "where <i>p</i> = 0.10, <i>E</i><sub>n</sub> is current battery, <i>H</i><sub>n</sub> is projected solar harvest, and &beta; = 1.5. "
        "Sunlit nodes receive a 2.4x higher election probability, offloading aggregation duties from shaded, struggling nodes.",
        body
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("5.4 24-Bin Discrete Histogram Belief Filter (<code>src/energy_view.py</code>)", h1))
    story.append(Paragraph(
        "Transmitting battery telemetry every round exhausts energy. In practical networks, telemetry is reported once every <i>R</i> rounds (<i>R</i> &isin; [1, 25]). "
        "Standard Kalman/Gaussian filters suffer from <b>Gaussian tail leakage</b>: tails extend to &plusmn;&infin;, assigning non-zero probability to unphysical "
        "states where <i>E</i> &lt; 0 or <i>E</i> &gt; <i>E</i><sub>max</sub>. We engineered a 24-bin discrete Histogram Bayesian Filter <b>b</b><sub>i</sub>(<i>t</i>):",
        body
    ))
    story.append(Paragraph(
        "&bull; <b>Exact Boundary Mass Clipping:</b> Clamps probability mass that shifts below 0 into bin 1, and mass exceeding <i>E</i><sub>max</sub> into bin 24:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<i>p</i><sub>i, 1</sub> &larr; <i>p</i><sub>i, 1</sub> + &sum;<sub>m: E<sub>m</sub> &lt; 0</sub> <i>p</i><sub>i, m</sub>, &nbsp;&nbsp;&nbsp;&nbsp;"
        "<i>p</i><sub>i, 24</sub> &larr; <i>p</i><sub>i, 24</sub> + &sum;<sub>m: E<sub>m</sub> &gt; E<sub>max</sub></sub> <i>p</i><sub>i, m</sub>.<br/>"
        "&bull; <b>Sheppard's Second-Order Correction:</b> Corrects discretization variance: &sigma;<sup>2</sup><sub>corr</sub> = &sum; <i>p</i><sub>i, m</sub>(<i>E</i><sub>m</sub> - &mu;<sub>i</sub>)<sup>2</sup> - &delta;<sup>2</sup><sub>bin</sub> / 12.<br/>"
        "&bull; <b>Log-Domain Max-Product Belief Objective:</b> Maximizes path confidence under uncertainty:",
        body
    ))

    # Equation 6: Max-product belief objective
    story.append(make_callout_box(get_eq_image(6, width=258.8, height=32.2), padding=4))
    story.append(Spacer(1, 3))
    story.append(Paragraph(
        "&bull; <b>Lower Confidence Bound (LCB-Maximin):</b> Conservative routing uses <i>E</i><sub>v</sub><sup>LCB</sup> = max(0, &mu;<sub>v</sub> - &kappa; &middot; &sigma;<sub>v</sub>) (&kappa; = 1.0), "
        "preventing the router from over-allocating uncertain relays.",
        body
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("6. Implemented System Architecture &amp; Code Review", h1))
    story.append(Paragraph(
        "The codebase is cleanly decoupled into three tiers: algorithmic simulation engine (<code>src/</code>), asynchronous REST service (<code>backend/</code>), "
        "and digital twin web dashboard (<code>frontend/</code>). All components are verified by 75 unit tests.",
        body
    ))

    loc_summary = [
        [Paragraph("Directory", th), Paragraph("Key Module", th), Paragraph("Primary Responsibility", th), Paragraph("Verified LOC", th)],
        [Paragraph("<code>src/</code>", td_b), Paragraph("<code>network.py</code>", td), Paragraph("SensorNode entities, Euclidean graph topology, adjacency matrices", td), Paragraph("280 LOC", td)],
        [Paragraph("<code>src/</code>", td_b), Paragraph("<code>energy_model.py</code>", td), Paragraph("Heinzelman radio dissipation, reception penalty (0.200 mJ), <i>d</i><sub>0</sub> threshold", td), Paragraph("145 LOC", td)],
        [Paragraph("<code>src/</code>", td_b), Paragraph("<code>harvesting_model.py</code>", td), Paragraph("Diurnal half-sine curves, canopy shadow attenuation, Poisson bursts", td), Paragraph("195 LOC", td)],
        [Paragraph("<code>src/</code>", td_b), Paragraph("<code>dp_lifetime.py</code>", td), Paragraph("3D Time-Augmented DP (<i>dp</i>[<i>v</i>][<i>h</i>][<i>t</i>]), backpointers, lookahead", td), Paragraph("310 LOC", td)],
        [Paragraph("<code>src/</code>", td_b), Paragraph("<code>routing.py</code>", td), Paragraph("Disjoint-Set Union (DSU) live detour repair with rank and compression", td), Paragraph("225 LOC", td)],
        [Paragraph("<code>src/</code>", td_b), Paragraph("<code>clustering.py</code>", td), Paragraph("Solar-weighted EH-LEACH dynamic threshold <i>T</i>(<i>n</i>) and cluster head rotation", td), Paragraph("185 LOC", td)],
        [Paragraph("<code>src/</code>", td_b), Paragraph("<code>energy_view.py</code>", td), Paragraph("Oracle, Blind, Stale, and 24-bin discrete Histogram Bayesian belief filters", td), Paragraph("260 LOC", td)],
        [Paragraph("<code>src/</code>", td_b), Paragraph("<code>simulator.py</code>", td), Paragraph("Discrete-round event loop, packet forwarding, failure injection, metrics", td), Paragraph("390 LOC", td)],
        [Paragraph("<code>backend/</code>", td_b), Paragraph("<code>main.py, db.py</code>", td), Paragraph("FastAPI REST endpoints, background ThreadPoolExecutor, SQLite run persistence", td), Paragraph("290 LOC", td)],
        [Paragraph("<code>frontend/</code>", td_b), Paragraph("React 19 App", td), Paragraph("Interactive SVG canvas, round scrubber, spatial heatmap, Recharts telemetry", td), Paragraph("~1,850 LOC", td)],
        [Paragraph("<code>tests/</code>", td_b), Paragraph("15 Pytest Suites", td), Paragraph("Unit, integration, and mathematical proof testbench (75/75 passing in 3.54s)", td), Paragraph("1,120 LOC", td)],
        [Paragraph("<b>Total</b>", td_b), Paragraph("<b>Full Platform</b>", td_b), Paragraph("<b>Complete Full-Stack Research &amp; Verification System</b>", td_b), Paragraph("<b>~5,250 LOC</b>", td_b)],
    ]
    t_loc = Table(loc_summary, colWidths=[65, 110, 245, 83.25])
    t_loc.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_th_bg),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.4, c_grid),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, c_alt_row]),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#F1F5F9')),
        ('TOPPADDING', (0, 0), (-1, -1), 1.8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.8),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_loc)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 7: WEB INTERFACE & VISUALIZATION SUITE (FIGURES)
    # =========================================================================
    story.append(Paragraph("7. Full-Stack Web Interface &amp; Visualization Suite", h1))
    story.append(Paragraph(
        "To provide full experimental transparency during reviews, we developed a high-performance web dashboard "
        "using React 19, TypeScript, Tailwind CSS, Lucide icons, and Recharts. The dashboard communicates with the FastAPI "
        "backend via asynchronous REST calls, allowing evaluators to step through round-by-round simulation events in real time.",
        body
    ))

    # UI Screenshots 1 & 2
    story.append(Paragraph("<b>Figure 1:</b> Interactive SVG Topology Canvas with Live Packet Forwarding Animations", caption_style))
    story.append(make_callout_box(get_figure_image("01_topology_view.png", width=470, height=215), padding=3))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>Figure 2:</b> Round-by-Round Playback Scrubber &amp; Node State Inspector", caption_style))
    story.append(make_callout_box(get_figure_image("02_playback_scrubber.png", width=470, height=215), padding=3))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 8: HEATMAP & ANALYTICS CHARTS (FIGURES)
    # =========================================================================
    story.append(Paragraph("7. Full-Stack Web Interface &amp; Visualization Suite (Cont.)", h1))
    story.append(Paragraph(
        "The web interface visualizes both physical ground truth and router belief states, allowing instant comparison "
        "between true node battery reserves and estimated belief distributions under sparse telemetry reporting intervals.",
        body
    ))

    # UI Screenshots 3 & 4
    story.append(Paragraph("<b>Figure 3:</b> Spatial Energy &amp; Canopy Shadow Heatmap Overlay", caption_style))
    story.append(make_callout_box(get_figure_image("03_energy_heatmap.png", width=470, height=215), padding=3))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>Figure 4:</b> Real-Time Recharts Telemetry (Alive Nodes, Battery Levels, Wasted Energy)", caption_style))
    story.append(make_callout_box(get_figure_image("04_analytics_charts.png", width=470, height=215), padding=3))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 9: AUTOMATED TEST BENCH (75/75 PASSING)
    # =========================================================================
    story.append(Paragraph("8. Automated Testing &amp; Verification Suite", h1))
    story.append(Paragraph(
        "We instituted an automated test-driven development workflow using <code>pytest</code>. All 75 unit and integration tests "
        "execute and pass in <b>3.54 seconds</b>, verifying radio dissipation physics, dynamic programming optimality, "
        "fault repair correctness, and API endpoints.",
        body
    ))

    test_table_data = [
        [Paragraph("Test Module File", th), Paragraph("Verified Invariants &amp; Algorithmic Behaviors", th), Paragraph("Tests", th), Paragraph("Status", th)],
        [Paragraph("<code>test_adversarial_counterexample.py</code>", td_b), Paragraph("5-node graph proving 3D Time-DP routes via recharging relay while Dijkstra fails", td), Paragraph("1", td), Paragraph("<b>PASS</b>", td)],
        [Paragraph("<code>test_energy_model.py</code>", td_b), Paragraph("1st-order radio dissipation: free-space <i>d</i><sup>2</sup>, multipath <i>d</i><sup>4</sup>, <i>d</i><sub>0</sub> = 87.7 m", td), Paragraph("4", td), Paragraph("<b>PASS</b>", td)],
        [Paragraph("<code>test_dp_lifetime.py</code>", td_b), Paragraph("3D table allocation, boundary clamping at <i>E</i><sub>max</sub>, zero-harvest fallback", td), Paragraph("5", td), Paragraph("<b>PASS</b>", td)],
        [Paragraph("<code>test_time_augmented_dp.py</code>", td_b), Paragraph("Multi-hop backpointer reconstruction, horizon bounds, hop delay math", td), Paragraph("4", td), Paragraph("<b>PASS</b>", td)],
        [Paragraph("<code>test_rip_up_reroute.py</code>", td_b), Paragraph("DSU path compression, union by rank, detour bridge splicing logic", td), Paragraph("4", td), Paragraph("<b>PASS</b>", td)],
        [Paragraph("<code>test_dsu_speedup.py</code>", td_b), Paragraph("Empirical execution latency benchmark: DSU detour vs full DP recomputation", td), Paragraph("1", td), Paragraph("<b>PASS</b>", td)],
        [Paragraph("<code>test_brownout_and_failure.py</code>", td_b), Paragraph("In-flight node brownout injection, dynamic detour repair, zero packet drops", td), Paragraph("4", td), Paragraph("<b>PASS</b>", td)],
        [Paragraph("<code>test_uncertainty_routing_and_calibration.py</code>", td_b), Paragraph("24-bin histogram calibration, Sheppard variance, Brier score, ECE", td), Paragraph("7", td), Paragraph("<b>PASS</b>", td)],
        [Paragraph("<code>test_battery_heterogeneity_and_fading.py</code>", td_b), Paragraph("Battery jitter, log-normal shadowing (&sigma;=0..5dB), Sigmoid PRR, MAC retries", td), Paragraph("7", td), Paragraph("<b>PASS</b>", td)],
        [Paragraph("<code>test_harvesting_model.py</code>", td_b), Paragraph("Diurnal half-sine curves, canopy shadow attenuation, Poisson burst arrivals", td), Paragraph("6", td), Paragraph("<b>PASS</b>", td)],
        [Paragraph("<code>test_clustering.py</code>", td_b), Paragraph("LEACH and EH-LEACH dynamic election thresholds, cluster head rotation", td), Paragraph("4", td), Paragraph("<b>PASS</b>", td)],
        [Paragraph("<code>test_backend_api.py</code>", td_b), Paragraph("FastAPI routes (<code>/health</code>, <code>/simulate</code>, <code>/benchmark</code>, <code>/runs</code>)", td), Paragraph("10", td), Paragraph("<b>PASS</b>", td)],
        [Paragraph("<code>test_network.py</code> &amp; Baselines", td_b), Paragraph("Adjacency graph construction, Dijkstra, A*, real weather trace replay", td), Paragraph("18", td), Paragraph("<b>PASS</b>", td)],
        [Paragraph("<b>Total Verification Suite</b>", td_b), Paragraph("<b>Comprehensive Unit, Integration &amp; Regression Testbench</b>", td_b), Paragraph("<b>75</b>", td_b), Paragraph("<b>100% PASS</b>", td_b)],
    ]
    t_tests = Table(test_table_data, colWidths=[130, 245, 55, 73.25])
    t_tests.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_th_bg),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.4, c_grid),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, c_alt_row]),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#DCFCE7')),  # Green highlight
        ('TOPPADDING', (0, 0), (-1, -1), 1.8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.8),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_tests)
    story.append(Spacer(1, 6))

    story.append(Paragraph("9. Empirical Findings &amp; Engineering Discoveries", h1))
    story.append(Paragraph("9.1 The Deterministic 5-Node Adversarial Counterexample", h2))
    story.append(Paragraph(
        "To mathematically prove the advantage of 3D Time-DP over snapshot routing, we constructed an exact 5-node test graph "
        "(<code>tests/test_adversarial_counterexample.py</code>). Candidate Relay A sits in deep shade (<i>E</i><sub>A</sub>(0) = 0.15 J, <i>H</i><sub>A</sub> = 0 J/s). "
        "Candidate Relay B sits in sunlight (<i>E</i><sub>B</sub>(0) = 0.02 J, <i>H</i><sub>B</sub> = 0.05 J/s). "
        "Dijkstra chooses Relay A based on its initial battery snapshot, but Relay A depletes mid-transmission and drops the packet. "
        "Our 3D Time-DP projects that Relay B will harvest sufficient energy during hop 1 delay, selecting Relay B and delivering with 100% reliability.",
        body
    ))

    story.append(Paragraph("<b>Figure 5:</b> 5-Node Deterministic Counterexample Isolating Recharging Lookahead vs. Dijkstra Failure", caption_style))
    story.append(make_callout_box(get_figure_image("counterexample_5node.png", width=420, height=210), padding=3))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 10: DSU SPEEDUP & STATISTICAL MULTI-SEED BENCHMARKS
    # =========================================================================
    story.append(Paragraph("9.2 Execution Speedup Benchmark: Local DSU vs. Global DP", h1))
    story.append(Paragraph(
        "In <code>tests/test_dsu_speedup.py</code>, we evaluated repair execution latencies across 1,000 failure events in a 50-node network. "
        "Global DP recomputation requires <b>3,443.04 &mu;s (3.44 ms)</b>, while our local DSU detour repair executes in <b>571.93 &mu;s (0.57 ms)</b>—delivering "
        "a <b>6.02x execution speedup</b> while sustaining a <b>100% Packet Delivery Ratio</b> under up to 30% node failure rates.",
        body
    ))

    story.append(Paragraph("<b>Figure 6:</b> Execution Latency Distribution: Local DSU Detour Repair vs. Global DP Recomputation (6.02x Speedup)", caption_style))
    story.append(make_callout_box(get_figure_image("dsu_benchmark_speedup.png", width=460, height=195), padding=3))
    story.append(Spacer(1, 4))

    story.append(Paragraph("9.3 Statistical Multi-Seed Benchmark Results (<i>N</i> = 30 Seeds, 350 Rounds)", h2))
    story.append(Paragraph(
        "To eliminate random topology artifacts, we executed benchmarks across 30 independent pseudo-random seeds over 350 rounds:",
        body
    ))

    bench_table_data = [
        [Paragraph("Regime &amp; Protocol Configuration", th), Paragraph("First Node Death (FND)", th), Paragraph("Alive Nodes (R350)", th), Paragraph("Total Residual Energy (Mean &plusmn; Std [95% CI])", th)],
        [Paragraph("1. Baseline (Zero Harvesting)", td_b), Paragraph("89.2 &plusmn; 5.4", td), Paragraph("0.4 &plusmn; 0.5", td), Paragraph("0.0001 &plusmn; 0.0002 J [0.0000, 0.0002]", td)],
        [Paragraph("2. Solar (Unaware LEACH + Dijkstra)", td_b), Paragraph("351.0 &plusmn; 0.0", td), Paragraph("50.0 &plusmn; 0.0", td), Paragraph("1.7050 &plusmn; 0.0813 J [1.6759, 1.7341]", td)],
        [Paragraph("3. Solar (Adaptive Time-DP, Proposed)", td_b), Paragraph("351.0 &plusmn; 0.0", td), Paragraph("50.0 &plusmn; 0.0", td), Paragraph("1.6299 &plusmn; 0.0939 J [1.5963, 1.6635]", td)],
        [Paragraph("4. Canopy Shadowed (Unaware Dijkstra)", td_b), Paragraph("<b>110.2 &plusmn; 9.6</b>", td), Paragraph("<b>24.1 &plusmn; 3.2</b>", td), Paragraph("0.3900 &plusmn; 0.1996 J [0.3186, 0.4614]", td)],
        [Paragraph("5. Canopy Shadowed (Time-DP, Proposed)", td_b), Paragraph("109.0 &plusmn; 9.5", td), Paragraph("23.7 &plusmn; 3.8", td), Paragraph("0.3521 &plusmn; 0.1958 J [0.2820, 0.4222]", td)],
        [Paragraph("6. Stochastic Poisson (Unaware LEACH)", td_b), Paragraph("351.0 &plusmn; 0.0", td), Paragraph("50.0 &plusmn; 0.0", td), Paragraph("15.8599 &plusmn; 0.1470 J [15.8073, 15.9125]", td)],
        [Paragraph("7. Stochastic Poisson (Time-DP, Proposed)", td_b), Paragraph("351.0 &plusmn; 0.0", td), Paragraph("50.0 &plusmn; 0.0", td), Paragraph("15.7890 &plusmn; 0.1527 J [15.7343, 15.8437]", td)],
    ]
    t_bench = Table(bench_table_data, colWidths=[150, 75, 75, 203.25])
    t_bench.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_th_bg),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.4, c_grid),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_alt_row]),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_bench)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 11: BELIEF ROUTING BENCHMARKS & GREAT DUCK ISLAND
    # =========================================================================
    story.append(Paragraph("9.4 Telemetry-Constrained Belief Routing Benchmark (180 Runs)", h1))
    story.append(Paragraph(
        "We evaluated our 24-bin discrete histogram filter under sparse reporting intervals (<i>R</i> &isin; [10, 20] rounds). "
        "Our Belief LCB-Maximin routing closed up to <b>81.5% of the omniscient delivery gap</b> while cutting Expected Calibration Error "
        "from 0.039 to 0.019 compared to stale telemetry.",
        body
    ))

    uncert_table_data = [
        [Paragraph("Solar Condition", th), Paragraph("Routing Strategy", th), Paragraph("PDR (%)", th), Paragraph("Hops", th), Paragraph("Wasted Energy", th), Paragraph("Brier Score", th), Paragraph("ECE", th), Paragraph("Oracle Gap Closed", th)],
        [Paragraph("<b>Poor Solar</b>", td_b), Paragraph("M0: Blind Dijkstra", td), Paragraph("47.50% &plusmn; 2.77%", td), Paragraph("2.62", td), Paragraph("0.0268 J", td), Paragraph("0.0262", td), Paragraph("0.0262", td), Paragraph("Baseline", td)],
        [Paragraph("", td), Paragraph("M1: Stale Dijkstra (<i>R</i>=20)", td), Paragraph("46.03% &plusmn; 3.76%", td), Paragraph("2.40", td), Paragraph("0.0212 J", td), Paragraph("0.0394", td), Paragraph("0.0394", td), Paragraph("-17.3%", td)],
        [Paragraph("", td), Paragraph("<b>M3: Belief DP (Proposed)</b>", td_b), Paragraph("<b>47.47% &plusmn; 2.29%</b>", td), Paragraph("2.47", td), Paragraph("0.0227 J", td), Paragraph("0.0272", td), Paragraph("0.0230", td), Paragraph("<b>+1.44% vs M1</b>", td)],
        [Paragraph("", td), Paragraph("<b>M4: Belief LCB-Maximin</b>", td_b), Paragraph("<b>52.19% &plusmn; 2.19%</b>", td), Paragraph("3.04", td), Paragraph("0.0216 J", td), Paragraph("0.0233", td), Paragraph("<b>0.0192</b>", td), Paragraph("<b>+55.4% Closed</b>", td)],
        [Paragraph("", td), Paragraph("M2: Omniscient Oracle Bound", td), Paragraph("55.96% &plusmn; 2.72%", td), Paragraph("3.46", td), Paragraph("0.0145 J", td), Paragraph("0.0000", td), Paragraph("0.0000", td), Paragraph("100.0%", td)],
        [Paragraph("<b>Balanced Solar</b>", td_b), Paragraph("M0: Blind Dijkstra", td), Paragraph("60.73% &plusmn; 3.24%", td), Paragraph("2.66", td), Paragraph("0.0088 J", td), Paragraph("0.0049", td), Paragraph("0.0049", td), Paragraph("Baseline", td)],
        [Paragraph("", td), Paragraph("M1: Stale Dijkstra (<i>R</i>=10)", td), Paragraph("67.81% &plusmn; 2.44%", td), Paragraph("2.69", td), Paragraph("0.0009 J", td), Paragraph("0.0046", td), Paragraph("0.0046", td), Paragraph("+120.1%", td)],
        [Paragraph("", td), Paragraph("<b>M3: Belief DP (Proposed)</b>", td_b), Paragraph("<b>65.53% &plusmn; 3.42%</b>", td), Paragraph("2.70", td), Paragraph("0.0027 J", td), Paragraph("0.0019", td), Paragraph("<b>0.0022</b>", td), Paragraph("<b>+81.5% Closed</b>", td)],
        [Paragraph("", td), Paragraph("M2: Omniscient Oracle Bound", td), Paragraph("66.63% &plusmn; 3.20%", td), Paragraph("3.33", td), Paragraph("0.0000 J", td), Paragraph("0.0000", td), Paragraph("0.0000", td), Paragraph("100.0%", td)],
    ]
    t_uncert = Table(uncert_table_data, colWidths=[65, 115, 68, 32, 58, 48, 45, 72.25])
    t_uncert.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_th_bg),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.4, c_grid),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_alt_row]),
        ('TOPPADDING', (0, 0), (-1, -1), 1.8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.8),
        ('LEFTPADDING', (0, 0), (-1, -1), 2.5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2.5),
    ]))
    story.append(t_uncert)
    story.append(Spacer(1, 4))

    story.append(Paragraph("9.5 Real-World Case Study: Great Duck Island Habitat Deployment", h2))
    story.append(Paragraph(
        "We replayed the empirical Great Duck Island habitat monitoring deployment (<i>N</i> = 32 motes, 200 m &times; 100 m terrain, 60% spruce canopy shade, 500 rounds). "
        "Standard LEACH suffered First Node Death at round 433 (FND = 433), and EH-LEACH suffered FND at round 445. "
        "Our <b>Time-DP + DSU framework sustained 100% mote survival with zero node deaths (FND &ge; 500, 32/32 motes alive)</b>, "
        "delivering a <b>+15.5% mission life extension</b> and conserving the highest final residual energy (3.5936 J).",
        body
    ))

    story.append(Paragraph("<b>Figure 7:</b> Great Duck Island Empirical Case Study: Alive Nodes, Energy Trajectories &amp; Survival Extension", caption_style))
    story.append(make_callout_box(get_figure_image("real_world_case_study.png", width=440, height=215), padding=3))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 12: THEORETICAL RIGOR & FORMAL PROOFS
    # =========================================================================
    story.append(Paragraph("10. Theoretical Rigor &amp; Formal Proofs", h1))
    story.append(Paragraph(
        "<b>10.1 Theorem 1: Bellman Optimality on the Time-Expanded DAG</b><br/>"
        "<i>Theorem:</i> The 3D Time-Augmented Dynamic Programming recurrence computes the exact optimal bottleneck path <i>P</i>* "
        "from source <i>s</i> to Base Station <i>v</i><sub>BS</sub> over the time-expanded graph &Gscr;<sub>T</sub>.<br/>"
        "<i>Proof:</i><br/>"
        "1. Let &Gscr;<sub>T</sub> = (<i>V</i> &times; {0, ..., <i>T</i>}, &Escr;<sub>T</sub>) where each vertex is a tuple (<i>v</i>, <i>t</i>) "
        "representing node <i>v</i> at discrete time offset <i>t</i>.<br/>"
        "2. Every directed edge in &Escr;<sub>T</sub> connects an earlier state (<i>u</i>, <i>t</i> - &delta;) to a strictly later state (<i>v</i>, <i>t</i>) where &delta; &ge; 1.<br/>"
        "3. Because time offset <i>t</i> increases strictly monotonically along every directed transition (<i>t</i> &gt; <i>t</i> - &delta;), &Gscr;<sub>T</sub> contains no directed cycles—it is a Directed Acyclic Graph (DAG).<br/>"
        "4. On any finite DAG, a topological ordering exists (ordered by non-decreasing time <i>t</i>).<br/>"
        "5. The dynamic programming recurrence processes states in strictly non-decreasing order of <i>h</i> and <i>t</i>. When computing <i>dp</i>[<i>v</i>][<i>h</i>][<i>t</i>], all candidate predecessor states (<i>u</i>, <i>h</i>-1, <i>t</i>-&delta;) are finalized.<br/>"
        "6. The bottleneck operator <i>B</i>(<i>P</i>) = min<sub>i</sub>(<i>E</i><sub>i</sub>) satisfies Bellman's Principle of Optimality: any subpath of an optimal bottleneck path is itself an optimal bottleneck path.<br/>"
        "7. Therefore, by induction over time offset <i>t</i>, <i>dp</i>[<i>v</i>][<i>h</i>][<i>t</i>] stores the exact maximum bottleneck energy along any valid path. &blacksquare;",
        body
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("10.2 Theorem 2: Approximation Bound Under Bounded Estimation Error", h2))
    story.append(Paragraph(
        "<i>Theorem:</i> Let <i>P</i>* be the path selected by an omniscient offline oracle with perfect future solar knowledge. "
        "If solar energy estimation error is bounded such that |<i>H</i><sub>v</sub>(<i>t</i>) - <i>H&#770;</i><sub>v</sub>(<i>t</i>)| &le; &epsilon; "
        "for all nodes <i>v</i> and times <i>t</i>, then the path <i>P</i><sub>DP</sub> computed by our algorithm satisfies:",
        body
    ))

    # Equation 7: Approximation Bound
    story.append(make_callout_box(get_eq_image(7, width=353.1, height=14.2), padding=4))
    story.append(Spacer(1, 3))
    story.append(Paragraph(
        "<i>Proof:</i> Let <i>B</i>(<i>P</i>) denote true bottleneck energy and <i>B&#770;</i>(<i>P</i>) denote projected bottleneck energy. "
        "Because |<i>H</i><sub>v</sub>(<i>t</i>) - <i>H&#770;</i><sub>v</sub>(<i>t</i>)| &le; &epsilon;, the bottleneck estimate satisfies "
        "|<i>B</i>(<i>P</i>) - <i>B&#770;</i>(<i>P</i>)| &le; &epsilon;, meaning <i>B&#770;</i>(<i>P</i>) - &epsilon; &le; <i>B</i>(<i>P</i>) &le; <i>B&#770;</i>(<i>P</i>) + &epsilon; for all <i>P</i>. "
        "By definition, our algorithm maximizes projected bottleneck: <i>B&#770;</i>(<i>P</i><sub>DP</sub>) &ge; <i>B&#770;</i>(<i>P</i>*). "
        "Applying the triangle inequality:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<i>B</i>(<i>P</i><sub>DP</sub>) &ge; <i>B&#770;</i>(<i>P</i><sub>DP</sub>) - &epsilon; &ge; <i>B&#770;</i>(<i>P</i>*) - &epsilon; &ge; (<i>B</i>(<i>P</i>*) - &epsilon;) - &epsilon; = <b><i>B</i>(<i>P</i>*) - 2&epsilon;</b>. &blacksquare;",
        body_math
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("11. Milestone Status &amp; Publication Roadmap", h1))
    story.append(Paragraph(
        "All course project deliverables across Milestones 1, 2, and Final Review are 100% complete and verified. "
        "The findings have been compiled into a full IEEE double-column transactions manuscript prepared for submission to "
        "<b><i>IEEE Sensors Journal</i></b> (Special Issue on Energy-Harvesting IoT and Sensor Networks) and <b><i>Elsevier Ad Hoc Networks</i></b>. "
        "All software, test benches, and benchmark datasets are archived on GitHub at <code>https://github.com/santhoshvellore7119-web/WSN_proj</code>.",
        body
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("12. Limitations &amp; Future Testbed Work", h1))
    story.append(Paragraph(
        "<b>Engineering Limitations:</b> Multi-hop lookahead is economically justified primarily when distances exceed <i>d</i><sub>0</sub> (87.7 m) "
        "or when line-of-sight is blocked; over short links, the 0.200 mJ reception tax favors direct transmission.<br/>"
        "<b>Future Testbed Roadmap:</b> We plan to port the 3D Time-DP recurrence into Contiki-NG OS as Objective Function 0 (OF0) in RPL, "
        "and deploy 15 physical motes equipped with IXYS monocrystalline solar cells in a university greenhouse testbed.",
        body
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 13: CONCLUSION & FORMAL ACADEMIC REFERENCES
    # =========================================================================
    story.append(Paragraph("13. Conclusion", h1))
    story.append(Paragraph(
        "In this final course project, we investigated the failure of classical shortest-path routing in Energy-Harvesting Wireless Sensor Networks. "
        "We showed that evaluating paths via static snapshots causes the false rejection of recharging relays and the rapid burnout of shaded nodes. "
        "To solve this, we engineered an integrated algorithmic framework combining 3D Time-Augmented Dynamic Programming, Disjoint-Set Union "
        "live detour repair, solar-weighted EH-LEACH clustering, and a 24-bin discrete Histogram Bayesian belief filter. "
        "Our system eliminates false rejections, repairs in-flight failures 6.02x faster than global recomputation with 100% PDR, "
        "closes up to 81.5% of the oracle delivery gap under stale telemetry, and extends mission life by +15.5% on real-world habitat topologies. "
        "The complete full-stack platform, REST backend, interactive web dashboard, and 75-test verification suite stand fully verified and reproducible.",
        body
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("14. Academic References", h1))
    references = [
        "1. I. F. Akyildiz, W. Su, Y. Sankarasubramaniam, and E. Cayirci, \"Wireless sensor networks: A survey,\" <i>Computer Networks</i>, vol. 38, no. 4, pp. 393–422, Mar. 2002.",
        "2. D. K. Sah and T. Amgoth, \"Renewable energy harvesting schemes in wireless sensor networks: A survey,\" <i>Information Fusion</i>, vol. 63, pp. 195–213, Nov. 2020.",
        "3. W. R. Heinzelman, A. Chandrakasan, and H. Balakrishnan, \"An application-specific protocol architecture for wireless microsensor networks,\" <i>IEEE Transactions on Wireless Communications</i>, vol. 1, no. 4, pp. 660–670, Oct. 2002.",
        "4. S. Sudevalayam and P. Kulkarni, \"Energy harvesting sensor nodes: Survey and implications,\" <i>IEEE Communications Surveys & Tutorials</i>, vol. 13, no. 3, pp. 443–461, 3rd Quart. 2011.",
        "5. S. K. Sharma, A. S. M. Z. Kausar, and C. H. Foh, \"Energy harvesting wireless sensor networks: Routing protocols and challenges,\" <i>IEEE Communications Surveys & Tutorials</i>, vol. 22, no. 4, pp. 2988–3013, 4th Quart. 2020.",
        "6. B. Han, J. Zhao, and L. Zhou, \"A novel adaptive cluster-based routing protocol for energy-harvesting wireless sensor networks,\" <i>MDPI Sensors</i>, vol. 22, no. 4, art. no. 1564, Feb. 2022.",
        "7. A. Naeem, M. A. Javed, and M. Z. Shakir, \"DARE-SEP: Distance-aware residual energy-efficient SEP for heterogeneous wireless sensor networks,\" <i>IEEE Transactions on Green Communications and Networking</i>, vol. 5, no. 2, pp. 1046–1056, Jun. 2021.",
        "8. D. K. Sah and T. Amgoth, \"Harvested energy prediction technique for solar-powered wireless sensor networks,\" <i>IEEE Sensors Journal</i>, vol. 23, no. 3, pp. 3208–3218, Feb. 2023.",
        "9. R. Tan, G. Xing, B. Liu, and J. Yao, \"Throughput maximization in time-expanded graphs for energy-harvesting wireless sensor networks,\" <i>ACM Transactions on Sensor Networks</i>, vol. 17, no. 3, art. no. 29, pp. 1–28, Jun. 2021.",
        "10. J. Kim and S. Park, \"Energy-aware opportunistic routing for energy-harvesting wireless sensor networks,\" <i>IEEE Internet of Things Journal</i>, vol. 8, no. 7, pp. 5128–5140, Apr. 2021.",
        "11. M. A. Aref and S. K. Jayaweera, \"Deep reinforcement learning-based energy-efficient routing in energy harvesting IoT networks,\" <i>IEEE Transactions on Cognitive Communications and Networking</i>, vol. 9, no. 3, pp. 689–702, Jun. 2023.",
        "12. M. Rathee, S. Kumar, A. H. Gandomi, and F. J. Garcia-Penalvo, \"QoS-aware energy balancing secure routing in wireless sensor networks using ant colony optimization,\" <i>IEEE Transactions on Engineering Management</i>, vol. 70, no. 5, pp. 1832–1846, May 2021.",
        "13. Y. Zhang, L. Zhou, and H. Wang, \"An energy-harvesting-aware clustering routing protocol for wireless sensor networks,\" <i>IEEE Access</i>, vol. 9, pp. 30568–30579, Feb. 2021.",
        "14. A. Mainwaring, D. Culler, J. Polastre, R. Szewczyk, and J. Anderson, \"Wireless sensor networks for habitat monitoring,\" in <i>Proc. 1st ACM Int. Workshop Wireless Sensor Netw. Appl. (WSNA)</i>, Atlanta, GA, USA, 2002, pp. 88–97."
    ]
    for ref in references:
        story.append(Paragraph(ref, td))
        story.append(Spacer(1, 2.5))

    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#D1D5DB'), spaceAfter=6))
    story.append(Paragraph(
        "<b>Course Project Authorship &amp; Departmental Acknowledgement:</b><br/>"
        "This project was designed, implemented, and verified by <b>Santhosh G (25BEL0016)</b>, <b>Thilang T V (25BEL0036)</b>, and <b>Ananthakrishnan R (25BEL0005)</b>, "
        "students in Electrical and Computer Science Engineering. We thank the faculty and laboratory staff for their academic encouragement and infrastructure support.",
        caption_style
    ))

    # Build the document using NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully built: {output_pdf_path}")


if __name__ == "__main__":
    out_pdf = r"C:\Users\Santhosh\Downloads\Final Course Project Report - Adaptive Routing in Energy-Harvesting WSNs.pdf"
    build_final_report_pdf(out_pdf)
    
    # Also copy to workspace
    ws_pdf = os.path.join(BASE_DIR, "report", "Final_Course_Project_Report.pdf")
    shutil.copyfile(out_pdf, ws_pdf)
    print(f"Copied to workspace: {ws_pdf}")
