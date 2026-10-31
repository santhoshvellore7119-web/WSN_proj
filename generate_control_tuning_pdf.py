import os
import sys
import shutil
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PDF = os.path.join(BASE_DIR, "report", "Control_Tuning_Guide_LQR_STSMC_Adaptive.pdf")
DOWNLOADS_PDF = r"C:\Users\Santhosh\Downloads\Control_Tuning_Guide_LQR_STSMC_Adaptive.pdf"

class ControlGuideNumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(ControlGuideNumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super(ControlGuideNumberedCanvas, self).showPage()
        super(ControlGuideNumberedCanvas, self).save()

    def draw_decorations(self, page_count):
        self.saveState()
        self.setFont('Helvetica-Bold', 7)
        self.setFillColor(colors.HexColor('#1E3A8A')) # Dark Blue
        
        # Running Header on page 2+
        if self._pageNumber > 1:
            self.drawString(36, 760, "CONTROL SYSTEMS TUNING MANUAL: LQR, FIXED STSMC & ADAPTIVE STSMC")
            self.drawRightString(576, 760, "SELECT, VIT VELLORE")
            self.setStrokeColor(colors.HexColor('#CBD5E1'))
            self.setLineWidth(0.5)
            self.line(36, 753, 576, 753)
        
        # Running Footer on all pages
        self.setFont('Helvetica', 7.5)
        self.setFillColor(colors.HexColor('#475569'))
        self.drawString(36, 20, "Practical Simulink Implementation Guide  |  Santhosh G, Thilang T V, Ananthakrishnan R")
        self.drawRightString(576, 20, f"Page {self._pageNumber} of {page_count}")
        self.setStrokeColor(colors.HexColor('#CBD5E1'))
        self.setLineWidth(0.5)
        self.line(36, 28, 576, 28)
        self.restoreState()


def generate_pdf():
    os.makedirs(os.path.join(BASE_DIR, "report"), exist_ok=True)
    
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13.5,
        leading=16.5,
        textColor=colors.HexColor('#0F172A'),
        alignment=1,
        spaceAfter=3
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#334155'),
        alignment=1,
        spaceAfter=6
    )
    
    h1 = ParagraphStyle(
        'SecH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11.5,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=5,
        spaceAfter=2,
        keepWithNext=True
    )
    
    body = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=7.6,
        leading=9.8,
        textColor=colors.HexColor('#1E293B'),
        alignment=4,
        spaceAfter=3
    )
    
    code_text = ParagraphStyle(
        'CodeText',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=6.2,
        leading=7.8,
        textColor=colors.HexColor('#0F172A')
    )
    
    tbl_hdr = ParagraphStyle(
        'TblHdr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=6.8,
        leading=8.5,
        textColor=colors.white,
        alignment=1
    )
    
    tbl_cell = ParagraphStyle(
        'TblCell',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=6.8,
        leading=8.2,
        textColor=colors.HexColor('#1E293B')
    )
    
    tbl_cell_bold = ParagraphStyle(
        'TblCellBold',
        parent=tbl_cell,
        fontName='Helvetica-Bold'
    )
    
    tbl_cell_center = ParagraphStyle(
        'TblCellCenter',
        parent=tbl_cell,
        alignment=1
    )

    story = []

    # =========================================================================
    # PAGE 1: TITLE, EXECUTIVE MATRIX & LQR
    # =========================================================================
    
    story.append(Paragraph(
        "<b>MATLAB / SIMULINK CONTROL SYSTEMS REFERENCE & TUNING MANUAL</b>",
        ParagraphStyle('Tag', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, textColor=colors.HexColor('#1E3A8A'), alignment=1)
    ))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor('#1E3A8A'), spaceBefore=2, spaceAfter=4))
    
    story.append(Paragraph(
        "Tuning Parameter Reference & Implementation Guide:<br/>LQR, Fixed Super-Twisting SMC, and Adaptive Super-Twisting SMC",
        title_style
    ))
    
    story.append(Paragraph(
        "Department of Electrical and Computer Science Engineering, School of Electrical Engineering (SELECT), VIT Vellore<br/>"
        "Authors: Santhosh G (25BEL0016), Thilang T V (25BEL0036), Ananthakrishnan R (25BEL0005)",
        subtitle_style
    ))

    # Executive Comparison Table
    story.append(Paragraph("I. EXECUTIVE TUNING PARAMETER MATRIX", h1))
    
    exec_data = [
        [Paragraph("Control Method", tbl_hdr), Paragraph("Primary Parameters", tbl_hdr), Paragraph("Typical Value Range", tbl_hdr), Paragraph("Systematic Tuning Criteria", tbl_hdr), Paragraph("Main Advantages / Trade-Offs", tbl_hdr)],
        
        [Paragraph("<b>1. Linear Quadratic Regulator (LQR)</b>", tbl_cell),
         Paragraph("<b>Q</b>: State penalty<br/><b>R</b>: Control effort penalty", tbl_cell),
         Paragraph("Q = diag([100, 1, 100, 1])<br/>R = 0.01 to 10.0", tbl_cell),
         Paragraph("<b>Bryson's Rule:</b><br/>Q<sub>ii</sub> = 1 / (x<sub>i,max</sub>)<sup>2</sup><br/>R<sub>jj</sub> = &rho; / (u<sub>j,max</sub>)<sup>2</sup>", tbl_cell),
         Paragraph("Guaranteed gain margins (&infin;) & phase margin (&ge;60&deg;). Optimal for linear models; degraded by unmodeled nonlinearities and saturations.", tbl_cell)],
         
        [Paragraph("<b>2. Fixed Super-Twisting SMC (STSMC)</b>", tbl_cell),
         Paragraph("&lambda;: Sliding slope<br/><b>k<sub>1</sub></b>: Fractional gain<br/><b>k<sub>2</sub></b>: Integral gain", tbl_cell),
         Paragraph("&lambda; = 5 to 30<br/>k<sub>1</sub> = 1.5 &radic;L &approx; 3 to 15<br/>k<sub>2</sub> = 1.1 L &approx; 10 to 50", tbl_cell),
         Paragraph("<b>Lyapunov Criterion:</b><br/>k<sub>1</sub> = 1.5 &radic;L<br/>k<sub>2</sub> = 1.1 L<br/>where |d'(t)| &le; L", tbl_cell),
         Paragraph("Finite-time convergence of s and ds/dt to zero. Eliminates high-frequency chattering without low-pass filtering. Requires known upper disturbance bound L.", tbl_cell)],
         
        [Paragraph("<b>3. Adaptive Super-Twisting SMC</b>", tbl_cell),
         Paragraph("&alpha;<sub>min</sub>: Base gain<br/>&rho;: Adaptation rate<br/>&mu;: Deadband width<br/>&sigma;: Leakage rate", tbl_cell),
         Paragraph("&alpha;<sub>min</sub> = 1.0 to 5.0<br/>&rho; = 5.0 to 20.0<br/>&mu; = 0.005 to 0.05<br/>&sigma; = 0.5 to 2.0", tbl_cell),
         Paragraph("<b>Anti-Windup Update:</b><br/>d&alpha;/dt = &rho;&radic;|s| for |s| &gt; &mu;<br/>d&alpha;/dt = -&sigma;(&alpha; - &alpha;<sub>min</sub>) for |s| &le; &mu;<br/>&beta;(t) = 2 &alpha;(t)", tbl_cell),
         Paragraph("Dynamically adjusts gains online to reject unknown, time-varying disturbances without knowing L. Deadband prevents gain drift and eliminates chatter.", tbl_cell)]
    ]
    
    exec_table = Table(exec_data, colWidths=[90, 95, 95, 115, 145])
    exec_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#94A3B8')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(exec_table)
    story.append(Spacer(1, 4))

    # Detailed Section 1: LQR
    story.append(Paragraph("II. LINEAR QUADRATIC REGULATOR (LQR) FORMULATION & TUNING", h1))
    story.append(Paragraph(
        "<b>1. Plant Representation:</b> For a continuous-time linear state-space model &nbsp; <i>x'(t) = A x(t) + B u(t)</i> &nbsp; with full state vector <i>x &isin; &real;<sup>n</sup></i> and control input <i>u &isin; &real;<sup>m</sup></i>.<br/>"
        "<b>2. Control Law & Optimization:</b> The optimal state feedback is &nbsp; <b>u = -K x</b>, &nbsp; which minimizes the quadratic cost functional:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<i>J = &int;<sub>0</sub><sup>&infin;</sup> ( x<sup>T</sup> Q x + u<sup>T</sup> R u ) dt</i><br/>"
        "The optimal feedback gain matrix is computed as &nbsp; <b>K = R<sup>-1</sup> B<sup>T</sup> P</b>, &nbsp; where <i>P = P<sup>T</sup> &gt; 0</i> is the unique positive-definite solution to the continuous-time <b>Algebraic Riccati Equation (ARE)</b>:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<i>A<sup>T</sup> P + P A - P B R<sup>-1</sup> B<sup>T</sup> P + Q = 0</i>",
        body
    ))
    story.append(Paragraph(
        "<b>3. Tuning Methodology & Physical Trade-Offs:</b><br/>"
        "&bull; <b>State Weighting Matrix Q &ge; 0:</b> Penalizes deviations of state variables from zero. Increasing <i>Q<sub>ii</sub></i> accelerates the decay rate of <i>x<sub>i</sub>(t)</i>, yielding faster transient rise times and lower steady-state tracking errors.<br/>"
        "&bull; <b>Control Weighting Matrix R &gt; 0:</b> Penalizes control actuator effort. Increasing <i>R<sub>jj</sub></i> prevents control saturation, reduces high-frequency actuator wear, and damps excessive voltage/current spikes, at the expense of slower closed-loop dynamics.<br/>"
        "&bull; <b>Bryson's Tuning Rule:</b> Set <i>Q<sub>ii</sub> = 1 / (x<sub>i,max</sub>)<sup>2</sup></i> where <i>x<sub>i,max</sub></i> is the maximum permissible excursion of state <i>i</i>, and <i>R<sub>jj</sub> = &rho; / (u<sub>j,max</sub>)<sup>2</sup></i> where <i>u<sub>j,max</sub></i> is actuator saturation limit and &rho; &isin; (0, 1] is an aggressiveness factor.",
        body
    ))

    # LQR Parameter Table
    lqr_params = [
        [Paragraph("Parameter", tbl_hdr), Paragraph("Symbol", tbl_hdr), Paragraph("Default Value", tbl_hdr), Paragraph("Tuning Action / Guidelines", tbl_hdr)],
        [Paragraph("State Matrix Weight", tbl_cell_bold), Paragraph("Q", tbl_cell_center), Paragraph("diag([100, 1, 100, 1])", tbl_cell), Paragraph("Increase diagonal elements corresponding to priority states (e.g. angle or position error) to enforce tighter tracking.", tbl_cell)],
        [Paragraph("Effort Penalty Weight", tbl_cell_bold), Paragraph("R", tbl_cell_center), Paragraph("0.1 to 1.0", tbl_cell), Paragraph("Decrease R for faster, more aggressive disturbance rejection; increase R if actuator hits hard torque/voltage saturation limits.", tbl_cell)],
        [Paragraph("Cross-Term Weight", tbl_cell_bold), Paragraph("N", tbl_cell_center), Paragraph("0 (zero matrix)", tbl_cell), Paragraph("Set to zero for uncoupled state-control penalties; only non-zero when state and control cross-coupling explicitly exists.", tbl_cell)]
    ]
    lqr_table = Table(lqr_params, colWidths=[110, 50, 120, 260])
    lqr_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#94A3B8')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(lqr_table)
    
    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: FIXED STSMC & ADAPTIVE STSMC
    # =========================================================================
    story.append(Paragraph("III. FIXED SUPER-TWISTING SLIDING MODE CONTROL (FIXED STSMC)", h1))
    story.append(Paragraph(
        "<b>1. Concept & Chattering Elimination:</b> Standard First-Order Sliding Mode Control enforces <i>s = 0</i> by applying high-frequency switching <i>u = -K sign(s)</i>, causing severe mechanical vibration and chattering. The <b>Super-Twisting Algorithm</b> (Levant, 1993) is a 2nd-order sliding mode technique that drives both <i>s(t) = 0</i> and <i>s'(t) = 0</i> in finite time by embedding the discontinuous signum function beneath a continuous integrator, producing a strictly continuous control signal.",
        body
    ))
    story.append(Paragraph(
        "<b>2. Sliding Surface Definition:</b> For tracking error <i>e(t) = x(t) - x<sub>d</sub>(t)</i>, define the sliding manifold:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>s(t) = e'(t) + &lambda; e(t)</b> &nbsp;&nbsp;&nbsp;&nbsp; (where &lambda; &gt; 0 dictates error decay bandwidth once on the sliding surface)<br/>"
        "<b>3. Super-Twisting Control Law:</b> The control signal comprises an equivalent feedforward term <i>u<sub>eq</sub></i> and super-twisting term <i>u<sub>st</sub></i>:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>u(t) = u<sub>eq</sub>(t) - k<sub>1</sub> |s|<sup>1/2</sup> sign(s) + v(t)</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>v'(t) = -k<sub>2</sub> sign(s)</b>",
        body
    ))
    story.append(Paragraph(
        "<b>4. Lyapunov Stability & Finite-Time Convergence Criterion:</b><br/>"
        "Assume the time derivative of the external disturbance is bounded by |d'(t)| &le; L. Based on the strict Lyapunov matrix inequality derived by Moreno & Osorio (2012), global finite-time convergence to the origin is guaranteed if gains are chosen as:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>k<sub>1</sub> = 1.5 &radic;L</b>, &nbsp;&nbsp;&nbsp;&nbsp; <b>k<sub>2</sub> = 1.1 L</b>",
        body
    ))

    # Fixed STSMC Table
    stsmc_params = [
        [Paragraph("Parameter", tbl_hdr), Paragraph("Symbol", tbl_hdr), Paragraph("Typical Value", tbl_hdr), Paragraph("Physical Role & Tuning Guidelines", tbl_hdr)],
        [Paragraph("Sliding Slope", tbl_cell_bold), Paragraph("&lambda;", tbl_cell_center), Paragraph("5.0 to 25.0", tbl_cell), Paragraph("Governs error convergence speed on the manifold: e(t) = e(0) exp(-&lambda; t). Higher &lambda; increases tracking speed but requires higher control authority.", tbl_cell)],
        [Paragraph("Fractional Gain", tbl_cell_bold), Paragraph("k<sub>1</sub>", tbl_cell_center), Paragraph("1.5 &radic;L &approx; 3.0 to 12.0", tbl_cell), Paragraph("Proportional fractional switching term. Dominates transient convergence toward the sliding surface |s| = 0.", tbl_cell)],
        [Paragraph("Integral Gain", tbl_cell_bold), Paragraph("k<sub>2</sub>", tbl_cell_center), Paragraph("1.1 L &approx; 10.0 to 45.0", tbl_cell), Paragraph("Integral switching term. Cancels smooth, unknown matched disturbances and parameter perturbations in steady state.", tbl_cell)],
        [Paragraph("Boundary Smoothing", tbl_cell_bold), Paragraph("&epsilon;<sub>st</sub>", tbl_cell_center), Paragraph("10<sup>-4</sup> to 10<sup>-3</sup>", tbl_cell), Paragraph("Smooths discontinuous sign(s) into s / (|s| + &epsilon;<sub>st</sub>) in digital implementations to eliminate numerical chatter.", tbl_cell)]
    ]
    stsmc_table = Table(stsmc_params, colWidths=[95, 45, 110, 290])
    stsmc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#94A3B8')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(stsmc_table)
    story.append(Spacer(1, 4))

    # Detailed Section 3: Adaptive STSMC
    story.append(Paragraph("IV. ADAPTIVE SUPER-TWISTING SMC (ADAPTIVE STSMC)", h1))
    story.append(Paragraph(
        "<b>1. Problem with Fixed Gains:</b> In practical environments, the disturbance bound <i>L</i> is rarely known a priori and varies with operating conditions. Overestimating <i>L</i> leads to excessively large fixed gains <i>k<sub>1</sub>, k<sub>2</sub></i>, causing control saturation and high-frequency chatter. Underestimating <i>L</i> causes loss of sliding motion.<br/>"
        "<b>2. Adaptive Control Structure:</b> The adaptive super-twisting control law replaces fixed gains with time-varying gains <i>&alpha;(t)</i> and <i>&beta;(t)</i>:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>u(t) = u<sub>eq</sub>(t) - &alpha;(t) |s|<sup>1/2</sup> sign(s) + v(t)</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>v'(t) = -&beta;(t) sign(s)</b>, &nbsp;&nbsp;&nbsp;&nbsp; where &nbsp; <b>&beta;(t) = &gamma; &alpha;(t)</b> &nbsp; (or &beta; = &alpha;<sup>2</sup> / 4)<br/>"
        "<b>3. Anti-Windup Adaptive Update Law with Deadband & Leakage:</b><br/>"
        "To prevent unbounded gain inflation due to unmodeled high-frequency sensor noise, gains are updated with a deadband threshold <i>&mu;</i> and linear leakage rate <i>&sigma;</i>:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>&alpha;'(t) = &rho; |s|<sup>1/2</sup></b> &nbsp;&nbsp;&nbsp;&nbsp; <i>if &nbsp; |s(t)| &gt; &mu;</i> &nbsp;&nbsp;&nbsp;&nbsp; (Gain ramps up aggressively to eliminate tracking error)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>&alpha;'(t) = -&sigma; (&alpha;(t) - &alpha;<sub>min</sub>)</b> &nbsp;&nbsp;&nbsp;&nbsp; <i>if &nbsp; |s(t)| &le; &mu;</i> &nbsp;&nbsp;&nbsp;&nbsp; (Gain smoothly decays toward minimum baseline to suppress chattering)",
        body
    ))

    # Adaptive STSMC Table
    astsmc_params = [
        [Paragraph("Parameter", tbl_hdr), Paragraph("Symbol", tbl_hdr), Paragraph("Typical Value", tbl_hdr), Paragraph("Physical Role & Tuning Guidelines", tbl_hdr)],
        [Paragraph("Minimum Base Gain", tbl_cell_bold), Paragraph("&alpha;<sub>min</sub>", tbl_cell_center), Paragraph("1.5 to 3.0", tbl_cell), Paragraph("Lower bound for proportional gain. Guarantees nominal control authority when system is inside the deadband.", tbl_cell)],
        [Paragraph("Adaptation Rate", tbl_cell_bold), Paragraph("&rho;", tbl_cell_center), Paragraph("5.0 to 15.0", tbl_cell), Paragraph("Rate of gain increase. Set higher if system experiences sharp, fast disturbances; set lower to prevent gain overshoot.", tbl_cell)],
        [Paragraph("Deadband Width", tbl_cell_bold), Paragraph("&mu;", tbl_cell_center), Paragraph("0.005 to 0.02", tbl_cell), Paragraph("Threshold boundary. Defines the sliding precision. Must be set larger than sensor noise amplitude to prevent drift.", tbl_cell)],
        [Paragraph("Leakage Decay Rate", tbl_cell_bold), Paragraph("&sigma;", tbl_cell_center), Paragraph("0.8 to 2.0", tbl_cell), Paragraph("Rate at which gain decays back to &alpha;<sub>min</sub> when inside deadband. Eliminates steady-state chattering.", tbl_cell)],
        [Paragraph("Coupling Gain Ratio", tbl_cell_bold), Paragraph("&gamma;", tbl_cell_center), Paragraph("1.5 to 2.5", tbl_cell), Paragraph("Proportional-to-integral gain multiplier. Standard value &gamma; = 2.0 satisfies the Shtessel-Edwards Lyapunov condition.", tbl_cell)]
    ]
    astsmc_table = Table(astsmc_params, colWidths=[95, 45, 110, 290])
    astsmc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#94A3B8')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(astsmc_table)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: SIMULINK WIRING & READY-TO-RUN MATLAB CODE
    # =========================================================================
    story.append(Paragraph("V. SIMULINK ARCHITECTURE & WIRING GUIDE", h1))
    story.append(Paragraph(
        "&bull; <b>LQR Block:</b> Feed state vector <i>x = [pos, vel, theta, theta_dot]<sup>T</sup></i> into a <code>Gain</code> block set to <code>-K_lqr</code> (Multiplication: <i>Matrix K*u</i>).<br/>"
        "&bull; <b>Fixed STSMC Block:</b> Compute <code>s = e_dot + lambda_smc * e</code>. Pass <code>s</code> into a MATLAB Function block executing: <code>u_st = -k1 * sqrt(abs(s)) * (s/(abs(s)+eps)) + v</code>, with <code>v</code> fed from an <code>Integrator</code> block with derivative <code>v_dot = -k2 * (s/(abs(s)+eps))</code>.<br/>"
        "&bull; <b>Adaptive STSMC Block:</b> Integrate <code>alpha</code> from initial condition <code>alpha_min</code>. Compute <code>alpha_dot = (abs(s) &gt; mu) * (rho * sqrt(abs(s))) - (abs(s) &lt;= mu) * (sigma * (alpha - alpha_min))</code>, and assign <code>beta = gamma * alpha</code>.<br/>"
        "&bull; <b>Solver Setup:</b> Use fixed-step solver: <code>ode4 (Runge-Kutta)</code> with fixed step size &Delta;t = <code>1e-4 s</code> to eliminate numerical chattering.",
        body
    ))

    story.append(Paragraph("VI. COMPLETE READY-TO-RUN MATLAB INITIALIZATION SCRIPT (init_controllers.m)", h1))
    
    matlab_code = """%% MATLAB / SIMULINK INITIALIZATION SCRIPT: LQR vs FIXED STSMC vs ADAPTIVE STSMC
clear; clc;
% 1. PLANT MATRICES (Example: Linearized Inverted Pendulum on a Cart)
M = 1.0; m = 0.1; l = 0.5; g = 9.81;
A = [0, 1, 0, 0; 0, 0, -m*g/M, 0; 0, 0, 0, 1; 0, 0, (M+m)*g/(M*l), 0];
B = [0; 1/M; 0; -1/(M*l)]; C = eye(4); D = zeros(4,1);

% 2. LQR CONTROLLER PARAMETERS
Q_lqr = diag([100.0, 1.0, 200.0, 1.0]); % State penalty (position & angle)
R_lqr = 0.1;                             % Control effort penalty
[K_lqr, P_lqr, E_lqr] = lqr(A, B, Q_lqr, R_lqr);
fprintf('[1] LQR Gain Matrix K: '); disp(K_lqr);

% 3. FIXED SUPER-TWISTING SMC (STSMC) PARAMETERS
lambda_smc  = 12.0;    % Sliding manifold slope: s = e_dot + lambda*e
L_dist_est  = 15.0;    % Assumed upper bound on disturbance derivative: |d_dot| <= L
k1_fixed    = 1.5 * sqrt(L_dist_est);  % Proportional fractional gain (~5.81)
k2_fixed    = 1.1 * L_dist_est;         % Integral switching gain (~16.50)
eps_smooth  = 1e-4;                     % Boundary layer smoothing: s / (|s| + eps)
fprintf('[2] Fixed STSMC Initialized: lambda=%.1f, k1=%.2f, k2=%.2f\\n', lambda_smc, k1_fixed, k2_fixed);

% 4. ADAPTIVE SUPER-TWISTING SMC (ASTSMC) PARAMETERS
alpha_min   = 2.0;     % Minimum baseline proportional gain
alpha_init  = 2.5;     % Initial gain at t = 0
rho_adapt   = 10.0;    % Adaptation acceleration rate (gain increase when |s| > mu)
mu_deadband = 0.01;    % Deadband threshold (|s| <= mu triggers gain decay)
sigma_leak  = 1.2;     % Gain leakage/decay rate to prevent drift
gamma_rel   = 2.0;     % Proportional-to-integral ratio: beta(t) = gamma * alpha(t)
fprintf('[3] Adaptive STSMC Initialized: alpha_min=%.1f, rho=%.1f, mu=%.3f, sigma=%.1f\\n', ...
    alpha_min, rho_adapt, mu_deadband, sigma_leak);
fprintf('=========================================================================\\n');
fprintf(' Workspace ready! You can now launch your Simulink simulation.\\n');"""

    code_tbl = Table([[Paragraph(matlab_code.replace('\n', '<br/>').replace(' ', '&nbsp;'), code_text)]], colWidths=[540])
    code_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(code_tbl)
    story.append(Spacer(1, 4))

    story.append(Paragraph("VII. TROUBLESHOOTING & COMMON PITFALLS", h1))
    story.append(Paragraph(
        "<b>1. Chattering in Fixed STSMC:</b> If micro-chatter persists, increase the smoothing factor <i>&epsilon;<sub>st</sub></i> from <code>1e-4</code> to <code>1e-3</code>, or reduce solver step size &Delta;t from <code>1e-3 s</code> to <code>1e-4 s</code>.<br/>"
        "<b>2. Gain Inflation / Windup in Adaptive STSMC:</b> If <i>&alpha;(t)</i> drifts to excessively large values during steady-state operation, the deadband <i>&mu;</i> is set too small relative to measurement noise. Increase <i>&mu;</i> (e.g. from <code>0.005</code> to <code>0.02</code>) or increase leakage rate <i>&sigma;</i>.<br/>"
        "<b>3. Algebraic Loops in Simulink:</b> Ensure that the integrator state for <i>v(t)</i> in STSMC does not form a direct algebraic loop with the plant input without passing through an explicit integration or unit delay block.",
        body
    ))

    doc.build(story, canvasmaker=ControlGuideNumberedCanvas)
    print(f"Generated Control Tuning PDF at: {OUTPUT_PDF}")

    try:
        shutil.copyfile(OUTPUT_PDF, DOWNLOADS_PDF)
        print(f"Copied to Downloads: {DOWNLOADS_PDF}")
    except Exception as e:
        print(f"Notice: Could not copy to Downloads: {e}")

if __name__ == "__main__":
    generate_pdf()
