# Deployment Audit Report

This document details the architectural configuration, build outputs, and environment requirements for deploying the Nasr City Smart Digital Twin application.

---

## 1. Project Components and Audit Details

### Backend Configuration
* **Framework:** FastAPI
* **Entrypoint:** `backend.app.main:app` (via uvicorn)
* **API Prefix:** `/api/weather-impact`
* **Health Check Path:** `/api/weather-impact/health`

### Frontend Configuration
* **Framework:** React / Vite / TypeScript
* **Build Command:** `npm run build`
* **Output Folder:** `frontend/dist/`
* **API Client Base URL:** Same-origin addressed requests (relative prefix `/api/weather-impact`) with development fallbacks.

### Path Resolution Logic
* The backend resolves file paths relative to `PROJECT_ROOT` derived dynamically in `paths.py` via:
  `PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent`
* When deployed, the repository structure must be preserved (e.g. `backend/app/` and `frontend/dist/` relative to `PROJECT_ROOT`).

---

## 2. Docker Deployment Strategy
* **Recommendation:** Use a multi-stage Docker build (`Dockerfile.deploy`):
  * **Stage 1 (Build):** Compile React production assets inside a Node environment.
  * **Stage 2 (Runtime):** Slim Python runtime containing `gdal`/geospatial system libraries, Python packages, and copying both the backend and `frontend/dist` folders to keep relative paths intact.
* **Environment Variables Required:**
  * `PORT` (assigned dynamically by Render, default `8000`)
  * `PYTHONUNBUFFERED=1`
  * `ENVIRONMENT=production`

---

## 3. Potential Risks and Mitigations
* **Path Resolution Errors:** If the backend cannot find `frontend/dist/` relative to its root, serving the frontend will fail.
  * *Mitigation:* The Dockerfile will map the code to `/app/backend` and the frontend build to `/app/frontend/dist`, ensuring `PROJECT_ROOT` resolves to `/app`.
* **Cold Starts on Free Tier:** Free Render instances spin down after inactivity.
  * *Mitigation:* Add warning notes to user guides to access URLs a few minutes before presentations.
