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
  route_type: "Route Type",
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
  no_distinct_safer_alternative: "No distinct alternative",
  normal_route_preferred: "Normal route preferred",
  pending: "Pending",
};

// Existing API getters
export function getFieldLabel(field: string): string {
  if (FIELD_LABELS[field]) {
    return FIELD_LABELS[field];
  }
  return field
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
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
    emergency: "Emergency Facility",
  };
  return labels[category.toLowerCase()] ?? "Point of Interest";
}

export function getPlaceIcon(category: unknown): string {
  if (typeof category !== "string") {
    return "📍";
  }
  const icons: Record<string, string> = {
    hospital: "🏥",
    clinic: "⚕️",
    doctors: "⚕️",
    mosque: "🕌",
    place_of_worship: "🕌",
    mall: "🛍️",
    school: "🏫",
    university: "🎓",
    police: "🚓",
    fire_station: "🚒",
    emergency: "🚑",
  };
  return icons[category.toLowerCase()] ?? "📍";
}

export function getRouteTypeLabel(routeType: unknown): string {
  return routeType === "weather_safe" || routeType === "safe"
    ? "Weather-Safe Route"
    : "Normal Route";
}

// New required format helpers
export function formatFieldLabel(key: string): string {
  return getFieldLabel(key);
}

export function formatZoneLabel(zoneCode?: string): string {
  return getZoneLabel(zoneCode);
}

export function formatEventLabel(eventId?: string, timestamp?: string): string {
  const label = getEventLabel(eventId);
  if (timestamp) {
    // Format timestamp nicely if it's ISO/JSON string, otherwise output raw
    let displayTime = timestamp;
    try {
      const date = new Date(timestamp);
      if (!isNaN(date.getTime())) {
        displayTime = date.toLocaleString(undefined, {
          month: "short",
          day: "numeric",
          hour: "2-digit",
          minute: "2-digit",
        });
      }
    } catch {
      // fallback to raw timestamp
    }
    return `${label} (${displayTime})`;
  }
  return label;
}

export function formatRiskClass(value?: string): string {
  return getRiskLevelLabel(value);
}

export function formatRouteQuality(value?: string): string {
  if (!value) return "No distinct alternative";
  return getRouteQualityLabel(value);
}

export function getRecommendationLabel(recommendation: unknown): string {
  if (typeof recommendation !== "string") {
    return "Normal Route Acceptable";
  }
  const labels: Record<string, string> = {
    normal_route_acceptable: "Normal Route Acceptable",
    weather_safe_route_recommended: "Weather-Safe Route Recommended",
    no_distinct_safer_alternative: "No Distinct Safer Alternative",
  };
  return labels[recommendation] ?? "Normal Route Acceptable";
}

