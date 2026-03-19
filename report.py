"""
report.py
---------
Generates a PDF report for a completed analysis and maintains a JSON history log.

PDF layout
----------
  Header   : title + timestamp
  Summary  : risk score, risk level, colour-coded badge
  Score Breakdown : table with ML / keyword / URL / blacklist sub-scores
  Headers  : parsed email headers
  URLs     : list of URLs found
  Findings : bullet list of flagged issues
  Footer   : page number

History log
-----------
  Appends each result as a JSON line to reports/history.json
"""

import os
import json
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# Output directory
REPORTS_DIR  = os.path.join(os.path.dirname(__file__), "reports")
HISTORY_FILE = os.path.join(REPORTS_DIR, "history.json")

# Risk-level colour map
RISK_COLORS = {
    "Low":      colors.HexColor("#2ea043"),
    "Medium":   colors.HexColor("#d29922"),
    "High":     colors.HexColor("#d1712a"),
    "Critical": colors.HexColor("#da3633"),
}


# ── Public API ────────────────────────────────────────────────────────────────

def generate_pdf(result, output_path=None):
    """
    Build a PDF report from the analysis result dict.
    Returns the path to the saved PDF file.
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)

    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(REPORTS_DIR, f"report_{timestamp}.pdf")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm,  bottomMargin=2*cm,
    )

    story = _build_story(result)
    doc.build(story, onFirstPage=_add_footer, onLaterPages=_add_footer)
    return output_path


def log_to_history(result):
    """Append a slim summary of the result to the JSON history log."""
    os.makedirs(REPORTS_DIR, exist_ok=True)

    entry = {
        "timestamp":       datetime.now().isoformat(),
        "score":           result.get("score"),
        "risk_level":      result.get("risk_level"),
        "ml_confidence":   round(result.get("ml_confidence", 0) * 100, 1),
        "keyword_score":   result.get("keyword_score"),
        "url_score":       result.get("url_score"),
        "blacklist_score": result.get("blacklist_score"),
        "urls_found":      result.get("urls_found", []),
        "findings":        result.get("findings", []),
        "headers":         result.get("headers", {}),
    }

    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    return HISTORY_FILE


# ── PDF construction helpers ─────────────────────────────────────────────────

def _build_story(result):
    styles = getSampleStyleSheet()
    risk   = result.get("risk_level", "Low")
    score  = result.get("score", 0)
    risk_color = RISK_COLORS.get(risk, colors.grey)

    # Custom styles
    title_style = ParagraphStyle("title", parent=styles["Title"],
                                 fontSize=20, spaceAfter=4, alignment=TA_CENTER)
    sub_style   = ParagraphStyle("sub",   parent=styles["Normal"],
                                 fontSize=9, textColor=colors.HexColor("#8b949e"),
                                 alignment=TA_CENTER, spaceAfter=16)
    h2_style    = ParagraphStyle("h2",    parent=styles["Heading2"],
                                 fontSize=12, spaceBefore=14, spaceAfter=6)
    body_style  = ParagraphStyle("body",  parent=styles["Normal"], fontSize=10)
    bullet_style = ParagraphStyle("bullet", parent=styles["Normal"],
                                  fontSize=10, leftIndent=12, spaceAfter=3)

    story = []

    # ── Title ────────────────────────────────────────────────────────────────
    story.append(Paragraph("Phishing Email Analysis Report", title_style))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}",
        sub_style
    ))
    story.append(HRFlowable(width="100%", thickness=1,
                             color=colors.HexColor("#30363d")))
    story.append(Spacer(1, 0.4*cm))

    # ── Risk summary badge ────────────────────────────────────────────────────
    badge_data = [[
        Paragraph(f"<b>Risk Score</b>", body_style),
        Paragraph(f"<b>{score} / 100</b>", body_style),
        Paragraph(f"<b>{risk}</b>",
                  ParagraphStyle("badge", parent=styles["Normal"],
                                 fontSize=11, textColor=risk_color,
                                 alignment=TA_CENTER)),
    ]]
    badge_table = Table(badge_data, colWidths=[5*cm, 5*cm, 5*cm])
    badge_table.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), colors.HexColor("#161b22")),
        ("TEXTCOLOR",   (0, 0), (-1, -1), colors.HexColor("#e6edf3")),
        ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.HexColor("#161b22")]),
        ("BOX",         (0, 0), (-1, -1), 1, colors.HexColor("#30363d")),
        ("INNERGRID",   (0, 0), (-1, -1), 0.5, colors.HexColor("#30363d")),
        ("TOPPADDING",  (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 10),
    ]))
    story.append(badge_table)
    story.append(Spacer(1, 0.4*cm))

    # ── Score breakdown ───────────────────────────────────────────────────────
    story.append(Paragraph("Score Breakdown", h2_style))

    ml_pct  = round(result.get("ml_confidence", 0) * 100, 1)
    breakdown_data = [
        ["Component",          "Raw Score", "Weight", "Contribution"],
        ["ML Classifier",      f"{ml_pct}%",                  "40%", f"{ml_pct*0.40:.1f}"],
        ["Keyword Analysis",   f"{result.get('keyword_score',0):.0f}",  "25%",
         f"{result.get('keyword_score',0)*0.25:.1f}"],
        ["URL Analysis",       f"{result.get('url_score',0):.0f}",      "20%",
         f"{result.get('url_score',0)*0.20:.1f}"],
        ["Blacklist Check",    f"{result.get('blacklist_score',0):.0f}", "15%",
         f"{result.get('blacklist_score',0)*0.15:.1f}"],
        ["", "", "Total", f"{score}"],
    ]
    bd_table = Table(breakdown_data, colWidths=[5*cm, 3.5*cm, 2.5*cm, 4*cm])
    bd_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), colors.HexColor("#21262d")),
        ("TEXTCOLOR",    (0, 0), (-1, 0), colors.HexColor("#58a6ff")),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND",   (0, 1), (-1, -1), colors.HexColor("#0d1117")),
        ("TEXTCOLOR",    (0, 1), (-1, -1), colors.HexColor("#e6edf3")),
        ("BOX",          (0, 0), (-1, -1), 1, colors.HexColor("#30363d")),
        ("INNERGRID",    (0, 0), (-1, -1), 0.5, colors.HexColor("#30363d")),
        ("ALIGN",        (1, 0), (-1, -1), "CENTER"),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
        ("FONTNAME",     (-1, -1), (-1, -1), "Helvetica-Bold"),
        ("TEXTCOLOR",    (-1, -1), (-1, -1), risk_color),
    ]))
    story.append(bd_table)
    story.append(Spacer(1, 0.3*cm))

    # ── Email headers ─────────────────────────────────────────────────────────
    headers = result.get("headers", {})
    if headers:
        story.append(Paragraph("Email Headers", h2_style))
        for key, val in headers.items():
            story.append(Paragraph(
                f"<b>{key}:</b> {_safe(val)}", bullet_style
            ))
        story.append(Spacer(1, 0.2*cm))

    # ── URLs found ────────────────────────────────────────────────────────────
    urls = result.get("urls_found", [])
    story.append(Paragraph(f"URLs Found ({len(urls)})", h2_style))
    if urls:
        for url in urls:
            story.append(Paragraph(f"• {_safe(url)}", bullet_style))
    else:
        story.append(Paragraph("No URLs detected.", body_style))
    story.append(Spacer(1, 0.2*cm))

    # ── Findings ──────────────────────────────────────────────────────────────
    story.append(Paragraph("Findings", h2_style))
    for finding in result.get("findings", []):
        story.append(Paragraph(f"• {_safe(finding)}", bullet_style))

    return story


def _safe(text):
    """Escape characters that break ReportLab paragraph XML."""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _add_footer(canvas, doc):
    """Draw page number at the bottom of each page."""
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#8b949e"))
    canvas.drawCentredString(
        A4[0] / 2, 1.2*cm,
        f"Phishing Email Analyzer — Page {doc.page}"
    )
    canvas.restoreState()
