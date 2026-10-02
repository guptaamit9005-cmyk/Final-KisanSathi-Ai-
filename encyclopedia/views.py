import json
from django.shortcuts import render

# ============================================================
# CROP ROADMAPS WITH DETAILED SCIENTIFIC & PRACTICAL GUIDES
# ============================================================

LEARNING_ROADMAPS = [
    {
        "id": "wheat",
        "crop": "Wheat",
        "hindi_name": "गेहूं",
        "title": "Modern Wheat Cultivation Roadmap",
        "icon": "🌾",
        "level": "All Farmers",
        "duration": "18-20 Weeks",
        "season": "Rabi (Oct - April)",
        "ideal_temp": "15°C - 24°C",
        "water_req": "4-6 Irrigations (Critical Stages)",
        "description": "Comprehensive guide for high-yield wheat production, covering zero-tillage sowing, crown root irrigation, rust disease management, and terminal heat protection.",
        "steps": [
            {
                "stage_num": 1,
                "title": "Seed Selection & Seed Treatment (बीज चयन एवं उपचार)",
                "icon": "🌱",
                "days": "Day 0 - 5",
                "description": "Select high-yielding certified seeds (e.g., HD-2967, HD-3086, DBW-187, DBW-303). Treat seeds with Carboxin + Thiram (2g/kg) and Azotobacter bio-fertilizer to prevent loose smut and root rot.",
                "modern": [
                    "Perform seed germination test: Ensure >85% germination before sowing.",
                    "Treat with Trichoderma viride (4g/kg) for organic root protection.",
                    "Seed rate: 100 kg/ha for timely sowing, 125 kg/ha for late sowing."
                ],
                "do_dont": {
                    "do": "Incorporate seed drill calibration for uniform 4-5 cm depth.",
                    "dont": "Do not sow untreated loose seeds from previous uncertified stock."
                }
            },
            {
                "stage_num": 2,
                "title": "Zero-Tillage Field Preparation (खेत की आधुनिक तैयारी)",
                "icon": "🚜",
                "days": "Day 5 - 10",
                "description": "Use Happy Seeder or Super Seeder directly into standing paddy stubble. This saves ₹2,500/acre in diesel and retains soil moisture while stopping stubble burning.",
                "modern": [
                    "Laser land leveling saves 25% irrigation water and guarantees uniform crop stand.",
                    "Apply basal dose: 50 kg DAP + 25 kg MOP + 10 kg Zinc Sulphate (21%) per acre.",
                    "Maintain soil moisture at sowing to ensure rapid, uniform emergence."
                ],
                "do_dont": {
                    "do": "Retain paddy straw mulch on topsoil for temperature moderation.",
                    "dont": "Avoid excessive rotavator tilling which pulverizes soil structure."
                }
            },
            {
                "stage_num": 3,
                "title": "Crown Root Initiation (CRI) & 1st Irrigation (CRI सिंचाई)",
                "icon": "💧",
                "days": "Day 20 - 25",
                "description": "The CRI stage is the MOST CRITICAL growth phase in wheat. Roots transition from seminal to nodal crown roots that anchor the plant and feed tillers.",
                "modern": [
                    "Apply 1st irrigation strictly between 20-25 days after sowing (DAS).",
                    "Delaying CRI irrigation by even 1 week reduces yield by 5-10 quintals/ha.",
                    "Top-dress 1st split of Urea (35-40 kg/acre) with Neem coating right after irrigation."
                ],
                "do_dont": {
                    "do": "Irrigate gently without waterlogging the crown roots.",
                    "dont": "Never miss or delay this irrigation under any circumstances."
                }
            },
            {
                "stage_num": 4,
                "title": "Active Tillering & Weed Management (कल्ले फूटना व खरपतवार नियंत्रण)",
                "icon": "🌿",
                "days": "Day 35 - 50",
                "description": "Maximum tiller emergence occurs. Control narrow-leaved weeds (Phalaris minor / Mandusi) and broad-leaved weeds before they choke young tillers.",
                "modern": [
                    "Spray Clodinafop-propargyl (60g/ha) for Mandusi or Sulfosulfuron for mixed weeds.",
                    "Spray during sunny hours when weed leaves are active (30-35 DAS).",
                    "Apply micronutrient foliar spray: 0.5% Zinc Sulphate + 2.5% Urea solution."
                ],
                "do_dont": {
                    "do": "Use flat fan or flood jet nozzle with 150 liters water per acre.",
                    "dont": "Avoid spraying weedicides during high wind or cold frosty mornings."
                }
            },
            {
                "stage_num": 5,
                "title": "Jointing & Booting Stage (गांठ बनना व गोभ अवस्था)",
                "icon": "🌾",
                "days": "Day 60 - 80",
                "description": "The stem elongates and earhead forms inside the flag leaf. Nutrient and water demand peaks as the prospective spikelet count is finalized.",
                "modern": [
                    "Provide 3rd irrigation at late jointing/booting stage.",
                    "Foliar spray of 0:52:34 (Monopotassium Phosphate @ 1 kg/acre) boosts spike size.",
                    "Scout for Yellow Rust (पीला रतुआ) stripe symptoms on lower leaves."
                ],
                "do_dont": {
                    "do": "Inspect flag leaves for yellowish powder pustules every 3 days.",
                    "dont": "Do not over-apply nitrogenous urea at this stage to prevent lodging."
                }
            },
            {
                "stage_num": 6,
                "title": "Flowering, Milking & Dough Stage (पुष्पन व दाना भराव)",
                "icon": "☀️",
                "days": "Day 90 - 115",
                "description": "Grain development stage where photosynthetic sugars are transferred to kernels. High March temperatures (terminal heat) can cause shriveled grain.",
                "modern": [
                    "Spray 1% Potassium Nitrate (13:0:45) to protect against terminal heat stress.",
                    "Light irrigation during calm weather (avoid windy days to prevent crop lodging).",
                    "Keep soil moist until grain enters the hard dough stage."
                ],
                "do_dont": {
                    "do": "Spray preventive Propiconazole 25% EC (1ml/L) if rust is reported in region.",
                    "dont": "Never irrigate on gusty windy days as top-heavy wheat stalks will lodge."
                }
            },
            {
                "stage_num": 7,
                "title": "Physiological Maturity & Combine Harvesting (कटाई व भंडारण)",
                "icon": "🚜",
                "days": "Day 125 - 145",
                "description": "Harvest when straw turns golden yellow and grain moisture drops below 12-14%. Clean combine harvesters reduce shattering losses.",
                "modern": [
                    "Test kernel moisture: Grain should make a sharp cracking sound between teeth.",
                    "Store in hermetic grain bags or GI bins treated with Celphos / Neem leaves.",
                    "Combine harvester with SMS (Straw Management System) prepares field for Zaid crops."
                ],
                "do_dont": {
                    "do": "Dry grain in sun for 2 days to reach <12% moisture before hermetic storage.",
                    "dont": "Never pack moist wheat in plastic sacks as fungus will develop aflatoxins."
                }
            }
        ]
    },

    {
        "id": "rice",
        "crop": "Rice (Paddy)",
        "hindi_name": "धान",
        "title": "Smart Paddy Cultivation Roadmap",
        "icon": "🌾",
        "level": "All Farmers",
        "duration": "16-18 Weeks",
        "season": "Kharif (June - Nov)",
        "ideal_temp": "22°C - 32°C",
        "water_req": "AWD (Alternate Wetting & Drying)",
        "description": "Learn cutting-edge Direct Seeded Rice (DSR), water-saving AWD techniques, blast and stem borer bio-management, and high-quality basmati production.",
        "steps": [
            {
                "stage_num": 1,
                "title": "Quality Nursery / DSR Sowing (नर्सरी या सीधी बिजाई)",
                "icon": "🌱",
                "days": "Day 0 - 25",
                "description": "Select salt-tolerant or high-yield varieties (PR-126, Pusa Basmati 1509, MTU-1010). Direct Seeded Rice (DSR) with tar-wattar technique saves 30% water and eliminates nursery transplanting labor.",
                "modern": [
                    "Treat seed with Carbendazim (2g/kg) + Streptocycline (1g/10kg) to stop Bacterial Leaf Blight.",
                    "For nursery: Maintain 1 meter wide raised nursery beds with organic vermicompost.",
                    "Transplant young seedlings at 21-25 days stage with 2-3 seedlings per hill."
                ],
                "do_dont": {
                    "do": "Maintain 20cm x 15cm spacing for optimal air circulation and solar interception.",
                    "dont": "Do not transplant over-aged (>30 days) seedlings as tillering capacity collapses."
                }
            },
            {
                "stage_num": 2,
                "title": "Water-Saving AWD & Root Aeration (वैकल्पिक सिंचाई - AWD)",
                "icon": "💧",
                "days": "Day 25 - 55",
                "description": "Instead of continuous 5cm water stagnation, implement Alternate Wetting and Drying (AWD) using a perforated field water pipe. Re-irrigate only when water drops 15cm below soil surface.",
                "modern": [
                    "AWD reduces greenhouse methane emissions by 40% and diesel pumping cost by 35%.",
                    "Allows oxygen penetration to roots, promoting deep anchoring and strong tillers.",
                    "Apply second dose of Nitrogen along with 5 kg Zinc-EDTA (12%) per acre."
                ],
                "do_dont": {
                    "do": "Keep field flooded only during flowering; use AWD in vegetative stages.",
                    "dont": "Avoid continuous deep water stagnation that breeds anaerobic root decay."
                }
            },
            {
                "stage_num": 3,
                "title": "Panicle Initiation & Stem Borer Defense (बाली निकलना व कीट प्रबंधन)",
                "icon": "🔍",
                "days": "Day 60 - 80",
                "description": "Panicle initiation marks transition from vegetative to reproductive phase. Protect against Yellow Stem Borer (Dead Heart / White Earhead) and Brown Planthopper (BPH).",
                "modern": [
                    "Install 4-5 Pheromone Traps per acre with Scirpophaga incertulas lures.",
                    "Release Trichogramma japonicum egg parasitoid cards (1 Lakh/ha) for bio-control.",
                    "If BPH exceeds ETL (5-10 insects/hill), spray Pymetrozine 50% WDG or Triflumezopyrim."
                ],
                "do_dont": {
                    "do": "Create 1-foot alley pathways (allies) every 10 rows for spray movement and aeration.",
                    "dont": "Avoid synthetic pyrethroid sprays as they destroy natural spider predators."
                }
            },
            {
                "stage_num": 4,
                "title": "Grain Filling & Blast Shield (दूधिया अवस्था व झुलसा नियंत्रण)",
                "icon": "🛡️",
                "days": "Day 85 - 110",
                "description": "Flowering and milk stage. Guard against Neck Blast (गर्दन तोड़) and Sheath Blight which can damage the entire earhead overnight during humid foggy weather.",
                "modern": [
                    "Foliar spray of Tricyclazole 75% WP (0.6g/L) or Azoxystrobin + Difenoconazole at boot leaf stage.",
                    "Maintain 2-3 cm shallow water film during pollen anthesis.",
                    "Foliar spray of 0:0:50 (Potassium Sulphate @ 1kg/acre) promotes lustrous bold grains."
                ],
                "do_dont": {
                    "do": "Drain standing water 10-12 days before anticipated harvest date.",
                    "dont": "Do not spray toxic chemicals within 20 days of harvest (maintain pre-harvest interval)."
                }
            },
            {
                "stage_num": 5,
                "title": "Harvesting & Moisture Management (कटाई एवं भंडारण)",
                "icon": "🌾",
                "days": "Day 115 - 130",
                "description": "Harvest when 80-85% grains on panicles turn golden straw color. Timely harvesting prevents kernel cracking during milling.",
                "modern": [
                    "Optimal harvest moisture is 20-22%; dry gently in shade to 14% for long storage.",
                    "Use modern combine harvesters equipped with straw chopper.",
                    "Store in moisture-proof polypropylene bags placed on wooden pallets."
                ],
                "do_dont": {
                    "do": "Maintain clean, rat-proof, fumigated storage godowns.",
                    "dont": "Never burn residual paddy straw — incorporate with Super Seeder for soil carbon."
                }
            }
        ]
    },

    {
        "id": "tomato",
        "crop": "Tomato",
        "hindi_name": "टमाटर",
        "title": "High-Tech Tomato Cultivation Guide",
        "icon": "🍅",
        "level": "Intermediate",
        "duration": "14-16 Weeks",
        "season": "Kharif, Rabi, Zaid",
        "ideal_temp": "18°C - 27°C",
        "water_req": "Drip Irrigation + Fertigation",
        "description": "Learn protected cultivation, determinate vs indeterminate staking, drip fertigation schedules, and integrated control of Early/Late Blight and Leaf Curl Virus.",
        "steps": [
            {
                "stage_num": 1,
                "title": "Pro-Tray Nursery & Net House Raising (प्रो-ट्रे में पौध तैयार करना)",
                "icon": "🌱",
                "days": "Day 0 - 25",
                "description": "Raise hybrid seeds (e.g., Abhinav, US-440, Saaho, Arka Rakshak) in 98-cell pro-trays using sterilized cocopeat, vermiculite, and perlite mixture under a 40-mesh insect net.",
                "modern": [
                    "Protected nursery prevents Whitefly transmission of incurable Tomato Leaf Curl Virus.",
                    "Drench seedlings with Trichoderma harzianum to prevent Damping Off (आर्द्र गलन).",
                    "Harden seedlings 3-4 days before field transplanting by withholding water."
                ],
                "do_dont": {
                    "do": "Transplant stocky 4-5 leaf healthy seedlings in late evening.",
                    "dont": "Do not pull bare root seedlings forcefully from muddy beds."
                }
            },
            {
                "stage_num": 2,
                "title": "Raised Bed, Silver-Black Mulch & Drip Setup (मल्चिंग व ड्रिप)",
                "icon": "💧",
                "days": "Day 25 - 35",
                "description": "Prepare 90cm wide raised beds with inline drip tubing (16mm, 40cm emitter spacing). Install 25-micron silver-black plastic mulch to suppress weeds and conserve 45% moisture.",
                "modern": [
                    "Silver surface reflects sunlight, disorienting aphids, thrips, and whiteflies.",
                    "Black underside blocks 100% sunlight, completely eliminating weeds without herbicides.",
                    "Saves ₹6,000/acre in weeding labor and increases soil warmth in winter."
                ],
                "do_dont": {
                    "do": "Make transplant holes with a hot pipe cutter at 50cm plant-to-plant spacing.",
                    "dont": "Never puncture drip pipes while punching mulch holes."
                }
            },
            {
                "stage_num": 3,
                "title": "Trellising / Staking & Pruning (तार-बांस बंधाई व छंटाई)",
                "icon": "🎋",
                "days": "Day 40 - 65",
                "description": "Erect bamboo poles and GI wire trellis system. Support indeterminate hybrid plants with plastic twine strings to keep fruits off the ground.",
                "modern": [
                    "Increases Grade-A marketable fruit yield by 35% through sun exposure.",
                    "Eliminates soil-borne fungal contact and fruit rot diseases.",
                    "Prune bottom suckers (side shoots) up to 20cm height for maximum canopy airflow."
                ],
                "do_dont": {
                    "do": "Tie vines loosely in an '8' loop shape to prevent stem girdling.",
                    "dont": "Do not let foliage touch wet soil or irrigation water."
                }
            },
            {
                "stage_num": 4,
                "title": "Precision Fertigation & Flower Boost (ड्रिप से खाद व पुष्पन)",
                "icon": "🧪",
                "days": "Day 50 - 90",
                "description": "Inject water-soluble fertilizers directly into drip lines: 19:19:19 during vegetative phase; 12:61:00 during flowering; and 13:0:45 + Calcium Nitrate during fruit swelling.",
                "modern": [
                    "Calcium Nitrate + Boron foliar spray prevents Blossom End Rot (काली तली रोग) and fruit cracking.",
                    "Spray Planofix (Alpha NAA @ 1ml/4.5L water) to arrest flower and bud drop in hot winds.",
                    "Release bumblebees or manually shake trellis wires at 10 AM to optimize pollination."
                ],
                "do_dont": {
                    "do": "Maintain continuous uniform soil moisture to prevent blossom end rot.",
                    "dont": "Avoid sudden water shocks after dry periods as fruits will crack open."
                }
            },
            {
                "stage_num": 5,
                "title": "Integrated Pest & Blight Defense (रोग व कीट सुरक्षा)",
                "icon": "🔍",
                "days": "Day 60 - 110",
                "description": "Scout for Tuta absoluta (Pinworm leaf miner) and Fruit Borer (Helicoverpa armigera). Spray bio-pesticides or targeted safe chemistries.",
                "modern": [
                    "Install 15 Yellow Sticky Traps/acre for Whitefly and 10 Blue Traps for Thrips.",
                    "For Early/Late Blight: Alternately spray Mancozeb 75% WP and Cymoxanil + Mancozeb.",
                    "For Fruit Borer: Spray Coragen (Chlorantraniliprole 18.5% SC @ 0.3ml/L)."
                ],
                "do_dont": {
                    "do": "Pluck and bury all bored and infected fruits immediately.",
                    "dont": "Do not spray insecticides while honeybees and pollinators are actively foraging."
                }
            },
            {
                "stage_num": 6,
                "title": "Graded Picking & Cold Chain Dispatch (तुड़ाई व विपणन)",
                "icon": "📦",
                "days": "Day 80 - 120",
                "description": "Pick fruits at 'Breaker stage' (pink tinge at blossom end) for distant mandi transport; pick at 'Full Red Ripe stage' for local processing and daily retail.",
                "modern": [
                    "Use ventilated plastic crates (20 kg) instead of rough wooden boxes or gunny sacks.",
                    "Pre-cool fruits in shaded packhouse at 12°C - 15°C to double shelf life.",
                    "Grade into Premium (A), Medium (B), and Small (C) for 20% higher market realization."
                ],
                "do_dont": {
                    "do": "Harvest in early morning or late evening when fruits are cool.",
                    "dont": "Never drop or toss fruits into crates as internal bruising triggers rot."
                }
            }
        ]
    },

    {
        "id": "potato",
        "crop": "Potato",
        "hindi_name": "आलू",
        "title": "Commercial Potato Farming Roadmap",
        "icon": "🥔",
        "level": "Intermediate",
        "duration": "12-14 Weeks",
        "season": "Rabi (Oct - Feb)",
        "ideal_temp": "15°C - 20°C (Tuberization)",
        "water_req": "Sprinkler / Furrow (Light & Frequent)",
        "description": "Master seed tuber cut treatment, automatic ridge sowing, earthing-up, late blight forecasting, dehaulming, and cold store curing for maximum tuber tonnage.",
        "steps": [
            {
                "stage_num": 1,
                "title": "Certified Seed Tubers & Sprouting (बीज कंद चयन व अंकुरण)",
                "icon": "🌱",
                "days": "Day 0 - 10",
                "description": "Procure certified seed tubers (Kufri Pukhraj, Kufri Jyoti, Kufri Chipsona). Seed cost is 40% of total cultivation expenditure.",
                "modern": [
                    "Break tuber dormancy and initiate green sprouting under diffused indirect light.",
                    "Tuber cut piece weight should be 40-50 grams with at least 2-3 prominent eyes.",
                    "Treat cut tubers with Mancozeb (2.5g/L) to prevent black scurf and rotting in soil."
                ],
                "do_dont": {
                    "do": "Suberin curing: Dry cut seed tubers in shade for 24-48 hours before planting.",
                    "dont": "Never plant freshly cut wet tubers directly into wet, cold soil."
                }
            },
            {
                "stage_num": 2,
                "title": "Automatic Ridge Planting & Fertilizer Placement (मेड़ बुवाई)",
                "icon": "🚜",
                "days": "Day 10 - 15",
                "description": "Plant with automatic potato planter on ridges spaced 60cm apart with 20cm tuber-to-tuber distance at 7-8cm depth.",
                "modern": [
                    "Apply full P & K and 50% N at planting time in bands 5cm away from seed tubers.",
                    "Apply 25 kg Zinc Sulphate and 10 kg Sulphur per acre for crisp skin quality.",
                    "Apply pre-emergence herbicide Metribuzin (70% WP @ 200g/acre) within 3 days of sowing."
                ],
                "do_dont": {
                    "do": "Ensure loose, well-drained friable sandy-loam soil bed.",
                    "dont": "Avoid heavy clay or waterlogging soils where tubers suffocate."
                }
            },
            {
                "stage_num": 3,
                "title": "Earthing-Up & Stolon Formation (मिट्टी चढ़ाना व कंद बनना)",
                "icon": "⛰️",
                "days": "Day 30 - 45",
                "description": "Earthing-up (मिट्टी चढ़ाना) is essential at 30-35 DAS when plants are 15-20cm tall. It covers emerging stolons and prevents tubers from turning green due to sun exposure.",
                "modern": [
                    "Top-dress remaining 50% Nitrogen urea before earthing-up.",
                    "Tubers exposed to sunlight produce toxic solanine (green skin), making them unsellable.",
                    "Irrigate immediately after earthing-up using sprinkler or light furrow flow."
                ],
                "do_dont": {
                    "do": "Build wide, broad flat ridges so tubers have maximum expansion room.",
                    "dont": "Do not let furrow water submerge ridge tops."
                }
            },
            {
                "stage_num": 4,
                "title": "Late Blight Alert & Tuber Bulking (पिछेती झुलसा से बचाव)",
                "icon": "🛡️",
                "days": "Day 50 - 75",
                "description": "Tuber bulking peaks. Humid, cloudy weather with night temperatures 10-15°C triggers devastating Late Blight (Phytophthora infestans).",
                "modern": [
                    "Prophylactic spray of Mancozeb 75% WP (2.5g/L) before disease onset.",
                    "If water-soaked dark leaf lesions appear, spray Curzate (Cymoxanil + Mancozeb @ 3g/L).",
                    "Foliar spray of 0:0:50 (Potassium Sulphate) to accelerate starch accumulation in tubers."
                ],
                "do_dont": {
                    "do": "Spray underside of leaves where blight spores multiply rapidly.",
                    "dont": "Avoid excessive nitrogen late in season which delays tuber maturity."
                }
            },
            {
                "stage_num": 5,
                "title": "Dehaulming, Curing & Digging (बेल काटना व खुदाई)",
                "icon": "🥔",
                "days": "Day 80 - 100",
                "description": "Dehaulming (cutting green foliage tops 10-15 days before harvest) hardens the potato skin, preventing skin peeling during digger operation and transit.",
                "modern": [
                    "Cut haulms at ground level or spray Paraquat 10 days before scheduled digging.",
                    "Withhold irrigation after dehaulming to allow tuber skin suberization.",
                    "Harvest using tractor-operated potato digger elevator on dry sunny days."
                ],
                "do_dont": {
                    "do": "Cure tubers in heap covered with straw in dark ventilated shed for 10 days.",
                    "dont": "Do not leave dug potatoes exposed to hot sun for more than 2 hours."
                }
            }
        ]
    },

    {
        "id": "maize",
        "crop": "Maize (Corn)",
        "hindi_name": "मक्का",
        "title": "High-Yield Maize Production Guide",
        "icon": "🌽",
        "level": "Beginner",
        "duration": "14-16 Weeks",
        "season": "Kharif, Rabi, Spring",
        "ideal_temp": "21°C - 30°C",
        "water_req": "4-5 Critical Stage Irrigations",
        "description": "Complete agronomic guide for grain corn and sweet corn, focusing on single-cross hybrids, Fall Armyworm (FAW) management, knee-high top-dressing, and tassel protection.",
        "steps": [
            {
                "stage_num": 1,
                "title": "Single-Cross Hybrid Sowing (संकर बीज बुवाई)",
                "icon": "🌱",
                "days": "Day 0 - 10",
                "description": "Plant high-yielding single-cross hybrids (Pioneer P3396, DKC 9108, Syngenta NK6240). Treat seed with Fortenza Duo (Cyantraniliprole) to provide 21-day protection against Fall Armyworm.",
                "modern": [
                    "Plant on ridges spaced 60cm apart with 20cm plant spacing (28,000 plants/acre).",
                    "Apply Atrazine 50% WP (1 kg/acre) pre-emergence within 48 hours of sowing.",
                    "Soil test: Apply 50 kg DAP + 30 kg MOP + 10 kg Zinc per acre as basal."
                ],
                "do_dont": {
                    "do": "Sow at uniform 4 cm depth for rapid coleoptile emergence.",
                    "dont": "Do not sow flat broadcast as weed management and intercultural operations become impossible."
                }
            },
            {
                "stage_num": 2,
                "title": "Knee-High Stage & Fall Armyworm Defense (घुटने बराबर अवस्था)",
                "icon": "🔍",
                "days": "Day 25 - 40",
                "description": "At knee-high stage (V6), maize enters rapid vegetative elongation. Inspect whorls for Fall Armyworm (FAW - Spodoptera frugiperda) pin-holes and sawdust-like frass.",
                "modern": [
                    "Apply 2nd split of Urea (40 kg/acre) placed 10cm away from stalk base.",
                    "For FAW: Drop neem cake powder + sand mixture into leaf whorls as bio-deterrent.",
                    "If larvae found: Direct spray of Spinetoram 11.7% SC (0.5ml/L) or Emamectin Benzoate into the whorls."
                ],
                "do_dont": {
                    "do": "Direct nozzle directly inside leaf whorls where FAW caterpillars hide.",
                    "dont": "Avoid spraying broad surface mist without penetrating the inner whorl."
                }
            },
            {
                "stage_num": 3,
                "title": "Tasseling & Silking Stage (नर व मादा फूल निकलना)",
                "icon": "🌽",
                "days": "Day 50 - 70",
                "description": "The tassel (male flower) sheds pollen which falls on the silk (female flower). Water stress at silking causes blank or poorly filled cobs.",
                "modern": [
                    "Critical irrigation window: Maintain good soil moisture throughout pollination.",
                    "Apply final top-dressing of Urea (25 kg/acre) at pre-tasseling stage.",
                    "Foliar spray of 13:0:45 (1 kg/acre) enhances cob length and girth."
                ],
                "do_dont": {
                    "do": "Ensure adequate water supply during the 10 days of active pollen shed.",
                    "dont": "Do not let field dry out during silking; even 2 days of drought reduces yield by 30%."
                }
            },
            {
                "stage_num": 4,
                "title": "Grain Milking, Dent & Black Layer (दाना भराव व पकना)",
                "icon": "☀️",
                "days": "Day 75 - 105",
                "description": "Kernels transition from blister stage to milky fluid, then to firm dough (dent stage). Physiological maturity occurs when a black layer forms at the base of the kernel.",
                "modern": [
                    "Check black layer: Detach kernel from cob; look for black abscission layer at base.",
                    "Outer husk turns dry paper-white while leaves begin natural yellow senescence.",
                    "Moisture drops from 35% at black layer to 18-20% at harvest."
                ],
                "do_dont": {
                    "do": "Harvest when cob husks are completely bleached and dry.",
                    "dont": "Do not shell grain at >20% moisture as kernels will get mechanically crushed."
                }
            }
        ]
    }
]

# ============================================================
# MODERN SMART FARMING TOPICS
# ============================================================

MODERN_MODULES = [
    {
        "id": "precision_drip",
        "title": "Precision Drip Irrigation & Smart Fertigation",
        "hindi_title": "ड्रिप सिंचाई एवं स्वचालित फर्टीगेशन",
        "icon": "💧",
        "badge": "Water Saving 50%",
        "summary": "Save up to 50% water while boosting crop yields by 30% using automated drip tubes, venturi injectors, and soil tensiometers.",
        "points": [
            "Inline 16mm pressure-compensating drip pipes deliver water drop-by-drop directly to the root rhizosphere.",
            "Venturi fertigation systems dissolve 100% water-soluble fertilizers (19:19:19, 0:52:34), reducing chemical waste by 40%.",
            "Soil tensiometers guide irrigation scheduling by reading exact root suction pressure in centibars."
        ]
    },
    {
        "id": "ai_drone_monitoring",
        "title": "Agri Drones & AI Crop Health Diagnostics",
        "hindi_title": "कृषि ड्रोन एवं एआई फसल जांच",
        "icon": "🛸",
        "badge": "Fast Coverage",
        "summary": "Cover 10 acres in 20 minutes with micronized drone spraying, multi-spectral NDVI health scanning, and early disease alerts.",
        "points": [
            "Electrostatic drone nozzles spray ultra-fine 100-micron droplets with uniform canopy penetration and zero pesticide wastage.",
            "Multi-spectral cameras calculate NDVI (Normalized Difference Vegetation Index) to detect nitrogen deficiency and water stress 7 days before visible symptoms.",
            "KisanSathi AI image diagnosis enables instant leaf disease classification from smart phone cameras."
        ]
    },
    {
        "id": "natural_soil_regenerative",
        "title": "Regenerative Natural Farming & Soil Microbiome",
        "hindi_title": "प्राकृतिक खेती एवं मृदा जीवाणु संवर्धन",
        "icon": "🌱",
        "badge": "Zero Chemical Input",
        "summary": "Revitalize exhausted soils using Jeevamrutha, Ghana-Jeevamrutha, living mulch, and multi-layer agro-forestry.",
        "points": [
            "Desi cow dung and urine microbial cultures (Jeevamrutha) multiply millions of beneficial nitrogen-fixing and phosphate-solubilizing microbes.",
            "Live green mulching (Sunhemp / Dhaincha) increases organic carbon from 0.4% to 1.2% in 3 years.",
            "Trap cropping with marigold and castor attracts bollworms and nematodes away from main cash crops."
        ]
    },
    {
        "id": "polyhouse_protected",
        "title": "Protected Polyhouse & Shade Net Farming",
        "hindi_title": "पॉलीहाउस एवं संरक्षित खेती",
        "icon": "🏡",
        "badge": "High ROI",
        "summary": "Achieve 4x to 5x higher output per acre by growing off-season bell peppers, seedless cucumbers, and exotic vegetables.",
        "points": [
            "Naturally ventilated polyhouses with UV-stabilized 200-micron polyethylene shield crops from torrential unseasonal rains and hail.",
            "Foggers and shade net screens modulate ambient microclimate, lowering summer greenhouse temperatures by 6-8°C.",
            "Eliminates viral vectors (whiteflies, thrips) via 40-mesh insect-proof side netting."
        ]
    }
]

# ============================================================
# 3D MODEL ANATOMY HOTSPOTS METADATA
# ============================================================

HOTSPOTS_3D = [
    {
        "id": "leaf_canopy",
        "title": "Leaf Canopy & Photosynthesis (पत्तियां एवं प्रकाश संश्लेषण)",
        "pos": [0, 2.6, 0.4],
        "info": "Leaves absorb sunlight and atmospheric CO2 through stomata. Healthy green leaves produce starches that feed developing grains. Maintain balanced Nitrogen and spray micronutrients during active vegetative growth.",
        "icon": "🍃"
    },
    {
        "id": "stem_vascular",
        "title": "Stem Vascular System - Xylem & Phloem (तना एवं रस वाहिकाएं)",
        "pos": [0, 1.4, 0],
        "info": "The plant stem houses xylem (which pumps water and minerals upward from roots) and phloem (which circulates photosynthetic sugars). Staking and silica nutrition keep stems sturdy against wind lodging.",
        "icon": "🎋"
    },
    {
        "id": "flower_panicle",
        "title": "Flower & Grain Spikelet (पुष्प एवं बाली)",
        "pos": [0, 3.2, 0],
        "info": "The reproductive center where pollen fertilizes the ovary to generate grains/fruits. Sensitive to heat stress (>35°C) and water deficits. Spray Potassium Nitrate (13:0:45) at booting for maximum grain weight.",
        "icon": "🌾"
    },
    {
        "id": "root_rhizosphere",
        "title": "Root Network & Rhizosphere (जड़ तंत्र एवं मिट्टी)",
        "pos": [0, 0.2, 0],
        "info": "Deep taproots and fibrous lateral roots anchor the plant and absorb moisture. Mycorrhizal fungi and Azotobacter bacteria in the rhizosphere unlock insoluble phosphorus and micronutrients.",
        "icon": "🌱"
    }
]


# ============================================================
# VERIFIED PRACTICAL AGRICULTURE TRAINING VIDEOS
# ============================================================

AGRICULTURE_VIDEOS = [
    {
        "id": "vid_mushroom",
        "title": "Mushroom Farming A to Z Setup & Practical Training",
        "hindi_title": "मशरूम की खेती: छोटे कमरे से लाखों की कमाई कैसे करें",
        "category": "revenue",
        "category_label": "High Revenue (कमाई वाली खेती)",
        "youtube_id": "R4VaWyriP0U",
        "duration": "18:42",
        "profit_badge": "₹3.5 - 5 Lakh / Year",
        "speaker": "Progressive Agri Masterclass",
        "views": "1.8M+ Views",
        "summary": "Step-by-step room climate management (18-24°C, 85% humidity), compost preparation, spawning, casing layer, and daily pinhead care for continuous harvesting.",
        "steps": [
            "Prepare straw compost with wheat/paddy straw, wheat bran, and gypsum over 28 days.",
            "Maintain dark spawn-run phase for 15 days until white mycelium colonizes the bags.",
            "Apply treated casing soil (sterilized with formalin/steam) to induce pinhead flushes."
        ]
    },
    {
        "id": "vid_polyhouse",
        "title": "Polyhouse & Protected Cultivation Masterclass: High Profit Farming",
        "hindi_title": "पॉलीहाउस खेती: बेमौसम सब्जियां उगाकर 4 गुना मुनाफा",
        "category": "revenue",
        "category_label": "High Revenue (कमाई वाली खेती)",
        "youtube_id": "BrD92Bpc2I8",
        "duration": "21:15",
        "profit_badge": "₹10 - 14 Lakh / Acre",
        "speaker": "Horticulture Expert Guide",
        "views": "950K+ Views",
        "summary": "Learn how naturally ventilated polyhouses protect crops from unseasonal storms while producing export-grade seedless cucumbers and Dutch bell peppers.",
        "steps": [
            "Structure orientation and 200-micron UV-stabilized polythene installation.",
            "Drip fertigation scheduling: Feeding NPK 19:19:19 and Calcium Nitrate daily.",
            "Pruning, single-stem trellis training, and blossom-end rot prevention."
        ]
    },
    {
        "id": "vid_dairy",
        "title": "Commercial Dairy Farm Business Plan & High-Yield Milk Management",
        "hindi_title": "डेयरी फार्मिंग बिजनेस: 10 पशुओं से हर महीने ₹60,000+ शुद्ध लाभ",
        "category": "revenue",
        "category_label": "High Revenue (कमाई वाली खेती)",
        "youtube_id": "2kSe7jw2mMw",
        "duration": "24:30",
        "profit_badge": "₹6.5 - 8.5 Lakh / Year",
        "speaker": "Modern Dairy Technologist",
        "views": "2.4M+ Views",
        "summary": "Selection of Murrah buffaloes and HF/Gir cows, green silage making, automated vacuum milking, calf rearing, and organic vermicompost byproduct profits.",
        "steps": [
            "Feed Total Mixed Ration (TMR) with maize silage to cut feed expenses by 35%.",
            "Maintain strict hygiene with rubber matting to prevent subclinical mastitis.",
            "Sell pure A2 milk directly to urban housing societies for ₹65-80/liter premium."
        ]
    },
    {
        "id": "vid_dragon",
        "title": "Dragon Fruit Farming: 25 Years Guaranteed Recurring Income",
        "hindi_title": "ड्रैगन फ्रूट की खेती: बंजर जमीन पर लगाएं, 25 साल तक हर साल लाखों पाएं",
        "category": "revenue",
        "category_label": "High Revenue (कमाई वाली खेती)",
        "youtube_id": "ClhqLjUEZqg",
        "duration": "16:50",
        "profit_badge": "₹6 - 9 Lakh / Acre / Year",
        "speaker": "Horticulture Agri-Tech",
        "views": "1.2M+ Views",
        "summary": "RCC pole trellising, selection of red-flesh C-variety saplings, minimal water requirement, and pest-free cultivation for desert & semi-arid lands.",
        "steps": [
            "Install 500 RCC poles per acre with top cement rings; plant 4 cuttings per pole.",
            "Provide drip irrigation once in 5-7 days; dragon fruit requires 80% less water.",
            "Harvest 6-8 tons fruit from year 2 onwards at wholesale rate of ₹100-140/kg."
        ]
    },
    {
        "id": "vid_beekeeping",
        "title": "Commercial Honeybee Keeping & Royal Jelly Production",
        "hindi_title": "मधुमक्खी पालन (Apiculture): 50 बॉक्स से ₹3 लाख शुद्ध सालाना बचत",
        "category": "revenue",
        "category_label": "High Revenue (कमाई वाली खेती)",
        "youtube_id": "2wh126Az27c",
        "duration": "14:10",
        "profit_badge": "₹2.8 - 3.5 Lakh / Year",
        "speaker": "National Bee Board Specialist",
        "views": "820K+ Views",
        "summary": "Apis mellifera bee colony management, seasonal migration across mustard and litchi belts, honey extraction, beeswax refining, and crop pollination boost.",
        "steps": [
            "Start with 25-50 bee boxes with queen excluder screens during mustard flowering.",
            "Extract 35-40 kg raw unprocessed honey per box annually.",
            "Bee pollination simultaneously boosts surrounding mustard & fruit yields by 20%."
        ]
    },
    {
        "id": "vid_vermicompost",
        "title": "Commercial Vermicompost & Earthworm Unit Business Setup",
        "hindi_title": "केंचुआ खाद (वर्मीकम्पोस्ट) बिजनेस: कचरे से बनाएं ₹2.5 लाख का मुनाफा",
        "category": "revenue",
        "category_label": "High Revenue (कमाई वाली खेती)",
        "youtube_id": "Pa8Hod6ZGMc",
        "duration": "19:25",
        "profit_badge": "₹1.8 - 2.4 Lakh / Year",
        "speaker": "Organic Agri Entrepreneur",
        "views": "1.5M+ Views",
        "summary": "Eisenia fetida Australian red earthworms, 30-foot HDPE bed construction, moisture control (60-70%), and organic packaging for nurseries & farmers.",
        "steps": [
            "Pre-decompose cow dung and crop residue for 10 days before releasing earthworms.",
            "Harvest fine dark brown granular vermicompost every 45-60 days.",
            "Collect liquid vermiwash nutrient tonic and sell to nurseries at ₹30-50/liter."
        ]
    },
    {
        "id": "vid_drone",
        "title": "Kisan Drone Spraying & Namo Drone Didi Training & Subsidy Guide",
        "hindi_title": "कृषि ड्रोन से छिड़काव: 10 एकड़ मात्र 20 मिनट में + सरकारी सब्सिडी",
        "category": "tech",
        "category_label": "Drones & Tech (ड्रोन व तकनीक)",
        "youtube_id": "FqNgAlXbKwo",
        "duration": "15:40",
        "profit_badge": "70% Time & 40% Chemical Saved",
        "speaker": "Agri Robotics India",
        "views": "1.1M+ Views",
        "summary": "How to operate agricultural spray drones, calculate waypoint trajectories with RTK GPS, and earn ₹400-500/acre offering custom spraying services to fellow farmers.",
        "steps": [
            "Calibrate 16-liter tank with ultra-low volume (ULV) nozzles for 100-micron droplets.",
            "Achieve 100% under-canopy penetration through powerful downward propeller downwash.",
            "Apply for up to ₹5,00,000 (50% subsidy) under Sub-Mission on Agricultural Mechanization (SMAM)."
        ]
    },
    {
        "id": "vid_wheat_yield",
        "title": "Modern Wheat Cultivation: Zero Tillage & Record Yield Techniques",
        "hindi_title": "गेहूं में रिकॉर्ड 30 क्विंटल प्रति एकड़ पैदावार की वैज्ञानिक विधि",
        "category": "crops",
        "category_label": "Field Crop Tech (फसल उत्पादन)",
        "youtube_id": "N84uYS5GVpA",
        "duration": "22:10",
        "profit_badge": "+35% Crop Yield",
        "speaker": "ICAR-Wheat Research Expert",
        "views": "3.1M+ Views",
        "summary": "Early sowing advantages, Happy Seeder direct drilling into standing stubble, timely CRI irrigation at 21 days, and micro-nutrient foliar spray schedules.",
        "steps": [
            "Use certified bio-treated seed varieties: DBW-187 (Karan Vandana) or DBW-303.",
            "Critical 1st irrigation at Crown Root Initiation (21-25 days); apply 1st urea split.",
            "Foliar spray of 0:52:34 + Boron at booting stage for bold, lustrous grain weight."
        ]
    },
    {
        "id": "vid_organic_jeevamrutha",
        "title": "Subhash Palekar Natural Farming: Jeevamrutha & Bio-Pesticide Preparation",
        "hindi_title": "जीवामृत एवं नीमास्त्र बनाने की सही विधि: खाद व कीटनाशक का खर्च शून्य करें",
        "category": "organic",
        "category_label": "Organic & Natural (प्राकृतिक खेती)",
        "youtube_id": "_CT76J7MQNQ",
        "duration": "17:35",
        "profit_badge": "Cut Chemical Cost by 100%",
        "speaker": "Natural Farming Foundation",
        "views": "2.7M+ Views",
        "summary": "Complete recipe for 200 liters of liquid Jeevamrutha using indigenous cow dung, urine, jaggery, pulse flour, and virgin forest soil to enrich soil carbon.",
        "steps": [
            "Mix 10 kg desi cow dung + 10L urine + 2 kg jaggery + 2 kg besan in 200L water.",
            "Ferment under shade for 48-72 hours, stirring clockwise twice daily.",
            "Apply through irrigation water (flood/drip) once a month for massive earthworm activity."
        ]
    },
    {
        "id": "vid_fpo_market",
        "title": "Direct Selling & Value Addition: How Farmers Earn 40% More Without Middlemen",
        "hindi_title": "सीधे मंडी और ग्राहक को बेचें: बिचौलियों को हटाएं और 40% ज्यादा दाम पाएं",
        "category": "market",
        "category_label": "Direct Selling & FPO (मार्केटिंग व बिक्री)",
        "youtube_id": "CuZTBXx0tSM",
        "duration": "20:05",
        "profit_badge": "+40% Direct Profit",
        "speaker": "Agri Marketing Strategist",
        "views": "1.3M+ Views",
        "summary": "Forming Farmer Producer Organizations (FPOs), grading & sorting farm produce, direct B2B supply to urban supermarkets, e-NAM registration, and basic processing.",
        "steps": [
            "Do not sell bulk unsorted produce; clean, grade, and pack into 5kg/10kg bags for 25% higher price.",
            "Sell cold-pressed mustard oil, milled dal, or turmeric powder instead of raw seed.",
            "Utilize e-NAM online mandis and ONDC to reach national bulk buyers with digital payments."
        ]
    }
]

VIDEO_CATEGORIES = [
    {"id": "all", "label": "All Videos (सभी वीडियो)", "icon": "🎬", "count": 10},
    {"id": "revenue", "label": "High-Income Farming (लाखों की कमाई)", "icon": "💰", "count": 6},
    {"id": "crops", "label": "Field Crop Tech (फसल तकनीक)", "icon": "🌾", "count": 1},
    {"id": "tech", "label": "Drones & Machines (ड्रोन व मशीनें)", "icon": "🛸", "count": 1},
    {"id": "organic", "label": "Organic & Natural (प्राकृतिक खेती)", "icon": "🌱", "count": 1},
    {"id": "market", "label": "Direct Selling & FPO (सीधी बिक्री)", "icon": "📈", "count": 1},
]

# ============================================================
# AGRIBUSINESS REVENUE GENERATION MODELS (ROI CALCULATOR)
# ============================================================

REVENUE_MODELS = [
    {
        "id": "mushroom",
        "name": "Oyster & Button Mushroom Unit",
        "hindi_name": "मशरूम उत्पादन यूनिट (कमरे में)",
        "icon": "🍄",
        "badge": "Fast Cashflow",
        "unit_name": "1,000 Sq. Ft. Room",
        "unit_multiplier_label": "Rooms / Sheds",
        "default_investment": 120000,
        "subsidy_pct": 40,
        "subsidy_scheme": "MIDH / National Horticulture Board (40-50% Subsidy)",
        "gross_revenue": 540000,
        "operating_cost": 180000,
        "net_annual_profit": 360000,
        "monthly_income": 30000,
        "payback_months": 5,
        "risk_level": "Low - Indoors",
        "production_details": "3 harvest cycles per year • 4,500 kg total harvest • ₹120/kg wholesale price",
        "tips": "Utilizes vertical racks up to 5 tiers high. High demand in local hotels, banquet halls, and vegetable mandis."
    },
    {
        "id": "polyhouse",
        "name": "Protected Polyhouse (Exotic Veggies)",
        "hindi_name": "संरक्षित पॉलीहाउस (खीरा, शिमला मिर्च)",
        "icon": "🏡",
        "badge": "Highest Yield / Acre",
        "unit_name": "1 Acre (4,000 Sq.m)",
        "unit_multiplier_label": "Acres",
        "default_investment": 3200000,
        "subsidy_pct": 50,
        "subsidy_scheme": "State Horticulture Mission / NHB (50% Project Cost Subsidy)",
        "gross_revenue": 2200000,
        "operating_cost": 800000,
        "net_annual_profit": 1400000,
        "monthly_income": 116000,
        "payback_months": 18,
        "risk_level": "Medium - High Tech",
        "production_details": "45-50 Tons/Acre high-grade seedless Dutch cucumber or red/yellow bell peppers at ₹45-55/kg avg.",
        "tips": "Zero crop damage from hail or sudden heavy rain. Year-round harvesting when open field market prices spike."
    },
    {
        "id": "dragon_fruit",
        "name": "High-Density Dragon Fruit Plantation",
        "hindi_name": "ड्रैगन फ्रूट बागवानी (25 साल कमाई)",
        "icon": "🐉",
        "badge": "25-Yr Asset",
        "unit_name": "1 Acre (500 Poles)",
        "unit_multiplier_label": "Acres",
        "default_investment": 450000,
        "subsidy_pct": 30,
        "subsidy_scheme": "Mission for Integrated Development of Horticulture (MIDH)",
        "gross_revenue": 950000,
        "operating_cost": 150000,
        "net_annual_profit": 800000,
        "monthly_income": 66000,
        "payback_months": 22,
        "risk_level": "Low - Drought Hardy",
        "production_details": "6,500 - 8,000 kg harvest per acre from 2nd year onwards • Sold at ₹110-140/kg in Tier 1/2 cities.",
        "tips": "Extremely low water requirement (cactus family). No damage from stray cattle or monkeys."
    },
    {
        "id": "dairy",
        "name": "Commercial Dairy (10 Murrah / HF Cattle)",
        "hindi_name": "आधुनिक डेयरी फार्मिंग (10 दुधारू पशु)",
        "icon": "🐄",
        "badge": "Daily Cashflow",
        "unit_name": "10 Animals + Shed",
        "unit_multiplier_label": "Units (10 Animals)",
        "default_investment": 1100000,
        "subsidy_pct": 25,
        "subsidy_scheme": "NABARD / Animal Husbandry Infrastructure Development Fund (AHIDF 3% Interest Subvention)",
        "gross_revenue": 2160000,
        "operating_cost": 1400000,
        "net_annual_profit": 760000,
        "monthly_income": 63000,
        "payback_months": 19,
        "risk_level": "Low-Medium",
        "production_details": "110-130 Liters/day milk production • Sold directly at ₹55-60/liter + 40 trolley organic manure per year.",
        "tips": "Silage making cuts green fodder costs by 40%. Direct selling to consumers gives 35% higher margin than milk dairies."
    },
    {
        "id": "apiculture",
        "name": "Commercial Apiculture (Honeybee Boxes)",
        "hindi_name": "व्यावसायिक मधुमक्खी पालन (50 बॉक्स)",
        "icon": "🐝",
        "badge": "Low Space Required",
        "unit_name": "50 Bee Boxes",
        "unit_multiplier_label": "Lots (50 Boxes)",
        "default_investment": 200000,
        "subsidy_pct": 50,
        "subsidy_scheme": "National Beekeeping & Honey Mission (NBHM)",
        "gross_revenue": 420000,
        "operating_cost": 100000,
        "net_annual_profit": 320000,
        "monthly_income": 26000,
        "payback_months": 9,
        "risk_level": "Low",
        "production_details": "1,800 kg pure raw honey annually • Sold at ₹220-280/kg + Beeswax + Pollination yield boost.",
        "tips": "Can be placed on field borders without using arable crop land. Boosts surrounding crop yield by 20% through pollination."
    },
    {
        "id": "vermicompost",
        "name": "Commercial Vermicompost & Bio-Fertilizer",
        "hindi_name": "केंचुआ खाद एवं वर्मीवॉश उत्पादन यूनिट",
        "icon": "🪱",
        "badge": "Zero Waste Eco Model",
        "unit_name": "10 Commercial Beds",
        "unit_multiplier_label": "Beds (10 Units)",
        "default_investment": 95000,
        "subsidy_pct": 40,
        "subsidy_scheme": "PKVY / Rashtriya Krishi Vikas Yojana (RKVY)",
        "gross_revenue": 310000,
        "operating_cost": 80000,
        "net_annual_profit": 230000,
        "monthly_income": 19000,
        "payback_months": 6,
        "risk_level": "Very Low",
        "production_details": "30 Tons organic vermicompost @ ₹7/kg + 800 Liters vermiwash @ ₹40/liter.",
        "tips": "Uses farm agro-waste, paddy straw, and cow dung. Sells rapidly to urban gardening nurseries, organic orchards, and polyhouses."
    }
]


def learning_home(request):
    """
    Advanced Farmer Learning Hub with:
    - 3D Plant Growth Lifecycle visualizer
    - Practical Agriculture Video Academy with category filters & modal player
    - Agri-Business Revenue & ROI Calculator for high-income farming models
    - Step-by-step crop roadmaps & audio guide
    - Direct-to-market revenue acceleration blueprints
    """
    selected_crop = request.GET.get("crop", "").strip().lower()

    if selected_crop:
        roadmaps = [r for r in LEARNING_ROADMAPS if r["id"] == selected_crop]
        if not roadmaps:
            roadmaps = LEARNING_ROADMAPS
    else:
        roadmaps = LEARNING_ROADMAPS

    crops_menu = [
        {"id": r["id"], "name": r["crop"], "hindi": r.get("hindi_name", ""), "icon": r["icon"]}
        for r in LEARNING_ROADMAPS
    ]

    context = {
        "roadmaps": roadmaps,
        "selected_crop": selected_crop,
        "all_roadmaps": LEARNING_ROADMAPS,
        "crops_menu": crops_menu,
        "modern_modules": MODERN_MODULES,
        "videos": AGRICULTURE_VIDEOS,
        "video_categories": VIDEO_CATEGORIES,
        "revenue_models": REVENUE_MODELS,
        "revenue_models_json": json.dumps(REVENUE_MODELS),
        "hotspots_json": json.dumps(HOTSPOTS_3D),
        "roadmaps_json": json.dumps(LEARNING_ROADMAPS),
    }

    return render(request, "encyclopedia/learning.html", context)