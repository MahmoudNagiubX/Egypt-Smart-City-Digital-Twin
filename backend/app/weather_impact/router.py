"""FastAPI API endpoints for weather-impact assessment."""

from fastapi import APIRouter, HTTPException
from . import service, paths, schemas

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



