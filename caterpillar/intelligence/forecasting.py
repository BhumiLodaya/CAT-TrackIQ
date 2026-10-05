import math
import random
from collections import defaultdict
from datetime import date, timedelta

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

SITE_LIST = ["S001", "S002", "S003", "S004", "S005", "S006"]
EQUIPMENT_TYPES = ["Excavator", "Bulldozer", "Crane", "Grader"]


def generate_synthetic_history(days=180, seed=42):
    random.seed(seed)
    start = date(2025, 6, 1)
    site_base = {
        "S001": {"Excavator": 5.2, "Bulldozer": 3.8, "Crane": 2.4, "Grader": 3.1},
        "S002": {"Excavator": 4.6, "Bulldozer": 5.1, "Crane": 2.0, "Grader": 2.7},
        "S003": {"Excavator": 6.1, "Bulldozer": 4.0, "Crane": 2.8, "Grader": 2.2},
        "S004": {"Excavator": 4.9, "Bulldozer": 3.2, "Crane": 2.6, "Grader": 3.5},
        "S005": {"Excavator": 3.5, "Bulldozer": 2.7, "Crane": 3.4, "Grader": 2.9},
        "S006": {"Excavator": 5.4, "Bulldozer": 4.3, "Crane": 2.3, "Grader": 3.0},
    }
    site_trend = {"S001": 0.18, "S002": 0.10, "S003": 0.24, "S004": 0.12, "S005": 0.07, "S006": 0.20}
    equipment_bias = {"Excavator": 1.18, "Bulldozer": 1.05, "Crane": 0.92, "Grader": 1.00}
    history = []
    for offset in range(days):
        current_date = start + timedelta(days=offset)
        weekend_factor = 1.2 if current_date.weekday() >= 5 else 0.9
        for site_id in SITE_LIST:
            site_index = SITE_LIST.index(site_id)
            for equipment_type in EQUIPMENT_TYPES:
                equipment_index = EQUIPMENT_TYPES.index(equipment_type)
                base = site_base[site_id][equipment_type]
                trend = 1 + (offset / max(days, 1)) * site_trend[site_id]
                seasonality = 1 + 0.15 * math.sin((offset + site_index * 4 + equipment_index * 2) / 5.5)
                daily_pattern = weekend_factor * equipment_bias[equipment_type]
                noise = random.uniform(-0.8, 0.8)
                rental_count = max(0, round(base * trend * seasonality * daily_pattern + noise))
                history.append({
                    "date": current_date.isoformat(),
                    "site_id": site_id,
                    "equipment_type": equipment_type,
                    "rental_count": rental_count,
                })
    return history


def _clean_history_rows(history):
    cleaned = []
    for record in history or []:
        try:
            current_date = date.fromisoformat(str(record.get("date")))
        except (TypeError, ValueError):
            continue
        site_id = record.get("site_id")
        equipment_type = record.get("equipment_type")
        if site_id not in SITE_LIST or equipment_type not in EQUIPMENT_TYPES:
            continue
        try:
            rental_count = float(record.get("rental_count", 0))
        except (TypeError, ValueError):
            continue
        cleaned.append({
            "date": current_date,
            "site_id": site_id,
            "equipment_type": equipment_type,
            "rental_count": rental_count,
        })
    return sorted(cleaned, key=lambda item: item["date"])


def _feature_vector(current_date, site_id, equipment_type):
    return [
        current_date.month,
        current_date.day,
        current_date.weekday(),
        SITE_LIST.index(site_id),
        EQUIPMENT_TYPES.index(equipment_type),
    ]


def _build_model(history):
    cleaned_history = _clean_history_rows(history)
    if not cleaned_history:
        return None
    X, y = [], []
    for record in cleaned_history:
        X.append(_feature_vector(record["date"], record["site_id"], record["equipment_type"]))
        y.append(float(record.get("rental_count", 0)))
    model = RandomForestRegressor(n_estimators=80, random_state=42)
    model.fit(X, y)
    return model


def _predict_one(model, site_id, equipment_type, forecast_date):
    if model is None:
        return 0.0
    features = _feature_vector(forecast_date, site_id, equipment_type)
    return max(0.0, float(model.predict([features])[0]))


def _safe_float(value, default=0.0):
    if value is None:
        return default
    try:
        float_value = float(value)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(float_value):
        return default
    return float_value


def evaluate_forecast_model(history):
    cleaned_history = _clean_history_rows(history)
    if not cleaned_history:
        return {
            "evaluation_type": "chronological_holdout",
            "data_type": "synthetic_demo_data",
            "train_records": 0,
            "test_records": 0,
            "train_start_date": None,
            "train_end_date": None,
            "test_start_date": None,
            "test_end_date": None,
            "model": {"name": "RandomForestRegressor", "mae": 0.0, "rmse": 0.0, "r2": None},
            "baseline": {"name": "Site-Type Training Mean", "mae": 0.0, "rmse": 0.0},
            "mae_improvement_vs_baseline_percent": 0.0,
            "interpretation": "No valid historical records were available for evaluation.",
            "limitations": [
                "Evaluation uses synthetic historical rental-demand data.",
                "Metrics demonstrate pipeline behaviour, not production Caterpillar accuracy."
            ],
            "data_leakage_check": "FAIL",
        }

    unique_dates = sorted({record["date"] for record in cleaned_history})
    if len(unique_dates) < 2:
        split_index = 1
    else:
        split_index = max(1, min(len(unique_dates) - 1, int(len(unique_dates) * 0.8)))
    train_dates = unique_dates[:split_index]
    test_dates = unique_dates[split_index:]
    if not test_dates:
        split_index = max(1, len(unique_dates) - 1)
        train_dates = unique_dates[:split_index]
        test_dates = unique_dates[split_index:]

    train_records = [record for record in cleaned_history if record["date"] in train_dates]
    test_records = [record for record in cleaned_history if record["date"] in test_dates]

    model = _build_model(train_records)
    global_mean = sum(record["rental_count"] for record in train_records) / max(len(train_records), 1)
    baseline_lookup = defaultdict(float)
    baseline_counts = defaultdict(int)
    for record in train_records:
        key = (record["site_id"], record["equipment_type"])
        baseline_lookup[key] += record["rental_count"]
        baseline_counts[key] += 1
    baseline_means = {
        key: (baseline_lookup[key] / baseline_counts[key])
        for key in baseline_counts
    }

    y_true, model_predictions, baseline_predictions = [], [], []
    for record in test_records:
        target = float(record["rental_count"])
        if model is not None:
            predicted = _predict_one(model, record["site_id"], record["equipment_type"], record["date"])
        else:
            predicted = global_mean
        baseline_pred = baseline_means.get((record["site_id"], record["equipment_type"]), global_mean)
        y_true.append(target)
        model_predictions.append(predicted)
        baseline_predictions.append(baseline_pred)

    def _calculate_metrics(true_values, predicted_values):
        if not true_values:
            return 0.0, 0.0, None
        mae = mean_absolute_error(true_values, predicted_values)
        rmse = math.sqrt(mean_squared_error(true_values, predicted_values))
        try:
            r2 = float(r2_score(true_values, predicted_values))
        except Exception:
            r2 = None
        if r2 is not None and not math.isfinite(r2):
            r2 = None
        return _safe_float(mae), _safe_float(rmse), r2

    model_mae, model_rmse, model_r2 = _calculate_metrics(y_true, model_predictions)
    baseline_mae, baseline_rmse, _ = _calculate_metrics(y_true, baseline_predictions)

    if baseline_mae > 0:
        improvement = ((baseline_mae - model_mae) / baseline_mae) * 100.0
    else:
        improvement = 0.0

    data_leakage_check = "PASS" if (
        train_records and test_records and
        train_dates and test_dates and
        max(train_dates) < min(test_dates) and
        baseline_means and
        model is not None
    ) else "FAIL"

    if model_mae < baseline_mae:
        interpretation = (
            "On the chronological synthetic holdout set, the Random Forest achieved an MAE of "
            f"{model_mae:.3f} equipment units compared with a baseline MAE of {baseline_mae:.3f}. "
            "Random Forest improved over the baseline."
        )
    else:
        interpretation = (
            "On the chronological synthetic holdout set, the Random Forest achieved an MAE of "
            f"{model_mae:.3f} equipment units compared with a baseline MAE of {baseline_mae:.3f}. "
            "The model did not improve over the baseline on this synthetic holdout."
        )

    return {
        "evaluation_type": "chronological_holdout",
        "data_type": "synthetic_demo_data",
        "train_records": int(len(train_records)),
        "test_records": int(len(test_records)),
        "train_start_date": train_dates[0].isoformat() if train_dates else None,
        "train_end_date": train_dates[-1].isoformat() if train_dates else None,
        "test_start_date": test_dates[0].isoformat() if test_dates else None,
        "test_end_date": test_dates[-1].isoformat() if test_dates else None,
        "model": {
            "name": "RandomForestRegressor",
            "mae": float(model_mae),
            "rmse": float(model_rmse),
            "r2": model_r2,
        },
        "baseline": {
            "name": "Site-Type Training Mean",
            "mae": float(baseline_mae),
            "rmse": float(baseline_rmse),
        },
        "mae_improvement_vs_baseline_percent": float(_safe_float(improvement)),
        "interpretation": interpretation,
        "limitations": [
            "Evaluation uses synthetic historical rental-demand data.",
            "Metrics demonstrate pipeline behaviour, not production Caterpillar accuracy."
        ],
        "data_leakage_check": data_leakage_check,
    }


def forecast_demand(history, current_assets):
    if not history:
        return []
    model = _build_model(history)
    available = defaultdict(int)
    for asset in current_assets:
        site_id = asset.get("site_id")
        equipment_type = asset.get("type")
        status = str(asset.get("status", "ACTIVE")).upper()
        if site_id in SITE_LIST and equipment_type in EQUIPMENT_TYPES and status not in {"BROKEN", "MAINTENANCE", "RETIRED"}:
            available[(site_id, equipment_type)] += 1
    latest_date = max(date.fromisoformat(str(record.get("date"))) for record in history if record.get("date"))
    forecast_date = latest_date + timedelta(days=7)
    rows = []
    for site_id in SITE_LIST:
        for equipment_type in EQUIPMENT_TYPES:
            if model is not None:
                predicted = _predict_one(model, site_id, equipment_type, forecast_date)
            else:
                subset = [
                    float(record.get("rental_count", 0))
                    for record in history
                    if record.get("site_id") == site_id and record.get("equipment_type") == equipment_type
                ]
                predicted = sum(subset) / max(len(subset), 1)
            available_assets = available.get((site_id, equipment_type), 0)
            rows.append({
                "site_id": site_id,
                "equipment_type": equipment_type,
                "predicted_demand": round(predicted, 2),
                "available_assets": available_assets,
                "shortage_or_surplus": round(predicted - available_assets, 2),
            })
    return rows
