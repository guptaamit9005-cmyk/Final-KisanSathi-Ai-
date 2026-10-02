"""
AI Seed Quality & Viability Analyzer Engine
Determines whether seeds are Good (suitable for sowing) or Bad (unfit for agriculture),
predicted germination percentage, defect breakdown, and pre-sowing treatment advisory.
"""

from pathlib import Path
import numpy as np
from PIL import Image, ImageStat, ImageFilter


CROP_SEED_STANDARDS = {
    "wheat": {
        "name_en": "Wheat",
        "name_hi": "गेहूं",
        "min_germination_std": 85,
        "ideal_moisture": "10% - 12%",
        "sowing_depth": "4 - 5 cm",
        "seed_rate": "40 - 45 kg / acre",
        "common_defects": [
            "Black point (भ्रूण कालापन)",
            "Karnal bunt / Fungal infection (करनाल बंट)",
            "Weevil / insect damage (घुन या कीट छिद्र)",
            "Shriveled grains (सिकुड़े व कमजोर दाने)"
        ],
        "organic_treatment": "Treat with Trichoderma viride @ 5g/kg seed or Beejamrit (बीजामृत).",
        "chemical_treatment": "Treat with Thiram 75% WP @ 2.5g/kg or Carbendazim 50% WP @ 2g/kg seed.",
    },
    "rice": {
        "name_en": "Rice / Paddy",
        "name_hi": "धान",
        "min_germination_std": 80,
        "ideal_moisture": "12% - 14%",
        "sowing_depth": "2 - 3 cm (Nursery bed)",
        "seed_rate": "15 - 20 kg / acre",
        "common_defects": [
            "False smut (झूठा कंडुआ)",
            "Discolored / spotted husk (भूरे-काले धब्बे)",
            "Chaffy / empty seeds (खोखला धान)",
            "Bakanae fungus infection"
        ],
        "organic_treatment": "Soak seeds in 17% salt solution (remove floating bad seeds), then treat with Pseudomonas fluorescens @ 10g/kg.",
        "chemical_treatment": "Soak in Streptocycline (1g) + Carbendazim (10g) in 10L water for 24 hours.",
    },
    "maize": {
        "name_en": "Maize / Corn",
        "name_hi": "मक्का",
        "min_germination_std": 85,
        "ideal_moisture": "11% - 13%",
        "sowing_depth": "4 - 5 cm",
        "seed_rate": "8 - 10 kg / acre",
        "common_defects": [
            "Seed rot & damping off (सड़न रोग)",
            "Pink / white fungal mold (फफूंद)",
            "Cracked pericarp (टूटा छिलका)",
            "Insect bore holes (कीट छिद्र)"
        ],
        "organic_treatment": "Treat with Trichoderma harzianum @ 6g/kg seed + Azotobacter bio-fertilizer.",
        "chemical_treatment": "Treat with Captan 50% WP or Thiram @ 3g/kg seed.",
    },
    "soybean": {
        "name_en": "Soybean",
        "name_hi": "सोयाबीन",
        "min_germination_std": 70,
        "ideal_moisture": "9% - 11%",
        "sowing_depth": "3 - 4 cm",
        "seed_rate": "25 - 30 kg / acre",
        "common_defects": [
            "Purple seed stain (बैंगनी धब्बा)",
            "Mechanical cracks / damaged coat (टूटा हुआ बीजचोल)",
            "Shriveled & greenish immature seeds (अपरिपक्व दाने)",
            "Anthracnose rot"
        ],
        "organic_treatment": "Inoculate with Rhizobium japonicum @ 5g/kg + Trichoderma viride @ 5g/kg.",
        "chemical_treatment": "Treat with Carboxin 37.5% + Thiram 37.5% DS @ 2.5g/kg seed.",
    },
    "mustard": {
        "name_en": "Mustard / Rapeseed",
        "name_hi": "सरसों / राई",
        "min_germination_std": 85,
        "ideal_moisture": "8% - 9%",
        "sowing_depth": "2 - 3 cm",
        "seed_rate": "1.5 - 2 kg / acre",
        "common_defects": [
            "Alternaria blight spores (झुलसा फफूंद)",
            "Immature / greenish grains (कच्चे दाने)",
            "Shriveled tiny seeds",
            "White rust residue"
        ],
        "organic_treatment": "Treat with Trichoderma viride @ 8g/kg seed.",
        "chemical_treatment": "Treat with Metalaxyl (Apron 35 SD) @ 6g/kg or Mancozeb @ 3g/kg.",
    },
    "gram": {
        "name_en": "Gram / Chickpea",
        "name_hi": "चना",
        "min_germination_std": 85,
        "ideal_moisture": "9% - 11%",
        "sowing_depth": "6 - 8 cm",
        "seed_rate": "30 - 35 kg / acre",
        "common_defects": [
            "Wilt & collar rot spores (उकठा / जड़ सड़न)",
            "Bruchid beetle holes (घुन के गोल छेद)",
            "Wrinkled & broken split cotyledons",
            "Ascochyta blight spots"
        ],
        "organic_treatment": "Treat with Trichoderma @ 5g/kg followed by Rhizobium culture @ 10g/kg.",
        "chemical_treatment": "Treat with Carbendazim (1g) + Thiram (2g) per kg of seed.",
    },
    "cotton": {
        "name_en": "Cotton",
        "name_hi": "कपास",
        "min_germination_std": 65,
        "ideal_moisture": "8% - 10%",
        "sowing_depth": "3 - 5 cm",
        "seed_rate": "2 - 2.5 kg / acre (Hybrids)",
        "common_defects": [
            "Bacterial blight / Black arm",
            "Root rot / fungal mold on fuzz",
            "Immature hollow fuzz seeds",
            "Borer damaged kernels"
        ],
        "organic_treatment": "Delinting if fuzzy, then soak in cow urine/dung solution (Beejamrit) for 2 hours.",
        "chemical_treatment": "Acid delinting + Carboxin (Vitavax) @ 2g/kg + Imidacloprid 70 WS @ 5g/kg.",
    },
    "tomato": {
        "name_en": "Tomato",
        "name_hi": "टमाटर",
        "min_germination_std": 75,
        "ideal_moisture": "7% - 8%",
        "sowing_depth": "0.5 - 1 cm (Pro-tray / Nursery)",
        "seed_rate": "40 - 50 g / acre (Hybrid)",
        "common_defects": [
            "Damping off fungus (आर्द्र गलन)",
            "Darkened / blackened embryo (मृत भ्रूण)",
            "Bacterial canker carrier",
            "Shriveled flat seeds (खाली बीज)"
        ],
        "organic_treatment": "Hot water treatment at 50°C for 25 minutes + Trichoderma @ 5g/kg.",
        "chemical_treatment": "Treat with Captan or Thiram @ 2g/kg seed.",
    },
    "chilli": {
        "name_en": "Chilli / Pepper",
        "name_hi": "मिर्च",
        "min_germination_std": 70,
        "ideal_moisture": "7% - 8%",
        "sowing_depth": "0.5 - 1 cm",
        "seed_rate": "80 - 100 g / acre (Hybrid)",
        "common_defects": [
            "Anthracnose / Die-back transmission",
            "Damping off fungus",
            "Discolored brownish-black seeds",
            "Hollow papery coat"
        ],
        "organic_treatment": "Soak in hot water at 52°C for 15 minutes, then coat with Trichoderma viride.",
        "chemical_treatment": "Treat with Thiram @ 3g/kg or Carbendazim @ 2g/kg seed.",
    },
    "onion": {
        "name_en": "Onion",
        "name_hi": "प्याज",
        "min_germination_std": 70,
        "ideal_moisture": "6% - 8%",
        "sowing_depth": "1 - 2 cm",
        "seed_rate": "3 - 4 kg / acre",
        "common_defects": [
            "Purple blotch carrier",
            "Loss of jet-black luster (भूरापन / चमक हीनता)",
            "Smut spores (कंडुआ)",
            "Old expired dead seeds"
        ],
        "organic_treatment": "Treat with Trichoderma harzianum @ 5g/kg seed.",
        "chemical_treatment": "Treat with Thiram or Captan @ 2.5g/kg seed.",
    },
    "groundnut": {
        "name_en": "Groundnut / Peanut",
        "name_hi": "मूंगफली",
        "min_germination_std": 70,
        "ideal_moisture": "8% - 9%",
        "sowing_depth": "5 - 6 cm",
        "seed_rate": "40 - 50 kg / acre",
        "common_defects": [
            "Aspergillus flavus / Aflatoxin yellow mold",
            "Tikka / collar rot transmission",
            "Split kernels with detached embryo",
            "Shriveled oily rancid seeds"
        ],
        "organic_treatment": "Treat with Trichoderma viride @ 4g/kg seed.",
        "chemical_treatment": "Treat with Mancozeb @ 3g/kg or Carbendazim @ 2g/kg seed.",
    },
    "general": {
        "name_en": "General Agri Seed",
        "name_hi": "सामान्य कृषि बीज",
        "min_germination_std": 80,
        "ideal_moisture": "9% - 12%",
        "sowing_depth": "3 - 5 cm",
        "seed_rate": "As per crop guidelines",
        "common_defects": [
            "Fungal discoloration / Mold (फफूंद)",
            "Insect boreholes (कीट छिद्र)",
            "Broken / cracked seed coat",
            "Shriveled / dead embryo"
        ],
        "organic_treatment": "Perform salt-water float test to discard hollow seeds, treat with Trichoderma viride @ 5g/kg.",
        "chemical_treatment": "Treat with standard seed treatment fungicide (Thiram/Carbendazim @ 2-2.5g/kg).",
    }
}


def get_crop_standard(crop_name):
    """Retrieve agronomic standards for a given crop."""
    key = str(crop_name or "").lower().strip()
    key = key.replace(" ", "_").replace("-", "_")

    for standard_key, data in CROP_SEED_STANDARDS.items():
        if standard_key in key or key in standard_key:
            return standard_key, data

    return "general", CROP_SEED_STANDARDS["general"]


def analyze_seed_image(image_path):
    """
    Perform computer vision metrics extraction on the uploaded seed image:
    1. Brightness & Luster (healthy seeds have good brightness and natural color saturation).
    2. Dark spots / Mold ratio (damaged seeds have abnormal dark necrotic regions or gray-green mold).
    3. Texture irregularity & edge variance (broken, shriveled, or insect-damaged seeds show high noise).
    4. Color health ratio.
    """
    if not image_path or not Path(image_path).exists():
        return {
            "has_image": False,
            "dark_spot_ratio": 0.05,
            "luster_score": 85.0,
            "uniformity_score": 88.0,
            "discoloration_index": 5.0,
            "image_quality_confidence": 75.0,
        }

    try:
        with Image.open(image_path) as img:
            rgb_img = img.convert("RGB")
            
            # Resize for fast processing
            resized = rgb_img.resize((256, 256))
            arr = np.array(resized, dtype=np.float32)

            # 1. Luminance and luster
            grayscale = resized.convert("L")
            gray_arr = np.array(grayscale, dtype=np.float32)
            mean_brightness = float(np.mean(gray_arr))
            std_brightness = float(np.std(gray_arr))

            # 2. Dark/Necrotic/Fungal spot detection
            # Extremely dark pixels compared to background and seed body
            dark_mask = gray_arr < 45
            dark_spot_ratio = float(np.sum(dark_mask) / (256 * 256))

            # 3. Discoloration check (abnormal gray/dark green/black vs warm healthy seed tones)
            r = arr[:, :, 0]
            g = arr[:, :, 1]
            b = arr[:, :, 2]

            # High green/blue excess often indicates mold/mildew or rotting moisture
            mold_suspect = (g > (r + 15)) & (gray_arr > 30)
            mold_ratio = float(np.sum(mold_suspect) / (256 * 256))

            # Discoloration index
            discoloration_index = round((dark_spot_ratio * 100 * 2.5) + (mold_ratio * 100 * 4.0), 2)
            discoloration_index = min(100.0, max(0.0, discoloration_index))

            # 4. Texture edge roughness (wrinkling/cracks) using Laplacian filter
            edges = grayscale.filter(ImageFilter.FIND_EDGES)
            edge_arr = np.array(edges, dtype=np.float32)
            edge_intensity = float(np.mean(edge_arr))

            # Normalized luster (0 - 100)
            luster_score = max(10.0, min(98.0, 100.0 - (discoloration_index * 1.2) - (std_brightness * 0.2)))
            
            # Uniformity score
            uniformity_score = max(15.0, min(96.0, 100.0 - (edge_intensity * 0.8) - (discoloration_index * 0.9)))

            return {
                "has_image": True,
                "mean_brightness": round(mean_brightness, 1),
                "dark_spot_ratio": round(dark_spot_ratio, 3),
                "mold_ratio": round(mold_ratio, 3),
                "discoloration_index": discoloration_index,
                "luster_score": round(luster_score, 1),
                "uniformity_score": round(uniformity_score, 1),
                "image_quality_confidence": round(min(98.0, 80.0 + (mean_brightness * 0.1)), 1),
            }

    except Exception:
        return {
            "has_image": False,
            "dark_spot_ratio": 0.08,
            "luster_score": 80.0,
            "uniformity_score": 82.0,
            "discoloration_index": 10.0,
            "image_quality_confidence": 70.0,
        }


def analyze_seed_quality(
    image_path=None,
    crop_type="Wheat",
    visual_condition="good",      # "good", "dull", "spotted", "shriveled", "damaged"
    has_insect_holes=False,       # True/False
    broken_coat_level="none",     # "none", "few", "high"
    moisture_status="normal",     # "normal", "damp", "musty_smell", "rotten"
    float_test_result="sink",     # "sink" (all sink = good), "few_float", "many_float" (hollow = bad)
):
    """
    Comprehensive multi-parameter seed prediction engine.
    Calculates:
    - Verdict: GOOD (बुवाई योग्य), MODERATE (बीजोपचार आवश्यक), or BAD (कृषि के लिए अनुपयुक्त)
    - Viability Score (%)
    - Physical Purity (%)
    - Specific defects list
    - Step-by-step pre-sowing treatment prescription
    - Agricultural yield impact
    """
    crop_key, crop_info = get_crop_standard(crop_type)

    # 1. Computer vision metrics from image
    cv_data = analyze_seed_image(image_path)

    # Base scores
    base_viability = 94.0
    base_purity = 98.0
    defects = []
    reasons_bad = []
    risk_factors = 0

    # Evaluate CV image signals
    if cv_data["has_image"]:
        disc_index = cv_data["discoloration_index"]
        if disc_index > 25.0:
            base_viability -= (disc_index * 0.8)
            base_purity -= (disc_index * 0.4)
            defects.append("Fungal / dark necrotic discoloration detected on seed surface (फफूंद व काले धब्बे)")
            reasons_bad.append("Visual analysis indicates presence of seed-borne fungal spores or storage rot.")
            risk_factors += 2
        elif disc_index > 12.0:
            base_viability -= 10.0
            base_purity -= 6.0
            defects.append("Mild surface discoloration or loss of natural luster (हल्का बदरंगपन)")
            risk_factors += 1

        if cv_data["uniformity_score"] < 50.0:
            base_viability -= 12.0
            base_purity -= 8.0
            defects.append("Irregular seed contour / wrinkled grain texture (सिकुड़े व असमान दाने)")
            risk_factors += 1

    # Evaluate manual / physical indicators
    if visual_condition == "spotted":
        base_viability -= 22.0
        base_purity -= 15.0
        defects.append("Visible black/brown spots and seed coat discoloration (धब्बेदार दाने)")
        reasons_bad.append("Seeds exhibit visible disease spotting, reducing embryo vitality.")
        risk_factors += 2
    elif visual_condition == "shriveled":
        base_viability -= 28.0
        base_purity -= 18.0
        defects.append("Shriveled, wrinkled & under-developed seeds (सिकुड़े व अविकसित दाने)")
        reasons_bad.append("Shriveled seeds lack sufficient endosperm reserves for strong seedling vigor.")
        risk_factors += 2
    elif visual_condition == "damaged":
        base_viability -= 35.0
        base_purity -= 25.0
        defects.append("Physically damaged, decayed, or deformed seeds (क्षतिग्रस्त व विकृत दाने)")
        reasons_bad.append("High mechanical or fungal destruction to seed embryos.")
        risk_factors += 3
    elif visual_condition == "dull":
        base_viability -= 8.0
        base_purity -= 5.0
        defects.append("Dull surface luster indicating old stock / improper storage (पुरानी चमकहीन फसल)")
        risk_factors += 1

    if has_insect_holes:
        base_viability -= 40.0
        base_purity -= 20.0
        defects.append("Insect / weevil bore holes detected (घुन या कीट द्वारा खाए हुए छेद)")
        reasons_bad.append("Insect boring destroys the germ embryo and hollows the internal seed cotyledon.")
        risk_factors += 3

    if broken_coat_level == "high":
        base_viability -= 25.0
        base_purity -= 18.0
        defects.append("High percentage of split, cracked seed coats (टूटा हुआ बीज आवरण)")
        reasons_bad.append("Cracked seed coats allow soil pathogens to rot the embryo immediately after sowing.")
        risk_factors += 2
    elif broken_coat_level == "few":
        base_viability -= 7.0
        base_purity -= 5.0
        defects.append("Minor seed coat cracks (कुछ टूटे छिलके)")
        risk_factors += 1

    if moisture_status == "rotten":
        base_viability -= 55.0
        base_purity -= 30.0
        defects.append("Damp rot & microbial fermentation smell (सड़न व तीव्र दुर्गंध)")
        reasons_bad.append("Seeds have decayed and lost all germination capacity.")
        risk_factors += 4
    elif moisture_status == "musty_smell":
        base_viability -= 25.0
        base_purity -= 15.0
        defects.append("High moisture & musty fungal odor (सीलन व फफूंद गंध)")
        reasons_bad.append("Excessive moisture in storage promotes internal rotting.")
        risk_factors += 2
    elif moisture_status == "damp":
        base_viability -= 12.0
        defects.append("Slight dampness / excess moisture (हल्की नमी)")
        risk_factors += 1

    if float_test_result == "many_float":
        base_viability -= 45.0
        base_purity -= 30.0
        defects.append("High floatation count in salt water test — hollow/dead seeds (तैरने वाले खोखले बीज)")
        reasons_bad.append("Seeds floating on water are empty husks or internally destroyed.")
        risk_factors += 3
    elif float_test_result == "few_float":
        base_viability -= 14.0
        base_purity -= 8.0
        defects.append("Some floating seeds observed in float test (कुछ खोखले दाने)")
        risk_factors += 1

    # Clamp scores
    viability_score = max(10, min(99, int(round(base_viability))))
    purity_score = max(20, min(99, int(round(base_purity))))

    # Determine Quality Classification
    min_std = crop_info["min_germination_std"]

    if viability_score >= min_std and risk_factors <= 1:
        quality_status = "good"
        is_good = True
        health_rating = "Excellent (उच्चतम गुणवत्ता)" if viability_score >= 90 else "Good (उत्तम गुणवत्ता)"
        risk_level = "Low (कम जोखिम)"
        verdict_summary = (
            f"✅ SEED IS GOOD FOR AGRICULTURE (कृषि हेतु उत्तम एवं बुवाई योग्य):\n"
            f"This seed sample of {crop_info['name_en']} ({crop_info['name_hi']}) meets and exceeds certified agricultural germination standards. "
            f"Predicted germination viability is {viability_score}% (Minimum govt. standard is {min_std}%). "
            f"Seed coats are healthy with intact embryos, ensuring vigorous sprout emergence and strong root establishment."
        )
        yield_impact = "Expected Normal to Bumper Yield (95% - 100% capacity) with optimal field management."
    
    elif viability_score >= (min_std - 15) and risk_factors <= 3:
        quality_status = "moderate"
        is_good = True
        health_rating = "Moderate / Fair (मध्यम गुणवत्ता - शोधन आवश्यक)"
        risk_level = "Medium (मध्यम जोखिम)"
        verdict_summary = (
            f"⚠️ SEED IS MODERATE — REQUIRES MANDATORY SEED TREATMENT (बीजोपचार के उपरांत ही बुवाई करें):\n"
            f"This seed sample of {crop_info['name_en']} has an estimated viability of {viability_score}% "
            f"(near the standard {min_std}%). While mostly viable, minor surface pathogens or weak grains were noted. "
            f"Direct sowing without treatment poses a risk of seed rot or damping off. "
            f"Perform salt-water float grading to discard light seeds, followed by the recommended biological/fungicide seed coating before sowing."
        )
        yield_impact = "Acceptable yield if treated (80% - 90% capacity). May suffer 15-25% germination gaps if sown untreated."
    
    else:
        quality_status = "bad"
        is_good = False
        health_rating = "Bad / Unfit for Agriculture (खराब बीज - अनुपयुक्त)"
        risk_level = "High / Critical (अत्यधिक जोखिम)"
        reasons_text = " ".join(reasons_bad) if reasons_bad else "Severe loss of embryo viability and heavy defect infestation."
        verdict_summary = (
            f"❌ SEED IS BAD / NOT SUITABLE FOR AGRICULTURE (कृषि के लिए अनुपयुक्त - बुवाई कदापि न करें):\n"
            f"This seed sample of {crop_info['name_en']} ({crop_info['name_hi']}) FAILED agricultural suitability tests. "
            f"Predicted germination viability is only {viability_score}%, which is far below the safe minimum standard of {min_std}%. "
            f"{reasons_text} Sowing this seed will lead to extensive germination failure, weak stunted seedlings, and severe economic loss."
        )
        yield_impact = "Severe Crop Failure Risk (Estimated 40% - 70% yield loss or total stand failure)."

    if not defects:
        defects = ["No significant defects observed. Seeds are plump, lustrous, and physically intact."]

    # Step-by-step Treatment advisory
    if is_good or quality_status == "moderate":
        treatment_steps = (
            f"🌱 1. Floatation Grading (बीज सफाई):\n"
            f"   Mix 100g salt in 1 liter water. Pour seeds into the water. Remove and discard all floating seeds (dead/hollow seeds). "
            f"   Rinse the settled healthy seeds with clean water.\n\n"
            f"🌿 2. Organic / Biological Treatment (जैविक बीजोपचार):\n"
            f"   {crop_info['organic_treatment']}\n\n"
            f"🧪 3. Chemical Fungicide Coating (रासायनिक फफूंदनाशक शोधन):\n"
            f"   {crop_info['chemical_treatment']}\n\n"
            f"☀️ 4. Drying Instruction:\n"
            f"   Spread treated seeds on a clean cloth in shade for 30-45 minutes before sowing. Never dry treated seeds under direct scorching sunlight."
        )
    else:
        treatment_steps = (
            f"🚫 DO NOT USE FOR SOWING IN AGRICULTURAL FIELDS:\n"
            f"1. Replace this seed batch with fresh certified seeds (प्रमाणित बीज) from a recognized agricultural cooperative or authorized seed center.\n"
            f"2. If non-toxic and untreated with chemicals, evaluate if it can be utilized for cattle feed or organic compost.\n"
            f"3. Always check certified seed tags (Blue tag / White tag) and expiry date before purchasing future seed stock."
        )

    sowing_guide = (
        f"🌾 Sowing Depth: {crop_info['sowing_depth']} | Ideal Seed Rate: {crop_info['seed_rate']}\n"
        f"💧 Safe Storage Moisture: {crop_info['ideal_moisture']}\n"
        f"🌱 Govt. Minimum Viability Standard: {min_std}%"
    )

    return {
        "crop_name_en": crop_info["name_en"],
        "crop_name_hi": crop_info["name_hi"],
        "quality_status": quality_status,
        "is_good_for_agriculture": is_good,
        "viability_score": viability_score,
        "purity_score": purity_score,
        "health_rating": health_rating,
        "risk_level": risk_level,
        "defects_detected": defects,
        "suitability_verdict": verdict_summary,
        "treatment_advisory": treatment_steps,
        "sowing_guidelines": sowing_guide,
        "yield_impact": yield_impact,
        "cv_metrics": cv_data,
        "min_germination_std": min_std,
    }
