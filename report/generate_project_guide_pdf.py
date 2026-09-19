import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

GITHUB_REPO_URL = "https://github.com/santhoshvellore7119-web/WSN_proj"

class NumberedCanvas(canvas.Canvas):
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
        self.setFont('Helvetica', 8)
        self.setFillColor(colors.HexColor('#64748B'))
        
        # Header on page 2+
        if self._pageNumber > 1:
            self.drawString(38, 758, "WSN Energy-Harvesting Routing Framework — System & Full-Stack Execution Guide")
            self.drawRightString(574, 758, "GitHub: santhoshvellore7119-web/WSN_proj")
            self.setStrokeColor(colors.HexColor('#CBD5E1'))
            self.setLineWidth(0.5)
            self.line(38, 750, 574, 750)
        
        # Footer on all pages
        self.drawString(38, 26, "WSN Project Full-Stack Deployment Manual • Python / FastAPI / React / Docker")
        self.drawRightString(574, 26, f"Page {self._pageNumber} of {page_count}")
        self.setStrokeColor(colors.HexColor('#CBD5E1'))
        self.setLineWidth(0.5)
        self.line(38, 36, 574, 36)
        self.restoreState()


def build_pdf_guide(output_pdf_path: str = "report/wsn_project_execution_guide.pdf"):
    os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        leftMargin=38,
        rightMargin=38,
        topMargin=42,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()

    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=2
    )

    sub_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#2563EB'),
        spaceAfter=6
    )

    github_banner = ParagraphStyle(
        'GitHubBanner',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#0F172A'),
        backColor=colors.HexColor('#F1F5F9'),
        borderColor=colors.HexColor('#3B82F6'),
        borderWidth=1,
        borderPadding=6,
        spaceAfter=8
    )

    h1 = ParagraphStyle(
        'H1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=14.5,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    h2 = ParagraphStyle(
        'H2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=9.2,
        leading=12,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=6,
        spaceAfter=2,
        keepWithNext=True
    )

    body = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.2,
        leading=11,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=3
    )

    bullet = ParagraphStyle(
        'Bullet',
        parent=body,
        leftIndent=10,
        firstLineIndent=-6,
        spaceAfter=2.5
    )

    code_block = ParagraphStyle(
        'CodeBlock',
        parent=body,
        fontName='Courier',
        fontSize=7.3,
        leading=9.5,
        textColor=colors.HexColor('#0F172A'),
        backColor=colors.HexColor('#F8FAFC'),
        borderColor=colors.HexColor('#E2E8F0'),
        borderWidth=0.6,
        borderPadding=4,
        spaceBefore=2,
        spaceAfter=4
    )

    callout = ParagraphStyle(
        'Callout',
        parent=body,
        fontName='Helvetica-Oblique',
        fontSize=7.8,
        leading=10.5,
        textColor=colors.HexColor('#1E40AF'),
        backColor=colors.HexColor('#EFF6FF'),
        borderColor=colors.HexColor('#BFDBFE'),
        borderWidth=0.6,
        borderPadding=4,
        spaceAfter=4
    )

    th = ParagraphStyle(
        'TH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.8,
        leading=10,
        textColor=colors.white
    )

    td = ParagraphStyle(
        'TD',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.2,
        leading=9.2,
        textColor=colors.HexColor('#1E293B')
    )

    td_code = ParagraphStyle(
        'TDCode',
        parent=td,
        fontName='Courier',
        fontSize=6.8,
        leading=8.5,
        textColor=colors.HexColor('#0969DA')
    )

    story = []

    # ==========================================
    # HEADER & GITHUB LINK BANNER
    # ==========================================
    story.append(Paragraph("Adaptive Routing in Energy-Harvesting WSNs", title_style))
    story.append(Paragraph("System Architecture, Mathematical Foundation, and Full-Stack Execution Manual", sub_style))
    
    # Prominent Top GitHub Banner
    gh_html = (
        f"<b>GitHub Repository:</b> <a href='{GITHUB_REPO_URL}'><u>{GITHUB_REPO_URL}</u></a> &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<b>Branch:</b> <code>master</code> &nbsp;&nbsp;|&nbsp;&nbsp; <b>Author:</b> Santhosh"
    )
    story.append(Paragraph(gh_html, github_banner))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor('#2563EB'), spaceAfter=6))

    # ==========================================
    # 1. PROJECT OVERVIEW & ARCHITECTURE
    # ==========================================
    story.append(Paragraph("1. Project Overview &amp; Problem Formulation", h1))
    story.append(Paragraph(
        "In classical battery-powered Wireless Sensor Networks (WSNs), sensor node battery levels decrease monotonically. "
        "Consequently, classical routing protocols (Dijkstra, LEACH, static maximin DP) evaluate nodes using static battery snapshots. "
        "In Energy-Harvesting WSNs (EH-WSNs), nodes recharge dynamically from ambient sources (solar, RF, thermal). "
        "Static algorithms falsely reject intermediate relays that have low energy at round start but would harvest sufficient ambient energy "
        "<i>just-in-time</i> as packets traverse preceding hops. Conversely, static algorithms over-utilize shaded non-harvesting nodes, "
        "causing early bottleneck depletion. This project delivers a unified simulation engine, algorithmic innovations, and a modern full-stack web interface.",
        body
    ))

    # Architecture Overview Table
    arch_data = [
        [Paragraph("Subsystem", th), Paragraph("Technology Stack", th), Paragraph("Key Role &amp; Capabilities", th)],
        [
            Paragraph("<b>Simulation Core</b>", td),
            Paragraph("Python 3.10+, NumPy, SciPy, Matplotlib", td),
            Paragraph("3D Time-Augmented DP, DSU detour repair, 1st-order radio model, LEACH/EH-LEACH, diurnal solar traces, 52 unit tests.", td)
        ],
        [
            Paragraph("<b>Backend API</b>", td),
            Paragraph("FastAPI, Uvicorn, SQLite, Pydantic, SQLAlchemy", td),
            Paragraph("Async REST API (Port 8000), background job execution, simulation parameter persistence, Swagger/OpenAPI documentation.", td)
        ],
        [
            Paragraph("<b>Frontend UI</b>", td),
            Paragraph("React 19, TypeScript, Vite, Tailwind CSS, Recharts", td),
            Paragraph("Interactive single-page application (Port 3000), live node topology canvas, round-by-round replay, multi-metric time-series charts.", td)
        ],
        [
            Paragraph("<b>Containerization</b>", td),
            Paragraph("Docker, Docker Compose", td),
            Paragraph("Multi-service container orchestration bundling backend and frontend for zero-configuration deployment.", td)
        ]
    ]
    t_arch = Table(arch_data, colWidths=[90, 150, 296])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 4))

    # ==========================================
    # 2. CORE ALGORITHMIC CONTRIBUTIONS
    # ==========================================
    story.append(Paragraph("2. Key Algorithmic Contributions &amp; Physical Modeling", h1))
    story.append(Paragraph(
        "&bull; <b>3D Time-Augmented Dynamic Programming (dp[v][h][t]):</b> Formulates a state recurrence over a time-expanded DAG where "
        "<i>dp[v][h][t] = max_{u &isin; nbr(v)} min(dp[u][h-1][t-&delta;], E_proj(v, t_curr + t))</i>. Operates in polynomial time <i>O(|E| &middot; H &middot; T)</i> "
        "and space <i>O(|V| &middot; H &middot; T)</i> (&lt;50 kB RAM), providing provable 2&epsilon;-approximation bounds.<br/>"
        "&bull; <b>Disjoint-Set Union (DSU) Live Detour Recovery:</b> Slices local alternate paths around depleted intermediate relays in "
        "<i>O(|E|&alpha;(V) + deg(u)&alpha;(V))</i>, maintaining 0% packet loss and achieving a <b>3.3&ndash;6.1&times; speedup</b> over global Time-DP recalculation.<br/>"
        "&bull; <b>First-Order Radio Dissipation &amp; Reception Penalty (E_rx):</b> Models physical transmission dissipation "
        "<i>E_tx = k &middot; (E_elec + &epsilon;_fs &middot; d^2)</i> (or <i>&epsilon;_mp &middot; d^4</i>) alongside unavoidable electronic reception dissipation "
        "<i>E_rx = k &middot; E_elec</i> on all intermediate forwarders.<br/>"
        "&bull; <b>Diurnal Solar &amp; Shadow Trace Replay:</b> Evaluates 24-hour diurnal solar irradiance profiles (clear sky, intermittent cloudy, overcast) "
        "and canopy occlusion fractions (p_shadow &isin; [0.0, 1.0]).",
        bullet
    ))
    story.append(Spacer(1, 4))

    # ==========================================
    # 3. PREREQUISITES & ENVIRONMENT SETUP
    # ==========================================
    story.append(Paragraph("3. Prerequisites &amp; Environment Setup", h1))
    story.append(Paragraph(
        "<b>Required Software:</b> Python 3.10+ (tested on Python 3.12), Node.js 18+ &amp; npm, Git. Optional: Docker &amp; Docker Compose.",
        body
    ))
    story.append(Paragraph(
        "<b>Step 1: Clone the Repository</b><br/>"
        "<font face='Courier' size='7.5'>git clone https://github.com/santhoshvellore7119-web/WSN_proj.git<br/>cd WSN_proj</font>",
        code_block
    ))
    story.append(Paragraph(
        "<b>Step 2: Create and Activate Virtual Environment</b><br/>"
        "• <u>Windows (Command Prompt / PowerShell):</u><br/>"
        "<font face='Courier' size='7.5'>python -m venv .venv<br/>.venv\\Scripts\\activate</font><br/>"
        "• <u>Linux / macOS:</u><br/>"
        "<font face='Courier' size='7.5'>python3 -m venv .venv<br/>source .venv/bin/activate</font>",
        code_block
    ))
    story.append(Paragraph(
        "<b>Step 3: Install Python Dependencies</b><br/>"
        "<font face='Courier' size='7.5'>pip install --upgrade pip<br/>pip install -r requirements.txt</font>",
        code_block
    ))
    story.append(Paragraph(
        "<b>Step 4: Verify Installation with Test Suite Tripwire</b><br/>"
        "<font face='Courier' size='7.5'>pytest -q</font>&nbsp;&nbsp;&nbsp;&nbsp;<i>(Expected output: 52 passed in &lt; 3.5s)</i>",
        code_block
    ))

    story.append(PageBreak())

    # ==========================================
    # 4. RUNNING EXPERIMENTS IN CMD / TERMINAL
    # ==========================================
    story.append(Paragraph("4. Running CLI Simulations &amp; Scientific Experiments in CMD", h1))
    story.append(Paragraph(
        "All simulation scenarios, multi-seed statistical tests, and benchmark sweeps can be executed directly from CMD or PowerShell:",
        body
    ))

    exp_data = [
        [Paragraph("Script / Command", th), Paragraph("Description &amp; Output Artifacts", th)],
        [
            Paragraph("<font face='Courier' size='6.8'>python main.py --nodes 50 --rounds 200 --harvesting solar --visualize</font>", td),
            Paragraph("Runs single 50-node simulation with interactive Matplotlib topology and energy history plots.", td)
        ],
        [
            Paragraph("<font face='Courier' size='6.8'>python run_experiments.py</font>", td),
            Paragraph("Executes the 5 canonical scenarios (Baseline, Solar Unaware, Solar Time-DP, Shadowed, Stochastic). Outputs comparison charts in <code>results/</code>.", td)
        ],
        [
            Paragraph("<font face='Courier' size='6.8'>python run_multiseed.py</font>", td),
            Paragraph("Runs 30-seed Monte Carlo evaluation (350 rounds/seed). Computes paired t-tests, Wilcoxon W, Cohen's d, and 95% Confidence Intervals.", td)
        ],
        [
            Paragraph("<font face='Courier' size='6.8'>python run_heterogeneity_sweep.py</font>", td),
            Paragraph("Sweeps canopy occlusion <i>p_shadow &isin; [0.0, 1.0]</i>. Generates sensitivity curves demonstrating the multi-hop E_rx reception threshold.", td)
        ],
        [
            Paragraph("<font face='Courier' size='6.8'>python run_scalability_benchmark.py</font>", td),
            Paragraph("Measures empirical latency scaling from N=50 to N=500 nodes with isolated timer blocks (Dijkstra vs DP vs Time-DP vs DSU Detour).", td)
        ],
        [
            Paragraph("<font face='Courier' size='6.8'>python run_dsu_benchmark.py</font>", td),
            Paragraph("Benchmarks DSU detour repair speedup across failure rates (0%–30%) over 10 seeds, showing 3.3–6.1x speedup over Time-DP recomputation.", td)
        ],
        [
            Paragraph("<font face='Courier' size='6.8'>python run_real_trace_experiment.py</font>", td),
            Paragraph("Replays 24-hour diurnal solar irradiance profiles across Clear Sky, Cloudy, and Overcast conditions.", td)
        ],
        [
            Paragraph("<font face='Courier' size='6.8'>python run_real_world_case_study.py</font>", td),
            Paragraph("Runs the Great Duck Island habitat monitoring case study (N=32 motes with spatial canopy heterogeneity).", td)
        ]
    ]
    t_exp = Table(exp_data, colWidths=[200, 336])
    t_exp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_exp)
    story.append(Spacer(1, 4))

    # ==========================================
    # 5. RUNNING & DEBUGGING IN VS CODE
    # ==========================================
    story.append(Paragraph("5. Step-by-Step Setup &amp; Execution in Visual Studio Code (VS Code)", h1))
    story.append(Paragraph(
        "<b>1. Open Workspace:</b> Launch VS Code in the root project folder: <font face='Courier' size='7.5'>code .</font><br/>"
        "<b>2. Select Python Interpreter:</b> Press <code>Ctrl+Shift+P</code> (or <code>Cmd+Shift+P</code> on macOS), type <b>Python: Select Interpreter</b>, "
        "and choose the virtual environment interpreter at <code>.\\.venv\\Scripts\\python.exe</code>.<br/>"
        "<b>3. Split Terminals Setup:</b> Open the integrated terminal (<code>Ctrl+`</code>) and split it into two panes (<code>Ctrl+\\</code>):<br/>"
        "&nbsp;&nbsp;&nbsp;&bull; <b>Terminal Pane 1 (Backend):</b> <font face='Courier' size='7.5'>cd backend &amp;&amp; python -m uvicorn main:app --reload --port 8000</font><br/>"
        "&nbsp;&nbsp;&nbsp;&bull; <b>Terminal Pane 2 (Frontend):</b> <font face='Courier' size='7.5'>cd frontend &amp;&amp; npm run dev</font><br/>"
        "<b>4. Interactive Debugging (.vscode/launch.json):</b> Create a launch configuration to set breakpoints in simulation algorithms or API routes:",
        body
    ))
    story.append(Paragraph(
        "// .vscode/launch.json example configuration:<br/>"
        "{\n"
        "  \"version\": \"0.2.0\",\n"
        "  \"configurations\": [\n"
        "    {\n"
        "      \"name\": \"Python: FastAPI Backend\",\n"
        "      \"type\": \"debugpy\",\n"
        "      \"request\": \"launch\",\n"
        "      \"module\": \"uvicorn\",\n"
        "      \"args\": [\"backend.main:app\", \"--reload\", \"--port\", \"8000\"],\n"
        "      \"jinja\": true\n"
        "    },\n"
        "    {\n"
        "      \"name\": \"Python: Run Experiments\",\n"
        "      \"type\": \"debugpy\",\n"
        "      \"request\": \"launch\",\n"
        "      \"program\": \"${workspaceFolder}/run_experiments.py\"\n"
        "    }\n"
        "  ]\n"
        "}",
        code_block
    ))
    story.append(Spacer(1, 4))

    # ==========================================
    # 6. FULL-STACK DEVELOPMENT WORKFLOW
    # ==========================================
    story.append(Paragraph("6. Full-Stack Web Application Development Workflow", h1))
    story.append(Paragraph(
        "The project includes a production-grade full-stack web application with a responsive React frontend and a FastAPI backend.",
        body
    ))

    story.append(Paragraph("<b>Backend API Architecture (FastAPI + SQLite on Port 8000):</b>", h2))
    story.append(Paragraph(
        "• <b>Start Backend:</b> <font face='Courier' size='7.5'>cd backend &amp;&amp; python -m uvicorn main:app --reload --port 8000</font><br/>"
        "• <b>Interactive API Documentation (Swagger UI):</b> Open <a href='http://localhost:8000/docs'><u>http://localhost:8000/docs</u></a> to inspect and test all endpoints.<br/>"
        "• <b>Alternative Redoc Docs:</b> Available at <a href='http://localhost:8000/redoc'><u>http://localhost:8000/redoc</u></a>.<br/>"
        "• <b>Database Persistence:</b> Simulation runs, configurations, and summary statistics are automatically stored in <code>backend/wsn_simulator.db</code> (SQLite).",
        bullet
    ))

    story.append(Paragraph("<b>Frontend Dashboard Architecture (React 19 + Vite on Port 3000):</b>", h2))
    story.append(Paragraph(
        "• <b>Install Dependencies:</b> <font face='Courier' size='7.5'>cd frontend &amp;&amp; npm install</font><br/>"
        "• <b>Start Dev Server:</b> <font face='Courier' size='7.5'>npm run dev</font><br/>"
        "• <b>Web Dashboard URL:</b> Open <a href='http://localhost:3000'><u>http://localhost:3000</u></a> in any browser.<br/>"
        "• <b>Vite API Proxy:</b> <code>frontend/server.ts</code> automatically proxies all <code>/api/*</code> HTTP requests to the FastAPI backend at <code>http://127.0.0.1:8000</code>.",
        bullet
    ))

    story.append(PageBreak())

    # Key REST API Endpoints Table
    story.append(Paragraph("<b>Key Backend REST API Endpoints:</b>", h2))
    api_data = [
        [Paragraph("HTTP Method &amp; Route", th), Paragraph("Request Body / Params", th), Paragraph("Function &amp; Response Payload", th)],
        [
            Paragraph("<font face='Courier' size='6.8'>POST /api/run-simulation</font>", td_code),
            Paragraph("JSON: { num_nodes, rounds, harvesting_profile, enable_time_dp, ... }", td),
            Paragraph("Triggers asynchronous simulation. Returns job ID and initial status.", td)
        ],
        [
            Paragraph("<font face='Courier' size='6.8'>GET /api/simulation/{job_id}</font>", td_code),
            Paragraph("Path param: job_id (UUID)", td),
            Paragraph("Polls simulation status, topology coordinates, and round-by-round energy telemetry.", td)
        ],
        [
            Paragraph("<font face='Courier' size='6.8'>GET /api/scenarios</font>", td_code),
            Paragraph("None", td),
            Paragraph("Returns list of pre-configured scenario templates (Baseline, Solar, Shadow, Stochastic).", td)
        ],
        [
            Paragraph("<font face='Courier' size='6.8'>GET /api/history</font>", td_code),
            Paragraph("Query: limit, offset", td),
            Paragraph("Fetches paginated past simulation runs from SQLite database.", td)
        ],
        [
            Paragraph("<font face='Courier' size='6.8'>GET /api/export/{job_id}/csv</font>", td_code),
            Paragraph("Path param: job_id", td),
            Paragraph("Downloads full round-by-round simulation metrics as a CSV spreadsheet.", td)
        ]
    ]
    t_api = Table(api_data, colWidths=[140, 160, 236])
    t_api.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_api)
    story.append(Spacer(1, 4))

    # ==========================================
    # 7. DOCKER COMPOSE DEPLOYMENT
    # ==========================================
    story.append(Paragraph("7. Containerized Deployment via Docker Compose", h1))
    story.append(Paragraph(
        "For a zero-dependency setup without configuring local Python or Node environments, run both services with Docker:",
        body
    ))
    story.append(Paragraph(
        "# Build and boot full-stack services in background:<br/>"
        "<font face='Courier' size='7.5'>docker compose up --build -d</font><br/><br/>"
        "# View live container logs:<br/>"
        "<font face='Courier' size='7.5'>docker compose logs -f</font><br/><br/>"
        "# Stop all services:<br/>"
        "<font face='Courier' size='7.5'>docker compose down</font>",
        code_block
    ))
    story.append(Paragraph(
        "• <b>Web Dashboard:</b> <a href='http://localhost:3000'><u>http://localhost:3000</u></a> &nbsp;&nbsp;|&nbsp;&nbsp; "
        "• <b>FastAPI Backend Docs:</b> <a href='http://localhost:8000/docs'><u>http://localhost:8000/docs</u></a>",
        callout
    ))
    story.append(Spacer(1, 4))

    # ==========================================
    # 8. TROUBLESHOOTING & COMMON PITFALLS
    # ==========================================
    story.append(Paragraph("8. Troubleshooting &amp; Common Pitfalls", h1))
    trouble_data = [
        [Paragraph("Issue / Error Symptom", th), Paragraph("Root Cause", th), Paragraph("Recommended Solution", th)],
        [
            Paragraph("<b>PowerShell Script Execution Disabled</b><br/><code>running scripts is disabled on this system</code>", td),
            Paragraph("Windows PowerShell default execution policy blocks <code>activate.ps1</code>.", td),
            Paragraph("Run in PowerShell:<br/><code>Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass</code> then reactivate <code>.venv\\Scripts\\activate</code>.", td)
        ],
        [
            Paragraph("<b>Port 8000 or 3000 in Use</b><br/><code>[Errno 10048] address already in use</code>", td),
            Paragraph("A previous backend or frontend process is still bound to the port.", td),
            Paragraph("Find and terminate process:<br/>• Windows: <code>netstat -ano | findstr :8000</code> then <code>taskkill /PID &lt;PID&gt; /F</code><br/>• Linux/macOS: <code>lsof -ti:8000 | xargs kill -9</code>", td)
        ],
        [
            Paragraph("<b>ModuleNotFoundError: No module named 'src'</b>", td),
            Paragraph("Python script executed from a subfolder without root in PYTHONPATH.", td),
            Paragraph("Run all experiment scripts from the repository root directory (e.g., <code>python run_experiments.py</code>).", td)
        ],
        [
            Paragraph("<b>502 Bad Gateway on Frontend</b><br/><code>Backend service unavailable</code>", td),
            Paragraph("Frontend Vite proxy cannot reach FastAPI on port 8000.", td),
            Paragraph("Ensure the FastAPI backend is running in Terminal 1 before launching the React dev server in Terminal 2.", td)
        ]
    ]
    t_trouble = Table(trouble_data, colWidths=[160, 160, 216])
    t_trouble.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_trouble)
    story.append(Spacer(1, 4))

    # ==========================================
    # 9. COMPLETE COMMAND REFERENCE CHEAT-SHEET
    # ==========================================
    story.append(Paragraph("9. Quick Command Reference Cheat-Sheet", h1))
    cmd_data = [
        [Paragraph("Task / Operation", th), Paragraph("Command Line String", th)],
        [Paragraph("Clone Project", td), Paragraph("<font face='Courier' size='6.8'>git clone https://github.com/santhoshvellore7119-web/WSN_proj.git</font>", td)],
        [Paragraph("Create Virtual Env (Win)", td), Paragraph("<font face='Courier' size='6.8'>python -m venv .venv &amp;&amp; .venv\\Scripts\\activate</font>", td)],
        [Paragraph("Install Python Requirements", td), Paragraph("<font face='Courier' size='6.8'>pip install -r requirements.txt</font>", td)],
        [Paragraph("Run Unit Tests (52 tests)", td), Paragraph("<font face='Courier' size='6.8'>pytest -q</font>", td)],
        [Paragraph("Start FastAPI Backend", td), Paragraph("<font face='Courier' size='6.8'>cd backend &amp;&amp; python -m uvicorn main:app --reload --port 8000</font>", td)],
        [Paragraph("Start React Frontend", td), Paragraph("<font face='Courier' size='6.8'>cd frontend &amp;&amp; npm install &amp;&amp; npm run dev</font>", td)],
        [Paragraph("Run 30-Seed Evaluation", td), Paragraph("<font face='Courier' size='6.8'>python run_multiseed.py</font>", td)],
        [Paragraph("Run Scalability Benchmark", td), Paragraph("<font face='Courier' size='6.8'>python run_scalability_benchmark.py</font>", td)],
        [Paragraph("Run Docker Full-Stack", td), Paragraph("<font face='Courier' size='6.8'>docker compose up --build</font>", td)]
    ]
    t_cmd = Table(cmd_data, colWidths=[150, 386])
    t_cmd.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_cmd)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated project execution guide PDF at: {output_pdf_path}")


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'report/wsn_project_execution_guide.pdf'
    build_pdf_guide(out)
