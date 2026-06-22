"""Weather data retrieval and preprocessing helpers."""

import logging
import pandas as pd
import requests
from . import data_loader, paths

logger = logging.getLogger(__name__)


def collect_open_meteo_weather(
    start_date: str = "2024-01-01",
    end_date: str = "2024-12-31",
    latitude: float = 30.0561,
    longitude: float = 31.3300,
) -> pd.DataFrame:
    """Collect historical hourly weather data for Nasr City using Open-Meteo Archive API."""
    paths.ensure_data_dirs()
    
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,wind_speed_10m",
        "timezone": "Africa/Cairo",
    }
    
    logger.info(f"Requesting Open-Meteo weather from {start_date} to {end_date} for ({latitude}, {longitude})...")
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch weather data from Open-Meteo API: {e}")
        raise RuntimeError(f"Open-Meteo weather collection failed: {e}")
        
    data = response.json()
    if "hourly" not in data:
        raise ValueError(f"Unexpected response format from Open-Meteo: {data}")
        
    hourly_data = data["hourly"]
    
    # Create DataFrame
    df = pd.DataFrame(hourly_data)
    
    # Rename time column to timestamp
    if "time" in df.columns:
        df = df.rename(columns={"time": "timestamp"})
        
    logger.info(f"Collected {len(df)} hourly weather rows.")
    
    # Save CSV
    data_loader.write_csv(df, paths.WEATHER_RAW_PATH)
    logger.info(f"Saved raw weather data to {paths.WEATHER_RAW_PATH}")
    
    return df
