"""Pydantic schemas for request/response validation."""

from typing import Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field


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
    safe_route_quality: str = "accepted"
    safe_route_available: bool = True
    quality_guard_passed: bool = True


class RouteCoordinate(BaseModel):
    lat: float = Field(ge=-90.0, le=90.0)
    lon: float = Field(ge=-180.0, le=180.0)


class CustomEmergencyRouteRequest(BaseModel):
    origin: RouteCoordinate
    destination: RouteCoordinate
    event_type: str = "top-rain"
    route_preference: Literal["both", "normal", "weather-safe"] = "both"


class LiveRoutingStatusResponse(BaseModel):
    status: str
    live_weather_available: bool
    live_risk_layer_available: bool
    live_report_status: str
    rain_risk_expected: bool
    risk_class_counts: Dict[str, int]
    recommended_mode: str
    warnings: List[str]
    honesty_note: str


class LiveEmergencyRouteRequest(BaseModel):
    origin: RouteCoordinate
    destination: RouteCoordinate
    route_preference: Literal["both", "normal", "weather-safe"] = "both"
    refresh_live_weather: bool = False


class LiveRouteSnappedPoint(BaseModel):
    lat: float
    lon: float
    nearest_node: Union[str, int]
    snap_distance_m: float


class LiveRouteComparison(BaseModel):
    safe_route_available: bool
    safe_route_quality: str
    risk_reduction_percent: float
    eta_tradeoff_percent: float
    avoided_high_risk_segments: int
    normal_distance_m: float
    safe_distance_m: float
    normal_weather_eta_sec: float
    safe_weather_eta_sec: float
    normal_mean_live_risk_score: float
    safe_mean_live_risk_score: float
    live_high_risk_segment_count_normal: int
    live_high_risk_segment_count_safe: int
    honesty_note: str


class LiveWeatherForecastSummary(BaseModel):
    rain_1h_mm: float
    rain_3h_mm: float
    rain_6h_mm: float
    rain_24h_mm: float
    max_precipitation_probability: float


class LiveEmergencyRouteResponse(BaseModel):
    status: str
    mode: str = "live_weather"
    rain_risk_expected: bool
    recommendation: str
    origin: LiveRouteSnappedPoint
    destination: LiveRouteSnappedPoint
    normal_route: Dict
    weather_safe_route: Dict
    comparison: LiveRouteComparison
    live_weather_summary: LiveWeatherForecastSummary
    honesty_note: str


class SearchResultItem(BaseModel):
    id: str
    name: str
    display_name: str
    category: str
    category_label: str
    source: str
    lat: float
    lon: float
    confidence: float
    inside_project_area: bool
    geometry_type: Literal["Point", "LineString", "Polygon"]


class SearchResponse(BaseModel):
    status: str
    query: str
    results: List[SearchResultItem]
    warnings: List[str]


# Phase 9C — Explainability Schemas
class ZoneFactor(BaseModel):
    factor: str
    label: str
    value: float
    impact: str
    reason: str


class ZoneExplainResponse(BaseModel):
    status: str
    zone_code: str
    zone_label: str
    mode: str
    risk_score: float
    risk_class: str
    risk_label: str
    summary: str
    top_factors: List[ZoneFactor]
    explanation_text: str
    confidence_note: str
    honesty_note: str


class RouteExplainRequest(BaseModel):
    origin: RouteCoordinate
    destination: RouteCoordinate
    mode: str = "live"
    route_preference: str = "both"


class RouteReason(BaseModel):
    label: str
    value: str
    reason: str


class RouteDetailExplanation(BaseModel):
    summary: str
    risk_level: str
    high_risk_segments: int
    mean_risk_score: float


class RouteComparisonSummary(BaseModel):
    risk_reduction_percent: float
    eta_tradeoff_percent: float
    avoided_high_risk_segments: int
    normal_distance_m: float
    safe_distance_m: float


class RouteExplainResponse(BaseModel):
    status: str
    mode: str
    recommendation: str
    recommendation_label: str
    summary: str
    route_reasons: List[RouteReason]
    normal_route_explanation: RouteDetailExplanation
    safe_route_explanation: RouteDetailExplanation
    comparison: RouteComparisonSummary
    honesty_note: str


class GlobalFeatureImportance(BaseModel):
    feature: str
    label: str
    importance: float
    reason: str


class ModelExplainabilitySummaryResponse(BaseModel):
    status: str
    model_name: str
    model_type: str
    target: str
    top_global_features: List[GlobalFeatureImportance]
    metrics: Dict[str, Union[float, int, str, dict, list, None]]
    model_size_mb: float
    known_limitations: List[str]
    honesty_note: str





