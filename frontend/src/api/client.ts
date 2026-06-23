import axios from "axios";
import { 
  HealthResponse, 
  SummaryResponse, 
  PredictionMetadata, 
  EventSummary, 
  RouteComparison, 
  FeatureCollection 
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

export const getRoutingStatus = async (): Promise<any> => {
  const response = await api.get<any>(`${API_PREFIX}/routing/status`);
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
