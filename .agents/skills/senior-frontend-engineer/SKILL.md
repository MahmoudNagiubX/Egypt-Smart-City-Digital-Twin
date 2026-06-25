# Senior Frontend Engineer Skill

Use this skill whenever implementing or reviewing frontend code for the Nasr City Weather Impact Dashboard.

## Role

Act like a senior frontend engineer building a production-quality geospatial operations dashboard.

The UI must look intentional, polished, and human-designed, not like a generic AI-generated template.

## Core Principles

* Build map-first interfaces.
* Keep components small, readable, and purposeful.
* Use real backend API data only.
* Do not hardcode risk values or route metrics.
* Prefer clear user flows over decorative UI.
* Use TypeScript types carefully but do not over-engineer.
* Avoid Redux/Zustand unless truly needed.
* Use local React state and hooks.
* Build graceful loading, error, and empty states.
* Use shadcn/ui components for consistent UI primitives.
* Use lucide-react icons only where they add meaning.

## UI Quality Bar

The dashboard should feel like a smart-city control room:

* dark command-center look
* sharp information hierarchy
* compact but readable cards
* clear layer controls
* useful route comparison panel
* informative popups
* visible honesty note
* no generic SaaS landing-page design
* no random gradients
* no huge empty cards
* no meaningless icons

## Data Rules

Use API responses from:

/api/weather-impact

Never fake:

* prediction rows
* risk scores
* route metrics
* event ids
* emergency facilities
* GeoJSON layers

If API data is missing, show a clear error or empty state.

## Honesty Rule

Always show this note somewhere visible:

"Predictions are model-estimated weather-impact risk scores derived from real observed and satellite data. They are not verified street-level flood incident labels. Routes are decision-support prototype outputs, not official emergency dispatch instructions."

## Review Checklist

Before finishing frontend work, verify:

* npm run build passes
* npm test passes
* no TypeScript errors
* no fake data
* no official flood-label claims
* no official emergency-dispatch claims
* dashboard uses API data
* UI is readable at 1366x768 and 1920x1080
