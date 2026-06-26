# Limitations and Future Work

This document outlines the current limitations of the Nasr City Weather-Impact and Heat Risk Digital Twin system and details planned expansion vectors.

---

## 1. System Limitations

### Geospatial and Meteorological Data Dependencies
* **Landsat Scene Constraints:** The urban heat risk layer's baseline relies on Landsat thermal infrared sensors. Cloud cover and satellite revisit schedules restrict live thermal scene availability, necessitating regression models to estimate intermediate changes.
* **Precipitation Proxies:** In the absence of real-time radar reflection data, rain risk levels are calculated using forecast values from the Open-Meteo API as statistical proxies for actual storm density.
* **OpenStreetMap Attribute Density:** Topological routing parameters (e.g. road widths, surface materials, and drainage configurations) are constrained by OSM volunteer edits and may contain gaps.

### Operational and Scientific Honesty
* **Decision-Support Focus:** This digital twin is a decision-support prototype. It does NOT serve as an official emergency dispatch system or certified public-health hazard warning mechanism.
* **Validation Gaps:** The correlation between predicted road hazard indices and actual physical flooding events requires validation against historical municipal emergency incident databases, which are currently unavailable to the system.

---

## 2. Future Work

### Real-Time IoT Integration
* **Rain and Flood Sensors:** Connect localized rain gauge stations and ultrasonic street water-level sensors directly to the FastAPI backend to replace forecast-derived proxies.
* **Urban Heat Sensors:** Interface with municipal IoT thermal sensors to validate remote sensing Landsat land surface temperatures with near-surface ambient air temperatures.

### System Scalability and Coverage
* **Regional Expansion:** Expand the geospatial models beyond Nasr City to encompass the wider Cairo Governorate and the New Administrative Capital.
* **Granular Elevation Models:** Integrate higher-resolution Digital Elevation Models (DEMs), such as SRTM or LiDAR-derived profiles, to improve hydrological accumulation calculations.

### Advanced Features
* **Active Alert Notifications:** Establish an automated system that pushes SMS or email alerts to municipal dispatchers when a grid zone crosses into the "High Risk" classification.
* **Dedicated Mobile App:** Build a cross-platform mobile companion app for field officers to submit real-time geo-tagged hazard pictures that feed back into the validation engine.
* **Admin Dashboard Controls:** Design a secure administrative portal allowing operators to manually override road hazard states based on ground-truth reports.
