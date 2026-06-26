# Scope Lock — Nasr City Weather-Impact Emergency Mobility Module

This document locks the final delivery scope and details features included, features excluded, and scientific honesty guidelines.

---

## 1. Final Delivery Scope
The repository delivers one integrated system module:
**Nasr City Weather-Impact and Heat Risk Emergency Mobility Module**

### Core Included Features
* **Nasr City Boundaries & 500m Grid:** 416-cell gridded spatial model of the district.
* **OpenStreetMap (OSM) Road Network:** Full road network topologies extracted using `osmnx`.
* **Hospitals & Emergency Facilities:** Indexed coordinates of critical POIs for search and routing destination targets.
* **Weather Forecast APIs:** Live connection to Open-Meteo current condition, forecast, and AQI layers.
* **Precipitation-Impact Road Delay Model:** Estimated road hazard risk grids (Low, Medium, High).
* **Emergency Safety Route Optimization:** Weighted routing algorithm calculation (Dijkstra) prioritizing safety index over pure physical distance.
* **Urban Heat Anomaly Layer:** Landsat-derived Celsius anomaly layers.
* **Heat Explainability Side Panels:** Local and global feature importance charts based on a `HistGradientBoostingRegressor` model trained on 4,932 real observed training rows.

---

## 2. Excluded Features (Out of Scope)
* **Road Damage Detection:** No machine learning analysis of street surface cracking.
* **Arabic Complaint NLP:** No citizen complaint text classification pipelines.
* **Garbage and Trash Detection:** No visual debris classification routines.
* **Multi-District Expansion:** Restricted strictly to the Nasr City administrative boundary.
* **Official Emergency Dispatch:** No connection to state dispatch systems.

---

## 3. Repository Safety Rules
* Do not modify or replace the root `README.md`.
* Deliver all module-specific documentation files under `docs/nasr_city_weather_impact/`.
* Keep the code clean and avoid unnecessary abstraction layers.

---

## 4. Scientific Honesty Statement
This decision-support prototype estimates relative environmental risk using open data, spatial indices, scenario calculations, and machine learning regressors. 

Because verified street-level flood incident records for Nasr City are unavailable, the rain models are trained on engineered weak labels. The heat models are trained on 4,932 verified Landsat observations. The system is a decision-support dashboard and does not represent an official emergency authority or public-health warning alert.
