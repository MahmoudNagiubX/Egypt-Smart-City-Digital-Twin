# Frontend Motion and Performance Skill

Use this skill whenever adding animations, transitions, interactions, or frontend performance improvements.

## Goal

Add polished interactions without making the dashboard slow, distracting, or overdesigned.

## Motion Stack

Use Motion for React only for subtle UI transitions.

Use CSS transitions where simpler.

Do not animate heavy GeoJSON data through React state if MapLibre can handle it.

## Good Motion Patterns

Use:

* fade-in panels
* slide-in side panel
* subtle card hover
* route panel metric highlight
* skeleton loading
* small tab/content transitions
* optional route line dash animation through MapLibre paint/layout if lightweight

Avoid:

* full-screen animation effects
* particle systems
* bouncing cards
* random decorative motion
* repeated rerenders of map components
* motion that hides information

## Performance Rules

* Keep the map component stable.
* Do not recreate MapLibre instance on every state change.
* Memoize static config when useful.
* Keep API calls batched or controlled.
* Avoid loading all event-specific layers at once.
* Load selected event layer only when selected.
* Use simple derived state.
* Keep tests independent from backend server.

## Senior UI Interaction Rules

Every interaction should answer a user need:

* What layer am I seeing?
* Which event is selected?
* Which route is normal?
* Which route is safer?
* How much risk is reduced?
* What tradeoff did the safe route add?
* What does the system not claim?

## Accessibility

* Maintain readable contrast.
* Buttons and toggles should be keyboard-accessible where possible.
* Use semantic labels.
* Do not rely only on color; include labels/badges.

## Final Checklist

Before finishing:

* npm run build passes
* npm test passes
* map does not flicker
* panels do not jump
* route/risk controls feel responsive
* no heavy animation causes lag
* no fake data
* honesty note visible
