import axios from "axios";
import { 
  HealthResponse, 
  SummaryResponse, 
  PredictionMetadata, 
  EventSummary, 
  RouteComparison, 
  FeatureCollection,
  PlaceCategory,
  PlaceProperties,
  CustomRouteRequest,
  CustomRouteResponse,
  LiveWeatherSummary,
  DailyForecastResponse,
  AirQualityResponse,
  LiveRoutingStatusResponse,
  LiveEmergencyRouteRequest,
  LiveEmergencyRouteResponse,
  SearchResponse,
  ZoneExplanationResponse,
  RouteExplanationResponse,
  ModelExplainabilitySummaryResponse,
  RouteCoordinate,
} from "../types/api";

const BASE_URL = import.meta.env?.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const API_PREFIX = "/api/weather-impact";

const api = axios.create({
  baseURL: `${BASE_URL}`,
});

export const getHealth = async (): Promise<HealthResponse> => {
  const response = await api.get<HealthResponse>(`${API_PREFIX}/health`);
  return response.data;
};

export const getSummary = async (): Promise<SummaryResponse> => {
  const response = await api.get<SummaryResponse>(`${API_PREFIX}/summary`);
  return response.data;
};

export const getPredictionMetadata = async (): Promise<PredictionMetadata> => {
  const response = await api.get<PredictionMetadata>(`${API_PREFIX}/predictions/metadata`);
  return response.data;
};

export const getBoundaryLayer = async (): Promise<FeatureCollection> => {
  const response = await api.get<FeatureCollection>(`${API_PREFIX}/layers/boundary`);
  return response.data;
};

export const getGridLayer = async (): Promise<FeatureCollection> => {
  const response = await api.get<FeatureCollection>(`${API_PREFIX}/layers/grid`);
  return response.data;
};

export const getEmergencyFacilities = async (): Promise<FeatureCollection> => {
  const response = await api.get<FeatureCollection>(`${API_PREFIX}/layers/emergency-facilities`);
  return response.data;
};

export const getPlaces = async (
  category: PlaceCategory = "all",
  limit?: number,
): Promise<FeatureCollection<PlaceProperties>> => {
  const response = await api.get<FeatureCollection<PlaceProperties>>(
    `${API_PREFIX}/places`,
    { params: { category, ...(limit ? { limit } : {}) } },
  );
  return response.data;
};

export const getLatestRiskLayer = async (): Promise<FeatureCollection> => {
  const response = await api.get<FeatureCollection>(`${API_PREFIX}/layers/predictions/latest`);
  return response.data;
};

export const getTopRainRiskLayer = async (): Promise<FeatureCollection> => {
  const response = await api.get<FeatureCollection>(`${API_PREFIX}/layers/predictions/top-rain`);
  return response.data;
};

export const getRiskSummaryLayer = async (): Promise<FeatureCollection> => {
  const response = await api.get<FeatureCollection>(`${API_PREFIX}/layers/risk-summary`);
  return response.data;
};

export const getEvents = async (): Promise<EventSummary[]> => {
  const response = await api.get<EventSummary[]>(`${API_PREFIX}/events`);
  return response.data;
};

export const getEventRiskLayer = async (eventId: string): Promise<FeatureCollection> => {
  const response = await api.get<FeatureCollection>(`${API_PREFIX}/events/${eventId}/risk-layer`);
  return response.data;
};

export const getRoutingStatus = async (): Promise<Record<string, unknown>> => {
  const response = await api.get<Record<string, unknown>>(`${API_PREFIX}/routing/status`);
  return response.data;
};

export const getDemoRoute = async (
  eventType: "top-rain" | "latest", 
  routeType: "normal" | "safe" | "weather_safe"
): Promise<FeatureCollection> => {
  const response = await api.get<FeatureCollection>(
    `${API_PREFIX}/routing/demo/${eventType}/${routeType}`
  );
  return response.data;
};

export const getRouteComparison = async (
  eventType: "top-rain" | "latest"
): Promise<RouteComparison> => {
  const response = await api.get<RouteComparison>(
    `${API_PREFIX}/routing/comparison/${eventType}`
  );
  return response.data;
};

export const getCustomEmergencyRoute = async (
  request: CustomRouteRequest,
): Promise<CustomRouteResponse> => {
  const response = await api.post<CustomRouteResponse>(
    `${API_PREFIX}/routing/custom/emergency-route`,
    request,
  );
  return response.data;
};

export const getLiveWeather = async (): Promise<LiveWeatherSummary> => {
  const response = await api.get<LiveWeatherSummary>(`${API_PREFIX}/weather/live`);
  return response.data;
};

export const getSevenDayForecast = async (): Promise<DailyForecastResponse> => {
  try {
    const response = await axios.get("https://api.open-meteo.com/v1/forecast", {
      params: {
        latitude: 30.0561,
        longitude: 31.33,
        daily: "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max",
        timezone: "Africa/Cairo",
        forecast_days: 7,
      },
      timeout: 12000,
    });
    const daily = response.data?.daily ?? {};
    const dates: string[] = daily.time ?? [];
    return {
      status: "ok",
      source: "Open-Meteo Forecast API",
      location: { name: "Nasr City", lat: 30.0561, lon: 31.33 },
      daily: dates.map((date, index) => ({
        date,
        weather_code: daily.weather_code?.[index] ?? null,
        temperature_2m_max: daily.temperature_2m_max?.[index] ?? null,
        temperature_2m_min: daily.temperature_2m_min?.[index] ?? null,
        precipitation_sum: daily.precipitation_sum?.[index] ?? null,
        precipitation_probability_max: daily.precipitation_probability_max?.[index] ?? null,
      })),
      warnings: [],
    };
  } catch (error) {
    return {
      status: "unavailable",
      source: "Open-Meteo Forecast API",
      location: { name: "Nasr City", lat: 30.0561, lon: 31.33 },
      daily: [],
      warnings: [error instanceof Error ? error.message : "Forecast unavailable."],
    };
  }
};

export const getAirQuality = async (): Promise<AirQualityResponse> => {
  try {
    const response = await axios.get("https://air-quality-api.open-meteo.com/v1/air-quality", {
      params: {
        latitude: 30.0561,
        longitude: 31.33,
        current: "european_aqi,pm10,pm2_5",
        hourly: "european_aqi,pm10,pm2_5",
        timezone: "Africa/Cairo",
        forecast_days: 2,
      },
      timeout: 12000,
    });
    const hourly = response.data?.hourly ?? {};
    const times: string[] = hourly.time ?? [];
    return {
      status: "ok",
      source: "Open-Meteo Air Quality API",
      location: { name: "Nasr City", lat: 30.0561, lon: 31.33 },
      current: {
        time: response.data?.current?.time ?? null,
        european_aqi: response.data?.current?.european_aqi ?? null,
        pm10: response.data?.current?.pm10 ?? null,
        pm2_5: response.data?.current?.pm2_5 ?? null,
      },
      hourly: times.map((time, index) => ({
        time,
        european_aqi: hourly.european_aqi?.[index] ?? null,
        pm10: hourly.pm10?.[index] ?? null,
        pm2_5: hourly.pm2_5?.[index] ?? null,
      })),
      warnings: [],
    };
  } catch (error) {
    return {
      status: "unavailable",
      source: "Open-Meteo Air Quality API",
      location: { name: "Nasr City", lat: 30.0561, lon: 31.33 },
      hourly: [],
      warnings: [error instanceof Error ? error.message : "Air quality unavailable."],
    };
  }
};

export const getLiveWeatherRiskLayer = async (): Promise<FeatureCollection> => {
  const response = await api.get<FeatureCollection>(`${API_PREFIX}/layers/predictions/live`);
  return response.data;
};

export const getLiveWeatherReport = async (): Promise<Record<string, unknown>> => {
  const response = await api.get<Record<string, unknown>>(`${API_PREFIX}/weather/live/report`);
  return response.data;
};

export const getLiveRoutingStatus = async (): Promise<LiveRoutingStatusResponse> => {
  const response = await api.get<LiveRoutingStatusResponse>(`${API_PREFIX}/routing/live/status`);
  return response.data;
};

export const requestLiveEmergencyRoute = async (
  request: LiveEmergencyRouteRequest,
): Promise<LiveEmergencyRouteResponse> => {
  const response = await api.post<LiveEmergencyRouteResponse>(
    `${API_PREFIX}/routing/live/emergency-route`,
    request,
  );
  return response.data;
};

export const searchLocalPlaces = async (
  q: string,
  limit?: number,
  category?: string
): Promise<SearchResponse> => {
  const response = await api.get<SearchResponse>(`${API_PREFIX}/search`, {
    params: { q, ...(limit ? { limit } : {}), ...(category ? { category } : {}) },
  });
  return response.data;
};

export const getZoneExplanation = async (
  zoneCode: string,
  mode: "live" | "historical" = "live",
  eventId?: string
): Promise<ZoneExplanationResponse> => {
  const response = await api.get<ZoneExplanationResponse>(
    `${API_PREFIX}/explain/zone/${zoneCode}`,
    { params: { mode, ...(eventId ? { event_id: eventId } : {}) } }
  );
  return response.data;
};

export const explainRoute = async (
  origin: RouteCoordinate,
  destination: RouteCoordinate,
  mode: string = "live"
): Promise<RouteExplanationResponse> => {
  const response = await api.post<RouteExplanationResponse>(
    `${API_PREFIX}/explain/route`,
    { origin, destination, mode }
  );
  return response.data;
};

export const getModelExplainabilitySummary = async (): Promise<ModelExplainabilitySummaryResponse> => {
  const response = await api.get<ModelExplainabilitySummaryResponse>(
    `${API_PREFIX}/model/explainability-summary`
  );
  return response.data;
};


