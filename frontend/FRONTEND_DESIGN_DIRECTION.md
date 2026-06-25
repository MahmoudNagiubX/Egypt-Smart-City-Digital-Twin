# Frontend Design Direction — Senior UI Quality Bar

Product:
Nasr City Weather Impact Dashboard

Design mood:
* professional smart-city operations dashboard
* dark geospatial command center
* clean, premium, technical, readable
* map-first
* realistic operations UI, not SaaS landing page

Visual system:
* near-black / slate background
* glassy dark panels with subtle borders
* cyan/teal primary accent
* risk colors:
  * low: green
  * medium: amber
  * high: red
* normal route: neutral dashed line
* weather-safe route: cyan/blue highlighted line
* emergency facilities: clear medical/emergency markers

Layout:
* full-screen dashboard
* map takes most of the screen
* left sidebar for layers/events/routes
* top compact status/header bar
* right or bottom panel for selected details and route comparison
* no huge empty cards
* no random generic icons

Interaction quality:
* layer toggles must be responsive
* event selector updates map smoothly
* zone click opens useful popup
* route comparison panel clearly compares normal vs weather-safe route
* loading states use skeletons
* errors are readable and actionable
* empty states explain what is missing

Use:
* shadcn/ui Card, Badge, Tabs, Sheet, Select, Switch, Tooltip, Skeleton, Separator, ScrollArea, ToggleGroup, Progress, Alert, Table
* MapLibre GL JS
* Motion for subtle transitions only
* lucide-react icons only where meaningful
* Recharts only for compact useful charts

Do not:
* use fake data
* hardcode backend values if API exists
* claim official flood prediction accuracy
* claim official emergency dispatch authority
* overuse gradients
* overuse animations
* create too many components
* use Redux/Zustand unless truly needed

Required visible honesty note:
"Predictions are model-estimated weather-impact risk scores derived from real observed and satellite data. They are not verified street-level flood incident labels. Routes are decision-support prototype outputs, not official emergency dispatch instructions."

Quality bar:
The dashboard should look like it was built by a senior frontend engineer for a smart-city operations demo.
