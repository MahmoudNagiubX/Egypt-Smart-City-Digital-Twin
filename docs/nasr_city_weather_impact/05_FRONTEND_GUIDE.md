# Frontend Dashboard Guide

This document explains how to interact with the React map dashboard to visualize risks and plan emergency transits.

---

## 1. Dashboard Layout
The dashboard UI fits within a single screen footprint (`h-screen overflow-hidden`) to avoid page-level scrollbars:
* **Map Canvas:** The center MapLibre component rendering vector tiles, boundary polylines, and hazard grids.
* **Header:** Displays live API statuses, Active Mode badges, and the geocoder search input.
* **Left Sidebar Drawer:** Houses weather metrics, routing configurations, and safety comparison outputs.
* **Right Sidebar Drawer:** Houses explainability breakdowns, local feature contribution factors, and global model cards.

---

## 2. Interactive Workflows

### Weather-Impact and Routing
1. **Explore Live Weather:** Review current temperatures, humidity levels, and AQI indices in the left card group.
2. **Search a Place:** Enter a facility (e.g. "hospital") in the search box. Select a result to fly the map camera to its coordinate.
3. **Select Transit Points:** In the search popup or right-click context menu, assign the point as "Start" or "Destination".
4. **Compare Routes:** Review the standard route drawn on the map alongside the green safe route. Compare distance, estimated time delays, and safety recommendations in the routing panel.

---

### Switching to Heat Risk
1. **Open Layers Drawer:** Open the main toggle panel on the map interface.
2. **Switch Mode:** Select the "Heat Risk" tab. The map style will shift to warm thermal gradients.
3. **Inspect Anomaly:** Click on any red grid cell. A popup will display its code and relative temperature anomaly.
4. **Inspect Explanations:** Review the sidebar panel, which lists local driving factors (e.g., Vegetation Canopy, Built-Up density) and displays model details.

---

## 3. Presentation Tips
* **Browser Zoom:** Keep browser zoom at 100% (or adjust to 90% for smaller screens) to fit all panels cleanly without scroll overlap.
* **Hide Controls:** You can toggle drawer panels closed when recording demo segments focused purely on the map visualizations.
