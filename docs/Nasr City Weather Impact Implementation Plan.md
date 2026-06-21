# Egypt Smart City Digital Twin — Nasr City Weather-Impact Emergency Mobility Module

**Implementation-Ready Master Plan**  
**Project Repository:** `https://github.com/MahmoudNagiubX/Egypt-Smart-City-Digital-Twin`  
**Case Study:** Nasr City, Cairo, Egypt  
**Track:** Machine Learning Engineering  
**Delivery Deadline:** Thursday, 2026-07-02  
**Plan Created:** Sunday, 2026-06-21  
**Target:** Build one strong, realistic, demo-ready digital twin module instead of trying to implement the full parent project.



> **Reviewed Version:** v3.0 — Clean architecture and per-step Git workflow review completed on 2026-06-21.  
> **Review Goal:** make the plan implementation-ready for coding agents, VS Code, Codex/Antigravity CLI, and final delivery with a clean maintainable architecture, simple naming, and a commit-after-every-step workflow.

---

## V3 Review Summary — What Was Verified and Tightened

This version was reviewed against the following criteria:

1. **Deadline realism:** every phase must be executable before the 2026-07-02 submission deadline.
2. **Dataset availability:** every core dataset must be open, accessible, and usable without paid access.
3. **Machine Learning Engineering value:** the project must include a real feature pipeline, model artifact, metrics, and explainability without falsely claiming verified real-world flood prediction accuracy.
4. **Geospatial correctness:** road network, grid, route graph, CRS handling, GeoJSON outputs, and spatial joins must be technically coherent.
5. **Frontend/backend integration:** every dashboard layer must have a matching FastAPI endpoint and output file.
6. **Fallback safety:** if Earth Engine, PostGIS, deployment, or external downloads fail, the project still has a demo-ready path.
7. **Documentation honesty:** limitations, weak labels, simulated scenarios, and future improvements must be clearly stated.
8. **Repository safety:** no deletion or rewriting of root `README.md` or old project files without confirmation.

### Critical V2 Corrections

- **OSMnx v2 syntax fixed:** `graph_from_bbox` must receive a tuple `(left, bottom, right, top)` instead of old keyword arguments such as `north=`, `south=`, `east=`, `west=`.
- **ML evaluation clarified:** metrics for the surrogate model measure reproduction of engineered weak labels, not verified real-world flood accuracy.
- **Feature importance clarified:** `RandomForestRegressor` supports built-in feature importance; `HistGradientBoostingRegressor` should use permutation importance.
- **Optional heat layer moved behind core delivery:** heat is valuable, but it must not delay flood + roads + routing + dashboard.
- **PostGIS made optional for MVP:** GeoJSON-first delivery is safer under deadline pressure; PostGIS remains an architecture upgrade.
- **Earth Engine fallback clarified:** if authentication/export fails, use SRTM/heat proxy outputs and document the limitation.
- **Deployment fallback clarified:** if hosted backend fails, provide frontend live link plus recorded local backend demo, but still attempt live backend.


### Critical V3 Additions

- **Clean architecture enforced:** use a feature-based `backend/app/weather_impact/` package instead of spreading the same module across many folders.
- **File count reduced:** avoid creating many tiny files. Start with a small number of clear files and split only when a file becomes hard to maintain.
- **Simple naming enforced:** file names, function names, variables, API names, and frontend component names must be direct and readable.
- **Per-step commits required:** every implementation step must end with a small Git commit, not one large phase commit.
- **Commit message style clarified:** the first commit inside a phase includes the phase number; following commits inside the same phase use only `step N: ...`.
- **No unnecessary abstraction rule added:** do not create interfaces, factories, generic managers, or extra layers unless they are directly used by the current module.

---

## V3 Research-Backed Final Approach

The final approach is:

```text
Open geospatial/weather data
↓
Grid-based feature engineering
↓
Rule-based flood, road delay, and emergency risk scoring
↓
ML surrogate model trained on engineered weak labels
↓
Weather-aware route optimization using weighted road graph
↓
FastAPI + React MapLibre dashboard
```

### Why This Is the Best Approach

- Urban flood risk is driven by interactions between rainfall, terrain, land cover, impervious/built-up surfaces, drainage, exposure, and road network vulnerability.
- For Nasr City, verified street-level flood incident labels are not guaranteed, so a purely supervised flood model would be risky and probably dishonest.
- Research on urban flood-risk modeling supports interpretable ML with hydrological, topographic, and built-environment features. Random Forest and XGBoost-style tree ensembles are common strong baselines for tabular flood susceptibility/risk modeling.
- Emergency routing naturally maps to weighted shortest-path algorithms, where edge weights can represent travel time plus flood/weather penalties.
- A full-stack geospatial dashboard is stronger for graduation delivery than a notebook-only model.

### Final Model Decision

| Task | Final Decision | Reason |
|---|---|---|
| Flood risk | Rule-based weighted geospatial score first | Explainable and feasible without labeled incidents |
| ML model | `RandomForestRegressor` main model | Reliable for small/medium tabular geospatial datasets, easy to explain |
| Optional comparison | `HistGradientBoostingRegressor` | Strong sklearn-native tabular model, but explain via permutation importance |
| Avoid for v1 | Deep learning / GNN / CNN-LSTM | Too risky without labels and too slow for deadline |
| Route optimization | Dijkstra / weighted shortest path | Correct fit for road graph with risk-adjusted edge weights |
| Heat risk | Optional geospatial/satellite layer | Useful visual upgrade but not core MVP |

### Final Dataset Decision

| Priority | Dataset/API | Use | Decision |
|---:|---|---|---|
| 1 | OpenStreetMap via OSMnx | roads, graph, facilities | Core required |
| 2 | Open-Meteo Archive API | hourly weather/rain/temp/humidity/wind | Core required |
| 3 | Generated 500m grid | standard analysis unit | Core required |
| 4 | SRTM 30m DEM | elevation/slope/low zones | Strongly recommended |
| 5 | Landsat C2 Surface Temperature | heat layer | Optional |
| 6 | Sentinel-2 NDVI / ESA WorldCover | vegetation/land cover | Optional |
| 7 | GHSL Built-up Surface | built-up/impervious proxy | Optional but valuable |
| 8 | WorldPop | exposed population | Optional final upgrade |


### V3 Clean Architecture Decision

The project must stay clean, small, and easy to debug. The goal is not to impress by having many files. The goal is to make every file obvious.

Use a **feature-based architecture**:

```text
backend/app/weather_impact/
```

This folder owns the complete weather-impact module:

- data loading helpers
- spatial/weather processing helpers
- scoring engines
- ML model utilities
- emergency routing
- API schemas
- service layer
- API router

Do **not** spread the same feature across too many folders such as:

```text
api/routes/
services/
schemas/
ml/weather_impact/
preprocessing/
```

That style is acceptable in large production systems, but for this 12-day graduation delivery it creates too much navigation overhead. The cleaner rule is:

```text
One main feature = one main package
```

#### Clean Architecture Rules

1. Keep the backend module under `backend/app/weather_impact/`.
2. Keep scripts thin. Scripts should call functions from `weather_impact/`; they should not contain large business logic.
3. Keep frontend components few and readable.
4. Do not create a file unless it has a clear job.
5. Do not create empty folders for future features.
6. Do not add unused classes just because they look professional.
7. Do not split a file until it becomes hard to read, usually above 250–350 lines or when it has mixed responsibilities.
8. Keep every function name simple and action-based.
9. Keep every output file name predictable.
10. Prefer working code and clear tests over over-engineered structure.

#### Naming Rules

Use simple `snake_case` for Python files and functions:

```text
flood.py
traffic.py
routing.py
model.py
build_grid()
score_flood_risk()
score_road_delay()
find_safe_route()
train_risk_model()
```

Use simple `PascalCase` for React components:

```text
MapView.tsx
SidePanel.tsx
SummaryCards.tsx
RoutePanel.tsx
LayerToggle.tsx
Legend.tsx
```

Avoid vague names:

```text
manager.py
handler.py
processor.py
utils.py
helper.py
engine_manager.py
main_service_handler.py
```

If a utility file is needed, name it by domain, not by generic purpose:

```text
paths.py
geo.py
weather.py
data_loader.py
```

### Non-Negotiable Honesty Statement for Report and Presentation

Use this exact idea in documentation:

```text
This MVP does not claim to be an officially validated flood forecasting system. It is a geospatial ML-powered decision-support prototype that estimates relative weather-impact risk using open data, engineered features, scenario simulation, and explainable scoring. The ML component is trained on engineered weak labels because verified street-level flood incident labels for Nasr City are not available within the project deadline.
```

---

## 0. Final Decision

We will implement **one production-style module**:

> **Nasr City Weather-Impact Emergency Mobility Module**

The module will estimate how rainfall and weather conditions affect:

1. **Flood-prone zones**
2. **Road delay**
3. **Emergency vehicle route safety**
4. **Optional heat-risk layer if time allows**

This is the best scope because it is realistic in 12 days, visually impressive, academically defendable, and strongly connected to the parent Egypt Smart City Digital Twin project.

---

## 1. Executive Summary

The parent project is a smart city digital twin platform. The full original vision includes flood prediction, traffic prediction, road damage detection, construction detection, complaint analysis, garbage monitoring, and district scoring.

Because the deadline is close, the first delivery will focus on one integrated module:

```text
Rainfall happens
↓
Some streets and grid zones become flood-prone
↓
Traffic delay increases on affected roads
↓
Emergency vehicles may be delayed
↓
The system recalculates a safer weather-aware route
↓
The dashboard visualizes the risk layers on a map
```

Optional extension:

```text
High temperature + dense built-up areas + low vegetation
↓
Urban heat risk increases
↓
Heat-risk zones are displayed on the dashboard
```

The final product should feel like a real smart-city decision-support dashboard, not just a notebook.

---

## 2. Non-Negotiable Constraints

These constraints must guide every implementation decision.

### 2.1 Time Constraint

We have approximately **12 calendar days** until submission.

Therefore:

- Do not implement the entire parent project.
- Do not start with deep learning from scratch.
- Do not wait for perfect datasets.
- Do not over-engineer the database before the map/API works.
- Do not build unused modules just to match the old README vision.

### 2.2 Scope Constraint

Only this module is in scope:

```text
Nasr City Weather-Impact Emergency Mobility Module
```

Core features:

- Nasr City boundary and grid
- Road network
- Hospitals / emergency facilities
- Weather data
- Flood risk by zone
- Road delay by weather/flood risk
- Emergency route optimization
- Backend API
- Frontend map dashboard
- Documentation and demo video

Optional features:

- Heat-risk layer
- Landsat LST
- NDVI
- GHSL built-up density
- ESA WorldCover
- WorldPop population exposure

Out of scope for this deadline:

- Road damage detection with YOLO
- Arabic complaint NLP
- Garbage detection
- Construction change detection
- Full multi-district digital twin
- Real-time official traffic API integration
- Full hydrological flood simulation
- IoT sensor integration
- Citizen reporting module

### 2.3 Repository Constraint

Use the same GitHub repository:

```text
https://github.com/MahmoudNagiubX/Egypt-Smart-City-Digital-Twin
```

The final submission must use the same GitHub link created at the start of the project.

### 2.4 Documentation Safety Rule

Do **not** replace or rewrite the root `README.md` without explicit confirmation.

Instead:

- Keep root README stable unless instructed.
- Add module-specific docs under `docs/nasr_city_weather_impact/`.
- Add new files instead of deleting old project vision files.
- If README needs a small note later, ask first.

### 2.5 Data Constraint

Use open and accessible datasets first.

Avoid paid APIs unless absolutely necessary.

---

## 3. Final MVP Definition

The MVP is complete when the system can:

1. Display Nasr City boundary.
2. Display 500m analysis grid cells.
3. Display drivable road network.
4. Display hospitals / clinics / emergency facilities.
5. Collect or load weather data.
6. Run a rainfall scenario.
7. Estimate flood risk per grid zone.
8. Estimate weather/flood delay per road segment.
9. Calculate a normal route and a weather-safe emergency route.
10. Compare normal ETA vs weather-safe ETA.
11. Show avoided high-risk road segments.
12. Expose map layers through FastAPI endpoints.
13. Display risk layers in a React map dashboard.
14. Provide summary cards and zone/road popups.
15. Include clear documentation, limitations, and future work.

---

## 4. Final Product Name

Use this name everywhere:

```text
Nasr City Weather-Impact Emergency Mobility Module
```

Short name:

```text
Weather Impact Module
```

Backend API title:

```text
Egypt Smart City Digital Twin API
```

Frontend page title:

```text
Nasr City Weather Impact Dashboard
```

---

## 5. Best Technical Approach

### 5.1 Recommended Approach

Use a **hybrid geospatial scoring + machine learning engineering approach**.

The system will have two layers:

1. **Rule-based geospatial risk engine**
   - Fast to build
   - Explainable
   - Works without official flood incident labels

2. **ML surrogate model**
   - Trained on engineered features and weak labels
   - Demonstrates ML engineering pipeline
   - Saves a real model artifact
   - Gives feature importance and evaluation metrics

### 5.2 Why Not Deep Learning First?

Do not start with CNN/LSTM/Graph Neural Networks because:

- We do not have enough verified labeled flood incidents for Nasr City.
- Real traffic data is difficult to access legally and reliably.
- Deep learning would consume time without guaranteeing a better demo.
- The final committee needs a working system, not only a research experiment.

### 5.3 Best ML Model Choice

Use these in order:

1. **RandomForestRegressor** as the main model
2. **HistGradientBoostingRegressor** as a stronger optional model
3. Optional later: XGBoost or LightGBM if installation is smooth

Why Random Forest first:

- Good for tabular geospatial features
- Easy to train
- Handles nonlinear relationships
- Produces feature importance
- Works well with small/medium datasets
- Easier to explain in the final presentation

Target variables:

```text
flood_risk_score
traffic_delay_risk
emergency_delay_risk
overall_weather_impact_score
```

Important honesty in documentation:

> Because verified local flood incident labels are unavailable for Nasr City, the first ML model is trained on engineered weak labels generated from geospatial and weather risk logic. This creates a reproducible ML pipeline and can later be replaced by supervised training when official flood/traffic incident data becomes available.

---

## 6. Dataset and API Choices

### 6.1 Must-Have Datasets

| Priority | Dataset | Source | Use | Required |
|---:|---|---|---|---|
| 1 | OpenStreetMap roads | OSMnx / Overpass | road graph, routing, travel time | Yes |
| 2 | OSM hospitals/clinics | OSMnx / Overpass | emergency routing targets | Yes |
| 3 | Open-Meteo Historical Weather API | Open-Meteo | rainfall, temperature, humidity, wind | Yes |
| 4 | Nasr City boundary | OSMnx or manual GeoJSON | clipping area | Yes |
| 5 | 500m grid cells | generated by GeoPandas | analysis units | Yes |
| 6 | SRTM 30m DEM | Google Earth Engine / geemap | elevation and slope | Strongly recommended |

### 6.2 Should-Have Datasets

| Dataset | Source | Use |
|---|---|---|
| Landsat Collection 2 Surface Temperature | USGS / Google Earth Engine | optional heat-risk layer |
| Sentinel-2 NDVI | Copernicus / Google Earth Engine | vegetation indicator |
| ESA WorldCover 10m | ESA | land cover / vegetation / built-up class |
| GHSL Built-up Surface | EC JRC / Google Earth Engine | built-up density / impervious proxy |
| WorldPop Egypt 100m | WorldPop | exposure / population risk |

### 6.3 Nice-to-Have Datasets

| Dataset | Use |
|---|---|
| NASA POWER Hourly API | weather validation |
| NASA GPM IMERG | stronger rainfall analysis |
| Google Maps / HERE / TomTom traffic | future real traffic validation |
| drainage network | better flood modeling |
| official incident reports | supervised flood classification |
| citizen complaints | future NLP integration |

### 6.4 Final Dataset Strategy

Use this order:

```text
1. OSM roads + hospitals
2. Open-Meteo weather
3. Generated grid
4. SRTM elevation/slope
5. Rule-based risk scoring
6. ML surrogate model
7. FastAPI + dashboard
8. Optional Landsat/NDVI/GHSL heat layer
```

---

## 7. Recommended Tech Stack

### 7.1 Backend

Use:

```text
Python 3.11
FastAPI
Uvicorn
Pydantic
Pydantic Settings
```

Reason:

- FastAPI gives clean REST APIs.
- Pydantic gives request/response validation.
- Swagger docs at `/docs` help testing and presentation.

### 7.2 Geospatial and Data

Use:

```text
geopandas
shapely
pyproj
osmnx>=2.0
networkx
rasterio
rioxarray
geemap
earthengine-api
pandas
numpy
requests
```

Important implementation note:

```text
Use OSMnx v2.x syntax consistently.
For bbox downloads, use bbox=(west, south, east, north), not old keyword arguments.
```

Purpose:

- `geopandas`: read/write GeoJSON, spatial joins, grid generation
- `shapely`: geometry operations
- `pyproj`: CRS transformations
- `osmnx`: OSM roads, graph extraction, speeds/travel times
- `networkx`: shortest path / Dijkstra routing
- `rasterio`: raster operations
- `rioxarray`: clip raster data
- `geemap` + `earthengine-api`: export SRTM/Landsat/GHSL/WorldCover when needed
- `pandas` / `numpy`: feature engineering
- `requests`: Open-Meteo API calls

### 7.3 Machine Learning

Use:

```text
scikit-learn
joblib
matplotlib
plotly
```

Models:

```text
RandomForestRegressor
HistGradientBoostingRegressor
RandomForestClassifier (optional severity classification)
```

Metrics:

```text
MAE
RMSE
R2
classification_report for severity class if used
feature_importances_
permutation_importance
```

### 7.4 Database

Recommended:

```text
PostgreSQL + PostGIS
SQLAlchemy
GeoAlchemy2
psycopg2-binary
Alembic (optional)
```

Practical decision:

- In early phases, write outputs to GeoJSON/CSV.
- Add PostGIS after the core pipeline works.
- Keep GeoJSON as backup even after database integration.

### 7.5 Frontend

Use:

```text
React
Vite
TypeScript optional
MapLibre GL JS
Axios
Recharts
Tailwind CSS
Lucide React
```

Important decision:

- Prefer **MapLibre GL JS** over Mapbox if you want to avoid Mapbox token/payment issues.
- Use OpenStreetMap raster/vector tiles through a free tile provider only for demo.
- If Mapbox token is available and stable, Mapbox GL JS is also acceptable.

### 7.6 Deployment

Use:

```text
Docker
Docker Compose
Render / Railway / Azure App Service / Azure Container Apps
Vercel / Netlify for frontend
```

Best practical path:

- Frontend: Vercel or Netlify
- Backend: Render, Railway, or Azure App Service
- Database: avoid hosted PostGIS unless necessary; for demo, backend can serve precomputed GeoJSON files

If Azure is required for presentation:

- Deploy backend container to Azure App Service or Azure Container Apps.
- Deploy frontend to Azure Static Web Apps.

### 7.7 Testing

Use:

```text
pytest
httpx
ruff optional
black optional
```

Minimum tests:

- risk scores stay between 0 and 1
- severity labels are correct
- road delay factor >= 1
- route endpoint returns geometry
- API endpoints return valid JSON/GeoJSON

---

## 8. Clean Repository Structure

Create this structure without deleting old files.

The structure is intentionally **smaller and cleaner** than a large enterprise layout. The project has one main feature, so the backend should be feature-based.

```text
Egypt-Smart-City-Digital-Twin/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   │
│   │   ├── weather_impact/
│   │   │   ├── __init__.py
│   │   │   ├── paths.py
│   │   │   ├── data_loader.py
│   │   │   ├── geo.py
│   │   │   ├── weather.py
│   │   │   ├── scoring.py
│   │   │   ├── flood.py
│   │   │   ├── traffic.py
│   │   │   ├── routing.py
│   │   │   ├── model.py
│   │   │   ├── service.py
│   │   │   ├── schemas.py
│   │   │   └── router.py
│   │   │
│   │   ├── scripts/
│   │   │   ├── 00_check_env.py
│   │   │   ├── 01_build_spatial_data.py
│   │   │   ├── 02_collect_weather.py
│   │   │   ├── 03_build_features.py
│   │   │   ├── 04_run_pipeline.py
│   │   │   ├── 05_train_model.py
│   │   │   ├── 06_test_route.py
│   │   │   └── 07_export_demo.py
│   │   │
│   │   ├── data/
│   │   │   └── nasr_city/
│   │   │       ├── raw/
│   │   │       ├── processed/
│   │   │       ├── outputs/
│   │   │       ├── models/
│   │   │       ├── maps/
│   │   │       └── samples/
│   │   │
│   │   └── tests/
│   │       ├── test_scoring.py
│   │       ├── test_pipeline.py
│   │       ├── test_routing.py
│   │       └── test_api.py
│   │
│   ├── db/
│   │   └── init.sql
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── api.ts
│       ├── types.ts
│       ├── pages/
│       │   └── Dashboard.tsx
│       ├── components/
│       │   ├── MapView.tsx
│       │   ├── SidePanel.tsx
│       │   ├── LayerToggle.tsx
│       │   ├── SummaryCards.tsx
│       │   ├── RoutePanel.tsx
│       │   └── Legend.tsx
│       └── styles/
│           └── index.css
│
├── docs/
│   └── nasr_city_weather_impact/
│       ├── MASTER_IMPLEMENTATION_PLAN.md
│       ├── PROJECT_DOCUMENTATION.md
│       ├── API_REFERENCE.md
│       └── DEMO_SCRIPT.md
│
├── deliverables/
│   ├── team_excel/
│   ├── presentation/
│   ├── video_demo/
│   └── source_code_zip/
│
├── docker-compose.yml
├── .gitignore
└── README.md
```

### 8.1 File Responsibility Map

| File | Responsibility |
|---|---|
| `backend/app/main.py` | create FastAPI app, health route, include weather router |
| `backend/app/config.py` | environment settings and constants |
| `weather_impact/paths.py` | all project data paths in one place |
| `weather_impact/data_loader.py` | read/write CSV, GeoJSON, GraphML, model files |
| `weather_impact/geo.py` | boundary, grid, roads, hospitals, elevation helpers |
| `weather_impact/weather.py` | Open-Meteo collection and storm scenarios |
| `weather_impact/scoring.py` | normalization, severity, shared score helpers |
| `weather_impact/flood.py` | flood-risk formula and weak-label target |
| `weather_impact/traffic.py` | road delay factor and road severity |
| `weather_impact/routing.py` | normal route and weather-safe route |
| `weather_impact/model.py` | train/predict model, save metrics, feature importance |
| `weather_impact/service.py` | functions used by API endpoints |
| `weather_impact/schemas.py` | Pydantic request/response models |
| `weather_impact/router.py` | FastAPI endpoints for this module |

### 8.2 File Count Guardrail

The first working version should stay close to this size:

| Area | Target |
|---|---:|
| backend feature files | 10–13 files |
| backend scripts | 6–8 files |
| backend tests | 4 files |
| frontend components | 5–7 files |
| docs | 4 main files |

Do not create a new file unless one of these is true:

- the current file became too long or mixed responsibilities
- the new file represents a real domain concept
- the new file will be imported by more than one script/API path
- the new file improves debugging immediately

### 8.3 Path Translation Rule

If an older instruction says to create a file under these paths:

```text
backend/app/ml/weather_impact/
backend/app/preprocessing/
backend/app/services/
backend/app/schemas/
backend/app/api/routes/
```

Use the clean v3 paths instead:

| Old path idea | v3 path |
|---|---|
| `ml/weather_impact/scoring.py` | `weather_impact/scoring.py` |
| `ml/weather_impact/flood_risk_engine.py` | `weather_impact/flood.py` |
| `ml/weather_impact/traffic_delay_engine.py` | `weather_impact/traffic.py` |
| `ml/weather_impact/emergency_route_engine.py` | `weather_impact/routing.py` |
| `ml/weather_impact/model_training.py` | `weather_impact/model.py` |
| `preprocessing/weather_pipeline.py` | `weather_impact/weather.py` |
| `preprocessing/*_pipeline.py` | `weather_impact/geo.py` or a thin script in `scripts/` |
| `services/weather_impact_service.py` | `weather_impact/service.py` |
| `schemas/weather_impact.py` | `weather_impact/schemas.py` |
| `api/routes/weather_impact.py` | `weather_impact/router.py` |

### 8.4 No Million Files Rule

Do not create these unless absolutely needed:

```text
managers/
handlers/
factories/
interfaces/
abstract_classes/
repositories/
controllers/
validators/
```

For this deadline, direct and readable code is better.

---
## 9. Environment Setup

### 9.1 Recommended Conda Setup

Use Conda because GeoPandas and OSMnx can be painful on Windows with pure pip.

```bash
conda create -n smartcity python=3.11 -y
conda activate smartcity

conda install -c conda-forge geopandas osmnx networkx shapely pyproj fiona rtree rasterio rioxarray pandas numpy matplotlib requests python-dotenv -y

pip install fastapi uvicorn[standard] pydantic pydantic-settings sqlalchemy psycopg2-binary geoalchemy2 scikit-learn joblib pytest httpx geemap earthengine-api
```

### 9.2 Backend Requirements

Create `backend/requirements.txt`:

```txt
fastapi
uvicorn[standard]
pydantic
pydantic-settings
python-dotenv
requests
pandas
numpy
geopandas
shapely
pyproj
fiona
rtree
osmnx
networkx
rasterio
rioxarray
geemap
earthengine-api
matplotlib
plotly
scikit-learn
joblib
sqlalchemy
psycopg2-binary
geoalchemy2
python-multipart
pytest
httpx
```

Recommended version notes for fewer surprises:

```txt
python>=3.11,<3.12
osmnx>=2.0
geopandas>=0.14
shapely>=2.0
networkx>=3.0
scikit-learn>=1.4
fastapi>=0.110
```

Do not add XGBoost/LightGBM to the first install unless the core pipeline is already working. They are optional comparison models, not required for the MVP.

### 9.3 Frontend Setup

```bash
cd frontend
npm create vite@latest . -- --template react-ts
npm install
npm install maplibre-gl axios recharts lucide-react
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

If TypeScript causes time issues, use React JavaScript instead.

---

## 10. Git Strategy

### 10.1 Branch

```bash
git checkout -b feature/nasr-city-weather-impact-module
```

### 10.2 Commit After Every Step

Every implementation step must end with a small commit.

Use this after each step:

```bash
git status --short
git add <only-files-changed-in-this-step>
git commit -m "<step message>"
git log --oneline -5
```

Do **not** wait until the end of the phase to commit everything.

The goal is:

- easy rollback
- easy debugging
- clean GitHub history
- clear progress for the team
- easier review if Antigravity/Codex makes a mistake

### 10.3 Commit Message Format

Inside each phase:

- The **first commit** includes the phase number.
- The following commits use only the step number.
- Keep messages short, lowercase, and action-based.
- Do not use emojis in commit messages.

Pattern:

```text
phase X step 1: <what changed>
step 2: <what changed>
step 3: <what changed>
```

Example:

```bash
git commit -m "phase 1 step 1: create clean backend structure"
git commit -m "step 2: add backend requirements"
git commit -m "step 3: add environment example"
```

When starting a new phase, reset the pattern:

```bash
git commit -m "phase 2 step 1: prepare nasr city boundary"
git commit -m "step 2: download road network"
git commit -m "step 3: extract emergency facilities"
```

### 10.4 Step Commit Message Map

Use this table as the default Git commit guide. If a step title changes slightly during implementation, keep the same style.

| Step | Work | Commit message |
|---:|---|---|
| 0.1 | Create Working Branch | `phase 0 step 1: create working branch` |
| 0.2 | Create Module Docs Folder | `step 2: create module docs folder` |
| 0.3 | Create Delivery Folder | `step 3: create delivery folder` |
| 0.4 | Add Scope Lock Document | `step 4: add scope lock document` |
| 0.5 | Create GitHub Issues | `step 5: create github issues` |
| 0.6 | Phase 0 Final Checkpoint | `step 6: finalize phase 0 checkpoint` |
| 1.1 | Create Backend Folder Structure | `phase 1 step 1: create backend folder structure` |
| 1.2 | Add Requirements | `step 2: add requirements` |
| 1.3 | Add `.env.example` | `step 3: add env example` |
| 1.4 | Add FastAPI Config | `step 4: add fastapi config` |
| 1.5 | Add Main FastAPI App | `step 5: add main fastapi app` |
| 1.6 | Add Docker Compose for PostGIS | `step 6: add docker compose for postgis` |
| 1.7 | Add Initial Database Schema | `step 7: add initial database schema` |
| 1.8 | Phase 1 Final Checkpoint | `step 8: finalize phase 1 checkpoint` |
| 2.1 | Prepare Nasr City Boundary | `phase 2 step 1: prepare nasr city boundary` |
| 2.2 | Download Road Network | `step 2: download road network` |
| 2.3 | Extract Hospitals and Emergency Facilities | `step 3: extract hospitals and emergency facilities` |
| 2.4 | Validate Road Network | `step 4: validate road network` |
| 2.5 | Generate 500m Grid Cells | `step 5: generate 500m grid cells` |
| 2.6 | Spatial Join Roads to Grid | `step 6: spatial join roads to grid` |
| 2.7 | Store Processed Data in PostGIS Optional | `step 7: store processed data in postgis optional` |
| 2.8 | Create Static Map Screenshot | `step 8: create static map screenshot` |
| 2.9 | Phase 2 Tests | `step 9: phase 2 tests` |
| 2.10 | Phase 2 Final Checkpoint | `step 10: finalize phase 2 checkpoint` |
| 3.1 | Build Open-Meteo Collector | `phase 3 step 1: build open-meteo collector` |
| 3.2 | Clean Weather Data | `step 2: clean weather data` |
| 3.3 | Create Demo Storm Scenarios | `step 3: create demo storm scenarios` |
| 3.4 | Add NASA POWER Optional Collector | `step 4: add nasa power optional collector` |
| 3.5 | Weather Validation Report | `step 5: weather validation report` |
| 3.6 | Phase 3 Tests | `step 6: phase 3 tests` |
| 3.7 | Phase 3 Final Checkpoint | `step 7: finalize phase 3 checkpoint` |
| 4.1 | Calculate Road Density Per Zone | `phase 4 step 1: calculate road density per zone` |
| 4.2 | Extract Elevation Features | `step 2: extract elevation features` |
| 4.3 | Build Rainfall Feature Joiner | `step 3: build rainfall feature joiner` |
| 4.4 | Normalize Features | `step 4: normalize features` |
| 4.5 | Add Built-Up Proxy | `step 5: add built-up proxy` |
| 4.6 | Add Vegetation Proxy | `step 6: add vegetation proxy` |
| 4.7 | Create Final Zone Feature Dataset | `step 7: create final zone feature dataset` |
| 4.8 | Feature Validation Report | `step 8: feature validation report` |
| 4.9 | Phase 4 Final Checkpoint | `step 9: finalize phase 4 checkpoint` |
| 5.1 | Implement Shared Scoring Utilities | `phase 5 step 1: implement shared scoring utilities` |
| 5.2 | Implement Flood Risk Engine | `step 2: implement flood risk engine` |
| 5.3 | Implement Heat Risk Engine Optional First Version | `step 3: implement heat risk engine optional first version` |
| 5.4 | Implement Traffic Delay Engine | `step 4: implement traffic delay engine` |
| 5.5 | Calculate Emergency Delay Risk by Zone | `step 5: calculate emergency delay risk by zone` |
| 5.6 | Calculate Overall Weather Impact Score | `step 6: calculate overall weather impact score` |
| 5.7 | Build Risk Pipeline Script | `step 7: build risk pipeline script` |
| 5.8 | Generate Weak Labels for ML | `step 8: generate weak labels for ml` |
| 5.9 | Train ML Risk Model | `step 9: train ml risk model` |
| 5.10 | Add Model Explainability | `step 10: add model explainability` |
| 5.11 | Phase 5 Tests | `step 11: phase 5 tests` |
| 5.12 | Phase 5 Final Checkpoint | `step 12: finalize phase 5 checkpoint` |
| 6.1 | Load Road Graph | `phase 6 step 1: load road graph` |
| 6.2 | Map Risk Penalties to Graph Edges | `step 2: map risk penalties to graph edges` |
| 6.3 | Implement Nearest Node Matching | `step 3: implement nearest node matching` |
| 6.4 | Implement Normal Route | `step 4: implement normal route` |
| 6.5 | Implement Weather-Safe Route | `step 5: implement weather-safe route` |
| 6.6 | Compare Routes | `step 6: compare routes` |
| 6.7 | Phase 6 Final Checkpoint | `step 7: finalize phase 6 checkpoint` |
| 7.1 | Create API Schemas | `phase 7 step 1: create api schemas` |
| 7.2 | Create Service Layer | `step 2: create service layer` |
| 7.3 | Create API Router | `step 3: create api router` |
| 7.4 | Connect Router in Main App | `step 4: connect router in main app` |
| 7.5 | API Test Data Flow | `step 5: api test data flow` |
| 7.6 | API Tests | `step 6: api tests` |
| 7.7 | Phase 7 Final Checkpoint | `step 7: finalize phase 7 checkpoint` |
| 8.1 | Create React App | `phase 8 step 1: create react app` |
| 8.2 | Setup API Client | `step 2: setup api client` |
| 8.3 | Create Dashboard Layout | `step 3: create dashboard layout` |
| 8.4 | Create Map View | `step 4: create map view` |
| 8.5 | Add Layer Controls | `step 5: add layer controls` |
| 8.6 | Add Risk Styling | `step 6: add risk styling` |
| 8.7 | Add Summary Cards | `step 7: add summary cards` |
| 8.8 | Add Emergency Route Panel | `step 8: add emergency route panel` |
| 8.9 | Add Popups | `step 9: add popups` |
| 8.10 | Frontend Polish and Final Checkpoint | `step 10: frontend polish` |
| 9.1 | Backend Deployment | `phase 9 step 1: backend deployment` |
| 9.2 | Frontend Deployment | `step 2: frontend deployment` |
| 9.3 | Documentation | `step 3: documentation` |
| 9.4 | Final Presentation | `step 4: final presentation` |
| 9.5 | Video Demo | `step 5: video demo` |
| 9.6 | Source Code ZIP | `step 6: source code zip` |
| 9.7 | Team Excel | `step 7: team excel` |
| 9.8 | Phase 9 Final Checkpoint | `step 8: finalize phase 9 checkpoint` |
| 10.1 | Add Landsat Surface Temperature | `phase 10 step 1: add landsat surface temperature` |
| 10.2 | Add NDVI | `step 2: add ndvi` |
| 10.3 | Add GHSL Built-Up Surface | `step 3: add ghsl built-up surface` |
| 10.4 | Add ESA WorldCover | `step 4: add esa worldcover` |
| 10.5 | Add WorldPop Optional Exposure | `step 5: add worldpop optional exposure` |
| 10.6 | Update Heat Formula | `step 6: update heat formula` |

### 10.5 Important Git Rule

Do not commit:

```text
.env
.venv/
__pycache__/
large raw raster files
large downloaded datasets
node_modules/
dist/
tmp/
```

### 10.6 Suggested `.gitignore`

```gitignore
# Python
__pycache__/
*.pyc
.venv/
.env
.env.local

# Data
backend/app/data/**/raw/*.tif
backend/app/data/**/raw/*.zip
backend/app/data/**/raw/*.nc
backend/app/data/**/raw/*.hdf
backend/app/data/**/raw/*.grib
backend/app/data/**/raw/*.gpkg

# Keep lightweight processed/demo outputs
!backend/app/data/**/processed/*.geojson
!backend/app/data/**/processed/*.csv
!backend/app/data/**/outputs/*.geojson
!backend/app/data/**/outputs/*.csv
!backend/app/data/**/samples/*.json

# Node
node_modules/
frontend/dist/

# OS
.DS_Store
Thumbs.db

# Temporary
tmp/
```

---
# 11. Phase Overview

Total plan:

```text
10 Phases
73 Implementation Steps
Per-step Git commit required
```

| Phase | Name | Estimated Duration | Steps | Must Finish? |
|---:|---|---:|---:|---|
| 0 | Scope Freeze and Repo Preparation | 0.5 day | 6 | Yes |
| 1 | Backend and Dev Environment Setup | 1 day | 8 | Yes |
| 2 | Nasr City Spatial Data Foundation | 1.5 days | 10 | Yes |
| 3 | Weather Data and Scenario Pipeline | 1 day | 7 | Yes |
| 4 | Geospatial Feature Engineering | 1.5 days | 9 | Yes |
| 5 | Risk Engines and ML Model | 2 days | 12 | Yes |
| 6 | Emergency Route Optimization | 1 day | 7 | Yes |
| 7 | FastAPI Integration | 1 day | 7 | Yes |
| 8 | Frontend Dashboard | 2 days | 10 | Yes |
| 9 | Deployment, Documentation, Demo, Submission | 1.5 days | 4 + substeps | Yes |
| 10 | Optional Heat Risk Upgrade | parallel / extra | optional | Optional |

---

# 12. Detailed Implementation Plan


> **V3 execution rule:** after finishing each step below, commit immediately using the commit message style in Section 10. Do not wait for the phase checkpoint.

---

## Phase 0 — Scope Freeze and Repo Preparation

**Duration:** 0.5 day  
**Goal:** Lock the scope and prepare the repo without breaking existing files.

### Step 0.1 — Create Working Branch

Run:

```bash
git checkout -b feature/nasr-city-weather-impact-module
```

What this does:

- Keeps main branch safe.
- Makes all module work traceable.

Output:

```text
Branch created successfully.
```

Acceptance criteria:

- `git branch` shows `feature/nasr-city-weather-impact-module`.

---

### Step 0.2 — Create Module Docs Folder

Create:

```text
docs/nasr_city_weather_impact/
```

Add placeholder files:

```text
00_MASTER_IMPLEMENTATION_PLAN.md
01_PROJECT_DESCRIPTION.md
02_DATASETS_AND_SOURCES.md
03_METHODOLOGY.md
04_API_DOCUMENTATION.md
05_FRONTEND_GUIDE.md
06_EVALUATION_AND_LIMITATIONS.md
07_DEMO_SCRIPT.md
```

What this does:

- Keeps module documentation separate from the old README.
- Avoids accidental overwrite of existing project vision.

Acceptance criteria:

- Docs folder exists.
- No old docs deleted.

---

### Step 0.3 — Create Delivery Folder

Create:

```text
deliverables/
deliverables/team_excel/
deliverables/presentation/
deliverables/video_demo/
deliverables/source_code_zip/
```

What this does:

- Keeps final submission assets organized.
- Makes it easy to prepare ministry/team deliverables.

Acceptance criteria:

- `deliverables/` folder exists.
- Contains subfolders for required submission items.

---

### Step 0.4 — Add Scope Lock Document

Create:

```text
docs/nasr_city_weather_impact/SCOPE_LOCK.md
```

Content should say:

```text
For the 2026-07-02 deadline, the project will deliver one complete module:
Nasr City Weather-Impact Emergency Mobility Module.

Core scope:
- flood risk zones
- road delay layer
- emergency route optimization
- FastAPI backend
- React map dashboard
- documentation and video demo

Optional:
- heat-risk layer if time allows

Out of scope:
- road damage CV
- Arabic complaint NLP
- garbage detection
- construction detection
- multi-district expansion
```

Acceptance criteria:

- Anyone opening the repo understands the scope.

---

### Step 0.5 — Create GitHub Issues

Create these issues manually or with GitHub UI:

1. Set up backend and project structure
2. Build Nasr City boundary, grid, roads, and hospitals pipeline
3. Collect weather and rainfall scenarios
4. Engineer geospatial risk features
5. Implement flood and traffic risk engines
6. Implement ML risk prediction model
7. Implement emergency route optimization
8. Expose FastAPI weather-impact endpoints
9. Build React map dashboard
10. Prepare deployment and final deliverables

Acceptance criteria:

- Each phase has a GitHub issue.
- Issue descriptions include checklist tasks.

---

### Step 0.6 — Phase 0 Final Checkpoint

```bash
git add docs deliverables
git commit -m "step 6: finalize phase 0 checkpoint"
```

Phase 0 is complete when:

- Branch exists.
- Scope is locked.
- Docs/deliverables folders exist.
- No existing important files were overwritten.

---

## Phase 1 — Backend and Development Environment Setup

**Duration:** 1 day  
**Goal:** Create a clean backend skeleton that can run locally and later serve the dashboard.

---

### Step 1.1 — Create Backend Folder Structure

Create:

```text
backend/
backend/app/
backend/app/weather_impact/
backend/app/scripts/
backend/app/tests/
backend/db/
backend/app/data/nasr_city/raw/
backend/app/data/nasr_city/processed/
backend/app/data/nasr_city/outputs/
backend/app/data/nasr_city/models/
backend/app/data/nasr_city/maps/
backend/app/data/nasr_city/samples/
```

Add `__init__.py` files inside Python packages.

Acceptance criteria:

- Import paths work.
- No folder naming conflicts.

---

### Step 1.2 — Add Requirements

Create:

```text
backend/requirements.txt
```

Include the dependencies listed in section 9.2.

Acceptance criteria:

- Dependencies are listed.
- Team can install environment.

---

### Step 1.3 — Add `.env.example`

Create:

```text
backend/.env.example
```

Content:

```env
APP_NAME=Egypt Smart City Digital Twin
APP_ENV=development
APP_DEBUG=true

DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=smart_city
DATABASE_USER=smartcity
DATABASE_PASSWORD=smartcity123
POSTGRES_URL=postgresql://smartcity:smartcity123@localhost:5432/smart_city

NASR_CITY_CENTER_LAT=30.0561
NASR_CITY_CENTER_LON=31.3300

DEFAULT_WEATHER_START_DATE=2024-01-01
DEFAULT_WEATHER_END_DATE=2024-12-31

USE_POSTGIS=false
DEMO_MODE=true
```

Acceptance criteria:

- `.env.example` exists.
- `.env` is ignored by Git.

---

### Step 1.4 — Add FastAPI Config

Create:

```text
backend/app/config.py
```

Purpose:

- Load settings from `.env`.
- Store constants for data paths.
- Avoid hardcoding everywhere.

Expected content behavior:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Egypt Smart City Digital Twin"
    app_env: str = "development"
    app_debug: bool = True
    postgres_url: str = "postgresql://smartcity:smartcity123@localhost:5432/smart_city"
    nasr_city_center_lat: float = 30.0561
    nasr_city_center_lon: float = 31.3300
    demo_mode: bool = True

    class Config:
        env_file = "backend/.env"
        env_file_encoding = "utf-8"

settings = Settings()
```

Acceptance criteria:

- `python -c "from backend.app.core.config import settings; print(settings.app_name)"` works.

---

### Step 1.5 — Add Main FastAPI App

Create:

```text
backend/app/main.py
```

Endpoints:

```http
GET /
GET /health
```

Expected root response:

```json
{
  "project": "Egypt Smart City Digital Twin",
  "module": "Nasr City Weather-Impact Emergency Mobility Module",
  "case_study": "Nasr City, Cairo",
  "status": "running"
}
```

Acceptance criteria:

```bash
uvicorn backend.app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

---

### Step 1.6 — Add Docker Compose for PostGIS

Create:

```text
docker-compose.yml
```

Content:

```yaml
services:
  postgis:
    image: postgis/postgis:15-3.4
    container_name: smart_city_postgis
    restart: unless-stopped
    environment:
      POSTGRES_DB: smart_city
      POSTGRES_USER: smartcity
      POSTGRES_PASSWORD: smartcity123
    ports:
      - "5432:5432"
    volumes:
      - smart_city_postgis_data:/var/lib/postgresql/data
      - ./backend/db/init.sql:/docker-entrypoint-initdb.d/init.sql

volumes:
  smart_city_postgis_data:
```

Acceptance criteria:

```bash
docker compose up -d
docker ps
```

Container should be running.

---

### Step 1.7 — Add Initial Database Schema

Create:

```text
backend/db/init.sql
```

Tables:

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

CREATE TABLE IF NOT EXISTS districts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    city VARCHAR(255),
    country VARCHAR(255),
    geometry GEOMETRY(POLYGON, 4326),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS zones (
    id SERIAL PRIMARY KEY,
    zone_code VARCHAR(50) UNIQUE NOT NULL,
    geometry GEOMETRY(POLYGON, 4326),
    area_m2 DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS road_segments (
    id SERIAL PRIMARY KEY,
    osm_id VARCHAR(100),
    road_name VARCHAR(255),
    road_type VARCHAR(100),
    length_m DOUBLE PRECISION,
    base_speed_kph DOUBLE PRECISION,
    base_travel_time_sec DOUBLE PRECISION,
    geometry GEOMETRY(LINESTRING, 4326),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS emergency_facilities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    facility_type VARCHAR(100),
    source VARCHAR(100),
    geometry GEOMETRY(POINT, 4326),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS weather_records (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    temperature_2m DOUBLE PRECISION,
    relative_humidity_2m DOUBLE PRECISION,
    precipitation DOUBLE PRECISION,
    rain DOUBLE PRECISION,
    wind_speed_10m DOUBLE PRECISION,
    source VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS zone_risk_scores (
    id SERIAL PRIMARY KEY,
    zone_code VARCHAR(50),
    timestamp TIMESTAMP,
    flood_risk DOUBLE PRECISION,
    heat_risk DOUBLE PRECISION,
    traffic_delay_risk DOUBLE PRECISION,
    emergency_delay_risk DOUBLE PRECISION,
    overall_weather_impact_score DOUBLE PRECISION,
    severity VARCHAR(50),
    confidence DOUBLE PRECISION,
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS road_weather_impacts (
    id SERIAL PRIMARY KEY,
    road_segment_id VARCHAR(100),
    timestamp TIMESTAMP,
    rainfall_mm DOUBLE PRECISION,
    flood_penalty DOUBLE PRECISION,
    rain_penalty DOUBLE PRECISION,
    traffic_penalty DOUBLE PRECISION,
    delay_factor DOUBLE PRECISION,
    adjusted_travel_time_sec DOUBLE PRECISION,
    severity VARCHAR(50),
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS emergency_route_results (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    start_lat DOUBLE PRECISION,
    start_lon DOUBLE PRECISION,
    end_lat DOUBLE PRECISION,
    end_lon DOUBLE PRECISION,
    normal_eta_minutes DOUBLE PRECISION,
    weather_safe_eta_minutes DOUBLE PRECISION,
    delay_minutes DOUBLE PRECISION,
    risk_level VARCHAR(50),
    route_geometry GEOMETRY(LINESTRING, 4326),
    avoided_roads JSONB,
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_districts_geom ON districts USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_zones_geom ON zones USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_road_segments_geom ON road_segments USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_facilities_geom ON emergency_facilities USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_emergency_routes_geom ON emergency_route_results USING GIST (route_geometry);
```

Acceptance criteria:

- Database initializes without errors.
- PostGIS extension exists.

---

### Step 1.8 — Phase 1 Final Checkpoint

```bash
git add backend docker-compose.yml .gitignore
git commit -m "step 8: finalize phase 1 checkpoint"
```

Phase 1 is complete when:

- FastAPI runs.
- `/health` returns ok.
- Docker PostGIS can start.
- Repo has stable backend structure.

---

## Phase 2 — Nasr City Spatial Data Foundation

**Duration:** 1.5 days  
**Goal:** Build the spatial base: boundary, roads, hospitals, and grid.

---

### Step 2.1 — Prepare Nasr City Boundary

Create:

```text
backend/app/scripts/01_build_spatial_data.py
```

Best approach:

1. Try OSMnx geocoding for `"Nasr City, Cairo, Egypt"`.
2. If it works, save boundary.
3. If it fails or boundary is inaccurate, use fallback bounding box.
4. Later manually refine boundary via `geojson.io`.

Fallback bounding box:

```python
FALLBACK_BBOX = {
    "north": 30.095,
    "south": 30.015,
    "east": 31.405,
    "west": 31.285,
}
```

Output:

```text
backend/app/data/nasr_city/processed/nasr_city_boundary.geojson
```

Acceptance criteria:

- GeoJSON file exists.
- Boundary opens correctly in QGIS / geojson.io.
- Boundary covers Nasr City roads.

---

### Step 2.2 — Download Road Network

Create:

```text
backend/app/scripts/01_build_spatial_data.py
```

Use:

```python
import osmnx as ox

G = ox.graph_from_place("Nasr City, Cairo, Egypt", network_type="drive", simplify=True)
G = ox.add_edge_speeds(G)
G = ox.add_edge_travel_times(G)
nodes, edges = ox.graph_to_gdfs(G)
```

Fallback:

```python
# OSMnx v2.x syntax: bbox = (left, bottom, right, top)
# left=west, bottom=south, right=east, top=north
bbox = (31.285, 30.015, 31.405, 30.095)
G = ox.graph_from_bbox(
    bbox,
    network_type="drive",
    simplify=True,
)
```

Outputs:

```text
backend/app/data/nasr_city/processed/nasr_city_graph.graphml
backend/app/data/nasr_city/processed/nasr_city_nodes.geojson
backend/app/data/nasr_city/processed/nasr_city_roads.geojson
```

Acceptance criteria:

- GraphML saved.
- Roads have `length`.
- Roads have `speed_kph` or equivalent.
- Roads have `travel_time`.

---

### Step 2.3 — Extract Hospitals and Emergency Facilities

Use OSM tags:

```text
amenity=hospital
amenity=clinic
amenity=doctors
amenity=fire_station
amenity=police
```

Output:

```text
backend/app/data/nasr_city/processed/nasr_city_emergency_facilities.geojson
```

If OSM returns too few results:

- Expand bbox slightly.
- Include clinics.
- Add sample hospital markers manually for demo, but document them as demo fallback.

Acceptance criteria:

- At least several emergency/medical facilities appear.
- Facility GeoJSON has name, type, geometry.

---

### Step 2.4 — Validate Road Network

Create a simple validation script or notebook:

Check:

- number of nodes
- number of roads
- bounding box
- CRS
- missing geometries
- missing travel times

Expected output example:

```json
{
  "nodes": 3200,
  "road_segments": 7800,
  "crs": "EPSG:4326",
  "missing_travel_time": 0
}
```

Acceptance criteria:

- Validation report saved as:

```text
backend/app/data/nasr_city/outputs/spatial_validation_report.json
```

---

### Step 2.5 — Generate 500m Grid Cells

Create:

```text
backend/app/scripts/01_build_spatial_data.py
```

Process:

1. Load boundary.
2. Reproject to metric CRS such as EPSG:3857 or Egypt-appropriate projected CRS.
3. Generate 500m x 500m square cells.
4. Clip to boundary.
5. Reproject back to EPSG:4326.
6. Assign zone IDs.

Zone ID format:

```text
NSR-GRID-001
NSR-GRID-002
NSR-GRID-003
```

Output:

```text
backend/app/data/nasr_city/processed/nasr_city_grid_500m.geojson
```

Acceptance criteria:

- Grid covers Nasr City.
- Every cell has `zone_code`.
- Grid is not too dense for frontend.

---

### Step 2.6 — Spatial Join Roads to Grid

Create output:

```text
backend/app/data/nasr_city/processed/roads_with_zone_ids.geojson
```

Each road should get nearest/intersecting zone ID.

Purpose:

- connect roads to flood-risk zones
- apply penalties to roads

Acceptance criteria:

- road segments can be linked to zones.
- roads outside boundary are removed or flagged.

---

### Step 2.7 — Store Processed Data in PostGIS Optional

If time allows:

- Insert zones into `zones`.
- Insert roads into `road_segments`.
- Insert facilities into `emergency_facilities`.

If PostGIS causes issues:

- Skip DB temporarily.
- Serve GeoJSON files directly through FastAPI.

Acceptance criteria:

- Either PostGIS has data or GeoJSON outputs are ready.

---

### Step 2.8 — Create Static Map Screenshot

Create one static plot for documentation:

```text
backend/app/data/nasr_city/maps/spatial_foundation_map.png
```

Shows:

- boundary
- grid
- roads
- hospitals

Acceptance criteria:

- This image can be used in presentation.

---

### Step 2.9 — Phase 2 Tests

Tests:

- boundary file exists
- roads file exists
- graph file exists
- facilities file exists
- grid file exists
- grid has `zone_code`
- roads have geometry

Acceptance criteria:

```bash
pytest backend/app/tests/test_spatial_data.py
```

passes.

---

### Step 2.10 — Phase 2 Final Checkpoint

```bash
git add backend/app/scripts backend/app/weather_impact backend/app/data/nasr_city/processed backend/app/data/nasr_city/outputs backend/app/data/nasr_city/maps
git commit -m "step 10: finalize spatial data foundation"
```

Phase 2 is complete when:

- Boundary, grid, roads, graph, and facilities exist.
- Basic route graph is valid.
- Static map screenshot exists.

---

## Phase 3 — Weather Data and Scenario Pipeline

**Duration:** 1 day  
**Goal:** Collect historical hourly weather data and create demo storm scenarios.

---

### Step 3.1 — Build Open-Meteo Collector

Create:

```text
backend/app/scripts/02_collect_weather.py
backend/app/weather_impact/weather.py
```

Use Open-Meteo Archive API.

Coordinates:

```text
lat = 30.0561
lon = 31.3300
timezone = Africa/Cairo
```

Variables:

```text
temperature_2m
relative_humidity_2m
apparent_temperature
precipitation
rain
wind_speed_10m
```

Date range:

```text
2024-01-01 to 2024-12-31
```

Also allow CLI args later:

```bash
python backend/app/scripts/02_collect_weather.py --start-date 2024-01-01 --end-date 2024-12-31
```

Output:

```text
backend/app/data/nasr_city/raw/weather_history_open_meteo.csv
```

Acceptance criteria:

- CSV contains hourly rows.
- Timestamps are in Cairo local time.
- Rain/precipitation are in mm.

---

### Step 3.2 — Clean Weather Data

Create processed file:

```text
backend/app/data/nasr_city/processed/weather_hourly_processed.csv
```

Add columns:

```text
timestamp
date
hour
temperature_2m
relative_humidity_2m
apparent_temperature
precipitation
rain
wind_speed_10m
rain_1h_mm
rain_3h_mm
rain_6h_mm
rain_24h_mm
rainfall_class
is_rush_hour
```

Rainfall classes:

```text
0 mm = none
0–2 mm = light
2–5 mm = moderate
5–10 mm = heavy
10+ mm = extreme/demo storm
```

Rush hour logic:

```text
07:00–10:00
16:00–19:00
```

Acceptance criteria:

- rolling rainfall columns exist.
- no critical nulls.
- rainfall class distribution printed.

---

### Step 3.3 — Create Demo Storm Scenarios

Because Cairo may have many dry hours, create deterministic demo scenarios.

Create:

```text
backend/app/data/nasr_city/samples/weather_scenarios.json
```

Content:

```json
[
  {
    "scenario_id": "normal_day",
    "name": "Normal Dry Day",
    "rain_1h_mm": 0.0,
    "rain_3h_mm": 0.0,
    "temperature_2m": 30.0,
    "apparent_temperature": 31.0,
    "hour": 12
  },
  {
    "scenario_id": "light_rain",
    "name": "Light Rain",
    "rain_1h_mm": 2.0,
    "rain_3h_mm": 4.0,
    "temperature_2m": 25.0,
    "apparent_temperature": 25.5,
    "hour": 9
  },
  {
    "scenario_id": "heavy_rain_rush_hour",
    "name": "Heavy Rain During Rush Hour",
    "rain_1h_mm": 12.0,
    "rain_3h_mm": 24.0,
    "temperature_2m": 23.0,
    "apparent_temperature": 23.5,
    "hour": 17
  },
  {
    "scenario_id": "extreme_rain",
    "name": "Extreme Rain Event",
    "rain_1h_mm": 25.0,
    "rain_3h_mm": 50.0,
    "temperature_2m": 22.0,
    "apparent_temperature": 22.5,
    "hour": 18
  },
  {
    "scenario_id": "hot_day_optional",
    "name": "Hot Urban Heat Day",
    "rain_1h_mm": 0.0,
    "rain_3h_mm": 0.0,
    "temperature_2m": 40.0,
    "apparent_temperature": 43.0,
    "hour": 14
  }
]
```

Acceptance criteria:

- frontend can select scenarios.
- backend can run scenario by `scenario_id`.

---

### Step 3.4 — Add NASA POWER Optional Collector

Do this only if time allows.

Purpose:

- validate Open-Meteo
- add scientific credibility

Output:

```text
backend/app/data/nasr_city/raw/weather_history_nasa_power.csv
```

Acceptance criteria:

- optional only.
- do not block core pipeline.

---

### Step 3.5 — Weather Validation Report

Create:

```text
backend/app/data/nasr_city/outputs/weather_validation_report.json
```

Include:

```json
{
  "source": "Open-Meteo Historical Weather API",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "rows": 8784,
  "max_rain_1h_mm": 0,
  "max_temperature": 0,
  "missing_values": {}
}
```

Acceptance criteria:

- report generated.
- can cite in docs.

---

### Step 3.6 — Phase 3 Tests

Tests:

- weather raw file exists
- processed file exists
- rolling rainfall columns exist
- scenario JSON loads
- rainfall class function works

Acceptance criteria:

```bash
pytest backend/app/tests/test_weather_pipeline.py
```

passes.

---

### Step 3.7 — Phase 3 Final Checkpoint

```bash
git add backend/app/scripts backend/app/weather_impact backend/app/data/nasr_city/raw backend/app/data/nasr_city/processed backend/app/data/nasr_city/samples backend/app/data/nasr_city/outputs
git commit -m "step 7: finalize weather scenario pipeline"
```

Phase 3 is complete when:

- Open-Meteo data exists.
- Weather scenarios exist.
- Risk pipeline can consume rainfall and temperature inputs.

---

## Phase 4 — Geospatial Feature Engineering

**Duration:** 1.5 days  
**Goal:** Create an ML-ready zone feature table.

---

### Step 4.1 — Calculate Road Density Per Zone

Input:

```text
nasr_city_grid_500m.geojson
nasr_city_roads.geojson
```

Output:

```text
backend/app/data/nasr_city/processed/grid_road_features.csv
```

Features:

```text
zone_code
road_length_m
road_density_m_per_km2
primary_road_count
secondary_road_count
residential_road_count
intersection_count
```

How:

- Reproject to metric CRS.
- Intersect roads with each grid.
- Sum road length.
- Count road types.

Acceptance criteria:

- each zone has road density.
- values are normalized later.

---

### Step 4.2 — Extract Elevation Features

Input:

```text
SRTM 30m DEM
nasr_city_grid_500m.geojson
```

Output:

```text
backend/app/data/nasr_city/processed/grid_elevation_features.csv
```

Features:

```text
zone_code
elevation_mean
elevation_min
elevation_max
slope_mean
low_elevation_score
low_slope_score
```

Best implementation options:

Option A:

- Use Google Earth Engine + geemap to export clipped SRTM features.

Option B:

- Use downloaded GeoTIFF + rasterio/rioxarray.

Acceptance criteria:

- each zone has elevation mean.
- each zone has slope mean.
- no missing zones.

Fallback if Earth Engine setup fails:

- use simplified low-area proxy based on relative position / generated random stable values.
- document fallback clearly.
- do not block the rest of the system.

---

### Step 4.3 — Build Rainfall Feature Joiner

For each scenario and zone, create:

```text
rain_1h_mm
rain_3h_mm
rain_6h_mm
rainfall_score
rainfall_accumulation_score
is_rush_hour
```

Output:

```text
backend/app/data/nasr_city/processed/zone_scenario_features.csv
```

Acceptance criteria:

- each zone appears for each scenario.
- enough rows to train ML surrogate model.

---

### Step 4.4 — Normalize Features

Create helper:

```text
backend/app/weather_impact/scoring.py
```

Functions:

```python
normalize_series(series)
safe_minmax(value, min_value, max_value)
severity_from_score(score)
clip01(value)
```

Feature normalization:

```text
rainfall_score
rainfall_accumulation_score
low_elevation_score
low_slope_score
road_density_score
builtup_proxy_score
low_vegetation_proxy_score
rush_hour_score
```

Acceptance criteria:

- all normalized scores are between 0 and 1.

---

### Step 4.5 — Add Built-Up Proxy

For MVP:

```text
builtup_proxy_score = normalized road density + road type density
```

Later optional GHSL will replace/strengthen it.

Features:

```text
builtup_proxy_score
impervious_proxy_score
```

Acceptance criteria:

- every zone has builtup proxy.
- values between 0 and 1.

---

### Step 4.6 — Add Vegetation Proxy

For MVP:

```text
low_vegetation_proxy_score = 1 - estimated vegetation proxy
```

If no NDVI:

- use fixed value `0.5`
- or infer from low road density as weak proxy

Later optional Sentinel-2 NDVI will replace it.

Acceptance criteria:

- every zone has low vegetation proxy.
- documented as proxy.

---

### Step 4.7 — Create Final Zone Feature Dataset

Output:

```text
backend/app/data/nasr_city/processed/zone_features_ml_ready.csv
backend/app/data/nasr_city/processed/zone_features_ml_ready.geojson
```

Columns:

```text
zone_code
scenario_id
rain_1h_mm
rain_3h_mm
rain_6h_mm
temperature_2m
apparent_temperature
hour
is_rush_hour
road_density_score
low_elevation_score
low_slope_score
builtup_proxy_score
impervious_proxy_score
low_vegetation_proxy_score
```

Acceptance criteria:

- CSV ready for ML.
- GeoJSON ready for map.

---

### Step 4.8 — Feature Validation Report

Create:

```text
backend/app/data/nasr_city/outputs/feature_validation_report.json
```

Include:

- number of zones
- number of scenarios
- number of rows
- missing values
- min/max for features

Acceptance criteria:

- report exists and shows no critical missing values.

---

### Step 4.9 — Phase 4 Final Checkpoint

```bash
git add backend/app/weather_impact backend/app/scripts backend/app/data/nasr_city/processed backend/app/data/nasr_city/outputs
git commit -m "step 9: finalize geospatial feature engineering"
```

Phase 4 is complete when:

- ML-ready feature table exists.
- Every zone has required features.
- Feature validation report exists.

---

## Phase 5 — Risk Engines and ML Model

**Duration:** 2 days  
**Goal:** Implement flood, traffic, emergency, and optional heat risk scoring, then train an ML model.

---

### Step 5.1 — Implement Shared Scoring Utilities

Create:

```text
backend/app/weather_impact/scoring.py
```

Functions:

```python
def clip01(value: float) -> float:
    ...

def normalize_value(value: float, min_value: float, max_value: float) -> float:
    ...

def severity_from_score(score: float) -> str:
    ...

def rainfall_to_score(rain_1h_mm: float, rain_3h_mm: float) -> float:
    ...

def temperature_to_score(temp_c: float, apparent_temp_c: float | None = None) -> float:
    ...
```

Severity:

```text
0.00–0.33 = low
0.34–0.66 = medium
0.67–1.00 = high
```

Acceptance criteria:

- functions tested.
- no score can exceed 1 or go below 0.

---

### Step 5.2 — Implement Flood Risk Engine

Create:

```text
backend/app/weather_impact/flood.py
```

Formula:

```text
Flood Risk Score =
0.30 × rainfall_score
+ 0.20 × rainfall_accumulation_score
+ 0.20 × low_elevation_score
+ 0.15 × impervious_surface_score
+ 0.10 × low_slope_score
+ 0.05 × low_vegetation_score
```

Inputs:

```text
zone_features_ml_ready.csv
scenario_id
```

Outputs:

```text
zone_code
flood_risk
flood_severity
flood_reasons
```

Main reasons logic:

- high rainfall
- high accumulated rain
- low elevation
- flat slope
- dense built-up area
- low vegetation

Acceptance criteria:

- no rain scenario gives mostly low risk.
- heavy rain scenario increases risk.
- high-risk zones have explanation strings.

---

### Step 5.3 — Implement Heat Risk Engine Optional First Version

Create:

```text
backend/app/weather_impact/heat.py
```

Formula v1:

```text
Heat Risk Score =
0.45 × apparent_temperature_score
+ 0.25 × builtup_proxy_score
+ 0.20 × low_vegetation_proxy_score
+ 0.10 × road_density_score
```

Later with Landsat:

```text
Heat Risk Score =
0.35 × lst_anomaly_score
+ 0.20 × builtup_score
+ 0.20 × low_vegetation_score
+ 0.15 × population_exposure_score
+ 0.10 × apparent_temperature_score
```

Acceptance criteria:

- hot scenario generates higher heat risk.
- if skipped, backend still works with heat_risk = 0 or proxy.

---

### Step 5.4 — Implement Traffic Delay Engine

Create:

```text
backend/app/weather_impact/traffic.py
```

Road delay formula:

```text
delay_factor =
1.0
+ rain_penalty
+ flood_penalty
+ rush_hour_penalty
+ road_type_penalty
```

Suggested penalties:

| Condition | Penalty |
|---|---:|
| no rain | 0.00 |
| light rain | 0.05 |
| moderate rain | 0.15 |
| heavy rain | 0.30 |
| extreme rain | 0.50 |
| road intersects medium flood zone | 0.20 |
| road intersects high flood zone | 0.45 |
| rush hour | 0.20 |
| narrow/residential road | 0.10 |

Output:

```text
backend/app/data/nasr_city/outputs/road_weather_impacts.geojson
```

Fields:

```text
road_segment_id
base_travel_time_sec
adjusted_travel_time_sec
delay_factor
rain_penalty
flood_penalty
rush_hour_penalty
traffic_delay_severity
reason
geometry
```

Acceptance criteria:

- adjusted time >= base time.
- roads intersecting high flood zones get higher delay.
- frontend can color roads by delay severity.

---

### Step 5.5 — Calculate Emergency Delay Risk by Zone

Formula:

```text
Emergency Delay Risk =
0.50 × average_zone_road_delay_score
+ 0.30 × flood_risk
+ 0.20 × critical_facility_distance_score
```

If facility distance is not ready:

```text
Emergency Delay Risk =
0.60 × average_zone_road_delay_score
+ 0.40 × flood_risk
```

Output:

```text
emergency_delay_risk
emergency_delay_severity
```

Acceptance criteria:

- zones with high flood + high road delay get high emergency delay.

---

### Step 5.6 — Calculate Overall Weather Impact Score

Formula:

```text
Overall Weather Impact Score =
0.35 × flood_risk
+ 0.25 × emergency_delay_risk
+ 0.20 × traffic_delay_risk
+ 0.20 × heat_risk
```

If heat is skipped:

```text
Overall Weather Impact Score =
0.45 × flood_risk
+ 0.30 × emergency_delay_risk
+ 0.25 × traffic_delay_risk
```

Output:

```text
overall_weather_impact_score
overall_severity
```

Acceptance criteria:

- score is 0–1.
- severity label is correct.
- summary can count high/medium/low zones.

---

### Step 5.7 — Build Risk Pipeline Script

Create:

```text
backend/app/scripts/04_run_pipeline.py
```

CLI examples:

```bash
python backend/app/scripts/04_run_pipeline.py --scenario heavy_rain_rush_hour
python backend/app/scripts/04_run_pipeline.py --scenario normal_day
```

Outputs:

```text
backend/app/data/nasr_city/outputs/zone_weather_impact.geojson
backend/app/data/nasr_city/outputs/road_weather_impacts.geojson
backend/app/data/nasr_city/outputs/weather_impact_summary.json
```

Acceptance criteria:

- one command generates all map layers.
- output files are valid GeoJSON/JSON.

---

### Step 5.8 — Generate Weak Labels for ML

Create:

```text
backend/app/data/nasr_city/processed/ml_training_dataset.csv
```

Rows:

```text
zone × scenario
```

Features:

```text
rain_1h_mm
rain_3h_mm
rain_6h_mm
temperature_2m
apparent_temperature
is_rush_hour
road_density_score
low_elevation_score
low_slope_score
impervious_proxy_score
low_vegetation_proxy_score
```

Targets:

```text
flood_risk
traffic_delay_risk
emergency_delay_risk
overall_weather_impact_score
```

Acceptance criteria:

- enough rows for training.
- target distributions include low/medium/high.

---

### Step 5.9 — Train ML Risk Model

Create:

```text
backend/app/weather_impact/model.py
backend/app/scripts/05_train_model.py
```

Use:

```python
RandomForestRegressor(
    n_estimators=200,
    random_state=42,
    max_depth=None,
    min_samples_leaf=2,
    n_jobs=-1,
)
```

Train models:

Option A:

- one model predicts `overall_weather_impact_score`

Option B:

- separate models predict flood/traffic/emergency/overall

Recommended:

- train one main model for `overall_weather_impact_score`
- keep rule-based flood/traffic/emergency engines as primary explanations

Outputs:

```text
backend/app/data/nasr_city/models/weather_impact_rf_model.joblib
backend/app/data/nasr_city/models/weather_impact_model_metrics.json
backend/app/data/nasr_city/models/weather_impact_feature_importance.csv
backend/app/data/nasr_city/models/weather_impact_predictions.csv
```

Acceptance criteria:

- model file saved.
- metrics file saved.
- feature importance saved.
- script can be rerun.

---

### Step 5.10 — Add Model Explainability

Create:

```text
backend/app/weather_impact/model.py
```

For MVP:

- use feature_importances_
- generate top 5 features
- save bar chart

Outputs:

```text
backend/app/data/nasr_city/models/feature_importance.png
```

Acceptance criteria:

- presentation can show which features drive risk.

---

### Step 5.11 — Phase 5 Tests

Tests:

- scoring functions
- flood score bounds
- heat score bounds
- road delay factor
- overall score
- model training smoke test

Acceptance criteria:

```bash
pytest backend/app/tests/test_scoring.py backend/app/tests/test_risk_engines.py
```

passes.

---

### Step 5.12 — Phase 5 Final Checkpoint

```bash
git add backend/app/weather_impact backend/app/scripts backend/app/tests backend/app/data/nasr_city/outputs backend/app/data/nasr_city/models
git commit -m "step 12: finalize risk engines and ml model"
```

Phase 5 is complete when:

- risk layers exist.
- ML model artifact exists.
- metrics and feature importance exist.

---

## Phase 6 — Emergency Route Optimization

**Duration:** 1 day  
**Goal:** Calculate normal route vs weather-safe route.

---

### Step 6.1 — Load Road Graph

Create:

```text
backend/app/weather_impact/routing.py
```

Load:

```text
nasr_city_graph.graphml
road_weather_impacts.geojson
```

Acceptance criteria:

- graph loads without errors.
- nodes and edges are accessible.

---

### Step 6.2 — Map Risk Penalties to Graph Edges

For each graph edge:

```text
normal_weight = travel_time
weather_weight = travel_time × delay_factor
```

If road has high flood severity:

```text
weather_weight += high_flood_extra_penalty
```

Acceptance criteria:

- every edge has `normal_weight`.
- every edge has `weather_weight`.

---

### Step 6.3 — Implement Nearest Node Matching

Function:

```python
get_nearest_node(lat, lon)
```

Use OSMnx nearest node utility.

Acceptance criteria:

- start/destination coordinates snap to graph nodes.

---

### Step 6.4 — Implement Normal Route

Function:

```python
calculate_normal_route(start_lat, start_lon, end_lat, end_lon)
```

Weight:

```text
travel_time
```

Output:

```text
route nodes
route geometry
eta minutes
```

Acceptance criteria:

- normal route returns valid LineString.

---

### Step 6.5 — Implement Weather-Safe Route

Function:

```python
calculate_weather_safe_route(start_lat, start_lon, end_lat, end_lon)
```

Weight:

```text
weather_weight
```

Output:

```text
route nodes
route geometry
weather_safe_eta_minutes
risk_level
avoided_segments
```

Acceptance criteria:

- weather route returns valid LineString.
- weather ETA >= normal ETA in heavy rain scenarios.

---

### Step 6.6 — Compare Routes

Output structure:

```json
{
  "start": {"lat": 30.061, "lon": 31.34},
  "end": {"lat": 30.045, "lon": 31.36},
  "normal_eta_minutes": 8.4,
  "weather_safe_eta_minutes": 11.2,
  "delay_minutes": 2.8,
  "risk_level": "medium",
  "avoided_segments": ["edge_12", "edge_87"],
  "normal_route_geojson": {},
  "weather_safe_route_geojson": {}
}
```

Acceptance criteria:

- route comparison is easy to show in frontend.

---

### Step 6.7 — Phase 6 Final Checkpoint

```bash
git add backend/app/weather_impact/routing.py backend/app/scripts/06_test_route.py backend/app/tests/test_routing.py
git commit -m "step 7: finalize emergency route optimization"
```

Phase 6 is complete when:

- normal and weather-safe routes work.
- output is valid GeoJSON.
- ETA comparison works.

---

## Phase 7 — FastAPI Integration

**Duration:** 1 day  
**Goal:** Expose all module outputs through backend API.

---

### Step 7.1 — Create API Schemas

Create:

```text
backend/app/weather_impact/schemas.py
```

Schemas:

```python
class ScenarioRunRequest(BaseModel):
    scenario_id: str

class EmergencyRouteRequest(BaseModel):
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    scenario_id: str | None = "heavy_rain_rush_hour"

class LayerResponse(BaseModel):
    type: str
    features: list
```

Acceptance criteria:

- request validation works.
- Swagger docs show schemas.

---

### Step 7.2 — Create Service Layer

Create:

```text
backend/app/weather_impact/service.py
```

Functions:

```python
get_summary()
get_zone_risks()
get_road_impacts()
get_facilities()
get_boundary()
get_scenarios()
run_scenario(scenario_id)
get_emergency_route(payload)
```

Acceptance criteria:

- service loads files reliably.
- missing files return clear message, not crash.

---

### Step 7.3 — Create API Router

Create:

```text
backend/app/weather_impact/router.py
```

Endpoints:

```http
GET /weather-impact/summary
GET /weather-impact/boundary
GET /weather-impact/zones
GET /weather-impact/roads
GET /weather-impact/facilities
GET /weather-impact/scenarios
POST /weather-impact/run-scenario
POST /weather-impact/emergency-route
```

Acceptance criteria:

- all endpoints appear in `/docs`.

---

### Step 7.4 — Connect Router in Main App

In `backend/app/main.py`:

```python
app.include_router(weather_impact_router)
```

Add CORS:

```python
allow_origins=["*"]
```

For deployment later, restrict origins if needed.

Acceptance criteria:

- frontend can call API.

---

### Step 7.5 — API Test Data Flow

Run:

```bash
uvicorn backend.app.main:app --reload
```

Test:

```text
GET  http://127.0.0.1:8000/health
GET  http://127.0.0.1:8000/weather-impact/summary
GET  http://127.0.0.1:8000/weather-impact/zones
GET  http://127.0.0.1:8000/weather-impact/roads
POST http://127.0.0.1:8000/weather-impact/run-scenario
POST http://127.0.0.1:8000/weather-impact/emergency-route
```

Acceptance criteria:

- endpoints return JSON/GeoJSON.
- no server crash.

---

### Step 7.6 — API Tests

Create:

```text
backend/app/tests/test_api.py
```

Test:

- health endpoint
- summary endpoint
- zones endpoint
- roads endpoint
- route endpoint

Acceptance criteria:

```bash
pytest backend/app/tests/test_api.py
```

passes.

---

### Step 7.7 — Phase 7 Final Checkpoint

```bash
git add backend/app/weather_impact backend/app/main.py backend/app/tests/test_api.py
git commit -m "step 7: finalize fastapi integration"
```

Phase 7 is complete when:

- API is functional.
- Swagger docs are clear.
- frontend can consume endpoints.

---

## Phase 8 — Frontend Dashboard

**Duration:** 2 days  
**Goal:** Build the visual product the committee will see.

---

### Step 8.1 — Create React App

Inside `frontend/`:

```bash
npm create vite@latest . -- --template react-ts
npm install
npm install maplibre-gl axios recharts lucide-react
```

Acceptance criteria:

```bash
npm run dev
```

runs.

---

### Step 8.2 — Setup API Client

Create:

```text
frontend/src/api.ts
```

Functions:

```ts
getSummary()
getBoundary()
getZones()
getRoads()
getFacilities()
getScenarios()
runScenario(scenarioId)
calculateEmergencyRoute(payload)
```

Use environment variable:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Acceptance criteria:

- frontend can call backend.

---

### Step 8.3 — Create Dashboard Page

Create:

```text
frontend/src/pages/Dashboard.tsx
```

Layout:

- top navbar
- left sidebar
- main map
- right panel / route panel
- bottom legend

Acceptance criteria:

- page looks organized.

---

### Step 8.4 — Create Map View

Create:

```text
frontend/src/components/MapView.tsx
```

Map center:

```text
lat: 30.0561
lon: 31.3300
zoom: 12
```

Layers:

- boundary
- grid risk layer
- road delay layer
- facilities markers
- emergency route line

Acceptance criteria:

- map loads.
- Nasr City appears.
- layers can be added.

---

### Step 8.5 — Add Layer Controls

Create:

```text
frontend/src/components/LayerControl.tsx
```

Toggles:

```text
Flood Risk
Overall Risk
Road Delay
Hospitals
Emergency Route
Heat Risk Optional
Grid
Boundary
```

Acceptance criteria:

- user can turn layers on/off.

---

### Step 8.6 — Add Risk Styling

Colors:

```text
low = green
medium = orange/yellow
high = red
```

If avoiding hard-coded colors for design is not important here, use consistent map styling.

Fields:

```text
flood_severity
overall_severity
traffic_delay_severity
```

Acceptance criteria:

- high-risk zones are visually obvious.
- roads have different styling by delay.

---

### Step 8.7 — Add Summary Cards

Create:

```text
frontend/src/components/SummaryCards.tsx
```

Cards:

```text
Overall Risk
High Flood Zones
Affected Roads
Average Emergency Delay
Selected Scenario
```

Acceptance criteria:

- cards update after scenario run.

---

### Step 8.8 — Add Emergency Route Panel

Create:

```text
frontend/src/components/EmergencyRoutePanel.tsx
```

Inputs:

- start latitude
- start longitude
- destination latitude
- destination longitude
- scenario dropdown
- button: Calculate Route

Preset buttons:

```text
Sample Hospital → Incident 1
Sample Hospital → Incident 2
```

Outputs:

```text
Normal ETA
Weather-Safe ETA
Delay Minutes
Risk Level
Avoided Segments
```

Acceptance criteria:

- route appears on map.
- ETA comparison visible.

---

### Step 8.9 — Add Popups

For grid cell popup:

```text
Zone ID
Flood Risk
Traffic Delay Risk
Emergency Delay Risk
Overall Risk
Main Reasons
```

For road popup:

```text
Road Name
Base ETA
Adjusted ETA
Delay Factor
Severity
Reason
```

Acceptance criteria:

- clicking map gives explanation.

---

### Step 8.10 — Frontend Polish

Make it presentation-ready:

- clean dark dashboard look
- strong title
- clear cards
- legend
- scenario selector
- loading states
- error messages
- responsive enough for laptop screen

Acceptance criteria:

- dashboard looks good on projector.
- no ugly raw JSON visible.

---

### Phase 8 Final Checkpoint

```bash
git add frontend
git commit -m "step 10: finalize frontend dashboard"
```

Phase 8 is complete when:

- frontend runs.
- map layers load.
- route calculation works.
- dashboard is demo-ready.

---

## Phase 9 — Deployment, Documentation, Demo, and Submission

**Duration:** 1.5 days  
**Goal:** Prepare final submission deliverables.

---

### Step 9.1 — Backend Deployment

Options:

1. Render
2. Railway
3. Azure App Service
4. Azure Container Apps

Practical recommendation:

- Use Render/Railway if speed matters.
- Use Azure only if required or if already set up.

Backend deployment checklist:

- set environment variables
- ensure CORS allows frontend URL
- ensure output GeoJSON files are included
- run `/health`
- run `/docs`
- test all endpoints

Acceptance criteria:

- backend live URL works.

---

### Step 9.2 — Frontend Deployment

Options:

1. Vercel
2. Netlify
3. Azure Static Web Apps

Set:

```text
VITE_API_BASE_URL=<live backend url>
```

Acceptance criteria:

- live frontend loads.
- map layers load from backend.
- route endpoint works.

---

### Step 9.3 — Documentation

Create final docs:

#### 9.3.1 Project Description

File:

```text
docs/nasr_city_weather_impact/01_PROJECT_DESCRIPTION.md
```

Include:

- problem
- solution
- target users
- module scope
- architecture
- datasets
- AI/ML approach
- final outputs

#### 9.3.2 Dataset Documentation

File:

```text
docs/nasr_city_weather_impact/02_DATASETS_AND_SOURCES.md
```

Include:

- dataset table
- source links
- variables used
- why each dataset was selected
- limitations

#### 9.3.3 Methodology

File:

```text
docs/nasr_city_weather_impact/03_METHODOLOGY.md
```

Include:

- grid generation
- feature engineering
- flood formula
- traffic formula
- emergency route algorithm
- ML training
- evaluation

#### 9.3.4 API Documentation

File:

```text
docs/nasr_city_weather_impact/04_API_DOCUMENTATION.md
```

Include:

- endpoints
- request examples
- response examples

#### 9.3.5 Evaluation and Limitations

File:

```text
docs/nasr_city_weather_impact/06_EVALUATION_AND_LIMITATIONS.md
```

Include:

- what is validated
- what is simulated
- why weak labels were used
- future real-data improvements

#### 9.3.6 Demo Script

File:

```text
docs/nasr_city_weather_impact/07_DEMO_SCRIPT.md
```

Include 2–4 minute video structure:

```text
0:00–0:20 Problem introduction
0:20–0:50 Dashboard overview
0:50–1:30 Rainfall scenario and flood-risk zones
1:30–2:10 Road delay layer
2:10–3:00 Emergency route comparison
3:00–3:40 ML model and feature importance
3:40–4:00 Final impact and future work
```

Acceptance criteria:

- docs explain the project enough for evaluator.

---

### Step 9.4 — Final Presentation

Use the required template.

Suggested slides:

1. Title
2. Problem
3. Why Nasr City
4. Proposed Solution
5. System Architecture
6. Dataset Sources
7. Feature Engineering
8. Flood Risk Engine
9. Traffic Delay Engine
10. Emergency Route Optimization
11. ML Model and Feature Importance
12. Dashboard Demo Screenshots
13. Evaluation / Scenario Results
14. Limitations
15. Future Work
16. Team Roles

Acceptance criteria:

- presentation fits 15 minutes.
- all team members can speak.

---

### Step 9.5 — Video Demo

Duration:

```text
2 to 4 minutes
```

Must show:

- dashboard
- scenario selection
- flood risk layer
- road delay layer
- emergency route
- normal vs safe ETA
- GitHub / docs briefly

Acceptance criteria:

- video is clear.
- audio or captions explain what is happening.

---

### Step 9.6 — Source Code ZIP

Create ZIP excluding:

```text
node_modules
.venv
.env
large raw data
__pycache__
tmp
```

Include:

```text
backend
frontend
docs
docker-compose.yml
README.md
requirements.txt
sample processed data
```

Acceptance criteria:

- ZIP opens.
- source code is complete.
- no secrets included.

---

### Step 9.7 — Team Excel

Columns:

```text
Team Name
Project Name
Team Leader
Member Name
Student ID
Email
Role
GitHub Username
Contribution
```

Acceptance criteria:

- Excel complete.
- Team leader submits.

---

### Step 9.8 — Phase 9 Final Checkpoint

```bash
git add docs deliverables backend frontend
git commit -m "step 8: finalize delivery package"
```

Phase 9 is complete when:

- live app link exists.
- GitHub link works.
- docs complete.
- PPT complete.
- video demo complete.
- ZIP ready.
- team Excel ready.

---

## Phase 10 — Optional Heat Risk Upgrade

**Duration:** only if time allows  
**Goal:** Add stronger heat-risk layer using satellite/land-cover data.

---

### Step 10.1 — Add Landsat Surface Temperature

Use:

```text
Landsat Collection 2 Level-2 Surface Temperature
```

Formula:

```text
ST_K = DN × 0.00341802 + 149.0
ST_C = ST_K - 273.15
```

Output:

```text
grid_heat_features.csv
```

Features:

```text
lst_celsius
lst_anomaly_score
```

Acceptance criteria:

- heat map appears.
- values are reasonable.

---

### Step 10.2 — Add NDVI

Use Sentinel-2 or Landsat.

Formula:

```text
NDVI = (NIR - Red) / (NIR + Red)
```

Features:

```text
ndvi_mean
low_vegetation_score
```

Acceptance criteria:

- low vegetation zones show higher heat risk.

---

### Step 10.3 — Add GHSL Built-Up Surface

Features:

```text
built_surface_mean
builtup_ratio
impervious_score
```

Acceptance criteria:

- dense built-up zones show higher risk.

---

### Step 10.4 — Add ESA WorldCover

Use classes to detect:

```text
built-up
tree cover
grassland
bare/sparse vegetation
water
```

Acceptance criteria:

- land-cover features improve explanation.

---

### Step 10.5 — Add WorldPop Optional Exposure

Features:

```text
population_density
population_exposure_score
```

Acceptance criteria:

- high-population hot/flood zones are prioritized.

---

### Step 10.6 — Update Heat Formula

Final heat formula:

```text
Heat Risk Score =
0.35 × lst_anomaly_score
+ 0.20 × builtup_score
+ 0.20 × low_vegetation_score
+ 0.15 × population_exposure_score
+ 0.10 × apparent_temperature_score
```

Acceptance criteria:

- heat layer becomes more scientific.

---

### Phase 10 Final Checkpoint

```bash
git add backend/app/weather_impact backend/app/data/nasr_city/processed backend/app/data/nasr_city/outputs frontend docs
git commit -m "step 6: finalize optional heat layer"
```

---

# 13. Final Execution Timeline

| Date | Main Work |
|---|---|
| 2026-06-21 | Phase 0 + start Phase 1 |
| 2026-06-22 | Finish Phase 1 |
| 2026-06-23 | Phase 2 roads, boundary, facilities |
| 2026-06-24 | Phase 2 grid + Phase 3 weather |
| 2026-06-25 | Phase 4 feature engineering |
| 2026-06-26 | Phase 5 flood/traffic engines |
| 2026-06-27 | Phase 5 ML model + Phase 6 routing |
| 2026-06-28 | Phase 7 FastAPI |
| 2026-06-29 | Phase 8 frontend map |
| 2026-06-30 | Frontend polish + deployment |
| 2026-07-01 | Documentation + PPT + demo recording |
| 2026-07-02 | Final test + ZIP + submission |

---

# 14. API Contract

## 14.1 Health

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

---

## 14.2 Summary

```http
GET /weather-impact/summary
```

Response:

```json
{
  "district": "Nasr City",
  "scenario_id": "heavy_rain_rush_hour",
  "overall_status": "high risk",
  "zone_count": 84,
  "high_flood_zones": 12,
  "high_heat_zones": 18,
  "affected_roads": 52,
  "average_flood_risk": 0.61,
  "average_traffic_delay": 1.34,
  "average_emergency_delay_minutes": 5.7
}
```

---

## 14.3 Zones Layer

```http
GET /weather-impact/zones
```

Returns GeoJSON FeatureCollection.

Each feature properties:

```json
{
  "zone_code": "NSR-GRID-024",
  "flood_risk": 0.78,
  "flood_severity": "high",
  "heat_risk": 0.52,
  "traffic_delay_risk": 0.71,
  "emergency_delay_risk": 0.82,
  "overall_weather_impact_score": 0.75,
  "overall_severity": "high",
  "main_reasons": [
    "High rainfall accumulation",
    "Low elevation",
    "High road density"
  ]
}
```

---

## 14.4 Roads Layer

```http
GET /weather-impact/roads
```

Returns GeoJSON FeatureCollection.

Properties:

```json
{
  "road_segment_id": "edge_1023",
  "road_name": "Unknown",
  "road_type": "primary",
  "base_travel_time_sec": 45,
  "adjusted_travel_time_sec": 78,
  "delay_factor": 1.73,
  "traffic_delay_severity": "high",
  "reason": "Heavy rain + high flood-risk zone"
}
```

---

## 14.5 Facilities Layer

```http
GET /weather-impact/facilities
```

Returns hospitals/clinics/fire/police GeoJSON.

---

## 14.6 Scenarios

```http
GET /weather-impact/scenarios
```

Response:

```json
[
  {
    "scenario_id": "normal_day",
    "name": "Normal Dry Day"
  },
  {
    "scenario_id": "heavy_rain_rush_hour",
    "name": "Heavy Rain During Rush Hour"
  }
]
```

---

## 14.7 Run Scenario

```http
POST /weather-impact/run-scenario
```

Request:

```json
{
  "scenario_id": "heavy_rain_rush_hour"
}
```

Response:

```json
{
  "status": "ok",
  "scenario_id": "heavy_rain_rush_hour",
  "outputs": {
    "zones": "/weather-impact/zones",
    "roads": "/weather-impact/roads",
    "summary": "/weather-impact/summary"
  }
}
```

---

## 14.8 Emergency Route

```http
POST /weather-impact/emergency-route
```

Request:

```json
{
  "start_lat": 30.061,
  "start_lon": 31.34,
  "end_lat": 30.045,
  "end_lon": 31.36,
  "scenario_id": "heavy_rain_rush_hour"
}
```

Response:

```json
{
  "normal_eta_minutes": 8.4,
  "weather_safe_eta_minutes": 11.2,
  "delay_minutes": 2.8,
  "risk_level": "medium",
  "avoided_segments": ["edge_12", "edge_87"],
  "normal_route_geojson": {},
  "weather_safe_route_geojson": {}
}
```

---

# 15. Dashboard Requirements

The frontend must show:

## 15.1 Header

Text:

```text
Nasr City Weather Impact Dashboard
Egypt Smart City Digital Twin
```

## 15.2 Sidebar

Contains:

- scenario selector
- run scenario button
- layer toggles
- legend
- emergency route form

## 15.3 Main Map

Layers:

- base map
- boundary
- grid zones
- flood risk
- road delay
- facilities
- route lines
- optional heat risk

## 15.4 Summary Cards

Cards:

```text
Overall Status
High Flood Zones
Affected Roads
Emergency Delay
Selected Scenario
```

## 15.5 Popups

Grid popup:

```text
Zone ID
Flood Risk
Emergency Risk
Overall Risk
Main Reasons
```

Road popup:

```text
Road Type
Delay Factor
Adjusted ETA
Severity
Reason
```

Facility popup:

```text
Name
Type
Source
```

## 15.6 Route Panel

Inputs:

- start lat/lon
- destination lat/lon
- scenario

Outputs:

- normal ETA
- weather-safe ETA
- delay minutes
- risk level
- avoided segments

---

# 16. Model Documentation

## 16.1 Features

Core features:

```text
rain_1h_mm
rain_3h_mm
rain_6h_mm
rainfall_score
rainfall_accumulation_score
temperature_2m
apparent_temperature
is_rush_hour
road_density_score
low_elevation_score
low_slope_score
impervious_proxy_score
low_vegetation_proxy_score
```

Optional heat features:

```text
lst_celsius
lst_anomaly_score
ndvi_mean
builtup_ratio
population_density
```

## 16.2 Targets

```text
flood_risk
traffic_delay_risk
emergency_delay_risk
overall_weather_impact_score
```

## 16.3 Model

Main model:

```text
RandomForestRegressor
```

Optional comparison:

```text
HistGradientBoostingRegressor
```

## 16.4 Metrics

Regression:

```text
MAE
RMSE
R2
```

Classification-style severity validation:

```text
accuracy
confusion matrix
classification report
```

## 16.5 Explainability

Use:

```text
RandomForestRegressor.feature_importances_
permutation_importance for HistGradientBoostingRegressor or model-agnostic checks
```

Show top features in presentation:

```text
rainfall_accumulation_score
low_elevation_score
road_density_score
impervious_proxy_score
is_rush_hour
```

## 16.6 Honest Limitation

Write this clearly:

```text
The model is not yet trained on official verified flood incident labels. It uses engineered weak labels based on weather, elevation, road density, and urban surface risk logic. This is appropriate for a first digital twin MVP and can be upgraded later with official incident reports, sensor data, or crowdsourced flood observations.
```

---

# 17. Validation Plan

## 17.1 Spatial Validation

Check:

- roads are inside Nasr City
- grid covers district
- hospitals are visible
- route works between two points

## 17.2 Weather Validation

Check:

- data date range
- no missing critical columns
- rainfall values are plausible
- demo scenarios are documented

## 17.3 Risk Validation

Test scenarios:

| Scenario | Expected Behavior |
|---|---|
| normal_day | low flood risk |
| light_rain | low/medium flood risk |
| heavy_rain_rush_hour | medium/high risk in dense/low zones |
| extreme_rain | more high-risk zones |
| hot_day_optional | high heat risk in dense zones |

## 17.4 Routing Validation

Compare:

```text
normal_eta_minutes
weather_safe_eta_minutes
delay_minutes
avoided_segments_count
```

Expected:

- heavy rain increases safe ETA
- safe route avoids more risky roads
- route geometry still reaches destination

## 17.5 API Validation

Check:

- all endpoints return status 200
- GeoJSON is valid
- route endpoint returns valid geometry

## 17.6 Frontend Validation

Check:

- map loads
- layers toggle
- scenario button works
- route appears
- cards update
- no console errors

---

# 18. Final Submission Checklist

## Required by Team / Ministry

| Required Item | Output |
|---|---|
| Excel team file | `deliverables/team_excel/team_data.xlsx` |
| Project Description | `docs/nasr_city_weather_impact/01_PROJECT_DESCRIPTION.md` |
| Final Presentation | `deliverables/presentation/final_presentation.pptx` |
| ZIP source code | `deliverables/source_code_zip/Egypt-Smart-City-Digital-Twin.zip` |
| Live Application | frontend + backend links |
| Project Documentation | docs folder |
| Video Demo | `deliverables/video_demo/demo.mp4` |
| GitHub Link | same existing repo link |

## Code Checklist

- backend runs
- frontend runs
- API works
- route works
- outputs generated
- no `.env` committed
- no `node_modules` committed
- no giant files committed

## Presentation Checklist

- project story clear
- architecture diagram ready
- dataset table ready
- model formula ready
- dashboard screenshots ready
- limitations honest
- future work strong

---

# 19. Implementation Commands Cheat Sheet

## Environment

```bash
conda activate smartcity
```

## Backend Run

```bash
uvicorn backend.app.main:app --reload
```

## Database

```bash
docker compose up -d
docker ps
```

## Data Pipeline

```bash
python backend/app/scripts/01_build_spatial_data.py
python backend/app/scripts/01_build_spatial_data.py
python backend/app/scripts/02_collect_weather.py
python backend/app/scripts/01_build_spatial_data.py
python backend/app/scripts/03_build_features.py
python backend/app/scripts/04_run_pipeline.py --scenario heavy_rain_rush_hour
python backend/app/scripts/05_train_model.py
python backend/app/scripts/06_test_route.py
```

## Tests

```bash
pytest backend/app/tests
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

## Git

```bash
git status --short
git add .
git commit -m "Clear commit message"
git log --oneline -5
```

---

# 20. Agent / CLI Execution Rules

When using Antigravity CLI, Codex, Copilot, or any coding agent, give strict instructions:

```text
You are working inside the existing Egypt-Smart-City-Digital-Twin repository.

Do not delete existing files.
Do not rewrite README.md unless explicitly instructed.
Do not change docs outside docs/nasr_city_weather_impact unless needed.
Implement only the current phase and step.
Keep changes small and reviewable.
After coding, run relevant tests or at least import checks.
Show files changed.
Do not invent unavailable datasets.
If external data download fails, implement a documented fallback sample.
```

For each phase prompt, include:

```text
Current phase:
Current step:
Files allowed to edit:
Expected outputs:
Tests to run:
Commit message:
```

---

# 21. Emergency Fallback Plan

If time becomes too tight, follow this priority order:

## Must deliver

1. FastAPI backend
2. sample GeoJSON layers
3. React map dashboard
4. flood risk layer
5. road delay layer
6. emergency route demo
7. documentation
8. PPT/video

## Can simplify

- PostGIS can be replaced by GeoJSON files.
- SRTM can be replaced by low-area proxy if Earth Engine fails.
- heat risk can be proxy-only or removed.
- ML model can be trained on engineered weak labels.
- deployment can be frontend live + backend local video if hosting fails, but try hard to get live backend.

## Do not sacrifice

- working dashboard
- clear project story
- route comparison
- documentation honesty
- GitHub cleanliness

---

# 22. Final CV Version of Project

Use this wording later:

```text
Built a geospatial ML-powered smart city digital twin module for Nasr City, Cairo, estimating rainfall-driven flood risk, weather-related road delay, and emergency route safety using OpenStreetMap, weather APIs, elevation data, FastAPI, React MapLibre, and machine learning risk scoring.
```

Stronger version:

```text
Developed a full-stack smart city digital twin module that integrates open geospatial data, weather scenarios, tabular ML risk modeling, road-network optimization, FastAPI APIs, and an interactive React map dashboard to support flood-risk and emergency-mobility decision-making in Nasr City.
```

---

# 23. Final Project Statement

The **Nasr City Weather-Impact Emergency Mobility Module** is the first complete module of the **Egypt Smart City Digital Twin** platform. It uses open geospatial, weather, elevation, road-network, and optional satellite data to estimate how rainfall and heat affect urban risk and emergency mobility.

The module combines:

- flood-risk scoring
- weather-based road delay estimation
- emergency route optimization
- optional heat-risk mapping
- machine learning surrogate modeling
- FastAPI backend APIs
- React interactive map dashboard

The final output is a decision-support dashboard that helps users understand risky zones, affected roads, and safer emergency routes under changing environmental conditions.

---

# 24. References and Source Links

## Project Sources

- GitHub Repository: https://github.com/MahmoudNagiubX/Egypt-Smart-City-Digital-Twin
- Existing module methodology file: `Smart_Nasr_City_Weather_Impact_Emergency_Mobility_Module.md`
- Existing execution guide file: `Smart_Nasr_City_Execution_Guide.md`

## Core Data Sources

- OpenStreetMap: https://www.openstreetmap.org/
- OSMnx Documentation: https://osmnx.readthedocs.io/
- Open-Meteo Historical Weather API: https://open-meteo.com/en/docs/historical-weather-api
- NASA POWER Hourly API: https://power.larc.nasa.gov/docs/services/api/temporal/hourly/
- NASA SRTM 30m: https://developers.google.com/earth-engine/datasets/catalog/USGS_SRTMGL1_003
- Landsat Collection 2 Surface Temperature: https://www.usgs.gov/landsat-missions/landsat-collection-2-surface-temperature
- ESA WorldCover: https://worldcover2021.esa.int/
- GHSL Built-Up Surface: https://developers.google.com/earth-engine/datasets/catalog/JRC_GHSL_P2023A_GHS_BUILT_S
- WorldPop: https://www.worldpop.org/

## Technical Documentation

- FastAPI: https://fastapi.tiangolo.com/
- NetworkX Shortest Paths: https://networkx.org/documentation/stable/reference/algorithms/shortest_paths.html
- scikit-learn Ensemble Models: https://scikit-learn.org/stable/modules/ensemble.html
- PostGIS: https://postgis.net/
- Docker Compose: https://docs.docker.com/compose/
- MapLibre GL JS: https://maplibre.org/maplibre-gl-js/docs/

---


---

# 26. V2 Implementation Guardrails Before Coding

Use this section before giving any coding agent a prompt.

## 26.1 Phase Execution Contract

For every phase, the coding agent must follow this structure:

```text
Goal:
Files allowed to create/edit:
Files forbidden to edit:
Exact outputs expected:
Commands to run:
Tests/import checks:
Commit message:
```

Never give a broad instruction like “build the module”. Always give only one phase or one step.

## 26.2 Minimum Viable Demo Data Contract

Even if external APIs fail, these files must exist by the time frontend starts:

```text
backend/app/data/nasr_city/processed/nasr_city_boundary.geojson
backend/app/data/nasr_city/processed/nasr_city_grid_500m.geojson
backend/app/data/nasr_city/processed/nasr_city_roads.geojson
backend/app/data/nasr_city/processed/nasr_city_emergency_facilities.geojson
backend/app/data/nasr_city/samples/weather_scenarios.json
backend/app/data/nasr_city/outputs/zone_weather_impact.geojson
backend/app/data/nasr_city/outputs/road_weather_impacts.geojson
backend/app/data/nasr_city/outputs/weather_impact_summary.json
```

If real downloads fail, create clearly labeled sample/demo files and document them.

## 26.3 Model Card Requirements

Create:

```text
backend/app/data/nasr_city/models/MODEL_CARD.md
```

It must include:

- model type
- target variable
- input features
- training data source
- weak-label generation method
- metrics meaning
- limitations
- future supervised-data upgrade path

Required limitation text:

```text
The reported metrics evaluate consistency with engineered weak labels, not official ground-truth flood incidents. The model is useful as a reproducible ML engineering layer and decision-support prototype, but it is not an operational flood warning system.
```

## 26.4 Deployment Fallback Levels

| Level | Condition | Submission Strategy |
|---:|---|---|
| A | frontend + backend both live | best case |
| B | frontend live + backend live without PostGIS | acceptable |
| C | frontend live + backend local in demo video | acceptable only if hosting fails |
| D | screenshots only | avoid unless emergency |

## 26.5 What Must Be Shown in Final Demo

The demo must show, in this order:

1. Nasr City dashboard opens.
2. Heavy rain scenario selected.
3. Flood-risk grid changes.
4. Road-delay layer appears.
5. Emergency route is calculated.
6. Normal ETA vs weather-safe ETA is compared.
7. Feature importance / ML model artifact is shown briefly.
8. Limitations and future improvements are stated honestly.

## 26.6 Final “Do Not Waste Time” Rules

Do not spend time on:

- perfect UI animations
- authentication/login
- full user accounts
- advanced PostGIS migrations
- real-time traffic paid APIs
- deep learning experiments
- adding old modules from the parent README

Spend time on:

- working map
- working scenario
- working route
- clean API
- clear documentation
- strong presentation story


# 25. Next Action

Start with:

```bash
git checkout -b feature/nasr-city-weather-impact-module
```

Then implement:

```text
Phase 0 → Phase 1 → Phase 2
```

Do not start frontend before backend has at least sample GeoJSON outputs.

Do not start optional heat upgrade until:

- flood layer works
- road delay layer works
- route works
- API works
- frontend map loads

