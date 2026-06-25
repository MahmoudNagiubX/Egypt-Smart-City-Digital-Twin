// @vitest-environment jsdom
import { render, screen, cleanup } from '@testing-library/react';
import { expect, test, vi, afterEach } from 'vitest';
import { ExplainabilityPanel } from '../components/ExplainabilityPanel';
import { RoutePanel } from '../components/RoutePanel';
import type { 
  ZoneExplanationResponse, 
  RouteExplanationResponse,
  ModelExplainabilitySummaryResponse
} from '../types/api';

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

// Mock getModelExplainabilitySummary API call
vi.mock('../api/client', () => ({
  getModelExplainabilitySummary: vi.fn().mockResolvedValue({
    status: "ok",
    model_name: "weather_impact_ridge_model.joblib",
    model_type: "Ridge Regression",
    target: "data_driven_weather_impact_score",
    top_global_features: [
      { feature: "rain_24h_mm", label: "24h Rainfall", importance: 0.85, reason: "Direct rainfall accumulation" },
      { feature: "built_surface_mean", label: "Built-Up Density", importance: 0.65, reason: "Impervious surface area runoff" },
      { feature: "population_sum", label: "Exposed Population", importance: 0.45, reason: "Exposed assets and human activity" }
    ],
    metrics: { mae: 0.015 },
    known_limitations: ["Resolution is limited to 250m grid cells.", "Assumes uniform topography within grid."],
    honesty_note: "Model-estimated risk scores only. Not a hydraulic simulation."
  } as ModelExplainabilitySummaryResponse),
  getZoneExplanation: vi.fn(),
  explainRoute: vi.fn()
}));

const mockZoneExplanation: ZoneExplanationResponse = {
  status: "ok",
  zone_code: "NSR-GRID-119",
  zone_label: "Zone 119",
  mode: "live",
  risk_score: 0.72,
  risk_class: "high",
  risk_label: "High Risk",
  summary: "High rainfall accumulation coupled with high built-up surface density increases water accumulation risk.",
  top_factors: [
    {
      factor: "rain_24h_mm",
      label: "24h Rainfall",
      value: 45.2,
      impact: "increases risk",
      reason: "Significant rain accumulation over the past 24 hours."
    },
    {
      factor: "built_surface_mean",
      label: "Built-Up Density",
      value: 0.82,
      impact: "increases risk",
      reason: "High built-up surface area prevents natural water drainage."
    }
  ],
  explanation_text: "Detailed explanation text.",
  confidence_note: "Decision-support estimate only. Not an official flood report.",
  honesty_note: "Based on static elevation contours and observed storm parameters."
};

const mockRouteExplanation: RouteExplanationResponse = {
  status: "ok",
  mode: "live",
  recommendation: "weather_safe_route_recommended",
  recommendation_label: "Weather-Safe Route Recommended",
  summary: "The weather-safe route avoids 4 high-risk segments with a reasonable ETA tradeoff of 8%.",
  route_reasons: [
    {
      label: "Risk Reduction",
      value: "40.0%",
      reason: "Calculated weather-impact risk score is reduced from 0.5 to 0.3."
    },
    {
      label: "ETA Tradeoff",
      value: "+8.3%",
      reason: "Travel time increases by 30 seconds compared to the normal route."
    }
  ],
  normal_route_explanation: {
    summary: "Crosses multiple flooding hotspots near El-Nasr road.",
    risk_level: "high",
    high_risk_segments: 4,
    mean_risk_score: 0.5
  },
  safe_route_explanation: {
    summary: "Bypasses low-lying segments via secondary streets.",
    risk_level: "low",
    high_risk_segments: 0,
    mean_risk_score: 0.1
  },
  comparison: {
    risk_reduction_percent: 40,
    eta_tradeoff_percent: 8,
    avoided_high_risk_segments: 4,
    normal_distance_m: 2000,
    safe_distance_m: 2200
  },
  honesty_note: "Prototype route guidance only. Not official dispatch instructions."
};

test('ExplainabilityPanel renders with active Area tab', () => {
  render(
    <ExplainabilityPanel
      zoneExplanation={mockZoneExplanation}
      routeExplanation={null}
      onClose={() => {}}
      activeTab="area"
    />
  );

  // Checks header and tab links
  expect(screen.getByText("Explainability")).toBeDefined();
  expect(screen.getByText("Area Info")).toBeDefined();
  expect(screen.getByText("Zone 119 Explainability")).toBeDefined();
  expect(screen.getByText("High rainfall accumulation coupled with high built-up surface density increases water accumulation risk.")).toBeDefined();
});

test('Zone explanation top factors render with human labels and do not show raw names as title', () => {
  render(
    <ExplainabilityPanel
      zoneExplanation={mockZoneExplanation}
      routeExplanation={null}
      onClose={() => {}}
      activeTab="area"
    />
  );

  // Must render human-readable labels
  expect(screen.getByText("24h Rainfall")).toBeDefined();
  expect(screen.getByText("Built-Up Density")).toBeDefined();

  // Must NOT render raw factor names as titles
  expect(screen.queryByText("rain_24h_mm")).toBeNull();
  expect(screen.queryByText("built_surface_mean")).toBeNull();

  // Render values and reasons
  expect(screen.getByText("45.2")).toBeDefined();
  expect(screen.getByText("0.82")).toBeDefined();
  expect(screen.getByText("Significant rain accumulation over the past 24 hours.")).toBeDefined();
  expect(screen.getByText("High built-up surface area prevents natural water drainage.")).toBeDefined();
  
  // Render impact badges
  const badges = screen.getAllByText("increases risk");
  expect(badges.length).toBe(2);
});

test('RoutePanel shows "Why this route?" when comparison is provided', () => {
  const onWhyThisRouteMock = vi.fn();
  render(
    <RoutePanel
      comparison={{
        normal_distance_m: 2000,
        safe_distance_m: 2200,
        normal_weather_eta_sec: 360,
        safe_weather_eta_sec: 390,
        normal_mean_risk_score: 0.5,
        safe_mean_risk_score: 0.3,
        risk_reduction_percent: 40,
        eta_tradeoff_percent: 8,
        avoided_high_risk_segments: 4,
        safe_route_available: true,
        safe_route_quality: "strong",
        honesty_note: "Note"
      }}
      eventType="latest"
      onEventTypeChange={() => {}}
      routeVisibility="both"
      onRouteVisibilityChange={() => {}}
      onWhyThisRoute={onWhyThisRouteMock}
    />
  );

  const button = screen.getByRole('button', { name: /Why this route\?/i });
  expect(button).toBeDefined();
  button.click();
  expect(onWhyThisRouteMock).toHaveBeenCalledTimes(1);
});

test('Route explanation tab renders recommendation label, summary, and tradeoffs', () => {
  render(
    <ExplainabilityPanel
      zoneExplanation={null}
      routeExplanation={mockRouteExplanation}
      onClose={() => {}}
      activeTab="route"
    />
  );

  // Recommendations and tradeoffs
  expect(screen.getByText("Weather-Safe Route Recommended")).toBeDefined();
  expect(screen.getByText("The weather-safe route avoids 4 high-risk segments with a reasonable ETA tradeoff of 8%.")).toBeDefined();
  expect(screen.getByText("Risk Reduction")).toBeDefined();
  expect(screen.getByText("40.0%")).toBeDefined();
  expect(screen.getByText("ETA Tradeoff")).toBeDefined();
  expect(screen.getByText("+8.3%")).toBeDefined();
});

test('Honesty notes render inside the panels', () => {
  const { rerender } = render(
    <ExplainabilityPanel
      zoneExplanation={mockZoneExplanation}
      routeExplanation={mockRouteExplanation}
      onClose={() => {}}
      activeTab="area"
    />
  );

  // Area disclaimers
  expect(screen.getByText(/Decision-support estimate only. Not an official flood report/i)).toBeDefined();

  // Re-render route tab
  rerender(
    <ExplainabilityPanel
      zoneExplanation={mockZoneExplanation}
      routeExplanation={mockRouteExplanation}
      onClose={() => {}}
      activeTab="route"
    />
  );

  // Route disclaimers
  expect(screen.getByText(/Prototype route guidance only. Not official dispatch instructions/i)).toBeDefined();
});
