# CAT TrackIQ

CAT TrackIQ is a Python prototype for rental-equipment decision intelligence. It turns equipment telemetry and rental history into four practical outputs:

- utilization percentages for each asset
- transparent, rule-based anomaly records
- site and equipment-type demand forecasts
- prioritized reallocation recommendations with demo cost estimates

The project is intentionally small and library-oriented. It uses synthetic data to demonstrate the workflow and does not claim production Caterpillar accuracy.

## Project layout

```text
intelligence/
	anomaly.py          Rule-based anomaly detection
	forecasting.py      Synthetic history, forecasting, and evaluation
	recommendations.py  Reallocation scoring and recommendations
	utilization.py      Asset utilization calculation
tests/
	test_intelligence.py
```

## Requirements

- Python 3.10 or newer
- `scikit-learn`
- `pytest` for development and verification

## Setup

From the repository root, create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install scikit-learn pytest
```

## Run the tests

```powershell
python -m pytest
```

The tests cover utilization calculations, anomaly rules, synthetic-history generation, demand forecasting, recommendation scoring, serialization, and forecast evaluation.

## Quick start

The main functions accept ordinary Python lists and dictionaries, so they can be called from a service, notebook, or application layer:

```python
from intelligence.anomaly import detect_anomalies
from intelligence.forecasting import (
		evaluate_forecast_model,
		forecast_demand,
		generate_synthetic_history,
)
from intelligence.recommendations import generate_recommendations
from intelligence.utilization import calculate_utilization

assets = [
		{
				"equipment_id": "EQX1001",
				"type": "Excavator",
				"site_id": "S003",
				"operator_id": "OP101",
				"status": "ACTIVE",
				"engine_hours_per_day": 1.5,
				"idle_hours_per_day": 10,
		}
]

history = generate_synthetic_history(days=180, seed=42)
anomalies = detect_anomalies(assets)
forecasts = forecast_demand(history, assets)
recommendations = generate_recommendations(assets, forecasts, anomalies)
evaluation = evaluate_forecast_model(history)

print(calculate_utilization(assets[0]))
print(anomalies)
print(forecasts)
print(recommendations)
print(evaluation["model"])
```

## Input contracts

### Asset records

Asset dictionaries should provide `equipment_id`, `type`, `site_id`, `operator_id`, `status`, `engine_hours_per_day`, and `idle_hours_per_day`. `forecast_demand` also uses the asset `type` and `site_id` to count available equipment. Assets with status `BROKEN`, `MAINTENANCE`, or `RETIRED` are excluded from availability counts.

### History records

Each history record must contain:

```python
{
		"date": "2025-06-01",
		"site_id": "S001",
		"equipment_type": "Excavator",
		"rental_count": 5,
}
```

The forecasting module currently recognizes sites `S001` through `S006` and equipment types `Excavator`, `Bulldozer`, `Crane`, and `Grader`. Invalid history rows are ignored during model construction.

## Forecast evaluation

`evaluate_forecast_model` uses a chronological holdout: earlier dates train the model and later dates form the test set. This avoids mixing future observations into training data.

The model is a `RandomForestRegressor`. It is compared with a site-and-equipment-type training-mean baseline using:

- MAE, the primary metric because demand is measured in equipment units
- RMSE, which gives larger errors more weight
- R2, when it is numerically meaningful

The returned evaluation record includes train/test date boundaries, record counts, model and baseline metrics, improvement versus baseline, a data-leakage check, and known limitations.

## Important limitations

- Forecast history is synthetic and generated with a fixed default seed.
- Demo rental rates and relocation costs are assumptions in INR, marked with `pricing_type: "DEMO_ASSUMPTION"`.
- The forecast predicts seven days after the latest history date.
- No database, API, authentication, persistence, or production monitoring is included.
- Replace the synthetic history and demo pricing with validated business data before using recommendations operationally.

## License

No license has been declared for this prototype.
