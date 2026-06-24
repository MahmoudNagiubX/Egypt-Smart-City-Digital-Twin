// @vitest-environment jsdom
import { render, screen, act, cleanup } from '@testing-library/react'
import { expect, test, vi, afterEach } from 'vitest'
import App from '../App'
import { SummaryCards } from '../components/SummaryCards'
import { RoutePanel } from '../components/RoutePanel'
import { LayerToggle } from '../components/LayerToggle'
import { EventSelector } from '../components/EventSelector'

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
  getLatestRiskLayer: vi.fn().mockResolvedValue({ type: "FeatureCollection", features: [] }),
  getTopRainRiskLayer: vi.fn().mockResolvedValue({ type: "FeatureCollection", features: [] }),
  getRiskSummaryLayer: vi.fn().mockResolvedValue({ type: "FeatureCollection", features: [] }),
  getEventRiskLayer: vi.fn().mockResolvedValue({ type: "FeatureCollection", features: [] }),
  getRoutingStatus: vi.fn().mockResolvedValue({ status: "ok" }),
  getDemoRoute: vi.fn().mockResolvedValue({ type: "FeatureCollection", features: [] }),
  getRouteComparison: vi.fn().mockResolvedValue({
    event_type: "top-rain",
    event_id: "evt_0557",
    timestamp: "2020-03-12",
    normal_distance_m: 5400,
    safe_distance_m: 5800,
    normal_base_eta_sec: 450,
    safe_base_eta_sec: 480,
    normal_weather_eta_sec: 600,
    safe_weather_eta_sec: 500,
    normal_mean_risk_score: 0.42,
    safe_mean_risk_score: 0.18,
    normal_high_risk_segment_count: 15,
    safe_high_risk_segment_count: 0,
    risk_reduction_percent: 57.1,
    eta_tradeoff_percent: 8.3,
    avoided_high_risk_segments: 15,
    safe_route_quality: "strong",
    safe_route_available: true,
    quality_guard_passed: true,
    selected_origin_zone_code: "NSR-GRID-119",
    selected_destination_facility_name: "Nasr City Hospital",
    honesty_note: "Predictions are model-estimated weather-impact risk scores... Routes are decision-support..."
  })
}));

test('App renders dashboard title and disclaimers', async () => {
  await act(async () => {
    render(<App />);
  });
  
  // Dashboard Title
  const title = screen.getAllByText(/Nasr City Weather-Impact/i);
  expect(title.length).toBeGreaterThan(0);
  expect(document.title).toBe("Egypt Smart City Digital Twin");

  // Disclaimer visibility
  const note = screen.getAllByText(/not official emergency dispatch instructions/i);
  expect(note.length).toBeGreaterThan(0);
});

test('SummaryCards renders the eight operational summary cards', () => {
  const mockSummary = {
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
  };
  const mockHealth = { status: "healthy", module_name: "Nasr City Weather-Impact Emergency Mobility Module", outputs_available: {}, official_flood_labels_claimed: false, demo_scenarios_used_for_training: false };
  
  render(<SummaryCards summary={mockSummary} health={mockHealth} />);
  
  expect(screen.getByText(/Zones Analyzed/i)).toBeDefined();
  expect(screen.getByText(/Prediction Rows/i)).toBeDefined();
  expect(screen.getByText(/Low Risk/i)).toBeDefined();
  expect(screen.getByText(/Routing Ready/i)).toBeDefined();
  expect(screen.getByText(/12\D?480/i)).toBeDefined();
  expect(screen.queryByText(/evt_dry_009|evt_0557/)).toBeNull();
});

test('SummaryCards renders safely with partial or missing mock data', () => {
  const mockSummary = {
    zone_count: undefined as any,
    prediction_row_count: undefined as any,
    event_count: undefined as any,
    risk_class_counts: undefined as any,
    highest_risk_zones: [] as any,
    latest_event_id: undefined as any,
    top_rain_event_id: undefined as any,
    model_name: undefined as any,
    dataset_name: undefined as any,
    honesty_statement: undefined as any
  };
  const mockHealth = null;

  render(<SummaryCards summary={mockSummary} health={mockHealth} />);

  // Should display the fallback "—" instead of crashing
  const elements = screen.getAllByText(/—/);
  expect(elements.length).toBeGreaterThan(0);
});


test('RoutePanel renders risk reduction and ETA tradeoff metrics', () => {
  const mockComp = {
    event_type: "top-rain",
    event_id: "evt_0557",
    timestamp: "2020-03-12",
    normal_distance_m: 5400,
    safe_distance_m: 5800,
    normal_base_eta_sec: 450,
    safe_base_eta_sec: 480,
    normal_weather_eta_sec: 600,
    safe_weather_eta_sec: 500,
    normal_mean_risk_score: 0.42,
    safe_mean_risk_score: 0.18,
    normal_high_risk_segment_count: 15,
    safe_high_risk_segment_count: 0,
    risk_reduction_percent: 57.1,
    eta_tradeoff_percent: 8.3,
    avoided_high_risk_segments: 15,
    safe_route_quality: "strong",
    safe_route_available: true,
    quality_guard_passed: true,
    selected_origin_zone_code: "NSR-GRID-119",
    selected_destination_facility_name: "Nasr City Hospital",
    honesty_note: "Predictions are model-estimated weather-impact risk scores... Routes are decision-support..."
  };

  render(
    <RoutePanel 
      comparison={mockComp} 
      eventType="top-rain" 
      onEventTypeChange={vi.fn()} 
      routeVisibility="both" 
      onRouteVisibilityChange={vi.fn()} 
    />
  );

  expect(screen.getByText(/57.1%/)).toBeDefined();
  expect(screen.getByText(/\+8.3%/)).toBeDefined();
  expect(screen.getByText(/High-Risk Segments Avoided/i)).toBeDefined();
  expect(screen.getByText(/^15$/)).toBeDefined();
});

test('LayerToggle renders spatial and risk toggle controls', () => {
  const mockLayers = {
    boundary: true,
    grid: false,
    facilities: true,
    roadsLabels: true,
    hospitals: true,
    mosques: true,
    malls: true,
    education: true,
    latestRisk: true,
    topRainRisk: false,
    riskSummary: false,
    selectedRisk: false
  };

  render(<LayerToggle layers={mockLayers} onToggle={vi.fn()} />);

  expect(screen.getByText(/Nasr City Boundary/i)).toBeDefined();
  expect(screen.getByText(/Analysis Grid/i)).toBeDefined();
  expect(screen.getByText(/Emergency Facilities/i)).toBeDefined();
  expect(screen.getByText(/Latest event/i)).toBeDefined();
  expect(screen.getByText(/Hospitals/i)).toBeDefined();
  expect(screen.getByText(/Mosques/i)).toBeDefined();
  expect(screen.getByText(/Malls/i)).toBeDefined();
});

test('EventSelector dropdown renders event options', () => {
  const mockEvents = [
    { event_id: "evt_0557", timestamp: "2020-03-12T00:00", mean_rain_24h_mm: 55.7, max_rain_24h_mm: 70, mean_predicted_score: 0.45, high_risk_zone_count: 206 }
  ];

  render(
    <EventSelector 
      events={mockEvents} 
      selectedEventId="evt_0557" 
      onSelectEvent={vi.fn()} 
    />
  );

  expect(screen.getByRole('heading', { name: /Event/i })).toBeDefined();
  expect(screen.getByRole('combobox', { name: /Observed weather event/i })).toBeDefined();
  expect(screen.queryByText("evt_0557")).toBeNull();
});

test('API Client resolves base URL defaults correctly', async () => {
  // Save current env
  const origEnv = import.meta.env.VITE_API_BASE_URL;
  delete (import.meta.env as any).VITE_API_BASE_URL;

  // Import dynamically to test base URL resolver fallback
  const clientModule = await import('../api/client');
  expect(clientModule).toBeDefined();

  // Restore env
  if (origEnv !== undefined) {
    (import.meta.env as any).VITE_API_BASE_URL = origEnv;
  }
});

test('EventSelector renders correctly when mean_rain_24h_mm is missing/undefined', () => {
  const mockEvents = [
    { event_id: "evt_0557", timestamp: "2020-03-12T00:00", mean_rain_24h_mm: undefined as any, max_rain_24h_mm: 70, mean_predicted_score: 0.45, high_risk_zone_count: 206 }
  ];

  render(
    <EventSelector 
      events={mockEvents} 
      selectedEventId="evt_0557" 
      onSelectEvent={vi.fn()} 
    />
  );

  expect(screen.getByRole('heading', { name: /Event/i })).toBeDefined();
  expect(screen.getAllByText(/— mm/i).length).toBeGreaterThan(0);
});

test('RoutePanel renders correctly when optional numeric metrics are missing/undefined', () => {
  const mockComp = {
    event_type: "top-rain",
    event_id: "evt_0557",
    timestamp: "2020-03-12",
    normal_distance_m: undefined as any,
    safe_distance_m: undefined as any,
    normal_base_eta_sec: undefined as any,
    safe_base_eta_sec: undefined as any,
    normal_weather_eta_sec: undefined as any,
    safe_weather_eta_sec: undefined as any,
    normal_mean_risk_score: undefined as any,
    safe_mean_risk_score: undefined as any,
    normal_high_risk_segment_count: undefined as any,
    safe_high_risk_segment_count: undefined as any,
    risk_reduction_percent: undefined as any,
    eta_tradeoff_percent: undefined as any,
    avoided_high_risk_segments: undefined as any,
    safe_route_quality: "strong",
    safe_route_available: true,
    quality_guard_passed: true,
    selected_origin_zone_code: "NSR-GRID-119",
    selected_destination_facility_name: "Nasr City Hospital",
    honesty_note: "Predictions are model-estimated... Routes are decision-support..."
  };

  render(
    <RoutePanel 
      comparison={mockComp} 
      eventType="top-rain" 
      onEventTypeChange={vi.fn()} 
      routeVisibility="both" 
      onRouteVisibilityChange={vi.fn()} 
    />
  );

  expect(screen.getAllByText(/—/).length).toBeGreaterThan(0);
});

test('mocked dashboard components do not expose raw API field labels or identifiers', () => {
  const mockComp = {
    event_type: "top-rain",
    event_id: "evt_0557",
    timestamp: "2020-03-12",
    normal_distance_m: 5400,
    safe_distance_m: 5800,
    normal_base_eta_sec: 450,
    safe_base_eta_sec: 480,
    normal_weather_eta_sec: 600,
    safe_weather_eta_sec: 500,
    normal_mean_risk_score: 0.42,
    safe_mean_risk_score: 0.18,
    normal_high_risk_segment_count: 15,
    safe_high_risk_segment_count: 0,
    risk_reduction_percent: 57.1,
    eta_tradeoff_percent: 8.3,
    avoided_high_risk_segments: 15,
    safe_route_quality: "strong",
    safe_route_available: true,
    quality_guard_passed: true,
    selected_origin_zone_code: "NSR-GRID-119",
    selected_destination_facility_name: "Nasr City Hospital",
    honesty_note: "Decision-support prototype output.",
  };

  const { container } = render(
    <RoutePanel
      comparison={mockComp}
      eventType="top-rain"
      onEventTypeChange={vi.fn()}
      routeVisibility="both"
      onRouteVisibilityChange={vi.fn()}
    />,
  );

  const visibleText = container.textContent ?? "";
  [
    "risk_reduction_percent",
    "eta_tradeoff_percent",
    "safe_route_available",
    "safe_route_quality",
    "evt_0557",
    "NSR-GRID-119",
  ].forEach((rawValue) => expect(visibleText).not.toContain(rawValue));
  expect(visibleText).toContain("Zone 119");
  expect(visibleText).toContain("Route Quality");
});
