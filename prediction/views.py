import logging
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

from .models import CropAnalysis, SeedAnalysis
from .forms import CropImageForm, ExpertReviewForm, SeedAnalysisForm
from .ai_model import predict_disease
from .seed_analyzer import analyze_seed_quality, get_crop_standard

logger = logging.getLogger(__name__)


# ============================================================
# 1. DISEASE SYMPTOMS REFERENCE DATABASE
# ============================================================

DISEASE_SYMPTOMS = {
    # ── Rice diseases ────────────────────────────────────────────
    "brown spot": {
        "visual_signs": [
            "Small brown or dark-brown spots may appear on rice leaves.",
            "Spots may increase in size as symptoms progress.",
            "Affected leaf tissue may become dry or necrotic.",
            "Severely affected leaves may show extensive discoloration.",
        ],
        "early_symptoms": (
            "Small brown spots may appear on rice leaf surfaces. "
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
            "Yellowing may extend along the rice leaf.",
            "Affected tissue may become straw-colored.",
            "Leaves may dry from the tip or edge.",
        ],
        "early_symptoms": (
            "Water-soaked or yellowish leaf areas may appear, often near "
            "the leaf tip or margin of rice plants."
        ),
        "severity_indicators": (
            "Long yellow-to-straw-colored lesions and extensive leaf drying "
            "may indicate more severe symptoms."
        ),
    },

    "leaf blast": {
        "visual_signs": [
            "Spindle-shaped or diamond-shaped lesions may develop on rice leaves.",
            "Lesions may have gray or pale centers with brown margins.",
            "Multiple lesions may occur on the same leaf.",
            "Neck blast may cause whitish or grayish panicles.",
        ],
        "early_symptoms": (
            "Small lesions may develop on rice leaves and later become "
            "spindle-shaped with pale centers."
        ),
        "severity_indicators": (
            "Increasing lesion count, expanding lesions, or panicle "
            "infection should be reviewed by an agricultural expert."
        ),
    },

    # ── Maize diseases ───────────────────────────────────────────
    "leaf blight": {
        "visual_signs": [
            "Long, grayish-green or tan lesions may appear on maize leaves.",
            "Lesions may extend parallel to leaf veins.",
            "Affected areas may turn brown and dry.",
            "Entire leaves may die in severe cases.",
        ],
        "early_symptoms": (
            "Small, water-soaked or pale lesions may appear on lower maize "
            "leaves first, then spread upward."
        ),
        "severity_indicators": (
            "Widespread lesion coverage, premature leaf death, or spread "
            "to upper canopy leaves may indicate severe infection."
        ),
    },

    "streak virus": {
        "visual_signs": [
            "Bright yellow or white streaks may run along maize leaf veins.",
            "Streaking may appear on younger leaves first.",
            "Leaves may appear pale or chlorotic overall.",
            "Severely affected plants may show stunted growth.",
        ],
        "early_symptoms": (
            "Fine yellow or white streaks may appear on young maize leaves, "
            "usually following vein patterns."
        ),
        "severity_indicators": (
            "Intense streaking across most leaves and stunted plant "
            "development suggest significant viral spread."
        ),
    },

    # ── Cashew diseases ──────────────────────────────────────────
    "leaf miner": {
        "visual_signs": [
            "Irregular silvery or brown winding trails may appear inside leaves.",
            "Leaf surface may blister or pucker along the mine trail.",
            "Affected leaf areas may dry out and die.",
            "Small exit holes may be visible at the end of each mine.",
        ],
        "early_symptoms": (
            "Small winding tunnels or trails may appear beneath the leaf "
            "surface of cashew plants."
        ),
        "severity_indicators": (
            "Numerous mines per leaf, extensive leaf area loss, or widespread "
            "infestation should prompt expert evaluation."
        ),
    },

    "red rust": {
        "visual_signs": [
            "Orange-red powdery or rust-colored pustules may appear on leaves.",
            "Pustules may rupture and release rust-colored spores.",
            "Affected leaves may yellow and drop prematurely.",
            "Stems or petioles may also show reddish discoloration.",
        ],
        "early_symptoms": (
            "Small orange or rust-colored spots may appear on cashew leaf "
            "surfaces, often on the underside."
        ),
        "severity_indicators": (
            "Heavy pustule coverage, significant defoliation, or spread to "
            "stems may indicate severe rust infection."
        ),
    },

    # ── Tomato diseases ──────────────────────────────────────────
    "septoria leaf spot": {
        "visual_signs": [
            "Small, circular spots with dark borders and lighter centers may appear on tomato leaves.",
            "Tiny dark dots (pycnidia) may be visible within the spots.",
            "Lower and older leaves are typically affected first.",
            "Severely infected leaves may turn yellow and drop.",
        ],
        "early_symptoms": (
            "Small water-soaked or grayish circular spots may first appear "
            "on lower tomato leaves."
        ),
        "severity_indicators": (
            "Rapidly increasing spots, yellowing, and premature leaf drop "
            "suggest spreading infection that requires expert review."
        ),
    },

    "verticillium wilt": {
        "visual_signs": [
            "Lower leaves may show V-shaped yellow lesions from the edge.",
            "Yellowing and wilting may begin on one side of the leaf or plant.",
            "Stems may show brown discoloration in vascular tissue when cut.",
            "Plants may appear stunted or wilted during warmer parts of the day.",
        ],
        "early_symptoms": (
            "Mild yellowing or wilting of lower tomato leaves, particularly "
            "in warm conditions, may be an early indicator."
        ),
        "severity_indicators": (
            "Progressive wilting, V-shaped lesions on multiple leaves, and "
            "internal stem browning indicate systemic infection."
        ),
    },

    "verticulium wilt": {
        "visual_signs": [
            "Lower leaves may show V-shaped yellow lesions from the edge.",
            "Yellowing and wilting may begin on one side of the leaf or plant.",
            "Stems may show brown discoloration in vascular tissue when cut.",
            "Plants may appear stunted or wilted during warmer parts of the day.",
        ],
        "early_symptoms": (
            "Mild yellowing or wilting of lower tomato leaves, particularly "
            "in warm conditions, may be an early indicator."
        ),
        "severity_indicators": (
            "Progressive wilting, V-shaped lesions on multiple leaves, and "
            "internal stem browning indicate systemic infection."
        ),
    },

    # ── General / multi-crop conditions ──────────────────────────
    "early blight": {
        "visual_signs": [
            "Brown lesions may appear on leaves with concentric ring patterns.",
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

    "fungi": {
        "visual_signs": [
            "Fungal-type discoloration or lesions may be visible on leaves or stems.",
            "Powdery, fuzzy, or rust-colored growth may be present.",
            "Affected tissue may turn yellow, brown, or necrotic.",
        ],
        "early_symptoms": (
            "The classifier detected possible fungal symptoms. "
            "Monitor closely and consult an agricultural expert for confirmation."
        ),
        "severity_indicators": (
            "Expanding affected areas, spore production, or widespread "
            "plant involvement may indicate serious fungal disease."
        ),
    },

    "nematode": {
        "visual_signs": [
            "Stunted plant growth compared to healthy neighbours may be observed.",
            "Root galls or swellings may be visible on excavated roots.",
            "Leaves may yellow despite adequate moisture and nutrients.",
            "Plants may wilt during hot periods and recover at night.",
        ],
        "early_symptoms": (
            "Patchy poor growth, unexplained wilting, or root swelling may "
            "indicate nematode activity in the soil."
        ),
        "severity_indicators": (
            "Widespread root galling, severe stunting, and yield loss are "
            "indicators of heavy nematode pressure."
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
    General crop-and-disease advisory guidance.
    Do not invent pesticide brands, application doses, or schedules.
    """

    crop = str(crop_name or "").lower().strip()
    disease = str(disease_name or "").lower().strip()

    # ── Rice advisories ──────────────────────────────────────────
    if crop == "rice":
        if "brown spot" in disease:
            return {
                "solution": (
                    "Remove and destroy severely affected plant material where practical. "
                    "Improve drainage and reduce crop stress. "
                    "Confirm the diagnosis with an agricultural expert."
                ),
                "fertilizer": (
                    "Follow a soil-test-based, balanced nutrient plan for rice. "
                    "Ensure adequate potassium; avoid excess nitrogen during "
                    "susceptible growth stages."
                ),
                "pesticide": (
                    "No pesticide has been automatically verified for this analysis. "
                    "Ask an agricultural expert to confirm the disease and select "
                    "a locally registered fungicide and label dose if treatment is needed."
                ),
                "prevention": (
                    "Use certified disease-free seed, maintain proper field drainage, "
                    "avoid nutrient stress, and follow local extension advice."
                ),
            }
        if "bacterial leaf blight" in disease:
            return {
                "solution": (
                    "Remove and destroy infected crop debris. "
                    "Avoid excessive nitrogen fertilizer. "
                    "Confirm with an agricultural expert before taking action."
                ),
                "fertilizer": (
                    "Reduce nitrogen applications that promote lush, susceptible growth. "
                    "Maintain balanced potassium and phosphorus levels."
                ),
                "pesticide": (
                    "Bacterial leaf blight has limited chemical control options. "
                    "Consult an agricultural extension officer for copper-based or "
                    "locally registered bactericide recommendations."
                ),
                "prevention": (
                    "Plant resistant varieties where available, manage irrigation water "
                    "carefully, and avoid mechanical damage that allows bacterial entry."
                ),
            }
        if "leaf blast" in disease or "blast" in disease:
            return {
                "solution": (
                    "Monitor the crop closely, especially during flowering and tillering. "
                    "Consult an agricultural expert promptly if blast is confirmed."
                ),
                "fertilizer": (
                    "Avoid heavy nitrogen applications which increase blast susceptibility. "
                    "Split nitrogen doses across crop stages as recommended."
                ),
                "pesticide": (
                    "Fungicides may be recommended for blast control when applied at "
                    "the correct growth stage. Consult an expert for locally registered "
                    "products and application timing."
                ),
                "prevention": (
                    "Use blast-resistant varieties, avoid late or heavy nitrogen applications, "
                    "and maintain proper plant spacing for good airflow."
                ),
            }
        if "healthy" in disease:
            return {
                "solution": "No treatment needed. The plant appears healthy.",
                "fertilizer": (
                    "Continue standard soil-test-based nutrient management for rice."
                ),
                "pesticide": "No pesticide application is required for healthy rice.",
                "prevention": (
                    "Continue regular monitoring, maintain proper field drainage, "
                    "and use certified seed in future seasons."
                ),
            }

    # ── Maize advisories ─────────────────────────────────────────
    if crop == "maize":
        if "leaf blight" in disease or "blight" in disease:
            return {
                "solution": (
                    "Remove heavily infected leaves. Improve air circulation by managing "
                    "plant density. Seek expert confirmation before applying fungicides."
                ),
                "fertilizer": (
                    "Maintain balanced nutrition. Ensure adequate potassium to support "
                    "plant defense. Follow soil-test recommendations."
                ),
                "pesticide": (
                    "Fungicide applications may reduce turcicum blight severity when "
                    "applied early. Consult an expert for locally registered products."
                ),
                "prevention": (
                    "Plant resistant hybrids, rotate crops to reduce pathogen load, "
                    "and avoid working in wet fields to limit disease spread."
                ),
            }
        if "streak virus" in disease or "streak" in disease:
            return {
                "solution": (
                    "Remove and destroy severely affected plants to reduce viral spread. "
                    "Control leafhopper vectors that transmit maize streak virus."
                ),
                "fertilizer": (
                    "Maintain adequate nutrition to support crop recovery. "
                    "Avoid excess nitrogen which may attract more vectors."
                ),
                "pesticide": (
                    "Insecticides targeting leafhopper vectors may help limit spread. "
                    "Consult an agricultural expert for registered products and timing."
                ),
                "prevention": (
                    "Plant streak-resistant maize varieties, plant early to avoid "
                    "peak vector populations, and use insecticide seed dressings "
                    "where recommended by local extension services."
                ),
            }
        if "healthy" in disease:
            return {
                "solution": "No treatment needed. The maize plant appears healthy.",
                "fertilizer": (
                    "Continue standard soil-test-based nutrient management for maize."
                ),
                "pesticide": "No pesticide application is required for healthy maize.",
                "prevention": (
                    "Continue regular scouting and follow local extension "
                    "recommendations for your maize variety."
                ),
            }

    # ── Cashew advisories ────────────────────────────────────────
    if crop == "cashew":
        if "leaf miner" in disease:
            return {
                "solution": (
                    "Remove and destroy heavily mined leaves. "
                    "Encourage natural predators. Consult an expert for "
                    "targeted management options."
                ),
                "fertilizer": (
                    "Maintain balanced nutrition to support plant vigour "
                    "and recovery from leaf miner damage."
                ),
                "pesticide": (
                    "Systemic insecticides or targeted sprays may be recommended. "
                    "Consult an agricultural expert for locally registered products "
                    "and appropriate timing."
                ),
                "prevention": (
                    "Monitor for early signs of mining activity, avoid dense planting "
                    "that reduces airflow, and use yellow sticky traps for monitoring."
                ),
            }
        if "red rust" in disease:
            return {
                "solution": (
                    "Remove heavily infected leaves and destroy fallen leaf debris. "
                    "Improve air circulation around the canopy."
                ),
                "fertilizer": (
                    "Maintain balanced nutrition, especially adequate potassium, "
                    "to support plant resistance to fungal infections."
                ),
                "pesticide": (
                    "Copper-based fungicides or locally registered products may be "
                    "effective. Consult an agricultural expert for timing and dosage."
                ),
                "prevention": (
                    "Prune dense canopies to improve airflow, avoid overhead "
                    "irrigation, and remove infected leaf litter regularly."
                ),
            }
        if "healthy" in disease:
            return {
                "solution": "No treatment needed. The cashew plant appears healthy.",
                "fertilizer": (
                    "Continue standard soil-test-based nutrient management for cashew."
                ),
                "pesticide": "No pesticide application is required for healthy cashew.",
                "prevention": (
                    "Continue regular monitoring and canopy management practices."
                ),
            }

    # ── Tomato advisories ────────────────────────────────────────
    if crop == "tomato":
        if "septoria" in disease:
            return {
                "solution": (
                    "Remove and destroy infected lower leaves. Avoid overhead "
                    "watering. Seek expert confirmation before applying treatments."
                ),
                "fertilizer": (
                    "Maintain balanced nutrition. Calcium sufficiency may support "
                    "cell wall integrity and reduce infection entry points."
                ),
                "pesticide": (
                    "Fungicides containing chlorothalonil or copper may reduce "
                    "septoria spread. Consult an expert for locally registered "
                    "products and appropriate application intervals."
                ),
                "prevention": (
                    "Use mulch to prevent soil splash, stake plants to improve "
                    "airflow, and rotate tomatoes away from solanaceous crops."
                ),
            }
        if "verticillium" in disease or "verticulium" in disease:
            return {
                "solution": (
                    "There is no cure once a plant is systemically infected. "
                    "Remove and destroy affected plants to limit soil inoculum. "
                    "Consult an expert for integrated management."
                ),
                "fertilizer": (
                    "Avoid excessive nitrogen. Maintain balanced nutrients to "
                    "support healthy root development."
                ),
                "pesticide": (
                    "Fungicide soil drenches have limited efficacy against "
                    "Verticillium wilt. Soil solarization or biological agents "
                    "may help—consult an agricultural expert."
                ),
                "prevention": (
                    "Plant resistant varieties, practice crop rotation for 3–4 years, "
                    "and avoid working infected soil into uninfested areas."
                ),
            }
        if "healthy" in disease:
            return {
                "solution": "No treatment needed. The tomato plant appears healthy.",
                "fertilizer": (
                    "Continue standard soil-test-based nutrient management for tomato."
                ),
                "pesticide": "No pesticide application is required for healthy tomato.",
                "prevention": (
                    "Continue regular scouting and good cultural practices."
                ),
            }

    # ── Generic fallback ─────────────────────────────────────────
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

    user_seed_analyses = (
        SeedAnalysis.objects
        .filter(farmer=request.user)
        .order_by("-created_at")
    )

    total = user_analyses.count()
    verified = user_analyses.filter(status=CropAnalysis.STATUS_VERIFIED).count()
    pending = user_analyses.filter(status=CropAnalysis.STATUS_SENT_TO_EXPERT).count()
    rejected = user_analyses.filter(status=CropAnalysis.STATUS_REJECTED).count()

    accuracy_rate = round((verified / total) * 100, 1) if total > 0 else 0

    total_seeds = user_seed_analyses.count()
    good_seeds = user_seed_analyses.filter(quality_status=SeedAnalysis.QUALITY_GOOD).count()
    bad_seeds = user_seed_analyses.filter(quality_status=SeedAnalysis.QUALITY_BAD).count()

    context = {
        "total_analyses": total,
        "pending_analyses": pending,
        "verified_analyses": verified,
        "rejected_analyses": rejected,
        "accuracy_rate": accuracy_rate,
        "recent_analyses": user_analyses[:5],
        "all_analyses": user_analyses,
        "form": CropImageForm(),

        # Seed Analysis metrics
        "total_seeds": total_seeds,
        "good_seeds": good_seeds,
        "bad_seeds": bad_seeds,
        "recent_seeds": user_seed_analyses[:5],
        "seed_form": SeedAnalysisForm(),
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
    logger.info(
        "Crop analysis request received from user: '%s' (Method: %s)",
        request.user.username,
        request.method,
    )

    if request.method != "POST":
        return render(
            request,
            "prediction/crop_analysis_home.html",
            {
                "form": CropImageForm(),
                "seed_form": SeedAnalysisForm(),
            },
        )

    form = CropImageForm(request.POST, request.FILES)

    if not form.is_valid():
        logger.warning(
            "Crop analysis form validation failed for user '%s': %s",
            request.user.username,
            form.errors.as_json(),
        )
        messages.error(
            request,
            "Please upload a valid image file (JPG, PNG, or WebP).",
        )
        return render(
            request,
            "prediction/crop_analysis_home.html",
            {
                "form": form,
                "seed_form": SeedAnalysisForm(),
            },
        )

    analysis = form.save(commit=False)
    analysis.farmer = request.user
    saved_image_name = None

    try:
        analysis.save()

        if not analysis.image:
            raise ValueError("No crop image was saved to storage.")

        saved_image_name = analysis.image.name
        image_full_path = getattr(analysis.image, "path", None)

        logger.info(
            "Image upload completed. Analysis ID: %d, Path: %s, Storage Name: %s",
            analysis.pk,
            image_full_path,
            saved_image_name,
        )

        # Optional user-selected crop hint from form POST
        user_selected_crop = (
            request.POST.get("crop")
            or request.POST.get("crop_name")
            or request.POST.get("selected_crop")
            or ""
        )

        # Run AI disease prediction using the optimized, thread-safe TensorFlow pipeline
        result = predict_disease(image_full_path)

        if not isinstance(result, dict):
            raise ValueError(
                "AI model returned an unexpected result format. Expected a dictionary."
            )

        disease_raw = (
            result.get("disease_name")
            or result.get("disease")
            or result.get("class_name")
            or "Unknown"
        )

        crop_raw = (
            user_selected_crop
            or result.get("crop_name")
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

        set_if_field_exists(analysis, "ai_disease", disease_name)
        set_if_field_exists(analysis, "ai_crop", crop_name)
        set_if_field_exists(analysis, "ai_confidence", str(confidence))
        set_if_field_exists(analysis, "ai_solution", str(result.get("solution") or advisory["solution"]))
        set_if_field_exists(analysis, "ai_fertilizer", str(result.get("fertilizer") or advisory["fertilizer"]))
        set_if_field_exists(analysis, "ai_pesticide", str(result.get("pesticide") or advisory["pesticide"]))
        set_if_field_exists(analysis, "ai_prevention", str(result.get("prevention") or advisory["prevention"]))

        analysis.status = CropAnalysis.STATUS_SENT_TO_EXPERT
        analysis.save()

        logger.info(
            "Database save completed for analysis ID: %d. Disease: %s, Crop: %s, Confidence: %s",
            analysis.pk,
            disease_name,
            crop_name,
            confidence,
        )

        messages.success(
            request,
            "Crop analysis completed successfully. Your result has been submitted for expert review.",
        )

        return redirect(
            "prediction:analysis_status",
            pk=analysis.pk,
        )

    except Exception as error:
        logger.exception(
            "Crop analysis failed for user '%s' on analysis record ID: %s. Error: %s",
            request.user.username,
            getattr(analysis, "pk", None),
            error,
        )

        # Safe database cleanup on error
        if analysis and getattr(analysis, "pk", None):
            try:
                analysis.delete()
            except Exception as cleanup_err:
                logger.warning(
                    "Cleanup warning: failed to delete aborted analysis record %s: %s",
                    analysis.pk,
                    cleanup_err,
                )

        # Safe storage cleanup on error
        if saved_image_name:
            try:
                if default_storage.exists(saved_image_name):
                    default_storage.delete(saved_image_name)
            except Exception as storage_err:
                logger.warning(
                    "Cleanup warning: failed to remove temporary uploaded image %s: %s",
                    saved_image_name,
                    storage_err,
                )

        # User-facing message without exposing internal server tracebacks
        if isinstance(error, ValueError) and "image" in str(error).lower():
            user_msg = "The uploaded file is not a valid or readable image. Please upload a clear photo of the crop leaf (JPG, PNG, or WebP)."
        else:
            user_msg = "Crop analysis could not be completed right now. Please verify your photo and try again."

        messages.error(request, user_msg)

        return render(
            request,
            "prediction/crop_analysis_home.html",
            {
                "form": form,
                "seed_form": SeedAnalysisForm(),
            },
        )


# ============================================================
# 6. ANALYSIS RESULT PAGE
# URL: /prediction/analyze/status/<pk>/
# ============================================================

@login_required(login_url="accounts:login")
def analysis_status_view(request, pk):
    """
    Render the crop-analysis result page.
    Supports case-insensitive template lookups for cross-platform Linux/Windows compatibility.
    """
    analysis = get_object_or_404(
        CropAnalysis,
        pk=pk,
        farmer=request.user,
    )

    context = get_analysis_report_data(analysis)
    context["analysis"] = analysis

    # Both lowercase and uppercase variants to ensure compatibility on Linux/Render
    template_candidates = [
        "prediction/analysis_status.html",
        "prediction/Analysis_status.html",
    ]

    return render(
        request,
        template_candidates,
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
    return render(
        request,
        [
            "prediction/expert_review.html",
            "prediction/crop_scanner_expert_review.html",
        ],
        {"analysis": analysis, "form": form},
    )


# ============================================================
# 10. SEED QUALITY & VIABILITY ANALYSIS
# URL: /prediction/seed/
# ============================================================

def get_seed_report_data(seed_analysis):
    """
    Format seed assessment report data for UI templates and PDF generator.
    """
    defects_raw = seed_analysis.defects_detected or ""
    defects_list = [d.strip() for d in defects_raw.split("\n") if d.strip()]
    if not defects_list and defects_raw:
        defects_list = [defects_raw]

    crop_key, crop_info = get_crop_standard(seed_analysis.crop_type)

    image_url = ""
    try:
        if seed_analysis.image and seed_analysis.image.name:
            image_url = seed_analysis.image.url
    except Exception:
        pass

    quality_display = "Good / Fit for Sowing"
    if seed_analysis.quality_status == SeedAnalysis.QUALITY_BAD:
        quality_display = "Bad / Unfit for Agriculture"
    elif seed_analysis.quality_status == SeedAnalysis.QUALITY_MODERATE:
        quality_display = "Moderate / Treatment Required"

    return {
        "seed": seed_analysis,
        "image_url": image_url,
        "crop_type": seed_analysis.crop_type,
        "crop_info": crop_info,
        "quality_status": seed_analysis.quality_status,
        "quality_display": quality_display,
        "is_good": seed_analysis.is_good_for_agriculture,
        "viability_score": seed_analysis.viability_score,
        "purity_score": seed_analysis.purity_score,
        "health_rating": seed_analysis.health_rating,
        "risk_level": seed_analysis.risk_level,
        "defects_list": defects_list,
        "suitability_verdict": seed_analysis.suitability_verdict,
        "treatment_advisory": seed_analysis.treatment_advisory,
        "sowing_guidelines": seed_analysis.sowing_guidelines,
        "yield_impact": seed_analysis.yield_impact,
        "created_at_display": seed_analysis.created_at.strftime("%d %B %Y, %I:%M %p") if seed_analysis.created_at else "Recently",
    }


@login_required(login_url="accounts:login")
def seed_analysis_view(request):
    """
    Seed Quality Testing View:
    Farmers can upload seed photos or input physical indicators to predict
    whether the seed is Good (suitable for agriculture) or Bad (defective / unfit).
    """
    if request.method != "POST":
        form = SeedAnalysisForm()
        recent_seeds = SeedAnalysis.objects.filter(farmer=request.user).order_by("-created_at")[:6]
        return render(
            request,
            "prediction/seed_analysis.html",
            {
                "form": form,
                "recent_seeds": recent_seeds,
            },
        )

    form = SeedAnalysisForm(request.POST, request.FILES)
    if not form.is_valid():
        messages.error(request, "Please review the form errors and try again.")
        recent_seeds = SeedAnalysis.objects.filter(farmer=request.user).order_by("-created_at")[:6]
        return render(
            request,
            "prediction/seed_analysis.html",
            {
                "form": form,
                "recent_seeds": recent_seeds,
            },
        )

    try:
        crop_type = form.cleaned_data.get("crop_type", "Wheat")
        visual_condition = form.cleaned_data.get("visual_condition", "good")
        has_insect_holes = form.cleaned_data.get("has_insect_holes", False)
        broken_coat_level = form.cleaned_data.get("broken_coat_level", "none")
        moisture_status = form.cleaned_data.get("moisture_status", "normal")
        float_test_result = form.cleaned_data.get("float_test_result", "sink")
        uploaded_image = request.FILES.get("image")

        # Create model instance
        seed_record = SeedAnalysis(
            farmer=request.user,
            crop_type=crop_type,
            image=uploaded_image,
        )
        seed_record.save()

        # Run AI seed analysis engine
        image_path = seed_record.image.path if seed_record.image else None
        analysis_result = analyze_seed_quality(
            image_path=image_path,
            crop_type=crop_type,
            visual_condition=visual_condition,
            has_insect_holes=has_insect_holes,
            broken_coat_level=broken_coat_level,
            moisture_status=moisture_status,
            float_test_result=float_test_result,
        )

        # Update record with AI output
        seed_record.quality_status = analysis_result["quality_status"]
        seed_record.is_good_for_agriculture = analysis_result["is_good_for_agriculture"]
        seed_record.viability_score = analysis_result["viability_score"]
        seed_record.purity_score = analysis_result["purity_score"]
        seed_record.health_rating = analysis_result["health_rating"]
        seed_record.risk_level = analysis_result["risk_level"]
        seed_record.defects_detected = "\n".join(analysis_result["defects_detected"])
        seed_record.suitability_verdict = analysis_result["suitability_verdict"]
        seed_record.treatment_advisory = analysis_result["treatment_advisory"]
        seed_record.sowing_guidelines = analysis_result["sowing_guidelines"]
        seed_record.yield_impact = analysis_result["yield_impact"]
        seed_record.moisture_condition = moisture_status
        seed_record.float_test_verdict = float_test_result
        seed_record.save()

        if seed_record.is_good_for_agriculture:
            messages.success(request, f"🌱 Seed Analysis Complete: Seed is GOOD for agriculture ({seed_record.viability_score}% Viability).")
        else:
            messages.warning(request, f"⚠️ Seed Analysis Alert: Seed is BAD / Unfit for agriculture ({seed_record.viability_score}% Viability). Do not sow directly.")

        return redirect("prediction:seed_analysis_result", pk=seed_record.pk)

    except Exception as error:
        messages.error(request, f"Seed analysis error: {error}")
        return render(
            request,
            "prediction/seed_analysis.html",
            {
                "form": form,
                "recent_seeds": SeedAnalysis.objects.filter(farmer=request.user).order_by("-created_at")[:6],
            },
        )


# ============================================================
# 11. SEED ANALYSIS RESULT DASHBOARD
# URL: /prediction/seed/status/<pk>/
# ============================================================

@login_required(login_url="accounts:login")
def seed_analysis_result_view(request, pk):
    """
    Detailed Seed Quality Diagnostic & Viability Dashboard.
    """
    seed_analysis = get_object_or_404(
        SeedAnalysis,
        pk=pk,
        farmer=request.user,
    )

    context = get_seed_report_data(seed_analysis)
    return render(
        request,
        "prediction/seed_analysis_result.html",
        context,
    )


# ============================================================
# 12. SEED ANALYSIS PDF REPORT
# URL: /prediction/seed/report/<pk>/pdf/
# ============================================================

@login_required(login_url="accounts:login")
def download_seed_analysis_pdf(request, pk):
    """
    Generate downloadable PDF Seed Testing Certificate.
    """
    seed_analysis = get_object_or_404(
        SeedAnalysis,
        pk=pk,
        farmer=request.user,
    )

    report = get_seed_report_data(seed_analysis)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="KisanSathi_Seed_Certificate_{seed_analysis.pk}.pdf"'
    )

    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=19 * mm,
        title=f"KisanSathi Seed Quality Certificate #{seed_analysis.pk}",
        author="KisanSathi AI",
    )

    GREEN = colors.HexColor("#166534")
    DARK_GREEN = colors.HexColor("#14532D")
    LIGHT_GREEN = colors.HexColor("#DCFCE7")
    PALE_GREEN = colors.HexColor("#F0FDF4")
    RED = colors.HexColor("#DC2626")
    LIGHT_RED = colors.HexColor("#FEF2F2")
    AMBER = colors.HexColor("#D97706")
    LIGHT_AMBER = colors.HexColor("#FEF3C7")
    BLUE = colors.HexColor("#2563EB")
    LIGHT_BLUE = colors.HexColor("#EFF6FF")
    PURPLE = colors.HexColor("#805AD5")
    LIGHT_PURPLE = colors.HexColor("#FAF7FF")
    TEXT = colors.HexColor("#1F2937")
    MUTED = colors.HexColor("#64748B")
    BORDER = colors.HexColor("#D1D5DB")
    WHITE = colors.white

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="KSTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=WHITE,
        alignment=TA_LEFT,
        spaceAfter=4,
    ))

    styles.add(ParagraphStyle(
        name="KSSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#E5F5E9"),
    ))

    styles.add(ParagraphStyle(
        name="KSSection",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=DARK_GREEN,
        spaceBefore=8,
        spaceAfter=6,
    ))

    styles.add(ParagraphStyle(
        name="KSSeedBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=TEXT,
    ))

    styles.add(ParagraphStyle(
        name="KSSeedLabel",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=MUTED,
    ))

    styles.add(ParagraphStyle(
        name="KSSeedVal",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=TEXT,
    ))

    def p(text, style="KSSeedBody"):
        safe = escape(str(text or "")).replace("\n", "<br/>")
        return Paragraph(safe, styles[style])

    story = []

    # Header
    header_color = GREEN if report["is_good"] else (AMBER if report["quality_status"] == "moderate" else RED)
    header = Table(
        [[
            [
                Paragraph("KisanSathi AI — Seed Quality Certificate", styles["KSTitle"]),
                Paragraph("Agricultural Seed Viability & Germination Assessment Report", styles["KSSubtitle"]),
            ]
        ]],
        colWidths=[174 * mm],
    )
    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), header_color),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(header)
    story.append(Spacer(1, 4 * mm))

    # Meta table
    meta_table = Table(
        [
            [
                p("CERTIFICATE ID", "KSSeedLabel"),
                p("CROP / SEED TYPE", "KSSeedLabel"),
                p("TEST DATE", "KSSeedLabel"),
            ],
            [
                p(f"KSS-{seed_analysis.pk}", "KSSeedVal"),
                p(f"{report['crop_type']} ({report['crop_info']['name_hi']})", "KSSeedVal"),
                p(report["created_at_display"]),
            ],
        ],
        colWidths=[48 * mm, 68 * mm, 58 * mm],
    )
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE_GREEN),
        ("BOX", (0, 0), (-1, -1), 0.7, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 4 * mm))

    # Verdict Card
    verdict_bg = LIGHT_GREEN if report["is_good"] else (LIGHT_AMBER if report["quality_status"] == "moderate" else LIGHT_RED)
    verdict_box = Table(
        [
            [
                p("AGRICULTURAL SUITABILITY VERDICT", "KSSeedLabel"),
                p("PREDICTED VIABILITY", "KSSeedLabel"),
                p("PHYSICAL PURITY", "KSSeedLabel"),
                p("RISK LEVEL", "KSSeedLabel"),
            ],
            [
                p(f"<b>{report['quality_display']}</b>", "KSSeedVal"),
                p(f"<b>{report['viability_score']}%</b>", "KSSeedVal"),
                p(f"<b>{report['purity_score']}%</b>", "KSSeedVal"),
                p(f"<b>{report['risk_level']}</b>", "KSSeedVal"),
            ],
        ],
        colWidths=[66 * mm, 36 * mm, 36 * mm, 36 * mm],
    )
    verdict_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), verdict_bg),
        ("BOX", (0, 0), (-1, -1), 0.8, header_color),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(verdict_box)
    story.append(Spacer(1, 4 * mm))

    # Detailed Verdict Section
    story.append(Paragraph("1. Expert Quality Verdict & Field Suitability", styles["KSSection"]))
    verdict_desc_table = Table([[p(report["suitability_verdict"])]], colWidths=[174 * mm])
    verdict_desc_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE_GREEN if report["is_good"] else LIGHT_RED),
        ("BOX", (0, 0), (-1, -1), 0.7, BORDER),
        ("LINEBEFORE", (0, 0), (0, -1), 3.5, header_color),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(verdict_desc_table)
    story.append(Spacer(1, 3 * mm))

    # Defects & Observations
    story.append(Paragraph("2. Physical Inspection & Defect Breakdown", styles["KSSection"]))
    defect_rows = []
    for d in report["defects_list"]:
        defect_rows.append([Paragraph("&#8226; " + escape(str(d)), styles["KSSeedBody"])])
    if defect_rows:
        defect_table = Table(defect_rows, colWidths=[174 * mm])
        defect_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_PURPLE),
            ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#D8C9F5")),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(defect_table)
        story.append(Spacer(1, 3 * mm))

    # Pre-sowing Treatment Advisory
    story.append(Paragraph("3. Recommended Pre-Sowing Seed Treatment (बीजोपचार विधि)", styles["KSSection"]))
    treatment_table = Table([[p(report["treatment_advisory"])]], colWidths=[174 * mm])
    treatment_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
        ("BOX", (0, 0), (-1, -1), 0.7, BLUE),
        ("LINEBEFORE", (0, 0), (0, -1), 3.5, BLUE),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(treatment_table)
    story.append(Spacer(1, 3 * mm))

    # Sowing & Yield
    story.append(Paragraph("4. Agronomic Sowing Guidelines & Yield Impact", styles["KSSection"]))
    sowing_table = Table(
        [
            [p("SOWING GUIDELINES", "KSSeedLabel"), p("ESTIMATED YIELD IMPACT", "KSSeedLabel")],
            [p(report["sowing_guidelines"]), p(report["yield_impact"])],
        ],
        colWidths=[87 * mm, 87 * mm],
    )
    sowing_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE_GREEN),
        ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(sowing_table)

    document.build(story)
    buffer.seek(0)
    response.write(buffer.getvalue())
    return response
