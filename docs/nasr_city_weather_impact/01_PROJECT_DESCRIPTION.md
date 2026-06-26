# Project Description — Nasr City Weather-Impact Digital Twin

This document outlines the purpose, target user personas, and core features of the Nasr City Weather-Impact and Heat Risk Digital Twin system.

---

## 1. The Problem
Densely populated urban centers like Nasr City in Cairo face growing extreme weather hazards:
* **Flash Floods:** Intense precipitation events cause localized urban pooling, blocking roads and delaying emergency transit.
* **Urban Heat Islands:** Built-up concrete surfaces absorb heat, elevating micro-climate temperatures and posing health risks.
* **Black-Box Planning:** Dispatchers and urban planners lack explainable, data-driven tools to evaluate safety routing and zone-specific risk drivers.

---

## 2. Target Area & Users
* **Target Area:** Nasr City, Cairo (divided into a 416-cell gridded spatial model).
* **Target Users:** Municipal dispatchers, emergency services coordinators, and urban resilience planners.

---

## 3. Main Features
* **Live Weather Monitoring:** Connects to forecast services to report temperatures, precipitation probability, and AQI.
* **Precipitation-Impact Grid:** Dynamically maps low, medium, and high road hazard zones across the city.
* **Safety-Optimized Routing:** Calculates safe routes that bypass high-risk zones, showing safety indexes and time trade-offs.
* **Landsat Heat Risk Mapping:** Displays Celsius anomalies across micro-zones.
* **Scientific Explainability Sidebar:** Explains heat/flood predictions using feature contributions, preventing black-box decisions.

---

## 4. Final System Value
This decision-support prototype bridges the gap between raw earth observations (Landsat, ESA WorldCover) and operational planning, enabling municipal agencies to visualize environmental risks and route critical assets safely.
