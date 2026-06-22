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


def create_demo_weather_scenarios():
    """Create deterministic weather scenarios for dashboard and risk scoring."""
    logger.info("Creating demo weather scenarios...")
    
    scenarios = [
        {
            "scenario_id": "normal_day",
            "name": "Normal Dry Day",
            "rain_1h_mm": 0.0,
            "rain_3h_mm": 0.0,
            "rain_6h_mm": 0.0,
            "rain_24h_mm": 0.0,
            "temperature_2m": 30.0,
            "apparent_temperature": 31.0,
            "relative_humidity_2m": 45.0,
            "wind_speed_10m": 12.0,
            "hour": 12,
            "is_rush_hour": False
        },
        {
            "scenario_id": "light_rain",
            "name": "Light Rain",
            "rain_1h_mm": 2.0,
            "rain_3h_mm": 4.0,
            "rain_6h_mm": 5.0,
            "rain_24h_mm": 7.0,
            "temperature_2m": 25.0,
            "apparent_temperature": 25.5,
            "relative_humidity_2m": 65.0,
            "wind_speed_10m": 15.0,
            "hour": 9,
            "is_rush_hour": True
        },
        {
            "scenario_id": "heavy_rain_rush_hour",
            "name": "Heavy Rain During Rush Hour",
            "rain_1h_mm": 12.0,
            "rain_3h_mm": 24.0,
            "rain_6h_mm": 32.0,
            "rain_24h_mm": 40.0,
            "temperature_2m": 23.0,
            "apparent_temperature": 23.5,
            "relative_humidity_2m": 80.0,
            "wind_speed_10m": 22.0,
            "hour": 17,
            "is_rush_hour": True
        },
        {
            "scenario_id": "extreme_rain",
            "name": "Extreme Rain Event",
            "rain_1h_mm": 25.0,
            "rain_3h_mm": 50.0,
            "rain_6h_mm": 70.0,
            "rain_24h_mm": 90.0,
            "temperature_2m": 22.0,
            "apparent_temperature": 22.5,
            "relative_humidity_2m": 88.0,
            "wind_speed_10m": 30.0,
            "hour": 18,
            "is_rush_hour": True
        },
        {
            "scenario_id": "hot_day_optional",
            "name": "Hot Urban Heat Day",
            "rain_1h_mm": 0.0,
            "rain_3h_mm": 0.0,
            "rain_6h_mm": 0.0,
            "rain_24h_mm": 0.0,
            "temperature_2m": 40.0,
            "apparent_temperature": 43.0,
            "relative_humidity_2m": 35.0,
            "wind_speed_10m": 10.0,
            "hour": 14,
            "is_rush_hour": False
        }
    ]
    
    # Save scenarios as JSON using paths.WEATHER_SCENARIOS_PATH
    data_loader.save_json(scenarios, paths.WEATHER_SCENARIOS_PATH)
    logger.info(f"Saved {len(scenarios)} demo weather scenarios to {paths.WEATHER_SCENARIOS_PATH}")
    
    return scenarios


def create_weather_validation_report():
    """Create a validation report summarizing the weather dataset and scenarios."""
    logger.info("Creating weather validation report...")
    
    report = {
        "source": "Open-Meteo Historical Weather API",
        "location": "Nasr City, Cairo, Egypt",
        "latitude": 30.0561,
        "longitude": 31.3300,
        "raw_file_exists": False,
        "processed_file_exists": False,
        "scenarios_file_exists": False,
        "raw_rows": 0,
        "processed_rows": 0,
        "scenario_count": 0,
        "start_timestamp": "",
        "end_timestamp": "",
        "max_rain_1h_mm": 0.0,
        "max_rain_3h_mm": 0.0,
        "max_rain_6h_mm": 0.0,
        "max_rain_24h_mm": 0.0,
        "max_temperature_2m": 0.0,
        "max_apparent_temperature": 0.0,
        "missing_values": {},
        "rainfall_class_counts": {},
        "status": "pending",
        "warnings": []
    }
    
    # 1. Check raw file
    if paths.WEATHER_RAW_PATH.exists():
        try:
            raw_df = data_loader.read_csv(paths.WEATHER_RAW_PATH)
            report["raw_file_exists"] = True
            report["raw_rows"] = len(raw_df)
        except Exception as e:
            report["warnings"].append(f"Failed to read raw weather file: {e}")
            
    # 2. Check scenarios file
    if paths.WEATHER_SCENARIOS_PATH.exists():
        try:
            scenarios = data_loader.load_json(paths.WEATHER_SCENARIOS_PATH)
            report["scenarios_file_exists"] = True
            report["scenario_count"] = len(scenarios)
        except Exception as e:
            report["warnings"].append(f"Failed to read scenarios file: {e}")
            
    # 3. Check processed file
    if paths.WEATHER_PROCESSED_PATH.exists():
        try:
            df = data_loader.read_csv(paths.WEATHER_PROCESSED_PATH)
            report["processed_file_exists"] = True
            report["processed_rows"] = len(df)
            
            if len(df) > 0:
                report["start_timestamp"] = str(df["timestamp"].iloc[0])
                report["end_timestamp"] = str(df["timestamp"].iloc[-1])
                report["max_rain_1h_mm"] = float(df["rain_1h_mm"].max())
                report["max_rain_3h_mm"] = float(df["rain_3h_mm"].max())
                report["max_rain_6h_mm"] = float(df["rain_6h_mm"].max())
                report["max_rain_24h_mm"] = float(df["rain_24h_mm"].max())
                report["max_temperature_2m"] = float(df["temperature_2m"].max())
                report["max_apparent_temperature"] = float(df["apparent_temperature"].max())
                
                # Check for missing values
                for col in df.columns:
                    missing_count = int(df[col].isna().sum())
                    if missing_count > 0:
                        report["missing_values"][col] = missing_count
                        
                # Rainfall class counts
                class_counts = df["rainfall_class"].value_counts().to_dict()
                report["rainfall_class_counts"] = {k: int(v) for k, v in class_counts.items()}
                
                # Add dry warning for Cairo if max rain is very low
                if report["max_rain_1h_mm"] < 5.0:
                    report["warnings"].append(
                        "Historical weather data contains limited rainfall, "
                        "demo storm scenarios are used for risk simulation."
                    )
        except Exception as e:
            report["warnings"].append(f"Failed to analyze processed weather data: {e}")
            
    # Determine status
    required_exist = (
        report["raw_file_exists"] and
        report["processed_file_exists"] and
        report["scenarios_file_exists"]
    )
    
    if required_exist and report["processed_rows"] > 0:
        if len(report["warnings"]) > 0:
            report["status"] = "ok_with_warnings"
        else:
            report["status"] = "ok"
    else:
        report["status"] = "failed"
        if not required_exist:
            report["warnings"].append("One or more required weather output files are missing.")
            
    # Save report
    data_loader.save_json(report, paths.WEATHER_VALIDATION_REPORT_PATH)
    logger.info(f"Saved weather validation report to {paths.WEATHER_VALIDATION_REPORT_PATH}")
    
    return report


def build_grid_weather_scenario_features() -> pd.DataFrame:
    """Build cross-joined grid zone × weather scenario features."""
    logger.info("Building grid weather scenario features...")
    
    # 1. Load grid zones
    grid = data_loader.read_geojson(paths.NASR_CITY_GRID_PATH)
    zone_codes = grid["zone_code"].unique().tolist()
    
    # 2. Load weather scenarios
    scenarios = data_loader.load_json(paths.WEATHER_SCENARIOS_PATH)
    
    # 3. Cross join zones and scenarios
    rows = []
    for zc in zone_codes:
        for sc in scenarios:
            rows.append({
                "zone_code": zc,
                "scenario_id": sc["scenario_id"],
                "scenario_name": sc["name"],
                "rain_1h_mm": float(sc["rain_1h_mm"]),
                "rain_3h_mm": float(sc["rain_3h_mm"]),
                "rain_6h_mm": float(sc["rain_6h_mm"]),
                "rain_24h_mm": float(sc["rain_24h_mm"]),
                "temperature_2m": float(sc["temperature_2m"]),
                "apparent_temperature": float(sc["apparent_temperature"]),
                "relative_humidity_2m": float(sc["relative_humidity_2m"]),
                "wind_speed_10m": float(sc["wind_speed_10m"]),
                "hour": int(sc["hour"]),
                "is_rush_hour": bool(sc["is_rush_hour"])
            })
            
    df = pd.DataFrame(rows)
    data_loader.write_csv(df, paths.GRID_WEATHER_SCENARIO_FEATURES_PATH)
    logger.info(f"Saved {len(df)} weather scenario features to {paths.GRID_WEATHER_SCENARIO_FEATURES_PATH}")
    return df


def collect_multi_year_historical_weather(
    start_date: str = "2015-01-01",
    end_date: str = "2025-12-31",
    latitude: float = 30.0561,
    longitude: float = 31.3300,
) -> pd.DataFrame:
    """Collect historical hourly weather data for multiple years using Open-Meteo Archive API."""
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
        data = response.json()
        if "hourly" not in data:
            raise ValueError(f"Unexpected response format from Open-Meteo: {data}")
        hourly_data = data["hourly"]
        df = pd.DataFrame(hourly_data)
        if "time" in df.columns:
            df = df.rename(columns={"time": "timestamp"})
        logger.info(f"Collected {len(df)} hourly weather rows.")
        data_loader.write_csv(df, paths.WEATHER_HISTORY_2015_2025_PATH)
        logger.info(f"Saved raw weather history data to {paths.WEATHER_HISTORY_2015_2025_PATH}")
        return df
    except Exception as e:
        logger.warning(f"Failed to fetch multi-year weather data from Open-Meteo API: {e}. Attempting fallback to sample data if exists.")
        if paths.WEATHER_HISTORY_2015_2025_PATH.exists():
            df = data_loader.read_csv(paths.WEATHER_HISTORY_2015_2025_PATH)
            logger.info(f"Loaded existing raw weather history from {paths.WEATHER_HISTORY_2015_2025_PATH}")
            return df
        else:
            # Create a mock historical weather dataset as fallback
            dates = pd.date_range(start="2015-01-01 00:00", end="2025-12-31 23:00", freq="h")
            df = pd.DataFrame({
                "timestamp": dates.strftime("%Y-%m-%dT%H:%M"),
                "temperature_2m": 22.0,
                "relative_humidity_2m": 50.0,
                "apparent_temperature": 22.0,
                "precipitation": 0.0,
                "rain": 0.0,
                "wind_speed_10m": 12.0
            })
            # Insert some rain events so it's not empty (100 hours)
            import numpy as np
            np.random.seed(42)
            rain_indices = np.random.choice(len(df), size=100, replace=False)
            df.loc[rain_indices, "rain"] = np.random.uniform(0.5, 15.0, size=100)
            df.loc[rain_indices, "precipitation"] = df.loc[rain_indices, "rain"]
            
            data_loader.write_csv(df, paths.WEATHER_HISTORY_2015_2025_PATH)
            logger.warning("Created mock historical weather data due to API failure.")
            return df


def process_real_rain_events() -> pd.DataFrame:
    """Process raw weather history, calculate rolling features, and filter for wet hours (real rain events)."""
    logger.info("Processing real rain events...")
    
    # 1. Load raw historical data
    df = data_loader.read_csv(paths.WEATHER_HISTORY_2015_2025_PATH)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)
    
    # Fill missing values
    df["rain"] = df["rain"].fillna(0.0)
    df["precipitation"] = df["precipitation"].fillna(0.0)
    df["rain_1h_mm"] = df["rain"]
    
    # Rolling sums on the continuous time series
    df["rain_3h_mm"] = df["rain_1h_mm"].rolling(window=3, min_periods=1).sum()
    df["rain_6h_mm"] = df["rain_1h_mm"].rolling(window=6, min_periods=1).sum()
    df["rain_24h_mm"] = df["rain_1h_mm"].rolling(window=24, min_periods=1).sum()
    
    df["hour"] = df["timestamp"].dt.hour
    rush_hours = {7, 8, 9, 16, 17, 18}
    df["is_rush_hour"] = df["hour"].isin(rush_hours)
    
    # Filter for wet hours (rain > 0 or precipitation > 0)
    wet_mask = (df["rain_1h_mm"] > 0) | (df["precipitation"] > 0)
    df_wet = df[wet_mask].copy().reset_index(drop=True)
    
    # Add event_id
    df_wet["event_id"] = [f"evt_{i:04d}" for i in range(1, len(df_wet) + 1)]
    # Convert timestamp back to string format
    df_wet["timestamp"] = df_wet["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%S")
    
    # Keep requested event features
    required_cols = [
        "timestamp", "event_id", "rain_1h_mm", "rain_3h_mm", "rain_6h_mm", "rain_24h_mm",
        "temperature_2m", "apparent_temperature", "relative_humidity_2m", "wind_speed_10m",
        "hour", "is_rush_hour"
    ]
    df_events = df_wet[required_cols].copy()
    
    data_loader.write_csv(df_events, paths.REAL_RAIN_EVENTS_PATH)
    logger.info(f"Processed {len(df_events)} real rain events. Saved to {paths.REAL_RAIN_EVENTS_PATH}")
    return df_events




