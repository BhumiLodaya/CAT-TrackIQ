"""
Module 2: Rule-Based Anomaly Detection

Detects anomalies using transparent, explainable rules.

Rules:
- UNASSIGNED: site_id == NULL OR operator_id == NULL
- HIGH_IDLE: idle_hours_per_day > 8
- LOW_UTILIZATION: utilization < 25%
- ZERO_USAGE: engine_hours_per_day == 0 AND idle_hours_per_day > 0

Returns structured anomaly output.
"""
from intelligence.utilization import calculate_utilization


def detect_anomalies(assets):
    """
    Detect anomalies in a list of equipment assets using rule-based logic.

    Parameters:
    assets (list[dict]): List of asset dictionaries with keys:
        - equipment_id
        - site_id
        - operator_id
        - engine_hours_per_day
        - idle_hours_per_day

    Returns:
    list[dict]: List of detected anomalies with structure:
        - equipment_id
        - anomaly_type
        - severity
        - reason
        - metric
        - recommended_action
    """
    anomalies = []

    for asset in assets:
        equipment_id = asset.get("equipment_id", "UNKNOWN")
        site_id = asset.get("site_id")
        operator_id = asset.get("operator_id")
        engine_hours = asset.get("engine_hours_per_day", 0)
        idle_hours = asset.get("idle_hours_per_day", 0)
        utilization = calculate_utilization(asset)

        # Rule 1: UNASSIGNED - site_id == NULL OR operator_id == NULL
        if site_id is None or operator_id is None:
            anomalies.append({
                "equipment_id": equipment_id,
                "anomaly_type": "UNASSIGNED",
                "severity": "CRITICAL",
                "reason": f"No site/operator assigned.",
                "metric": None,
                "recommended_action": "Consider reallocating this asset.",
            })

        # Rule 2: HIGH_IDLE - idle_hours_per_day > 8
        if idle_hours > 8:
            # Avoid duplicate if already flagged as UNASSIGNED
            already_unassigned = any(
                a["equipment_id"] == equipment_id and a["anomaly_type"] == "UNASSIGNED"
                for a in anomalies
            )
            if not already_unassigned:
                anomalies.append({
                    "equipment_id": equipment_id,
                    "anomaly_type": "HIGH_IDLE",
                    "severity": "HIGH",
                    "reason": f"Idle hours per day: {idle_hours}.",
                    "metric": idle_hours,
                    "recommended_action": "Investigate equipment usage and maintenance.",
                })
            else:
                # Combine with UNASSIGNED
                for a in anomalies:
                    if a["equipment_id"] == equipment_id and a["anomaly_type"] == "UNASSIGNED":
                        a["anomaly_type"] = "UNASSIGNED_HIGH_IDLE"
                        a["severity"] = "CRITICAL"
                        a["reason"] = f"No site/operator assigned with {idle_hours} idle hours/day."
                        a["metric"] = idle_hours
                        break

        # Rule 3: LOW_UTILIZATION - utilization < 25%
        if utilization < 25:
            already_low_util = any(
                a["equipment_id"] == equipment_id and a["anomaly_type"] == "LOW_UTILIZATION"
                for a in anomalies
            )
            if not already_low_util:
                anomalies.append({
                    "equipment_id": equipment_id,
                    "anomaly_type": "LOW_UTILIZATION",
                    "severity": "MEDIUM",
                    "reason": f"Utilization is {utilization}%, below the 25% utilization threshold.",
                    "metric": utilization,
                    "recommended_action": "Consider reallocating or redeploying this asset.",
                })

        # Rule 4: ZERO_USAGE - engine_hours_per_day == 0 AND idle_hours_per_day > 0
        if engine_hours == 0 and idle_hours > 0:
            already_zero_usage = any(
                a["equipment_id"] == equipment_id and a["anomaly_type"] == "ZERO_USAGE"
                for a in anomalies
            )
            if not already_zero_usage:
                anomalies.append({
                    "equipment_id": equipment_id,
                    "anomaly_type": "ZERO_USAGE",
                    "severity": "HIGH",
                    "reason": f"Engine hours: 0 with {idle_hours} idle hours per day.",
                    "metric": 0,
                    "recommended_action": "Asset appears non-functional; inspect for maintenance needs.",
                })

    # Sort anomalies by equipment_id for consistent output
    anomalies.sort(key=lambda x: x["equipment_id"])
    return anomalies


# Example usage with the Caterpillar assets
if __name__ == "__main__":
    caterpillar_assets = [
        {"equipment_id": "EQX1001", "site_id": "S003", "operator_id": "OP101", "engine_hours_per_day": 1.5, "idle_hours_per_day": 10},
        {"equipment_id": "EQX1002", "site_id": None, "operator_id": None, "engine_hours_per_day": 0, "idle_hours_per_day": 11},
        {"equipment_id": "EQX1003", "site_id": "S002", "operator_id": "OP203", "engine_hours_per_day": 7.5, "idle_hours_per_day": 0.5},
        {"equipment_id": "EQX1004", "site_id": "S004", "operator_id": "OP106", "engine_hours_per_day": 2, "idle_hours_per_day": 9},
        {"equipment_id": "EQX1005", "site_id": "S006", "operator_id": "OP301", "engine_hours_per_day": 8, "idle_hours_per_day": 0},
        {"equipment_id": "EQX1006", "site_id": "S001", "operator_id": "OP114", "engine_hours_per_day": 3, "idle_hours_per_day": 6},
        {"equipment_id": "EQX1007", "site_id": None, "operator_id": None, "engine_hours_per_day": 0, "idle_hours_per_day": 12},
    ]

    print("=== Anomaly Detection Results ===\n")
    results = detect_anomalies(caterpillar_assets)
    for r in results:
        print(f"{r['equipment_id']}: {r['anomaly_type']} | Severity: {r['severity']} | Reason: {r['reason']} | Metric: {r['metric']} | Action: {r['recommended_action']}")