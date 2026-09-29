from io import BytesIO
from xml.sax.saxutils import escape

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as PDFImage,
)

from .models import CropAnalysis
from .forms import CropImageForm, ExpertReviewForm
from .ai_model import predict_disease


# ============================================================
# 1. DISEASE SYMPTOMS REFERENCE DATABASE
# ============================================================

DISEASE_SYMPTOMS = {
    "brown spot": {
        "visual_signs": [
            "Small brown or dark-brown spots may appear on leaves.",
            "Spots may increase in size as symptoms progress.",
            "Affected leaf tissue may become dry or necrotic.",
            "Severely affected leaves may show extensive discoloration.",
        ],
        "early_symptoms": (
            "Small brown spots may appear on leaf surfaces. "
            "Monitor whether spots increase in number or size."
        ),
        "severity_indicators": (
            "Increasing numbers of lesions, larger affected areas, "
            "and drying leaf tissue may indicate worsening symptoms."
        ),
    },

    "bacterial leaf blight": {
        "visual_signs": [
            "Water-soaked or pale-yellow areas may appear near leaf tips or margins.",
            "Yellowing may extend along the leaf.",
            "Affected tissue may become straw-colored.",
            "Leaves may dry from the tip or edge.",
        ],
        "early_symptoms": (
            "Water-soaked or yellowish leaf areas may appear, often near "
            "the leaf tip or margin."
        ),
        "severity_indicators": (
            "Long yellow-to-straw-colored lesions and extensive leaf drying "
            "may indicate more severe symptoms."
        ),
    },

    "leaf blast": {
        "visual_signs": [
            "Spindle-shaped or diamond-shaped lesions may develop.",
            "Lesions may have gray or pale centers.",
            "Lesion margins may appear brown.",
            "Multiple lesions may occur on the same leaf.",
        ],
        "early_symptoms": (
            "Small lesions may develop on leaves and later become "
            "spindle-shaped."
        ),
        "severity_indicators": (
            "Increasing lesion count, expanding lesions, or affected "
            "plant parts should be reviewed by an agricultural expert."
        ),
    },

    "early blight": {
        "visual_signs": [
            "Brown lesions may appear on leaves.",
            "Some lesions may show concentric ring patterns.",
            "Yellowing may develop around affected areas.",
            "Older leaves may show more visible symptoms.",
        ],
        "early_symptoms": (
            "Small brown leaf lesions may develop and gradually enlarge."
        ),
        "severity_indicators": (
            "Larger lesions, increasing yellowing, and extensive leaf "
            "damage may indicate progression."
        ),
    },

    "late blight": {
        "visual_signs": [
            "Irregular dark-green, brown, or water-soaked-looking patches may appear.",
            "Lesions may expand under favorable conditions.",
            "Leaf tissue may become brown and necrotic.",
            "Affected areas may appear irregular rather than circular.",
        ],
        "early_symptoms": (
            "Irregular pale, dark, or water-soaked-looking patches may "
            "appear on leaves."
        ),
        "severity_indicators": (
            "Rapidly expanding dark lesions or widespread tissue damage "
            "requires prompt expert assessment."
        ),
    },

    "healthy": {
        "visual_signs": [
            "The classifier identified the image as a healthy class.",
            "No disease-specific symptoms were assigned by the classifier.",
            "Continue monitoring for spots, discoloration, or wilting.",
        ],
        "early_symptoms": (
            "The classifier identified the uploaded image as belonging "
            "to a healthy class."
        ),
        "severity_indicators": (
            "No disease severity is assigned for a healthy-class prediction."
        ),
    },
}


def get_disease_symptoms(disease_name):
    """
    Return general reference symptoms for the predicted disease label.
    These are not independently verified image-level detections.
    """
    normalized = str(disease_name or "").lower()
    normalized = normalized.replace("_", " ").replace("-", " ")

    for disease_key, symptom_data in DISEASE_SYMPTOMS.items():
        if disease_key in normalized:
            return symptom_data

    return {
        "visual_signs": [
            "Disease-specific visual signs are not yet available in the reference database.",
            "Review the uploaded crop image with an agricultural expert.",
        ],
        "early_symptoms": (
            "A disease-specific early symptom description is not available "
            "for this prediction label."
        ),
        "severity_indicators": (
            "Severity has not been assessed. Expert confirmation is recommended."
        ),
    }


# ============================================================
# 2. GENERAL DISEASE ADVISORY DATABASE
# ============================================================

def get_disease_advisory(crop_name, disease_name):
    """
    General fallback guidance.
    Do not invent pesticide brands, application doses, or schedules.
    """

    crop = str(crop_name or "").lower()
    disease = str(disease_name or "").lower()

    if crop == "rice" and "brown spot" in disease:
        return {
            "solution": (
                "Remove severely affected plant material where practical. "
                "Monitor nearby plants and avoid prolonged crop stress. "
                "Confirm the diagnosis with an agricultural expert."
            ),
            "fertilizer": (
                "Follow a soil-test-based, balanced nutrient plan for rice. "
                "Avoid applying extra nitrogen without considering crop stage "
                "and local agricultural recommendations."
            ),
            "pesticide": (
                "No pesticide has been verified for this analysis. "
                "Ask an agricultural expert to confirm the disease and select "
                "a locally registered product and label dose, if treatment is needed."
            ),
            "prevention": (
                "Use healthy seed, maintain suitable field and water management, "
                "monitor the crop regularly, and follow local extension advice."
            ),
        }

    return {
        "solution": (
            "A verified disease-specific solution is not available in the "
            "advisory database yet. Please obtain expert confirmation."
        ),
        "fertilizer": (
            "Use fertilizer according to crop type, crop stage, and soil-test "
            "recommendations. Fertilizer is not a substitute for disease treatment."
        ),
        "pesticide": (
            "No verified pesticide recommendation is available for this result. "
            "Confirm the crop and disease with an agricultural expert before use."
        ),
        "prevention": (
            "Monitor the crop regularly and follow recommendations from your "
            "local agricultural extension office."
        ),
    }


# ============================================================
# 3. COMMON HELPERS
# ============================================================

def normalize_label(value):
    value = str(value or "").strip()

    if not value:
        return "Not available"

    return value.replace("_", " ").replace("-", " ").title()


def infer_crop_name(crop_value, disease_value):
    """
    Prefer the crop name returned by the model.
    Otherwise infer from recognizable disease labels.
    """
    crop_value = str(crop_value or "").strip()

    if crop_value and crop_value.lower() not in {
        "unknown",
        "none",
        "null",
        "not available",
    }:
        return normalize_label(crop_value)

    disease = str(disease_value or "").lower().replace("_", " ")

    crop_patterns = {
        "rice": ["rice", "brown spot", "bacterial leaf blight", "leaf blast"],
        "tomato": ["tomato"],
        "maize": ["maize", "corn"],
        "cashew": ["cashew"],
        "potato": ["potato"],
        "apple": ["apple"],
        "grape": ["grape"],
        "chilli": ["chilli", "chili"],
    }

    for crop, patterns in crop_patterns.items():
        if any(pattern in disease for pattern in patterns):
            return crop.title()

    return "Crop not identified"


def format_confidence(value):
    if value is None or str(value).strip() == "":
        return "Not available"

    confidence = str(value).strip()

    if confidence.endswith("%"):
        return confidence

    try:
        return f"{float(confidence):.2f}%"
    except (TypeError, ValueError):
        return confidence


def set_if_field_exists(instance, field_name, value):
    """
    Assign only when the model has the requested field.
    """
    if hasattr(instance, field_name):
        setattr(instance, field_name, value)


def get_analysis_image_url(analysis):
    try:
        if analysis.image and analysis.image.name:
            return analysis.image.url
    except (ValueError, OSError):
        pass

    return ""


def get_status_display(analysis):
    try:
        return analysis.get_status_display()
    except (AttributeError, ValueError):
        return normalize_label(getattr(analysis, "status", "Pending"))


def get_analysis_report_data(analysis):
    """
    Prepare structured result data for the HTML page and PDF.
    Expert-reviewed values take priority over AI-generated values.
    """

    disease_raw = (
        getattr(analysis, "expert_disease", "")
        or getattr(analysis, "ai_disease", "")
        or "Unknown"
    )

    disease_name = normalize_label(disease_raw)

    crop_name = infer_crop_name(
        getattr(analysis, "ai_crop", ""),
        disease_name,
    )

    advisory = get_disease_advisory(
        crop_name,
        disease_name,
    )

    symptoms = get_disease_symptoms(disease_name)

    solution = (
        getattr(analysis, "expert_solution", "")
        or getattr(analysis, "ai_solution", "")
        or advisory["solution"]
    )

    fertilizer = (
        getattr(analysis, "expert_fertilizer", "")
        or getattr(analysis, "ai_fertilizer", "")
        or advisory["fertilizer"]
    )

    pesticide = (
        getattr(analysis, "expert_pesticide", "")
        or getattr(analysis, "ai_pesticide", "")
        or advisory["pesticide"]
    )

    prevention = (
        getattr(analysis, "expert_prevention", "")
        or getattr(analysis, "ai_prevention", "")
        or advisory["prevention"]
    )

    return {
        "analysis": analysis,
        "image_url": get_analysis_image_url(analysis),

        "crop_name": crop_name,
        "disease_name": disease_name,
        "confidence_display": format_confidence(
            getattr(analysis, "ai_confidence", "")
        ),

        "solution_display": solution,
        "fertilizer_display": fertilizer,
        "pesticide_display": pesticide,
        "prevention_display": prevention,

        "visual_signs": symptoms["visual_signs"],
        "early_symptoms": symptoms["early_symptoms"],
        "severity_indicators": symptoms["severity_indicators"],
        "symptom_source": (
            "General reference symptoms associated with the predicted disease. "
            "These are not individually verified image detections."
        ),

        "status_display": get_status_display(analysis),
    }


# ============================================================
# 4. CROP ANALYSIS HOMEPAGE
# URL: /prediction/
# ============================================================

@login_required(login_url="accounts:login")
def crop_analysis_home(request):

    user_analyses = (
        CropAnalysis.objects
        .filter(farmer=request.user)
        .order_by("-created_at")
    )

    context = {
        "total_analyses": user_analyses.count(),

        "pending_analyses": user_analyses.filter(
            status=CropAnalysis.STATUS_SENT_TO_EXPERT
        ).count(),

        "verified_analyses": user_analyses.filter(
            status=CropAnalysis.STATUS_VERIFIED
        ).count(),

        "recent_analyses": user_analyses[:5],
        "form": CropImageForm(),
    }

    return render(
        request,
        "prediction/crop_analysis_home.html",
        context,
    )


# ============================================================
# 5. CROP IMAGE ANALYSIS
# URL: /prediction/analyze/
# ============================================================

@login_required(login_url="accounts:login")
def crop_analysis_view(request):

    if request.method != "POST":
        return render(
            request,
            "prediction/crop_analysis.html",
            {"form": CropImageForm()},
        )

    form = CropImageForm(request.POST, request.FILES)

    if not form.is_valid():
        messages.error(
            request,
            "Please correct the errors in the uploaded image form.",
        )

        return render(
            request,
            "prediction/crop_analysis.html",
            {"form": form},
        )

    analysis = form.save(commit=False)
    analysis.farmer = request.user

    saved_image_name = None

    try:
        analysis.save()

        if not analysis.image:
            raise ValueError("No crop image was saved.")

        saved_image_name = analysis.image.name

        result = predict_disease(analysis.image.path)

        if not isinstance(result, dict):
            raise ValueError(
                "AI model returned an invalid result. Expected a dictionary."
            )

        disease_raw = (
            result.get("disease_name")
            or result.get("disease")
            or result.get("class_name")
            or "Unknown"
        )

        crop_raw = (
            result.get("crop_name")
            or result.get("crop")
            or result.get("plant")
            or ""
        )

        confidence = result.get("confidence", "")

        disease_name = str(disease_raw).strip() or "Unknown"
        crop_name = infer_crop_name(crop_raw, disease_name)

        advisory = get_disease_advisory(
            crop_name,
            disease_name,
        )

        set_if_field_exists(
            analysis,
            "ai_disease",
            disease_name,
        )

        set_if_field_exists(
            analysis,
            "ai_crop",
            crop_name,
        )

        set_if_field_exists(
            analysis,
            "ai_confidence",
            str(confidence),
        )

        set_if_field_exists(
            analysis,
            "ai_solution",
            str(result.get("solution") or advisory["solution"]),
        )

        set_if_field_exists(
            analysis,
            "ai_fertilizer",
            str(result.get("fertilizer") or advisory["fertilizer"]),
        )

        set_if_field_exists(
            analysis,
            "ai_pesticide",
            str(result.get("pesticide") or advisory["pesticide"]),
        )

        set_if_field_exists(
            analysis,
            "ai_prevention",
            str(result.get("prevention") or advisory["prevention"]),
        )

        analysis.status = CropAnalysis.STATUS_SENT_TO_EXPERT
        analysis.save()

        messages.success(
            request,
            "Crop analysis completed successfully. "
            "Your result has been submitted for expert review.",
        )

        return redirect(
            "prediction:analysis_status",
            pk=analysis.pk,
        )

    except Exception as error:

        if analysis.pk:
            analysis.delete()

        if saved_image_name:
            try:
                if default_storage.exists(saved_image_name):
                    default_storage.delete(saved_image_name)
            except Exception:
                pass

        messages.error(
            request,
            f"Crop analysis failed: {error}",
        )

        return render(
            request,
            "prediction/crop_analysis.html",
            {"form": form},
        )


# ============================================================
# 6. ANALYSIS RESULT PAGE
# URL: /prediction/analyze/status/<pk>/
# ============================================================

@login_required(login_url="accounts:login")
def analysis_status_view(request, pk):
    """
    Render the crop-analysis result page.

    The template path is intentionally analysis_status.html because this is
    the template used by the current analysis-status route.
    """
    analysis = get_object_or_404(
        CropAnalysis,
        pk=pk,
        farmer=request.user,
    )

    context = get_analysis_report_data(analysis)

    # Keep the model instance available to the template for any additional
    # project-specific fields, while preserving the existing report context.
    context["analysis"] = analysis

    return render(
        request,
        "prediction/analysis_status.html",
        context,
    )


# ============================================================
# 7. COLORFUL PDF REPORT
# URL: /prediction/report/<pk>/pdf/
# ============================================================

@login_required(login_url="accounts:login")
def download_analysis_pdf(request, pk):

    analysis = get_object_or_404(
        CropAnalysis,
        pk=pk,
        farmer=request.user,
    )

    report = get_analysis_report_data(analysis)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="KisanSathi_Crop_Report_{analysis.pk}.pdf"'
    )

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=19 * mm,
        title=f"KisanSathi AI Crop Report {analysis.pk}",
        author="KisanSathi AI",
    )

    # Color palette
    GREEN = colors.HexColor("#166534")
    DARK_GREEN = colors.HexColor("#14532D")
    LIGHT_GREEN = colors.HexColor("#DCFCE7")
    PALE_GREEN = colors.HexColor("#F0FDF4")

    BLUE = colors.HexColor("#2563EB")
    LIGHT_BLUE = colors.HexColor("#EFF6FF")

    PURPLE = colors.HexColor("#805AD5")
    LIGHT_PURPLE = colors.HexColor("#FAF7FF")

    ORANGE = colors.HexColor("#D97706")
    LIGHT_ORANGE = colors.HexColor("#FFF7E6")

    TEXT = colors.HexColor("#1F2937")
    MUTED = colors.HexColor("#64748B")
    BORDER = colors.HexColor("#D1D5DB")
    WHITE = colors.white

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="KSReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=23,
        leading=28,
        textColor=WHITE,
        alignment=TA_LEFT,
        spaceAfter=4,
    ))

    styles.add(ParagraphStyle(
        name="KSReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#E5F5E9"),
    ))

    styles.add(ParagraphStyle(
        name="KSSectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=DARK_GREEN,
        spaceBefore=10,
        spaceAfter=7,
    ))

    styles.add(ParagraphStyle(
        name="KSBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=TEXT,
    ))

    styles.add(ParagraphStyle(
        name="KSLabel",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=MUTED,
    ))

    styles.add(ParagraphStyle(
        name="KSValue",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=TEXT,
    ))

    styles.add(ParagraphStyle(
        name="KSFooter",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=MUTED,
    ))

    def para(value, style="KSBody"):
        safe_value = escape(str(value or "")).replace("\n", "<br/>")
        return Paragraph(safe_value, styles[style])

    story = []

    # Header banner
    header = Table(
        [[
            [
                Paragraph("KisanSathi AI", styles["KSReportTitle"]),
                Paragraph(
                    "Smart Agriculture | Crop Health Analysis Report",
                    styles["KSReportSubtitle"],
                ),
            ]
        ]],
        colWidths=[174 * mm],
    )

    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GREEN),
        ("LEFTPADDING", (0, 0), (-1, -1), 15),
        ("RIGHTPADDING", (0, 0), (-1, -1), 15),
        ("TOPPADDING", (0, 0), (-1, -1), 15),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 15),
    ]))

    story.append(header)
    story.append(Spacer(1, 7 * mm))

    # Report metadata
    created_at = getattr(analysis, "created_at", None)

    report_date = (
        created_at.strftime("%d %B %Y, %I:%M %p")
        if created_at
        else "Not available"
    )

    metadata_table = Table(
        [
            [
                para("REPORT ID", "KSLabel"),
                para("GENERATED ON", "KSLabel"),
                para("REVIEW STATUS", "KSLabel"),
            ],
            [
                para(f"KS-{analysis.pk}", "KSValue"),
                para(report_date),
                para(report["status_display"]),
            ],
        ],
        colWidths=[48 * mm, 70 * mm, 56 * mm],
    )

    metadata_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE_GREEN),
        ("BOX", (0, 0), (-1, -1), 0.7, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    story.append(metadata_table)
    story.append(Spacer(1, 5 * mm))

    # Uploaded crop image
    try:
        if analysis.image and analysis.image.path:
            crop_image = PDFImage(
                analysis.image.path,
                width=75 * mm,
                height=58 * mm,
                kind="proportional",
            )

            image_table = Table(
                [[crop_image]],
                colWidths=[174 * mm],
            )

            image_table.setStyle(TableStyle([
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("BACKGROUND", (0, 0), (-1, -1), PALE_GREEN),
                ("BOX", (0, 0), (-1, -1), 0.7, BORDER),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]))

            story.append(image_table)
            story.append(Spacer(1, 4 * mm))

    except (ValueError, OSError):
        story.append(para("Crop image is unavailable for this report."))
        story.append(Spacer(1, 4 * mm))

    # Prediction summary
    story.append(Paragraph(
        "1. AI Prediction Summary",
        styles["KSSectionHeading"],
    ))

    summary_table = Table(
        [
            [
                para("CROP", "KSLabel"),
                para("DETECTED DISEASE", "KSLabel"),
                para("MODEL CONFIDENCE", "KSLabel"),
            ],
            [
                para(report["crop_name"], "KSValue"),
                para(report["disease_name"], "KSValue"),
                para(report["confidence_display"], "KSValue"),
            ],
        ],
        colWidths=[48 * mm, 78 * mm, 48 * mm],
    )

    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GREEN),
        ("BOX", (0, 0), (-1, -1), 0.8, GREEN),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))

    story.append(summary_table)
    story.append(Spacer(1, 3 * mm))

    # Disease symptoms section
    story.append(Paragraph(
        "2. Disease Symptoms and Visual Signs",
        styles["KSSectionHeading"],
    ))

    story.append(para(
        "Common reference symptoms associated with the predicted disease:"
    ))
    story.append(Spacer(1, 3 * mm))

    symptom_rows = []

    for sign in report["visual_signs"]:
        symptom_rows.append([
            Paragraph(
                "&#8226; " + escape(str(sign)),
                styles["KSBody"],
            )
        ])

    symptom_table = Table(
        symptom_rows,
        colWidths=[174 * mm],
    )

    symptom_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_PURPLE),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#D8C9F5")),
        ("LINEBEFORE", (0, 0), (0, -1), 4, PURPLE),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    story.append(symptom_table)
    story.append(Spacer(1, 4 * mm))

    symptom_details = Table(
        [
            [
                para("EARLY SYMPTOMS", "KSLabel"),
                para("SEVERITY INDICATORS", "KSLabel"),
            ],
            [
                para(report["early_symptoms"]),
                para(report["severity_indicators"]),
            ],
        ],
        colWidths=[87 * mm, 87 * mm],
    )

    symptom_details.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_PURPLE),
        ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#D8C9F5")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D8C9F5")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))

    story.append(symptom_details)
    story.append(Spacer(1, 3 * mm))

    story.append(Paragraph(
        escape(report["symptom_source"]),
        styles["KSFooter"],
    ))

    story.append(Spacer(1, 3 * mm))

    # Reusable advisory section
    def add_advisory_section(number, title, content, background, accent):
        story.append(Paragraph(
            f"{number}. {title}",
            styles["KSSectionHeading"],
        ))

        advisory_table = Table(
            [[para(content)]],
            colWidths=[174 * mm],
        )

        advisory_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), background),
            ("BOX", (0, 0), (-1, -1), 0.8, accent),
            ("LINEBEFORE", (0, 0), (0, -1), 4, accent),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 11),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 11),
        ]))

        story.append(advisory_table)
        story.append(Spacer(1, 2 * mm))

    add_advisory_section(
        3,
        "Suggested Solution",
        report["solution_display"],
        LIGHT_BLUE,
        BLUE,
    )

    add_advisory_section(
        4,
        "Fertilizer Guidance",
        report["fertilizer_display"],
        LIGHT_GREEN,
        GREEN,
    )

    add_advisory_section(
        5,
        "Pesticide Guidance",
        report["pesticide_display"],
        LIGHT_ORANGE,
        ORANGE,
    )

    add_advisory_section(
        6,
        "Prevention and Monitoring",
        report["prevention_display"],
        PALE_GREEN,
        GREEN,
    )

    # Build the PDF and return it as a downloadable response.
    document.build(story)
    buffer.seek(0)
    response.write(buffer.getvalue())
    return response


# ============================================================
# 8. EXPERT DASHBOARD
# ============================================================

@login_required(login_url="accounts:login")
def expert_dashboard_view(request):
    """Display crop analyses awaiting expert review."""
    analyses = CropAnalysis.objects.all().order_by("-created_at")
    if hasattr(CropAnalysis, "STATUS_SENT_TO_EXPERT"):
        analyses = analyses.filter(status=CropAnalysis.STATUS_SENT_TO_EXPERT)
    return render(request, "prediction/expert_dashboard.html", {"analyses": analyses})


# ============================================================
# 9. EXPERT REVIEW
# ============================================================

@login_required(login_url="accounts:login")
def expert_review_view(request, pk):
    """Save an expert review using the project's ExpertReviewForm."""
    analysis = get_object_or_404(CropAnalysis, pk=pk)
    if request.method == "POST":
        form = ExpertReviewForm(request.POST, instance=analysis)
        if form.is_valid():
            reviewed_analysis = form.save(commit=False)
            if hasattr(reviewed_analysis, "expert"):
                reviewed_analysis.expert = request.user
            if hasattr(CropAnalysis, "STATUS_VERIFIED"):
                reviewed_analysis.status = CropAnalysis.STATUS_VERIFIED
            reviewed_analysis.save()
            messages.success(request, "Expert review saved successfully.")
            return redirect("prediction:expert_dashboard")
        messages.error(request, "Please correct the errors in the review form.")
    else:
        form = ExpertReviewForm(instance=analysis)
    return render(request, "prediction/expert_review.html", {"analysis": analysis, "form": form})
