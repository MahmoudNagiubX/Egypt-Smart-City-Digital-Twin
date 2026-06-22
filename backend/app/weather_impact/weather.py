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


def clean_weather_data() -> pd.DataFrame:
    """Clean raw weather data and calculate rolling precipitation features."""
    logger.info("Cleaning weather data...")
    
    # 1. Load raw data
    df = data_loader.read_csv(paths.WEATHER_RAW_PATH)
    
    # 2. Parse timestamp and sort
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)
    
    # 3. Fill missing values in rain/precipitation with 0
    if "rain" in df.columns:
        df["rain"] = df["rain"].fillna(0.0)
    else:
        df["rain"] = 0.0
        
    if "precipitation" in df.columns:
        df["precipitation"] = df["precipitation"].fillna(0.0)
    else:
        df["precipitation"] = 0.0
        
    # Other potential columns to fill if missing
    for col in ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "wind_speed_10m"]:
        if col in df.columns:
            df[col] = df[col].ffill().bfill().fillna(0.0)
            
    # 4. rain_1h_mm = rain column or precipitation fallback
    df["rain_1h_mm"] = df["rain"] if "rain" in df.columns else df["precipitation"]
    
    # 5. Calculate rolling sums
    df["rain_3h_mm"] = df["rain_1h_mm"].rolling(window=3, min_periods=1).sum()
    df["rain_6h_mm"] = df["rain_1h_mm"].rolling(window=6, min_periods=1).sum()
    df["rain_24h_mm"] = df["rain_1h_mm"].rolling(window=24, min_periods=1).sum()
    
    # 6. Extract hour and date
    df["hour"] = df["timestamp"].dt.hour
    df["date"] = df["timestamp"].dt.date.astype(str)
    
    # 7. is_rush_hour: 7, 8, 9, 16, 17, 18
    rush_hours = {7, 8, 9, 16, 17, 18}
    df["is_rush_hour"] = df["hour"].isin(rush_hours)
    
    # 8. rainfall_class mapping
    def classify_rainfall(rain_val):
        if rain_val == 0:
            return "none"
        elif 0 < rain_val <= 2:
            return "light"
        elif 2 < rain_val <= 5:
            return "moderate"
        elif 5 < rain_val <= 10:
            return "heavy"
        else:
            return "extreme"
            
    df["rainfall_class"] = df["rain_1h_mm"].apply(classify_rainfall)
    
    # Keep only required columns
    required_cols = [
        "timestamp", "date", "hour", "temperature_2m", "relative_humidity_2m",
        "apparent_temperature", "precipitation", "rain", "wind_speed_10m",
        "rain_1h_mm", "rain_3h_mm", "rain_6h_mm", "rain_24h_mm",
        "rainfall_class", "is_rush_hour"
    ]
    df_processed = df[[c for c in required_cols if c in df.columns]].copy()
    
    # Save processed CSV
    data_loader.write_csv(df_processed, paths.WEATHER_PROCESSED_PATH)
    logger.info(f"Saved processed weather data with {len(df_processed)} rows to {paths.WEATHER_PROCESSED_PATH}")
    
    return df_processed

