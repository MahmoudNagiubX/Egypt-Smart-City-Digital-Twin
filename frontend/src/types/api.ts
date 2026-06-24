// API types for the Nasr City Weather Impact Dashboard

export interface GeoJsonFeature<Properties = Record<string, unknown>> {
  type: "Feature";
  properties: Properties;
  geometry: {
    type: string;
    coordinates: unknown;
  };
}

export interface FeatureCollection<Properties = Record<string, unknown>> {
  type: "FeatureCollection";
  features: Array<GeoJsonFeature<Properties>>;
}

export type PlaceCategory =
  | "all"
  | "hospital"
  | "clinic"
  | "mosque"
  | "mall"
  | "school"
  | "university"
  | "police"
  | "fire_station"
  | "emergency"
  | "landmark";

export interface PlaceProperties {
  place_id: string;
  name?: string | null;
  display_name: string;
  category: Exclude<PlaceCategory, "all">;
  category_label: string;
  icon_type: string;
  source: string;
  lon: number;
  lat: number;
}

export interface RouteCoordinate {
  lat: number;
  lon: number;
}

export interface HealthResponse {
  status: string;
  module_name: string;
  outputs_available: Record<string, boolean>;
  prediction_report_status?: string;
  official_flood_labels_claimed: boolean;
  demo_scenarios_used_for_training: boolean;
}

export interface SummaryResponse {
  zone_count: number;
  event_count: number;
  prediction_row_count: number;
  risk_class_counts: {
    low: number;
    medium: number;
    high: number;
  };
  highest_risk_zones: Array<{
    zone_code: string;
    max_predicted_score: number;
    dominant_risk_class: string;
  }>;
  top_rain_event_id: string;
  latest_event_id: string;
  model_name: string;
  dataset_name: string;
  honesty_statement: string;
}

export interface PredictionMetadata {
  model_name: string;
  model_type: string;
  features_used: string[];
  split_strategy: string;
  rf_metrics: {
    mae: number;
    rmse: number;
    r2: number;
    severity_accuracy: number;
  };
  dataset_rows: number;
  events_count: number;
}

export interface EventSummary {
  event_id: string;
  timestamp: string;
  mean_rain_24h_mm: number;
  max_rain_24h_mm: number;
  mean_predicted_score: number;
  high_risk_zone_count: number;
}

export interface RouteComparison {
  event_type?: string;
  event_id?: string;
  timestamp?: string;
  normal_distance_m: number;
  safe_distance_m: number;
  normal_base_eta_sec?: number;
  safe_base_eta_sec?: number;
  normal_weather_eta_sec: number;
  safe_weather_eta_sec: number;
  normal_mean_risk_score: number;
  safe_mean_risk_score: number;
  normal_high_risk_segment_count?: number;
  safe_high_risk_segment_count?: number;
  risk_reduction_percent: number;
  eta_tradeoff_percent: number;
  avoided_high_risk_segments: number;
  safe_route_quality: string;
  safe_route_available: boolean;
  quality_guard_passed?: boolean;
  selected_origin_zone_code?: string;
  selected_destination_facility_name?: string;
  honesty_note: string;
}

export interface CustomRouteRequest {
  origin: RouteCoordinate;
  destination: RouteCoordinate;
  event_type: "top-rain" | "latest";
  route_preference: "both";
}

export interface CustomRouteResponse {
  status: "ok" | "ok_with_warnings";
  event_type: "top-rain" | "latest";
  origin: RouteCoordinate & { nearest_node: string | number; snap_distance_m: number };
  destination: RouteCoordinate & { nearest_node: string | number; snap_distance_m: number };
  normal_route: FeatureCollection;
  weather_safe_route: FeatureCollection;
  comparison: RouteComparison;
  warnings?: string[];
  honesty_note: string;
}

export interface LayerToggles {
  boundary: boolean;
  grid: boolean;
  roadsLabels: boolean;
  hospitals: boolean;
  clinics: boolean;
  mosques: boolean;
  malls: boolean;
  schools: boolean;
  universities: boolean;
  police: boolean;
  fireStations: boolean;
  emergency: boolean;
  latestRisk: boolean;
  topRainRisk: boolean;
  riskSummary: boolean;
  selectedRisk: boolean;
  liveRisk: boolean;
}

export interface LiveWeatherSummary {
  status: string;
  source: string;
  location: {
    name: string;
    lat: number;
    lon: number;
  };
  current: {
    time: string;
    temperature_2m: number;
    apparent_temperature?: number;
    relative_humidity_2m?: number;
    rain: number;
    precipitation: number;
    wind_speed_10m: number;
    weather_code: number;
  };
  forecast_window: {
    hours: number;
    rain_1h_mm: number;
    rain_3h_mm: number;
    rain_6h_mm: number;
    rain_24h_mm: number;
    max_precipitation_probability: number;
    mean_temperature_2m?: number;
    mean_relative_humidity_2m?: number;
    mean_apparent_temperature?: number;
    mean_wind_speed_10m?: number;
  };
  rain_risk_expected: boolean;
  recommended_event_mode: "live" | "normal";
  warnings: string[];
}

export interface LiveRoutingStatusResponse {
  status: "ok" | "ok_with_warnings" | "failed";
  live_weather_available: boolean;
  live_risk_layer_available: boolean;
  live_report_status: string;
  rain_risk_expected: boolean;
  risk_class_counts: {
    low: number;
    medium: number;
    high: number;
  };
  recommended_mode: "normal_route_acceptable" | "weather_safe_routing_available";
  warnings: string[];
  honesty_note: string;
}

export interface LiveEmergencyRouteRequest {
  origin: RouteCoordinate;
  destination: RouteCoordinate;
  route_preference: "both";
  refresh_live_weather?: boolean;
}

export interface LiveRouteComparison {
  safe_route_available: boolean;
  safe_route_quality: string;
  risk_reduction_percent: number;
  eta_tradeoff_percent: number;
  avoided_high_risk_segments: number;
  normal_distance_m: number;
  safe_distance_m: number;
  normal_weather_eta_sec: number;
  safe_weather_eta_sec: number;
  normal_mean_live_risk_score: number;
  safe_mean_live_risk_score: number;
  live_high_risk_segment_count_normal: number;
  live_high_risk_segment_count_safe: number;
  honesty_note: string;
}

export interface LiveEmergencyRouteResponse {
  status: "ok" | "ok_with_warnings";
  mode: "live_weather";
  rain_risk_expected: boolean;
  recommendation: "normal_route_acceptable" | "weather_safe_route_recommended" | "no_distinct_safer_alternative";
  origin: RouteCoordinate & { nearest_node: string | number; snap_distance_m: number };
  destination: RouteCoordinate & { nearest_node: string | number; snap_distance_m: number };
  normal_route: FeatureCollection;
  weather_safe_route: FeatureCollection;
  comparison: LiveRouteComparison;
  live_weather_summary: {
    rain_1h_mm: number;
    rain_3h_mm: number;
    rain_6h_mm: number;
    rain_24h_mm: number;
    max_precipitation_probability: number;
  };
  honesty_note: string;
}

export type RouteMode = "demo" | "custom-live";

