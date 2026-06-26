# Smart City Digital Twin - Run Commands Guide

This document lists the PowerShell commands required to launch, test, and build the backend and frontend components of the Nasr City Weather-Impact and Heat Risk Digital Twin.

---

## Environment Context
* **OS:** Windows
* **Terminal:** PowerShell
* **Virtual Environment:** Python `.venv` located at the root of the workspace (`C:\Users\mahmo\Documents\Smart Digital Twin\.venv`).

---

## 1. Backend Service Setup & Execution

### Activate Python Virtual Environment
```powershell
# Run from the repository root: C:\Users\mahmo\Documents\Smart Digital Twin
.\.venv\Scripts\Activate.ps1
```

### Run Backend API Server
```powershell
# Run from repository root with activated environment:
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
* **Expected Backend URL:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
* **API Documentation (Swagger):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 2. Frontend Dashboard Setup & Execution

### Install Dependencies (If needed)
```powershell
cd frontend
npm install
```

### Run Vite Development Server
```powershell
# From the frontend directory:
npm run dev
```
* **Expected Frontend URL:** [http://localhost:5173](http://localhost:5173) (or the specific port printed in the terminal).

---

## 3. Verification & Testing Commands

### Verify Backend Python Compilation
Checks that all Python files compile without syntax errors:
```powershell
# From repository root with activated environment:
python -m compileall backend/app
```

### Run Backend Pytest Suite
Runs all 146 unit and integration tests (including routing, predictions, heat, and spatial data validation):
```powershell
# From repository root with activated environment:
python -m pytest backend/app/tests
```

### Run Frontend Vitest Suite
Runs the 43 vitest-driven frontend tests:
```powershell
# From the frontend directory:
npm test
```

### Build Frontend for Production
Verifies TypeScript compilation and builds static assets:
```powershell
# From the frontend directory:
npm run build
```
