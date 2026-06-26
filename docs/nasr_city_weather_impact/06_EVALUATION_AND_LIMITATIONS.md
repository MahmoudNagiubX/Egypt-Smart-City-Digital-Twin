# Evaluation and Limitations

This document presents the system's verification status, operational boundaries, and planned extension vectors.

---

## 1. System Evaluation & Testing
The codebase has been verified under a strict testing cycle:
* **Backend pytest Suite:** 146 / 146 tests passed successfully.
* **Frontend vitest Suite:** 43 / 43 tests passed successfully.
* **Frontend Build compilation:** completed without errors (`dist/` asset bundle generated cleanly).
* **Python Static Analysis:** completed with 0 syntax or import errors.

---

## 2. Model Metrics
* **Weather-Impact Model:** Uses Random Forest classifiers to predict road delay risks (low, medium, high).
* **Heat Anomaly Model:** Trained on 4,932 real observed Landsat scene rows to predict surface temperature anomalies using a `HistGradientBoostingRegressor`. 
* **Fallback rows:** 0 (confirms training was performed entirely on real environmental observations).

---

## 3. Known Limitations

### Data Availability & Proxies
* **No Verified Flood Records:** Because verified street-level flood incident records for Nasr City are unavailable, the ML models are trained on engineered weak labels.
* **Meteorological Resolution:** Rainfall risk calculations rely on forecast data from Open-Meteo as statistical proxies for actual storm density.
* **Landsat Cloud Coverage:** Cloud cover can obscure Landsat sensors, meaning baseline heat anomalies represent clear-day historical observation splits.

### Operational Boundaries
* **Decision-Support Prototype:** This system is for decision-support and urban planning. It does NOT serve as an official emergency dispatch mechanism or certified public-health warning alert.

---

## 4. Future Development
* **IoT Sensor Integration:** Connect physical street water-level gauges and thermal sensors.
* **Scalability:** Scale spatial calculations to cover all of Cairo Governorate.
* **Alert Notifications:** Integrate automated SMS/email alerts when grid zones transition to high-risk states.
