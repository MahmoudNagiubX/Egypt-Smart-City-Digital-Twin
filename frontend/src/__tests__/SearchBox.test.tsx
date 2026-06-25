// @vitest-environment jsdom
import { render, screen, fireEvent, act, cleanup } from '@testing-library/react'
import { expect, test, vi, afterEach } from 'vitest'
import { SearchBox } from '../components/SearchBox'
import { Dashboard } from '../components/Dashboard'
import * as client from '../api/client'

// Mock client.searchLocalPlaces
vi.mock('../api/client', async (importOriginal) => {
  const actual = await importOriginal() as any;
  return {
    ...actual,
    searchLocalPlaces: vi.fn().mockResolvedValue({
      status: "ok",
      query: "hospital",
      results: [
        {
          id: "place-1",
          name: "Nasr City Hospital",
          display_name: "Nasr City Hospital",
          category: "hospital",
          category_label: "Hospital",
          source: "OpenStreetMap",
          lat: 30.06,
          lon: 31.33,
          confidence: 1.0,
          inside_project_area: true,
          geometry_type: "Point"
        }
      ],
      warnings: []
    })
  };
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
    flyTo() {}
  }
  
  class PopupMock {
    setLngLat() { return this; }
    setHTML() { return this; }
    addTo() {}
    remove() {}
  }

  return {
    default: {
      Map: MapMock,
      NavigationControl: function() {},
      ScaleControl: function() {},
      Popup: PopupMock
    },
    Map: MapMock,
    NavigationControl: function() {},
    ScaleControl: function() {},
    Popup: PopupMock
  };
});

afterEach(() => {
  cleanup();
});

test("SearchBox renders correctly", () => {
  const onSelectResult = vi.fn();
  const onSetStart = vi.fn();
  const onSetDestination = vi.fn();
  const onClear = vi.fn();

  render(
    <SearchBox
      onSelectResult={onSelectResult}
      selectedResult={null}
      onSetStart={onSetStart}
      onSetDestination={onSetDestination}
      onClear={onClear}
    />
  );

  expect(screen.getByPlaceholderText(/Search street, place, hospital/i)).toBeDefined();
});

test("typing query calls search API and renders results", async () => {
  const onSelectResult = vi.fn();
  const onSetStart = vi.fn();
  const onSetDestination = vi.fn();
  const onClear = vi.fn();

  render(
    <SearchBox
      onSelectResult={onSelectResult}
      selectedResult={null}
      onSetStart={onSetStart}
      onSetDestination={onSetDestination}
      onClear={onClear}
    />
  );

  const input = screen.getByPlaceholderText(/Search street, place, hospital/i) as HTMLInputElement;
  
  await act(async () => {
    fireEvent.change(input, { target: { value: "hospital" } });
  });

  // Wait for debounce timer (300ms)
  await act(async () => {
    await new Promise((resolve) => setTimeout(resolve, 310));
  });

  expect(client.searchLocalPlaces).toHaveBeenCalledWith("hospital");
  
  const resultItem = await screen.findByText("Nasr City Hospital");
  expect(resultItem).toBeDefined();
  
  const categoryLabel = screen.getByText(/Hospital\s+•\s+OpenStreetMap/i);
  expect(categoryLabel).toBeDefined();
});

test("selectedResult shows action panel with start/destination buttons", () => {
  const onSelectResult = vi.fn();
  const onSetStart = vi.fn();
  const onSetDestination = vi.fn();
  const onClear = vi.fn();

  const selectedResult = {
    id: "place-1",
    name: "Nasr City Hospital",
    display_name: "Nasr City Hospital",
    category: "hospital",
    category_label: "Hospital",
    source: "OpenStreetMap",
    lat: 30.06,
    lon: 31.33,
    confidence: 1.0,
    inside_project_area: true,
    geometry_type: "Point" as const
  };

  render(
    <SearchBox
      onSelectResult={onSelectResult}
      selectedResult={selectedResult}
      onSetStart={onSetStart}
      onSetDestination={onSetDestination}
      onClear={onClear}
    />
  );

  expect(screen.getByText("Nasr City Hospital")).toBeDefined();
  
  const startBtn = screen.getByRole("button", { name: /Set Start/i });
  const destBtn = screen.getByRole("button", { name: /Set Destination/i });
  expect(startBtn).toBeDefined();
  expect(destBtn).toBeDefined();

  fireEvent.click(startBtn);
  expect(onSetStart).toHaveBeenCalled();

  fireEvent.click(destBtn);
  expect(onSetDestination).toHaveBeenCalled();
});

test("Dashboard renders with SearchBox without crashing", async () => {
  // Mock necessary dashboard APIs
  vi.spyOn(client, 'getHealth').mockResolvedValue({ status: "healthy", module_name: "Nasr City Weather-Impact Emergency Mobility Module", outputs_available: {}, official_flood_labels_claimed: false, demo_scenarios_used_for_training: false });
  vi.spyOn(client, 'getSummary').mockResolvedValue({
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
  });
  vi.spyOn(client, 'getEvents').mockResolvedValue([
    { event_id: "evt_0557", timestamp: "2020-03-12T00:00", mean_rain_24h_mm: 55.7, max_rain_24h_mm: 70, mean_predicted_score: 0.45, high_risk_zone_count: 206 }
  ]);
  vi.spyOn(client, 'getBoundaryLayer').mockResolvedValue({ type: "FeatureCollection", features: [] });
  vi.spyOn(client, 'getGridLayer').mockResolvedValue({ type: "FeatureCollection", features: [] });
  vi.spyOn(client, 'getEmergencyFacilities').mockResolvedValue({ type: "FeatureCollection", features: [] });
  vi.spyOn(client, 'getPlaces').mockResolvedValue({ type: "FeatureCollection", features: [] });
  vi.spyOn(client, 'getLatestRiskLayer').mockResolvedValue({ type: "FeatureCollection", features: [] });
  vi.spyOn(client, 'getTopRainRiskLayer').mockResolvedValue({ type: "FeatureCollection", features: [] });
  vi.spyOn(client, 'getRiskSummaryLayer').mockResolvedValue({ type: "FeatureCollection", features: [] });

  await act(async () => {
    render(<Dashboard />);
  });
  
  const h1 = screen.getByText("Egypt Smart City Digital Twin");
  expect(h1).toBeDefined();
});
