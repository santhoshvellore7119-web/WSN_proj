import os
import sys
import shutil
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
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
C_AMBER_LIGHT = RGBColor(254, 243, 199)  # #FEF3C7 (Amber tint bg)
C_RED = RGBColor(220, 38, 38)            # #DC2626 (Failure, Brownout)
C_RED_LIGHT = RGBColor(254, 242, 242)    # #FEF2F2 (Red tint bg)
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
    """Draws standardized humanized corporate header, category pill badge, and running footer."""
    pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.35), Inches(3.6), Inches(0.3))
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

    tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.68), Inches(11.7), Inches(0.65))
    tf_t = tb.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = title
    p_t.font.name = FONT_HEADING
    p_t.font.size = Pt(21)
    p_t.font.bold = True
    p_t.font.color.rgb = C_NAVY_DARK

    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.36), Inches(11.733), Inches(0.015))
    line.fill.solid()
    line.fill.fore_color.rgb = C_CARD_BORDER
    line.line.fill.background()

    f_tb = slide.shapes.add_textbox(Inches(0.8), Inches(7.0), Inches(10.2), Inches(0.35))
    f_tf = f_tb.text_frame
    f_p = f_tf.paragraphs[0]
    f_p.text = "Adaptive Routing in EH-WSNs  |  Santhosh G (25BEL0016), Thilang T V (25BEL0036), Ananthakrishnan R (25BEL0005)"
    f_p.font.name = FONT_BODY
    f_p.font.size = Pt(8.5)
    f_p.font.color.rgb = C_SLATE_MUTED

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
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1)
    return card

def add_speaker_notes(slide, notes_text):
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = notes_text.strip()

def add_bullet(tf, bold_prefix, text, pt_size=11, space_after=6, text_color=C_NAVY_DARK):
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

print("Base setup ready.")
# ==============================================================================
# SLIDE 1: TITLE SLIDE (Dark Navy Premium Theme with Human Narrative Subtitle)
# ==============================================================================
s1 = prs.slides.add_slide(blank_layout)
bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
bg1.fill.solid()
bg1.fill.fore_color.rgb = C_NAVY_DARK
bg1.line.fill.background()

# Title badge
t_pill = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(1.0), Inches(4.3), Inches(0.4))
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

# Main Title text
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
p2.text = "Teaching sensor networks to look ahead in time, anticipate solar recharge, and recover from failures on the fly."
p2.font.name = FONT_BODY
p2.font.size = Pt(15)
p2.font.color.rgb = RGBColor(148, 163, 184)
p2.space_before = Pt(8)

# Team Member Cards
members = [
    ("Santhosh G", "25BEL0016", "3D Lookahead DP (dp[v][h][t])\n24-Bin Belief Filter & Sim Core"),
    ("Thilang T V", "25BEL0036", "Live DSU Detour Recovery\nFastAPI REST Backend & React 19 UI"),
    ("Ananthakrishnan R", "25BEL0005", "Heinzelman Radio Physics\nSolar Harvesting Profiles & Pytest Suite")
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
Good morning, respected professors and members of the panel. 
Today, my teammates Thilang, Ananthakrishnan, and I, Santhosh, are excited to present our Final Capstone Defense on 'Adaptive Routing in Energy-Harvesting Wireless Sensor Networks'.
Let me start with a simple real-life analogy: if you know your phone has only 5% battery, but you're plugging it into a fast charger right now, you wouldn't throw it away.
Yet for over 20 years, standard sensor network routing algorithms have been doing exactly that - rejecting nodes that are actively recharging because they only look at a static snapshot of the past.
In this project, we designed, built, and verified a complete DSA and software framework that teaches routing to look ahead in time, fixes mid-flight relay deaths on the fly, and exposes hidden radio physics that standard textbooks miss.
We will now walk you through the problem, our algorithms, the codebase, and our empirical results.
""")

# ==============================================================================
# SLIDE 2: THE CORE IDEA IN 60 SECONDS (Humanized Elevator Pitch)
# ==============================================================================
s2 = prs.slides.add_slide(blank_layout)
add_header(s2, "The Big Idea: What Happens When Sensors Recharge Themselves?", "The Elevator Pitch", 2)

# Left Card: The Old Assumption vs The Real World
add_card(s2, Inches(0.8), Inches(1.6), Inches(5.7), Inches(4.3))
tb = s2.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(5.3), Inches(4.0))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "The Old Rule vs. The Solar Reality"
p.font.name = FONT_HEADING
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY_DARK
p.space_after = Pt(8)

add_bullet(tf, "The AA Battery Assumption:", "For decades, sensor protocols assumed battery power only drains down. When energy hits zero, the node is dead forever.", 11)
add_bullet(tf, "The Solar Reality:", "Modern environmental motes have small solar cells. Their energy fluctuates dynamically: recharging during daylight hours and dipping at night.", 11)
add_bullet(tf, "The Big Blindspot:", "Standard algorithms like Dijkstra evaluate nodes on a frozen snapshot of residual battery at round start. They treat actively reviving nodes as if they are dying!", 11)
add_bullet(tf, "Why Not Just Use AI / Machine Learning?", "Heavy Deep Q-Networks require >1 MB of memory and heavy matrix math. Real 32-bit Cortex-M motes possess only 4 to 48 KB of RAM!", 11)

# Right Card: What We Built to Fix It
add_card(s2, Inches(6.833), Inches(1.6), Inches(5.7), Inches(4.3))
tb = s2.shapes.add_textbox(Inches(7.033), Inches(1.75), Inches(5.3), Inches(4.0))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "What We Built to Fix It"
p.font.name = FONT_HEADING
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY_DARK
p.space_after = Pt(8)

add_bullet(tf, "1. 3D Lookahead DP:", "Plans routes based on the energy a relay will have when packets arrive (h hops later), not what it has now. Runs in strictly O(|E|HT) polynomial time.", 11)
add_bullet(tf, "2. Instant DSU Live Detours:", "When an intermediate relay dies mid-flight, Union-Find splices a bridge from immediate neighbors in 0.85 ms with 0% packet loss.", 11)
add_bullet(tf, "3. Solar-Smart Clustering (EH-LEACH):", "Elects cluster heads from sunlit nodes 2.4x more frequently, letting shaded nodes rest as low-power listeners.", 11)
add_bullet(tf, "4. Interactive Full-Stack Suite:", "A headless simulation core coupled to FastAPI and a React 19 dashboard with round-by-round time-travel scrubbing and heatmaps.", 11)

# Bottom Metrics Ribbon
ribbon = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.05), Inches(11.733), Inches(0.8))
ribbon.fill.solid()
ribbon.fill.fore_color.rgb = C_TEAL_LIGHT
ribbon.line.color.rgb = C_TEAL
ribbon.line.width = Pt(1)
rtf = ribbon.text_frame
rtf.word_wrap = True
rp = rtf.paragraphs[0]
rp.text = "PROVEN NUMBERS:  68/68 Pytest Tests Passing (100%)  |  6.02x Faster Route Repairs  |  < 5.2 ms Latency  |  < 48 KB RAM Footprint"
rp.font.name = FONT_HEADING
rp.font.size = Pt(10.5)
rp.font.bold = True
rp.font.color.rgb = C_TEAL
rp.alignment = PP_ALIGN.CENTER

add_speaker_notes(s2, """
On Slide 2, we summarize the entire motivation in 60 seconds.
In classical sensor networks, battery energy only goes in one direction: down. But modern environmental sensors have solar cells. 
Data packets take time to travel across hops. A relay node that has only 5% battery right now might be in bright morning sun and reach 40% by the time our packet actually arrives two hops later.
Dijkstra looks at the 5% snapshot, labels it dangerous, and forces a wasteful 4-hop detour around it.
We solved this using fundamental computer science: a 3D Dynamic Programming algorithm that looks ahead in time, and an instant Union-Find detour algorithm that repairs mid-flight failures in less than a millisecond.
Our whole system runs in under 48 KB of RAM and is backed by 68 passing unit tests.
""")

# ==============================================================================
# SLIDE 3: TWO COSTLY MISTAKES OLD ALGORITHMS MAKE
# ==============================================================================
s3 = prs.slides.add_slide(blank_layout)
add_header(s3, "Two Costly Mistakes: Why Dijkstra Breaks on Solar Sensors", "The Problem in Action", 3)

pitfalls = [
    ("Mistake 1: The False Alarm", C_RED, [
        ("The Setup:", "Relay B has only 5% battery at 8:00 AM. Source S needs to send sensor data 2 hops away."),
        ("What Dijkstra Does:", "Dijkstra checks residual battery at t = 0, declares Relay B 'critically low', and routes packets onto a long 4-hop detour."),
        ("What Actually Happens:", "By 8:05 AM (Hop 2), morning sunlight recharged Relay B to 40%! Dijkstra threw away a perfectly good, short path based on outdated past data.")
    ]),
    ("Mistake 2: The Shaded Trap", C_AMBER, [
        ("The Setup:", "Relay A sits under dense tree shade. It starts with 80% battery."),
        ("What Dijkstra Does:", "Dijkstra sees 80% battery, thinks Relay A is strong, and continuously funnels heavy multi-hop traffic through it."),
        ("The Fatal Crash:", "Because Relay A gets zero sunlight, it burns out completely by noon, splitting the network in two while sunny nodes sat idle.")
    ]),
    ("Why Machine Learning Fails Here", C_NAVY_DARK, [
        ("The ML Promise:", "Deep Reinforcement Learning (DQN) can learn stochastic solar refill patterns."),
        ("The Embedded Reality:", "A sensor mote uses a 32-bit ARM Cortex-M or MSP430 microcontroller with 4 KB to 48 KB of RAM! Neural network weights take over 1 MB."),
        ("Our Insight:", "We need deterministic, lightweight Data Structures & Algorithms that run in milliseconds within tens of kilobytes of memory.")
    ])
]

c_w = Inches(3.7)
c_h = Inches(5.1)
for i, (title, accent, bullets) in enumerate(pitfalls):
    cx = Inches(0.8) + i * Inches(4.0)
    c = add_card(s3, cx, Inches(1.6), c_w, c_h)
    
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
    
    tb = s3.shapes.add_textbox(cx + Inches(0.15), Inches(2.15), c_w - Inches(0.3), c_h - Inches(0.65))
    tf = tb.text_frame
    tf.word_wrap = True
    for prefix, body in bullets:
        add_bullet(tf, prefix, body, 10, space_after=8)

add_speaker_notes(s3, """
Slide 3 breaks down the two biggest mistakes standard routing algorithms make in solar networks.
First is 'The False Alarm': imagine skipping a bus stop because the bus hasn't arrived yet, even though it's pulling up right in front of you. That's what Dijkstra does to recharging nodes. It sees low battery at t=0 and takes a long detour, ignoring that the node is actively recharging.
Second is 'The Shaded Trap': a node under a mango tree starts at 80% battery. Dijkstra thinks it's healthy, routes all traffic through it, and drains it to zero, splitting the network in half.
And why not just use Deep Learning? Because an IoT sensor has 4 to 48 KB of RAM. A neural network model takes megabytes! We solved this using pure, efficient algorithms.
""")

# ==============================================================================
# SLIDE 4: WHAT WE LEARNED FROM 5 YEARS OF RESEARCH PAPERS (2020-2025)
# ==============================================================================
s4 = prs.slides.add_slide(blank_layout)
add_header(s4, "What 9 Recent Research Papers Missed (2020-2025)", "Academic Context", 4)

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

headers = ["Paper & Authors", "Venue & Year", "What They Tried", "The Critical Flaw We Caught"]
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

papers = [
    ("Adaptive Clustering for EH-WSNs\nB. Han, et al.", "MDPI Sensors\n(2022)", "Weighted cluster head election by instantaneous solar intake.", "Completely ignored multi-hop transit delay delta-t! Assumes all deliveries happen instantly."),
    ("Throughput in Time-Expanded Graphs\nR. Tan, et al.", "ACM TOSN\n(2021)", "Time-expanded graph with Integer Linear Programming (ILP).", "Centralized offline solver on a server. You cannot run an ILP solver on a distributed sensor node!"),
    ("Harvested Energy Prediction in WSNs\nD. K. Sah, T. Amgoth", "IEEE Sensors J.\n(2023)", "EWMA solar irradiance forecasting for edge costing.", "Fed forecasts into standard Dijkstra, falling straight into the False Alarm trap."),
    ("Deep RL for Energy-Efficient Routing\nM. A. Aref, S. K. Jayaweera", "IEEE TCCN\n(2023)", "Deep Q-Networks (DQN) for stochastic energy routing.", "Heavy neural network weights (>1 MB). Impossible to run on 8/32-bit sensor motes with 10 KB RAM."),
    ("Our Framework (This Project)\nSanthosh, Thilang, Ananthakrishnan", "Final Defense\n(2026)", "3D Lookahead DP + DSU Live Detours + 24-Bin Belief Filter.", "Solves transit recharge in O(|E|HT) polynomial time with <48 KB RAM and 6.02x live detour speedup.")
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
p.text = "THE RESEARCH GAP WE BRIDGED:"
p.font.name = FONT_HEADING
p.font.size = Pt(10)
p.font.bold = True
p.font.color.rgb = C_BLUE

p2 = tf.add_paragraph()
p2.text = "Existing literature either ignored transit time, used centralized offline supercomputers (ILP), or used bloated deep neural networks. Our framework is the first to achieve lookahead recharge awareness and live fault recovery using lightweight, deterministic DSA that easily runs on embedded microcontrollers."
p2.font.name = FONT_BODY
p2.font.size = Pt(10)
p2.font.color.rgb = C_NAVY_MED

add_speaker_notes(s4, """
Slide 4 summarizes what we learned from surveying 9 key research papers published between 2020 and 2025 across IEEE, ACM, and MDPI.
We noticed three major issues:
First, authors like Han et al. in MDPI Sensors weighted cluster heads by solar power, but assumed packets arrive instantaneously, completely ignoring multi-hop delay.
Second, authors like Tan et al. in ACM used time-expanded graphs, but solved them with Integer Linear Programming - which is an offline solver that cannot run on a real sensor node in a field.
Third, authors like Aref in IEEE used Deep Reinforcement Learning. But their neural network models require over 1 megabyte of memory, which completely overflows the 4 to 10 kilobytes of RAM on real sensor motes.
Our project bridges this gap: a practical, distributed algorithm that runs in under 48 kilobytes of RAM.
""")

# ==============================================================================
# SLIDE 5: THE PHYSICS UNDER THE HOOD: RADIO HARDWARE & THE RECEIVER TAX
# ==============================================================================
s5 = prs.slides.add_slide(blank_layout)
add_header(s5, "The Physics: Heinzelman's Radio Model & The Receiver Tax", "Hardware Realism", 5)

# Left Card: Theoretical Model & Formulas
add_card(s5, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1))
tb = s5.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(5.3), Inches(4.8))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "Physical Radio Model (Texas Instruments CC2420)"
p.font.name = FONT_HEADING
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY_DARK
p.space_after = Pt(8)

add_bullet(tf, "Real Physical Wireless Hardware:", "Rather than toy unit-costs, our simulator implements the physical first-order radio dissipation model of Heinzelman et al.", 11)

# Embed Equation 5 image if available
eq5_path = os.path.join(EQ_DIR, "eq_5.png")
if os.path.exists(eq5_path):
    s5.shapes.add_picture(eq5_path, Inches(1.0), Inches(2.85), width=Inches(5.3))

tb_sub = s5.shapes.add_textbox(Inches(1.0), Inches(3.6), Inches(5.3), Inches(3.0))
tf_sub = tb_sub.text_frame
tf_sub.word_wrap = True
add_bullet(tf_sub, "Two Distinct Range Regimes:", "When transmission distance d < 87.7m (free-space), power loss scales with d^2. When distance exceeds 87.7m, multipath ground interference steepens power loss to d^4.", 10.5)
add_bullet(tf_sub, "The Hidden Receiver Tax (E_rx):", "Every intermediate relay burns Erx = k * E_elec simply keeping its radio receiver awake to capture a packet. For 4000 bits, Erx = 0.200 mJ. This reception tax is crucial!", 10.5)

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

add_bullet(tf, "Electronic Circuitry (E_elec):", "50.0 nJ/bit -- energy to run transmitter & receiver digital baseband.", 11)
add_bullet(tf, "Free-Space RF Amplifier (eps_fs):", "10.0 pJ/bit/m^2 -- power amplification when line-of-sight holds.", 11)
add_bullet(tf, "Multipath RF Amplifier (eps_mp):", "0.0013 pJ/bit/m^4 -- power amplification when ground clutter scatters RF.", 11)
add_bullet(tf, "Crossover Boundary (d0):", "d0 = sqrt(eps_fs / eps_mp) = 87.70 meters.", 11)

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
cp.text = "THE INTUITIVE HARDWARE REALITY:"
cp.font.name = FONT_HEADING
cp.font.size = Pt(10)
cp.font.bold = True
cp.font.color.rgb = C_AMBER

cp2 = ctf.add_paragraph()
cp2.text = "In a 100m x 100m sensor field, most nodes are 20m to 40m apart (well under d0 = 87.7m). In this zone, adding an extra hop adds an unavoidable 0.200 mJ receiver tax! Relaying is NOT always greener unless the node is actively recharging."
cp2.font.name = FONT_BODY
cp2.font.size = Pt(9.5)
cp2.font.color.rgb = C_NAVY_DARK

add_speaker_notes(s5, """
Slide 5 covers the physical radio hardware modeled in src/energy_model.py.
Rather than assuming radio transmission is just a magic unit number, we implemented Heinzelman's first-order radio model, which is the gold standard for Texas Instruments CC2420 transceiver motes.
Notice two key things:
First, the crossover distance d0 is 87.7 meters. Below 87.7 meters, power loss scales with distance squared. Beyond that, it steepens to distance to the 4th power.
Second, look at the receiver tax Erx: every time an intermediate relay receives a 4000-bit packet, it burns 0.200 millijoules just powering its listening radio. As we will show later, this receiver tax completely changes whether multi-hop relaying is worthwhile.
""")

# ==============================================================================
# SLIDE 6: SIMULATING REAL WEATHER: CLOUDS, TREE SHADOWS & DAY-NIGHT CYCLES
# ==============================================================================
s6 = prs.slides.add_slide(blank_layout)
add_header(s6, "Simulating Real Weather: Clouds, Tree Shadows & Day-Night Cycles", "Weather Engine", 6)

regimes = [
    ("1. The 24-Hour Solar Day", C_TEAL, [
        ("The Mechanism:", "Simulates realistic diurnal solar cycles (1 round = 1 hour)."),
        ("The Math:", "Solar irradiance follows a clipped half-sine wave: sunrise at Round 6, peaking at 0.035 J/round at midday (Round 12), and zero at night (Rounds 19 to 23)."),
        ("Why It Matters:", "Tests whether algorithms can store daytime energy to survive the dark nighttime hours.")
    ]),
    ("2. Spatial Tree Canopy Shadows", C_AMBER, [
        ("The Mechanism:", "Simulates uneven tree foliage or building shadows across the field."),
        ("The Math:", "Parameterized by shadow probability p_shadow in [0, 1]. Shaded nodes receive only 10% of incoming sunlight."),
        ("Why It Matters:", "Creates realistic spatial inequality: sunny relays recharge continuously while shaded relays must be conserved.")
    ]),
    ("3. Bursty Ambient Energy", C_BLUE, [
        ("The Mechanism:", "Models sporadic ambient power sources like indoor light, vibration, or RF harvesting."),
        ("The Math:", "Energy arrives in unpredictable Poisson bursts with arrival rate lambda and discrete quantum size q."),
        ("Why It Matters:", "Tests how routing handles energy that cannot be predicted with a smooth sine wave.")
    ]),
    ("4. Real Weather Trace Replays", C_NAVY_MED, [
        ("The Mechanism:", "Replays verified 24-hour meteorological solar datasets."),
        ("The Math:", "Evaluates across Clear Sky (smooth solar curve), Intermittent Clouds (sharp random drops), and Overcast (heavily damped solar intake)."),
        ("Why It Matters:", "Guarantees our simulator reflects real-world cloud cover rather than toy equations.")
    ])
]

for i, (title, color, bullets) in enumerate(regimes):
    row = i // 2
    col = i % 2
    cx = Inches(0.8) + col * Inches(6.0)
    cy = Inches(1.6) + row * Inches(2.55)
    
    add_card(s6, cx, cy, Inches(5.7), Inches(2.4))
    
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
    
    tb = s6.shapes.add_textbox(cx + Inches(0.15), cy + Inches(0.42), Inches(5.4), Inches(1.9))
    tf = tb.text_frame
    tf.word_wrap = True
    for pfx, txt in bullets:
        add_bullet(tf, pfx, txt, 9.5, space_after=3)

add_speaker_notes(s6, """
Slide 6 shows how we simulate the real physical environment in src/harvesting_model.py.
We didn't just assume constant battery power. We implemented four realistic environmental scenarios:
First, a 24-hour diurnal solar cycle where power peaks at noon and drops to zero at night.
Second, tree canopy shadowing: in an agricultural field or forest, nodes under trees receive only 10% of the sunlight.
Third, a Poisson arrival process modeling sporadic energy bursts like indoor lighting or vibration.
And fourth, real meteorological trace replays using recorded 24-hour solar datasets under clear, cloudy, and overcast conditions.
This tests our algorithms under genuine weather variance.
""")

# ==============================================================================
# SLIDE 7: ALGORITHM 1  -  TEACHING DYNAMIC PROGRAMMING TO LOOK AHEAD
# ==============================================================================
s7 = prs.slides.add_slide(blank_layout)
add_header(s7, "Algorithm 1: Teaching Dynamic Programming to Look Ahead", "Algorithm 1: Time-DP", 7)

# Left Card: The Intuition & The Recurrence
add_card(s7, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1))
tb = s7.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(5.3), Inches(4.8))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "The Core Intuition & 3D Recurrence"
p.font.name = FONT_HEADING
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY_DARK
p.space_after = Pt(6)

add_bullet(tf, "The Big Shift:", "Instead of asking 'Does node B have battery right now?', we ask: 'Will node B have battery when our packet actually reaches it 2 hops from now?'", 10.5)
add_bullet(tf, "The 3D State dp[v][h][t]:", "Maximum bottleneck residual energy along any candidate h-hop path reaching node v at arrival time offset t.", 10.5)

# Embed Equation 3 image if available
eq3_path = os.path.join(EQ_DIR, "eq_3.png")
if os.path.exists(eq3_path):
    s7.shapes.add_picture(eq3_path, Inches(1.0), Inches(2.95), width=Inches(5.3))

tb_sub = s7.shapes.add_textbox(Inches(1.0), Inches(3.6), Inches(5.3), Inches(3.0))
tf_sub = tb_sub.text_frame
tf_sub.word_wrap = True
add_bullet(tf_sub, "Lookahead Recharge Projection E_proj:", "E_proj(v, t) adds the solar recharge expected during transit minus battery leakage. It anticipates refill before packets arrive!", 10)
add_bullet(tf_sub, "Physical Feasibility Gate:", "A hop from u to v is only explored if u has enough battery to pay the radio transmission cost E_tx. Infeasible paths are pruned immediately.", 10)

# Right Card: Complexity & Embedded Budget
add_card(s7, Inches(6.833), Inches(1.6), Inches(5.7), Inches(5.1))
tb = s7.shapes.add_textbox(Inches(7.033), Inches(1.75), Inches(5.3), Inches(4.8))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "Why It Runs in Milliseconds (<48 KB RAM)"
p.font.name = FONT_HEADING
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY_DARK
p.space_after = Pt(6)

add_bullet(tf, "Polynomial Time O(|E| * H * T):", "Because time strictly advances with each hop, the state space is a Directed Acyclic Graph (DAG). There are zero cycles to recompute!", 10.5)
add_bullet(tf, "Compact Memory Footprint:", "Consumes < 48 KB RAM for a 50-node network. It easily fits on modern 32-bit ARM Cortex-M4 or ESP32 microcontrollers.", 10.5)
add_bullet(tf, "Real Benchmark Latency:", "Table fills in under 5.2 milliseconds per call on standard sensor hardware.", 10.5)

# Route Selection Eq
eq2_path = os.path.join(EQ_DIR, "eq_2.png")
if os.path.exists(eq2_path):
    s7.shapes.add_picture(eq2_path, Inches(7.033), Inches(4.5), width=Inches(5.3))

tb_rec = s7.shapes.add_textbox(Inches(7.033), Inches(5.15), Inches(5.3), Inches(1.5))
tf_rec = tb_rec.text_frame
tf_rec.word_wrap = True
add_bullet(tf_rec, "Optimal Backtracking:", "Backpointers parent[(v, h, t)] trace backwards from the Base Station to extract the optimal bottleneck-maximizing route P*.", 10)

add_speaker_notes(s7, """
Slide 7 explains our core algorithm: 3D Time-Augmented Dynamic Programming in src/dp_lifetime.py.
Here is the intuition: instead of checking whether a node has energy right now at round start, we project its energy forward in time to the exact moment the packet arrives.
Our state space is 3-dimensional: node v, hop count h, and arrival time t.
Look at the formula: dp[v][h][t] evaluates candidate predecessor u, but evaluates node v's energy using E_proj, which adds the solar recharge expected during transit minus the receiver tax Erx.
Because time moves forward, the state graph is a DAG with no loops. It runs in strictly polynomial time O(|E|HT), taking only 5.2 milliseconds and under 48 kilobytes of RAM.
""")

prs.save("Final_Review_Presentation_WSN_Adaptive_Routing.pptx")
print("Saved Slide 1 to 7 checkpoint.")
# ==============================================================================
# SLIDE 8: ALGORITHM 2  -  FIXING BROKEN ROUTES ON THE FLY IN 0.85 MS
# ==============================================================================
s8 = prs.slides.add_slide(blank_layout)
add_header(s8, "Algorithm 2: Fixing Broken Routes on the Fly in 0.85 ms", "Algorithm 2: DSU Detours", 8)

c_w = Inches(3.7)
c_h = Inches(5.1)

# Card 1: The In-Flight Breakdown
c1 = add_card(s8, Inches(0.8), Inches(1.6), c_w, c_h)
tb1 = s8.shapes.add_textbox(Inches(0.95), Inches(1.75), c_w - Inches(0.3), c_h - Inches(0.3))
tf1 = tb1.text_frame
tf1.word_wrap = True
p = tf1.paragraphs[0]
p.text = "The In-Flight Breakdown"
p.font.name = FONT_HEADING
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = C_RED
p.space_after = Pt(6)

add_bullet(tf1, "The Unexpected Crash:", "Sensors don't politely wait for round boundaries to die. A relay can brown out mid-transmission due to sudden cloud cover or unexpected data load.", 10)
add_bullet(tf1, "The Wasted Energy:", "If we drop the packet, all transmission energy spent across prior hops is permanently lost.", 10)
add_bullet(tf1, "Why Full Recompute Fails:", "Rerunning full Time-DP takes over 5.12 milliseconds and floods the entire field with route recalculation broadcasts.", 10)

# Card 2: The Union-Find Shortcut
c2 = add_card(s8, Inches(4.8), Inches(1.6), c_w, c_h)
tb2 = s8.shapes.add_textbox(Inches(4.95), Inches(1.75), c_w - Inches(0.3), c_h - Inches(0.3))
tf2 = tb2.text_frame
tf2.word_wrap = True
p = tf2.paragraphs[0]
p.text = "The Union-Find Shortcut"
p.font.name = FONT_HEADING
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = C_BLUE
p.space_after = Pt(6)

add_bullet(tf2, "Two Classic Optimizations:", "1. Path Compression flattens the tree during find(x).\n2. Union by Rank attaches the smaller tree under the root of the larger tree.", 10)
add_bullet(tf2, "The Invariant We Maintain:", "We maintain the connected component of the Base Station. Any node b can reach the sink iff find(b) == bs_root.", 10)
add_bullet(tf2, "Near O(1) Speed:", "Amortized complexity is O(alpha(V)) where alpha is the inverse Ackermann function (<= 4). Near-instant lookup!", 10)

# Card 3: The Local Bridge Splice
c3 = add_card(s8, Inches(8.8), Inches(1.6), c_w, c_h)
tb3 = s8.shapes.add_textbox(Inches(8.95), Inches(1.75), c_w - Inches(0.3), c_h - Inches(0.3))
tf3 = tb3.text_frame
tf3.word_wrap = True
p = tf3.paragraphs[0]
p.text = "The Local Bridge Splice"
p.font.name = FONT_HEADING
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = C_TEAL
p.space_after = Pt(6)

add_bullet(tf3, "Asking Immediate Neighbors:", "When the relay at hop i dies, predecessor u asks only its immediate neighbors: 'Who among you is already in the Base Station's component?'", 10)
add_bullet(tf3, "Lowest Radio Cost Wins:", "Among connected neighbors, u picks the one requiring the lowest transmission power and immediately splices it into the route.", 10)
add_bullet(tf3, "The Result:", "Executed in 0.85 ms vs 5.12 ms (6.02x faster) with a 100% Packet Delivery Ratio across 500 failure injection trials!", 10)

add_speaker_notes(s8, """
Slide 8 presents Algorithm 2 in src/routing.py: DSU Live Detour Recovery.
In real life, a sensor node can brown out while a packet is mid-air. 
If we drop the packet, all the battery spent moving it across the first three hops is wasted. But if we rerun global Dynamic Programming, it takes over 5 milliseconds and causes a huge lag spike.
Think of our solution like a GPS that finds a local detour when a bridge is closed. Predecessor node u simply queries its immediate neighbors to check who is already connected to the Base Station component using Union-Find.
This local check runs in 0.85 milliseconds - 6.02 times faster - achieving 100% packet delivery with zero global recalculation overhead.
""")

# ==============================================================================
# SLIDE 9: ALGORITHM 3  -  PICKING CLUSTER HEADS THAT ACTUALLY HAVE SUNLIGHT
# ==============================================================================
s9 = prs.slides.add_slide(blank_layout)
add_header(s9, "Algorithm 3: Picking Cluster Heads That Actually Have Sunlight", "Algorithm 3: EH-LEACH", 9)

# Left Card: The Problem with Random Heads
add_card(s9, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1))
tb = s9.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(5.3), Inches(4.8))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "The Flaw with Standard LEACH Clustering"
p.font.name = FONT_HEADING
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY_DARK
p.space_after = Pt(6)

add_bullet(tf, "The Random Coin Flip:", "Classical LEACH elects Cluster Heads (CHs) based purely on random chance (probability p = 0.10). Every alive node has the exact same probability of being picked.", 10.5)
add_bullet(tf, "The Heavy Burden of a Cluster Head:", "Cluster Heads must stay awake, collect data from 10+ member nodes, aggregate the packets, and transmit high-power uplinks to the Base Station.", 10.5)
add_bullet(tf, "The Shaded Disaster:", "When a shaded sensor under a tree gets randomly elected as Cluster Head, its battery completely drains within 1-2 rounds!", 10.5)
add_bullet(tf, "Our Fix in src/clustering.py:", "Weight the election threshold dynamically based on the incoming solar recharge rate.", 10.5)

# Right Card: Our Solar-Weighted Formula
add_card(s9, Inches(6.833), Inches(1.6), Inches(5.7), Inches(5.1))
tb = s9.shapes.add_textbox(Inches(7.033), Inches(1.75), Inches(5.3), Inches(4.8))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "Our Solar-Weighted Threshold Formula T(n)"
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
add_bullet(tf_sub, "E_n, H_n:", "Residual battery and expected solar harvest intake of candidate node n in the upcoming round.", 10)
add_bullet(tf_sub, "E_avg, H_avg:", "Average residual energy and solar harvest rate across all currently operational sensors.", 10)
add_bullet(tf_sub, "beta = 0.5:", "Harvest weighting coefficient balancing stored battery vs incoming solar rate.", 10)
add_bullet(tf_sub, "2.4x Election Boost:", "Sensors basking in bright sunlight are elected 2.4x more frequently, handling the heavy aggregation lifting and shielding shaded sensors from early burnout.", 10)

add_speaker_notes(s9, """
Slide 9 covers Algorithm 3: Solar-Weighted Dynamic Clustering (EH-LEACH) in src/clustering.py.
Standard LEACH picks cluster heads by flipping a random coin. But being a cluster head requires heavy work: collecting readings from 10 nodes, fusing the data, and transmitting long-range uplinks to the base station.
If a sensor under a tree gets picked, it collapses in one round.
Our formula weights the election probability by the node's solar and battery ratio: (E_n + beta * H_n) / (E_avg + beta * H_avg).
Nodes in open sunlight get picked 2.4 times more frequently, taking on the heavy work, while shaded sensors rest as low-power leaf nodes.
""")

# ==============================================================================
# SLIDE 10: ALGORITHM 4  -  ROUTING WHEN BATTERY REPORTS ARE STALE
# ==============================================================================
s10 = prs.slides.add_slide(blank_layout)
add_header(s10, "Algorithm 4: Routing When Battery Reports Are Stale", "Algorithm 4: Belief Filter", 10)

# Left Card: The Partial Observability Dilemma
add_card(s10, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1))
tb = s10.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(5.3), Inches(4.8))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "The Partial Observability Dilemma"
p.font.name = FONT_HEADING
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY_DARK
p.space_after = Pt(6)

add_bullet(tf, "The Telemetry Dilemma:", "Sensors cannot broadcast battery telemetry every round. Transmitting the status update itself burns precious battery! The router must make decisions under uncertainty.", 10)
add_bullet(tf, "5 Belief Views Evaluated (src/energy_view.py):", "", 10)
add_bullet(tf, "- Oracle:", "Omniscient exact battery reading. (Cheating upper baseline).", 9.5)
add_bullet(tf, "- Blind:", "Zero updates after Round 0. Completely blind to solar refill.", 9.5)
add_bullet(tf, "- Stale:", "Periodic 8-bit report every R rounds. Lags behind true state.", 9.5)
add_bullet(tf, "- Gaussian:", "Kalman filter. Suffers severe errors at battery boundaries.", 9.5)
add_bullet(tf, "- Histogram (Ours):", "24-bin discrete probability distribution p in [0, 1]^24.", 9.5)

# Right Card: Why Discrete Histogram & Max-Product DP
add_card(s10, Inches(6.833), Inches(1.6), Inches(5.7), Inches(5.1))
tb = s10.shapes.add_textbox(Inches(7.033), Inches(1.75), Inches(5.3), Inches(4.8))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "Why 24-Bin Histograms Win at the Limits"
p.font.name = FONT_HEADING
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY_DARK
p.space_after = Pt(6)

add_bullet(tf, "The Gaussian Boundary Trap:", "Gaussian bell curves stretch to infinity. In a battery, energy cannot physically drop below 0 Joules or exceed E_max = 0.5 Joules! Gaussian math creates false probabilities.", 10)
add_bullet(tf, "Exact Boundary Mass Clipping:", "Our 24-bin histogram explicitly clips probability mass: negative energy shifts into Bin 0 (brownout probability); excess solar shifts into Bin 23 (saturation).", 10)
add_bullet(tf, "Log-Domain Max-Product Confidence Routing:", "Maximizes the mathematical probability that all hops survive:", 10)

# Embed Equation 6 image if available
eq6_path = os.path.join(EQ_DIR, "eq_6.png")
if os.path.exists(eq6_path):
    s10.shapes.add_picture(eq6_path, Inches(7.033), Inches(4.2), width=Inches(5.3))

tb_cens = s10.shapes.add_textbox(Inches(7.033), Inches(4.85), Inches(5.3), Inches(1.8))
tf_cens = tb_cens.text_frame
tf_cens.word_wrap = True
add_bullet(tf_cens, "Censored Evidence Updates:", "When a packet drops, the router updates its belief: P(E < E_tx) = 1.0, instantly zeroing out higher probability bins without waiting for telemetry.", 9.5)

add_speaker_notes(s10, """
Slide 10 addresses real-world partial observability in src/energy_view.py.
Sensors cannot transmit telemetry reports every minute; transmitting the report itself drains battery. So the router must maintain a belief state.
Most papers use Kalman filters with Gaussian noise. But batteries have hard physical boundaries: they cannot drop below 0 Joules or exceed 0.5 Joules. Gaussian tails create severe errors at these boundaries.
We implement a 24-bin discrete histogram filter with exact boundary mass clipping: mass below zero goes into bin 0 (brownout probability), and mass above E_max clips into bin 23 (saturation).
Our Max-Product DP maximizes the sum of log-probabilities across the route, choosing paths with the highest mathematical confidence of end-to-end survival.
""")

# ==============================================================================
# SLIDE 11: UNDER THE HOOD: HOW WE STRUCTURED THE 4,000+ LINES OF CODE
# ==============================================================================
s11 = prs.slides.add_slide(blank_layout)
add_header(s11, "Under the Hood: How We Structured the 4,000+ Lines of Code", "Codebase Architecture", 11)

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

headers = ["Directory", "Key Module", "Plain English Responsibility", "Lines of Code"]
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
    ("src/", "dp_lifetime.py, routing.py", "3D Lookahead DP (dp[v][h][t]), DSU live detour recovery, Dijkstra", "535 LOC"),
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

add_card(s11, Inches(0.8), Inches(5.7), Inches(11.733), Inches(1.1), bg_color=C_TEAL_LIGHT, border_color=C_TEAL)
tb = s11.shapes.add_textbox(Inches(1.0), Inches(5.75), Inches(11.333), Inches(1.0))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "THREE DECOUPLED TIERS: BUILT FOR RESEARCH & REAL HARDWARE:"
p.font.name = FONT_HEADING
p.font.size = Pt(10)
p.font.bold = True
p.font.color.rgb = C_TEAL

p2 = tf.add_paragraph()
p2.text = "- Tier 1 (Headless Simulation Core): Pure Python 3.12 without GUI dependencies. Can run batch sweeps in parallel or be ported to embedded C.\n- Tier 2 (Asynchronous Backend): FastAPI REST service with SQLite persistence, offloading heavy simulation sweeps to worker threads.\n- Tier 3 (Client-Side Dashboard): React 19 single-page application with SVG animations, timeline playback, and Recharts analytics."
p2.font.name = FONT_BODY
p2.font.size = Pt(9.5)
p2.font.color.rgb = C_NAVY_DARK

add_speaker_notes(s11, """
Slide 11 reviews our software architecture.
We followed strict software engineering standards to ensure modularity.
The project is divided into three completely decoupled tiers:
Tier 1 in src/ is the pure algorithmic engine. It has zero GUI dependencies and can run headlessly in batch sweeps or be compiled to C for embedded deployment.
Tier 2 in backend/ is a FastAPI REST API that persists simulation histories to an embedded SQLite database.
Tier 3 in frontend/ is a React 19 research dashboard providing interactive visualization.
Total verified code volume exceeds 4,000 lines, anchored by 15 pytest test suites.
""")

# ==============================================================================
# SLIDE 12: CODE WALKTHROUGH: SEEING THE REAL LOGIC
# ==============================================================================
s12 = prs.slides.add_slide(blank_layout)
add_header(s12, "A Look at the Code: Real Python Logic Running the System", "Code Walkthrough", 12)

# Left Column: 3D Time-DP Code Excerpt
add_card(s12, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1), bg_color=C_CODE_BG)
tb = s12.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.3), Inches(0.4))
tf = tb.text_frame
p = tf.paragraphs[0]
p.text = "3D Lookahead DP (src/dp_lifetime.py)"
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
                    continue  # Prune infeasible hop
                
                # Project recharge at arrival time t!
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
p2.text = "DSU Live Detour Repair (src/routing.py)"
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
# SLIDE 13: THE WEB DASHBOARD: WATCHING SENSOR ROUTES ADAPT LIVE
# ==============================================================================
s13 = prs.slides.add_slide(blank_layout)
add_header(s13, "The Web Dashboard: Watching Sensor Routes Adapt Live", "User Interface", 13)

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
# SLIDE 14: HEATMAPS & ANALYTICS: SPOTTING DYING RELAYS BEFORE THEY FAIL
# ==============================================================================
s14 = prs.slides.add_slide(blank_layout)
add_header(s14, "Heatmaps & Analytics: Seeing Trouble Before It Happens", "Heatmaps & Analytics", 14)

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

prs.save("Final_Review_Presentation_WSN_Adaptive_Routing.pptx")
print("Saved Slide 8 to 14 checkpoint.")
# ==============================================================================
# SLIDE 15: PUTTING IT TO THE TEST: 68 AUTOMATED TESTS, 100% PASS RATE
# ==============================================================================
s15 = prs.slides.add_slide(blank_layout)
add_header(s15, "Putting It to the Test: 68 Automated Tests, 100% Pass Rate", "Testing & Reliability", 15)

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

# Right Column: What the Tests Actually Prove
add_card(s15, Inches(6.833), Inches(1.6), Inches(5.7), Inches(5.1))
tb2 = s15.shapes.add_textbox(Inches(7.033), Inches(1.75), Inches(5.3), Inches(4.8))
tf2 = tb2.text_frame
tf2.word_wrap = True
p2_h = tf2.paragraphs[0]
p2_h.text = "What Our Automated Testbench Guarantees"
p2_h.font.name = FONT_HEADING
p2_h.font.size = Pt(14)
p2_h.font.bold = True
p2_h.font.color.rgb = C_NAVY_DARK
p2_h.space_after = Pt(6)

add_bullet(tf2, "Mathematical Correctness:", "test_adversarial_counterexample mathematically confirms Time-DP picks recharging relay B (0.040J) over Dijkstra relay A (0.030J).", 10)
add_bullet(tf2, "Radio Physics Compliance:", "test_energy_model verifies the d^2 / d^4 crossover at d0 = 87.7m and receiver electronic dissipation Erx = 50 nJ/bit.", 10)
add_bullet(tf2, "Live Fault Tolerance:", "test_brownout_and_failure confirms 100% PDR under 10% to 30% injected node deaths via DSU bridge repairs.", 10)
add_bullet(tf2, "Speedup Verification:", "test_dsu_speedup confirms 3.8x to 6.1x execution speedup over full DP recomputation.", 10)
add_bullet(tf2, "Probability Conservation:", "test_energy_view confirms 24-bin histogram probability mass always sums to exactly 1.0 with zero leak.", 10)
add_bullet(tf2, "API Reliability:", "test_backend_api validates FastAPI simulation runs, benchmark sweeps, and SQLite persistence.", 10)

add_speaker_notes(s15, """
Slide 15 shows our automated testing suite.
We didn't just write code and hope it works. We built a 15-file test suite with 68 automated unit tests.
As shown on the left terminal capture, all 68 tests pass in 4.72 seconds.
These tests verify that our radio formulas match real physics, that our 5-node proof behaves as predicted, that DSU sustains a 100% packet delivery ratio during failures, and that our histogram probability mass never leaks.
This gives us total confidence in the software's reliability.
""")

# ==============================================================================
# SLIDE 16: THE 5-NODE EXPERIMENT: PROVING OUR POINT WITHOUT ANY FLUFF
# ==============================================================================
s16 = prs.slides.add_slide(blank_layout)
add_header(s16, "The 5-Node Experiment: Proving Our Point Without Any Fluff", "Empirical Proof", 16)

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
add_bullet(tf_cd, "The Setup:", "Source S must reach BS through Relay A (starts at 30 mJ, zero harvest) or Relay B (starts at 5 mJ, harvests +35 mJ during transit).", 9.5)

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
add_bullet(tf_con, "The Plain Truth:", "Time-DP calculates that Relay B will reach 0.040 J (+33.3% higher capacity) at arrival time t=1. It picks Relay B, achieving infinite route survival.", 9.5)
add_bullet(tf_con, "Why Dijkstra Dies:", "Dijkstra only sees 0.005 J at t=0. It falsely rejects B and funnels traffic through dying Relay A until the network collapses.", 9.5)

add_speaker_notes(s16, """
Slide 16 details our deterministic 5-node proof from run_counterexample.py.
To prove our algorithmic advantage without statistical noise, we constructed a minimal 5-node topology: Source S must choose between Relay A and Relay B to reach the Base Station.
Relay A has 0.030 J but zero harvest. Relay B has only 0.005 J, but harvests +0.035 J per step.
Look at the table: Dijkstra, Energy-Aware Dijkstra, and Classical Maximin DP all choose Relay A because they only look at the t=0 snapshot. After 15 rounds, Relay A runs out of energy and the network dies.
Our Time-Augmented DP looks ahead to arrival time t=1, correctly computes that Relay B will reach 0.040 Joules, and routes through Relay B. The network survives indefinitely. This proves our claim beyond doubt.
""")

# ==============================================================================
# SLIDE 17: LIVE DETOUR BENCHMARK: 6x FASTER THAN REBUILDING FROM SCRATCH
# ==============================================================================
s17 = prs.slides.add_slide(blank_layout)
add_header(s17, "Live Detour Benchmark: 6x Faster Than Rebuilding From Scratch", "Benchmark Results", 17)

# Left Column: Embedded DSU Benchmark Chart
add_card(s17, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1))
tb = s17.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.3), Inches(0.4))
tf = tb.text_frame
p = tf.paragraphs[0]
p.text = "Injected Failure Rate vs Route Repair Latency"
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
add_bullet(tf_dd, "Stress Testing Setup:", "Evaluated across 500 failure injection trials under 10% to 30% randomly induced relay deaths while packets are actively in flight.", 9.5)

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
# SLIDE 18: THE BIG SURPRISE: WHY MULTI-HOP RELAYING USES 2x MORE ENERGY!
# ==============================================================================
s18 = prs.slides.add_slide(blank_layout)
add_header(s18, "The Big Surprise: Multi-Hop Relaying Uses 2x MORE Energy!", "Surprise Discovery", 18)

# Left Card: Direct Link vs Two-Hop Link Calculations
add_card(s18, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1))
tb = s18.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(5.3), Inches(4.8))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "The Radio Energy Balance for a 4000-Bit Packet"
p.font.name = FONT_HEADING
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY_DARK
p.space_after = Pt(6)

add_bullet(tf, "The Multi-Hop Myth:", "Almost every textbook claims multi-hop routing is universally greener because transmission energy scales with distance squared (d^2).", 10.5)
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
cp.text = "THE EYE-OPENING DISCOVERY:"
cp.font.name = FONT_HEADING
cp.font.size = Pt(10)
cp.font.bold = True
cp.font.color.rgb = C_RED

cp2 = ctf.add_paragraph()
cp2.text = "Relaying costs 0.672 mJ vs 0.344 mJ for direct transmission -- nearly TWICE as much energy! Relaying is only economical if distance spans beyond 87.7m (d^4 zone) or if the relay is actively absorbing free solar recharge."
cp2.font.name = FONT_BODY
cp2.font.size = Pt(9.5)
cp2.font.color.rgb = C_NAVY_DARK

# Right Card: The Macroscopic Network Dilemma
add_card(s18, Inches(6.833), Inches(1.6), Inches(5.7), Inches(5.1))
tb2 = s18.shapes.add_textbox(Inches(7.033), Inches(1.75), Inches(5.3), Inches(4.8))
tf2 = tb2.text_frame
tf2.word_wrap = True
p2 = tf2.paragraphs[0]
p2.text = "The Macroscopic Lesson: Traffic Funneling"
p2.font.name = FONT_HEADING
p2.font.size = Pt(14)
p2.font.bold = True
p2.font.color.rgb = C_NAVY_DARK
p2.space_after = Pt(6)

add_bullet(tf2, "Single-Path Maximin vs Global Energy:", "Our Time-DP algorithm provably maximizes the bottleneck residual energy along an isolated route. But at the network level, more hops burn more aggregate battery.", 10.5)
add_bullet(tf2, "Uncoordinated Traffic Funneling:", "When multiple cluster heads all see the same sunny relay as attractive, they simultaneously dump packets onto it, burning its battery faster than the sun can recharge it!", 10.5)
add_bullet(tf2, "Multi-Seed Evaluation (30 Seeds):", "Evaluated across 30 random topologies in run_multiseed.py. In dense networks, direct transmission preserves more aggregate energy.", 10.5)
add_bullet(tf2, "Our Realistic Routing Rule:", "Our Time-DP explicitly subtracts E_rx in its recurrence, so it only chooses relaying when the relay is genuinely flooded with surplus solar energy.", 10.5)

add_speaker_notes(s18, """
Slide 18 presents our most interesting scientific discovery: the Electronic Reception Penalty trade-off.
Most students and textbooks assume that multi-hop is always better. But look at the math on the left:
Transmitting directly over 60 meters costs 0.344 millijoules.
Splitting that into two 30-meter hops requires 0.472 millijoules of transmission plus 0.200 millijoules of receiver dissipation Erx. That totals 0.672 millijoules - nearly double the direct cost!
This reveals that multi-hop routing actually wastes network energy unless the link spans into the d^4 multipath fading regime beyond 87.7 meters, or unless the relay is receiving surplus solar energy.
Our Time-DP router is one of the few algorithms that explicitly incorporates Erx into its recurrence, preventing wasteful relay detours.
""")

# ==============================================================================
# SLIDE 19: THE MATH BEHIND IT: PROVABLE GUARANTEES & OPTIMALITY
# ==============================================================================
s19 = prs.slides.add_slide(blank_layout)
add_header(s19, "The Math Behind It: Provable Guarantees & Optimality", "Mathematical Rigor", 19)

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
p2.text = "Theorem 2: The 2-Epsilon Guarantee"
p2.font.name = FONT_HEADING
p2.font.size = Pt(13)
p2.font.bold = True
p2.font.color.rgb = C_NAVY_DARK
p2.space_after = Pt(6)

add_bullet(tf2, "Real-World Weather Uncertainty:", "What if our solar forecast is slightly off? Let estimation error be bounded: |xi_v(t)| <= epsilon.", 10)
add_bullet(tf2, "Theoretical Guarantee Statement:", "Under bounded forecast error epsilon, the path P_DP selected by Time-DP achieves a realized bottleneck within 2-epsilon of an omniscient offline oracle P*:", 10)

# Embed Equation 7 image if available
eq7_path = os.path.join(EQ_DIR, "eq_7.png")
if os.path.exists(eq7_path):
    s19.shapes.add_picture(eq7_path, Inches(7.033), Inches(3.6), width=Inches(5.3))

tb_pf = s19.shapes.add_textbox(Inches(7.033), Inches(4.3), Inches(5.3), Inches(2.2))
tf_pf = tb_pf.text_frame
tf_pf.word_wrap = True
add_bullet(tf_pf, "Why This Gives Peace of Mind:", "Even if a cloud causes weather forecasts to drift by epsilon, our algorithm never degrades by more than 2-epsilon compared to an imaginary oracle that has a crystal ball seeing the future!", 10)

add_speaker_notes(s19, """
Slide 19 establishes our mathematical foundations through two formal theorems.
Theorem 1 proves Bellman Optimality. Because every hop in our time-expanded state space increments time by at least one slot, the state graph is a Directed Acyclic Graph (DAG) with no cycles. The min-operator preserves optimal substructure, guaranteeing global maximin optimality.
Theorem 2 establishes a 2-epsilon approximation bound under bounded harvest forecasting errors. Even if actual solar intake varies by +/- epsilon, our polynomial DP guarantees a realized bottleneck within 2-epsilon of an omniscient offline oracle with perfect foresight.
""")

# ==============================================================================
# SLIDE 20: PROJECT WRAP-UP: WHAT WE BUILT & WHERE WE'RE HEADING
# ==============================================================================
s20 = prs.slides.add_slide(blank_layout)
add_header(s20, "Project Wrap-Up: What We Built & Where We're Heading", "Status & Roadmap", 20)

rows = 6
cols = 4
tbl_d = s20.shapes.add_table(rows, cols, Inches(0.8), Inches(1.6), Inches(11.733), Inches(3.4)).table
tbl_d.columns[0].width = Inches(2.2)
tbl_d.columns[1].width = Inches(3.8)
tbl_d.columns[2].width = Inches(1.8)
tbl_d.columns[3].width = Inches(3.933)

d_headers = ["Milestone", "Technical Deliverable", "Status", "Verification Evidence"]
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

add_card(s20, Inches(0.8), Inches(5.2), Inches(11.733), Inches(1.5), bg_color=C_BLUE_LIGHT, border_color=C_BLUE)
tb = s20.shapes.add_textbox(Inches(1.0), Inches(5.25), Inches(11.333), Inches(1.4))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "NEXT STEPS & PUBLICATION BLUEPRINT (2026-2027):"
p.font.name = FONT_HEADING
p.font.size = Pt(10.5)
p.font.bold = True
p.font.color.rgb = C_BLUE

p2 = tf.add_paragraph()
p2.text = "- Journal Target: IEEE Sensors Journal (SCI Q1, IF: 4.3) or Elsevier Ad Hoc Networks (SCI Q1, IF: 4.8).\n- Manuscript Focus: 'Adaptive Lookahead Routing, First-Order Radio Dissipation Trade-Offs, and DSU-Based Live Detour Recovery in Energy-Harvesting Wireless Sensor Networks'.\n- Embedded Hardware Roadmap: Compiling algorithmic core into C/C++ firmware for hardware evaluation on physical ESP32 and MicaZ sensor motes."
p2.font.name = FONT_BODY
p2.font.size = Pt(9.5)
p2.font.color.rgb = C_NAVY_DARK

add_speaker_notes(s20, """
Slide 20 summarizes our completed deliverables and future roadmap.
All five major project milestones are 100% complete and fully verified.
Looking forward, our publication blueprint targets IEEE Sensors Journal or Elsevier Ad Hoc Networks. The paper will present our 3D Time-Augmented DP, our 6.02x DSU detour speedup, and our empirical findings regarding receiver dissipation Erx.
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

t_pill = s21.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(0.8), Inches(3.6), Inches(0.35))
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

tb = s21.shapes.add_textbox(Inches(1.0), Inches(1.3), Inches(11.333), Inches(1.5))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "Thank You! We're Ready for Your Questions"
p.font.name = FONT_HEADING
p.font.size = Pt(34)
p.font.bold = True
p.font.color.rgb = C_WHITE

p2 = tf.add_paragraph()
p2.text = "Adaptive Routing in Energy-Harvesting Wireless Sensor Networks"
p2.font.name = FONT_BODY
p2.font.size = Pt(14)
p2.font.color.rgb = RGBColor(148, 163, 184)

summary_points = [
    ("Lookahead 3D DP", "Stops the False Alarm of skipping recharging sensors, running in O(|E|HT) polynomial time under 48 KB RAM.", C_TEAL),
    ("6.02x Faster DSU Repairs", "Saves packets in 0.85 ms using Union-Find when relays die mid-flight, sustaining 100% delivery.", C_BLUE),
    ("Caught the Receiver Tax", "Proved multi-hop relaying burns ~2x more energy under 87.7m unless sustained by solar recharge.", C_AMBER),
    ("Full-Stack Tested Platform", "React 19 interactive SVG canvas, FastAPI service, and 68/68 passing tests ready for real motes.", C_WHITE)
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

b_tb = s21.shapes.add_textbox(Inches(1.0), Inches(6.6), Inches(11.333), Inches(0.5))
b_tf = b_tb.text_frame
b_p = b_tf.paragraphs[0]
b_p.text = "Presenters: Santhosh G (25BEL0016), Thilang T V (25BEL0036), Ananthakrishnan R (25BEL0005)  |  VIT Vellore  |  GitHub: WSN_proj"
b_p.font.name = FONT_BODY
b_p.font.size = Pt(10)
b_p.font.color.rgb = RGBColor(148, 163, 184)

add_speaker_notes(s21, """
Thank you, respected professors and members of the panel, for your time and guidance throughout this project.
To conclude, our work bridges theoretical computer science with the practical reality of solar-powered wireless networks:
1. 3D Time-Augmented Dynamic Programming eliminates the False Alarm flaw of rejecting recharging nodes.
2. Disjoint-Set Union local detours deliver a 6.02x latency speedup during in-flight failures with zero dropped packets.
3. Our first-order radio modeling discovered the critical role of electronic reception dissipation Erx.
4. And our full-stack React 19 and FastAPI platform makes the entire framework interactive, verifiable, and reproducible.
We are now ready to take your questions.
""")

# ==============================================================================
# FINAL SAVE & EXPORT
# ==============================================================================
output_pptx_path = os.path.join(BASE_DIR, "Final_Review_Presentation_WSN_Adaptive_Routing.pptx")
prs.save(output_pptx_path)
print(f"Presentation successfully compiled to: {output_pptx_path}")

downloads_path = r"C:\Users\Santhosh\Downloads\Final_Review_Presentation_WSN_Adaptive_Routing.pptx"
try:
    shutil.copyfile(output_pptx_path, downloads_path)
    print(f"Copied presentation to Downloads: {downloads_path}")
except Exception as e:
    print(f"Warning: Could not copy to Downloads: {e}")
