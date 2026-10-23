import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ==============================================================================
# COLOR PALETTE & DESIGN SYSTEM
# ==============================================================================
C_NAVY_DARK = RGBColor(15, 23, 42)       # #0F172A (Primary Dark)
C_NAVY_MED = RGBColor(30, 41, 59)        # #1E293B (Card headers)
C_SLATE_MUTED = RGBColor(100, 116, 139)  # #64748B (Secondary / Muted text)
C_CARD_BG = RGBColor(248, 250, 252)      # #F8FAFC (Card background)
C_CARD_BORDER = RGBColor(226, 232, 240)  # #E2E8F0 (Subtle border)
C_WHITE = RGBColor(255, 255, 255)
C_TEAL = RGBColor(13, 148, 136)          # #0D9488 (Solar, Success, Accent)
C_TEAL_LIGHT = RGBColor(240, 253, 250)   # #F0FDFA (Teal tint bg)
C_BLUE = RGBColor(37, 99, 235)           # #2563EB (Tech / Algorithm)
C_BLUE_LIGHT = RGBColor(239, 246, 255)   # #EFF6FF (Blue tint bg)
C_AMBER = RGBColor(217, 119, 6)          # #D97706 (Warning, Draining)
C_RED = RGBColor(220, 38, 38)            # #DC2626 (Failure, Brownout)
C_CODE_BG = RGBColor(241, 245, 249)      # #F1F5F9 (Code block bg)
C_DARK_TERMINAL = RGBColor(17, 24, 39)   # #111827 (Terminal black)

FONT_HEADING = "Calibri"
FONT_BODY = "Calibri"
FONT_CODE = "Consolas"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
EXPLAINER_DIR = os.path.join(BASE_DIR, "report", "explainer_images")
EQ_DIR = os.path.join(BASE_DIR, "rep2_eq_pngs")

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

def add_header(slide, title, category, slide_num, total_slides=21):
    """Draws standardized corporate header, category pill badge, and running footer."""
    # Top Category Pill Badge
    pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.35), Inches(3.4), Inches(0.3))
    pill.fill.solid()
    pill.fill.fore_color.rgb = C_TEAL_LIGHT
    pill.line.color.rgb = C_TEAL
    pill.line.width = Pt(0.75)
    tf = pill.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = category.upper()
    p.font.name = FONT_HEADING
    p.font.size = Pt(8.5)
    p.font.bold = True
    p.font.color.rgb = C_TEAL
    p.alignment = PP_ALIGN.CENTER

    # Main Title
    tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.68), Inches(11.7), Inches(0.65))
    tf_t = tb.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = title
    p_t.font.name = FONT_HEADING
    p_t.font.size = Pt(21)
    p_t.font.bold = True
    p_t.font.color.rgb = C_NAVY_DARK

    # Top separator line
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.36), Inches(11.733), Inches(0.015))
    line.fill.solid()
    line.fill.fore_color.rgb = C_CARD_BORDER
    line.line.fill.background()

    # Running Footer on slide
    f_tb = slide.shapes.add_textbox(Inches(0.8), Inches(7.0), Inches(10.2), Inches(0.35))
    f_tf = f_tb.text_frame
    f_p = f_tf.paragraphs[0]
    f_p.text = "Adaptive Routing in EH-WSNs  |  Santhosh G (25BEL0016), Thilang T V (25BEL0036), Ananthakrishnan R (25BEL0005)"
    f_p.font.name = FONT_BODY
    f_p.font.size = Pt(8.5)
    f_p.font.color.rgb = C_SLATE_MUTED

    # Slide Number
    num_tb = slide.shapes.add_textbox(Inches(11.3), Inches(7.0), Inches(1.2), Inches(0.35))
    num_tf = num_tb.text_frame
    num_p = num_tf.paragraphs[0]
    num_p.text = f"{slide_num} / {total_slides}"
    num_p.font.name = FONT_BODY
    num_p.font.size = Pt(8.5)
    num_p.font.bold = True
    num_p.font.color.rgb = C_SLATE_MUTED
    num_p.alignment = PP_ALIGN.RIGHT

def add_card(slide, left, top, width, height, bg_color=C_CARD_BG, border_color=C_CARD_BORDER):
    """Draws a rounded card container for content grouping."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1)
    return card

def add_speaker_notes(slide, notes_text):
    """Attaches complete speaker notes to the slide."""
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = notes_text.strip()

def add_bullet(tf, bold_prefix, text, pt_size=11, space_after=6, text_color=C_NAVY_DARK):
    """Adds a formatted bullet point with bold lead-in."""
    p = tf.add_paragraph()
    p.space_after = Pt(space_after)
    if bold_prefix:
        r_bold = p.add_run()
        r_bold.text = bold_prefix + " "
        r_bold.font.name = FONT_BODY
        r_bold.font.size = Pt(pt_size)
        r_bold.font.bold = True
        r_bold.font.color.rgb = text_color
    r_text = p.add_run()
    r_text.text = text
    r_text.font.name = FONT_BODY
    r_text.font.size = Pt(pt_size)
    r_text.font.color.rgb = text_color

# ==============================================================================
# SLIDE 1: TITLE SLIDE (Dark Navy Premium Academic Theme)
# ==============================================================================
s1 = prs.slides.add_slide(blank_layout)
bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
bg1.fill.solid()
bg1.fill.fore_color.rgb = C_NAVY_DARK
bg1.line.fill.background()

# Title badge
t_pill = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(1.0), Inches(4.2), Inches(0.4))
t_pill.fill.solid()
t_pill.fill.fore_color.rgb = RGBColor(17, 34, 64)
t_pill.line.color.rgb = C_TEAL
t_pill.line.width = Pt(1)
t_ptf = t_pill.text_frame
p = t_ptf.paragraphs[0]
p.text = "CAPSTONE FINAL DEFENSE & PROJECT REVIEW"
p.font.name = FONT_HEADING
p.font.size = Pt(10)
p.font.bold = True
p.font.color.rgb = C_TEAL
p.alignment = PP_ALIGN.CENTER

# Title text
tb = s1.shapes.add_textbox(Inches(1.0), Inches(1.6), Inches(11.333), Inches(2.2))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "Adaptive Routing in Energy-Harvesting\nWireless Sensor Networks"
p.font.name = FONT_HEADING
p.font.size = Pt(36)
p.font.bold = True
p.font.color.rgb = C_WHITE

p2 = tf.add_paragraph()
p2.text = "A 3D Lookahead Dynamic Programming, Live DSU Detour Recovery, and Full-Stack Verification Framework"
p2.font.name = FONT_BODY
p2.font.size = Pt(15)
p2.font.color.rgb = RGBColor(148, 163, 184)
p2.space_before = Pt(8)

# Team Member Cards
members = [
    ("Santhosh G", "25BEL0016", "3D Time-Augmented DP ($dp[v][h][t]$)\n24-Bin Belief Filter & Sim Core"),
    ("Thilang T V", "25BEL0036", "Disjoint-Set Union (DSU) Live Detours\nFastAPI REST Backend & React 19 UI"),
    ("Ananthakrishnan R", "25BEL0005", "Heinzelman 1st-Order Radio Physics\nSolar Harvesting Profiles & Pytest Suite")
]

card_w = Inches(3.55)
card_h = Inches(1.8)
start_x = Inches(1.0)
card_gap = Inches(0.34)
top_y = Inches(4.3)

for i, (name, reg, role) in enumerate(members):
    c_x = start_x + i * (card_w + card_gap)
    c = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, c_x, top_y, card_w, card_h)
    c.fill.solid()
    c.fill.fore_color.rgb = RGBColor(30, 41, 59)
    c.line.color.rgb = RGBColor(51, 65, 85)
    c.line.width = Pt(1)
    ctf = c.text_frame
    ctf.word_wrap = True
    ctf.margin_left = Inches(0.2)
    ctf.margin_top = Inches(0.2)
    
    cp1 = ctf.paragraphs[0]
    cp1.text = name
    cp1.font.name = FONT_HEADING
    cp1.font.size = Pt(14)
    cp1.font.bold = True
    cp1.font.color.rgb = C_WHITE
    
    cp2 = ctf.add_paragraph()
    cp2.text = f"Reg No: {reg}"
    cp2.font.name = FONT_BODY
    cp2.font.size = Pt(11)
    cp2.font.bold = True
    cp2.font.color.rgb = C_TEAL
    cp2.space_after = Pt(4)
    
    cp3 = ctf.add_paragraph()
    cp3.text = role
    cp3.font.name = FONT_BODY
    cp3.font.size = Pt(9.5)
    cp3.font.color.rgb = RGBColor(203, 213, 225)

# Institution Banner
b_tb = s1.shapes.add_textbox(Inches(1.0), Inches(6.5), Inches(11.333), Inches(0.5))
b_tf = b_tb.text_frame
b_p = b_tf.paragraphs[0]
b_p.text = "Department of Electrical & Computer Science Engineering  |  Vellore Institute of Technology (VIT), Vellore  |  GitHub: WSN_proj"
b_p.font.name = FONT_BODY
b_p.font.size = Pt(10)
b_p.font.color.rgb = RGBColor(148, 163, 184)

add_speaker_notes(s1, """
Good morning, respected members of the panel. 
Today, my teammates Thilang, Ananthakrishnan, and I, Santhosh, are presenting our Final Capstone Defense on 'Adaptive Routing in Energy-Harvesting Wireless Sensor Networks'.
In classical sensor networks, battery energy is strictly non-increasing. But when nodes harvest solar energy, that basic rule breaks down.
Our project solves this using fundamental Data Structures and Algorithms: a polynomial 3D Time-Augmented Dynamic Programming algorithm that looks ahead in time, an instant Disjoint-Set Union detour recovery mechanism, and a full-stack simulation and verification platform.
We will now walk you through the problem, the mathematics, the codebase, and our empirical findings.
""")

# ==============================================================================
# SLIDE 2: PROJECT OVERVIEW & EXECUTIVE SUMMARY
# ==============================================================================
s2 = prs.slides.add_slide(blank_layout)
add_header(s2, "Project Overview: Bridging Classical DSA & Energy Harvesting", "Executive Summary", 2)

# Left Column: The Core Challenge
add_card(s2, Inches(0.8), Inches(1.6), Inches(5.7), Inches(4.3))
tb = s2.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(5.3), Inches(4.0))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "The Fundamental Challenge in EH-WSNs"
p.font.name = FONT_HEADING
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY_DARK
p.space_after = Pt(8)

add_bullet(tf, "Monotonic vs Non-Monotonic Energy:", "Classical WSNs assume battery only drains (monotonic non-increasing). Solar nodes recharge dynamically during daylight hours.", 11)
add_bullet(tf, "The Transit Recharge Window:", "Data packets take measurable time (hops delta-t) to travel across a network. A relay with 5% battery right now may recharge to 40% before the packet arrives.", 11)
add_bullet(tf, "Why Machine Learning Fails Here:", "Heavy Deep Q-Networks and reinforcement learning require >1 MB memory and heavy matrix operations. 32-bit Cortex-M / MicaZ sensor motes possess only 4–10 KB RAM.", 11)
add_bullet(tf, "The Core Research Question:", "Can we achieve lookahead recharge awareness and live fault recovery using strictly polynomial Data Structures & Algorithms within a 48 KB RAM footprint?", 11)

# Right Column: Our 4-Pillar Solution
add_card(s2, Inches(6.833), Inches(1.6), Inches(5.7), Inches(4.3))
tb = s2.shapes.add_textbox(Inches(7.033), Inches(1.75), Inches(5.3), Inches(4.0))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "Our Four-Pillar Algorithmic & Software Solution"
p.font.name = FONT_HEADING
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY_DARK
p.space_after = Pt(8)

add_bullet(tf, "1. 3D Time-Augmented DP:", "Evaluates states dp[v][h][t] on a time-expanded DAG in O(|E|HT) time, mathematically eliminating false path rejections.", 11)
add_bullet(tf, "2. DSU Live Detour Recovery:", "Union-Find with path compression splices replacement relays in 0.85 ms (6.02x speedup) during mid-flight brownouts.", 11)
add_bullet(tf, "3. Solar-Weighted EH-LEACH:", "Dynamic cluster threshold T(n) boosts sunlit node elections by 2.4x, shielding shaded nodes from early burnout.", 11)
add_bullet(tf, "4. Full-Stack Research Platform:", "Headless simulator engine coupled to FastAPI, SQLite, and a React 19 interactive SVG canvas with round-by-round time scrubbing.", 11)

# Bottom Metrics Ribbon
ribbon = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.05), Inches(11.733), Inches(0.8))
ribbon.fill.solid()
ribbon.fill.fore_color.rgb = C_TEAL_LIGHT
ribbon.line.color.rgb = C_TEAL
ribbon.line.width = Pt(1)
rtf = ribbon.text_frame
rtf.word_wrap = True
rp = rtf.paragraphs[0]
rp.text = "KEY DELIVERABLES:  68/68 Pytest Unit Tests Passing (100%)  |  6.02x DSU Detour Speedup  |  < 5.2 ms DP Latency  |  < 48 KB RAM Table"
rp.font.name = FONT_HEADING
rp.font.size = Pt(11)
rp.font.bold = True
rp.font.color.rgb = C_TEAL
rp.alignment = PP_ALIGN.CENTER

add_speaker_notes(s2, """
On this slide, we present the executive summary of our project. 
The central insight is simple: in classical sensor networks powered by AA batteries, energy only goes down. Algorithms like Dijkstra or LEACH assume a frozen snapshot of residual energy. 
However, in solar-powered networks, a relay node with 5% battery at round start can recharge back to full within minutes once sunlight hits its panel. If we use standard Dijkstra, it rejects that node and takes a wasteful 4-hop detour.
To solve this without heavy neural networks that would overwhelm a sensor node's microcontroller, we designed four DSA contributions: 3D Time-Augmented DP, DSU live detours, EH-LEACH, and a full-stack dashboard. All 68 tests pass with 100% success rate.
""")

# ==============================================================================
# SLIDE 3: PROBLEM STATEMENT & CLASSICAL ROUTING PITFALLS
# ==============================================================================
s3 = prs.slides.add_slide(blank_layout)
add_header(s3, "Problem Statement: Why Classical Routing Fails in EH-WSNs", "Theoretical Motivation", 3)

# 3 Pitfall Cards
pitfalls = [
    ("The Monotonic Invariant Fallacy", C_NAVY_DARK, [
        ("The Classical Assumption:", "E_v(t2) <= E_v(t1) for all t2 >= t1. Energy never increases."),
        ("The Physical Reality:", "Ambient solar, thermal, or RF harvesting creates non-monotonic energy curves. Energy fluctuates continuously."),
        ("The Consequence:", "Static snapshot routing protocols make decisions on outdated past data, ignoring future harvest refilling.")
    ]),
    ("Pitfall 1: The False Rejection Flaw", C_RED, [
        ("Scenario:", "Relay B has only 5% battery at t = 0. Source S needs to transmit data 2 hops away."),
        ("Dijkstra's Choice:", "Dijkstra sees 5% residual battery at t = 0, labels Relay B as 'critically weak', rejects it, and routes via a long 4-hop path."),
        ("The Failure:", "By hop 2 (t = 2), solar recharge restored Relay B to 40%! Dijkstra wasted bandwidth and energy on a false detour.")
    ]),
    ("Pitfall 2: The Shaded Burnout Flaw", C_AMBER, [
        ("Scenario:", "Relay A is under deep canopy shade (0 harvest). Starts with 80% battery at t = 0."),
        ("Dijkstra's Choice:", "Dijkstra sees 80% battery, assumes Relay A is strong, and continuously funnels heavy multi-hop traffic through it."),
        ("The Failure:", "Because Relay A receives zero solar intake, it burns out rapidly, partitioning the network while sunny nodes sit idle.")
    ])
]

c_w = Inches(3.7)
c_h = Inches(5.1)
for i, (title, accent, bullets) in enumerate(pitfalls):
    cx = Inches(0.8) + i * Inches(4.0)
    c = add_card(s3, cx, Inches(1.6), c_w, c_h)
    
    # Header bar inside card
    hbar = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, Inches(1.6), c_w, Inches(0.45))
    hbar.fill.solid()
    hbar.fill.fore_color.rgb = accent
    hbar.line.fill.background()
    htf = hbar.text_frame
    hp = htf.paragraphs[0]
    hp.text = title
    hp.font.name = FONT_HEADING
    hp.font.size = Pt(11)
    hp.font.bold = True
    hp.font.color.rgb = C_WHITE
    hp.alignment = PP_ALIGN.CENTER
    
    # Body text
    tb = s3.shapes.add_textbox(cx + Inches(0.15), Inches(2.15), c_w - Inches(0.3), c_h - Inches(0.65))
    tf = tb.text_frame
    tf.word_wrap = True
    for prefix, body in bullets:
        add_bullet(tf, prefix, body, 10, space_after=8)

add_speaker_notes(s3, """
Here we break down the two fatal flaws of classical routing in solar WSNs.
First is the 'False Rejection Flaw'. Consider a node with 5% battery at 8:00 AM. A standard Dijkstra algorithm checks the battery at t=0, declares the node dead, and routes traffic through a 4-hop detour. But by 8:05 AM, the sun has come out and recharged that node to 40%. The packet could have easily used this direct path, but Dijkstra threw it away.
Second is the 'Shaded Burnout Flaw'. A sensor placed under a tree starts with 80% battery. Dijkstra thinks it's healthy and routes all network traffic through it. Because it gets no solar recharge, it exhausts completely within hours, splitting the network in two, while sunlit nodes sat completely idle.
Our framework mathematically solves both flaws.
""")

# ==============================================================================
# SLIDE 4: LITERATURE REVIEW & STATE-OF-THE-ART ANALYSIS
# ==============================================================================
s4 = prs.slides.add_slide(blank_layout)
add_header(s4, "Literature Review: State-of-the-Art Analysis (2020–2025)", "Academic Foundation", 4)

# Table of Literature
rows = 6
cols = 4
left = Inches(0.8)
top = Inches(1.6)
width = Inches(11.733)
height = Inches(4.0)

table_shape = s4.shapes.add_table(rows, cols, left, top, width, height)
tbl = table_shape.table
tbl.columns[0].width = Inches(2.6)
tbl.columns[1].width = Inches(1.8)
tbl.columns[2].width = Inches(3.6)
tbl.columns[3].width = Inches(3.733)

headers = ["Paper Title & Authors", "Venue & Year", "Core Methodology", "Identified Limitation / Gap"]
for j, h in enumerate(headers):
    cell = tbl.cell(0, j)
    cell.fill.solid()
    cell.fill.fore_color.rgb = C_NAVY_DARK
    p = cell.text_frame.paragraphs[0]
    p.text = h
    p.font.name = FONT_HEADING
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = C_WHITE
    p.alignment = PP_ALIGN.LEFT

papers = [
    ("Adaptive Clustering for EH-WSNs\nB. Han, et al.", "MDPI Sensors\n(2022)", "Dynamic cluster head election weighted by solar intake ratio.", "Ignores packet transit delay delta-t; does not model recharge during multi-hop forwarding."),
    ("Throughput in Time-Expanded Graphs\nR. Tan, et al.", "ACM TOSN\n(2021)", "Time-expanded graph formulation with Integer Linear Programming (ILP).", "Offline centralized batch scheduling; cannot execute on distributed resource-constrained sensor motes."),
    ("Harvested Energy Prediction in Solar WSNs\nD. K. Sah, T. Amgoth", "IEEE Sensors J.\n(2023)", "Pro-Energy EWMA solar irradiance prediction model for edge costing.", "Single-path Dijkstra optimization; prone to false rejections of transient recharging relays."),
    ("Deep RL for Energy-Efficient Routing\nM. A. Aref, S. K. Jayaweera", "IEEE TCCN\n(2023)", "Deep Q-Networks (DQN) for stochastic Poisson arrival routing.", "Heavy neural weight memory (>1 MB); infeasible for 8/32-bit embedded microcontrollers (MicaZ)."),
    ("Proposed Framework (Our Work)\nSanthosh, Thilang, Ananthakrishnan", "Review 3\n(2026)", "3D Time-Augmented DP + DSU Live Detours + 24-Bin Histogram Filter.", "Solves transit recharge in O(|E|HT) polynomial time with <48 KB RAM footprint and 6.02x live detour speedup.")
]

for i, p_data in enumerate(papers):
    for j in range(4):
        cell = tbl.cell(i + 1, j)
        cell.fill.solid()
        if i == 4:
            cell.fill.fore_color.rgb = C_TEAL_LIGHT
        else:
            cell.fill.fore_color.rgb = C_WHITE if i % 2 == 0 else C_CARD_BG
        p = cell.text_frame.paragraphs[0]
        p.text = p_data[j]
        p.font.name = FONT_BODY
        p.font.size = Pt(9.5)
        if i == 4 and j == 0:
            p.font.bold = True
            p.font.color.rgb = C_TEAL
        else:
            p.font.color.rgb = C_NAVY_DARK

# Summary take-away card below table
add_card(s4, Inches(0.8), Inches(5.8), Inches(11.733), Inches(1.0), bg_color=C_BLUE_LIGHT, border_color=C_BLUE)
tb = s4.shapes.add_textbox(Inches(1.0), Inches(5.85), Inches(11.333), Inches(0.9))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "RESEARCH GAP IDENTIFIED & ADDRESSED:"
p.font.name = FONT_HEADING
p.font.size = Pt(10)
p.font.bold = True
p.font.color.rgb = C_BLUE

p2 = tf.add_paragraph()
p2.text = "Existing literature either ignores transit time, relies on centralized offline solvers (ILP), or demands heavy deep learning. Our framework is the first to achieve lookahead recharge awareness and live fault recovery using deterministic polynomial DSA feasible for 32-bit ARM Cortex-M microcontrollers."
p2.font.name = FONT_BODY
p2.font.size = Pt(10)
p2.font.color.rgb = C_NAVY_MED

add_speaker_notes(s4, """
In our literature survey of 9 top papers between 2020 and 2025, we discovered three distinct camps:
Camp 1, like Han et al. in MDPI Sensors, uses solar weighting for cluster heads, but completely ignores multi-hop transit delay.
Camp 2, like Tan et al. in ACM TOSN, uses time-expanded graphs, but relies on Integer Linear Programming (ILP). That is a centralized, offline solver that cannot run on a distributed sensor network.
Camp 3, like Aref et al. in IEEE TCCN, uses Deep Reinforcement Learning. But their neural network weights require over 1 MB of memory, which completely exceeds the 4 to 10 KB RAM of typical sensor microcontrollers like MicaZ or TelosB.
Our framework fills this exact gap: a distributed, polynomial DSA solution requiring under 48 KB RAM with live local fault recovery.
""")

# Save checkpoint
prs.save("Final_Review_Presentation_WSN_Adaptive_Routing.pptx")
print("Saved Slide 1 to 4 checkpoint.")
# ==============================================================================
# SLIDE 5: HARDWARE & PHYSICAL RADIO DISSIPATION MODELING
# ==============================================================================
s5 = prs.slides.add_slide(blank_layout)
add_header(s5, "Physical Modeling: Heinzelman First-Order Radio Dissipation", "Hardware & Physics", 5)

# Left Card: Theoretical Model & Formulas
add_card(s5, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1))
tb = s5.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(5.3), Inches(4.8))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "Heinzelman First-Order Radio Equations"
p.font.name = FONT_HEADING
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY_DARK
p.space_after = Pt(8)

add_bullet(tf, "Radio Transmission Dissipation:", "Energy spent to transmit a k-bit packet across distance d accounts for electronic circuitry and RF power amplification.", 11)

# Embed Equation 5 image if available
eq5_path = os.path.join(EQ_DIR, "eq_5.png")
if os.path.exists(eq5_path):
    s5.shapes.add_picture(eq5_path, Inches(1.0), Inches(2.85), width=Inches(5.3))

# Spacer below image
tb_sub = s5.shapes.add_textbox(Inches(1.0), Inches(3.6), Inches(5.3), Inches(3.0))
tf_sub = tb_sub.text_frame
tf_sub.word_wrap = True
add_bullet(tf_sub, "Two Channel Regimes:", "When transmission distance d < d0 (crossover distance), path loss follows d^2 (free-space). When d >= d0, path loss steepens to d^4 (multipath fading).", 10.5)
add_bullet(tf_sub, "Electronic Reception Penalty (E_rx):", "Every intermediate relay expends Erx = k * E_elec simply to receive a packet. For 4000 bits, Erx = 0.200 mJ. This reception penalty is central to real-world performance.", 10.5)

# Right Card: Hardware Constants & The Crossover Discovery
add_card(s5, Inches(6.833), Inches(1.6), Inches(5.7), Inches(5.1))
tb = s5.shapes.add_textbox(Inches(7.033), Inches(1.75), Inches(5.3), Inches(4.8))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "Hardware Constants & Crossover Distance"
p.font.name = FONT_HEADING
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY_DARK
p.space_after = Pt(8)

add_bullet(tf, "Circuitry Dissipation (E_elec):", "50.0 nJ/bit (5.0 x 10^-8 J/bit) -- drives transmitter and receiver electronics.", 11)
add_bullet(tf, "Free-Space Amplifier (eps_fs):", "10.0 pJ/bit/m^2 (1.0 x 10^-11 J/bit/m^2) -- power amplification for d < d0.", 11)
add_bullet(tf, "Multipath Amplifier (eps_mp):", "0.0013 pJ/bit/m^4 (1.3 x 10^-15 J/bit/m^4) -- power amplification for d >= d0.", 11)
add_bullet(tf, "Calculated Crossover Distance (d0):", "d0 = sqrt(eps_fs / eps_mp) = sqrt(10.0 / 0.0013) = 87.70 meters.", 11)

# Highlight Callout Box inside right card
callout = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.033), Inches(4.8), Inches(5.3), Inches(1.7))
callout.fill.solid()
callout.fill.fore_color.rgb = C_AMBER
callout.fill.transparency = 0.85
callout.line.color.rgb = C_AMBER
callout.line.width = Pt(1)
ctf = callout.text_frame
ctf.word_wrap = True
cp = ctf.paragraphs[0]
cp.text = "CRITICAL HARDWARE REALISM INSIGHT:"
cp.font.name = FONT_HEADING
cp.font.size = Pt(10)
cp.font.bold = True
cp.font.color.rgb = C_AMBER

cp2 = ctf.add_paragraph()
cp2.text = "In a 100m x 100m sensor field, most adjacent nodes are separated by 20m to 50m (well below d0 = 87.7m). In this zone, transmission scales with d^2. Relaying introduces an additional Erx = 0.200 mJ penalty per hop that static algorithms often overlook!"
cp2.font.name = FONT_BODY
cp2.font.size = Pt(9.5)
cp2.font.color.rgb = C_NAVY_DARK

add_speaker_notes(s5, """
Here we explain the physical radio model implemented in src/energy_model.py.
Rather than using an idealized unit-cost model, our simulator implements Heinzelman's first-order radio model, which is standard for Texas Instruments CC2420 and MicaZ motes.
Notice the crossover distance d0: at 87.7 meters, path loss shifts from d^2 free-space to d^4 multipath fading. 
More importantly, look at Erx: every time an intermediate relay node receives a 4000-bit packet, it dissipates 0.200 mJ of energy simply operating its receiver circuitry. As we will show later in our empirical results, this creates a major trade-off between single-hop and multi-hop routing that literature baselines frequently ignore.
""")

# ==============================================================================
# SLIDE 6: ENVIRONMENTAL ENERGY HARVESTING REGIMES
# ==============================================================================
s6 = prs.slides.add_slide(blank_layout)
add_header(s6, "Environmental Modeling: 4 Solar & Ambient Harvesting Regimes", "Environmental Engine", 6)

regimes = [
    ("1. Diurnal Solar Model", C_TEAL, [
        ("Physics:", "Simulates 24-round solar days (1 round ~ 1 hour)."),
        ("Mathematical Profile:", "Daytime irradiance follows a clipped half-sine wave with peak 0.035 J/round at midday (rounds 6 to 18), dropping to 0.0 J at night (rounds 0 to 5, 19 to 23)."),
        ("Effect:", "Tests algorithm's ability to store charge and anticipate day/night transitions.")
    ]),
    ("2. Spatial Canopy Shadowing", C_AMBER, [
        ("Physics:", "Simulates uneven tree foliage or building occlusion across the field."),
        ("Mathematical Profile:", "Parameterized by shadow probability p_shadow in [0, 1]. Shaded nodes receive only 10% of incoming solar irradiance."),
        ("Effect:", "Creates permanent spatial heterogeneity: sunlit relays recharge rapidly while shaded relays must be conserved.")
    ]),
    ("3. Poisson Arrival Process", C_BLUE, [
        ("Physics:", "Models sporadic, bursty ambient energy sources (vibration, indoor lighting, beamed RF)."),
        ("Mathematical Profile:", "Arrival events occur via Poisson process with rate lambda and discrete energy quantum size q."),
        ("Effect:", "Tests routing robustness when solar harvest cannot be predicted deterministically.")
    ]),
    ("4. Real 24-Hour Weather Trace Replay", C_NAVY_MED, [
        ("Physics:", "Replays verified 24-hour solar irradiance empirical datasets."),
        ("Mathematical Profile:", "Clear Sky (smooth diurnal curve), Intermittent Clouds (sharp random dips), and Overcast (heavily damped solar intake)."),
        ("Effect:", "Validates the simulator against real meteorological conditions.")
    ])
]

for i, (title, color, bullets) in enumerate(regimes):
    row = i // 2
    col = i % 2
    cx = Inches(0.8) + col * Inches(6.0)
    cy = Inches(1.6) + row * Inches(2.55)
    
    add_card(s6, cx, cy, Inches(5.7), Inches(2.4))
    
    # Header bar
    hbar = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, cy, Inches(5.7), Inches(0.38))
    hbar.fill.solid()
    hbar.fill.fore_color.rgb = color
    hbar.line.fill.background()
    htf = hbar.text_frame
    hp = htf.paragraphs[0]
    hp.text = title
    hp.font.name = FONT_HEADING
    hp.font.size = Pt(11)
    hp.font.bold = True
    hp.font.color.rgb = C_WHITE
    hp.alignment = PP_ALIGN.LEFT
    
    # Content
    tb = s6.shapes.add_textbox(cx + Inches(0.15), cy + Inches(0.42), Inches(5.4), Inches(1.9))
    tf = tb.text_frame
    tf.word_wrap = True
    for pfx, txt in bullets:
        add_bullet(tf, pfx, txt, 9.5, space_after=3)

add_speaker_notes(s6, """
In src/harvesting_model.py, our simulator models four distinct energy regimes.
First, a Diurnal Solar Model that simulates realistic 24-hour solar cycles where daytime follows a clipped half-sine wave peaking at 0.035 Joules per round.
Second, Spatial Canopy Shadowing, where some nodes are in bright sun while others sit under trees receiving only 10% solar intake.
Third, a Poisson Arrival Process that models sporadic ambient bursts like indoor lighting or vibration.
And fourth, Real Weather Trace Replays using empirical 24-hour solar irradiance datasets under clear, cloudy, and overcast skies.
This ensures our algorithms are not just evaluated on toy mathematical assumptions, but on realistic meteorological profiles.
""")

# ==============================================================================
# SLIDE 7: ALGORITHM 1 — 3D TIME-AUGMENTED DYNAMIC PROGRAMMING
# ==============================================================================
s7 = prs.slides.add_slide(blank_layout)
add_header(s7, "Algorithm 1: 3D Time-Augmented Dynamic Programming (dp[v][h][t])", "Core DSA Algorithm", 7)

# Left Card: Recurrence & State Formulation
add_card(s7, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1))
tb = s7.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(5.3), Inches(4.8))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "Mathematical State Space & 3D Recurrence"
p.font.name = FONT_HEADING
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY_DARK
p.space_after = Pt(6)

add_bullet(tf, "Discrete 3D State (v, h, t):", "Node v, hop distance h (1 to H=8), arrival time slot t from now (1 slot/hop).", 10.5)
add_bullet(tf, "State Variable dp[v][h][t]:", "Maximum bottleneck residual energy among all candidate h-hop paths reaching v at time offset t.", 10.5)

# Embed Equation 3 image if available
eq3_path = os.path.join(EQ_DIR, "eq_3.png")
if os.path.exists(eq3_path):
    s7.shapes.add_picture(eq3_path, Inches(1.0), Inches(2.95), width=Inches(5.3))

tb_sub = s7.shapes.add_textbox(Inches(1.0), Inches(3.6), Inches(5.3), Inches(3.0))
tf_sub = tb_sub.text_frame
tf_sub.word_wrap = True
add_bullet(tf_sub, "Lookahead Energy Projection E_proj(v, t):", "E_proj(v, t) = min(E_max, E_v(t_curr) + sum H_v(tau)*eta - E_leak*t). Anticipates incoming solar refill during packet transit.", 10)
add_bullet(tf_sub, "Physical Feasibility Gate:", "Candidate transition from u to v is valid iff dp[u][h-1][t-delta] >= E_tx(k, d(u,v)). Prevents routing through depleted nodes.", 10)

# Right Card: Complexity & Embedded Microcontroller Feasibility
add_card(s7, Inches(6.833), Inches(1.6), Inches(5.7), Inches(5.1))
tb = s7.shapes.add_textbox(Inches(7.033), Inches(1.75), Inches(5.3), Inches(4.8))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "Complexity & Embedded Microcontroller Budget"
p.font.name = FONT_HEADING
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY_DARK
p.space_after = Pt(6)

add_bullet(tf, "Time Complexity:", "O(|E| * H * T). Strictly polynomial! Each state evaluates incoming edges across H hops and T time slots.", 10.5)
add_bullet(tf, "Space Complexity:", "O(|V| * H * T). Compact 3D memoization table.", 10.5)
add_bullet(tf, "Real Execution Benchmark:", "On a 50-node network with H = 8 and T = 8, the table evaluates in < 5.2 ms per call.", 10.5)
add_bullet(tf, "RAM Memory Footprint:", "Consumes < 48 KB RAM. Easily fits within modern 32-bit ARM Cortex-M4 (64 KB to 256 KB RAM) or ESP32 microcontrollers.", 10.5)

# Route Selection Eq
eq2_path = os.path.join(EQ_DIR, "eq_2.png")
if os.path.exists(eq2_path):
    s7.shapes.add_picture(eq2_path, Inches(7.033), Inches(4.5), width=Inches(5.3))

tb_rec = s7.shapes.add_textbox(Inches(7.033), Inches(5.15), Inches(5.3), Inches(1.5))
tf_rec = tb_rec.text_frame
tf_rec.word_wrap = True
add_bullet(tf_rec, "Optimal Route Reconstruction:", "Backpointers parent[(v, h, t)] backtrack from target Base Station to extract the optimal bottleneck-maximizing path P*.", 10)

add_speaker_notes(s7, """
This is Algorithm 1, our core theoretical contribution in src/dp_lifetime.py.
Instead of evaluating nodes on frozen t=0 snapshots, we formulate a 3D state space indexed by (v, h, t): node v, hop count h, and arrival time t.
Look at the recurrence: dp[v][h][t] is the maximum bottleneck capacity to reach node v. It evaluates predecessor u, but critically evaluates node v's energy at arrival time t using the lookahead projection function E_proj.
This projection adds the solar recharge expected during the h-hop transit.
Because this runs on a Directed Acyclic Graph ordered by hop count and time, time complexity is strictly O(|E|HT), taking only 5.2 ms and under 48 KB RAM on a 50-node network.
""")

# ==============================================================================
# SLIDE 8: ALGORITHM 2 — DISJOINT-SET UNION (DSU) LIVE DETOUR RECOVERY
# ==============================================================================
s8 = prs.slides.add_slide(blank_layout)
add_header(s8, "Algorithm 2: Disjoint-Set Union (DSU) Live Detour Recovery", "Fault Tolerance & Recovery", 8)

# 3 Column Cards
c_w = Inches(3.7)
c_h = Inches(5.1)

# Card 1: The In-Flight Brownout Problem
c1 = add_card(s8, Inches(0.8), Inches(1.6), c_w, c_h)
tb1 = s8.shapes.add_textbox(Inches(0.95), Inches(1.75), c_w - Inches(0.3), c_h - Inches(0.3))
tf1 = tb1.text_frame
tf1.word_wrap = True
p = tf1.paragraphs[0]
p.text = "The In-Flight Brownout Problem"
p.font.name = FONT_HEADING
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = C_RED
p.space_after = Pt(6)

add_bullet(tf1, "Transient Occlusion:", "A relay node can brown out unexpectedly mid-round due to transient cloud cover or unexpected packet handling demands.", 10)
add_bullet(tf1, "Wasted Hop Energy:", "If the packet is dropped, all transmission energy spent across prior hops is permanently wasted.", 10)
add_bullet(tf1, "Global DP Recompute is Slow:", "Triggering a global Time-DP recalculation causes > 5.1 ms latency spikes and floods the network with route discovery packets.", 10)

# Card 2: Union-Find with Path Compression
c2 = add_card(s8, Inches(4.8), Inches(1.6), c_w, c_h)
tb2 = s8.shapes.add_textbox(Inches(4.95), Inches(1.75), c_w - Inches(0.3), c_h - Inches(0.3))
tf2 = tb2.text_frame
tf2.word_wrap = True
p = tf2.paragraphs[0]
p.text = "Union-Find Data Structure"
p.font.name = FONT_HEADING
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = C_BLUE
p.space_after = Pt(6)

add_bullet(tf2, "Two Classic Optimizations:", "1. Path Compression during find(x): flattens tree so parent points directly to root.\n2. Union by Rank during union(x, y): attaches shallower tree beneath deeper tree.", 10)
add_bullet(tf2, "Inverse Ackermann Guarantee:", "Amortized operation time is O(alpha(V)) where alpha(V) <= 4 for all practical universe sizes. Near O(1) in practice!", 10)
add_bullet(tf2, "Component Invariant:", "Maintains live graph partition: node b can reach Base Station iff find(b) == find(BS).", 10)

# Card 3: Local Bridge Splicing
c3 = add_card(s8, Inches(8.8), Inches(1.6), c_w, c_h)
tb3 = s8.shapes.add_textbox(Inches(8.95), Inches(1.75), c_w - Inches(0.3), c_h - Inches(0.3))
tf3 = tb3.text_frame
tf3.word_wrap = True
p = tf3.paragraphs[0]
p.text = "Local Bridge Splicing & Speedup"
p.font.name = FONT_HEADING
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = C_TEAL
p.space_after = Pt(6)

add_bullet(tf3, "Local Splicing Logic:", "When relay at hop i fails, predecessor u inspects its immediate neighbors. It selects candidate b that shares BS component (find(b) == bs_root) with lowest radio cost.", 10)
add_bullet(tf3, "Repair Complexity:", "O(deg(u) * alpha(V)). Checks only deg(u) local edges without global route broadcasts.", 10)
add_bullet(tf3, "Empirical Benchmark:", "Repair executes in 0.85 ms vs 5.12 ms for full DP recompute -- delivering a 6.02x latency speedup with 100% PDR!", 10)

add_speaker_notes(s8, """
Slide 8 presents Algorithm 2: Disjoint-Set Union Live Detour Recovery in src/routing.py.
In real sensor networks, nodes don't wait for round boundaries to die. A relay can run out of energy mid-transmission. 
If we drop that packet, all energy spent getting it halfway across the field is wasted. If we rerun global Dynamic Programming, it takes over 5 milliseconds and requires broadcasting route updates across the entire field.
Our solution is local DSU repair. By maintaining Union-Find components with Path Compression and Rank, the predecessor node simply checks its immediate neighbors in O(deg(u)) to find one already connected to the Base Station component.
This splices a replacement bridge in 0.85 milliseconds—a 6.02x speedup—achieving a 100% packet delivery ratio.
""")

# ==============================================================================
# SLIDE 9: ALGORITHM 3 — SOLAR-WEIGHTED DYNAMIC CLUSTERING (EH-LEACH)
# ==============================================================================
s9 = prs.slides.add_slide(blank_layout)
add_header(s9, "Algorithm 3: Solar-Weighted Dynamic Clustering (EH-LEACH)", "Clustering & Epoch Management", 9)

# Left Card: Classical LEACH vs EH-LEACH
add_card(s9, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1))
tb = s9.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(5.3), Inches(4.8))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "The Classical LEACH Clustering Defect"
p.font.name = FONT_HEADING
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY_DARK
p.space_after = Pt(6)

add_bullet(tf, "Classical LEACH Principle:", "Sensors elect themselves as Cluster Heads (CHs) based on random probability p = 0.10 within an epoch of 1/p = 10 rounds.", 10.5)
add_bullet(tf, "The Solar Blindspot:", "Classical LEACH treats every alive node equally. A shaded sensor under heavy canopy has the exact same probability of becoming a CH as a sensor under bright, open sunlight.", 10.5)
add_bullet(tf, "The Burnout Cascade:", "Cluster Heads must aggregate sensor data from 10+ member nodes and transmit long-range uplinks to the Base Station. When a shaded node becomes a CH, its battery collapses in 1–2 rounds.", 10.5)
add_bullet(tf, "Our Fix in src/clustering.py:", "Weight the threshold T(n) dynamically using both residual energy and expected solar harvest intake.", 10.5)

# Right Card: Modified Election Threshold & Results
add_card(s9, Inches(6.833), Inches(1.6), Inches(5.7), Inches(5.1))
tb = s9.shapes.add_textbox(Inches(7.033), Inches(1.75), Inches(5.3), Inches(4.8))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "Modified Solar Threshold Equation T(n)"
p.font.name = FONT_HEADING
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY_DARK
p.space_after = Pt(6)

# Embed Equation 4 image if available
eq4_path = os.path.join(EQ_DIR, "eq_4.png")
if os.path.exists(eq4_path):
    s9.shapes.add_picture(eq4_path, Inches(7.033), Inches(2.4), width=Inches(5.3))

tb_sub = s9.shapes.add_textbox(Inches(7.033), Inches(3.2), Inches(5.3), Inches(3.3))
tf_sub = tb_sub.text_frame
tf_sub.word_wrap = True
add_bullet(tf_sub, "E_n, H_n:", "Residual battery energy and expected incoming solar harvest of candidate node n.", 10)
add_bullet(tf_sub, "E_avg, H_avg:", "Average residual energy and harvest rate across all currently alive nodes.", 10)
add_bullet(tf_sub, "beta = 0.5:", "Harvest weighting coefficient balancing stored battery vs solar rate.", 10)
add_bullet(tf_sub, "2.4x Sunlit Election Boost:", "Nodes under bright sunlight are elected 2.4x more frequently, taking over heavy aggregation duties and shielding shaded nodes from early burnout.", 10)

add_speaker_notes(s9, """
Slide 9 covers Algorithm 3: Solar-Weighted Dynamic Clustering (EH-LEACH) in src/clustering.py.
In standard LEACH, cluster head election is essentially a random coin flip. Every node has probability p of becoming a head. 
In an energy-harvesting network, this is disastrous. Becoming a cluster head requires collecting readings from member nodes, fusing data, and transmitting long-range uplinks to the base station. If a shaded node is elected, it exhausts its battery in one round.
Our EH-LEACH algorithm modifies the Heinzelman election threshold T(n) with a ratio: (E_n + beta * H_n) / (E_avg + beta * H_avg).
Nodes in open sunlight receive a boosted election threshold, being elected 2.4 times more frequently, while shaded nodes are shielded and remain simple leaf nodes.
""")

# ==============================================================================
# SLIDE 10: ALGORITHM 4 — ROUTING UNDER ENERGY UNCERTAINTY & BELIEF STATES
# ==============================================================================
s10 = prs.slides.add_slide(blank_layout)
add_header(s10, "Algorithm 4: Routing Under Uncertainty & 24-Bin Belief Filter", "Probabilistic DSA", 10)

# Left Card: Telemetry Dilemma & 5 Energy Views
add_card(s10, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1))
tb = s10.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(5.3), Inches(4.8))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "The Telemetry Dilemma & 5 Energy Views"
p.font.name = FONT_HEADING
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY_DARK
p.space_after = Pt(6)

add_bullet(tf, "The Signaling Dilemma:", "Nodes cannot report exact battery levels every round without wasting radio energy on telemetry packets. Decisions must be made under partial observability.", 10)
add_bullet(tf, "Five Belief Models (src/energy_view.py):", "", 10)
add_bullet(tf, "- Oracle:", "Omniscient exact battery E_i(t). Unrealistic upper baseline.", 9.5)
add_bullet(tf, "- Blind:", "Fixed snapshot E_i(0). Completely blind to solar recharge.", 9.5)
add_bullet(tf, "- Stale:", "Periodic 8-bit report every R rounds. Lags behind true state.", 9.5)
add_bullet(tf, "- Gaussian:", "Kalman filter (mu, sigma^2). Suffers severe boundary errors.", 9.5)
add_bullet(tf, "- Histogram (Ours):", "24-bin discrete probability distribution p in [0, 1]^24.", 9.5)

# Right Card: Why Discrete Histogram & Max-Product DP
add_card(s10, Inches(6.833), Inches(1.6), Inches(5.7), Inches(5.1))
tb = s10.shapes.add_textbox(Inches(7.033), Inches(1.75), Inches(5.3), Inches(4.8))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "24-Bin Discrete Histogram & Max-Product DP"
p.font.name = FONT_HEADING
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY_DARK
p.space_after = Pt(6)

add_bullet(tf, "The Gaussian Failure at Boundaries:", "Gaussian tails extend to +/- infinity, producing non-zero probabilities for negative energy (< 0 J) or over-capacity (> E_max). This corrupts routing decisions.", 10)
add_bullet(tf, "Exact Boundary Mass Clipping:", "Our 24-bin histogram explicitly clips probability mass: negative transitions accumulate in bin 0 (brownout probability); excess recharge accumulates in bin 23 (saturation).", 10)
add_bullet(tf, "Log-Domain Max-Product DP Objective:", "Maximizes end-to-end multi-hop packet delivery confidence:", 10)

# Embed Equation 6 image if available
eq6_path = os.path.join(EQ_DIR, "eq_6.png")
if os.path.exists(eq6_path):
    s10.shapes.add_picture(eq6_path, Inches(7.033), Inches(4.2), width=Inches(5.3))

tb_cens = s10.shapes.add_textbox(Inches(7.033), Inches(4.85), Inches(5.3), Inches(1.8))
tf_cens = tb_cens.text_frame
tf_cens.word_wrap = True
add_bullet(tf_cens, "Censored Evidence Updates:", "When a packet fails to reach the Base Station, the router immediately updates belief: P(E < E_tx) = 1.0, zeroing out higher probability bins without waiting for telemetry.", 9.5)

add_speaker_notes(s10, """
In Slide 10, we address real-world partial observability in src/energy_view.py.
Sensors cannot transmit telemetry reports every minute; transmitting the report itself would drain the battery. So the router must maintain a belief state.
Most papers use Kalman filters with Gaussian noise. But batteries have hard boundaries: they cannot drop below 0 Joules or exceed E_max = 0.5 Joules. Gaussian tails create severe errors at these boundaries.
We implement a 24-bin discrete histogram filter with exact boundary mass clipping: mass below zero goes into bin 0 (brownout probability), and mass above E_max clips into bin 23 (saturation).
Our Max-Product DP maximizes the sum of log-probabilities across the route, choosing paths with the highest mathematical confidence of end-to-end survival.
""")

# Save checkpoint
prs.save("Final_Review_Presentation_WSN_Adaptive_Routing.pptx")
print("Saved Slide 5 to 10 checkpoint.")
# ==============================================================================
# SLIDE 11: IMPLEMENTED SYSTEM ARCHITECTURE & CODEBASE WALKTHROUGH
# ==============================================================================
s11 = prs.slides.add_slide(blank_layout)
add_header(s11, "Implemented Architecture & Codebase Walkthrough", "Software Architecture", 11)

# Codebase Directory Table
rows = 7
cols = 4
left = Inches(0.8)
top = Inches(1.6)
width = Inches(11.733)
height = Inches(3.9)

table_shape = s11.shapes.add_table(rows, cols, left, top, width, height)
tbl = table_shape.table
tbl.columns[0].width = Inches(1.8)
tbl.columns[1].width = Inches(2.2)
tbl.columns[2].width = Inches(6.333)
tbl.columns[3].width = Inches(1.4)

headers = ["Directory", "Key Module", "Algorithmic Responsibility", "Lines of Code"]
for j, h in enumerate(headers):
    cell = tbl.cell(0, j)
    cell.fill.solid()
    cell.fill.fore_color.rgb = C_NAVY_DARK
    p = cell.text_frame.paragraphs[0]
    p.text = h
    p.font.name = FONT_HEADING
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

modules_data = [
    ("src/", "network.py, energy_model.py", "Euclidean graph adjacency, 1st-order radio model (d^2/d^4), Erx penalty", "425 LOC"),
    ("src/", "dp_lifetime.py, routing.py", "3D Time-Augmented DP (dp[v][h][t]), DSU live detour recovery, Dijkstra", "535 LOC"),
    ("src/", "clustering.py, energy_view.py", "EH-LEACH solar threshold rotation, 24-bin histogram belief filter", "445 LOC"),
    ("src/", "harvesting_model.py, simulator.py", "Diurnal solar, canopy shadows, Poisson bursts, discrete-round loop", "585 LOC"),
    ("backend/", "main.py, database.py", "FastAPI REST API, async threadpool execution, SQLite run history", "290 LOC"),
    ("frontend/", "src/ (React 19 + TypeScript)", "Interactive SVG canvas, timeline scrubber, spatial heatmap, Recharts", "~1,850 LOC")
]

for i, row_data in enumerate(modules_data):
    for j in range(4):
        cell = tbl.cell(i + 1, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_WHITE if i % 2 == 0 else C_CARD_BG
        p = cell.text_frame.paragraphs[0]
        p.text = row_data[j]
        p.font.name = FONT_CODE if j in [0, 1, 3] else FONT_BODY
        p.font.size = Pt(9.5)
        p.font.color.rgb = C_NAVY_MED
        if j == 3:
            p.alignment = PP_ALIGN.RIGHT

# Bottom Architecture Summary Card
add_card(s11, Inches(0.8), Inches(5.7), Inches(11.733), Inches(1.1), bg_color=C_TEAL_LIGHT, border_color=C_TEAL)
tb = s11.shapes.add_textbox(Inches(1.0), Inches(5.75), Inches(11.333), Inches(1.0))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "THREE-TIER DECOUPLED ARCHITECTURE & PRODUCTION STANDARDS:"
p.font.name = FONT_HEADING
p.font.size = Pt(10)
p.font.bold = True
p.font.color.rgb = C_TEAL

p2 = tf.add_paragraph()
p2.text = "- Tier 1 (Headless Engine): Pure Python 3.12 + NumPy/SciPy without GUI dependencies. Fully headless and unit-tested.\n- Tier 2 (Asynchronous Backend): FastAPI REST service with SQLite persistence, offloading simulation sweeps to background threads.\n- Tier 3 (Client-Side Dashboard): React 19 single-page application with SVG animations, timeline playback, and Recharts analytics."
p2.font.name = FONT_BODY
p2.font.size = Pt(9.5)
p2.font.color.rgb = C_NAVY_DARK

add_speaker_notes(s11, """
Slide 11 reviews our overall codebase structure and software architecture.
We followed strict software engineering standards to ensure modularity and academic reproducibility.
The project is divided into three completely decoupled tiers:
Tier 1 in src/ is the pure algorithmic engine. It has zero GUI dependencies and can be compiled into an embedded binary or run headlessly in batch sweeps.
Tier 2 in backend/ is a FastAPI REST API that persists simulation histories to an embedded SQLite database and runs sweeps in background worker threads.
Tier 3 in frontend/ is a React 19 research dashboard providing interactive visualization.
Total verified code volume exceeds 4,000 lines, anchored by 15 pytest test suites.
""")

# ==============================================================================
# SLIDE 12: CODE REVIEW — CORE IMPLEMENTATION WALKTHROUGH
# ==============================================================================
s12 = prs.slides.add_slide(blank_layout)
add_header(s12, "Code Review: Core Algorithmic Implementations", "Code Inspection", 12)

# Left Column: 3D Time-DP Code Excerpt
add_card(s12, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1), bg_color=C_CODE_BG)
tb = s12.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.3), Inches(0.4))
tf = tb.text_frame
p = tf.paragraphs[0]
p.text = "3D Time-Augmented DP (src/dp_lifetime.py)"
p.font.name = FONT_HEADING
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = C_BLUE

code_dp = """def compute_time_augmented_dp(network, source, target,
                              max_hops=8, delta_t=1):
    dp = defaultdict(lambda: -float('inf'))
    parent = {}
    dp[(source, 0, 0)] = network.nodes[source].energy

    for h in range(1, max_hops + 1):
        t = h * delta_t
        for v in network.nodes:
            for u in network.get_incoming_neighbors(v):
                prev_e = dp.get((u, h-1, t-delta_t), -inf)
                cost_tx = network.calc_tx_cost(u, v)
                if prev_e < cost_tx: 
                    continue  # Infeasible hop
                
                # Project recharge at arrival time t
                proj_v = network.project_energy(v, t) - \\
                         (network.E_rx if v != target else 0)
                bottleneck = min(prev_e, proj_v)
                if bottleneck > dp[(v, h, t)]:
                    dp[(v, h, t)] = bottleneck
                    parent[(v, h, t)] = u
    return reconstruct_path(parent, target, dp)"""

tb_c = s12.shapes.add_textbox(Inches(0.9), Inches(2.1), Inches(5.5), Inches(4.5))
tf_c = tb_c.text_frame
tf_c.word_wrap = True
p_c = tf_c.paragraphs[0]
p_c.text = code_dp
p_c.font.name = FONT_CODE
p_c.font.size = Pt(8.5)
p_c.font.color.rgb = C_NAVY_DARK

# Right Column: DSU Route Repair Code Excerpt
add_card(s12, Inches(6.833), Inches(1.6), Inches(5.7), Inches(5.1), bg_color=C_CODE_BG)
tb2 = s12.shapes.add_textbox(Inches(7.033), Inches(1.7), Inches(5.3), Inches(0.4))
tf2 = tb2.text_frame
p2 = tf2.paragraphs[0]
p2.text = "DSU Live Detour Recovery (src/routing.py)"
p2.font.name = FONT_HEADING
p2.font.size = Pt(12)
p2.font.bold = True
p2.font.color.rgb = C_TEAL

code_dsu = """class UnionFind:
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x]) # Path compression
        return self.parent[x]

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry: return False
        if self.rank[rx] < self.rank[ry]: rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]: self.rank[rx] += 1
        return True

def repair_route_dsu(active_path, failed_idx, dsu, network):
    u = active_path[failed_idx - 1] # Predecessor
    bs_root = dsu.find(network.base_station_id)
    # Check neighbors connected to BS component
    candidates = [b for b in network.neighbors(u)
                  if b != active_path[failed_idx] and
                  dsu.find(b) == bs_root and
                  network.can_transmit(u, b)]
    if not candidates: return None # Partitioned
    best = min(candidates, key=lambda b: network.calc_tx_cost(u, b))
    return active_path[:failed_idx] + [best, network.bs_id]"""

tb_c2 = s12.shapes.add_textbox(Inches(6.933), Inches(2.1), Inches(5.5), Inches(4.5))
tf_c2 = tb_c2.text_frame
tf_c2.word_wrap = True
p_c2 = tf_c2.paragraphs[0]
p_c2.text = code_dsu
p_c2.font.name = FONT_CODE
p_c2.font.size = Pt(8.5)
p_c2.font.color.rgb = C_NAVY_DARK

add_speaker_notes(s12, """
On Slide 12, we inspect the actual Python implementation from src/dp_lifetime.py and src/routing.py.
On the left is compute_time_augmented_dp. Notice how clean the loop is: it iterates over hops h and arrival time t = h * delta_t.
The feasibility check prev_e < cost_tx prunes infeasible paths immediately.
Then, notice line proj_v = network.project_energy(v, t) - E_rx: this is where the magic happens. It evaluates the candidate node's energy at arrival time t, taking into account both expected solar intake and reception dissipation.
On the right is repair_route_dsu. Using Union-Find with path compression and rank, it queries dsu.find(b) == bs_root. This check takes amortized O(alpha(V)) time, allowing predecessor u to instantly splice a viable bridge node without triggering global network recalculation.
""")

# ==============================================================================
# SLIDE 13: FULL-STACK WEB INTERFACE — TOPOLOGY & PLAYBACK SCRUBBER
# ==============================================================================
s13 = prs.slides.add_slide(blank_layout)
add_header(s13, "Full-Stack Web Interface: Topology Visualizer & Playback", "User Interface & Visualization", 13)

# Figure 1: Topology Visualizer
add_card(s13, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1))
tb = s13.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.3), Inches(0.4))
tf = tb.text_frame
p = tf.paragraphs[0]
p.text = "Interactive SVG Topology Visualizer"
p.font.name = FONT_HEADING
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = C_NAVY_DARK

img1_path = os.path.join(EXPLAINER_DIR, "01_topology_view.png")
if os.path.exists(img1_path):
    s13.shapes.add_picture(img1_path, Inches(1.0), Inches(2.15), width=Inches(5.3))

tb_desc1 = s13.shapes.add_textbox(Inches(1.0), Inches(5.15), Inches(5.3), Inches(1.4))
tf_d1 = tb_desc1.text_frame
tf_d1.word_wrap = True
add_bullet(tf_d1, "Real-Time SVG Canvas:", "Renders all 50 sensor nodes with color-coded operational states: Green (solar rich), Amber (draining relay), Red (browned out).", 9.5)
add_bullet(tf_d1, "Dynamic Routing Vectors:", "Renders active forwarding paths and cluster head uplinks as directed vector arrows terminating at central Base Station (50, 50).", 9.5)

# Figure 2: Playback Scrubber & Simulation Controls
add_card(s13, Inches(6.833), Inches(1.6), Inches(5.7), Inches(5.1))
tb2 = s13.shapes.add_textbox(Inches(7.033), Inches(1.7), Inches(5.3), Inches(0.4))
tf2 = tb2.text_frame
p2 = tf2.paragraphs[0]
p2.text = "Timeline Playback Scrubber & Speed Controls"
p2.font.name = FONT_HEADING
p2.font.size = Pt(13)
p2.font.bold = True
p2.font.color.rgb = C_NAVY_DARK

img2_path = os.path.join(EXPLAINER_DIR, "02_playback_scrubber.png")
if os.path.exists(img2_path):
    s13.shapes.add_picture(img2_path, Inches(7.033), Inches(2.15), width=Inches(5.3))

tb_desc2 = s13.shapes.add_textbox(Inches(7.033), Inches(5.15), Inches(5.3), Inches(1.4))
tf_d2 = tb_desc2.text_frame
tf_d2.word_wrap = True
add_bullet(tf_d2, "Granular Time Scrubbing:", "Evaluators can scrub forward and backward round-by-round across 200+ rounds to inspect energy changes and route adjustments.", 9.5)
add_bullet(tf_d2, "Playback Engine:", "Supports Play, Pause, Single-Step increment, and adjustable playback speeds (1x, 2x, 5x, 10x) with live telemetry HUD.", 9.5)

add_speaker_notes(s13, """
Slide 13 demonstrates our full-stack web application built using React 19, TypeScript, and Tailwind CSS.
On the left is Figure 1: the Interactive Network Topology Visualizer. It renders all 50 sensor motes in real-time on an SVG canvas. Nodes change color dynamically: bright green when their batteries are saturated by sun, amber when they are carrying heavy relay traffic, and red if they brown out. Directed vector arrows show the exact forwarding paths to the Base Station.
On the right is Figure 2: the Playback Scrubber. It allows evaluators to step through rounds one by one or play them back at up to 10x speed. This lets researchers visually inspect exactly how routes shift as the sun moves across the sky.
""")

# ==============================================================================
# SLIDE 14: FULL-STACK WEB INTERFACE — HEATMAPS & TELEMETRY ANALYTICS
# ==============================================================================
s14 = prs.slides.add_slide(blank_layout)
add_header(s14, "Full-Stack Web Interface: Spatial Heatmaps & Telemetry", "Analytics Drawer", 14)

# Figure 3: Spatial Energy Heatmap
add_card(s14, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1))
tb = s14.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.3), Inches(0.4))
tf = tb.text_frame
p = tf.paragraphs[0]
p.text = "2D Spatial Energy Contour Heatmap"
p.font.name = FONT_HEADING
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = C_NAVY_DARK

img3_path = os.path.join(EXPLAINER_DIR, "03_energy_heatmap.png")
if os.path.exists(img3_path):
    s14.shapes.add_picture(img3_path, Inches(1.0), Inches(2.15), width=Inches(5.3))

tb_desc1 = s14.shapes.add_textbox(Inches(1.0), Inches(5.15), Inches(5.3), Inches(1.4))
tf_d1 = tb_desc1.text_frame
tf_d1.word_wrap = True
add_bullet(tf_d1, "Spatial Energy Field:", "Renders battery density contours across the 100m x 100m field. High-density solar charging appears in bright teal/green.", 9.5)
add_bullet(tf_d1, "Early Hotspot Detection:", "Canopy shadow zones and depleted relays appear in dark purple/blue, immediately exposing impending network disconnections.", 9.5)

# Figure 4: Real-Time Telemetry Charts
add_card(s14, Inches(6.833), Inches(1.6), Inches(5.7), Inches(5.1))
tb2 = s14.shapes.add_textbox(Inches(7.033), Inches(1.7), Inches(5.3), Inches(0.4))
tf2 = tb2.text_frame
p2 = tf2.paragraphs[0]
p2.text = "Real-Time Telemetry & Performance Analytics"
p2.font.name = FONT_HEADING
p2.font.size = Pt(13)
p2.font.bold = True
p2.font.color.rgb = C_NAVY_DARK

img4_path = os.path.join(EXPLAINER_DIR, "04_analytics_charts.png")
if os.path.exists(img4_path):
    s14.shapes.add_picture(img4_path, Inches(7.033), Inches(2.15), width=Inches(5.3))

tb_desc2 = s14.shapes.add_textbox(Inches(7.033), Inches(5.15), Inches(5.3), Inches(1.4))
tf_d2 = tb_desc2.text_frame
tf_d2.word_wrap = True
add_bullet(tf_d2, "Four Real-Time Recharts Metrics:", "1. Alive Node Progression (FND and HND milestones)\n2. Aggregate Residual Energy vs Harvest Intake (Joules)\n3. Packet Delivery Ratio (PDR %)\n4. Jain's Fairness Index quantifying energy balance.", 9.5)

add_speaker_notes(s14, """
Slide 14 showcases the spatial heatmap and telemetry drawer.
Figure 3 on the left shows the 2D Spatial Energy Heatmap. Bright teal regions indicate sunlit areas where batteries are saturated. Dark purple regions highlight canopy shadows or relays undergoing heavy drainage. This allows researchers to see impending bottlenecks before a disconnection actually happens.
Figure 4 on the right shows the Analytics Drawer built with Recharts. It graphs four vital metrics in real-time: First Node Death (FND), total network residual energy, Packet Delivery Ratio (PDR), and Jain's Fairness Index.
""")

# ==============================================================================
# SLIDE 15: AUTOMATED TESTING & VERIFICATION SUITE (68/68 PASSING)
# ==============================================================================
s15 = prs.slides.add_slide(blank_layout)
add_header(s15, "Automated Verification Suite: 68/68 Unit Tests Passing", "Testbench Verification", 15)

# Left Column: Terminal Output Block (Dark theme)
add_card(s15, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1), bg_color=C_DARK_TERMINAL, border_color=C_NAVY_DARK)
tb = s15.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(5.3), Inches(4.8))
tf = tb.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.text = "pytest --rootdir=. -v  [Terminal Run]"
p.font.name = FONT_CODE
p.font.size = Pt(10)
p.font.bold = True
p.font.color.rgb = RGBColor(56, 189, 248) # Cyan

terminal_text = """============================= test session starts =============================
platform win32 -- Python 3.12.9, pytest-9.1.1
rootdir: C:\\Users\\Santhosh\\Documents\\antigravity\\WSN_proj
collected 68 items

tests/test_adversarial_counterexample.py ....                            [  5%]
tests/test_backend_api.py .........                                      [ 19%]
tests/test_brownout_and_failure.py .....                                 [ 26%]
tests/test_clustering.py .....                                           [ 33%]
tests/test_dp_lifetime.py ........                                       [ 45%]
tests/test_dsu_speedup.py ...                                            [ 50%]
tests/test_energy_aware_dijkstra.py ....                                 [ 55%]
tests/test_energy_model.py ......                                        [ 64%]
tests/test_energy_view.py ......                                         [ 73%]
tests/test_harvesting_clustering.py ....                                 [ 79%]
tests/test_harvesting_model.py .....                                     [ 86%]
tests/test_heterogeneous_harvesting.py ...                               [ 91%]
tests/test_network.py ....                                               [ 97%]
tests/test_routing.py ..                                                 [100%]

============================== 68 passed in 4.72s =============================="""

p2 = tf.add_paragraph()
p2.text = terminal_text
p2.font.name = FONT_CODE
p2.font.size = Pt(7.5)
p2.font.color.rgb = RGBColor(74, 222, 128) # Bright Green

# Right Column: Verification Matrix by Module
add_card(s15, Inches(6.833), Inches(1.6), Inches(5.7), Inches(5.1))
tb2 = s15.shapes.add_textbox(Inches(7.033), Inches(1.75), Inches(5.3), Inches(4.8))
tf2 = tb2.text_frame
tf2.word_wrap = True
p2_h = tf2.paragraphs[0]
p2_h.text = "Comprehensive Invariant Verification Matrix"
p2_h.font.name = FONT_HEADING
p2_h.font.size = Pt(14)
p2_h.font.bold = True
p2_h.font.color.rgb = C_NAVY_DARK
p2_h.space_after = Pt(6)

add_bullet(tf2, "Deterministic Proofs:", "test_adversarial_counterexample verifies Time-DP picks recharging relay B (0.040J) over Dijkstra relay A (0.030J).", 10)
add_bullet(tf2, "Radio Physics:", "test_energy_model validates d^2 / d^4 crossover at d0 = 87.7m and receiver electronic dissipation Erx = 50 nJ/bit.", 10)
add_bullet(tf2, "Fault Tolerance:", "test_brownout_and_failure confirms 100% PDR under 10% to 30% injected node deaths via DSU bridge repairs.", 10)
add_bullet(tf2, "DSU Speedup Benchmark:", "test_dsu_speedup confirms 3.8x to 6.1x execution speedup over full DP recomputation.", 10)
add_bullet(tf2, "Belief Distribution:", "test_energy_view confirms 24-bin histogram probability mass conservation (sum p = 1.0) and boundary clipping.", 10)
add_bullet(tf2, "Backend REST Endpoints:", "test_backend_api validates FastAPI simulation, benchmark sweeps, and SQLite persistence.", 10)

add_speaker_notes(s15, """
Slide 15 highlights our automated testing and verification suite.
To guarantee mathematical correctness and prevent regressions, our codebase includes 15 distinct pytest test suites with 68 comprehensive unit tests.
As shown on the left terminal capture, all 68 tests execute in 4.72 seconds with a 100% pass rate.
The verification matrix on the right covers every aspect of the project: deterministic counterexample validation, radio physics crossover verification, DSU fault recovery with zero packet loss, histogram probability conservation, and FastAPI REST endpoint validation.
""")

# ==============================================================================
# SLIDE 16: EMPIRICAL RESULT 1 — DETERMINISTIC 5-NODE COUNTEREXAMPLE
# ==============================================================================
s16 = prs.slides.add_slide(blank_layout)
add_header(s16, "Empirical Result 1: Deterministic 5-Node Proof Validation", "Empirical Findings", 16)

# Left Column: Embedded Counterexample Diagram
add_card(s16, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1))
tb = s16.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.3), Inches(0.4))
tf = tb.text_frame
p = tf.paragraphs[0]
p.text = "Isolating Mechanism from Simulation Noise"
p.font.name = FONT_HEADING
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = C_NAVY_DARK

cnt_path = os.path.join(RESULTS_DIR, "counterexample_5node.png")
if os.path.exists(cnt_path):
    s16.shapes.add_picture(cnt_path, Inches(1.0), Inches(2.2), width=Inches(5.3))

tb_c_desc = s16.shapes.add_textbox(Inches(1.0), Inches(5.5), Inches(5.3), Inches(1.1))
tf_cd = tb_c_desc.text_frame
tf_cd.word_wrap = True
add_bullet(tf_cd, "Canonical Topology:", "Source S must reach BS through Relay A (starts at 0.030J, zero recharge) or Relay B (starts at 0.005J, harvests +0.035J during transit).", 9.5)

# Right Column: Comparative Execution Table & Analysis
add_card(s16, Inches(6.833), Inches(1.6), Inches(5.7), Inches(5.1))
tb2 = s16.shapes.add_textbox(Inches(7.033), Inches(1.7), Inches(5.3), Inches(0.4))
tf2 = tb2.text_frame
p2 = tf2.paragraphs[0]
p2.text = "Algorithmic Decision Matrix & Ground Truth"
p2.font.name = FONT_HEADING
p2.font.size = Pt(13)
p2.font.bold = True
p2.font.color.rgb = C_NAVY_DARK

# Table of Counterexample Results
rows = 5
cols = 4
tbl_c = s16.shapes.add_table(rows, cols, Inches(7.033), Inches(2.2), Inches(5.3), Inches(2.6)).table
tbl_c.columns[0].width = Inches(1.6)
tbl_c.columns[1].width = Inches(1.1)
tbl_c.columns[2].width = Inches(1.1)
tbl_c.columns[3].width = Inches(1.5)

c_headers = ["Algorithm", "Chosen Route", "Bottleneck", "Outcome"]
for j, h in enumerate(c_headers):
    c = tbl_c.cell(0, j)
    c.fill.solid()
    c.fill.fore_color.rgb = C_NAVY_DARK
    p = c.text_frame.paragraphs[0]
    p.text = h
    p.font.name = FONT_HEADING
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

c_data = [
    ("Min-Hop Dijkstra", "S -> A -> BS", "0.030 J", "FAILS: Depletes A in 15 rounds"),
    ("Energy-Aware Dijkstra", "S -> A -> BS", "0.030 J", "FAILS: Rejects B at t=0 snapshot"),
    ("Classical Maximin DP", "S -> A -> BS", "0.030 J", "FAILS: Blind to solar refill"),
    ("Time-Augmented DP", "S -> B -> BS", "0.040 J", "SUCCEEDS: Route survives indefinitely!")
]

for i, row in enumerate(c_data):
    for j in range(4):
        cell = tbl_c.cell(i + 1, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_TEAL_LIGHT if i == 3 else (C_WHITE if i % 2 == 0 else C_CARD_BG)
        p = cell.text_frame.paragraphs[0]
        p.text = row[j]
        p.font.name = FONT_BODY
        p.font.size = Pt(8.5)
        if i == 3:
            p.font.bold = True
            p.font.color.rgb = C_TEAL
        else:
            p.font.color.rgb = C_NAVY_DARK

tb_concl = s16.shapes.add_textbox(Inches(7.033), Inches(4.9), Inches(5.3), Inches(1.7))
tf_con = tb_concl.text_frame
tf_con.word_wrap = True
add_bullet(tf_con, "Mathematical Proof:", "Time-DP projects Relay B will reach 0.040 J (+33.3% higher capacity) at arrival time t=1. It correctly routes through Relay B, achieving infinite route survival.", 9.5)
add_bullet(tf_con, "Why Baseline Fails:", "Dijkstra sees 0.005 J at t=0, labels B as critically weak, and funnels traffic through dying Relay A until network collapse.", 9.5)

add_speaker_notes(s16, """
Slide 16 details our deterministic 5-node counterexample proof from run_counterexample.py.
To prove our algorithmic advantage without statistical noise, we constructed a minimal 5-node topology: Source S must choose between Relay A and Relay B to reach the Base Station.
Relay A has 0.030 J but zero harvest. Relay B has only 0.005 J, but harvests +0.035 J per step.
Look at the table: Dijkstra, Energy-Aware Dijkstra, and Classical Maximin DP all choose Relay A because they only look at the t=0 snapshot. After 15 rounds, Relay A runs out of energy and the network dies.
Our Time-Augmented DP looks ahead to arrival time t=1, correctly computes that Relay B will reach 0.040 Joules, and routes through Relay B. The network survives indefinitely. This deterministically proves our theoretical claim.
""")

# Save checkpoint
prs.save("Final_Review_Presentation_WSN_Adaptive_Routing.pptx")
print("Saved Slide 11 to 16 checkpoint.")
# ==============================================================================
# SLIDE 17: EMPIRICAL RESULT 2 — DSU LIVE DETOUR SPEEDUP BENCHMARK
# ==============================================================================
s17 = prs.slides.add_slide(blank_layout)
add_header(s17, "Empirical Result 2: DSU Live Detour Speedup Benchmark", "Empirical Findings", 17)

# Left Column: Embedded DSU Benchmark Chart
add_card(s17, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1))
tb = s17.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.3), Inches(0.4))
tf = tb.text_frame
p = tf.paragraphs[0]
p.text = "Failure Rate vs Route Repair Latency"
p.font.name = FONT_HEADING
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = C_NAVY_DARK

dsu_img_path = os.path.join(RESULTS_DIR, "dsu_benchmark_speedup.png")
if os.path.exists(dsu_img_path):
    s17.shapes.add_picture(dsu_img_path, Inches(1.0), Inches(2.2), width=Inches(5.3))

tb_dsu_desc = s17.shapes.add_textbox(Inches(1.0), Inches(5.35), Inches(5.3), Inches(1.2))
tf_dd = tb_dsu_desc.text_frame
tf_dd.word_wrap = True
add_bullet(tf_dd, "Benchmark Setup:", "Evaluated across 500 failure injection trials under 10% to 30% randomly induced relay brownouts during active multi-hop packet transit.", 9.5)

# Right Column: Performance Analysis & Quantitative Gains
add_card(s17, Inches(6.833), Inches(1.6), Inches(5.7), Inches(5.1))
tb2 = s17.shapes.add_textbox(Inches(7.033), Inches(1.7), Inches(5.3), Inches(0.4))
tf2 = tb2.text_frame
p2 = tf2.paragraphs[0]
p2.text = "Quantitative Performance Breakdown"
p2.font.name = FONT_HEADING
p2.font.size = Pt(13)
p2.font.bold = True
p2.font.color.rgb = C_NAVY_DARK

# Key Metric Badges
m_data = [
    ("6.02x", "Latency Speedup", "0.85 ms (DSU) vs 5.12 ms (Full Time-DP)", C_TEAL),
    ("100%", "Packet Delivery Ratio", "Zero dropped packets across 500 failure trials", C_BLUE),
    ("O(deg u)", "Local Repair Time", "Inspects only immediate predecessor neighbors", C_NAVY_MED)
]

for idx, (val, label, sub, color) in enumerate(m_data):
    my = Inches(2.2) + idx * Inches(1.0)
    b_card = s17.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.033), my, Inches(5.3), Inches(0.85))
    b_card.fill.solid()
    b_card.fill.fore_color.rgb = C_CARD_BG
    b_card.line.color.rgb = color
    b_card.line.width = Pt(1.5)
    btf = b_card.text_frame
    btf.word_wrap = True
    btf.margin_left = Inches(0.2)
    btf.margin_top = Inches(0.1)
    
    bp1 = btf.paragraphs[0]
    bp1.text = f"{val}  -  {label}"
    bp1.font.name = FONT_HEADING
    bp1.font.size = Pt(13)
    bp1.font.bold = True
    bp1.font.color.rgb = color
    
    bp2 = btf.add_paragraph()
    bp2.text = sub
    bp2.font.name = FONT_BODY
    bp2.font.size = Pt(9.5)
    bp2.font.color.rgb = C_NAVY_DARK

tb_concl2 = s17.shapes.add_textbox(Inches(7.033), Inches(5.35), Inches(5.3), Inches(1.2))
tf_c2 = tb_concl2.text_frame
tf_c2.word_wrap = True
add_bullet(tf_c2, "Takeaway:", "DSU live detours eliminate the need for global state recomputation, reducing route repair latency by 6.02x while preserving in-flight packets that would otherwise be discarded.", 9.5)

add_speaker_notes(s17, """
Slide 17 highlights our DSU live detour benchmark from run_dsu_benchmark.py.
We injected random relay deaths mid-transmission at rates between 10% and 30%.
Without DSU, the network either drops the packet or must rerun the full 3D Dynamic Programming table from scratch, which takes 5.12 milliseconds.
With our local DSU detour algorithm, the predecessor node executes a bridge splice in only 0.85 milliseconds. That is a 6.02x latency reduction.
Furthermore, the Packet Delivery Ratio was sustained at 100%, proving that local graph partition data structures are ideal for embedded wireless networks.
""")

# ==============================================================================
# SLIDE 18: EMPIRICAL RESULT 3 — THE ELECTRONIC RECEPTION PENALTY (E_rx)
# ==============================================================================
s18 = prs.slides.add_slide(blank_layout)
add_header(s18, "Empirical Result 3: The Electronic Reception Penalty (E_rx)", "Scientific Discovery", 18)

# Left Card: Direct Link vs Two-Hop Link Calculations
add_card(s18, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1))
tb = s18.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(5.3), Inches(4.8))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "First-Order Radio Energy Balance (4000 Bits)"
p.font.name = FONT_HEADING
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY_DARK
p.space_after = Pt(6)

add_bullet(tf, "The Multi-Hop Routing Myth:", "Sensor network textbooks frequently claim multi-hop forwarding is universally superior because transmission energy scales with distance squared (d^2).", 10.5)
add_bullet(tf, "Direct Link (60 m):", "Transmitting directly over 60 meters:\nE_tx = 4000*(50 nJ) + 4000*(10 pJ/m^2)*(60 m)^2\n= 0.200 mJ + 0.144 mJ = 0.344 mJ.", 10.5)
add_bullet(tf, "Two-Hop Relay Link (30 m + 30 m):", "Transmitting via an intermediate relay:\n2 * E_tx(30m) + E_rx\n= 2 * [0.200 mJ + 0.036 mJ] + 0.200 mJ\n= 0.472 mJ + 0.200 mJ = 0.672 mJ.", 10.5)

# Highlight Callout
c_box = s18.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(5.0), Inches(5.3), Inches(1.5))
c_box.fill.solid()
c_box.fill.fore_color.rgb = C_RED
c_box.fill.transparency = 0.88
c_box.line.color.rgb = C_RED
c_box.line.width = Pt(1)
ctf = c_box.text_frame
ctf.word_wrap = True
cp = ctf.paragraphs[0]
cp.text = "DISCOVERY: RELAYING COSTS NEARLY 2x MORE ENERGY!"
cp.font.name = FONT_HEADING
cp.font.size = Pt(10)
cp.font.bold = True
cp.font.color.rgb = C_RED

cp2 = ctf.add_paragraph()
cp2.text = "Two-hop routing costs 0.672 mJ vs 0.344 mJ for direct transmission -- nearly twice as much total network energy! Relaying is only economical if d >= d0 = 87.7m or if the relay receives surplus solar energy."
cp2.font.name = FONT_BODY
cp2.font.size = Pt(9.5)
cp2.font.color.rgb = C_NAVY_DARK

# Right Card: The Macroscopic Network Dilemma
add_card(s18, Inches(6.833), Inches(1.6), Inches(5.7), Inches(5.1))
tb2 = s18.shapes.add_textbox(Inches(7.033), Inches(1.75), Inches(5.3), Inches(4.8))
tf2 = tb2.text_frame
tf2.word_wrap = True
p2 = tf2.paragraphs[0]
p2.text = "The Macroscopic Dilemma: Single-Path vs Global"
p2.font.name = FONT_HEADING
p2.font.size = Pt(14)
p2.font.bold = True
p2.font.color.rgb = C_NAVY_DARK
p2.space_after = Pt(6)

add_bullet(tf2, "Single-Path Maximin Optimality:", "Our Time-DP mathematically maximizes the bottleneck residual energy along an isolated route P*. This guarantees no link fails due to insufficient battery during traversal.", 10.5)
add_bullet(tf2, "Uncoordinated Traffic Funneling:", "When all cluster heads independently identify the same sunlit relays as attractive forwarders, they simultaneously funnel traffic through them. This dissipates harvested energy faster than it can recharge!", 10.5)
add_bullet(tf2, "Multi-Seed Evaluation (N = 30 Seeds):", "Evaluated across 30 independent random topologies (run_multiseed.py). FND for Time-DP = 98.5 +/- 6.5 rounds vs Dijkstra = 97.9 +/- 7.4 rounds (p = 0.666). In dense networks, direct transmission preserves more aggregate energy.", 10.5)
add_bullet(tf2, "Honest Scientific Takeaway:", "Lookahead routing provides decisive gains under stochastic variance and canopy occlusion, but must account for receiver dissipation E_rx to prevent wasteful over-relaying.", 10.5)

add_speaker_notes(s18, """
Slide 18 presents what we consider our most insightful scientific discovery: the Electronic Reception Penalty trade-off.
Many papers assume that multi-hop is always better than single-hop. But look at the math on the left:
Transmitting directly over 60 meters costs 0.344 millijoules.
Splitting that into two 30-meter hops requires 0.472 millijoules of transmission plus 0.200 millijoules of receiver dissipation E_rx. That totals 0.672 millijoules—nearly double the direct cost!
This reveals that multi-hop routing actually wastes network energy unless the link spans into the d^4 multipath fading regime beyond 87.7 meters, or unless the relay is receiving surplus solar energy.
Our Time-DP router is one of the few algorithms that explicitly incorporates E_rx into its recurrence, preventing wasteful relay detours.
""")

# ==============================================================================
# SLIDE 19: THEORETICAL RIGOR — OPTIMALITY & APPROXIMATION BOUNDS
# ==============================================================================
s19 = prs.slides.add_slide(blank_layout)
add_header(s19, "Theoretical Rigor: Bellman Optimality & 2-Eps Bound", "Formal Proofs", 19)

# Left Card: Theorem 1 (Bellman Optimality on Time-Expanded DAG)
add_card(s19, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1))
tb = s19.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(5.3), Inches(4.8))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "Theorem 1: Bellman Optimality on DAG G_T"
p.font.name = FONT_HEADING
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = C_NAVY_DARK
p.space_after = Pt(6)

add_bullet(tf, "Time-Expanded Directed Acyclic Graph (G_T):", "V_T = {(v, h, t)}, E_T = {((u, h-1, t-delta), (v, h, t))}. Because every edge strictly increments hop h by +1 and time t by +delta (delta >= 1), G_T contains strictly zero directed cycles.", 10)
add_bullet(tf, "Monotonicity of Maximin Substructure:", "The bottleneck capacity B(P) decomposes as min(B(P_prev), E_proj). Because scalar min(a, c) is monotonically non-decreasing in a (a >= a' implies min(a, c) >= min(a', c)), the optimal substructure property strictly holds.", 10)
add_bullet(tf, "Proof Conclusion:", "Dynamic programming on topologically sorted G_T provably computes the globally optimal maximin bottleneck path without cyclic dependency.", 10)

# Right Card: Theorem 2 (2-Eps Approximation Bound)
add_card(s19, Inches(6.833), Inches(1.6), Inches(5.7), Inches(5.1))
tb2 = s19.shapes.add_textbox(Inches(7.033), Inches(1.75), Inches(5.3), Inches(4.8))
tf2 = tb2.text_frame
tf2.word_wrap = True
p2 = tf2.paragraphs[0]
p2.text = "Theorem 2: 2-Epsilon Approximation Bound"
p2.font.name = FONT_HEADING
p2.font.size = Pt(13)
p2.font.bold = True
p2.font.color.rgb = C_NAVY_DARK
p2.space_after = Pt(6)

add_bullet(tf2, "Bounded Stochastic Harvest Variance:", "Let true harvest be H_v(t) = H_hat_v(t) + xi_v(t), where estimation error is bounded: |xi_v(t)| <= epsilon.", 10)
add_bullet(tf2, "Theoretical Guarantee Statement:", "Under bounded forecast error epsilon, the path P_DP selected by Time-DP achieves a realized bottleneck within 2-epsilon of an omniscient offline oracle P*:", 10)

# Embed Equation 7 image if available
eq7_path = os.path.join(EQ_DIR, "eq_7.png")
if os.path.exists(eq7_path):
    s19.shapes.add_picture(eq7_path, Inches(7.033), Inches(3.6), width=Inches(5.3))

tb_pf = s19.shapes.add_textbox(Inches(7.033), Inches(4.3), Inches(5.3), Inches(2.2))
tf_pf = tb_pf.text_frame
tf_pf.word_wrap = True
add_bullet(tf_pf, "Mathematical Proof Sketch:", "1. Estimated bottleneck satisfies |B_hat(P) - B(P)| <= epsilon.\n2. By DP maximization: B_hat(P_DP) >= B_hat(P*).\n3. B(P_DP) >= B_hat(P_DP) - epsilon >= B_hat(P*) - epsilon >= (B(P*) - epsilon) - epsilon = B(P*) - 2*epsilon. Q.E.D.", 10)

add_speaker_notes(s19, """
Slide 19 establishes our mathematical rigor through two formal theorems.
Theorem 1 proves Bellman Optimality. Because every hop in our time-expanded state space increments time by at least one slot, the state graph is a Directed Acyclic Graph (DAG) with no cycles. The min-operator preserves optimal substructure, guaranteeing global maximin optimality.
Theorem 2 establishes a 2-epsilon approximation bound under bounded harvest forecasting errors. Even if actual solar intake varies by +/- epsilon, our polynomial DP guarantees a realized bottleneck within 2-epsilon of an omniscient offline oracle with perfect foresight.
""")

# ==============================================================================
# SLIDE 20: MILESTONE DELIVERABLES STATUS & PUBLICATION ROADMAP
# ==============================================================================
s20 = prs.slides.add_slide(blank_layout)
add_header(s20, "Milestone Deliverables Status & Publication Roadmap", "Project Status", 20)

# Deliverables Table
rows = 6
cols = 4
tbl_d = s20.shapes.add_table(rows, cols, Inches(0.8), Inches(1.6), Inches(11.733), Inches(3.4)).table
tbl_d.columns[0].width = Inches(2.2)
tbl_d.columns[1].width = Inches(3.8)
tbl_d.columns[2].width = Inches(1.8)
tbl_d.columns[3].width = Inches(3.933)

d_headers = ["Milestone", "Technical Specification", "Status", "Verification Evidence"]
for j, h in enumerate(d_headers):
    c = tbl_d.cell(0, j)
    c.fill.solid()
    c.fill.fore_color.rgb = C_NAVY_DARK
    p = c.text_frame.paragraphs[0]
    p.text = h
    p.font.name = FONT_HEADING
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

deliv_data = [
    ("Core Simulation Engine", "Heinzelman radio physics, diurnal solar, canopy shadows", "100% Completed", "src/network.py, src/energy_model.py, verified"),
    ("Lookahead 3D DP Router", "Time-expanded DAG maximin DP with backpointers", "100% Completed", "src/dp_lifetime.py, <5.2 ms, <48 KB RAM"),
    ("Fault Recovery (DSU)", "Path compression & rank Union-Find local splicing", "100% Completed", "6.02x latency speedup, 100% PDR sustained"),
    ("Dynamic Clustering", "EH-LEACH harvest-weighted threshold T(n)", "100% Completed", "src/clustering.py, 2.4x sunlit election boost"),
    ("Interactive Web Suite", "React 19 + FastAPI + SQLite persistence + SVG canvas", "100% Completed", "Production build verified; live scrubber & heatmaps")
]

for i, row in enumerate(deliv_data):
    for j in range(4):
        cell = tbl_d.cell(i + 1, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_TEAL_LIGHT if j == 2 else (C_WHITE if i % 2 == 0 else C_CARD_BG)
        p = cell.text_frame.paragraphs[0]
        p.text = row[j]
        p.font.name = FONT_BODY
        p.font.size = Pt(9.5)
        if j == 2:
            p.font.bold = True
            p.font.color.rgb = C_TEAL
        else:
            p.font.color.rgb = C_NAVY_DARK

# Bottom Publication Blueprint Card
add_card(s20, Inches(0.8), Inches(5.2), Inches(11.733), Inches(1.5), bg_color=C_BLUE_LIGHT, border_color=C_BLUE)
tb = s20.shapes.add_textbox(Inches(1.0), Inches(5.25), Inches(11.333), Inches(1.4))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "PUBLICATION BLUEPRINT & TARGET VENUES (2026–2027):"
p.font.name = FONT_HEADING
p.font.size = Pt(10.5)
p.font.bold = True
p.font.color.rgb = C_BLUE

p2 = tf.add_paragraph()
p2.text = "- Recommended Paper Title: 'Adaptive Lookahead Routing, First-Order Radio Dissipation Trade-Offs, and DSU-Based Live Detour Recovery in Energy-Harvesting Wireless Sensor Networks'\n- Primary Target: IEEE Sensors Journal (SCI Q1, IF: 4.3) -- ideal focus on energy harvesting sensor networks.\n- Alternative Targets: Elsevier Ad Hoc Networks (SCI Q1, IF: 4.8) or IEEE Internet of Things Journal (SCI Q1, IF: 10.6).\n- Hardware Testbed Roadmap: Compiling algorithmic core into C/C++ for hardware evaluation on ESP32 / MicaZ motes."
p2.font.name = FONT_BODY
p2.font.size = Pt(9.5)
p2.font.color.rgb = C_NAVY_DARK

add_speaker_notes(s20, """
Slide 20 summarizes our completed deliverables and future roadmap.
All five major project milestones are 100% complete and fully verified.
Looking forward, our publication blueprint targets IEEE Sensors Journal or Elsevier Ad Hoc Networks. The paper will present our 3D Time-Augmented DP, our 6.02x DSU detour speedup, and our empirical findings regarding receiver dissipation E_rx.
We also plan to port the core C/C++ algorithms onto real ESP32 and MicaZ motes for physical testbed validation.
""")

# ==============================================================================
# SLIDE 21: CONCLUSION & Q&A DEFENSE SLIDE (Dark Navy Theme)
# ==============================================================================
s21 = prs.slides.add_slide(blank_layout)
bg21 = s21.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
bg21.fill.solid()
bg21.fill.fore_color.rgb = C_NAVY_DARK
bg21.line.fill.background()

# Top pill
t_pill = s21.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(0.8), Inches(3.2), Inches(0.35))
t_pill.fill.solid()
t_pill.fill.fore_color.rgb = RGBColor(17, 34, 64)
t_pill.line.color.rgb = C_TEAL
t_pill.line.width = Pt(1)
t_ptf = t_pill.text_frame
p = t_ptf.paragraphs[0]
p.text = "CAPSTONE DEFENSE CONCLUDED"
p.font.name = FONT_HEADING
p.font.size = Pt(10)
p.font.bold = True
p.font.color.rgb = C_TEAL
p.alignment = PP_ALIGN.CENTER

# Main Title
tb = s21.shapes.add_textbox(Inches(1.0), Inches(1.3), Inches(11.333), Inches(1.5))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "Thank You! Questions & Discussion"
p.font.name = FONT_HEADING
p.font.size = Pt(34)
p.font.bold = True
p.font.color.rgb = C_WHITE

p2 = tf.add_paragraph()
p2.text = "Adaptive Routing in Energy-Harvesting Wireless Sensor Networks"
p2.font.name = FONT_BODY
p2.font.size = Pt(14)
p2.font.color.rgb = RGBColor(148, 163, 184)

# 4 Key Takeaway Cards
summary_points = [
    ("3D Lookahead Routing", "Solves the False Rejection Flaw by projecting solar recharge during hop transit in O(|E|HT) polynomial time.", C_TEAL),
    ("6.02x DSU Fault Recovery", "Splicing local detour bridges in 0.85 ms using Union-Find with path compression, achieving 100% PDR.", C_BLUE),
    ("E_rx Reception Penalty", "Discovered that multi-hop relaying costs ~2x more energy under 87.7m unless sustained by solar recharge.", C_AMBER),
    ("Production Full-Stack Platform", "React 19 interactive SVG dashboard, FastAPI service, and 68/68 passing pytest testbench.", C_WHITE)
]

for i, (title, desc, color) in enumerate(summary_points):
    cx = Inches(1.0) + (i % 2) * Inches(5.8)
    cy = Inches(3.0) + (i // 2) * Inches(1.8)
    
    c = s21.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx, cy, Inches(5.5), Inches(1.5))
    c.fill.solid()
    c.fill.fore_color.rgb = RGBColor(30, 41, 59)
    c.line.color.rgb = RGBColor(51, 65, 85)
    c.line.width = Pt(1)
    
    ctf = c.text_frame
    ctf.word_wrap = True
    ctf.margin_left = Inches(0.2)
    ctf.margin_top = Inches(0.15)
    
    cp1 = ctf.paragraphs[0]
    cp1.text = title
    cp1.font.name = FONT_HEADING
    cp1.font.size = Pt(13)
    cp1.font.bold = True
    cp1.font.color.rgb = color
    
    cp2 = ctf.add_paragraph()
    cp2.text = desc
    cp2.font.name = FONT_BODY
    cp2.font.size = Pt(10)
    cp2.font.color.rgb = RGBColor(203, 213, 225)
    cp2.space_before = Pt(4)

# Bottom Student Bar
b_tb = s21.shapes.add_textbox(Inches(1.0), Inches(6.6), Inches(11.333), Inches(0.5))
b_tf = b_tb.text_frame
b_p = b_tf.paragraphs[0]
b_p.text = "Presenters: Santhosh G (25BEL0016), Thilang T V (25BEL0036), Ananthakrishnan R (25BEL0005)  |  VIT Vellore  |  GitHub: WSN_proj"
b_p.font.name = FONT_BODY
b_p.font.size = Pt(10)
b_p.font.color.rgb = RGBColor(148, 163, 184)

add_speaker_notes(s21, """
Thank you, respected professors and members of the panel, for your time and attention.
In summary, our project has successfully unified fundamental Data Structures and Algorithms with physical wireless sensor networks:
1. 3D Time-Augmented Dynamic Programming eliminates the False Rejection Flaw.
2. Disjoint-Set Union local detours deliver a 6.02x latency speedup during in-flight failures with zero dropped packets.
3. Our first-order radio modeling discovered the critical role of electronic reception dissipation E_rx.
4. And our full-stack React 19 and FastAPI platform makes the entire framework interactive, verifiable, and reproducible.
We are now ready to take your questions.
""")

# ==============================================================================
# FINAL SAVE & EXPORT
# ==============================================================================
output_pptx_path = os.path.join(BASE_DIR, "Final_Review_Presentation_WSN_Adaptive_Routing.pptx")
prs.save(output_pptx_path)
print(f"Presentation successfully compiled to: {output_pptx_path}")

# Also copy to Downloads folder for convenient user access
downloads_path = r"C:\Users\Santhosh\Downloads\Final_Review_Presentation_WSN_Adaptive_Routing.pptx"
try:
    import shutil
    shutil.copyfile(output_pptx_path, downloads_path)
    print(f"Copied presentation to Downloads: {downloads_path}")
except Exception as e:
    print(f"Warning: Could not copy to Downloads: {e}")
