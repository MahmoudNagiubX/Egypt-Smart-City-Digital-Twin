"""Collect real OpenStreetMap places for the Nasr City map experience."""

import json
import logging
import sys
from pathlib import Path

import geopandas as gpd
import osmnx as ox
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))

from backend.app.weather_impact import paths, service

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

OSM_TAGS = {
    "amenity": [
        "hospital",
        "clinic",
        "place_of_worship",
        "school",
        "university",
        "police",
        "fire_station",
    ],
    "shop": "mall",
    "tourism": ["attraction", "museum"],
    "historic": True,
}


def _category(row):
    amenity = str(row.get("amenity") or "").lower()
    if amenity == "place_of_worship":
        return "mosque" if str(row.get("religion") or "").lower() == "muslim" else None
    if amenity in {
        "hospital",
        "clinic",
        "school",
        "university",
        "police",
        "fire_station",
    }:
        return amenity
    if str(row.get("shop") or "").lower() == "mall":
        return "mall"
    if pd.notna(row.get("tourism")) or pd.notna(row.get("historic")):
        return "landmark"
    return None


def collect_pois():
    """Fetch and persist OSM places; never synthesize fallback features."""
    if not paths.NASR_CITY_BOUNDARY_PATH.exists():
        raise FileNotFoundError(
            f"Nasr City boundary is required at {paths.NASR_CITY_BOUNDARY_PATH}"
        )

    boundary = gpd.read_file(paths.NASR_CITY_BOUNDARY_PATH).to_crs("EPSG:4326")
    polygon = boundary.geometry.union_all()
    ox.settings.use_cache = False
    logger.info("Fetching real Nasr City POIs from OpenStreetMap...")
    raw = ox.features_from_polygon(polygon, OSM_TAGS)
    if raw.empty:
        raise RuntimeError("OpenStreetMap returned no matching POIs.")

    raw = raw.reset_index()
    raw["category"] = raw.apply(_category, axis=1)
    raw = raw[raw["category"].notna()].copy()
    if raw.empty:
        raise RuntimeError("OpenStreetMap returned no POIs in supported categories.")

    raw["geometry"] = raw.geometry.apply(
        lambda geometry: geometry
        if geometry.geom_type == "Point"
        else geometry.representative_point()
    )
    raw["source"] = "OpenStreetMap"
    raw["place_id"] = raw.apply(
        lambda row: (
            f"osm-{row.get('element', row.get('element_type', 'feature'))}-"
            f"{row.get('id', row.name)}"
        ),
        axis=1,
    )
    raw = raw.drop_duplicates(subset=["place_id"]).to_crs("EPSG:4326")

    columns = [
        "place_id",
        "name",
        "name:en",
        "category",
        "amenity",
        "religion",
        "shop",
        "tourism",
        "historic",
        "source",
        "geometry",
    ]
    for column in columns:
        if column not in raw.columns:
            raw[column] = None
    pois = gpd.GeoDataFrame(raw[columns], geometry="geometry", crs="EPSG:4326")
    paths.ensure_data_dirs()
    pois.to_file(paths.NASR_CITY_POIS_PATH, driver="GeoJSON")
    logger.info("Saved %s real POIs to %s", len(pois), paths.NASR_CITY_POIS_PATH)
    return pois


def write_summary_report(fetch_warning=None):
    summary = service.get_places_summary()
    if fetch_warning:
        summary["status"] = "ok_with_warnings"
        summary["warnings"] = list(dict.fromkeys([fetch_warning, *summary["warnings"]]))
    with open(paths.PLACES_SUMMARY_REPORT_PATH, "w", encoding="utf-8") as output:
        json.dump(summary, output, indent=2, ensure_ascii=False)
    logger.info("Saved places summary to %s", paths.PLACES_SUMMARY_REPORT_PATH)
    return summary


def main():
    warning = None
    try:
        collect_pois()
    except Exception as exc:
        warning = (
            "Broader OpenStreetMap POI fetch failed; existing emergency facilities remain "
            f"available. Reason: {exc}"
        )
        logger.warning(warning)
    summary = write_summary_report(warning)
    logger.info("POI collection status: %s", summary["status"])


if __name__ == "__main__":
    main()
