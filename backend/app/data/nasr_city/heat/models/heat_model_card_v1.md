# Urban Heat Risk Prediction Model Card (v1)

## Model Purpose
This model predicts Land Surface Temperature (LST) anomalies (relative Urban Heat Island intensity) across 416 grid sectors in Nasr City, Cairo. It supports spatial mapping, identifying high-risk zones, and generating localized explanations for urban decision support.

## Data Sources
* **Observed Target:** Landsat 8 and Landsat 9 Collection 2 Level 2 Surface Temperature (ST_B10 thermal band), converted to Celsius.
* **Geospatial Features:**
  * JRC GHSL Built-Up footprints (built-up density).
  * ESA WorldCover land-cover ratios (tree canopy, grassland, bare land, water).
  * OpenStreetMap road network density and primary road presence.
  * WorldPop population density counts.
  * SRTM 30m digital elevation model.

## Target Definitions
* **Primary Target:** `heat_anomaly_c` (local zone surface temperature minus the day's scene median temperature).
* **Evaluation Target:** `heat_risk_class` (low, medium, high relative risk derived from LST anomalies and local population/road exposure factors).

## Landsat Authenticity Statement
> [!IMPORTANT]
> All training target rows used in this model are derived from verified Landsat observations, not fallback-generated LST values. The training labels reflect true satellite observed skin temperatures.

## Validation Strategy
Grouped cross-validation (5-Fold) was utilized to prevent feature leakage due to spatial and temporal autocorrelation:
1. **Scene-based split:** Grouped by `scene_id` to evaluate temporal generalization to unseen dates and weather events.
2. **Zone-based split:** Grouped by `zone_code` to evaluate spatial generalization to unseen geographic sectors.

## Selected Model Candidates
* Baseline: DummyRegressor (median)
* Linear: Ridge Regression (alpha=1.0)
* Tree Ensembles: RandomForestRegressor, ExtraTreesRegressor, GradientBoostingRegressor
* Selected best: **HistGradientBoosting_Default**

## Model Performance Summary (HistGradientBoosting_Default)
* **Scene Split Validation:**
  * Mean Absolute Error (MAE): 0.456 °C
  * Root Mean Squared Error (RMSE): 0.602 °C
  * R² Score: 0.909
  * Risk Class Accuracy: 91.4%
  * Risk Class Macro F1: 0.909
* **Zone Split Validation:**
  * Mean Absolute Error (MAE): 0.705 °C
  * Root Mean Squared Error (RMSE): 0.909 °C
  * R² Score: 0.799
  * Risk Class Accuracy: 85.2%
  * Risk Class Macro F1: 0.849
* **Generalization Gap (Scene vs Zone MAE):** 0.249 °C
* **Estimated Model Size:** 0.50 MB

## Explainability Methodology
* **Global Importance:** Feature importances and permutation importances identify top drivers across the entire city.
* **Local Importance:** Local explanations are compiled for every single observation. Real human-readable labels are mapped (e.g. "Built Environment Density" instead of "built_surface_mean") to render user-facing risk rationales in the dashboard.

## Known Limitations
* LST represents land skin temperature, not ambient air temperature. Skin temperatures on asphalt/concrete often exceed air temperature by 10-15 °C.
* Contextual weather features (wind, humidity, air temperature) are simulated context proxies.

## Disclaimer & Honesty Statement
> [!WARNING]
> This heat-risk layer estimates relative urban heat exposure from satellite land-surface temperature and geospatial features. It is not an official public-health heat warning system.
