# Deliverables Structure Guide

This directory holds the final packaged deliverables for submission.

---

## 1. Directory Contents & Staging Requirements

### `presentation/`
* **Assets to Staged:** PDF/PPTX presentation slides.
* **Content:** Project background, problem statement, Landsat-derived heat regressor models, Dijkstra safety routing methodologies, and evaluation stats.

### `source_code_zip/`
* **Assets to Staged:** A zip compression of the repository code files (excluding `.venv/` and `node_modules/`).
* **Content:** The FastAPI backend module, React MapLibre frontend components, unit/integration test suites, and data models.

### `team_excel/`
* **Assets to Staged:** Team grading worksheets, contribution logs, or resource budget calculators (if required by project guidelines).

### `video_demo/`
* **Assets to Staged:** A 3-5 minute recorded walkthrough video.
* **Content:** Recorded presentation of the 12-step demo flow detailing live weather, routing, and explainability tabs.

---

## 2. Staged Support Assets
The automatic verification logs, running instructions, and demo script resources are stored inside:
`backend/app/data/nasr_city/final_demo_package/`

* Run Commands Guide: `run_commands.md`
* 12-Step Demo Script: `demo_flow.md`
* Speaking Script: `presentation_script.md`
* Screenshot Checklist: `screenshot_checklist.md`
* Technical Summary: `technical_summary.md`
* Limitations and Future Work: `limitations_and_future_work.md`
* Test Confirmation JSON: `final_demo_test_confirmation.json`

---

## 3. Manual Steps Remaining
1. Capture screenshots using the checklist guidelines and place them in `presentation/` or your slides.
2. Record the 3-5 minute demo walkthrough and save the video file inside `video_demo/`.
3. Zip the project folder (excluding virtualenv and node_modules) and save the archive inside `source_code_zip/`.
