# Source Code Staging Instructions

This directory holds the compressed repository archive for final submission.

---

## 1. Naming Convention
* **Zip File Name:** `geo_weather_source.zip`

---

## 2. Archiving Instructions
When creating the zip archive, ensure the following local folders and caches are excluded to minimize file footprint and prevent build contamination:
* `.venv/` (Python virtual environment)
* `node_modules/` (Node package modules)
* `frontend/dist/` (Compiled static files)
* `.git/` (Git repository metadata)
* `**/__pycache__/` (Python compilation caches)
* `.pytest_cache/` (Testing environment logs)
