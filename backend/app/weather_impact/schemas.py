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
