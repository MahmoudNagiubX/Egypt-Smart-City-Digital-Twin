"""FastAPI API endpoints for weather-impact assessment."""

from fastapi import APIRouter, HTTPException, Query
from . import service, paths, schemas, weather, routing, heat_service, heat_explain

router = APIRouter(prefix="/api/weather-impact", tags=["weather-impact"])


@router.get("/health", response_model=schemas.ModuleStatusResponse)
def get_health():
    """Retrieve module health and file availability status."""
    try:
        return service.get_module_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve health status: {e}")


@router.get("/layers/boundary")
def get_boundary():
    """Get the Nasr City boundary GeoJSON."""
    try:
        return service.load_geojson_layer(paths.NASR_CITY_BOUNDARY_PATH)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/layers/grid")
def get_grid():
    """Get the 500m grid cells GeoJSON."""
    try:
        return service.load_geojson_layer(paths.NASR_CITY_GRID_PATH)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/layers/roads")
def get_roads():
    """Get the roads GeoJSON."""
    try:
        return service.load_geojson_layer(paths.NASR_CITY_ROADS_PATH)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/layers/roads-zones")
def get_roads_zones():
    """Get the roads joined with grid zone IDs GeoJSON."""
    try:
        return service.load_geojson_layer(paths.ROADS_WITH_ZONE_IDS_PATH)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/layers/emergency-facilities")
def get_emergency_facilities():
    """Get the emergency facilities GeoJSON."""
    try:
        return service.load_geojson_layer(paths.NASR_CITY_FACILITIES_PATH)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/places")
def get_places(category: str = "all", limit: int | None = Query(default=None, ge=1)):
    """Get real processed places and POIs as a frontend-ready FeatureCollection."""
    try:
        return service.get_places(category=category, limit=limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/places/summary")
def get_places_summary():
    """Get place category counts and source warnings."""
    try:
        return service.get_places_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictions/metadata", response_model=schemas.PredictionMetadataResponse)
def get_prediction_metadata():
    """Get metadata about predictions (model used, row counts, events, etc.)."""
    try:
        return service.get_prediction_metadata()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/layers/predictions/all")
def get_predictions_all():
    """Get all prediction records joined with grid geometry GeoJSON."""
    try:
        return service.load_geojson_layer(paths.REAL_OBSERVED_PREDICTIONS_GEOJSON_PATH)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/layers/predictions/latest")
def get_predictions_latest():
    """Get latest selected event prediction layer GeoJSON."""
    try:
        return service.load_geojson_layer(paths.LATEST_SELECTED_EVENT_RISK_GEOJSON_PATH)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/layers/predictions/top-rain")
def get_predictions_top_rain():
    """Get top rain event prediction layer GeoJSON."""
    try:
        return service.load_geojson_layer(paths.TOP_RAIN_EVENT_RISK_GEOJSON_PATH)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/layers/risk-summary")
def get_risk_summary():
    """Get zone risk summary GeoJSON."""
    try:
        return service.load_geojson_layer(paths.ZONE_RISK_SUMMARY_GEOJSON_PATH)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events", response_model=list[schemas.EventSummary])
def get_events():
    """List unique events with summary metrics from predictions."""
    try:
        return service.list_prediction_events()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/{event_id}/risk-layer")
def get_event_risk_layer(event_id: str):
    """Get prediction risk layer GeoJSON for a specific event."""
    try:
        return service.get_event_risk_layer(event_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
def get_summary():
    """Get aggregated summary statistics for dashboard display."""
    try:
        return service.get_summary_stats()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/routing/status", response_model=schemas.RoutingStatusResponse)
def get_routing_status():
    """Get the routing validation report status."""
    try:
        return service.get_routing_status()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/routing/demo/{event_type}/{route_type}")
def get_routing_demo(event_type: str, route_type: str):
    """Get the GeoJSON FeatureCollection for a normal or safe demo route."""
    if event_type not in ["top-rain", "latest"]:
        raise HTTPException(status_code=400, detail=f"Invalid event_type: {event_type}")
    if route_type not in ["normal", "safe", "weather_safe"]:
        raise HTTPException(status_code=400, detail=f"Invalid route_type: {route_type}")
        
    try:
        return service.get_demo_route(event_type, route_type)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/routing/comparison/{event_type}", response_model=schemas.RouteComparisonResponse)
def get_routing_comparison(event_type: str):
    """Get comparison metrics for normal vs safe route."""
    if event_type not in ["top-rain", "latest"]:
        raise HTTPException(status_code=400, detail=f"Invalid event_type: {event_type}")
        
    try:
        return service.get_route_comparison(event_type)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/routing/custom/emergency-route")
def post_custom_emergency_route(request: schemas.CustomEmergencyRouteRequest):
    """Compute normal and weather-safe routes between clicked map coordinates."""
    if request.event_type not in ["top-rain", "latest"]:
        raise HTTPException(
            status_code=400, detail=f"Invalid event_type: {request.event_type}"
        )
    try:
        return service.get_custom_emergency_route(
            request.origin.model_dump(),
            request.destination.model_dump(),
            request.event_type,
            request.route_preference,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weather/live")
def get_live_weather():
    """Get the current live weather forecast summary for Nasr City."""
    try:
        forecast_data, warnings = weather.fetch_live_weather_forecast()
        summary = weather.summarize_live_weather_forecast(forecast_data, warnings=warnings)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch live weather: {e}")


@router.get("/layers/predictions/live")
def get_live_predictions():
    """Get live weather risk layer GeoJSON."""
    try:
        if not paths.LIVE_WEATHER_RISK_GEOJSON_PATH.exists():
            service.generate_live_weather_risk_layer()
        return service.load_geojson_layer(paths.LIVE_WEATHER_RISK_GEOJSON_PATH)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weather/live/report")
def get_live_report():
    """Get live weather risk report JSON."""
    try:
        if not paths.LIVE_WEATHER_RISK_REPORT_PATH.exists():
            service.generate_live_weather_risk_layer()
        return service.load_json_file(paths.LIVE_WEATHER_RISK_REPORT_PATH)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/routing/live/status", response_model=schemas.LiveRoutingStatusResponse)
def get_live_routing_status():
    """Get status and readiness metadata for live weather-aware routing."""
    try:
        return service.get_live_routing_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/routing/live/emergency-route", response_model=schemas.LiveEmergencyRouteResponse)
def post_live_emergency_route(request: schemas.LiveEmergencyRouteRequest):
    """Compute custom live weather-aware routes and return comparison and GeoJSON overlays."""
    try:
        origin = {"lat": request.origin.lat, "lon": request.origin.lon}
        destination = {"lat": request.destination.lat, "lon": request.destination.lon}
        
        result = routing.compute_live_custom_route(
            origin,
            destination,
            route_preference=request.route_preference,
            refresh_live_weather=request.refresh_live_weather
        )
        return result
    except routing.RoutingPointOutsideGraphError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=schemas.SearchResponse)
def get_search(
    q: str = Query(..., min_length=1),
    limit: int = Query(default=8, ge=1, le=20),
    category: str | None = Query(default=None),
    include_roads: bool = Query(default=True),
    include_places: bool = Query(default=True)
):
    """Search street, POI place, emergency facility, or grid zone within Nasr City local index."""
    try:
        return service.search_places_and_roads(
            q=q,
            limit=limit,
            category=category,
            include_roads=include_roads,
            include_places=include_places
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/explain/zone/{zone_code}", response_model=schemas.ZoneExplainResponse)
def get_explain_zone(
    zone_code: str,
    mode: str = Query(default="live"),
    event_id: str | None = Query(default=None)
):
    """Explain estimated risk factors for a specific zone."""
    try:
        return service.explain_zone_risk(zone_code, mode=mode, event_id=event_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain/route", response_model=schemas.RouteExplainResponse)
def post_explain_route(request: schemas.RouteExplainRequest):
    """Explain weather-safe custom routing decisions and tradeoffs."""
    try:
        origin = {"lat": request.origin.lat, "lon": request.origin.lon}
        destination = {"lat": request.destination.lat, "lon": request.destination.lon}
        return service.explain_route_recommendation(origin, destination, mode=request.mode)
    except routing.RoutingPointOutsideGraphError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model/explainability-summary", response_model=schemas.ModelExplainabilitySummaryResponse)
def get_model_explainability_summary():
    """Retrieve global model explainability metrics, permutation importances, and limitations."""
    try:
        return service.get_model_explainability_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/heat/health", response_model=schemas.HeatHealthResponse)
def get_heat_health():
    """Retrieve availability and status of Urban Heat Risk components."""
    try:
        return heat_service.get_heat_health()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/heat/layer/latest")
def get_heat_layer_latest():
    """Get the latest heat risk GeoJSON layer."""
    try:
        return heat_service.get_latest_layer()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/heat/summary", response_model=schemas.HeatSummaryResponse)
def get_heat_summary():
    """Get latest heat risk dashboard summary metrics."""
    try:
        return heat_service.get_heat_summary()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/heat/explain/zone/{zone_code}", response_model=schemas.HeatZoneExplainResponse)
def get_heat_explain_zone(
    zone_code: str,
    date: str | None = Query(default=None),
    latest: bool = Query(default=True)
):
    """Explain model-estimated heat risk factors for a specific grid zone."""
    try:
        return heat_explain.load_explanation_and_prediction(
            zone_code=zone_code,
            date=date,
            latest=latest
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/heat/model/summary", response_model=schemas.HeatModelSummaryResponse)
def get_heat_model_summary():
    """Retrieve global explainability, benchmarking metrics, and authenticity metadata for the Heat Risk model."""
    try:
        return heat_service.get_model_summary()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





