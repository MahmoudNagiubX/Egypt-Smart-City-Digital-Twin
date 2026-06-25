import { beforeEach, describe, expect, test, vi } from "vitest";

const requestMocks = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
}));

vi.mock("axios", () => ({
  default: {
    create: () => requestMocks,
  },
}));

import { getCustomEmergencyRoute, getPlaces, getLiveWeather, getLiveWeatherRiskLayer, requestLiveEmergencyRoute } from "../api/client";

describe("weather-impact API client", () => {
  beforeEach(() => {
    requestMocks.get.mockReset();
    requestMocks.post.mockReset();
  });

  test("loads places with the supported category query", async () => {
    requestMocks.get.mockResolvedValue({ data: { type: "FeatureCollection", features: [] } });
    await getPlaces("hospital", 25);
    expect(requestMocks.get).toHaveBeenCalledWith("/api/weather-impact/places", {
      params: { category: "hospital", limit: 25 },
    });
  });

  test("posts selected coordinates to the custom emergency route endpoint", async () => {
    const request = {
      origin: { lat: 30.05, lon: 31.35 },
      destination: { lat: 30.07, lon: 31.37 },
      event_type: "top-rain" as const,
      route_preference: "both" as const,
    };
    requestMocks.post.mockResolvedValue({ data: { status: "ok" } });
    await getCustomEmergencyRoute(request);
    expect(requestMocks.post).toHaveBeenCalledWith(
      "/api/weather-impact/routing/custom/emergency-route",
      request,
    );
  });

  test("gets live weather", async () => {
    requestMocks.get.mockResolvedValue({ data: { status: "ok", rain_risk_expected: true } });
    await getLiveWeather();
    expect(requestMocks.get).toHaveBeenCalledWith("/api/weather-impact/weather/live");
  });

  test("gets live weather risk layer", async () => {
    requestMocks.get.mockResolvedValue({ data: { type: "FeatureCollection", features: [] } });
    await getLiveWeatherRiskLayer();
    expect(requestMocks.get).toHaveBeenCalledWith("/api/weather-impact/layers/predictions/live");
  });

  test("posts selected coordinates to request live emergency route", async () => {
    const request = {
      origin: { lat: 30.05, lon: 31.35 },
      destination: { lat: 30.07, lon: 31.37 },
      route_preference: "both" as const,
      refresh_live_weather: false,
    };
    requestMocks.post.mockResolvedValue({ data: { normal_route: {}, weather_safe_route: {} } });
    await requestLiveEmergencyRoute(request);
    expect(requestMocks.post).toHaveBeenCalledWith(
      "/api/weather-impact/routing/live/emergency-route",
      request,
    );
  });
});
