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
            self.drawString(38, 758, "WSN Energy-Harvesting Routing Simulator — Full-Stack Execution Guide")
            self.drawRightString(574, 758, "GitHub: santhoshvellore7119-web/WSN_proj")
            self.setStrokeColor(colors.HexColor('#CBD5E1'))
            self.setLineWidth(0.5)
            self.line(38, 750, 574, 750)
        
        # Footer on all pages
        self.drawString(38, 26, "Full-Stack Deployment Manual • FastAPI (Port 8000) + React (Port 3000)")
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
        topMargin=40,
        bottomMargin=44
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=17,
        leading=21,
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
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=7,
        spaceAfter=3.5,
        keepWithNext=True
    )

    h2 = ParagraphStyle(
        'H2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=8.8,
        leading=11.5,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=5,
        spaceAfter=2,
        keepWithNext=True
    )

    body = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.8,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=2.5
    )

    bullet = ParagraphStyle(
        'Bullet',
        parent=body,
        leftIndent=9,
        firstLineIndent=-6,
        spaceAfter=2
    )

    code_block = ParagraphStyle(
        'CodeBlock',
        parent=body,
        fontName='Courier',
        fontSize=7.2,
        leading=9.2,
        textColor=colors.HexColor('#0F172A'),
        backColor=colors.HexColor('#F8FAFC'),
        borderColor=colors.HexColor('#E2E8F0'),
        borderWidth=0.6,
        borderPadding=4,
        spaceBefore=1.5,
        spaceAfter=3.5
    )

    callout = ParagraphStyle(
        'Callout',
        parent=body,
        fontName='Helvetica-Oblique',
        fontSize=7.8,
        leading=10.2,
        textColor=colors.HexColor('#1E40AF'),
        backColor=colors.HexColor('#EFF6FF'),
        borderColor=colors.HexColor('#BFDBFE'),
        borderWidth=0.6,
        borderPadding=3.5,
        spaceAfter=3.5
    )

    th = ParagraphStyle(
        'TH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.6,
        leading=9.5,
        textColor=colors.white
    )

    td = ParagraphStyle(
        'TD',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=9,
        textColor=colors.HexColor('#1E293B')
    )

    td_code = ParagraphStyle(
        'TDCode',
        parent=td,
        fontName='Courier',
        fontSize=6.6,
        leading=8.2,
        textColor=colors.HexColor('#0969DA')
    )

    story = []

    # ==========================================
    # HEADER & GITHUB LINK BANNER
    # ==========================================
    story.append(Paragraph("WSN Energy-Harvesting Routing Simulator", title_style))
    story.append(Paragraph("Full-Stack Web Application Execution &amp; Setup Guide (FastAPI Backend + React Frontend)", sub_style))
    
    # Prominent Top GitHub Banner
    gh_html = (
        f"<b>GitHub Repository:</b> <a href='{GITHUB_REPO_URL}'><u>{GITHUB_REPO_URL}</u></a> &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<b>Branch:</b> <code>master</code> &nbsp;&nbsp;|&nbsp;&nbsp; <b>Author:</b> Santhosh"
    )
    story.append(Paragraph(gh_html, github_banner))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor('#2563EB'), spaceAfter=5))

    # ==========================================
    # 1. FULL-STACK ARCHITECTURE OVERVIEW
    # ==========================================
    story.append(Paragraph("1. Full-Stack System Architecture Overview", h1))
    story.append(Paragraph(
        "The project consists of a complete full-stack web application integrating an asynchronous Python FastAPI backend "
        "with an interactive React 19 single-page dashboard. The frontend visualizes node topology, live multi-hop routing paths, "
        "and round-by-round energy harvesting telemetry in real time.",
        body
    ))

    arch_data = [
        [Paragraph("Layer", th), Paragraph("Tech Stack &amp; Port", th), Paragraph("Role &amp; Responsibilities", th)],
        [
            Paragraph("<b>Frontend UI</b>", td),
            Paragraph("React 19, TypeScript, Vite, Tailwind CSS, Recharts<br/><b>Port 3000</b>", td),
            Paragraph("Interactive single-page application. Features real-time SVG sensor topology canvas, round-by-round replay controls, and dynamic residual energy line charts.", td)
        ],
        [
            Paragraph("<b>Backend API</b>", td),
            Paragraph("FastAPI, Uvicorn, SQLite, SQLAlchemy, Pydantic<br/><b>Port 8000</b>", td),
            Paragraph("Asynchronous REST API. Manages background simulation jobs, SQLite database persistence (<code>backend/wsn_simulator.db</code>), and provides OpenAPI / Swagger documentation.", td)
        ],
        [
            Paragraph("<b>Simulation Engine</b>", td),
            Paragraph("Python 3.10+, NumPy, SciPy<br/>(Core Library in <code>src/</code>)", td),
            Paragraph("Executes 3D Time-Augmented DP ($dp[v][h][t]$), DSU live detour recovery, LEACH clustering, 1st-order radio model, and solar harvesting profiles.", td)
        ]
    ]
    t_arch = Table(arch_data, colWidths=[80, 160, 296])
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
    story.append(Spacer(1, 3))

    # ==========================================
    # 2. PREREQUISITES & INITIAL SETUP
    # ==========================================
    story.append(Paragraph("2. Prerequisites &amp; One-Time Initial Setup", h1))
    story.append(Paragraph(
        "Ensure the following tools are installed on your machine before running: "
        "<b>Python 3.10+</b> (with pip), <b>Node.js 18+</b> (with npm), and <b>Git</b>.",
        body
    ))
    story.append(Paragraph(
        "<b>Step 1: Clone the Repository</b><br/>"
        "<font face='Courier' size='7.2'>git clone https://github.com/santhoshvellore7119-web/WSN_proj.git<br/>cd WSN_proj</font>",
        code_block
    ))
    story.append(Paragraph(
        "<b>Step 2: Setup Python Virtual Environment &amp; Install Backend Dependencies</b><br/>"
        "• <u>Windows (CMD / PowerShell):</u><br/>"
        "<font face='Courier' size='7.2'>python -m venv .venv<br/>.venv\\Scripts\\activate<br/>pip install --upgrade pip<br/>pip install -r requirements.txt</font><br/>"
        "• <u>Linux / macOS:</u><br/>"
        "<font face='Courier' size='7.2'>python3 -m venv .venv<br/>source .venv/bin/activate<br/>pip install --upgrade pip<br/>pip install -r requirements.txt</font>",
        code_block
    ))
    story.append(Paragraph(
        "<b>Step 3: Install Frontend Node Dependencies</b><br/>"
        "<font face='Courier' size='7.2'>cd frontend<br/>npm install<br/>cd ..</font>",
        code_block
    ))
    story.append(Spacer(1, 3))

    # ==========================================
    # 3. HOW TO RUN IN CMD / POWERSHELL
    # ==========================================
    story.append(Paragraph("3. How to Run the Full-Stack Application in Command Prompt / Terminal", h1))
    story.append(Paragraph(
        "To run both the backend API and frontend UI concurrently, open <b>two separate terminal windows</b> from the project root:",
        body
    ))
    story.append(Paragraph(
        "<b>Terminal 1: Start the FastAPI Backend (Port 8000)</b><br/>"
        "• Activate virtual environment and launch Uvicorn with auto-reload:<br/>"
        "<font face='Courier' size='7.2'>"
        "# Windows CMD / PowerShell:<br/>"
        ".venv\\Scripts\\activate<br/>"
        "python -m uvicorn backend.main:app --reload --port 8000<br/><br/>"
        "# Or navigate into backend folder:<br/>"
        "cd backend<br/>"
        "python -m uvicorn main:app --reload --port 8000"
        "</font><br/>"
        "• <i>Backend will be live at:</i> <b>http://localhost:8000</b><br/>"
        "• <i>Interactive API Documentation (Swagger UI):</i> <b>http://localhost:8000/docs</b>",
        code_block
    ))
    story.append(Paragraph(
        "<b>Terminal 2: Start the React Frontend (Port 3000)</b><br/>"
        "• Navigate into the frontend folder and start the dev server:<br/>"
        "<font face='Courier' size='7.2'>"
        "cd frontend<br/>"
        "npm run dev"
        "</font><br/>"
        "• <i>Frontend Web Dashboard will be live at:</i> <b>http://localhost:3000</b><br/>"
        "• <i>Automatic API Proxying:</i> <code>frontend/server.ts</code> automatically forwards all <code>/api/*</code> requests to <code>http://127.0.0.1:8000</code>.",
        code_block
    ))

    story.append(PageBreak())

    # ==========================================
    # 4. HOW TO RUN IN VS CODE
    # ==========================================
    story.append(Paragraph("4. Step-by-Step Procedure to Run in Visual Studio Code (VS Code)", h1))
    story.append(Paragraph(
        "Follow these steps for a clean, integrated development experience inside VS Code:",
        body
    ))
    story.append(Paragraph(
        "<b>Step 1: Open Project in VS Code</b><br/>"
        "Launch VS Code in the project root: <font face='Courier' size='7.2'>code .</font>",
        bullet
    ))
    story.append(Paragraph(
        "<b>Step 2: Select Python Interpreter</b><br/>"
        "1. Press <code>Ctrl + Shift + P</code> (or <code>Cmd + Shift + P</code> on macOS).<br/>"
        "2. Type and select <b>Python: Select Interpreter</b>.<br/>"
        "3. Choose the workspace virtual environment interpreter: <code>.\\.venv\\Scripts\\python.exe</code> (or <code>./.venv/bin/python</code>).",
        bullet
    ))
    story.append(Paragraph(
        "<b>Step 3: Open Integrated Split Terminals</b><br/>"
        "1. Open the integrated terminal with <code>Ctrl + `</code> (backtick).<br/>"
        "2. Click the <b>Split Terminal</b> button on the top right of the terminal panel (or press <code>Ctrl + \\</code>).<br/>"
        "3. In the <b>Left Pane (Backend)</b>, run:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<font face='Courier' size='7.2'>cd backend &amp;&amp; python -m uvicorn main:app --reload --port 8000</font><br/>"
        "4. In the <b>Right Pane (Frontend)</b>, run:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<font face='Courier' size='7.2'>cd frontend &amp;&amp; npm run dev</font>",
        bullet
    ))
    story.append(Paragraph(
        "<b>Step 4: Optional 1-Click Debugging via .vscode/launch.json</b><br/>"
        "You can configure VS Code debugger to launch FastAPI with breakpoint support by adding to <code>.vscode/launch.json</code>:",
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
    story.append(Spacer(1, 3))

    # ==========================================
    # 5. DOCKER COMPOSE 1-COMMAND EXECUTION
    # ==========================================
    story.append(Paragraph("5. Running with Docker Compose (1-Command Full-Stack Boot)", h1))
    story.append(Paragraph(
        "If you have Docker Desktop installed, you can boot both the FastAPI backend and React frontend simultaneously without configuring local environments:",
        body
    ))
    story.append(Paragraph(
        "# Build and start all containers in detached mode:<br/>"
        "<font face='Courier' size='7.2'>docker compose up --build -d</font><br/><br/>"
        "# View live logs from both services:<br/>"
        "<font face='Courier' size='7.2'>docker compose logs -f</font><br/><br/>"
        "# Stop and clean up containers:<br/>"
        "<font face='Courier' size='7.2'>docker compose down</font>",
        code_block
    ))
    story.append(Paragraph(
        "• <b>Web Dashboard:</b> <a href='http://localhost:3000'><u>http://localhost:3000</u></a> &nbsp;&nbsp;|&nbsp;&nbsp; "
        "• <b>FastAPI Swagger Docs:</b> <a href='http://localhost:8000/docs'><u>http://localhost:8000/docs</u></a>",
        callout
    ))
    story.append(Spacer(1, 3))

    # ==========================================
    # 6. KEY REST API ENDPOINTS
    # ==========================================
    story.append(Paragraph("6. Key REST API Endpoints Overview", h1))
    api_data = [
        [Paragraph("Method &amp; Route", th), Paragraph("Request Body / Params", th), Paragraph("Functionality", th)],
        [
            Paragraph("<font face='Courier' size='6.6'>POST /api/run-simulation</font>", td_code),
            Paragraph("JSON: { num_nodes, rounds, harvesting_profile, enable_time_dp, ... }", td),
            Paragraph("Triggers asynchronous simulation in background task. Returns job ID.", td)
        ],
        [
            Paragraph("<font face='Courier' size='6.6'>GET /api/simulation/{id}</font>", td_code),
            Paragraph("Path param: job_id (UUID)", td),
            Paragraph("Polls live execution status, node topology coordinates, and round telemetry.", td)
        ],
        [
            Paragraph("<font face='Courier' size='6.6'>GET /api/scenarios</font>", td_code),
            Paragraph("None", td),
            Paragraph("Returns pre-configured scenario templates (Baseline, Solar, Shadowed, Stochastic).", td)
        ],
        [
            Paragraph("<font face='Courier' size='6.6'>GET /api/history</font>", td_code),
            Paragraph("Query: limit, offset", td),
            Paragraph("Retrieves paginated past simulation runs stored in SQLite.", td)
        ],
        [
            Paragraph("<font face='Courier' size='6.6'>GET /api/export/{id}/csv</font>", td_code),
            Paragraph("Path param: job_id", td),
            Paragraph("Exports round-by-round energy, alive nodes, and packet metrics as CSV.", td)
        ]
    ]
    t_api = Table(api_data, colWidths=[130, 160, 246])
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
    story.append(Spacer(1, 3))

    # ==========================================
    # 7. TROUBLESHOOTING & COMMON FIXES
    # ==========================================
    story.append(Paragraph("7. Troubleshooting &amp; Common Fixes", h1))
    trouble_data = [
        [Paragraph("Symptom / Error", th), Paragraph("Cause", th), Paragraph("Fix", th)],
        [
            Paragraph("<b>PowerShell script execution disabled</b>", td),
            Paragraph("Windows policy blocks <code>activate.ps1</code>.", td),
            Paragraph("Run in PowerShell:<br/><code>Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass</code>", td)
        ],
        [
            Paragraph("<b>Port 8000 or 3000 already in use</b>", td),
            Paragraph("Previous server process is still running.", td),
            Paragraph("Windows: <code>netstat -ano | findstr :8000</code> then <code>taskkill /PID &lt;PID&gt; /F</code>", td)
        ],
        [
            Paragraph("<b>502 Bad Gateway / Backend unavailable</b>", td),
            Paragraph("Frontend proxy cannot connect to port 8000.", td),
            Paragraph("Ensure FastAPI backend is running in Terminal 1 before opening the frontend in Terminal 2.", td)
        ]
    ]
    t_trouble = Table(trouble_data, colWidths=[150, 150, 236])
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
    story.append(Spacer(1, 3))

    # ==========================================
    # 8. QUICK FULL-STACK CHEAT SHEET
    # ==========================================
    story.append(Paragraph("8. Quick Full-Stack Execution Cheat-Sheet", h1))
    story.append(Paragraph(
        "<font face='Courier' size='7.2'>"
        "# 1. Clone &amp; Setup<br/>"
        "git clone https://github.com/santhoshvellore7119-web/WSN_proj.git &amp;&amp; cd WSN_proj<br/>"
        "python -m venv .venv &amp;&amp; .venv\\Scripts\\activate &amp;&amp; pip install -r requirements.txt<br/>"
        "cd frontend &amp;&amp; npm install &amp;&amp; cd ..<br/><br/>"
        "# 2. Start Backend (Terminal 1)<br/>"
        "python -m uvicorn backend.main:app --reload --port 8000<br/><br/>"
        "# 3. Start Frontend (Terminal 2)<br/>"
        "cd frontend &amp;&amp; npm run dev<br/><br/>"
        "# 4. Open in Browser<br/>"
        "http://localhost:3000 (React App) | http://localhost:8000/docs (Swagger API)"
        "</font>",
        code_block
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated full-stack execution guide PDF at: {output_pdf_path}")


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'report/wsn_project_execution_guide.pdf'
    build_pdf_guide(out)
