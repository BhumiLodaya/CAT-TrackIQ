# CAT TrackIQ

CAT TrackIQ is a rental equipment tracking and decision intelligence prototype for forecasting demand, detecting anomalies, and recommending reallocations.

## Forecast Evaluation

The demand forecasting model is evaluated by using a chronological holdout rather than a random split. The model is trained on earlier dates and tested on later unseen dates, which reflects the real forecasting task of predicting future demand.

The primary metric is MAE, because rental demand is measured in equipment-count units. RMSE is also reported for completeness. The Random Forest forecast is compared against a simple site-and-equipment-type mean baseline trained on the same earlier period. The evaluation currently uses synthetic demo history, so it validates the pipeline behavior and methodology rather than claiming production Caterpillar accuracy. In a real deployment, the same evaluation process would be rerun using actual rental history and the model would be retrained on the relevant historical period before forecasting.
