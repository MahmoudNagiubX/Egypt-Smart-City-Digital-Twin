CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

CREATE TABLE IF NOT EXISTS districts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    city VARCHAR(255),
    country VARCHAR(255),
    geometry GEOMETRY(POLYGON, 4326),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS zones (
    id SERIAL PRIMARY KEY,
    zone_code VARCHAR(50) UNIQUE NOT NULL,
    geometry GEOMETRY(POLYGON, 4326),
    area_m2 DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS road_segments (
    id SERIAL PRIMARY KEY,
    osm_id VARCHAR(100),
    road_name VARCHAR(255),
    road_type VARCHAR(100),
    length_m DOUBLE PRECISION,
    base_speed_kph DOUBLE PRECISION,
    base_travel_time_sec DOUBLE PRECISION,
    geometry GEOMETRY(LINESTRING, 4326),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS emergency_facilities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    facility_type VARCHAR(100),
    source VARCHAR(100),
    geometry GEOMETRY(POINT, 4326),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS weather_records (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    temperature_2m DOUBLE PRECISION,
    relative_humidity_2m DOUBLE PRECISION,
    precipitation DOUBLE PRECISION,
    rain DOUBLE PRECISION,
    wind_speed_10m DOUBLE PRECISION,
    source VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS zone_risk_scores (
    id SERIAL PRIMARY KEY,
    zone_code VARCHAR(50),
    timestamp TIMESTAMP,
    flood_risk DOUBLE PRECISION,
    heat_risk DOUBLE PRECISION,
    traffic_delay_risk DOUBLE PRECISION,
    emergency_delay_risk DOUBLE PRECISION,
    overall_weather_impact_score DOUBLE PRECISION,
    severity VARCHAR(50),
    confidence DOUBLE PRECISION,
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS road_weather_impacts (
    id SERIAL PRIMARY KEY,
    road_segment_id VARCHAR(100),
    timestamp TIMESTAMP,
    rainfall_mm DOUBLE PRECISION,
    flood_penalty DOUBLE PRECISION,
    rain_penalty DOUBLE PRECISION,
    traffic_penalty DOUBLE PRECISION,
    delay_factor DOUBLE PRECISION,
    adjusted_travel_time_sec DOUBLE PRECISION,
    severity VARCHAR(50),
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS emergency_route_results (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    start_lat DOUBLE PRECISION,
    start_lon DOUBLE PRECISION,
    end_lat DOUBLE PRECISION,
    end_lon DOUBLE PRECISION,
    normal_eta_minutes DOUBLE PRECISION,
    weather_safe_eta_minutes DOUBLE PRECISION,
    delay_minutes DOUBLE PRECISION,
    risk_level VARCHAR(50),
    route_geometry GEOMETRY(LINESTRING, 4326),
    avoided_roads JSONB,
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_districts_geom ON districts USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_zones_geom ON zones USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_road_segments_geom ON road_segments USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_facilities_geom ON emergency_facilities USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_emergency_routes_geom ON emergency_route_results USING GIST (route_geometry);
