// @vitest-environment jsdom
import { render, screen, act, cleanup, fireEvent } from '@testing-library/react';
import { expect, test, vi, afterEach } from 'vitest';
import React from 'react';

// Mock IntersectionObserver
class IntersectionObserverMock {
  observe = vi.fn();
  unobserve = vi.fn();
  disconnect = vi.fn();
}
(globalThis as any).IntersectionObserver = IntersectionObserverMock as any;

// Mock maplibre-gl
vi.mock('maplibre-gl', () => {
  class MapMock {
    addControl() {}
    on() {}
    remove() {}
    addSource() {}
    addLayer() {}
    getStyle() { return { layers: [] }; }
    getSource() {
      return {
        setData: () => {}
      };
    }
    getLayer() { return true; }
    getLayoutProperty() { return "visible"; }
    setLayoutProperty() {}
    setPaintProperty() {}
  }
  class PopupMock {
    setLngLat() { return this; }
    setHTML() { return this; }
    addTo() {}
  }
  const NavigationControlMock = function() {};
  const ScaleControlMock = function() {};
  return {
    default: {
      Map: MapMock,
      NavigationControl: NavigationControlMock,
      ScaleControl: ScaleControlMock,
      Popup: PopupMock
    },
    Map: MapMock,
    NavigationControl: NavigationControlMock,
    ScaleControl: ScaleControlMock,
    Popup: PopupMock
  };
});

// Mock motion/react
vi.mock('motion/react', () => {
  const motionMock = new Proxy({}, {
    get: (_target, key) => {
      return ({ children, ...props }: any) => {
        const cleanProps = { ...props };
        delete cleanProps.initial;
        delete cleanProps.animate;
        delete cleanProps.exit;
        delete cleanProps.transition;
        delete cleanProps.whileInView;
        const Tag = key as any;
        return <Tag {...cleanProps}>{children}</Tag>;
      };
    }
  });
  return {
    motion: motionMock,
    AnimatePresence: ({ children }: any) => <>{children}</>,
    useReducedMotion: () => true,
  };
});

// Mock api client
import * as client from '../api/client';
vi.mock('../api/client', () => ({
  getHealth: vi.fn().mockResolvedValue({ status: "healthy", module_name: "Weather Impact Module" }),
  getSummary: vi.fn().mockResolvedValue({ zone_count: 416, highest_risk_zones: [] }),
  getEvents: vi.fn().mockResolvedValue([]),
  getBoundaryLayer: vi.fn().mockResolvedValue({ type: "FeatureCollection", features: [] }),
  getGridLayer: vi.fn().mockResolvedValue({ type: "FeatureCollection", features: [] }),
  getEmergencyFacilities: vi.fn().mockResolvedValue({ type: "FeatureCollection", features: [] }),
  getPlaces: vi.fn().mockResolvedValue({ type: "FeatureCollection", features: [] }),
  getLatestRiskLayer: vi.fn().mockResolvedValue({ type: "FeatureCollection", features: [] }),
  getTopRainRiskLayer: vi.fn().mockResolvedValue({ type: "FeatureCollection", features: [] }),
  getRiskSummaryLayer: vi.fn().mockResolvedValue({ type: "FeatureCollection", features: [] }),
  getEventRiskLayer: vi.fn().mockResolvedValue({ type: "FeatureCollection", features: [] }),
  getRoutingStatus: vi.fn().mockResolvedValue({ status: "ok" }),
  getDemoRoute: vi.fn().mockResolvedValue({ type: "FeatureCollection", features: [] }),
  getLiveWeather: vi.fn().mockResolvedValue({ status: "ok" }),
  getSevenDayForecast: vi.fn().mockResolvedValue({ daily: [] }),
  getAirQuality: vi.fn().mockResolvedValue({ current: { pm10: 5, pm2_5: 2 } }),
  getLiveWeatherRiskLayer: vi.fn().mockResolvedValue({ type: "FeatureCollection", features: [] }),
  getLiveWeatherReport: vi.fn().mockResolvedValue({ status: "ok" }),
  getLiveRoutingStatus: vi.fn().mockResolvedValue({ status: "ok" }),
  requestLiveEmergencyRoute: vi.fn().mockResolvedValue({}),
  getHeatHealth: vi.fn().mockResolvedValue({
    status: "healthy",
    model_available: true,
    latest_layer_available: true,
    explainability_available: true,
    message: "HistGradientBoostingRegressor heat model online"
  }),
  getLatestHeatLayer: vi.fn().mockResolvedValue({
    type: "FeatureCollection",
    features: [
      {
        type: "Feature",
        properties: {
          zone_code: "NSR-GRID-123",
          predicted_heat_risk_score: 0.75,
          predicted_heat_risk_class: "high",
          predicted_heat_anomaly_c: 4.2,
          observed_lst_c: 42.1,
          date: "2026-06-25"
        },
        geometry: { type: "Polygon", coordinates: [] }
      }
    ]
  }),
  getHeatSummary: vi.fn().mockResolvedValue({
    status: "ok",
    date: "2026-06-25",
    zone_count: 100,
    risk_counts: { low: 50, medium: 30, high: 20 },
    max_heat_anomaly_c: 4.5,
    mean_heat_anomaly_c: 2.1,
    hottest_zone: {
      zone_code: "NSR-GRID-123",
      zone_label: "Area 123",
      predicted_heat_anomaly_c: 4.5,
      predicted_heat_risk_class: "High"
    },
    model_name: "HistGradientBoostingRegressor",
    honesty_note: "Satellite-based heat estimate, not an official warning."
  }),
  getHeatZoneExplanation: vi.fn().mockResolvedValue({
    status: "ok",
    zone_code: "NSR-GRID-123",
    zone_label: "Area 123",
    date: "2026-06-25",
    predicted_heat_risk_class: "high",
    predicted_heat_anomaly_c: 4.5,
    predicted_heat_risk_score: 0.75,
    summary: "High density of built surface contributing to heat accumulation.",
    top_factors: [
      { factor: "built_up_density", label: "Built-Up Density", value: 0.85, impact: "increases anomaly", reason: "Dense structures hold heat." }
    ],
    explanation_text: "A dense build-up of structures in this area causes elevated surface temp.",
    honesty_note: "Satellite-based heat estimate, not an official warning."
  }),
  getHeatModelSummary: vi.fn().mockResolvedValue({
    status: "ok",
    model_name: "HistGradientBoostingRegressor",
    target: "heat_anomaly_c",
    feature_count: 61,
    top_global_features: [
      { feature: "built_up_density", label: "Built-Up Density", importance: 0.45, reason: "Built environments absorb more solar radiation." }
    ],
    data_authenticity: {
      landsat_rows: 4932,
      fallback_rows: 0,
      ready_for_training: true
    },
    honesty_note: "Trained on real Landsat-derived heat anomalies."
  })
}));

import App from '../App';
import { LayerToggle } from '../components/LayerToggle';
import { ExplainabilityPanel } from '../components/ExplainabilityPanel';

afterEach(() => {
  cleanup();
});

test('1. Heat API client methods exist and are functions', () => {
  expect(typeof client.getHeatHealth).toBe('function');
  expect(typeof client.getLatestHeatLayer).toBe('function');
  expect(typeof client.getHeatSummary).toBe('function');
  expect(typeof client.getHeatZoneExplanation).toBe('function');
  expect(typeof client.getHeatModelSummary).toBe('function');
});

test('2. LayerToggle renders Heat Risk option, opacities, and toggles cleanly', () => {
  const onActiveRiskLayerChange = vi.fn();
  const onToggle = vi.fn();
  const setRiskFillOpacity = vi.fn();
  const setGridLineOpacity = vi.fn();

  // Test activeRiskLayer === "rain"
  const { rerender } = render(
    <LayerToggle
      mapMode="today"
      onMapModeChange={() => {}}
      selectionState="idle"
      routingError={null}
      onResetRoute={() => {}}
      layers={{
        boundary: true,
        grid: false,
        roadsLabels: true,
        hospitals: true,
        clinics: false,
        mosques: false,
        malls: false,
        schools: false,
        universities: false,
        police: false,
        fireStations: false,
        emergency: true,
        latestRisk: false,
        topRainRisk: false,
        riskSummary: false,
        liveRisk: false,
      }}
      onToggle={onToggle}
      riskFillOpacity={0.4}
      setRiskFillOpacity={setRiskFillOpacity}
      gridLineOpacity={0.15}
      setGridLineOpacity={setGridLineOpacity}
      events={[]}
      selectedEventId={null}
      onSelectEvent={() => {}}
      riskDisplayMode="focus"
      setRiskDisplayMode={() => {}}
      activeRiskLayer="rain"
      onActiveRiskLayerChange={onActiveRiskLayerChange}
    />
  );

  // Switch Segmented Mode is displayed
  expect(screen.getByText("Active Mode")).toBeDefined();
  const heatButton = screen.getByText("Heat Risk");
  expect(heatButton).toBeDefined();

  // Trigger switch
  fireEvent.click(heatButton);
  expect(onActiveRiskLayerChange).toHaveBeenCalledWith("heat");

  // Rerender as heat mode
  rerender(
    <LayerToggle
      mapMode="today"
      onMapModeChange={() => {}}
      selectionState="idle"
      routingError={null}
      onResetRoute={() => {}}
      layers={{
        boundary: true,
        grid: false,
        roadsLabels: true,
        hospitals: true,
        clinics: false,
        mosques: false,
        malls: false,
        schools: false,
        universities: false,
        police: false,
        fireStations: false,
        emergency: true,
        latestRisk: false,
        topRainRisk: false,
        riskSummary: false,
        liveRisk: false,
      }}
      onToggle={onToggle}
      riskFillOpacity={0.4}
      setRiskFillOpacity={setRiskFillOpacity}
      gridLineOpacity={0.15}
      setGridLineOpacity={setGridLineOpacity}
      events={[]}
      selectedEventId={null}
      onSelectEvent={() => {}}
      riskDisplayMode="focus"
      setRiskDisplayMode={() => {}}
      activeRiskLayer="heat"
      onActiveRiskLayerChange={onActiveRiskLayerChange}
    />
  );

  // Urban Heat title and sliders should be displayed
  expect(screen.getByText("Urban Heat")).toBeDefined();
  expect(screen.getByText("Heat Layer Opacity")).toBeDefined();
  expect(screen.getByText("Grid Line Opacity")).toBeDefined();
});

test('3. ExplainabilityPanel displays human-readable factors and Landsat authenticity for heat model', () => {
  const onClose = vi.fn();
  const heatExplanation = {
    status: "ok",
    zone_code: "NSR-GRID-123",
    zone_label: "Area 123",
    date: "2026-06-25",
    predicted_heat_risk_class: "High",
    predicted_heat_anomaly_c: 4.4,
    predicted_heat_risk_score: 0.85,
    summary: "Built-up surface anomaly",
    top_factors: [
      { factor: "built_up_density", label: "Built-Up Density", value: 0.85, impact: "increases anomaly", reason: "Holds heat." }
    ],
    explanation_text: "Heat zone analysis",
    honesty_note: "Satellite-based heat estimate, not an official warning."
  };

  const heatModelSummary = {
    status: "ok",
    model_name: "HistGradientBoostingRegressor",
    target: "heat_anomaly_c",
    feature_count: 61,
    top_global_features: [
      { feature: "built_up_density", label: "Built-Up Density", importance: 0.45, reason: "Heat driver." }
    ],
    data_authenticity: {
      landsat_rows: 4932,
      fallback_rows: 0,
      ready_for_training: true
    },
    honesty_note: "Satellite-based heat estimate, not an official warning."
  };

  const { rerender } = render(
    <ExplainabilityPanel
      zoneExplanation={null}
      routeExplanation={null}
      onClose={onClose}
      activeTab="area"
      zoneLoading={false}
      routeLoading={false}
      activeRiskLayer="heat"
      heatZoneExplanation={heatExplanation}
      heatModelSummary={heatModelSummary}
    />
  );

  // Verifying area explanation
  expect(screen.getByText("Why this heat risk?")).toBeDefined();
  expect(screen.getByText("Built-Up Density")).toBeDefined();
  expect(screen.getByText("+4.4°C")).toBeDefined();

  // Switch tab to model
  rerender(
    <ExplainabilityPanel
      zoneExplanation={null}
      routeExplanation={null}
      onClose={onClose}
      activeTab="model"
      zoneLoading={false}
      routeLoading={false}
      activeRiskLayer="heat"
      heatZoneExplanation={heatExplanation}
      heatModelSummary={heatModelSummary}
    />
  );

  // Verifying model explanation
  expect(screen.getByText("Model: HistGradientBoostingRegressor")).toBeDefined();
  expect(screen.getByText("Landsat Observed Rows:")).toBeDefined();
  expect(screen.getByText("4932")).toBeDefined();
});

test('4. Full App Integration renders dashboard elements, search, routing panel, and disclaimers without official public-health warning claim', async () => {
  await act(async () => {
    render(<App />);
  });

  const openBtn = screen.getByText("Open Live Map");
  await act(async () => {
    fireEvent.click(openBtn);
  });

  // Verify search renders
  expect(screen.getByPlaceholderText(/Search street/i)).toBeDefined();

  // Open drawer
  const controlsBtn = screen.getByText(/Controls/i);
  await act(async () => {
    fireEvent.click(controlsBtn);
  });

  // Toggle heat risk
  const heatBtn = screen.getByText("Heat Risk");
  await act(async () => {
    fireEvent.click(heatBtn);
  });

  // Heat Risk active: check for honesty note
  expect(screen.getAllByText(/not an official warning/i).length).toBeGreaterThan(0);
  expect(screen.queryByText(/official public-health heat warning/i)).toBeNull();

  // Toggle back to rain
  const rainBtn = screen.getByText("Rain Risk");
  await act(async () => {
    fireEvent.click(rainBtn);
  });

  // Routing setup checks
  expect(screen.getByText("Route Setup")).toBeDefined();
});
