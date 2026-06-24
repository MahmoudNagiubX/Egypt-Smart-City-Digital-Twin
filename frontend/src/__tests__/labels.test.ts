import { describe, expect, test } from "vitest";

import {
  getEventLabel,
  getFieldLabel,
  getRouteQualityLabel,
  getZoneLabel,
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
  });
});
