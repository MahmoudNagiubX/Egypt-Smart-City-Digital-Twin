import { describe, expect, test } from "vitest";

import {
  getEventLabel,
  getFieldLabel,
  getRouteQualityLabel,
  getPlaceIcon,
  getRouteTypeLabel,
  getZoneLabel,
  formatFieldLabel,
  formatZoneLabel,
  formatEventLabel,
  formatRiskClass,
  formatRouteQuality,
} from "../utils/labels";

describe("human-readable label utilities", () => {
  test("maps route API fields to application labels", () => {
    expect(getFieldLabel("risk_reduction_percent")).toBe("Risk Reduction");
    expect(getFieldLabel("eta_tradeoff_percent")).toBe("ETA Tradeoff");
    expect(getFieldLabel("safe_route_available")).toBe("Safer Route Available");
    expect(getFieldLabel("safe_route_quality")).toBe("Route Quality");
    expect(getFieldLabel("normal_weather_eta_sec")).toBe("Normal ETA");
    expect(getFieldLabel("safe_weather_eta_sec")).toBe("Safe Route ETA");
  });

  test("presents known event and zone identifiers as readable labels", () => {
    expect(getEventLabel("evt_0557")).toBe("Historic Rain Event");
    expect(getEventLabel("evt_dry_009")).toBe("Dry Weather Event");
    expect(getEventLabel("evt_unknown")).toBe("Observed Weather Event");
    expect(getZoneLabel("NSR-GRID-119")).toBe("Zone 119");
  });

  test("maps route quality codes without exposing underscores", () => {
    expect(getRouteQualityLabel("weak_but_valid")).toBe("Limited improvement");
    expect(getRouteQualityLabel("rejected_identical_routes")).toBe("No distinct alternative");
    expect(getRouteTypeLabel("weather_safe")).toBe("Weather-Safe Route");
  });

  test("maps place categories to stable map icons", () => {
    expect(getPlaceIcon("hospital")).toBe("🏥");
    expect(getPlaceIcon("mosque")).toBe("🕌");
    expect(getPlaceIcon("fire_station")).toBe("🚒");
    expect(getPlaceIcon("unknown")).toBe("📍");
  });

  test("new format helpers format labels correctly", () => {
    // 1. labels utility formats field names
    expect(formatFieldLabel("risk_reduction_percent")).toBe("Risk Reduction");
    expect(formatFieldLabel("predicted_risk_class")).toBe("Risk Level");
    expect(formatFieldLabel("some_random_field")).toBe("Some Random Field");

    // 2. formatZoneLabel converts NSR-GRID-119 and NSR-GRID-006 consistently
    expect(formatZoneLabel("NSR-GRID-119")).toBe("Zone 119");
    expect(formatZoneLabel("NSR-GRID-006")).toBe("Zone 6");

    // 3. formatEventLabel handles event labels and timestamps
    expect(formatEventLabel("evt_0557")).toBe("Historic Rain Event");
    expect(formatEventLabel("evt_dry_009", "2026-06-25T00:00:00Z")).toContain("Dry Weather Event");

    // 4. formatRiskClass formats risk classes
    expect(formatRiskClass("high")).toBe("High");
    expect(formatRiskClass("medium")).toBe("Medium");

    // 5. formatRouteQuality formats quality codes
    expect(formatRouteQuality("strong")).toBe("Strong improvement");
    expect(formatRouteQuality("rejected_identical_routes")).toBe("No distinct alternative");
  });
});
