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

