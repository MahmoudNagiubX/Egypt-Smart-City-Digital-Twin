# API Documentation

The backend service is exposed via a REST API implemented in FastAPI.

* **API Path Prefix:** `/api/weather-impact`

---

## 1. System Health and Metadata

### GET `/health`
* **Purpose:** Returns the status of the weather-impact module and checks output directory file availability.
* **Response Summary:** `{"module_name": "...", "status": "healthy", "outputs_available": {...}}`

### GET `/heat/health`
* **Purpose:** Returns the status and availability of the Urban Heat Risk model and data layers.
* **Response Summary:** `{"status": "ok", "model_available": true, "latest_layer_available": true}`

---

## 2. Weather & Prediction Layers

### GET `/weather/live`
* **Purpose:** Retrieves live current weather forecasts and 7-day windows for Nasr City from Open-Meteo.
* **Response Summary:** Contains `location`, `current` (temp, relative humidity, rain), and `forecast_window` objects.

### GET `/layers/predictions/live`
* **Purpose:** Retrieves the live gridded risk calculations as a GeoJSON `FeatureCollection`.
* **Response Summary:** Returns 416 grid features containing calculated risk classes (Low, Medium, High).

### GET `/layers/predictions/latest`
* **Purpose:** Retrieves the latest stored event prediction layer.

---

## 3. Search & Routing

### GET `/search?q={query}`
* **Purpose:** Queries local OSM points-of-interest and streets inside Nasr City.
* **Example:** `/search?q=hospital`
* **Response Summary:** List of search results matching the query, containing coordinate latitudes, longitudes, and category labels.

### POST `/explain/route`
* **Purpose:** Evaluates standard vs. safe routing coordinates, calculating safety indicators and travel delays.
* **Payload:** `{"origin": {"lat": 30.061, "lon": 31.344}, "destination": {"lat": 30.044, "lon": 31.365}, "mode": "live"}`
* **Response Summary:** Contains calculated path arrays, recommendations, safety scores, and travel time comparison deltas.

---

## 4. Heat Risk and Explainability

### GET `/heat/layer/latest`
* **Purpose:** Returns the relative temperature anomaly layers as a GeoJSON `FeatureCollection`.

### GET `/heat/summary`
* **Purpose:** Summarizes relative heat risks across the grid (counts of low/medium/high risk zones) and returns the hottest zone code.

### GET `/heat/model/summary`
* **Purpose:** Details model statistics, target metadata, top feature contributions, and Landsat observation counts (4,932 rows).

### GET `/heat/explain/zone/{zone_code}`
* **Purpose:** Evaluates local risk factors for a specific zone, returning feature importance values and explanatory labels.
* **Response Summary:** `{"status": "ok", "zone_code": "NSR-GRID-382", "top_factors": [{"factor": "...", "label": "Built-Up Density", "value": 0.85}]}`
