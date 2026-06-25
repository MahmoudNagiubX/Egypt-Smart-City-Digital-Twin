# Model Card — Nasr City Weather Impact ML Model

## Model Purpose
This machine learning model is designed as a spatial-temporal surrogate to predict urban risk outcomes under severe weather. It maps multi-source environmental variables directly to risk severity classes to prioritize emergency response.

## Target
* **Target Column**: `data_driven_weather_impact_score`
* **Interpretation**: This is an engineered target derived from real observed weather, satellite rainfall, geospatial built-up, landcover, population exposure, elevation, and road network features. It is **NOT** an official street-level flood incident label.

## Training Data
* **Dataset**: `real_observed_training_dataset.csv`
* **Row Count**: 12,480
* **Sources**:
  - Open-Meteo multi-year historical weather (2015-2025)
  - NASA GPM IMERG satellite precipitation
  - SRTM elevation/slope DEM
  - JRC GHSL built-up surface density
  - ESA WorldCover land cover
  - WorldPop population exposure
  - OpenStreetMap road network

## Features
The model utilizes 49 numeric features across several key categories:
1. **Weather**: hourly rainfall, rolling accumulations (3h/6h/24h), temperature, apparent temperature, relative humidity, wind speed, hour, and rush hour indicator.
2. **Satellite Rain**: GPM IMERG mean, max, and sum precipitation.
3. **Terrain**: elevation mean, min, max, stdDev, slope mean, min, max, and low elevation/slope hazard scores.
4. **Built-up Density**: JRC GHSL built surface mean, sum, max, non-residential mean/sum, and ratios.
5. **Land Cover**: ESA WorldCover ratios (trees, grassland, built-up, bare soil, water) and dominant class.
6. **Exposure**: WorldPop population sum, mean, and density proxy.
7. **Road Network**: segment count, lengths, OSM class counts, base speeds, and travel times.

## Models Trained
* **Baseline mean predictor**: predicts the training set mean.
* **Random Forest Regressor** (300 estimators, min_samples_leaf=2).
* **HistGradientBoosting Regressor** (300 max_iter, learning_rate=0.05).

## Split Strategy
An **event-based split** (`GroupShuffleSplit` on `event_id`) was used instead of a random row split. Cairo rainfall is highly clustered; split by `event_id` ensures that training and testing sets contain completely distinct weather events. This prevents severe data leakage and gives a realistic estimate of model generalization to unseen storms.
* **Train Rows**: 9,984 (24 events)
* **Test Rows**: 2,496 (6 events)
* **Train/Test Group Overlap**: none (0 overlap events)

## Metrics (Test Evaluation)
- **Baseline (Mean Predictor)**:
  - MAE: 0.18780
  - RMSE: 0.23126
  - R²: -0.11547
  - Severity Accuracy: 52.12%
- **Random Forest**:
  - MAE: 0.01739
  - RMSE: 0.02876
  - R²: 0.98275
  - Severity Accuracy: 98.04%
- **HistGradientBoosting**:
  - MAE: 0.03384
  - RMSE: 0.05034
  - R²: 0.94714
  - Severity Accuracy: 94.99%

* **Best Model Selected**: **Random Forest**

## Limitations
* **No Official Incident Labels**: Street-level verified flood incident logs were not available. The target is an engineered hazard-exposure-vulnerability risk target.
* **Prototype Output**: The model output is suitable for prototype decision-support systems and spatial analysis. It should not be used as the sole basis for real-time emergency routing or deployment warnings.
* **GHSL Partial Fallback**: GHSL satellite density features failed on a single grid cell (`NSR-GRID-023`) and used partial fallback; this has a negligible effect on performance but is audited for transparency.

## Ethical and Practical Use
* Do not use for automated emergency dispatch without human verification.
* The model is intended as a planning utility to flag priority zones under storm scenarios, not as a safety-critical real-time forecast.

## Future Improvements
* Integration of official flood incident logs.
* Inclusion of municipal drainage, sewage, and elevation depression networks.
* Real-world validation against sensor networks.
* Calibration using field observations.
