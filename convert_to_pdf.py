#!/usr/bin/env python
"""
Convert PROJECT_DOCUMENTATION.md to PDF using reportlab
Lightweight alternative
"""

import os
import sys

def markdown_to_pdf():
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib import colors
    except ImportError:
        print("Installing reportlab...")
        os.system("pip install reportlab -q")
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib import colors
    
    md_file = "PROJECT_DOCUMENTATION.md"
    pdf_file = "PROJECT_DOCUMENTATION.pdf"
    
    if not os.path.exists(md_file):
        print(f"Error: {md_file} not found!")
        sys.exit(1)
    
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        doc = SimpleDocTemplate(
            pdf_file,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
            title="Bitcoin Price Prediction Documentation"
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#f7931a'),
            spaceAfter=20,
            alignment=1
        )
        
        h1_style = ParagraphStyle(
            'H1',
            parent=styles['Heading1'],
            fontSize=14,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=10,
            spaceBefore=8
        )
        
        h2_style = ParagraphStyle(
            'H2',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#2c2c2c'),
            spaceAfter=8,
            spaceBefore=8
        )
        
        body_style = ParagraphStyle(
            'Body',
            parent=styles['BodyText'],
            fontSize=10,
            leading=13,
            alignment=4
        )
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            if not stripped:
                elements.append(Spacer(1, 0.05*inch))
                continue
            
            if stripped.startswith('# '):
                text = stripped.replace('# ', '')
                elements.append(Paragraph(text, title_style))
            elif stripped.startswith('## '):
                text = stripped.replace('## ', '')
                elements.append(Paragraph(text, h1_style))
            elif stripped.startswith('### '):
                text = stripped.replace('### ', '')
                elements.append(Paragraph(text, h2_style))
            elif stripped.startswith('```'):
                continue
            elif stripped == '---':
                elements.append(Spacer(1, 0.2*inch))
            else:
                elements.append(Paragraph(stripped, body_style))
        
        doc.build(elements)
        
        file_size = os.path.getsize(pdf_file) / 1024
        print(f"✅ PDF created successfully!")
        print(f"📄 File: PROJECT_DOCUMENTATION.pdf")
        print(f"📊 Size: {file_size:.1f} KB")
        print(f"📍 Location: {os.path.abspath(pdf_file)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    markdown_to_pdf()
