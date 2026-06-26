# 3-5 Minute Presentation Script

This script provides a concise, professional speaking guide for demonstrating the Geo Weather (Nasr City) dashboard.

---

### 1. Opening & Problem Statement (Approx. 30 seconds)
"Good day. Urban centers like Cairo, and specifically dense districts like Nasr City, face mounting challenges from climate volatility. Sudden intense rainfall can compromise local road networks, while rapid urbanization drives severe micro-climate heat islands. 

Municipal emergency teams and urban planners often lack integrated, street-level views to assess these relative environmental risks dynamically. Traditional routing services do not consider localized weather hazard estimates when calculating paths, potentially leading transit vehicles into flooded segments."

---

### 2. System Overview (Approx. 45 seconds)
"To address this challenge, we developed the Geo Weather dashboard for Nasr City. This dashboard serves as an open-data-powered, decision-support prototype. 

It is divided into two primary operational modes: **Rain Risk** for precipitation-induced street obstructions, and **Heat Risk** for land surface temperature anomalies. The platform integrates real-time weather forecasts, open geographic datasets, and machine learning models to estimate relative risks across 416 individual grid zones in Nasr City."

---

### 3. Rain Risk and Routing (Approx. 60 seconds)
"Let's look first at our default Rain Risk mode. The system retrieves live meteorological metrics via the Open-Meteo API. If rainfall is forecasted, our model automatically adjusts the grid cells' risk profiles. 

If we plan a transit route—for example, selecting a local emergency hospital as our starting point—the system performs a route comparison. It calculates a standard shortest path alongside a safety-optimized route. The safe route dynamically avoids grid cells with elevated rain-impact risk, offering a safer alternative during high-water events."

---

### 4. Explainability (Approx. 45 seconds)
"A key feature of this twin is scientific explainability. When we select a route, the dashboard presents a clear breakdown of safety versus distance trade-offs, recommending the safest alternative based on live risk weights.

Furthermore, we can inspect individual grid zones. Clicking a cell reveals the precise local features driving its risk estimation—such as low elevation slope or high building density—preventing 'black box' model decisions."

---

### 5. Urban Heat Risk (Approx. 45 seconds)
"Switching the dashboard to Heat Risk mode transitions our visual focus to thermal hazards. Here, we display relative land surface temperature anomalies across Nasr City. 

We can select a high-risk zone to see its local drivers, such as high Built-Up Density or low Vegetation Canopy. The model detail panel shows that these predictions are powered by a HistGradientBoostingRegressor model trained on 4,932 real observed Landsat scene rows."

---

### 6. Real Data Sources & Limitations (Approx. 30 seconds)
"The system relies entirely on authentic, open environmental data. This includes OpenStreetMap for street topology, Landsat thermal bands, and ESA WorldCover land use maps. 

We want to emphasize that this system is a decision-support prototype. It does not replace official emergency dispatch authorities, and its calculations represent statistical estimates rather than verified street-level flood sensors."

---

### 7. Closing Value Statement (Approx. 15 seconds)
"In conclusion, by combining live meteorology, geospatial density markers, and explainable machine learning models, this system demonstrates how municipal planners can leverage open data to build safer, more resilient cities. Thank you."
