# Screenshot Capture Checklist

Use this checklist to capture high-quality, professional screenshots for slides and documentation. 

---

### Recommended Environment Setup:
* **Browser:** Google Chrome or Microsoft Edge
* **Resolution:** 1920x1080 (1080p Full HD)
* **Theme:** System Default (as styled by the app UI)
* **Map Controls:** Standard zoom buttons should be aligned.

---

### Screenshot Specifications:

#### 1. Welcome Page
* **Suggested Filename:** `01_welcome_page.png`
* **Zoom Level:** 100%
* **What Should Be Visible:** The clean landing page layout, main introductory header, cards describing the Weather-Impact and Heat Risk modules, and the "Launch Dashboard" button.
* **What Should NOT Be Visible:** Developer console, browser bookmarks, address bar.

#### 2. Dashboard Default View (Rain Risk Active)
* **Suggested Filename:** `02_dashboard_default.png`
* **Zoom Level:** 100% (or 90% if needed on smaller screens to see full layout)
* **What Should Be Visible:** Live weather cards in the sidebar showing current temperature/forecast, the Nasr City boundary map with green/yellow risk grid overlay, legend panel.
* **What Should NOT Be Visible:** Active tooltips, popups, or open drawer menus.

#### 3. Rain Risk Mode (Controls Drawer Closed)
* **Suggested Filename:** `03_rain_risk_closed.png`
* **Zoom Level:** 100%
* **What Should Be Visible:** Full screen map view of the rain risk layer with the sidebar minimized/closed, showing the maximum spatial map area.
* **What Should NOT Be Visible:** Controls panel, search dropdowns.

#### 4. Rain Risk Mode (Controls Drawer Open)
* **Suggested Filename:** `04_rain_risk_controls_open.png`
* **Zoom Level:** 100%
* **What Should Be Visible:** The layer control toggle panel open, detailing individual layer layers, active checkboxes, and theme selectors.
* **What Should NOT Be Visible:** Disclaimers (these have been removed from the visible UI).

#### 5. Search Result Highlight
* **Suggested Filename:** `05_search_result.png`
* **Zoom Level:** 100%
* **What Should Be Visible:** Search input text containing "hospital", matching facilities rendered in the autocomplete list, and the corresponding map zoom centered on the first result with a marker popup.
* **What Should NOT Be Visible:** Keyboard focus indicators outside the search box.

#### 6. Route Selection Start/Destination Pins
* **Suggested Filename:** `06_route_pins_selected.png`
* **Zoom Level:** 100%
* **What Should Be Visible:** A green marker pin at the origin point and an orange marker pin at the destination point on the map.
* **What Should NOT Be Visible:** Unrelated hover tooltips.

#### 7. Safe Route Comparison Map View
* **Suggested Filename:** `07_route_comparison_map.png`
* **Zoom Level:** 100% (map zoomed to fit the route geometries)
* **What Should Be Visible:** The standard/shortest route rendered in a gray/blue polyline and the safe route rendering in a prominent green path, clearly bypassing high-risk zones.
* **What Should NOT Be Visible:** Overlay cards overlapping the main route lines.

#### 8. Route Explanation Card Details
* **Suggested Filename:** `08_route_explanation.png`
* **Zoom Level:** 100%
* **What Should Be Visible:** The sidebar Route Comparison Panel displaying distance differences, travel time estimates, safety scores, and the recommendation block.
* **What Should NOT Be Visible:** Any truncated text or clipping boundaries.

#### 9. Heat Risk Mode (Controls Drawer Closed)
* **Suggested Filename:** `09_heat_risk_closed.png`
* **Zoom Level:** 100%
* **What Should Be Visible:** The thermal red/orange heat anomaly layer covering Nasr City, with side panels minimized.
* **What Should NOT Be Visible:** Active popup tooltips.

#### 10. Heat Risk Mode (Controls Drawer Open)
* **Suggested Filename:** `10_heat_risk_controls_open.png`
* **Zoom Level:** 100%
* **What Should Be Visible:** The Layer Toggle panel displaying heat layer configurations, anomaly threshold adjustments, and the thermal gradient color key.
* **What Should NOT Be Visible:** Standard rain legends.

#### 11. Heat Zone Click Popup
* **Suggested Filename:** `11_heat_zone_popup.png`
* **Zoom Level:** 100%
* **What Should Be Visible:** A clicked grid cell highlighted on the map with a popup card displaying its Zone Code (e.g. `NSR-GRID-382`) and its specific Celsius anomaly.
* **What Should NOT Be Visible:** Multi-point highlights.

#### 12. Heat Explanation Panel
* **Suggested Filename:** `12_heat_explanation_sidebar.png`
* **Zoom Level:** 100%
* **What Should Be Visible:** The Explainability Panel in the sidebar displaying local risk factors mapped to clean labels like "Built-Up Density" and "Vegetation Canopy".
* **What Should NOT Be Visible:** Database column names (e.g., `built_surface_mean`, `tree_cover_ratio`).

#### 13. Heat Model Insight (Model Cards)
* **Suggested Filename:** `13_heat_model_insight.png`
* **Zoom Level:** 95% (to fit the entire model info block)
* **What Should Be Visible:** The global feature importance chart/list showing HistGradientBoostingRegressor outputs and data authenticity numbers (4,932 Landsat rows).
* **What Should NOT Be Visible:** Any "official hazard warning" claims in the title.

#### 14. Final Full-Dashboard Overview
* **Suggested Filename:** `14_dashboard_overview.png`
* **Zoom Level:** 80% or 90% (to capture the maximum layout context in a single shot)
* **What Should Be Visible:** Side panels fully expanded, active routes, a clicked cell explanation, and the map layers all visible concurrently in a single screen footprint.
* **What Should NOT Be Visible:** Browser UI elements.
