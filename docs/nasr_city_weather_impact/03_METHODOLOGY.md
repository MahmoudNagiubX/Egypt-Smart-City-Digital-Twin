# System Methodology

This document details the mathematical logic, spatial calculations, and machine learning structures implemented in the Geo Weather dashboard.

---

## 1. Spatial Grid and Zonal Aggregation
Nasr City's boundary is gridded into a 416-cell spatial polygon structure. Every zone contains:
* Baseline topological metrics (mean elevation, slope).
* Built-up density metrics (building coverage, road ratios).
* Spectral vegetation and building indexes derived from satellite observations.

---

## 2. Weather-Impact Scoring
The road hazard index maps live hourly precipitation to specific road delay categories:
$$\text{Safety Score} = f(\text{Rain Intensity}, \text{Road Classification}, \text{Elevation Slope}, \text{Zone Building Density})$$
These variables are passed to a Random Forest classifier that generates three risk classes: **Low**, **Medium**, and **High**.

---

## 3. Safety-Weighted Route Calculation
Standard routing services run shortest-path algorithms based only on physical distance. 

Our emergency routing engine applies safety coefficients:
$$\text{Weight}_{e} = \text{Length}_{e} \times (1 + \alpha \times \text{RiskScore}_{e})$$
Where:
* $\text{Length}_{e}$ is the segment length in meters.
* $\text{RiskScore}_{e}$ is the estimated safety hazard score (0 to 1) of the zone containing the edge $e$.
* $\alpha$ is a scaling sensitivity coefficient (set to 5.0 for emergency routing).

A safety-optimized safe path is then calculated using Dijkstra's algorithm over this weighted network, routing vehicles around high-risk zones.

---

## 4. Urban Heat Risk Model
The heat anomaly regressor predicts relative temperature deviations ($\text{heat\_anomaly\_c}$):
* **Model:** `HistGradientBoostingRegressor` (selected for its robust handling of spatial feature interactions).
* **Inputs:** GHSL Built-Up Density, ESA Tree Cover Ratio, Normalized Difference Vegetation Index (NDVI), Normalized Difference Built-up Index (NDBI), and seasonal parameters.

---

## 5. Explainability Panels
* **Local Explainability:** When a zone is clicked, the system computes the exact feature contribution values (local feature importances) to explain that specific zone's anomaly value.
* **Global Explainability:** Displays the top feature contributions (global model importances) showing that Built-Up Density and Vegetation Canopy are dominant factors.
* **Mapped Labels:** Mappings convert database column names (like `built_surface_mean`) to clean user-facing labels like "Built-Up Density".
