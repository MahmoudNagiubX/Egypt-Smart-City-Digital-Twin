# Project Rename Audit Report

This report outlines the public project branding references located during the repository scan, specifying files to update, files to preserve, and operational risks.

---

## 1. Audit Findings

### Files to Update (Public-Facing Branding)

#### Frontend Component Files
* `frontend/src/App.tsx`: App title text (`Egypt Smart City Digital Twin`) and browser document title configurations.
* `frontend/src/components/Dashboard.tsx`: Accessibility header tags (`Egypt Smart City Digital Twin`).
* `frontend/src/__tests__/App.test.tsx` & `SearchBox.test.tsx`: Test assertions expecting the old name.

#### Deployment Configurations
* `render.yaml`: Service name should be updated from `smart-digital-twin` to `geo-weather`.
* `deploy/huggingface_space/README.md`: Space title should be updated to `Geo Weather` and description updated.
* `deploy/huggingface_space/DEPLOY_HUGGINGFACE_SPACES.md`: Recommend space name updated to `geo-weather`.
* `deliverables/LIVE_APPLICATION_URL.md`: Heading updated to `Geo Weather — Live Application URL`.

#### Documentation & Demo Packages
* `docs/nasr_city_weather_impact/*.md`: Public headers and intro texts containing `Smart Digital Twin`.
* `backend/app/data/nasr_city/final_demo_package/*.md`: Guide headings, presentation scripts, and checklist titles.
* `deliverables/DELIVERABLES_STRUCTURE.md`: Section referencing the digital twin.

---

### Files and Settings to Preserve (Internal Technical Names)
The following files and folders must be preserved to maintain API contract stability and avoid breaking imports:
* **Package Directory:** `backend/app/weather_impact/`
* **API Route Prefix:** `/api/weather-impact`
* **Docs Directory Path:** `docs/nasr_city_weather_impact/`
* **Data Paths & Models:** GeoJSON data folders, trained model filenames (`weather_impact_rf_model.joblib`), and local absolute file paths referencing the old repository name on the disk (e.g. `C:\Users\mahmo\Documents\Smart Digital Twin`).
* **Git Repository Remote & Branch:** `feature/nasr-city-weather-impact-module` branch.

---

## 2. Risk Notes
* **Import Failures:** Renaming the `weather_impact` Python package or the `/api/weather-impact` FastAPI routes would break test coverage and backend routing contracts.
* **Mitigation:** We will only update public-facing text, welcome pages, headers, deployment labels, and document titles while keeping internal paths and backend variables exactly as they are.
