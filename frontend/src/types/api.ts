// API types for the Nasr City Weather Impact Dashboard

export interface FeatureCollection {
  type: "FeatureCollection";
  features: any[];
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
