"""
PDF Incident Report Generator
──────────────────────────────
Generates a professional PDF incident report from a ReasoningResult alert dict.
Uses ReportLab for PDF generation.
"""

import os
from datetime import datetime
from pathlib import Path

REPORTS_DIR          = os.getenv("REPORTS_DIR", "./reports")
INSTITUTION_NAME     = os.getenv("INSTITUTION_NAME", "Institution")

# Severity color map (RGB tuples for ReportLab)
_VERDICT_COLORS = {
    "CLEAR":       (0.06, 0.72, 0.51),   # green
    "SUSPICIOUS":  (0.96, 0.62, 0.04),   # orange
    "COMPROMISED": (0.94, 0.27, 0.27),   # red
}


def generate_pdf_report(alert: dict) -> str:
    """
    Generate a PDF incident report and save it to REPORTS_DIR.
    Returns the file path.
    """
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    )

    Path(REPORTS_DIR).mkdir(parents=True, exist_ok=True)

    sid       = alert.get("session_id", "unknown")
    ts        = alert.get("timestamp", datetime.utcnow().isoformat())
    score     = alert.get("integrity_score", 0)
    verdict   = alert.get("verdict", "SUSPICIOUS")
    reasoning = alert.get("reasoning", "No reasoning available.")
    triggered = alert.get("triggered_by", [])

    filename  = f"incident_{sid}_{ts[:10]}.pdf"
    filepath  = os.path.join(REPORTS_DIR, filename)

    doc    = SimpleDocTemplate(filepath, pagesize=A4,
                                leftMargin=20*mm, rightMargin=20*mm,
                                topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "Title", parent=styles["Title"],
        fontSize=20, spaceAfter=4, textColor=colors.HexColor("#0D1B3E")
    )
    heading_style = ParagraphStyle(
        "Heading2", parent=styles["Heading2"],
        fontSize=13, spaceAfter=4, textColor=colors.HexColor("#1A3A6B")
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontSize=11, spaceAfter=6, leading=16
    )

    v_color_rgb  = _VERDICT_COLORS.get(verdict, (0.5, 0.5, 0.5))
    verdict_color = colors.Color(*v_color_rgb)

    # Build document content
    content = []

    # Header
    content.append(Paragraph("ExamGuard AI — Incident Report", title_style))
    content.append(Paragraph(INSTITUTION_NAME, body_style))
    content.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#00C6FF")))
    content.append(Spacer(1, 6*mm))

    # Metadata table
    meta_data = [
        ["Session ID",       sid],
        ["Timestamp (UTC)",  ts],
        ["Report Generated", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")],
    ]
    meta_table = Table(meta_data, colWidths=[55*mm, 120*mm])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EEF3FA")),
        ("FONTNAME",   (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 10),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("PADDING",    (0, 0), (-1, -1), 6),
    ]))
    content.append(meta_table)
    content.append(Spacer(1, 6*mm))

    # Verdict
    content.append(Paragraph("Verdict", heading_style))
    verdict_style = ParagraphStyle(
        "Verdict", parent=styles["Normal"],
        fontSize=22, textColor=verdict_color, fontName="Helvetica-Bold", spaceAfter=4
    )
    content.append(Paragraph(f"{verdict}  —  Integrity Score: {score}/100", verdict_style))
    content.append(Spacer(1, 4*mm))

    # AI Reasoning
    content.append(Paragraph("AI Reasoning", heading_style))
    content.append(Paragraph(reasoning, body_style))
    content.append(Spacer(1, 4*mm))

    # Triggered events
    if triggered:
        content.append(Paragraph("Triggered By", heading_style))
        for evt in triggered:
            content.append(Paragraph(f"• {evt}", body_style))
        content.append(Spacer(1, 4*mm))

    # Footer note
    content.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
    content.append(Spacer(1, 3*mm))
    footer_style = ParagraphStyle(
        "Footer", parent=styles["Normal"],
        fontSize=8, textColor=colors.grey
    )
    content.append(Paragraph(
        "This report was generated autonomously by ExamGuard AI. "
        "All detections are logged with timestamps and confidence scores. "
        "This report should be reviewed by an authorised administrator before any disciplinary action.",
        footer_style,
    ))

    doc.build(content)
    return filepath
