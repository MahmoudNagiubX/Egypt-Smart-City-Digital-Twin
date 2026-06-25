# Urban Heat Risk and Land Surface Temperature Estimation Methodology

## Overview
This module integrates satellite-based thermal observations from Landsat 8/9 with static geospatial parameters to establish a relative Urban Heat Risk dataset for Nasr City, Cairo. The goal is to identify hot zones and high-exposure areas across the 416 grid sectors.

## Target Definition
1. **LST (lst_c)**: Land Surface Temperature in Celsius, converted from Landsat Band 10 (TIRS 1).
2. **Heat Anomaly (heat_anomaly_c)**: The local variation of a grid zone's LST relative to the median LST of the entire scene on that day.
3. **Heat Risk Score (heat_risk_score)**: A weighted index computed from temperature anomalies (35%), built-up density (25%), roads (20%), and population exposure (20%).
4. **Heat Risk Class**: Categorization into 'low', 'medium', or 'high' relative vulnerability.

## Core Features Engineered
* **Thermal**: observed LST, local anomalies, scene percentile ranks, and hot zone flags.
* **Vegetation (NDVI/Canopy)**: mean/min/max NDVI, tree cover ratio, bare land ratio.
* **Built Environment (NDBI/Imperviousness)**: build-up ratio, non-residential footprint, imperviousness index.
* **Mobility**: road density, primary/secondary road densities.
* **Exposure**: WorldPop population count and density, exposure interaction terms.
* **Interaction terms**: LST x Built-up, LST x Low Vegetation, Heat Anomaly x Population, NDBI x Low NDVI.

## Known Limitations
* Satellite LST measures skin temperature, which is often 10-15°C higher than ambient air temperature during peak summer hours.
* Cloud masking blocks observations on overcast days, limiting historical records to clear days.
* Fallback estimates are generated via a physics-based spatial simulation utilizing pre-extracted local spatial statistics when satellite connection is offline.

## Disclaimer & Honesty Statement
> [!IMPORTANT]
> This heat-risk layer estimates relative urban heat exposure from satellite land-surface temperature and geospatial features. It is not an official public-health heat warning system.
