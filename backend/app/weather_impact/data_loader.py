"""Data loading and retrieval helpers."""

import json
from pathlib import Path

import geopandas as gpd
import pandas as pd


def read_geojson(path):
    """Read a GeoJSON file and return a GeoDataFrame."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"GeoJSON file not found: {path}")
    return gpd.read_file(path)


def write_geojson(gdf, path):
    """Write a GeoDataFrame to a GeoJSON file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(path, driver="GeoJSON")


def save_json(data, path):
    """Save a dict or list as JSON."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_json(path):
    """Load and return a JSON file."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")
    with open(path, "r") as f:
        return json.load(f)


def read_csv(path):
    """Read a CSV file and return a pandas DataFrame."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")
    return pd.read_csv(path)


def write_csv(df, path):
    """Write a pandas DataFrame to a CSV file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
