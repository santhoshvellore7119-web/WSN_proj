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
    """
    Two-pass canvas to dynamically compute and stamp total page numbers,
    running headers, and footers on all pages.
    """
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []
        self.is_bw = kwargs.get('is_bw', False)

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
        
        # Color definitions for header/footer
        text_color = colors.HexColor('#444444') if getattr(self, 'is_bw', False) else colors.HexColor('#64748B')
        line_color = colors.HexColor('#888888') if getattr(self, 'is_bw', False) else colors.HexColor('#CBD5E1')
        
        self.setFillColor(text_color)
        
        # Header on page 2+
        if self._pageNumber > 1:
            self.drawString(38, 758, "WSN Energy-Harvesting Routing Simulator - Full-Stack Execution Guide")
            self.drawRightString(574, 758, "GitHub: santhoshvellore7119-web/WSN_proj")
            self.setStrokeColor(line_color)
            self.setLineWidth(0.5)
            self.line(38, 750, 574, 750)
        
        # Footer on all pages
        self.drawString(38, 26, "Full-Stack Deployment Manual * FastAPI (Port 8000) + React (Port 3000)")
        self.drawRightString(574, 26, f"Page {self._pageNumber} of {page_count}")
        self.setStrokeColor(line_color)
        self.setLineWidth(0.5)
        self.line(38, 36, 574, 36)
        self.restoreState()


def make_canvas_class(is_bw: bool):
    class CustomNumberedCanvas(NumberedCanvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.is_bw = is_bw
    return CustomNumberedCanvas


def build_pdf_guide(output_pdf_path: str = "report/wsn_project_execution_guide.pdf", is_bw: bool = False):
    """
    Builds the complete full-stack execution guide PDF.
    Supports standard color palette or high-contrast monochrome (B&W) palette.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_pdf_path)), exist_ok=True)

    # Determine if B&W mode based on parameter or filename
    if "bw" in os.path.basename(output_pdf_path).lower():
        is_bw = True

    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        leftMargin=38,
        rightMargin=38,
        topMargin=40,
        bottomMargin=44
    )

    styles = getSampleStyleSheet()

    # Palette setup
    if is_bw:
        c_title = colors.HexColor('#000000')
        c_sub = colors.HexColor('#333333')
        c_h1 = colors.HexColor('#000000')
        c_h2 = colors.HexColor('#222222')
        c_body = colors.HexColor('#111111')
        c_line = colors.HexColor('#000000')
        c_th_bg = colors.HexColor('#222222')
        c_th_text = colors.white
        c_td_text = colors.HexColor('#111111')
        c_td_code = colors.HexColor('#000000')
        c_grid = colors.HexColor('#888888')
        c_row_alt = colors.HexColor('#F5F5F5')
        c_code_bg = colors.HexColor('#F8F8F8')
        c_code_border = colors.HexColor('#CCCCCC')
        c_code_text = colors.HexColor('#000000')
        c_banner_bg = colors.HexColor('#F0F0F0')
        c_banner_border = colors.HexColor('#444444')
        c_banner_text = colors.HexColor('#000000')
        c_callout_bg = colors.HexColor('#EFEFEF')
        c_callout_border = colors.HexColor('#333333')
        c_callout_text = colors.HexColor('#000000')
        c_warn_bg = colors.HexColor('#E5E5E5')
        c_warn_border = colors.HexColor('#000000')
        c_warn_text = colors.HexColor('#000000')
    else:
        c_title = colors.HexColor('#0F172A')
        c_sub = colors.HexColor('#2563EB')
        c_h1 = colors.HexColor('#0F172A')
        c_h2 = colors.HexColor('#1E3A8A')
        c_body = colors.HexColor('#1E293B')
        c_line = colors.HexColor('#2563EB')
        c_th_bg = colors.HexColor('#0F172A')
        c_th_text = colors.white
        c_td_text = colors.HexColor('#1E293B')
        c_td_code = colors.HexColor('#0969DA')
        c_grid = colors.HexColor('#CBD5E1')
        c_row_alt = colors.HexColor('#F8FAFC')
        c_code_bg = colors.HexColor('#F8FAFC')
        c_code_border = colors.HexColor('#E2E8F0')
        c_code_text = colors.HexColor('#0F172A')
        c_banner_bg = colors.HexColor('#F1F5F9')
        c_banner_border = colors.HexColor('#3B82F6')
        c_banner_text = colors.HexColor('#0F172A')
        c_callout_bg = colors.HexColor('#EFF6FF')
        c_callout_border = colors.HexColor('#BFDBFE')
        c_callout_text = colors.HexColor('#1E40AF')
        c_warn_bg = colors.HexColor('#FEF2F2')
        c_warn_border = colors.HexColor('#DC2626')
        c_warn_text = colors.HexColor('#991B1B')

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=c_title,
        spaceAfter=2
    )

    sub_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12.5,
        textColor=c_sub,
        spaceAfter=5
    )

    github_banner = ParagraphStyle(
        'GitHubBanner',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=c_banner_text,
        backColor=c_banner_bg,
        borderColor=c_banner_border,
        borderWidth=1,
        borderPadding=5,
        spaceAfter=6
    )

    h1 = ParagraphStyle(
        'H1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=13.5,
        textColor=c_h1,
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    )

    body = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.5,
        textColor=c_body,
        spaceAfter=2
    )

    bullet = ParagraphStyle(
        'Bullet',
        parent=body,
        leftIndent=9,
        firstLineIndent=-6,
        spaceAfter=1.5
    )

    code_block = ParagraphStyle(
        'CodeBlock',
        parent=body,
        fontName='Courier',
        fontSize=7.0,
        leading=9.0,
        textColor=c_code_text,
        backColor=c_code_bg,
        borderColor=c_code_border,
        borderWidth=0.6,
        borderPadding=3.5,
        spaceBefore=1,
        spaceAfter=3
    )

    callout = ParagraphStyle(
        'Callout',
        parent=body,
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.8,
        textColor=c_callout_text,
        backColor=c_callout_bg,
        borderColor=c_callout_border,
        borderWidth=0.6,
        borderPadding=3,
        spaceAfter=3
    )

    warning_box = ParagraphStyle(
        'WarningBox',
        parent=body,
        fontName='Helvetica-Bold',
        fontSize=7.6,
        leading=10.0,
        textColor=c_warn_text,
        backColor=c_warn_bg,
        borderColor=c_warn_border,
        borderWidth=0.8,
        borderPadding=4,
        spaceBefore=2,
        spaceAfter=3.5
    )

    th = ParagraphStyle(
        'TH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.2,
        leading=9.2,
        textColor=c_th_text
    )

    td = ParagraphStyle(
        'TD',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=6.8,
        leading=8.8,
        textColor=c_td_text
    )

    td_code = ParagraphStyle(
        'TDCode',
        parent=td,
        fontName='Courier',
        fontSize=6.5,
        leading=8.2,
        textColor=c_td_code
    )

    story = []

    # ==========================================
    # HEADER & GITHUB LINK BANNER
    # ==========================================
    story.append(Paragraph("WSN Energy-Harvesting Routing Simulator", title_style))
    story.append(Paragraph("Full-Stack Web Application Execution &amp; Setup Guide (FastAPI Backend + React Frontend)", sub_style))
    
    gh_html = (
        f"<b>GitHub Repository:</b> <a href='{GITHUB_REPO_URL}'><u>{GITHUB_REPO_URL}</u></a> &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<b>Branch:</b> <code>master</code> &nbsp;&nbsp;|&nbsp;&nbsp; <b>Author:</b> Santhosh"
    )
    story.append(Paragraph(gh_html, github_banner))
    story.append(HRFlowable(width="100%", thickness=1.0, color=c_line, spaceAfter=4))

    # ==========================================
    # 1. FULL-STACK ARCHITECTURE OVERVIEW
    # ==========================================
    story.append(Paragraph("1. Full-Stack System Architecture Overview", h1))
    story.append(Paragraph(
        "The system pairs an asynchronous FastAPI REST backend with a modern React 19 single-page application. "
        "The frontend provides an interactive SVG topology canvas, replay controls, and real-time residual energy charts.",
        body
    ))

    arch_data = [
        [Paragraph("Layer", th), Paragraph("Tech Stack &amp; Port", th), Paragraph("Role &amp; Responsibilities", th)],
        [
            Paragraph("<b>Frontend UI</b>", td),
            Paragraph("React 19, TypeScript, Vite, Tailwind CSS, Recharts<br/><b>Port 3000</b>", td),
            Paragraph("Interactive dashboard: real-time SVG topology visualization, round replay controls, dynamic energy analytics.", td)
        ],
        [
            Paragraph("<b>Backend API</b>", td),
            Paragraph("FastAPI, Uvicorn, SQLite, SQLAlchemy, Pydantic<br/><b>Port 8000</b>", td),
            Paragraph("Async REST API: manages background simulation jobs, SQLite database persistence, and OpenAPI Swagger documentation.", td)
        ],
        [
            Paragraph("<b>Simulation Engine</b>", td),
            Paragraph("Python 3.10+, NumPy, SciPy<br/>(Core Library in <code>src/</code>)", td),
            Paragraph("Executes 3D Time-Augmented DP ($dp[v][h][t]$), DSU live detour recovery, LEACH clustering, and solar irradiance traces.", td)
        ]
    ]
    t_arch = Table(arch_data, colWidths=[80, 160, 296])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_th_bg),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.4, c_grid),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_row_alt]),
        ('TOPPADDING', (0, 0), (-1, -1), 2.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.2),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 2))

    # ==========================================
    # CRITICAL WORKING DIRECTORY NOTICE
    # ==========================================
    warn_html = (
        "<b>CRITICAL WORKING DIRECTORY REQUIREMENT:</b><br/>"
        "• <b>Project Root:</b> <code>C:\\Users\\Santhosh\\wsn-energy-routing</code><br/>"
        "• <b>Frontend Folder:</b> <code>C:\\Users\\Santhosh\\wsn-energy-routing\\frontend</code><br/>"
        "• <b>CAUTION:</b> Do <u>NOT</u> run commands inside <code>C:\\Users\\Santhosh\\frontend</code> (which is an unrelated, separate project). "
        "Executing commands in the wrong directory will trigger <i>'Missing script: dev'</i> or <i>'requirements.txt not found'</i>."
    )
    story.append(Paragraph(warn_html, warning_box))

    # ==========================================
    # 2. PREREQUISITES & INITIAL SETUP
    # ==========================================
    story.append(Paragraph("2. Prerequisites &amp; One-Time Initial Setup", h1))
    story.append(Paragraph(
        "Ensure the following tools are installed: <b>Python 3.10+</b> (with pip), <b>Node.js 18+</b> (with npm), and <b>Git</b>.",
        body
    ))
    story.append(Paragraph(
        "<b>Step 1: Open or Clone the Repository</b><br/>"
        "<font face='Courier' size='7.0'>"
        "cd C:\\Users\\Santhosh\\wsn-energy-routing<br/>"
        "# (If cloning for the first time: git clone https://github.com/santhoshvellore7119-web/WSN_proj.git wsn-energy-routing)"
        "</font>",
        code_block
    ))
    story.append(Paragraph(
        "<b>Step 2: Setup Python Virtual Environment (.venv) &amp; Install Backend Dependencies</b><br/>"
        "• <u>Windows (CMD / PowerShell):</u><br/>"
        "<font face='Courier' size='7.0'>"
        "cd C:\\Users\\Santhosh\\wsn-energy-routing<br/>"
        "python -m venv .venv<br/>"
        ".venv\\Scripts\\activate<br/>"
        "python -m pip install --upgrade pip<br/>"
        "pip install -r requirements.txt"
        "</font><br/>"
        "<i>(Note: Always use <code>python -m pip install</code> to prevent Windows binary-locking update errors)</i>",
        code_block
    ))
    story.append(Paragraph(
        "<b>Step 3: Install Frontend Node Dependencies</b><br/>"
        "<font face='Courier' size='7.0'>"
        "cd C:\\Users\\Santhosh\\wsn-energy-routing\\frontend<br/>"
        "npm install<br/>"
        "cd .."
        "</font>",
        code_block
    ))

    # ==========================================
    # 3. HOW TO RUN IN CMD / POWERSHELL
    # ==========================================
    story.append(Paragraph("3. How to Run the Full-Stack Application", h1))
    story.append(Paragraph(
        "<b>Method A: Automated 1-Click Startup (Recommended)</b><br/>"
        "A pre-configured startup script is included in the project root to automatically manage ports, activate environments, and launch both servers:<br/>"
        "<font face='Courier' size='7.0'>"
        "cd C:\\Users\\Santhosh\\wsn-energy-routing<br/>"
        ".\\start_offline.bat"
        "</font><br/>"
        "<i>(Or simply double-click <code>start_offline.bat</code> in Windows File Explorer. It cleans ports 8000/3000, starts FastAPI, starts React, and opens http://localhost:3000 in your browser).</i>",
        callout
    ))
    story.append(Paragraph(
        "<b>Method B: Manual Startup in Two Terminals</b><br/>"
        "• <u>Terminal 1 — Backend (Port 8000):</u><br/>"
        "<font face='Courier' size='7.0'>"
        "cd C:\\Users\\Santhosh\\wsn-energy-routing<br/>"
        ".venv\\Scripts\\activate<br/>"
        "python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"
        "</font><br/>"
        "• <u>Terminal 2 — Frontend (Port 3000):</u><br/>"
        "<font face='Courier' size='7.0'>"
        "cd C:\\Users\\Santhosh\\wsn-energy-routing\\frontend<br/>"
        "npm run dev"
        "</font><br/>"
        "• <i>Dashboard:</i> <b>http://localhost:3000</b> &nbsp;|&nbsp; <i>Swagger API Docs:</i> <b>http://127.0.0.1:8000/docs</b>",
        code_block
    ))

    story.append(PageBreak())

    # ==========================================
    # 4. HOW TO RUN IN VS CODE
    # ==========================================
    story.append(Paragraph("4. Step-by-Step Procedure to Run in Visual Studio Code (VS Code)", h1))
    story.append(Paragraph(
        "Follow these steps for a clean, integrated development workflow inside VS Code:",
        body
    ))
    story.append(Paragraph(
        "<b>Step 1: Open Project in VS Code</b><br/>"
        "Open terminal and launch VS Code at the project root: <font face='Courier' size='7.0'>cd C:\\Users\\Santhosh\\wsn-energy-routing &amp;&amp; code .</font>",
        bullet
    ))
    story.append(Paragraph(
        "<b>Step 2: Select Python Interpreter</b><br/>"
        "1. Press <code>Ctrl + Shift + P</code> (or <code>Cmd + Shift + P</code> on macOS).<br/>"
        "2. Type and select <b>Python: Select Interpreter</b>.<br/>"
        "3. Choose the workspace virtual environment: <code>.\\.venv\\Scripts\\python.exe</code>.",
        bullet
    ))
    story.append(Paragraph(
        "<b>Step 3: Open Integrated Split Terminals</b><br/>"
        "1. Open the terminal panel with <code>Ctrl + `</code> (backtick).<br/>"
        "2. Click the <b>Split Terminal</b> icon on the top right (or press <code>Ctrl + \\</code>).<br/>"
        "3. In the <b>Left Pane (Backend)</b>, run:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<font face='Courier' size='7.0'>.\\.venv\\Scripts\\activate &amp;&amp; python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000</font><br/>"
        "4. In the <b>Right Pane (Frontend)</b>, run:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<font face='Courier' size='7.0'>cd frontend &amp;&amp; npm run dev</font>",
        bullet
    ))
    story.append(Paragraph(
        "<b>Step 4: Optional 1-Click Debugging via .vscode/launch.json</b><br/>"
        "Configure the VS Code debugger for breakpoint inspection by adding to <code>.vscode/launch.json</code>:",
        bullet
    ))
    story.append(Paragraph(
        "{\n"
        "  \"version\": \"0.2.0\",\n"
        "  \"configurations\": [\n"
        "    {\n"
        "      \"name\": \"Debug FastAPI Backend\",\n"
        "      \"type\": \"debugpy\",\n"
        "      \"request\": \"launch\",\n"
        "      \"module\": \"uvicorn\",\n"
        "      \"args\": [\"backend.main:app\", \"--reload\", \"--port\", \"8000\"],\n"
        "      \"jinja\": true\n"
        "    }\n"
        "  ]\n"
        "}",
        code_block
    ))
    story.append(Spacer(1, 2))

    # ==========================================
    # 5. DOCKER COMPOSE 1-COMMAND EXECUTION
    # ==========================================
    story.append(Paragraph("5. Running with Docker Compose (1-Command Full-Stack Boot)", h1))
    story.append(Paragraph(
        "If you have Docker Desktop installed, boot both containers simultaneously without configuring local environments:",
        body
    ))
    story.append(Paragraph(
        "# Build and start all containers in detached mode:<br/>"
        "<font face='Courier' size='7.0'>docker compose up --build -d</font><br/><br/>"
        "# View live logs from both services:<br/>"
        "<font face='Courier' size='7.0'>docker compose logs -f</font><br/><br/>"
        "# Stop and clean up containers:<br/>"
        "<font face='Courier' size='7.0'>docker compose down</font>",
        code_block
    ))
    story.append(Paragraph(
        "• <b>Web Dashboard:</b> <a href='http://localhost:3000'><u>http://localhost:3000</u></a> &nbsp;&nbsp;|&nbsp;&nbsp; "
        "• <b>FastAPI Swagger Docs:</b> <a href='http://127.0.0.1:8000/docs'><u>http://127.0.0.1:8000/docs</u></a>",
        callout
    ))
    story.append(Spacer(1, 2))

    # ==========================================
    # 6. KEY REST API ENDPOINTS
    # ==========================================
    story.append(Paragraph("6. Key REST API Endpoints Overview", h1))
    api_data = [
        [Paragraph("Method &amp; Route", th), Paragraph("Request Body / Params", th), Paragraph("Functionality", th)],
        [
            Paragraph("<font face='Courier' size='6.5'>POST /api/run-simulation</font>", td_code),
            Paragraph("JSON: { num_nodes, rounds, harvesting_profile, enable_time_dp, ... }", td),
            Paragraph("Triggers asynchronous simulation in background task. Returns job ID.", td)
        ],
        [
            Paragraph("<font face='Courier' size='6.5'>GET /api/simulation/{id}</font>", td_code),
            Paragraph("Path param: job_id (UUID)", td),
            Paragraph("Polls live execution status, node topology coordinates, and round telemetry.", td)
        ],
        [
            Paragraph("<font face='Courier' size='6.5'>GET /api/scenarios</font>", td_code),
            Paragraph("None", td),
            Paragraph("Returns pre-configured scenario templates (Baseline, Solar, Shadowed, Stochastic).", td)
        ],
        [
            Paragraph("<font face='Courier' size='6.5'>GET /api/history</font>", td_code),
            Paragraph("Query: limit, offset", td),
            Paragraph("Retrieves paginated past simulation runs stored in SQLite.", td)
        ],
        [
            Paragraph("<font face='Courier' size='6.5'>GET /api/export/{id}/csv</font>", td_code),
            Paragraph("Path param: job_id", td),
            Paragraph("Exports round-by-round energy, alive nodes, and packet metrics as CSV.", td)
        ]
    ]
    t_api = Table(api_data, colWidths=[130, 160, 246])
    t_api.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_th_bg),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.4, c_grid),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_row_alt]),
        ('TOPPADDING', (0, 0), (-1, -1), 2.0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.0),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_api)

    story.append(PageBreak())

    # ==========================================
    # 7. TROUBLESHOOTING & COMMON FIXES
    # ==========================================
    story.append(Paragraph("7. Troubleshooting &amp; Common Issues", h1))
    trouble_data = [
        [Paragraph("Symptom / Error", th), Paragraph("Underlying Cause", th), Paragraph("Resolution", th)],
        [
            Paragraph("<b>npm error Missing script: \"dev\"</b>", td),
            Paragraph("Command was run in <code>C:\\Users\\Santhosh\\frontend</code> (unrelated folder) rather than the project frontend.", td),
            Paragraph("Navigate to <code>cd C:\\Users\\Santhosh\\wsn-energy-routing\\frontend</code> and verify <code>package.json</code> contains <code>\"dev\": \"tsx server.ts\"</code>.", td)
        ],
        [
            Paragraph("<b>ERROR: Could not open requirements file: 'requirements.txt'</b>", td),
            Paragraph("Terminal is inside <code>frontend\\</code> or outside project. <code>requirements.txt</code> is in the project root.", td),
            Paragraph("Run <code>cd C:\\Users\\Santhosh\\wsn-energy-routing</code> before executing <code>pip install -r requirements.txt</code>.", td)
        ],
        [
            Paragraph("<b>ERROR: To modify pip, please run python.exe -m pip...</b>", td),
            Paragraph("Windows file-locking prevents running <code>pip.exe</code> from modifying its own executable in-place.", td),
            Paragraph("Always use the module syntax:<br/><code>python -m pip install --upgrade pip</code>", td)
        ],
        [
            Paragraph("<b>PowerShell execution policy blocks activate.ps1</b>", td),
            Paragraph("Default Windows PowerShell restriction blocks local script execution.", td),
            Paragraph("Execute once in PowerShell:<br/><code>Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass</code>", td)
        ],
        [
            Paragraph("<b>Port 8000 or 3000 already in use</b>", td),
            Paragraph("Previous uvicorn or node server processes are still occupying the ports.", td),
            Paragraph("Run <code>start_offline.bat</code> (auto-cleans ports) or manually:<br/><code>netstat -ano | findstr :8000</code> then <code>taskkill /PID &lt;PID&gt; /F</code>", td)
        ],
        [
            Paragraph("<b>502 Bad Gateway / Network Error in Browser</b>", td),
            Paragraph("Frontend proxy cannot connect to backend because FastAPI is offline.", td),
            Paragraph("Ensure the FastAPI backend is running on port 8000 before opening the frontend in your browser.", td)
        ]
    ]
    t_trouble = Table(trouble_data, colWidths=[130, 160, 246])
    t_trouble.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_th_bg),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.4, c_grid),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_row_alt]),
        ('TOPPADDING', (0, 0), (-1, -1), 2.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.2),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_trouble)
    story.append(Spacer(1, 3))

    # ==========================================
    # 8. QUICK FULL-STACK CHEAT SHEET
    # ==========================================
    story.append(Paragraph("8. Quick Full-Stack Execution Cheat-Sheet", h1))
    story.append(Paragraph(
        "<font face='Courier' size='7.0'>"
        "# -------------------------------------------------------------<br/>"
        "# OPTION A: ONE-CLICK LAUNCH (FASTEST)<br/>"
        "# -------------------------------------------------------------<br/>"
        "cd C:\\Users\\Santhosh\\wsn-energy-routing<br/>"
        ".\\start_offline.bat<br/><br/>"
        "# -------------------------------------------------------------<br/>"
        "# OPTION B: MANUAL TWO-TERMINAL SETUP<br/>"
        "# -------------------------------------------------------------<br/>"
        "# Terminal 1 (FastAPI Backend - Port 8000):<br/>"
        "cd C:\\Users\\Santhosh\\wsn-energy-routing<br/>"
        ".venv\\Scripts\\activate<br/>"
        "python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000<br/><br/>"
        "# Terminal 2 (React Frontend - Port 3000):<br/>"
        "cd C:\\Users\\Santhosh\\wsn-energy-routing\\frontend<br/>"
        "npm run dev<br/><br/>"
        "# Access in Browser:<br/>"
        "# Dashboard: http://localhost:3000  |  API Docs: http://127.0.0.1:8000/docs"
        "</font>",
        code_block
    ))

    canvas_class = make_canvas_class(is_bw)
    doc.build(story, canvasmaker=canvas_class)
    print(f"Successfully generated execution guide PDF at: {output_pdf_path} (B&W mode: {is_bw})")


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'report/wsn_project_execution_guide.pdf'
    bw_flag = False
    if len(sys.argv) > 2 and sys.argv[2].lower() in ['--bw', '-bw', 'bw', 'true']:
        bw_flag = True
    elif "bw" in os.path.basename(out).lower():
        bw_flag = True
    build_pdf_guide(out, is_bw=bw_flag)
