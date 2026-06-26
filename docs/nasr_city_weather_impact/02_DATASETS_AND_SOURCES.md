# Datasets and Sources

This document lists the baseline geographic and meteorological datasets integrated into the Nasr City Digital Twin.

---

## 1. Integrated Geospatial and Weather Datasets

### Open-Meteo API
* **Role:** Fetches live weather conditions, hourly precipitation forecasts, daily parameters, and Air Quality Index (AQI) values.
* **Update Interval:** Queried dynamically via FastAPI endpoints.

### OpenStreetMap (OSM)
* **Role:** Supplies district boundaries, road network geometries, and location coordinates for emergency services (hospitals, civil defense, pharmacies).
* **Extraction Tool:** Configured via `osmnx` libraries targeting Nasr City boundary polygons.

### Landsat 8/9 Thermal Infrared (TIRS)
* **Role:** Core source for land surface temperature (LST) and Celsius temperature anomalies.
* **Data Volume:** 4,932 verified observations extracted from cloud-free scenes.

### ESA WorldCover (10m Resolution)
* **Role:** Mapped land use variables such as tree cover density, grass cover, built-up pixels, and open water bodies across the Nasr City grid cells.

### Global Human Settlement Layer (GHSL)
* **Role:** Supplies building footprint compactness and human settlement densities to model surface reflectivity.

---

## 2. Generated Codebase Data Files
All processed assets are stored under `backend/app/data/nasr_city/`:
* `maps/nasr_city_boundary.geojson`: Extracted OSM boundaries.
* `maps/nasr_city_grid_500m.geojson`: The 416 individual zone grid polygons.
* `maps/nasr_city_roads.geojson` & `nasr_city_roads_zones.geojson`: OSM road network segments.
* `processed/real_observed_training_dataset.csv`: 12,480 rows of engineered training metrics.

---

## 3. Data Authenticity Statement
The heat risk model has been trained exclusively on 4,932 real observed Landsat scene rows. Standard fallback dataset rows were recorded as `0`, confirming that no simulated fallback rows were introduced. No fake data was created, and all environmental metrics reflect verified geological observations.
