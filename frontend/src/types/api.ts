// API types for the Nasr City Weather Impact Dashboard

export interface FeatureCollection {
  type: "FeatureCollection";
  features: any[];
}

export interface HealthResponse {
  status: string;
  service: string;
  module: string;
  files?: {
    required_files_checked: number;
    missing_files: string[];
  };
  database?: string;
  model_status?: string;
  routing_status?: string;
}

export interface SummaryResponse {
  grid_cells: number;
  road_segments: number;
  emergency_facilities: number;
  real_training_rows: number;
  prediction_rows: number;
  events: number;
  risk_class_counts: {
    low: number;
    medium: number;
    high: number;
  };
  latest_selected_event: {
    event_id: string;
    timestamp: string;
    rain_sum_mm: number;
  };
  top_rain_event: {
    event_id: string;
    timestamp: string;
    rain_sum_mm: number;
  };
  routing_readiness: {
    top_rain_safe_route_available: boolean;
    latest_safe_route_available: boolean;
    routing_validation_status: string;
  };
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
  rain_sum_mm: number;
  predicted_risk_class_counts: {
    low: number;
    medium: number;
    high: number;
  };
  mean_predicted_risk: number;
  max_predicted_risk: number;
}

export interface RouteComparison {
  event_type: string;
  event_id: string;
  timestamp: string;
  normal_distance_m: number;
  safe_distance_m: number;
  normal_base_eta_sec: number;
  safe_base_eta_sec: number;
  normal_weather_eta_sec: number;
  safe_weather_eta_sec: number;
  normal_mean_risk_score: number;
  safe_mean_risk_score: number;
  normal_high_risk_segment_count: number;
  safe_high_risk_segment_count: number;
  risk_reduction_percent: number;
  eta_tradeoff_percent: number;
  avoided_high_risk_segments: number;
  safe_route_quality: string;
  safe_route_available: boolean;
  quality_guard_passed: boolean;
  selected_origin_zone_code?: string;
  selected_destination_facility_name?: string;
  honesty_note: string;
}

export interface LayerToggles {
  boundary: boolean;
  grid: boolean;
  facilities: boolean;
  roadsLabels: boolean;
  hospitals: boolean;
  mosques: boolean;
  malls: boolean;
  education: boolean;
  latestRisk: boolean;
  topRainRisk: boolean;
  riskSummary: boolean;
  selectedRisk: boolean;
}
