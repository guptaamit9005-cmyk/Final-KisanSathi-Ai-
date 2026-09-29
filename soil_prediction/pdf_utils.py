from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)


GREEN = colors.HexColor("#176B3A")
DARK_GREEN = colors.HexColor("#104D2B")
LIGHT_GREEN = colors.HexColor("#EAF6EE")
LIGHT_GREY = colors.HexColor("#F4F7F5")
TEXT = colors.HexColor("#24332A")
MUTED = colors.HexColor("#65736A")
BORDER = colors.HexColor("#DCE7DF")


def safe_text(value):
    """Escape user-provided text before placing it in a ReportLab Paragraph."""
    if value is None or value == "":
        return "Not provided"
    return escape(str(value))


def draw_page(canvas, doc):
    """Add a consistent header and footer to every PDF page."""
    canvas.saveState()

    page_width, page_height = A4

    canvas.setFillColor(DARK_GREEN)
    canvas.rect(0, page_height - 16 * mm, page_width, 16 * mm, fill=1, stroke=0)

    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(18 * mm, page_height - 10 * mm, "KisanSathi AI | Soil Intelligence")

    canvas.setStrokeColor(BORDER)
    canvas.line(18 * mm, 15 * mm, page_width - 18 * mm, 15 * mm)

    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(18 * mm, 10 * mm, "Informational soil screening report")
    canvas.drawRightString(page_width - 18 * mm, 10 * mm, f"Page {doc.page}")

    canvas.restoreState()


def build_soil_pdf(analysis):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=24 * mm,
        bottomMargin=22 * mm,
        title=f"KisanSathi Soil Report {analysis.id}",
        author="KisanSathi AI",
    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=21,
        leading=26,
        textColor=DARK_GREEN,
        alignment=TA_LEFT,
        spaceAfter=5,
    ))

    styles.add(ParagraphStyle(
        name="SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=GREEN,
        spaceBefore=12,
        spaceAfter=7,
    ))

    styles.add(ParagraphStyle(
        name="BodySmall",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=14,
        textColor=TEXT,
    ))

    styles.add(ParagraphStyle(
        name="Disclaimer",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=MUTED,
    ))

    story = []

    story.append(Paragraph("Soil Analysis Report", styles["ReportTitle"]))
    story.append(Paragraph(
        "A structured record of the soil and environmental values entered into KisanSathi AI.",
        styles["BodySmall"],
    ))
    story.append(Spacer(1, 8))

    farm_data = [
        ["Report ID", f"KS-SOIL-{analysis.id:06d}"],
        ["Farm name", safe_text(analysis.farm_name)],
        ["Location", safe_text(analysis.location)],
        ["Planned crop", safe_text(analysis.target_crop)],
        ["Report created", analysis.created_at.strftime("%d %B %Y, %I:%M %p")],
    ]

    farm_table = Table(farm_data, colWidths=[42 * mm, 125 * mm])
    farm_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_GREEN),
        ("TEXTCOLOR", (0, 0), (0, -1), DARK_GREEN),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
    ]))
    story.append(farm_table)

    story.append(Paragraph("Recorded Soil & Environment Values", styles["SectionHeading"]))

    value_rows = [
        ["Parameter", "Recorded value"],
        ["Nitrogen (N)", str(analysis.nitrogen)],
        ["Phosphorus (P)", str(analysis.phosphorus)],
        ["Potassium (K)", str(analysis.potassium)],
        ["Soil pH", str(analysis.ph)],
        ["Temperature", f"{analysis.temperature} °C"],
        ["Humidity", f"{analysis.humidity} %"],
        ["Rainfall", f"{analysis.rainfall} mm"],
        ["Organic carbon", safe_text(analysis.organic_carbon)],
        ["Electrical conductivity", safe_text(analysis.electrical_conductivity)],
        ["Soil texture", safe_text(analysis.get_soil_texture_display())],
    ]

    values_table = Table(value_rows, colWidths=[85 * mm, 82 * mm], repeatRows=1)
    values_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GREEN),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GREY]),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
    ]))
    story.append(values_table)

    report = analysis.report or {}

    story.append(Paragraph("Soil pH Screening", styles["SectionHeading"]))
    story.append(Paragraph(
        f"<b>{safe_text(report.get('ph_status'))}</b><br/>"
        f"{safe_text(report.get('ph_message'))}",
        styles["BodySmall"],
    ))

    story.append(Paragraph("Suggested Follow-up Actions", styles["SectionHeading"]))

    recommendations = report.get("recommendations", [])
    if recommendations:
        for index, recommendation in enumerate(recommendations, start=1):
            story.append(Paragraph(
                f"{index}. {safe_text(recommendation)}",
                styles["BodySmall"],
            ))
            story.append(Spacer(1, 4))
    else:
        story.append(Paragraph(
            "No follow-up actions were recorded.",
            styles["BodySmall"],
        ))

    story.append(Paragraph("Important Advisory", styles["SectionHeading"]))
    story.append(Paragraph(
        safe_text(report.get(
            "disclaimer",
            "This report is informational and is not a laboratory diagnosis or fertilizer prescription."
        )),
        styles["Disclaimer"],
    ))

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "For crop-specific interpretation and fertilizer planning, consult a qualified "
        "soil-testing laboratory or local agriculture officer.",
        styles["Disclaimer"],
    ))

    doc.build(
        story,
        onFirstPage=draw_page,
        onLaterPages=draw_page,
    )

    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes