# CAT-TrackIQ

### Equipment Demand Forecasting, Anomaly Detection & Decision Intelligence

CAT-TrackIQ is a machine-learning and decision-intelligence prototype designed for rental equipment operations. The project focuses on forecasting equipment demand, identifying unusual utilization patterns, and generating recommendation signals to support better equipment allocation.

> **Current scope:** This repository focuses on the **machine-learning and decision-intelligence component** of CAT-TrackIQ and uses synthetic demonstration data. It does not represent a production Caterpillar system.

---

## 📌 Problem Statement

Rental equipment businesses need to balance equipment availability across different locations and equipment types.

Poor demand visibility can lead to:

- Equipment shortages at high-demand sites
- Underutilized equipment
- Inefficient equipment allocation
- Delayed operational decisions
- Difficulty identifying unusual utilization patterns

CAT-TrackIQ explores how machine learning and data-driven decision support can help address these challenges.

---

## 🚀 Key Features

### 1. Demand Forecasting

A **Random Forest Regressor** is used to forecast future equipment demand.

The forecasting pipeline:

1. Processes historical rental data
2. Uses earlier observations for training
3. Tests the model on later unseen observations
4. Generates equipment demand predictions
5. Evaluates predictions against actual demand

The chronological evaluation approach is designed to better represent a real forecasting scenario where the model predicts future demand from historical information.

---

### 2. Anomaly Detection

The project includes anomaly detection logic to identify unusual equipment utilization or operational patterns.

These signals can help highlight situations that may require further investigation.

The current implementation uses rule-based logic rather than claiming a production-grade anomaly detection system.

---

### 3. Equipment Reallocation Recommendations

The project generates recommendation signals based on demand and equipment conditions.

These recommendations are intended as **decision support** rather than autonomous actions.

The goal is to help identify potential opportunities to move or reallocate equipment where demand may be higher.

---

## 📊 Forecast Evaluation

The forecasting model uses a **chronological holdout strategy** instead of a random train-test split.

### Why chronological evaluation?

In a real forecasting problem, future data should not be used to train the model before making predictions.

Therefore:

```text
Earlier Historical Data
        ↓
     Training
        ↓
Random Forest Model
        ↓
Later Unseen Data
        ↓
    Forecasts
        ↓
   Evaluation

This approach better reflects the actual task of predicting future rental demand.

📏 Evaluation Metrics
Mean Absolute Error (MAE)

MAE is the primary evaluation metric because equipment demand is measured in equipment-count units.

It represents the average absolute difference between predicted and actual demand.

Root Mean Squared Error (RMSE)

RMSE is also reported to provide additional insight into prediction errors and gives greater weight to larger errors.

R² Score

R² is used as an additional measure of how much variation in the target variable is explained by the model.

🆚 Baseline Comparison

The Random Forest forecasting model is compared against a simple baseline.

Baseline

The baseline uses the mean demand for the same site and equipment type, calculated using the same earlier training period.

This provides a simple reference point for determining whether the machine-learning model provides value beyond a basic historical average.

Historical Data
      │
      ├── Random Forest Forecast
      │
      └── Site + Equipment Mean Baseline
                    │
                    ↓
              Compare Results
                    │
                    ↓
             MAE / RMSE / R²
🧠 Methodology

The current workflow follows these stages:

Load historical equipment demand data
Prepare and process the data
Separate training and future test periods chronologically
Create the required forecasting features
Train the Random Forest model
Generate predictions for the unseen period
Calculate MAE, RMSE and R²
Compare results with the historical mean baseline
Identify unusual utilization patterns
Generate equipment reallocation signals
Use the results as decision-support information
🌲 Why Random Forest?

Random Forest was selected as the initial forecasting model because it can:

Capture nonlinear relationships
Handle interactions between features
Work well with structured/tabular data
Require relatively little preprocessing
Provide a strong baseline for experimentation

The model is intended as a starting point rather than a claim that Random Forest is optimal for all rental-demand forecasting scenarios.

🛠️ Tech Stack
Technology	Purpose
Python	Core development
Pandas	Data processing
NumPy	Numerical operations
Scikit-learn	Machine learning
Random Forest Regressor	Demand forecasting
MAE	Primary evaluation metric
RMSE	Error evaluation
R²	Additional model evaluation
Synthetic Data	Demonstration and testing
📂 Project Structure

The exact structure may vary depending on the implementation. A typical organization is:

CAT-TrackIQ/
│
├── data/
│   └── synthetic/
│
├── notebooks/
│   └── forecasting_analysis.ipynb
│
├── src/
│   ├── forecasting/
│   ├── anomaly_detection/
│   └── recommendations/
│
├── README.md
└── requirements.txt

Update this section if your repository uses different file or folder names.

📈 Current Evaluation Scope

The current experiments use synthetic demonstration history.

Therefore, the results should be interpreted as validation of:

The forecasting pipeline
The evaluation methodology
The model-vs-baseline comparison
The overall decision-support approach

They should not be interpreted as production-level Caterpillar forecasting accuracy.

For a real deployment, the same evaluation process would be repeated using actual historical rental data, with the model retrained on the relevant historical period before generating forecasts.

⚠️ Limitations

The current prototype has several limitations:

Uses synthetic rather than real rental history
Does not represent production Caterpillar data
Limited historical context
No production deployment
No live equipment telemetry integration
Recommendation signals are not autonomous actions
Anomaly detection currently uses rule-based logic

These limitations are intentional and define the current scope of the prototype.

🔮 Future Improvements

Potential future improvements include:

Integrating real rental transaction data
Adding lag and rolling-window demand features
Comparing Random Forest with XGBoost and time-series models
Evaluating forecasts across individual sites and equipment types
Adding prediction confidence intervals
Implementing statistical or machine-learning-based anomaly detection
Adding model explainability
Monitoring model drift
Building an interactive analytics dashboard
Deploying the forecasting pipeline through an API
Automating model retraining and evaluation
Adding human-in-the-loop approval for reallocation recommendations
🎯 Key Takeaway

CAT-TrackIQ explores a data-driven workflow for rental equipment decision support:

Forecast Demand
      ↓
Detect Unusual Patterns
      ↓
Evaluate Model Performance
      ↓
Generate Recommendation Signals
      ↓
Support Better Equipment Decisions

The project demonstrates how machine learning can be combined with structured operational logic to turn historical equipment data into actionable decision-support insights.
