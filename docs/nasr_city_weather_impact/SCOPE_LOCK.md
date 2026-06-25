# Scope Lock — Nasr City Weather-Impact Emergency Mobility Module

## Final Delivery Scope

For the 2026-07-02 deadline, this repository will deliver one complete module:

Nasr City Weather-Impact Emergency Mobility Module.

## Core Features

* Nasr City boundary and 500m grid
* OpenStreetMap road network
* Hospitals, clinics, and emergency facilities
* Weather data and rainfall scenarios
* Flood risk zones
* Road delay layer
* Emergency route optimization
* FastAPI backend
* React map dashboard
* Documentation and demo video

## Optional If Time Allows

* Heat-risk layer
* Landsat surface temperature
* NDVI
* GHSL built-up density
* ESA WorldCover
* WorldPop exposure layer

## Out of Scope for This Deadline

* Road damage detection
* Arabic complaint NLP
* Garbage detection
* Construction detection
* Multi-district expansion
* Real-time official traffic API integration
* Full hydrological flood simulation
* IoT sensor integration
* Citizen reporting module

## Repository Safety Rules

* Do not replace or rewrite root README.md without explicit confirmation.
* Do not delete existing project files.
* Add module-specific docs under docs/nasr_city_weather_impact/.
* Keep the architecture clean and maintainable.
* Avoid unnecessary files, factories, managers, handlers, or abstract layers.

## Implementation Direction

The final approach is:

Open geospatial/weather data
→ grid-based feature engineering
→ rule-based flood, traffic, and emergency risk scoring
→ ML surrogate model trained on engineered weak labels
→ weather-aware route optimization
→ FastAPI backend
→ React MapLibre dashboard

## Honesty Statement

This MVP does not claim to be an officially validated flood forecasting system. It is a geospatial ML-powered decision-support prototype that estimates relative weather-impact risk using open data, engineered features, scenario simulation, and explainable scoring. The ML component is trained on engineered weak labels because verified street-level flood incident labels for Nasr City are not available within the project deadline.
