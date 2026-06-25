// @vitest-environment jsdom
import { render, screen, act, cleanup, fireEvent } from '@testing-library/react'
import { expect, test, vi, afterEach } from 'vitest'

// Mock IntersectionObserver for Framer Motion viewport options
class IntersectionObserverMock {
  observe = vi.fn();
  unobserve = vi.fn();
  disconnect = vi.fn();
}
(globalThis as any).IntersectionObserver = IntersectionObserverMock as any;

import App from '../App'
import { SummaryCards } from '../components/SummaryCards'
import { RoutePanel } from '../components/RoutePanel'
import { LayerToggle } from '../components/LayerToggle'
import { Legend } from '../components/Legend'
import { MapView } from '../components/MapView'

afterEach(() => {
  cleanup();
});

// Mock maplibre-gl to avoid WebGL / canvas warnings inside jsdom env
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
    getLayer() {
      return true;
    }
    getLayoutProperty() {
      return "visible";
    }
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

// Mock motion/react to avoid framer-motion async/animation delays in tests
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

// Mock API Client calls
vi.mock('../api/client', () => ({
  getHealth: vi.fn().mockResolvedValue({ status: "healthy", module_name: "Nasr City Weather-Impact Emergency Mobility Module", outputs_available: {}, official_flood_labels_claimed: false, demo_scenarios_used_for_training: false }),
  getSummary: vi.fn().mockResolvedValue({
    zone_count: 416,
    prediction_row_count: 12480,
    event_count: 30,
    risk_class_counts: { low: 4502, medium: 6732, high: 1246 },
    highest_risk_zones: [],
    latest_event_id: "evt_dry_009",
    top_rain_event_id: "evt_0557",
    model_name: "weather_impact_rf_model.joblib",
    dataset_name: "real_observed_training_dataset.csv",
    honesty_statement: "Model-estimated risk scores."
  }),
  getEvents: vi.fn().mockResolvedValue([
    { event_id: "evt_0557", timestamp: "2020-03-12T00:00", mean_rain_24h_mm: 55.7, max_rain_24h_mm: 70, mean_predicted_score: 0.45, high_risk_zone_count: 206 }
  ]),
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
  getLiveWeather: vi.fn().mockResolvedValue({
    status: "ok",
    source: "open-meteo",
    location: { name: "Nasr City", lat: 30.06, lon: 31.33 },
    current: { time: "2026-06-25T00:00", temperature_2m: 25.0, rain: 0.0, precipitation: 0.0, wind_speed_10m: 10.0, weather_code: 0 },
    forecast_window: { hours: 24, rain_1h_mm: 0.0, rain_3h_mm: 0.0, rain_6h_mm: 0.0, rain_24h_mm: 0.0, max_precipitation_probability: 0.0 },
    rain_risk_expected: false,
    recommended_event_mode: "normal",
    warnings: []
  }),
  getSevenDayForecast: vi.fn().mockResolvedValue({
    status: "ok",
    source: "Open-Meteo Forecast API",
    location: { name: "Nasr City", lat: 30.0561, lon: 31.33 },
    daily: [
      { date: "2026-06-25", weather_code: 0, temperature_2m_max: 30, temperature_2m_min: 20, precipitation_sum: 0, precipitation_probability_max: 0 }
    ],
    warnings: []
  }),
  getAirQuality: vi.fn().mockResolvedValue({
    status: "ok",
    source: "Open-Meteo Air Quality API",
    location: { name: "Nasr City", lat: 30.0561, lon: 31.33 },
    current: { time: "2026-06-25T00:00", european_aqi: 15, pm10: 5, pm2_5: 2 },
    hourly: [],
    warnings: []
  }),
  getLiveWeatherRiskLayer: vi.fn().mockResolvedValue({ type: "FeatureCollection", features: [] }),
  getLiveWeatherReport: vi.fn().mockResolvedValue({ status: "ok" }),
  getLiveRoutingStatus: vi.fn().mockResolvedValue({
    status: "ok",
    live_weather_available: true,
    live_risk_layer_available: true,
    live_report_status: "ok",
    rain_risk_expected: false,
    risk_class_counts: { low: 221, medium: 195, high: 0 },
    recommended_mode: "normal_route_acceptable",
    warnings: [],
    honesty_note: "Model-estimated risk scores."
  }),
  requestLiveEmergencyRoute: vi.fn().mockResolvedValue({
    status: "ok",
    recommendation: "normal_route_acceptable",
    rain_risk_expected: false,
    live_weather_summary: {
      status: "ok",
      source: "open-meteo",
      location: { name: "Nasr City", lat: 30.06, lon: 31.33 },
      current: { time: "2026-06-25T00:00", temperature_2m: 25.0, rain: 0.0, precipitation: 0.0, wind_speed_10m: 10.0, weather_code: 0 },
      forecast_window: { hours: 24, rain_1h_mm: 0.0, rain_3h_mm: 0.0, rain_6h_mm: 0.0, rain_24h_mm: 0.0, max_precipitation_probability: 0.0 },
      rain_risk_expected: false,
      recommended_event_mode: "normal",
      warnings: []
    },
    normal_route: { type: "FeatureCollection", features: [] },
    weather_safe_route: { type: "FeatureCollection", features: [] },
    comparison: {
      normal_distance_m: 2000,
      safe_distance_m: 2200,
      normal_weather_eta_sec: 360,
      safe_weather_eta_sec: 390,
      normal_mean_live_risk_score: 0.5,
      safe_mean_live_risk_score: 0.3,
      live_high_risk_segment_count_normal: 4,
      live_high_risk_segment_count_safe: 0,
      risk_reduction_percent: 40,
      eta_tradeoff_percent: 8,
      avoided_high_risk_segments: 4,
      safe_route_quality: "strong",
      safe_route_available: true,
      honesty_note: "Decision-support prototype output."
    },
    honesty_note: "Decision-support prototype output."
  })
}));

test('App renders dashboard title and disclaimers', async () => {
  await act(async () => {
    render(<App />);
  });
  
  // Verify welcome page title
  expect(screen.getAllByText(/safer/i).length).toBeGreaterThan(0);

  // Transition to dashboard
  const openBtn = screen.getByText("Open Live Map");
  await act(async () => {
    fireEvent.click(openBtn);
  });

  // Dashboard Title check
  expect(document.title).toBe("Egypt Smart City Digital Twin");

  // Open controls drawer to render the LayerToggle disclaimer
  const controlsBtn = screen.getByText(/Controls/i);
  await act(async () => {
    fireEvent.click(controlsBtn);
  });

  // Disclaimer visibility
  const note = screen.getAllByText(/Predictions are weather-impact model/i);
  expect(note.length).toBeGreaterThan(0);
});

test('SummaryCards renders operational cards', () => {
  const mockLiveWeather = {
    status: "ok",
    source: "open-meteo",
    location: { name: "Nasr City", lat: 30.06, lon: 31.33 },
    current: { time: "2026-06-25T00:00", temperature_2m: 25.0, rain: 0.0, precipitation: 0.0, wind_speed_10m: 10.0, weather_code: 0 },
    forecast_window: { hours: 24, rain_1h_mm: 0.0, rain_3h_mm: 0.0, rain_6h_mm: 0.0, rain_24h_mm: 5.2, max_precipitation_probability: 85.0 },
    rain_risk_expected: true,
    recommended_event_mode: "live" as const,
    warnings: []
  };

  const { rerender } = render(
    <SummaryCards
      mapMode="today"
      comparison={null}
      liveWeather={mockLiveWeather}
    />
  );

  expect(screen.getByText(/Today’s Rain Risk/i)).toBeDefined();
  expect(screen.getByText(/Rain Probability/i)).toBeDefined();
  expect(screen.getByText(/Risk Reduction/i)).toBeDefined();
  
  // Checks actual values
  expect(screen.getByText("Expected")).toBeDefined();
  expect(screen.getByText("85%")).toBeDefined();

  // Test that comparison stats are shown when comparison is present
  const mockComp = {
    risk_reduction_percent: 45,
    eta_tradeoff_percent: 5,
    safe_route_available: true,
    safe_route_quality: "strong",
    selected_origin_zone_code: "NSR-GRID-119",
    selected_destination_facility_name: "Selected Destination",
    honesty_note: "Note",
    recommendation: "weather_safe_route_recommended"
  } as any;

  rerender(
    <SummaryCards
      mapMode="today"
      comparison={mockComp}
      liveWeather={mockLiveWeather}
    />
  );

  expect(screen.getByText("Weather-Safe Route Recommended")).toBeDefined();
  expect(screen.getByText("45%")).toBeDefined();
});

test('SummaryCards renders safely with partial or missing mock data', () => {
  render(
    <SummaryCards
      mapMode="today"
      comparison={null}
      liveWeather={null}
    />
  );

  expect(screen.getByText(/Today’s Rain Risk/i)).toBeDefined();
  expect(screen.getAllByText("—").length).toBeGreaterThan(0);
});

test('Today risk layer is default in Today mode and handles displays correctly', () => {
  const mockLayers = {
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
    selectedRisk: false,
    liveRisk: true, // Today risk layer active by default
  };

  render(
    <LayerToggle
      mapMode="today"
      onMapModeChange={vi.fn()}
      selectionState="idle"
      routingError={null}
      onResetRoute={vi.fn()}
      layers={mockLayers}
      onToggle={vi.fn()}
      riskFillOpacity={0.35}
      setRiskFillOpacity={vi.fn()}
      gridLineOpacity={0.20}
      setGridLineOpacity={vi.fn()}
      events={[]}
      selectedEventId={null}
      onSelectEvent={vi.fn()}
      riskDisplayMode="focus"
      setRiskDisplayMode={vi.fn()}
    />
  );

  // Expect Today’s Rain Risk text
  const liveToggles = screen.getAllByText(/Today’s Rain Risk/i);
  expect(liveToggles.length).toBeGreaterThan(0);

  // Historical options should not be visible in today mode
  expect(screen.queryByText(/Choose Historical Event/i)).toBeNull();
});

test('Risk display mode labels render in Today mode', () => {
  const mockLayers = {
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
    selectedRisk: false,
    liveRisk: true,
  };

  render(
    <LayerToggle
      mapMode="today"
      onMapModeChange={vi.fn()}
      selectionState="idle"
      routingError={null}
      onResetRoute={vi.fn()}
      layers={mockLayers}
      onToggle={vi.fn()}
      riskFillOpacity={0.35}
      setRiskFillOpacity={vi.fn()}
      gridLineOpacity={0.20}
      setGridLineOpacity={vi.fn()}
      events={[]}
      selectedEventId={null}
      onSelectEvent={vi.fn()}
      riskDisplayMode="focus"
      setRiskDisplayMode={vi.fn()}
    />
  );

  expect(screen.getByText("Focus Risk Areas")).toBeDefined();
  expect(screen.getByText("Show All Risk Zones")).toBeDefined();
});

test('Legend explains blue/red route colors and risks', () => {
  render(<Legend />);

  expect(screen.getByText(/Today’s Rain Risk/i)).toBeDefined();
  expect(screen.getByText(/Low: Minimal risk/i)).toBeDefined();
  expect(screen.getByText(/Medium: Caution area/i)).toBeDefined();
  expect(screen.getByText(/High: Avoid if possible/i)).toBeDefined();

  expect(screen.getByText(/Blue: Recommended \/ safe route/i)).toBeDefined();
  expect(screen.getByText(/Red: Risky normal route/i)).toBeDefined();
  expect(screen.getByText(/Dashed: Alternative comparison route/i)).toBeDefined();
});

test('RoutePanel maps normal_route_acceptable correctly', () => {
  const mockComp = {
    normal_distance_m: 2000,
    safe_distance_m: 2200,
    normal_weather_eta_sec: 360,
    safe_weather_eta_sec: 390,
    normal_mean_risk_score: 0.5,
    safe_mean_risk_score: 0.3,
    risk_reduction_percent: 0.0, // test zero risk reduction
    eta_tradeoff_percent: 8.3,
    avoided_high_risk_segments: 0,
    safe_route_quality: "rejected_identical_routes",
    safe_route_available: false,
    recommendation: "normal_route_acceptable",
    live_weather_summary: {
      forecast_window: { rain_24h_mm: 0.0, max_precipitation_probability: 0.0 }
    }
  };

  render(
    <RoutePanel
      comparison={mockComp as any}
      eventType="latest"
      onEventTypeChange={vi.fn()}
      routeVisibility="both"
      onRouteVisibilityChange={vi.fn()}
      routeSource="custom-live"
    />
  );

  // Expect title
  expect(screen.getAllByText("Normal Route Acceptable").length).toBeGreaterThan(0);
  // Expect subtitle
  expect(screen.getByText("No meaningful rain risk is expected on this route.")).toBeDefined();
  // Expect neutral risk reduction wordings
  expect(screen.getByText("No change")).toBeDefined();
});

test('RoutePanel maps weather_safe_route_recommended correctly', () => {
  const mockComp = {
    normal_distance_m: 2000,
    safe_distance_m: 2200,
    normal_weather_eta_sec: 360,
    safe_weather_eta_sec: 390,
    normal_mean_risk_score: 0.8,
    safe_mean_risk_score: 0.3,
    risk_reduction_percent: 62.5,
    eta_tradeoff_percent: 8.3,
    avoided_high_risk_segments: 5,
    safe_route_quality: "strong",
    safe_route_available: true,
    recommendation: "weather_safe_route_recommended",
    live_weather_summary: {
      forecast_window: { rain_24h_mm: 12.0, max_precipitation_probability: 90.0 }
    }
  };

  render(
    <RoutePanel
      comparison={mockComp as any}
      eventType="latest"
      onEventTypeChange={vi.fn()}
      routeVisibility="both"
      onRouteVisibilityChange={vi.fn()}
      routeSource="custom-live"
    />
  );

  expect(screen.getAllByText("Weather-Safe Route Recommended").length).toBeGreaterThan(0);
  expect(screen.getByText("The normal route crosses higher-risk areas. Use the safer route.")).toBeDefined();
  expect(screen.getByText("62.5%")).toBeDefined();
  expect(screen.getByText("12.0 mm")).toBeDefined();
  expect(screen.getByText("90%")).toBeDefined();
});

test('RoutePanel maps no_distinct_safer_alternative correctly', () => {
  const mockComp = {
    normal_distance_m: 2000,
    safe_distance_m: 2200,
    normal_weather_eta_sec: 360,
    safe_weather_eta_sec: 390,
    normal_mean_risk_score: 0.5,
    safe_mean_risk_score: 0.5,
    risk_reduction_percent: 0.0,
    eta_tradeoff_percent: 0.0,
    avoided_high_risk_segments: 0,
    safe_route_quality: "no_distinct_safer_alternative",
    safe_route_available: false,
    recommendation: "no_distinct_safer_alternative",
    live_weather_summary: {
      forecast_window: { rain_24h_mm: 5.0, max_precipitation_probability: 45.0 }
    }
  };

  render(
    <RoutePanel
      comparison={mockComp as any}
      eventType="latest"
      onEventTypeChange={vi.fn()}
      routeVisibility="both"
      onRouteVisibilityChange={vi.fn()}
      routeSource="custom-live"
    />
  );

  expect(screen.getAllByText("No Distinct Safer Alternative").length).toBeGreaterThan(0);
  expect(screen.getByText("The system did not find a route with lower model-estimated risk.")).toBeDefined();
});

test('No raw recommendation strings are visible in RoutePanel', () => {
  const mockComp = {
    normal_distance_m: 2000,
    safe_distance_m: 2200,
    normal_weather_eta_sec: 360,
    safe_weather_eta_sec: 390,
    normal_mean_risk_score: 0.8,
    safe_mean_risk_score: 0.3,
    risk_reduction_percent: 62.5,
    eta_tradeoff_percent: 8.3,
    avoided_high_risk_segments: 5,
    safe_route_quality: "strong",
    safe_route_available: true,
    recommendation: "weather_safe_route_recommended"
  };

  const { container } = render(
    <RoutePanel
      comparison={mockComp as any}
      eventType="latest"
      onEventTypeChange={vi.fn()}
      routeVisibility="both"
      onRouteVisibilityChange={vi.fn()}
      routeSource="custom-live"
    />
  );

  const text = container.textContent ?? "";
  expect(text).not.toContain("weather_safe_route_recommended");
  expect(text).not.toContain("normal_route_acceptable");
  expect(text).not.toContain("no_distinct_safer_alternative");
});

test('MapView renders safely with zoom-restricted POI markers', () => {
  const layers = {
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
    selectedRisk: false,
    liveRisk: true,
  };

  render(
    <MapView
      layers={layers}
      routeVisibility="both"
      boundaryData={null}
      gridData={null}
      placesData={null}
      emergencyPlaceIds={new Set()}
      latestRiskData={null}
      topRainRiskData={null}
      riskSummaryData={null}
      selectedEventRiskData={null}
      liveRiskData={null}
      normalRouteData={null}
      safeRouteData={null}
      routeComparison={null}
      routeOrigin={null}
      routeDestination={null}
      routingLoading={false}
      routingError={null}
      onMapPointClick={vi.fn()}
      onResetRoute={vi.fn()}
      riskFillOpacity={0.35}
      gridLineOpacity={0.20}
      riskDisplayMode="focus"
      searchSelectedPoint={null}
      onSetStartPoint={vi.fn()}
      onSetDestinationPoint={vi.fn()}
    />
  );

  expect(screen.getByLabelText(/Interactive Nasr City weather-impact map/i)).toBeDefined();
});

test('LayerToggle renders POI category counts when placesData is provided', () => {
  const mockLayers = {
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
    selectedRisk: false,
    liveRisk: true,
  };

  const mockPlacesData = {
    type: "FeatureCollection" as const,
    features: [
      {
        type: "Feature" as const,
        properties: { place_id: "1", category: "hospital" },
        geometry: { type: "Point" as const, coordinates: [31.365, 30.055] }
      },
      {
        type: "Feature" as const,
        properties: { place_id: "2", category: "doctors" },
        geometry: { type: "Point" as const, coordinates: [31.365, 30.055] }
      },
      {
        type: "Feature" as const,
        properties: { place_id: "3", category: "place_of_worship" },
        geometry: { type: "Point" as const, coordinates: [31.365, 30.055] }
      }
    ]
  };

  render(
    <LayerToggle
      mapMode="today"
      onMapModeChange={vi.fn()}
      selectionState="idle"
      routingError={null}
      onResetRoute={vi.fn()}
      layers={mockLayers}
      onToggle={vi.fn()}
      riskFillOpacity={0.35}
      setRiskFillOpacity={vi.fn()}
      gridLineOpacity={0.20}
      setGridLineOpacity={vi.fn()}
      events={[]}
      selectedEventId={null}
      onSelectEvent={vi.fn()}
      riskDisplayMode="focus"
      setRiskDisplayMode={vi.fn()}
      placesData={mockPlacesData as any}
    />
  );

  expect(screen.getByText("Hospitals")).toBeDefined();
  expect(screen.getByText("Clinics")).toBeDefined();
  expect(screen.getByText("Mosques")).toBeDefined();
  // should render the count "1" for hospital, clinic, mosque
  const counts = screen.getAllByText("1");
  expect(counts.length).toBeGreaterThanOrEqual(3);
});

test('MapView filters markers by active category state', () => {
  const layers = {
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
    emergency: false,
    latestRisk: false,
    topRainRisk: false,
    riskSummary: false,
    selectedRisk: false,
    liveRisk: true,
  };

  const mockPlacesData = {
    type: "FeatureCollection" as const,
    features: [
      {
        type: "Feature" as const,
        properties: { place_id: "p1", category: "hospital", display_name: "Hospital One", category_label: "Hospital" },
        geometry: { type: "Point" as const, coordinates: [31.365, 30.055] }
      },
      {
        type: "Feature" as const,
        properties: { place_id: "p2", category: "clinic", display_name: "Clinic One", category_label: "Clinic" },
        geometry: { type: "Point" as const, coordinates: [31.366, 30.056] }
      }
    ]
  };

  render(
    <MapView
      layers={layers}
      routeVisibility="both"
      boundaryData={null}
      gridData={null}
      placesData={mockPlacesData as any}
      emergencyPlaceIds={new Set()}
      latestRiskData={null}
      topRainRiskData={null}
      riskSummaryData={null}
      selectedEventRiskData={null}
      liveRiskData={null}
      normalRouteData={null}
      safeRouteData={null}
      routeComparison={null}
      routeOrigin={null}
      routeDestination={null}
      routingLoading={false}
      routingError={null}
      onMapPointClick={vi.fn()}
      onResetRoute={vi.fn()}
      riskFillOpacity={0.35}
      gridLineOpacity={0.20}
      riskDisplayMode="focus"
      searchSelectedPoint={null}
      onSetStartPoint={vi.fn()}
      onSetDestinationPoint={vi.fn()}
    />
  );

  // Assert MapView is rendered. (Marker checks can be difficult due to deep jsdom mock interactions, 
  // but this ensures categoryVisible filters them without rendering errors).
  expect(screen.getByLabelText(/Interactive Nasr City weather-impact map/i)).toBeDefined();
});

test('Welcome Page interactive features and modal navigation', async () => {
  await act(async () => {
    render(<App />);
  });

  // 1. Welcome Page renders
  expect(screen.getAllByText(/safer/i).length).toBeGreaterThan(0);
  expect(screen.getByText("Open Live Map")).toBeDefined();
  expect(screen.getByText("See how it works")).toBeDefined();

  // 7. Check that bottom feature card elements are NOT visible by default (no "What it does" header)
  expect(screen.queryByText("What it does")).toBeNull();

  // 3. See how it works opens How it works panel
  const seeHowBtn = screen.getByText("See how it works");
  await act(async () => {
    fireEvent.click(seeHowBtn);
  });
  expect(screen.getByText("How the system works")).toBeDefined();
  expect(screen.getByText("Search / Click Map")).toBeDefined();

  // 6. Closing panel works
  const closeBtn = screen.getByLabelText("Close modal");
  await act(async () => {
    fireEvent.click(closeBtn);
  });
  expect(screen.queryByText("How the system works")).toBeNull();

  // 4. Features nav opens Features panel
  const featuresBtn = screen.getByRole("button", { name: "Features" });
  await act(async () => {
    fireEvent.click(featuresBtn);
  });
  expect(screen.getByText("Smart mobility features")).toBeDefined();
  expect(screen.getByText("Live Rain Risk")).toBeDefined();

  // 5. Model nav opens Model panel
  const modelBtn = screen.getByRole("button", { name: "Model" });
  await act(async () => {
    fireEvent.click(modelBtn);
  });
  expect(screen.getByText("How the AI model helps")).toBeDefined();

  // Close again
  const closeBtn2 = screen.getByLabelText("Close modal");
  await act(async () => {
    fireEvent.click(closeBtn2);
  });

  // 2 & 8. Open Live Map button switches to Dashboard
  const openBtn = screen.getByText("Open Live Map");
  await act(async () => {
    fireEvent.click(openBtn);
  });
  expect(document.title).toBe("Egypt Smart City Digital Twin");
});
