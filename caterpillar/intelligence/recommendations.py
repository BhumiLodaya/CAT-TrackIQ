"""Recommendation logic."""

import math

from intelligence.utilization import calculate_utilization

PRIORITY_ORDER = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}

DEMO_DAILY_RENTAL_RATE = {
    "Excavator": 18000,
    "Bulldozer": 17000,
    "Crane": 22000,
    "Grader": 15000,
}
DEMO_RELOCATION_COST_RATE = 0.8333333333


def _safe_int(value):
    try:
        numeric = int(value)
    except (TypeError, ValueError):
        return 0
    return numeric


def _calculate_demographic_benefit(equipment_type, shortage):
    daily_rate = DEMO_DAILY_RENTAL_RATE.get(equipment_type, 15000)
    avoided_days = max(1, min(7, int(math.ceil(float(shortage) if shortage > 0 else 1.0))))
    gross_avoided_rental_cost = int(daily_rate * avoided_days)
    estimated_relocation_cost = int(daily_rate * DEMO_RELOCATION_COST_RATE)
    net_benefit = gross_avoided_rental_cost - estimated_relocation_cost
    return {
        "currency": "INR",
        "pricing_type": "DEMO_ASSUMPTION",
        "gross_avoided_rental_cost": gross_avoided_rental_cost,
        "estimated_relocation_cost": estimated_relocation_cost,
        "estimated_net_benefit": net_benefit,
    }


def _calculate_reallocation_score(shortage, utilization, idle_hours, site_assigned, estimated_net_benefit):
    if shortage <= 0:
        shortage_score = 0
    elif shortage >= 3.0:
        shortage_score = 35
    elif shortage >= 1.5:
        shortage_score = 25
    elif shortage >= 0.5:
        shortage_score = 15
    else:
        shortage_score = 5

    if utilization < 25:
        underutilization_score = 25
    elif utilization < 50:
        underutilization_score = 15
    else:
        underutilization_score = 5

    if not site_assigned:
        availability_score = 20
    elif idle_hours > 8:
        availability_score = 10
    else:
        availability_score = 0

    cost_benefit_score = min(20, max(0, int(round(estimated_net_benefit / 12000.0))))
    total = shortage_score + underutilization_score + availability_score + cost_benefit_score
    return max(0, min(100, total)), {
        "demand_urgency": shortage_score,
        "underutilization": underutilization_score,
        "availability": availability_score,
        "cost_benefit": cost_benefit_score,
    }


def generate_recommendations(assets, forecasts, anomalies):
    recommendations = []
    anomaly_map = {}
    for anomaly in anomalies:
        equipment_id = anomaly.get("equipment_id")
        anomaly_map.setdefault(equipment_id, []).append(anomaly)

    for forecast in forecasts:
        site_id = forecast.get("site_id")
        equipment_type = forecast.get("equipment_type")
        shortage = float(forecast.get("shortage_or_surplus", 0))
        if shortage <= 0:
            continue

        candidates = []
        for asset in assets:
            if asset.get("type") != equipment_type:
                continue
            if asset.get("site_id") == site_id:
                continue
            equipment_id = asset.get("equipment_id")
            utilization = calculate_utilization(asset)
            idle_hours = float(asset.get("idle_hours_per_day", 0) or 0)
            site_assigned = asset.get("site_id") is not None and asset.get("operator_id") is not None
            score = 0.0
            if not site_assigned:
                score += 40
            if utilization < 25:
                score += 25
            if idle_hours > 8:
                score += 20
            score += min(shortage * 12, 35)
            for anomaly in anomaly_map.get(equipment_id, []):
                anomaly_type = anomaly.get("anomaly_type")
                if anomaly_type in {"UNASSIGNED", "HIGH_IDLE", "LOW_UTILIZATION", "ZERO_USAGE", "UNASSIGNED_HIGH_IDLE"}:
                    score += 15
            if score >= 50:
                candidates.append({"equipment_id": equipment_id, "score": round(score, 2), "asset": asset})

        if not candidates:
            continue

        best = sorted(candidates, key=lambda item: item["score"], reverse=True)[0]
        asset = best["asset"]
        equipment_id = best["equipment_id"]
        utilization = calculate_utilization(asset)
        idle_hours = float(asset.get("idle_hours_per_day", 0) or 0)
        site_assigned = asset.get("site_id") is not None and asset.get("operator_id") is not None

        if not site_assigned or utilization < 25 or idle_hours > 8:
            priority = "HIGH"
        elif shortage >= 1.5:
            priority = "MEDIUM"
        else:
            priority = "LOW"

        if not site_assigned:
            reason = f"Asset is currently unassigned while predicted {equipment_type.lower()} demand at {site_id} exceeds available inventory."
        else:
            reason = f"Asset utilization is {utilization}% with {idle_hours} idle hours/day while predicted {equipment_type.lower()} demand at {site_id} exceeds available inventory."

        benefit_details = _calculate_demographic_benefit(equipment_type, shortage)
        reallocation_score, score_breakdown = _calculate_reallocation_score(
            shortage=shortage,
            utilization=utilization,
            idle_hours=idle_hours,
            site_assigned=site_assigned,
            estimated_net_benefit=benefit_details["estimated_net_benefit"],
        )
        recommendation = {
            "equipment_id": equipment_id,
            "action": "REALLOCATE",
            "target_site": site_id,
            "priority": priority,
            "reason": reason,
            "score": best["score"],
            "equipment_type": equipment_type,
            "predicted_shortage": round(shortage, 2),
            "reallocation_score": int(reallocation_score),
            "score_breakdown": {
                "demand_urgency": int(score_breakdown["demand_urgency"]),
                "underutilization": int(score_breakdown["underutilization"]),
                "availability": int(score_breakdown["availability"]),
                "cost_benefit": int(score_breakdown["cost_benefit"]),
            },
            "currency": benefit_details["currency"],
            "pricing_type": benefit_details["pricing_type"],
            "gross_avoided_rental_cost": int(benefit_details["gross_avoided_rental_cost"]),
            "estimated_relocation_cost": int(benefit_details["estimated_relocation_cost"]),
            "estimated_net_benefit": int(benefit_details["estimated_net_benefit"]),
        }
        recommendations.append(recommendation)

    recommendations.sort(key=lambda item: (
        item.get("reallocation_score", 0),
        item.get("estimated_net_benefit", 0),
        PRIORITY_ORDER.get(item.get("priority"), 0),
    ), reverse=True)
    return recommendations