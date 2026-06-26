# Presentation and Demo Script

This document provides the presenter with a structured walk-through script for live demonstrations and recordings.

---

## 1. Demo Flow Summary (12 Steps)
1. **Launch App:** Open browser, land on welcome page.
2. **Dashboard Entrance:** Click launch, verify dashboard mounts.
3. **Live Weather Check:** View weather conditions in top-left sidebar.
4. **Rain Risk Mode:** Inspect baseline rain overlay grid.
5. **Overlay Explanation:** Hover over cell, view calculated risk tooltip.
6. **Search POI:** Type "hospital" in search box, select result.
7. **Fly-To Camera:** Watch map fly to coordinate center.
8. **Origin/Destination Pins:** Assign coordinate pins for routing.
9. **Calculate Safe Route:** Compare shortest path (blue) and safe path (green).
10. **Routing Recommendation:** Review safety score difference card.
11. **Switch to Heat Mode:** Toggle "Heat Risk" mode, see map turn red/orange.
12. **Explain Heat Anomaly:** Click red cell, read Built-Up Density drivers and Model Info cards.

---

## 2. Speaking Script Outline (3-5 Minutes)

### Introduction
> "Welcome. Densely populated urban centers like Nasr City in Cairo face growing climate risks, including sudden rain-induced road blockages and micro-climate heat islands. 
> 
> The Smart Digital Twin dashboard serves as an open-data-powered, decision-support prototype to help municipal dispatchers and urban planners evaluate these environmental risks."

### Rain Mode & Safety Routing
> "Under default Rain Risk mode, the platform combines live forecast data from the Open-Meteo API with building density and slope metrics. 
> 
> If we plan an emergency transit route using our OSM search box, the engine calculates a standard shortest path alongside a safety-optimized route. The safe route dynamically redirects vehicles around high-hazard zones."

### Heat Risk & Model Details
> "Toggling the Heat Risk layer displays micro-zone land surface temperature anomalies. 
> 
> Clicking a hot zone reveals its local environmental drivers, such as high building density. Our Model Info section details the `HistGradientBoostingRegressor` model, which was trained on 4,932 real observed Landsat scene rows."

### Conclusion
> "This digital twin demonstrates how municipal agencies can leverage explainable machine learning models and open datasets to build safer, more resilient cities. Thank you."
