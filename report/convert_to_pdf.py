#!/usr/bin/env python
"""
Simple markdown to PDF converter using reportlab.
"""
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.colors import black, blue, darkgray, lightgrey

def convert_md_to_pdf(md_file, pdf_file):
    """Convert markdown file to PDF with basic formatting."""
    # Read the markdown file
    with open(md_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Create PDF document
    doc = SimpleDocTemplate(pdf_file, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    story = []

    # Get styles
    styles = getSampleStyleSheet()
    # Custom styles
    heading1 = ParagraphStyle(
        'Heading1',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=12,
        textColor=darkgray,
        alignment=TA_LEFT
    )
    heading2 = ParagraphStyle(
        'Heading2',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=10,
        textColor=darkgray,
        alignment=TA_LEFT
    )
    heading3 = ParagraphStyle(
        'Heading3',
        parent=styles['Heading3'],
        fontSize=14,
        spaceAfter=8,
        textColor=darkgray,
        alignment=TA_LEFT
    )
    normal = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        alignment=TA_LEFT
    )
    # Code style: monospaced, smaller font, light gray background
    code = ParagraphStyle(
        'Code',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Courier',
        leftIndent=12,
        spaceAfter=6,
        backColor=lightgrey,
        borderColor=black,
        borderWidth=0.5,
        borderPadding=3
    )

    # Process lines
    in_code_block = False
    code_lines = []

    for line in lines:
        line = line.rstrip('\n')
        # Handle code blocks
        if line.startswith('```'):
            if in_code_block:
                # End code block
                code_content = '\n'.join(code_lines)
                p = Paragraph(code_content, code)
                story.append(p)
                story.append(Spacer(1, 6))
                code_lines = []
                in_code_block = False
            else:
                # Start code block
                in_code_block = True
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        # Handle headings
        if line.startswith('# '):
            text = line[2:]
            p = Paragraph(text, heading1)
            story.append(p)
            story.append(Spacer(1, 12))
        elif line.startswith('## '):
            text = line[3:]
            p = Paragraph(text, heading2)
            story.append(p)
            story.append(Spacer(1, 10))
        elif line.startswith('### '):
            text = line[4:]
            p = Paragraph(text, heading3)
            story.append(p)
            story.append(Spacer(1, 8))
        elif line.startswith('#### '):
            text = line[5:]
            p = Paragraph(text, styles['Heading4'])
            story.append(p)
            story.append(Spacer(1, 6))
        elif line.startswith('##### ') or line.startswith('###### '):
            text = line[6:]  # approximate
            p = Paragraph(text, styles['Heading5'])
            story.append(p)
            story.append(Spacer(1, 6))
        # Handle bold and italic (simple)
        else:
            # Convert **bold** and *italic*
            text = line
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
            # Handle horizontal rule
            if re.match(r'^\\s*[-*_]{3,}\\s*$', line):
                story.append(Spacer(1, 12))
                continue
            # Handle empty lines
            if not line.strip():
                story.append(Spacer(1, 6))
                continue
            p = Paragraph(text, normal)
            story.append(p)

    # Build PDF
    doc.build(story)
    print(f"PDF generated: {pdf_file}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python convert_to_pdf.py <input.md> <output.pdf>")
        sys.exit(1)
    convert_md_to_pdf(sys.argv[1], sys.argv[2])