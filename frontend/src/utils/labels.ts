const FIELD_LABELS: Record<string, string> = {
  predicted_risk_class: "Risk Level",
  y_pred: "Predicted Risk",
  risk_reduction_percent: "Risk Reduction",
  eta_tradeoff_percent: "ETA Tradeoff",
  safe_route_available: "Safer Route Available",
  safe_route_quality: "Route Quality",
  avoided_high_risk_segments: "High-Risk Segments Avoided",
  normal_distance_m: "Normal Distance",
  safe_distance_m: "Safe Route Distance",
  normal_weather_eta_sec: "Normal ETA",
  safe_weather_eta_sec: "Safe Route ETA",
  zone_code: "Zone",
  event_id: "Event",
  timestamp: "Time",
  rain_24h_mm: "24h Rainfall",
  population_sum: "Exposed Population",
  built_surface_mean: "Built-Up Density",
};

const EVENT_LABELS: Record<string, string> = {
  evt_0557: "Historic Rain Event",
  evt_dry_009: "Dry Weather Event",
};

const ROUTE_QUALITY_LABELS: Record<string, string> = {
  strong: "Strong improvement",
  accepted: "Safer alternative",
  weak_but_valid: "Limited improvement",
  rejected_identical_routes: "No distinct alternative",
  rejected_negative_risk_reduction: "Normal route preferred",
  pending: "Pending",
};

export function getFieldLabel(field: string): string {
  return FIELD_LABELS[field] ?? "Metric";
}

export function getEventLabel(eventId: unknown): string {
  if (typeof eventId !== "string" || !eventId.trim()) {
    return "Observed Weather Event";
  }
  return EVENT_LABELS[eventId] ?? "Observed Weather Event";
}

export function getZoneLabel(zoneCode: unknown): string {
  if (typeof zoneCode !== "string") {
    return "Zone";
  }
  const match = zoneCode.match(/^NSR-GRID-(\d+)$/i);
  return match ? `Zone ${Number(match[1])}` : "Zone";
}

export function getRouteQualityLabel(quality: unknown): string {
  if (typeof quality !== "string") {
    return ROUTE_QUALITY_LABELS.pending;
  }
  return ROUTE_QUALITY_LABELS[quality] ?? "Route assessed";
}

export function getRiskLevelLabel(level: unknown): string {
  if (typeof level !== "string") {
    return "Not available";
  }
  const labels: Record<string, string> = {
    low: "Low",
    medium: "Medium",
    high: "High",
  };
  return labels[level.toLowerCase()] ?? "Not available";
}

export function getCategoryLabel(category: unknown): string {
  if (typeof category !== "string") {
    return "Point of Interest";
  }
  const labels: Record<string, string> = {
    hospital: "Hospital",
    clinic: "Clinic",
    doctors: "Medical Clinic",
    mosque: "Mosque",
    place_of_worship: "Mosque",
    mall: "Shopping Mall",
    school: "School",
    university: "University",
    police: "Police Station",
    fire_station: "Fire Station",
  };
  return labels[category.toLowerCase()] ?? "Point of Interest";
}
