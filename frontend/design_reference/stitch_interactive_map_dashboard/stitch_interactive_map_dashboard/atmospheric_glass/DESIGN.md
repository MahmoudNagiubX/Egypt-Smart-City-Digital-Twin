---
name: Atmospheric Glass
colors:
  surface: '#f5faff'
  surface-dim: '#d5dbe0'
  surface-bright: '#f5faff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4f9'
  surface-container: '#e9eff4'
  surface-container-high: '#e3e9ee'
  surface-container-highest: '#dde3e8'
  on-surface: '#161c20'
  on-surface-variant: '#3d484f'
  inverse-surface: '#2b3135'
  inverse-on-surface: '#ecf1f6'
  outline: '#6d7980'
  outline-variant: '#bcc8d1'
  surface-tint: '#006688'
  primary: '#006688'
  on-primary: '#ffffff'
  primary-container: '#00c2ff'
  on-primary-container: '#004c66'
  inverse-primary: '#75d1ff'
  secondary: '#006d36'
  on-secondary: '#ffffff'
  secondary-container: '#83fba5'
  on-secondary-container: '#00743a'
  tertiary: '#8b5000'
  on-tertiary: '#ffffff'
  tertiary-container: '#ff9e2a'
  on-tertiary-container: '#693b00'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#c2e8ff'
  primary-fixed-dim: '#75d1ff'
  on-primary-fixed: '#001e2b'
  on-primary-fixed-variant: '#004d67'
  secondary-fixed: '#83fba5'
  secondary-fixed-dim: '#66dd8b'
  on-secondary-fixed: '#00210c'
  on-secondary-fixed-variant: '#005227'
  tertiary-fixed: '#ffdcbe'
  tertiary-fixed-dim: '#ffb871'
  on-tertiary-fixed: '#2d1600'
  on-tertiary-fixed-variant: '#6a3c00'
  background: '#f5faff'
  on-background: '#161c20'
  surface-variant: '#dde3e8'
  warning-amber: '#FFB800'
  alert-orange: '#FF7A00'
  aqi-green: '#E8F5E9'
  text-charcoal: '#1A1C1E'
  text-muted: '#60646C'
  glass-border: rgba(255, 255, 255, 0.5)
  glass-fill: rgba(255, 255, 255, 0.8)
typography:
  display-hero:
    fontFamily: Inter
    fontSize: 56px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  metric-xl:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  container-padding: 2rem
  gutter: 1.25rem
  card-padding: 1.5rem
  stack-sm: 0.5rem
  stack-md: 1rem
---

## Brand & Style

The design system is centered on a **Premium Glassmorphism** aesthetic tailored for high-fidelity digital twin monitoring. The personality is "Futuristic Serenity"—combining technical precision with a soft, approachable visual language. 

The target audience consists of urban planners, emergency responders, and citizens who require complex data delivered through a calm, high-clarity interface.

### Key Visual Principles:
- **Atmospheric Depth:** Backgrounds utilize soft sky-blue gradients and blurred cloud formations to provide a natural context for weather data.
- **Glassmorphism:** Primary containers use frosted glass effects with high background blur (20-40px) and varying opacities (70-90%) to maintain legibility while feeling lightweight.
- **Tactile Softness:** High corner radii and thin, light-colored borders simulate physical high-end glass hardware.
- **Precision Minimalism:** Data density is kept high but readable, using small typography and generous internal padding to avoid visual clutter.

## Colors

The color palette is inspired by meteorological charts and clear sky conditions. 

- **Primary (Sky Blue/Cyan):** Used for interaction points, active states, and precipitation intensity markers.
- **Secondary (Soft Green):** Indicates safety, "Normal" status levels, and organic AQI trend fills.
- **Status Colors:** Pale yellow and orange are reserved for warnings to ensure they stand out against the blue/white base without appearing aggressive.
- **Neutral/Text:** Charcoal (#1A1C1E) is used for primary reading to provide high contrast against frosted backgrounds, while muted grays handle secondary metadata.
- **Glass System:** Backgrounds are never pure white; they are semi-transparent with a 0.5pt white border to define edges against the cloud-gradient backdrop.

## Typography

This design system uses **Inter** exclusively to leverage its neutral, highly legible character at small sizes.

- **Scale:** The system relies on a "Large Metric / Small Label" hierarchy. Large numerical values (e.g., 26°C) use `metric-xl` for immediate recognition.
- **Hero Treatment:** On the landing page, the hero text uses tight letter spacing and heavy weights to create a premium editorial feel.
- **Technical Labels:** Sub-headers and data descriptions use `label-sm` with increased letter spacing and uppercase styling to mimic aviation or satellite monitoring equipment.
- **Mobile Adjustments:** For mobile views, `display-hero` should scale down to 36px to prevent excessive line breaks.

## Layout & Spacing

The design system utilizes a **Fixed Shell Grid** model for the dashboard and a **Fluid Content** model for the landing page.

### Dashboard Layout:
- **Shell:** A centered container at 90% width of the viewport.
- **Grid:** A 12-column layout. The map area spans 8 columns, while the Detail Sidebar spans 4 columns.
- **Gutters:** 20px (1.25rem) spacing between glass cards to allow the background clouds to "peek through," enhancing the glass effect.

### Responsive Reflow:
- **Desktop (1440px+):** Sidebar on the right, analytics below the map.
- **Tablet (768px - 1024px):** Sidebar remains but map and analytics cards may collapse into a single column.
- **Mobile (<768px):** All glass containers stack vertically. Container padding reduces from 2rem to 1rem.

## Elevation & Depth

Hierarchy is established through **transparency and blur** rather than traditional shadow casting.

- **Level 1 (Main Shell):** 80% opacity with 40px backdrop blur. This separates the workspace from the atmospheric background.
- **Level 2 (In-app Cards):** 90% opacity with 20px blur. Features a thin 1px white border (`rgba(255, 255, 255, 0.5)`).
- **Overlays (Modals/Tooltips):** Near-opaque white or charcoal with a soft 12px drop shadow (0px 4px 12px rgba(0,0,0,0.1)) to indicate the highest level of interactivity.
- **Visual Markers:** Map overlays (heatmaps) should use organic, blurred edges to represent weather fluidity, rather than hard geometric shapes.

## Shapes

The shape language is consistently rounded to reinforce the "Soft Modern" style.

- **Main Containers:** Use a radius between 18px and 22px (`rounded-xl`).
- **Interactive Elements:** Buttons and input fields use a 12px radius (`rounded-lg`).
- **Pills:** Navigation items and status chips use full pill rounding (999px) for a friendly, approachable feel.
- **Charts:** Bar charts should have subtle top-rounding (2px-4px) to avoid looking "sharp" or aggressive.

## Components

### Buttons
- **Primary:** Solid charcoal background with white text for the Landing Page. Bright Cyan with white text for "Export" or "Action" items in the dashboard.
- **Secondary/Ghost:** Translucent white background with a thin border.
- **Icon Buttons:** Circular glass containers with centered 20px icons.

### Frosted Cards
- Every card must include a header with a title and a three-dot vertical menu for "more options."
- Footer actions in cards should be placed on a very light gray (2-4% opacity) rounded strip.

### Charts
- **AQI Trends:** Stepped line charts with a semi-transparent green area fill. Axis lines should be 0.5pt muted gray.
- **Precipitation:** Vertical bars in Bright Cyan. Use a red-dotted vertical line to indicate "Now."

### Monitoring Details
- Use three-column grids for weather metrics (Humidity, Wind, Pressure) with labels in `label-sm` and values in `body-lg` bold.
- Use weather icons that are multi-colored and soft (gradient-based) rather than flat monochrome.

### Map Controls
- Floating glass pillar on the right side of the map containing: Layer toggle, Navigation arrow, and +/- zoom.