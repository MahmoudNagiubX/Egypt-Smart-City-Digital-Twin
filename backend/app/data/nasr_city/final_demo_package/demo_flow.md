# 12-Step Demo Flow Script

This script guides the presenter through the live demo of the Geo Weather (Nasr City) dashboard, explaining interactive operations step-by-step.

---

### Step 1: Open the Application
* **Action:** Open your browser and navigate to the frontend URL (typically `http://localhost:5173`).
* **What to Say:** "Welcome to the Geo Weather Dashboard. We're launching the dashboard, which acts as a decision-support system for emergency mobility and environmental risks in Nasr City."
* **What the Evaluator Should Notice:** The clean welcome/landing page loads, showing a summary of the model capabilities, before the user proceeds to the main dashboard without layout issues.

### Step 2: Show Live Weather Status
* **Action:** Direct attention to the top-right header section indicating "Live Forecast Mode".
* **What to Say:** "The system is currently configured in Live Forecast Mode. It actively pulls meteorological metrics directly from Open-Meteo services rather than simulating weather events."
* **What the Evaluator Should Notice:** The live weather indicator is active, demonstrating integration with live web APIs.

### Step 3: Show Current Weather, Forecast, and AQI
* **Action:** Hover over and read details in the top-left sidebar cards representing weather metrics.
* **What to Say:** "Here we can review current temperature, humidity levels, current rain intensity, a 7-day forecast grid, and a live Air Quality Index (AQI) tracking particulate levels."
* **What the Evaluator Should Notice:** The data structure loads properly; numbers are realistic and reflect actual live conditions.

### Step 4: Show Rain Risk Mode
* **Action:** Confirm the active tab in the main layers panel is set to "Rain Risk".
* **What to Say:** "By default, the dashboard opens in Rain Risk mode. This layer visualizes the predicted street-level flood and traffic-obstruction risk based on current and forecasted precipitation levels."
* **What the Evaluator Should Notice:** The grid cells on the map overlay are rendered in shades of green (Low Risk) and yellow/orange (Medium Risk).

### Step 5: Explain Rain Risk Overlay
* **Action:** Hover over a medium-risk grid cell on the map to show the tooltip details.
* **What to Say:** "The cells show model-estimated risk levels. The underlying weather-impact model combines topographical slope, OSM street density, and building compactness to compute this risk score."
* **What the Evaluator Should Notice:** Grid cells match the physical geography of Nasr City and tooltip hover highlights the calculated risk score.

### Step 6: Use Search to Find a Place
* **Action:** Click the search box at the top left of the map, type `hospital`, and press Enter or select the first item.
* **What to Say:** "We can search for critical safety infrastructures. Let's find emergency hospitals in Nasr City using our local OSM search tool."
* **What the Evaluator Should Notice:** Auto-suggestions appear as the user types, and selecting a hospital flies the map camera smoothly to the target coordinate.

### Step 7: Select Start and Destination
* **Action:** Set the search result as the "Start" pin, and click another point on the map to set as the "Destination" pin.
* **What to Say:** "Let's plan an emergency transit route. We'll set the hospital as our origin and a point across town as our destination."
* **What the Evaluator Should Notice:** Green (start) and orange (destination) marker pins appear at the selected locations on the map.

### Step 8: Show Standard Route vs Safer Route
* **Action:** Direct attention to the two distinct paths drawn on the map canvas.
* **What to Say:** "The system calculates two paths: a standard shortest route drawn in gray, and a safety-optimized route in green that actively bypasses zones with elevated flooding risks."
* **What the Evaluator Should Notice:** The green route avoids cells marked with higher rain risk, prioritizing low-risk grid segments even if it adds slightly to the distance.

### Step 9: Open Route Explanation
* **Action:** Look at the comparison card in the left sidebar routing drawer.
* **What to Say:** "The dashboard quantifies the trade-off. The safe route is longer, but it increases the overall safety factor, helping dispatchers evaluate time vs safety risk."
* **What the Evaluator Should Notice:** Comparative data (meters, estimated travel times, safety index delta) is rendered cleanly without text truncation.

### Step 10: Switch to Heat Risk Mode
* **Action:** Open the layers drawer and click the "Heat Risk" mode tab.
* **What to Say:** "Now, let's pivot to extreme heat risks. We switch the active view to Heat Risk mode."
* **What the Evaluator Should Notice:** The dashboard colors shift to thermal red/orange gradients, and the summary statistics update to heat metrics.

### Step 11: Show Heat Summary and Heat Overlay
* **Action:** Point to the bottom summary cards showing the count of low/medium/high heat anomaly cells.
* **What to Say:** "This layer renders relative surface temperature anomalies. The bottom cards now track the distribution of relative heat risks throughout the district."
* **What the Evaluator Should Notice:** The legend displays temperature anomaly differences in degrees Celsius, derived from Landsat thermal sensors.

### Step 12: Click Heat Zone and Show Heat Explanation/Model Insight
* **Action:** Click a high-anomaly (dark red) cell on the map, then scroll down to the explainability section of the side panel.
* **What to Say:** "Clicking a cell displays its local heat risk factors. The model lists variables such as high Built-Up Density as primary drivers. Under 'Model Info', we see this uses a HistGradientBoostingRegressor model trained on 4,932 real observed Landsat data rows."
* **What the Evaluator Should Notice:** The explanation panel updates with the specific zone code, displaying the exact features (e.g. Built-Up Surface density) influencing the prediction, showcasing the machine learning model card details.
