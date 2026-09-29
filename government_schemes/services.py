from datetime import date
from decimal import Decimal


def check_scheme_eligibility(scheme, farmer):

    score = 0
    reasons = []
    warnings = []

    today = date.today()

    # ==================================================
    # ACTIVE CHECK
    # ==================================================

    if not scheme.is_active:
        return {
            "eligible": False,
            "score": 0,
            "reasons": [],
            "warnings": ["Scheme is currently inactive."]
        }

    # ==================================================
    # VALID DATE
    # ==================================================

    if scheme.valid_from and today < scheme.valid_from:

        return {
            "eligible": False,
            "score": 0,
            "reasons": [],
            "warnings": [
                f"Scheme starts from {scheme.valid_from.strftime('%d %b %Y')}."
            ]
        }

    if scheme.valid_until and today > scheme.valid_until:

        return {
            "eligible": False,
            "score": 0,
            "reasons": [],
            "warnings": [
                "Scheme validity period has ended."
            ]
        }

    # ==================================================
    # DEADLINE
    # ==================================================

    deadline = scheme.application_deadline

    if deadline:

        if today > deadline:

            return {
                "eligible": False,
                "score": 0,
                "reasons": [],
                "warnings": [
                    "Application deadline has passed."
                ]
            }

        days_left = (deadline - today).days

        if days_left <= 7:

            warnings.append(
                f"Application deadline is in {days_left} days."
            )

        elif days_left <= 30:

            warnings.append(
                f"Application deadline is in {days_left} days."
            )

    # ==================================================
    # STATE
    # ==================================================

    if scheme.state not in ["All India", "", None]:

        if scheme.state.lower() != farmer["state"].lower():

            return {
                "eligible": False,
                "score": 0,
                "reasons": [],
                "warnings": [
                    f"This scheme is not available in {farmer['state']}."
                ]
            }

        score += 20

        reasons.append(
            f"Available in {farmer['state']}."
        )

    else:

        score += 20

        reasons.append(
            "Available across India."
        )

    # ==================================================
    # AGE
    # ==================================================

    if scheme.min_age is not None:

        if farmer["age"] < scheme.min_age:

            return {
                "eligible": False,
                "score": 0,
                "reasons": [],
                "warnings": [
                    f"Minimum age is {scheme.min_age}."
                ]
            }

        score += 10

        reasons.append(
            "Age requirement satisfied."
        )

    if scheme.max_age is not None:

        if farmer["age"] > scheme.max_age:

            return {
                "eligible": False,
                "score": 0,
                "reasons": [],
                "warnings": [
                    f"Maximum age is {scheme.max_age}."
                ]
            }

        score += 10

    # ==================================================
    # GENDER
    # ==================================================

    if scheme.gender != "any":

        if scheme.gender != farmer["gender"]:

            return {
                "eligible": False,
                "score": 0,
                "reasons": [],
                "warnings": []
            }

        score += 10

        reasons.append(
            "Gender eligibility satisfied."
        )

    # ==================================================
    # FARMER TYPE
    # ==================================================

    if scheme.farmer_type not in ["any", "all"]:

        if scheme.farmer_type != farmer["farmer_type"]:

            return {
                "eligible": False,
                "score": 0,
                "reasons": [],
                "warnings": []
            }

        score += 15

        reasons.append(
            "Farmer category/type matches."
        )

    # ==================================================
    # LAND AREA
    # ==================================================

    if scheme.min_land_area is not None:

        if farmer["land_area"] < scheme.min_land_area:

            return {
                "eligible": False,
                "score": 0,
                "reasons": [],
                "warnings": [
                    "Land area is below the minimum requirement."
                ]
            }

        score += 10

        reasons.append(
            "Land-area requirement satisfied."
        )

    if scheme.max_land_area is not None:

        if farmer["land_area"] > scheme.max_land_area:

            return {
                "eligible": False,
                "score": 0,
                "reasons": [],
                "warnings": [
                    "Land area exceeds the scheme limit."
                ]
            }

        score += 10

    # ==================================================
    # INCOME
    # ==================================================

    if scheme.max_income is not None:

        income = Decimal(
            str(farmer.get("annual_income") or 0)
        )

        if income > scheme.max_income:

            return {
                "eligible": False,
                "score": 0,
                "reasons": [],
                "warnings": [
                    "Annual income is above the scheme limit."
                ]
            }

        score += 10

        reasons.append(
            "Income requirement satisfied."
        )

    # ==================================================
    # CROP
    # ==================================================

    if scheme.crops:

        crops = [
            str(c).lower()
            for c in scheme.crops
        ]

        if farmer["crop"].lower() not in crops:

            return {
                "eligible": False,
                "score": 0,
                "reasons": [],
                "warnings": [
                    "This crop is not listed for this scheme."
                ]
            }

        score += 15

        reasons.append(
            f"{farmer['crop'].title()} is covered."
        )

    # ==================================================
    # SEASON
    # ==================================================

    if scheme.seasons:

        seasons = [
            str(s).lower()
            for s in scheme.seasons
        ]

        if farmer["season"].lower() not in seasons:

            return {
                "eligible": False,
                "score": 0,
                "reasons": [],
                "warnings": [
                    "This scheme is not currently applicable "
                    "for the selected season."
                ]
            }

        score += 10

        reasons.append(
            f"{farmer['season'].title()} season matches."
        )

    # ==================================================
    # RESULT
    # ==================================================

    score = min(score, 100)

    return {
        "eligible": True,
        "score": score,
        "reasons": reasons,
        "warnings": warnings,
    }