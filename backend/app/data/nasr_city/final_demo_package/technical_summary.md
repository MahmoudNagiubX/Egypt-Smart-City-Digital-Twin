# Digital Twin - Technical Summary

This document provides a technical specification of the Nasr City Weather-Impact and Heat Risk Digital Twin system.

---

## 1. Technological Stack

### Frontend Dashboard
* **Framework:** React 19 / Vite 8 / TypeScript 6
* **Map Engine:** MapLibre GL (`maplibre-gl` ^5.24.0) with custom GeoJSON vector layers and dynamic styling.
* **Layout & Theme:** Vanilla CSS / TailwindCSS / Next-themes for seamless mode transitions.
* **State Management:** Custom React hooks, query parameters, and component-level states.
* **Visual Components:** Vaul drawer elements, Lucide-React icons, and custom scrollbar aesthetics.
* **Search & Location:** Integrated SearchBox autocomplete linked directly to custom OpenStreetMap indexing.
* **Explainability:** Tabbed interactive sidebar panels updating based on map click coordinates.

### Backend Services
* **Framework:** FastAPI / Uvicorn (runtime environment: Python >=3.11, <3.12).
* **Package Architecture:** Modular `weather_impact` namespace split into dedicated submodules:
  * `router.py`: API routing contracts and request/response validations.
  * `service.py`: Business logic coordinating geo, heat, and routing.
  * `geo.py`: Shapefiles, grid boundaries, and spatial geometry operations.
  * `routing.py`: Custom safety-weighted routing algorithm over OpenStreetMap network.
  * `heat.py` & `heat_model.py`: Model inference engines and training hooks.
  * `explain.py` & `heat_explain.py`: Model explainability calculations and feature mapping.
  * `weather.py`: Open-Meteo external service integrations.

---

## 2. Machine Learning Models

### Weather-Impact Model
* **Algorithm:** Ridge Regression and Random Forest models.
* **Purpose:** Evaluates road routing risk values (Low, Medium, High) based on precipitation forecast, local elevation slope, building density, and road infrastructure classifications.

### Urban Heat Risk Model
* **Algorithm:** `HistGradientBoostingRegressor` (from `scikit-learn`).
* **Target variable:** `heat_anomaly_c` (relative land surface temperature anomaly in degrees Celsius).
* **Training Rows:** 4,932 verified Landsat scene observations.
* **Fallback rows:** 0 (indicates high data authenticity; fallback models were not required).
* **Primary Features:** Built-Up Density, Vegetation Canopy, Normalized Difference Vegetation Index (NDVI), Normalized Difference Built-up Index (NDBI), and seasonal identifiers.

---

## 3. Integrated Data Sources
* **Open-Meteo API:** Live hourly weather, 7-day daily forecasts, and gridded Air Quality Indices (AQI).
* **OpenStreetMap (OSM):** Road network network topologies and geocoded emergency point-of-interest configurations.
* **Landsat (USGS):** Remote sensing thermal and multi-spectral bands.
* **ESA WorldCover:** Tree cover, grass cover, built-up surfaces, and water body classifications.
* **Global Human Settlement Layer (GHSL):** Historical built-up surfaces and urban expansion grids.
* **WorldPop:** Gridded population counts for spatial hazard normalization.

---

## 4. Verification & Testing Metrics
* **Backend Pytest Count:** 146 / 146 tests passed.
* **Frontend Vitest Count:** 43 / 43 tests passed.
* **Frontend Build Status:** Success (`tsc -b && vite build` completes without warnings or errors).
* **Python Static Analysis:** 100% compiled successfully via `compileall`.
