"""Weather-impact scoring helpers and normalization utilities."""

import pandas as pd


def clip01(value):
    """Clip a value or pandas Series between 0.0 and 1.0."""
    if isinstance(value, pd.Series):
        return value.clip(0.0, 1.0)
    try:
        return max(0.0, min(1.0, float(value)))
    except (ValueError, TypeError):
        return 0.0


def normalize_series(series, inverse=False):
    """Normalize a pandas Series to range [0.0, 1.0]."""
    series_num = pd.to_numeric(series, errors="coerce").fillna(0.0)
    s_min = series_num.min()
    s_max = series_num.max()
    
    if s_max > s_min:
        normalized = (series_num - s_min) / (s_max - s_min)
    else:
        normalized = series_num * 0.0 + 0.5
        
    if inverse:
        normalized = 1.0 - normalized
        
    return normalized.clip(0.0, 1.0)


def safe_divide(a, b, default=0.0):
    """Safely divide a by b, handling zero division."""
    try:
        if b == 0.0 or b == 0:
            return default
        return a / b
    except Exception:
        return default


def rainfall_to_score(rain_1h_mm, rain_3h_mm, rain_6h_mm, rain_24h_mm):
    """Map rainfall intensities to primary and accumulation scores."""
    if isinstance(rain_1h_mm, pd.Series):
        score_1h = (rain_1h_mm / 15.0).clip(0.0, 1.0)
        
        acc = (
            (rain_3h_mm / 25.0) * 0.5 +
            (rain_6h_mm / 45.0) * 0.3 +
            (rain_24h_mm / 75.0) * 0.2
        )
        score_acc = acc.clip(0.0, 1.0)
    else:
        score_1h = max(0.0, min(1.0, float(rain_1h_mm) / 15.0))
        
        acc = (
            (float(rain_3h_mm) / 25.0) * 0.5 +
            (float(rain_6h_mm) / 45.0) * 0.3 +
            (float(rain_24h_mm) / 75.0) * 0.2
        )
        score_acc = max(0.0, min(1.0, acc))
        
    return score_1h, score_acc


def temperature_to_score(temperature_2m, apparent_temperature):
    """Map temperature and apparent temperature to a score between 0.0 and 1.0."""
    if isinstance(temperature_2m, pd.Series):
        temp_diff = (temperature_2m - 20.0) / 25.0
        app_diff = (apparent_temperature - 20.0) / 25.0
        score = (temp_diff * 0.5 + app_diff * 0.5).clip(0.0, 1.0)
    else:
        temp_diff = (float(temperature_2m) - 20.0) / 25.0
        app_diff = (float(apparent_temperature) - 20.0) / 25.0
        score = max(0.0, min(1.0, temp_diff * 0.5 + app_diff * 0.5))
        
    return score


def calculate_real_data_targets(df):
    """Calculate observed_rain_hazard_score, observed_exposure_score, and data_driven_weather_impact_score."""
    # observed_rain_hazard_score
    # Uses rain_1h_mm and rain_24h_mm
    rain_1h = df["rain_1h_mm"]
    rain_24 = df["rain_24h_mm"]
    df["observed_rain_hazard_score"] = normalize_series(rain_1h * 0.4 + rain_24 * 0.6)
    
    # observed_exposure_score
    # Uses population_sum (or proxy) and built_surface_mean
    pop_sum = df["population_sum"]
    built_surface = df["built_surface_mean"]
    df["observed_exposure_score"] = normalize_series(pop_sum * 0.6 + built_surface * 0.4)
    
    # data_driven_weather_impact_score
    # Combine hazard, exposure, and vulnerability (low_elevation_score, low_slope_score)
    low_elev = df.get("low_elevation_score", 0.5)
    low_slope = df.get("low_slope_score", 0.5)
    
    impact = (
        df["observed_rain_hazard_score"] * 0.4 +
        df["observed_exposure_score"] * 0.3 +
        low_elev * 0.15 +
        low_slope * 0.15
    )
    df["data_driven_weather_impact_score"] = normalize_series(impact)
    df["target_type"] = "engineered_from_real_observations"
    
    return df
