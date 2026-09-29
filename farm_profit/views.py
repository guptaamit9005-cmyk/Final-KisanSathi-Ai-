from django.shortcuts import render
from .models import FarmProfitCalculation


def farm_profit_calculator(request):

    result = None

    if request.method == "POST":

        crop = request.POST.get("crop")

        area = float(
            request.POST.get("area", 0)
        )

        seed_cost = float(
            request.POST.get("seed_cost", 0)
        )

        fertilizer_cost = float(
            request.POST.get("fertilizer_cost", 0)
        )

        pesticide_cost = float(
            request.POST.get("pesticide_cost", 0)
        )

        labour_cost = float(
            request.POST.get("labour_cost", 0)
        )

        irrigation_cost = float(
            request.POST.get("irrigation_cost", 0)
        )

        machinery_cost = float(
            request.POST.get("machinery_cost", 0)
        )

        other_cost = float(
            request.POST.get("other_cost", 0)
        )

        expected_yield = float(
            request.POST.get("expected_yield", 0)
        )

        selling_price = float(
            request.POST.get("selling_price", 0)
        )

        # --------------------------------
        # TOTAL COST
        # --------------------------------

        total_cost = (
            seed_cost
            + fertilizer_cost
            + pesticide_cost
            + labour_cost
            + irrigation_cost
            + machinery_cost
            + other_cost
        )

        # --------------------------------
        # EXPECTED REVENUE
        # --------------------------------

        expected_revenue = (
            expected_yield
            * selling_price
        )

        # --------------------------------
        # PROFIT / LOSS
        # --------------------------------

        expected_profit = (
            expected_revenue
            - total_cost
        )

        # --------------------------------
        # ROI
        # --------------------------------

        if total_cost > 0:

            roi = (
                expected_profit
                / total_cost
            ) * 100

        else:

            roi = 0

        # --------------------------------
        # BREAK EVEN PRICE
        # --------------------------------

        if expected_yield > 0:

            break_even_price = (
                total_cost
                / expected_yield
            )

        else:

            break_even_price = 0

        # --------------------------------
        # PROFIT PER ACRE
        # --------------------------------

        if area > 0:

            profit_per_acre = (
                expected_profit
                / area
            )

            cost_per_acre = (
                total_cost
                / area
            )

        else:

            profit_per_acre = 0
            cost_per_acre = 0

        # --------------------------------
        # RESULT
        # --------------------------------

        result = {

            "crop": crop,

            "area": area,

            "total_cost": round(
                total_cost,
                2
            ),

            "expected_revenue": round(
                expected_revenue,
                2
            ),

            "expected_profit": round(
                expected_profit,
                2
            ),

            "roi": round(
                roi,
                2
            ),

            "break_even_price": round(
                break_even_price,
                2
            ),

            "profit_per_acre": round(
                profit_per_acre,
                2
            ),

            "cost_per_acre": round(
                cost_per_acre,
                2
            ),

            "expected_yield": expected_yield,

            "selling_price": selling_price,
        }

        # --------------------------------
        # SAVE CALCULATION
        # --------------------------------

        FarmProfitCalculation.objects.create(

            user=(
                request.user
                if request.user.is_authenticated
                else None
            ),

            crop=crop,

            area=area,

            seed_cost=seed_cost,

            fertilizer_cost=fertilizer_cost,

            pesticide_cost=pesticide_cost,

            labour_cost=labour_cost,

            irrigation_cost=irrigation_cost,

            machinery_cost=machinery_cost,

            other_cost=other_cost,

            expected_yield=expected_yield,

            selling_price=selling_price,

            total_cost=total_cost,

            expected_revenue=expected_revenue,

            expected_profit=expected_profit,

            roi=roi,

            break_even_price=break_even_price,
        )

    return render(
        request,
        "farm_profit/calculator.html",
        {
            "result": result
        }
    )