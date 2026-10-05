import json
import math

from intelligence.utilization import calculate_utilization
from intelligence.anomaly import detect_anomalies
from intelligence.forecasting import generate_synthetic_history, forecast_demand, evaluate_forecast_model
from intelligence.recommendations import generate_recommendations


ASSETS = [
    {"equipment_id": "EQX1001", "type": "Excavator", "site_id": "S003", "operator_id": "OP101", "status": "ACTIVE", "engine_hours_per_day": 1.5, "idle_hours_per_day": 10, "operating_days": 14, "expected_return_date": "2026-09-05"},
    {"equipment_id": "EQX1002", "type": "Crane", "site_id": None, "operator_id": None, "status": "IDLE", "engine_hours_per_day": 0, "idle_hours_per_day": 11, "operating_days": 0, "expected_return_date": None},
    {"equipment_id": "EQX1003", "type": "Bulldozer", "site_id": "S002", "operator_id": "OP203", "status": "ACTIVE", "engine_hours_per_day": 7.5, "idle_hours_per_day": 0.5, "operating_days": 21, "expected_return_date": "2026-09-10"},
    {"equipment_id": "EQX1004", "type": "Excavator", "site_id": "S004", "operator_id": "OP106", "status": "ACTIVE", "engine_hours_per_day": 2, "idle_hours_per_day": 9, "operating_days": 12, "expected_return_date": "2026-09-03"},
    {"equipment_id": "EQX1005", "type": "Bulldozer", "site_id": "S006", "operator_id": "OP301", "status": "ACTIVE", "engine_hours_per_day": 8, "idle_hours_per_day": 0, "operating_days": 18, "expected_return_date": "2026-09-12"},
    {"equipment_id": "EQX1006", "type": "Grader", "site_id": "S001", "operator_id": "OP114", "status": "ACTIVE", "engine_hours_per_day": 3, "idle_hours_per_day": 6, "operating_days": 10, "expected_return_date": "2026-09-08"},
    {"equipment_id": "EQX1007", "type": "Excavator", "site_id": None, "operator_id": None, "status": "IDLE", "engine_hours_per_day": 0, "idle_hours_per_day": 12, "operating_days": 0, "expected_return_date": None},
]


def test_calculate_utilization():
    result = calculate_utilization({"engine_hours_per_day": 1.5, "idle_hours_per_day": 10})
    assert result == 13.04


def test_detect_anomalies_returns_structured_records():
    anomalies = detect_anomalies(ASSETS)
    assert any(item["equipment_id"] == "EQX1007" and item["anomaly_type"] in {"UNASSIGNED", "UNASSIGNED_HIGH_IDLE"} for item in anomalies)
    assert any(item["equipment_id"] == "EQX1001" and item["anomaly_type"] == "LOW_UTILIZATION" for item in anomalies)


def test_generate_synthetic_history_returns_records():
    history = generate_synthetic_history(days=90)
    assert len(history) > 0
    assert set(history[0].keys()) >= {"date", "site_id", "equipment_type", "rental_count"}


def test_forecast_demand_returns_site_type_forecasts():
    history = generate_synthetic_history(days=120)
    forecasts = forecast_demand(history, ASSETS)
    assert len(forecasts) > 0
    assert set(forecasts[0].keys()) >= {"site_id", "equipment_type", "predicted_demand", "available_assets", "shortage_or_surplus"}


def test_generate_recommendations_returns_actionable_items():
    history = generate_synthetic_history(days=120)
    forecasts = forecast_demand(history, ASSETS)
    anomalies = detect_anomalies(ASSETS)
    recommendations = generate_recommendations(ASSETS, forecasts, anomalies)
    assert isinstance(recommendations, list)
    assert all(set(item.keys()) >= {"equipment_id", "action", "target_site", "priority", "reason"} for item in recommendations)


def test_reallocation_scoring_and_benefit_are_present_and_serializable():
    history = generate_synthetic_history(days=120)
    forecasts = forecast_demand(history, ASSETS)
    anomalies = detect_anomalies(ASSETS)
    recommendations = generate_recommendations(ASSETS, forecasts, anomalies)

    rec = next(item for item in recommendations if item["equipment_id"] == "EQX1007")
    assert 0 <= rec["reallocation_score"] <= 100
    assert rec["score_breakdown"]["demand_urgency"] + rec["score_breakdown"]["underutilization"] + rec["score_breakdown"]["availability"] + rec["score_breakdown"]["cost_benefit"] == rec["reallocation_score"]
    assert rec["pricing_type"] == "DEMO_ASSUMPTION"
    assert rec["estimated_net_benefit"] == rec["gross_avoided_rental_cost"] - rec["estimated_relocation_cost"]
    assert rec["currency"] == "INR"
    json.dumps(rec)


def test_higher_shortage_and_underutilization_increase_score():
    base_asset = {
        "equipment_id": "EQX1008",
        "type": "Excavator",
        "site_id": None,
        "operator_id": None,
        "status": "IDLE",
        "engine_hours_per_day": 0,
        "idle_hours_per_day": 12,
        "operating_days": 0,
        "expected_return_date": None,
    }
    low_score = generate_recommendations([base_asset], [{"site_id": "S001", "equipment_type": "Excavator", "shortage_or_surplus": 0.5}], [])
    high_score = generate_recommendations([base_asset], [{"site_id": "S001", "equipment_type": "Excavator", "shortage_or_surplus": 2.5}], [])

    assert low_score[0]["reallocation_score"] <= high_score[0]["reallocation_score"]


def test_evaluate_forecast_model_returns_serializable_metrics():
    history = generate_synthetic_history(days=120)
    evaluation = evaluate_forecast_model(history)

    assert evaluation["evaluation_type"] == "chronological_holdout"
    assert evaluation["data_leakage_check"] == "PASS"
    assert evaluation["train_records"] > 0
    assert evaluation["test_records"] > 0
    assert evaluation["train_end_date"] < evaluation["test_start_date"]

    model_metrics = evaluation["model"]
    baseline_metrics = evaluation["baseline"]

    for metric_name in ("mae", "rmse"):
        assert metric_name in model_metrics
        assert metric_name in baseline_metrics
        assert model_metrics[metric_name] >= 0
        assert baseline_metrics[metric_name] >= 0
        assert math.isfinite(model_metrics[metric_name])
        assert math.isfinite(baseline_metrics[metric_name])
        assert not math.isnan(model_metrics[metric_name])
        assert not math.isnan(baseline_metrics[metric_name])
        assert not math.isinf(model_metrics[metric_name])
        assert not math.isinf(baseline_metrics[metric_name])

    json.dumps(evaluation)
    assert isinstance(evaluation["model"]["name"], str)
    assert isinstance(evaluation["baseline"]["name"], str)
