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

import { getCustomEmergencyRoute, getPlaces } from "../api/client";

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
});
