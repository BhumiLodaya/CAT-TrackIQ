# CAT-TrackIQ

### Equipment Demand Forecasting, Anomaly Detection & Decision Intelligence

CAT-TrackIQ is a machine learning prototype for rental equipment decision
intelligence. The project explores how historical equipment usage data can be
used to forecast future demand, identify unusual equipment behavior, and
support data-driven equipment allocation decisions.

> **Current scope:** This repository focuses on the machine learning and
> decision-intelligence component of CAT-TrackIQ. The forecasting model and
> evaluation pipeline were developed using synthetic demonstration data.

---

## Problem

Rental equipment fleets operate across different sites, equipment types, and
time periods. Poor visibility into future demand can lead to:

- Equipment being underutilized
- Equipment shortages at high-demand sites
- Unnecessary idle time
- Inefficient equipment allocation
- Delayed responses to changing demand

CAT-TrackIQ explores whether historical rental patterns can be transformed into
useful forecasts and signals that support better equipment allocation.

---

## What This Project Does

The current ML pipeline focuses on three core capabilities:

### 1. Demand Forecasting

A **Random Forest regression model** is used to forecast future equipment
demand based on historical patterns.

The forecasting workflow:

```text
Historical Equipment Data
          ↓
Data Preparation
          ↓
Feature Engineering
          ↓
Chronological Train/Test Split
          ↓
Random Forest Model
          ↓
Future Demand Forecast
          ↓
Evaluation
