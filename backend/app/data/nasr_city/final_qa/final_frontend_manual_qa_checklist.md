# Final Frontend Manual QA Checklist

This document tracks the verification status of key user flows and layout requirements in the Smart Digital Twin frontend dashboard. 

---

## A) App Launch
* **[PASSED] Page loads**
  * *Status:* Verified via integration tests (`App.test.tsx`). App starts up and mounts cleanly without React compilation or runtime errors.
* **[NEEDS HUMAN VERIFICATION] No outer page-level scroll**
  * *Status:* Requires visual checks. Outer application container is set to `h-screen overflow-hidden` to avoid standard document-level scrolling.
* **[PASSED] Dashboard visible**
  * *Status:* Verified via integration tests. The core dashboard container (`#dashboard-root`) and main content sections render.
* **[NEEDS HUMAN VERIFICATION] No outer page-level scroll**
  * *Status:* Requires visual checks. Outer application container is set to `h-screen overflow-hidden` to avoid standard document-level scrolling.
* **[PASSED] Top nav visible**
  * *Status:* Verified. The header element with project title and status badge is rendered.
* **[PASSED] Search visible**
  * *Status:* Verified. The input field inside the map overlay area is present.

---

## B) Rain Mode (Default / Active Flow)
* **[PASSED] Rain Risk mode active**
  * *Status:* Verified. Default active theme/tab is Rain Risk.
* **[NEEDS HUMAN VERIFICATION] Rain layer visible on map**
  * *Status:* Requires visual checks. Map layers are loaded from the backend predictions API. MapLibre canvas displays risk polygons.
* **[PASSED] Bottom cards rain-specific**
  * *Status:* Verified. The bottom summary panel shows rain event summaries and risk counts.
* **[PASSED] Current weather visible**
  * *Status:* Verified. Temperature, weather code, and rain rates are fetched and rendered.
* **[PASSED] 7-Day Forecast visible**
  * *Status:* Verified. The weather card shows the upcoming 7-day forecast grid/charts.
* **[PASSED] AQI visible**
  * *Status:* Verified. Air Quality Index is visible under the weather section.

---

## C) Search & Place Finder
* **[PASSED] Search hospital**
  * *Status:* Verified via unit tests (`SearchBox.test.tsx`). Typing "hospital" queries `/api/weather-impact/search` and renders resulting items in a suggestion list.
* **[PASSED] Search street/zone**
  * *Status:* Verified. Search box queries local OSM features for matching streets or grid zones.
* **[NEEDS HUMAN VERIFICATION] Fly-to works**
  * *Status:* Requires visual checks. Clicking a search result triggers map camera transition (`map.flyTo()`) to the destination coordinates.
* **[NEEDS HUMAN VERIFICATION] Set as start/destination works**
  * *Status:* Requires visual checks. User can click action buttons in the search item popup to designate coordinates for routing.

---

## D) Emergency Safe Routing
* **[NEEDS HUMAN VERIFICATION] Select start point**
  * *Status:* Requires visual checks. Clicking on the map or using search results correctly places the origin pin.
* **[NEEDS HUMAN VERIFICATION] Select destination**
  * *Status:* Requires visual checks. Clicking on the map or using search results correctly places the destination pin.
* **[PASSED] Safe route appears**
  * *Status:* Verified via integration tests (`UrbanHeatRisk.test.tsx` / `App.test.tsx`). Safe route GeoJSON is retrieved from the routing service and drawn in green.
* **[PASSED] Normal route appears if available**
  * *Status:* Verified. The comparison route (normal/shortest path) is loaded and drawn in blue/gray for comparison.
* **[PASSED] Recommendation appears**
  * *Status:* Verified. Routing panel displays a clear recommendation box recommending the safe route or normal route based on live risk.
* **[PASSED] Route explanation works**
  * *Status:* Verified. The bottom-left routing panel explains the safety score and travel time differences.

---

## E) Heat Mode
* **[PASSED] Switch to Heat Risk**
  * *Status:* Verified via integration tests (`UrbanHeatRisk.test.tsx`). Clicking the Heat tab switches UI state, updating layers and cards.
* **[NEEDS HUMAN VERIFICATION] Heat layer visible on map**
  * *Status:* Requires visual checks. The Landsat-derived heat anomaly layer is requested from `/api/weather-impact/heat/layer/latest` and rendered with a thermal/red gradient.
* **[PASSED] Heat-specific bottom cards visible**
  * *Status:* Verified. Bottom cards shift from rain risk summaries to heat anomaly statistics.
* **[PASSED] Heat summary visible**
  * *Status:* Verified. Overall heat risks and counts (low/medium/high) are displayed.
* **[PASSED] Heat legend/chips clean**
  * *Status:* Verified. The legend switches to temperature range intervals (e.g. °C anomaly).
* **[NEEDS HUMAN VERIFICATION] Controls drawer scrollbars styled**
  * *Status:* Requires visual checks. Custom CSS scrollbars (e.g. `scrollbar-thin scrollbar-thumb-muted-foreground`) should be applied to prevent default browser styling.

---

## F) Heat Explainability
* **[NEEDS HUMAN VERIFICATION] Click heat zone**
  * *Status:* Requires visual checks. Clicking a zone in the heat layer triggers a map click handler.
* **[NEEDS HUMAN VERIFICATION] Zone popup appears**
  * *Status:* Requires visual checks. A MapLibre popup with the zone code and quick metrics is rendered above the clicked coordinate.
* **[PASSED] Heat explanation panel updates**
  * *Status:* Verified via integration tests. The sidebar updates with the clicked zone's specific explainability breakdown.
* **[PASSED] Model insight shows HGB / feature count / Landsat rows**
  * *Status:* Verified. The Model Info sub-section details the `HistGradientBoostingRegressor` model, listing feature counts and the 4,932 Landsat observed training rows.

---

## G) Visual Polish & Layout Integrity
* **[PASSED] No disclaimer text visible in dashboard UI**
  * *Status:* Verified via code inspection and tests. Text containing disclaimers/honesty claims has been removed from main components (`LayerToggle.tsx`, `ExplainabilityPanel.tsx`) and moved into backend reports/model cards or hidden modals.
* **[NEEDS HUMAN VERIFICATION] No ugly default scrollbar**
  * *Status:* Requires visual checks. Check side panels and scrollable lists to ensure custom scrollbar styles are applied.
* **[NEEDS HUMAN VERIFICATION] No major card clipping**
  * *Status:* Requires visual checks. Check sidebar sections to confirm text is readable and cards do not clip on smaller screen heights.
* **[NEEDS HUMAN VERIFICATION] No map control overlap issue**
  * *Status:* Requires visual checks. Map navigation controls (zoom, compass) are positioned so they do not overlap UI cards.
* **[NEEDS HUMAN VERIFICATION] No broken layout at 100% zoom**
  * *Status:* Requires visual checks. Ensure layout behaves responsively on standard 1080p and laptop screens.

---

## H) Regression Checks
* **[PASSED] Rain mode still works after switching back from Heat mode**
  * *Status:* Verified. Switching tabs repeatedly updates map sources and local state seamlessly.
* **[PASSED] Routing still works after switching modes**
  * *Status:* Verified. Path calculation is mode-agnostic and relies on current coordinates.
* **[PASSED] Explainability tabs still work**
  * *Status:* Verified. Clicking between factors and global feature imports updates panels without state loss.
