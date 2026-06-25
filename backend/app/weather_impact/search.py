"""Local search index building and query matching for Nasr City."""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional

from backend.app.weather_impact import paths, service

logger = logging.getLogger(__name__)

# Search index in-memory cache
_search_index: List[dict] = []
_initialized = False

def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower().strip()
    # Ignore punctuation
    text = re.sub(r'[^\w\s]', '', text)
    # Normalize Arabic letters
    text = re.sub(r'[أإآا]', 'ا', text)
    text = re.sub(r'[ة]', 'ه', text)
    text = re.sub(r'[ىي]', 'ي', text)
    return text

def get_geom_centroid(geometry: dict) -> tuple[float, float]:
    """Calculate representative centroid coordinates (lat, lon) for a geometry."""
    try:
        from shapely.geometry import shape
        point = shape(geometry).centroid
        return float(point.y), float(point.x)
    except Exception:
        # Fallback to coordinate average
        coords = []
        def extract_coords(g):
            if "coordinates" in g:
                c = g["coordinates"]
                if isinstance(c, list) and len(c) > 0:
                    if isinstance(c[0], list):
                        for sub in c:
                            if isinstance(sub, list) and len(sub) > 0:
                                if isinstance(sub[0], list):
                                    for sub2 in sub:
                                        coords.append(sub2)
                                else:
                                    coords.append(sub)
                            else:
                                coords.append(c)
                    else:
                        coords.append(c)
        extract_coords(geometry)
        if coords:
            lons = [c[0] for c in coords if isinstance(c, list) and len(c) >= 2]
            lats = [c[1] for c in coords if isinstance(c, list) and len(c) >= 2]
            if lats and lons:
                return sum(lats)/len(lats), sum(lons)/len(lons)
        return 30.0, 31.0

def build_local_search_index():
    """Build the local search index from POIs, emergency facilities, roads, and zones."""
    global _search_index, _initialized
    logger.info("Building local map search index...")
    
    index_items = []
    place_count = 0
    road_count = 0
    facility_count = 0
    zone_count = 0
    missing_name_count = 0
    warnings = []
    
    # 1. Load places & emergency facilities
    try:
        places_data, places_warnings = service._load_normalised_places()
        warnings.extend(places_warnings)
        
        for feature in places_data:
            properties = feature.get("properties") or {}
            geom = feature.get("geometry") or {}
            
            lat = properties.get("lat")
            lon = properties.get("lon")
            if lat is None or lon is None:
                coords = get_geom_centroid(geom)
                lat, lon = coords
                
            name = properties.get("name") or properties.get("display_name")
            display_name = properties.get("display_name")
            
            if not name:
                missing_name_count += 1
                name = properties.get("category_label") or "POI"
                display_name = name
                
            is_facility = properties.get("is_emergency_facility", False)
            category = properties.get("category") or "poi"
            category_label = properties.get("category_label") or "Place"
            
            item = {
                "id": f"place-{properties.get('place_id') or len(index_items)}",
                "name": name,
                "display_name": display_name,
                "category": "emergency" if is_facility else category,
                "category_label": f"Emergency {category_label}" if is_facility else category_label,
                "source": properties.get("source") or "OpenStreetMap",
                "lat": float(lat),
                "lon": float(lon),
                "confidence": 1.0,
                "inside_project_area": True,
                "geometry_type": "Point"
            }
            index_items.append(item)
            if is_facility:
                facility_count += 1
            else:
                place_count += 1
    except Exception as e:
        logger.error(f"Error loading places for search index: {e}")
        warnings.append(f"Error loading places: {e}")
        
    # 2. Load roads from nasr_city_roads.geojson
    try:
        if paths.NASR_CITY_ROADS_PATH.exists():
            roads_data = service.load_geojson_layer(paths.NASR_CITY_ROADS_PATH)
            
            # Aggregate roads by name to avoid duplicates
            road_segments = {}
            for feature in roads_data.get("features", []):
                properties = feature.get("properties") or {}
                name = properties.get("name") or properties.get("name:en")
                if name is not None and str(name).lower() != "nan" and str(name).strip() != "":
                    geom = feature.get("geometry") or {}
                    norm_name = normalize_text(name)
                    
                    if norm_name not in road_segments:
                        road_segments[norm_name] = {
                            "name": name,
                            "highway": properties.get("highway") or "road",
                            "geometries": []
                        }
                    road_segments[norm_name]["geometries"].append(geom)
            
            for norm_name, road_info in road_segments.items():
                lats = []
                lons = []
                for g in road_info["geometries"]:
                    lat, lon = get_geom_centroid(g)
                    lats.append(lat)
                    lons.append(lon)
                avg_lat = sum(lats)/len(lats) if lats else 30.0
                avg_lon = sum(lons)/len(lons) if lons else 31.0
                
                hw = road_info["highway"]
                category_label = hw.replace("_", " ").capitalize()
                
                item = {
                    "id": f"road-{norm_name[:30]}",
                    "name": road_info["name"],
                    "display_name": road_info["name"],
                    "category": "road",
                    "category_label": category_label,
                    "source": "OpenStreetMap / local project data",
                    "lat": float(avg_lat),
                    "lon": float(avg_lon),
                    "confidence": 0.90,
                    "inside_project_area": True,
                    "geometry_type": "LineString"
                }
                index_items.append(item)
                road_count += 1
        else:
            warnings.append("nasr_city_roads.geojson missing; road search unavailable.")
    except Exception as e:
        logger.error(f"Error loading roads for search index: {e}")
        warnings.append(f"Error loading roads: {e}")
        
    # 3. Load grid zones from nasr_city_grid_500m.geojson
    try:
        if paths.NASR_CITY_GRID_PATH.exists():
            grid_data = service.load_geojson_layer(paths.NASR_CITY_GRID_PATH)
            for feature in grid_data.get("features", []):
                properties = feature.get("properties") or {}
                zone_code = properties.get("zone_code")
                if zone_code:
                    match = re.search(r'\d+', zone_code)
                    number = match.group(0).lstrip('0') if match else zone_code
                    if not number:
                        number = "0"
                    
                    geom = feature.get("geometry") or {}
                    lat, lon = get_geom_centroid(geom)
                    
                    item = {
                        "id": f"zone-{zone_code}",
                        "name": f"Zone {number}",
                        "display_name": f"Zone {number}",
                        "category": "zone",
                        "category_label": "Grid Zone",
                        "source": "Local project grid",
                        "lat": float(lat),
                        "lon": float(lon),
                        "confidence": 0.95,
                        "inside_project_area": True,
                        "geometry_type": "Polygon"
                    }
                    index_items.append(item)
                    zone_count += 1
        else:
            warnings.append("nasr_city_grid_500m.geojson missing; zone search unavailable.")
    except Exception as e:
        logger.error(f"Error loading zones for search index: {e}")
        warnings.append(f"Error loading zones: {e}")
        
    _search_index = index_items
    _initialized = True
    
    # Save search index report
    report = {
        "status": "ok",
        "total_indexed_records": len(index_items),
        "place_count": place_count,
        "road_count": road_count,
        "emergency_facility_count": facility_count,
        "zone_count": zone_count,
        "missing_name_count": missing_name_count,
        "warnings": warnings
    }
    
    reports_dir = paths.NASR_CITY_DIR / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / "search_index_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    logger.info(f"Saved search index report with {len(index_items)} records to {report_path}")

def search_local(
    q: str,
    limit: int = 8,
    category: Optional[str] = None,
    include_roads: bool = True,
    include_places: bool = True
) -> List[dict]:
    """Search the local index for matching names, ranking matches by exactness/prefix."""
    global _search_index, _initialized
    if not _initialized:
        build_local_search_index()
        
    if not q or q.strip() == "":
        return []
        
    q_norm = normalize_text(q)
    results = []
    
    for item in _search_index:
        cat = item["category"]
        
        # Category filtering
        if cat == "road" and not include_roads:
            continue
        if cat != "road" and cat != "zone" and not include_places:
            continue
        if category and category != "all" and category != cat:
            continue
            
        # Match checks
        name_norm = normalize_text(item["name"])
        disp_norm = normalize_text(item["display_name"])
        
        is_zone_match = False
        if cat == "zone" and "nsr" in q_norm:
            if q_norm.replace(" ", "").replace("-", "") in item["id"].lower().replace("-", ""):
                is_zone_match = True
                
        if q_norm in name_norm or q_norm in disp_norm or is_zone_match:
            # Score calculations
            if q_norm == name_norm or q_norm == disp_norm:
                score = 1.0
            elif name_norm.startswith(q_norm) or disp_norm.startswith(q_norm):
                score = 0.8
            else:
                score = 0.5
                
            item_copy = dict(item)
            item_copy["confidence"] = float(round(item["confidence"] * score, 2))
            
            results.append((item_copy, score))
            
    # Sort results by score (descending), then by name length (ascending)
    results.sort(key=lambda x: (-x[1], len(x[0]["name"])))
    
    return [r[0] for r in results[:limit]]
