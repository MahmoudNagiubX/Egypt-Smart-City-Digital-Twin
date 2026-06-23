"""Pydantic schemas for request/response validation."""

from pydantic import BaseModel
from typing import Dict, List, Optional


class ModuleStatusResponse(BaseModel):
    module_name: str
    status: str
    outputs_available: Dict[str, bool]
    prediction_report_status: Optional[str] = None
    official_flood_labels_claimed: bool = False
    demo_scenarios_used_for_training: bool = False


class PredictionMetadataResponse(BaseModel):
    model_used: str
    dataset_used: str
    prediction_rows: int
    zone_count: int
    event_count: int
    risk_class_counts: Dict[str, int]
    latest_event_id: str
    latest_event_timestamp: str
    top_rain_event_id: str
    official_flood_labels_claimed: bool = False
    demo_scenarios_used_for_training: bool = False
    status: str


class EventSummary(BaseModel):
    event_id: str
    timestamp: str
    mean_rain_24h_mm: float
    max_rain_24h_mm: float
    mean_predicted_score: float
    high_risk_zone_count: int


class RoutingStatusResponse(BaseModel):
    status: str
    warnings: List[str]
    graph_loaded: bool
    road_risk_weights_top_rain_exists: bool
    road_risk_weights_latest_exists: bool
    top_rain_routes_created: bool
    latest_routes_created: bool
    top_rain_comparison_exists: bool
    latest_comparison_exists: bool
    official_emergency_dispatch_claimed: bool = False
    official_flood_labels_claimed: bool = False
    honesty_note: str


class RouteComparisonResponse(BaseModel):
    normal_distance_m: float
    safe_distance_m: float
    normal_base_eta_sec: float
    safe_base_eta_sec: float
    normal_weather_eta_sec: float
    safe_weather_eta_sec: float
    normal_high_risk_segment_count: int
    safe_high_risk_segment_count: int
    avoided_high_risk_segments: int
    normal_mean_risk_score: float
    safe_mean_risk_score: float
    risk_reduction_percent: float
    eta_tradeoff_percent: float
    origin_zone_code: str
    destination_facility_name: Optional[str] = None
    destination_facility_type: str
    event_type: str
    event_id: str
    timestamp: str
    honesty_note: str
    candidate_search_used: bool = False
    candidate_pairs_tested: int = 0
    selected_origin_zone_code: Optional[str] = None
    selected_destination_facility_name: Optional[str] = None
    selected_reason: Optional[str] = None
    routes_identical: bool = False


