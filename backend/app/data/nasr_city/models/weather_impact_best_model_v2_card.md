# Model Card — Nasr City Weather Impact ML Model V2

## Model Purpose
This machine learning model acts as a spatial-temporal surrogate to predict relative urban weather-impact risk scores for emergency response prioritization.

## Target Definition and Honesty Note
* **Target Column**: `data_driven_weather_impact_score`
* **Limitation**: **The model predicts an engineered weather-impact risk score derived from real weather, satellite, road, and exposure features. It is not trained on verified official flood incident labels.**
* **Interpretation**: The target is an engineered index representing exposure, vulnerability, and satellite rain hazards. It indicates relative risk rather than real verified flood depths.

## Training Dataset
* **Dataset V2 Path**: `backend/app/data/nasr_city/models/weather_impact_training_dataset_v2.csv`
* **Rows**: 12480
* **Features**: 77 (includes weather ratios, temporal sin/cos, spatial flags, and physical hazard-exposure interaction terms).

## Validation Strategy
* An event-based split (`GroupShuffleSplit` on `event_id`) was used to validate temporal generalization. 
* A zone-based split (`GroupShuffleSplit` on `zone_code`) was used to validate geographical generalization and evaluate spatial data leakage.

## Model Benchmarking & Performance
* **Ridge Regression Baseline**: Event MAE = 0.00001, Zone MAE = 0.00000
* **Random Forest Tuned**: Event MAE = 0.01704, Zone MAE = 0.01671
* **Extra Trees Tuned**: Event MAE = 0.02097, Zone MAE = 0.01365
* **HistGradientBoosting Tuned**: Event MAE = 0.01286, Zone MAE = 0.01016

## Selected Model
* **Model Selected**: **Ridge Baseline**
* **Weighted Score**: 0.74921
* **Reason**: Selected using a weighted multi-metric framework balancing event test performance ($30\%$), zone test generalization ($20\%$), Severity Macro F1 ($20\%$), generalization gap ($15\%$), model file size ($10\%$), and ease of explainability ($5\%$). The tuned hyperparameters significantly reduce model file size (to 0.003 MB) compared to the baseline 96.5 MB model.

## Explainability Methods
* Global permutation importance was calculated on the unseen event test split to identify the strongest indicators.
* Local rule-based rank explanations were exported for every grid zone, mapping physical reasons (e.g., elevation sinks, impervious built-up density, and 24h rainfall) to predicted risk classes.

## Known Limitations
* Relies on engineered weak targets due to lack of municipal flood incident databases.
* Static topography features lead to spatial autocorrelation (generalization gap between event split and zone split).
* The model output is a decision-support prototype and must not be used as official emergency dispatch authority.

## Future Improvements
1. Integration of official Cairo flood incident logs.
2. Infiltration mapping via physical municipal drainage and sewage network overlays.
3. Live traffic congestion feeds.
4. IoT street sensor feeds.
5. Urban heat-risk and thermal comfort model integration.
