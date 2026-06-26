# Project Rename Preservation Note

This note documents the design decision to decouple the public project branding name from the internal technical folder structures, API routes, and machine learning files.

---

## 1. Public vs. Internal Naming
* **Public Branding Name:** **Geo Weather**
* **Subtitle:** *Nasr City Weather Impact & Urban Heat Risk Dashboard*

---

## 2. Preserved Technical Configurations
To ensure API stability, maintain test coverage, and prevent broken python module imports, the following names have been intentionally preserved:
* **Python Package Name:** `backend/app/weather_impact/` remains unchanged.
* **API Router Route Prefix:** `/api/weather-impact` remains unchanged.
* **Documentation Folder Name:** `docs/nasr_city_weather_impact/` remains unchanged.
* **Trained Model Filenames:** Joblib files (`weather_impact_rf_model.joblib`, `heat_anomaly_hgb_model.joblib`) remain unchanged.
* **Geospatial Data Folders:** Folder paths containing OSM and Landsat shapefiles remain unchanged.
* **Git Repository Remote & Branch:** Branch name remains `feature/nasr-city-weather-impact-module`.
