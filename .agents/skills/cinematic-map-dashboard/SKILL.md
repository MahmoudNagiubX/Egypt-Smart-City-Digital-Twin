# Cinematic Map Dashboard Skill

Use this skill whenever implementing the map, map layers, risk visualization, route visualization, or map interactions.

## Goal

Create a cinematic smart-city geospatial dashboard.

The map should feel alive and interactive, like a tactical urban operations map, while remaining professional and readable.

Do not copy any specific game or proprietary map style. Use a general game-inspired, cinematic, tactical map feeling.

## Map Mood

* dark urban map
* high-contrast risk overlays
* subtle glow effects
* smooth camera movement
* animated route emphasis
* clean map controls
* visual hierarchy that makes risk and routes obvious

## Map Stack

Use:

* MapLibre GL JS
* GeoJSON sources from backend API
* React hooks
* CSS variables and Tailwind classes
* shadcn/ui for controls and panels

## Layer Styling

Boundary:

* subtle cyan outline
* low opacity fill or no fill

Grid:

* thin slate/cyan line
* visible only when zoomed enough or toggle enabled

Risk:

* low = green
* medium = amber
* high = red
* use opacity and subtle glow
* avoid fully hiding the basemap

Emergency facilities:

* clear medical/emergency marker
* preferably pulse or halo on hover
* popup with name/type

Normal route:

* neutral gray or white
* dashed line
* lower visual priority

Weather-safe route:

* cyan/blue
* solid line
* stronger width
* subtle glow
* optional animated pulse/dash effect

## Interactions

Implement:

* layer toggles
* event selector
* risk layer selector
* route mode selector
* zone popup on click
* route comparison panel
* hover cursor feedback
* smooth map flyTo when selecting major event/route if safe

## Performance Rules

* Do not repeatedly recreate the map.
* Add sources/layers only after map load.
* Update existing sources with setData where possible.
* Remove event listeners on cleanup.
* Avoid duplicate source/layer errors.
* Do not render thousands of DOM markers; prefer GeoJSON layers.
