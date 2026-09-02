"""
Utility script to convert markdown review reports into clean PDF documents using ReportLab.
"""

import sys
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def md_to_pdf(input_md_path: str, output_pdf_path: str):
    if not os.path.exists(input_md_path):
        print(f"Error: {input_md_path} does not exist.")
        return

    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()
    normal = styles['Normal']
    normal.fontSize = 9.5
    normal.leading = 13

    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1a365d'),
        spaceAfter=10
    )

    h2_style = ParagraphStyle(
        'H2Style',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#2b6cb0'),
        spaceBefore=12,
        spaceAfter=6
    )

    h3_style = ParagraphStyle(
        'H3Style',
        parent=styles['Heading3'],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#2d3748'),
        spaceBefore=8,
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=normal,
        fontName='Courier',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#2c5282'),
        backColor=colors.HexColor('#edf2f7'),
        borderPadding=4
    )

    story = []

    with open(input_md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    in_code_block = False
    code_lines = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith('```'):
            if in_code_block:
                code_text = "<br/>".join(code_lines).replace(" ", "&nbsp;")
                story.append(Paragraph(code_text, code_style))
                story.append(Spacer(1, 6))
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_lines.append(stripped.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
            continue

        if not stripped:
            story.append(Spacer(1, 4))
            continue

        if stripped.startswith('# '):
            story.append(Paragraph(stripped[2:], title_style))
        elif stripped.startswith('## '):
            story.append(Paragraph(stripped[3:], h2_style))
        elif stripped.startswith('### '):
            story.append(Paragraph(stripped[4:], h3_style))
        elif stripped.startswith('---'):
            story.append(Spacer(1, 6))
        elif stripped.startswith('- ') or stripped.startswith('* '):
            story.append(Paragraph(f"• {stripped[2:]}", normal))
        else:
            story.append(Paragraph(stripped, normal))

    doc.build(story)
    print(f"PDF successfully generated: {output_pdf_path}")


if __name__ == '__main__':
    src = sys.argv[1] if len(sys.argv) > 1 else 'report/first_review_report.md'
    dst = sys.argv[2] if len(sys.argv) > 2 else 'report/first_review_report.pdf'
    md_to_pdf(src, dst)
