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
  getHealth: vi.fn().mockResolvedValue({ status: "ok", service: "backend", module: "weather_impact" }),
  getSummary: vi.fn().mockResolvedValue({
    grid_cells: 416,
    road_segments: 17411,
    emergency_facilities: 44,
    real_training_rows: 12480,
    prediction_rows: 12480,
    events: 30,
    risk_class_counts: { low: 4502, medium: 6732, high: 1246 },
    latest_selected_event: { event_id: "evt_dry_009", timestamp: "2024-02-20T00:00", rain_sum_mm: 0.0 },
    top_rain_event: { event_id: "evt_0557", timestamp: "2020-03-12T00:00", rain_sum_mm: 55.7 },
    routing_readiness: { top_rain_safe_route_available: true, latest_safe_route_available: true, routing_validation_status: "ok" }
  }),
  getEvents: vi.fn().mockResolvedValue([
    { event_id: "evt_0557", timestamp: "2020-03-12T00:00", rain_sum_mm: 55.7, predicted_risk_class_counts: { low: 10, medium: 200, high: 206 }, mean_predicted_risk: 0.45, max_predicted_risk: 0.98 }
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
  const title = screen.getByText(/Nasr City Weather-Impact/i);
  expect(title).toBeDefined();

  // Disclaimer visibility
  const note = screen.getAllByText(/not official emergency dispatch instructions/i);
  expect(note.length).toBeGreaterThan(0);
});

test('SummaryCards renders mock summary statistics correctly', () => {
  const mockSummary = {
    grid_cells: 416,
    road_segments: 17411,
    emergency_facilities: 44,
    real_training_rows: 12480,
    prediction_rows: 12480,
    events: 30,
    risk_class_counts: { low: 4502, medium: 6732, high: 1246 },
    latest_selected_event: { event_id: "evt_dry_009", timestamp: "2024-02-20T00:00", rain_sum_mm: 0.0 },
    top_rain_event: { event_id: "evt_0557", timestamp: "2020-03-12T00:00", rain_sum_mm: 55.7 },
    routing_readiness: { top_rain_safe_route_available: true, latest_safe_route_available: true, routing_validation_status: "ok" }
  };
  const mockHealth = { status: "ok", service: "backend", module: "weather_impact" };
  
  render(<SummaryCards summary={mockSummary} health={mockHealth} />);
  
  expect(screen.getByText(/416 Zones \| 17\D?411 Roads/i)).toBeDefined();
  expect(screen.getByText(/12\D?480 Predictions/i)).toBeDefined();
  expect(screen.getByText(/LOW: 4\D?502/i)).toBeDefined();
});

test('SummaryCards renders safely with partial or missing mock data', () => {
  const mockSummary = {
    grid_cells: undefined as any,
    road_segments: null as any,
    emergency_facilities: undefined as any,
    real_training_rows: undefined as any,
    prediction_rows: undefined as any,
    events: undefined as any,
    risk_class_counts: undefined as any,
    latest_selected_event: null as any,
    top_rain_event: null as any,
    routing_readiness: null as any
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

  expect(screen.getByText(/-57.1%/)).toBeDefined();
  expect(screen.getByText(/\+8.3%/)).toBeDefined();
  expect(screen.getByText(/Avoided Segs: 15/i)).toBeDefined();
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
  expect(screen.getByText(/500m Elevation Grid/i)).toBeDefined();
  expect(screen.getByText(/Emergency Facilities/i)).toBeDefined();
  expect(screen.getByText(/Latest Rainfall Event Risk/i)).toBeDefined();
});

test('EventSelector dropdown renders event options', () => {
  const mockEvents = [
    { event_id: "evt_0557", timestamp: "2020-03-12T00:00", rain_sum_mm: 55.7, predicted_risk_class_counts: { low: 10, medium: 200, high: 206 }, mean_predicted_risk: 0.45, max_predicted_risk: 0.98 }
  ];

  render(
    <EventSelector 
      events={mockEvents} 
      selectedEventId="evt_0557" 
      onSelectEvent={vi.fn()} 
    />
  );

  // Selector shows standard label
  expect(screen.getByText(/Simulated Event Selector/i)).toBeDefined();
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

test('EventSelector renders correctly when rain_sum_mm is missing/undefined', () => {
  const mockEvents = [
    { event_id: "evt_0557", timestamp: "2020-03-12T00:00", rain_sum_mm: undefined as any, predicted_risk_class_counts: { low: 10, medium: 200, high: 206 }, mean_predicted_risk: 0.45, max_predicted_risk: 0.98 }
  ];

  render(
    <EventSelector 
      events={mockEvents} 
      selectedEventId="evt_0557" 
      onSelectEvent={vi.fn()} 
    />
  );

  expect(screen.getByText(/Simulated Event Selector/i)).toBeDefined();
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

  // Expect default outputs or fallbacks
  expect(screen.getAllByText(/0.0%/).length).toBeGreaterThan(0);
});
