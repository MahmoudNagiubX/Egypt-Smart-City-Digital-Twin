import { useCallback, useEffect, useRef, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import {
  getBoundaryLayer,
  getDemoRoute,
  getEventRiskLayer,
  getEvents,
  getGridLayer,
  getHealth,
  getLatestRiskLayer,
  getPlaces,
  getRiskSummaryLayer,
  getRouteComparison,
  getSummary,
  getTopRainRiskLayer,
  getLiveWeather,
  getSevenDayForecast,
  getAirQuality,
  getLiveWeatherRiskLayer,
  getLiveRoutingStatus,
  requestLiveEmergencyRoute,
  getZoneExplanation,
  explainRoute,
} from "../api/client";
import type {
  EventSummary,
  FeatureCollection,
  LayerToggles,
  PlaceProperties,
  RouteComparison,
  RouteCoordinate,
  LiveWeatherSummary,
  DailyForecastResponse,
  AirQualityResponse,
  LiveRoutingStatusResponse,
  SearchResultItem,
  ZoneExplanationResponse,
  RouteExplanationResponse,
} from "../types/api";
import { LayerToggle } from "./LayerToggle";
import { Legend } from "./Legend";
import { ErrorDisplay, LoadingSpinner } from "./LoadingError";
import { MapView } from "./MapView";
import { RoutePanel } from "./RoutePanel";
import { SearchBox } from "./SearchBox";
import { ExplainabilityPanel } from "./ExplainabilityPanel";
import { toFiniteNumber, EMPTY_VALUE } from "../utils/format";
import { getRecommendationLabel } from "../utils/labels";

const formatTemperature = (value: unknown) => {
  const number = toFiniteNumber(value);
  return number === null ? EMPTY_VALUE : `${Math.round(number)}°`;
};

const formatMetric = (value: unknown, suffix: string, digits = 0) => {
  const number = toFiniteNumber(value);
  return number === null ? EMPTY_VALUE : `${number.toFixed(digits)}${suffix}`;
};

const getWeatherCondition = (code: unknown) => {
  const value = Number(code);
  if ([0, 1].includes(value)) return "Clear";
  if ([2, 3].includes(value)) return "Partly cloudy";
  if ([45, 48].includes(value)) return "Hazy";
  if ([51, 53, 55, 56, 57].includes(value)) return "Drizzle";
  if ([61, 63, 65, 66, 67, 80, 81, 82].includes(value)) return "Rain";
  if ([95, 96, 99].includes(value)) return "Thunderstorm";
  return "Weather update";
};

const getWeatherIcon = (code: unknown) => {
  const label = getWeatherCondition(code);
  if (label === "Clear") return "sunny";
  if (label === "Partly cloudy") return "partly_cloudy_day";
  if (label === "Hazy") return "foggy";
  if (label === "Thunderstorm") return "thunderstorm";
  if (label === "Rain" || label === "Drizzle") return "rainy";
  return "partly_cloudy_day";
};

const getWeatherIconColor = (iconName: string) => {
  switch (iconName) {
    case "sunny":
      return "#FFB800"; // Warm golden
    case "partly_cloudy_day":
      return "#42A5F5"; // Soft blue cloud
    case "foggy":
      return "#78909c"; // Blue-gray haze
    case "thunderstorm":
      return "#e0a900"; // Dark yellow lightning/storm accent
    case "rainy":
      return "#0288d1"; // Blue rain cloud
    default:
      return "#42A5F5";
  }
};

const getAqiLabel = (aqi: unknown) => {
  const value = toFiniteNumber(aqi);
  if (value === null) return "Unavailable";
  if (value <= 20) return "Good";
  if (value <= 40) return "Fair";
  if (value <= 60) return "Moderate";
  if (value <= 80) return "Poor";
  if (value <= 100) return "Very poor";
  return "Extremely poor";
};

const buildSparklinePath = (values: number[], width = 132, height = 34) => {
  if (values.length < 2) return "";
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = Math.max(1, max - min);
  return values
    .map((value, index) => {
      const x = (index / (values.length - 1)) * width;
      const y = height - ((value - min) / range) * (height - 4) - 2;
      return `${index === 0 ? "M" : "L"} ${x.toFixed(1)} ${y.toFixed(1)}`;
    })
    .join(" ");
};

type RouteEventType = "top-rain" | "latest";
type RouteVisibility = "normal" | "safe" | "both";

interface RouteSelection {
  origin: RouteCoordinate | null;
  destination: RouteCoordinate | null;
}

interface DashboardProps {
  onGoHome?: () => void;
}

const emptySelection: RouteSelection = { origin: null, destination: null };

const getErrorMessage = (error: unknown, fallback: string) =>
  error instanceof Error && error.message ? error.message : fallback;

export const Dashboard = ({ onGoHome }: DashboardProps) => {
  const prefersReducedMotion = useReducedMotion();
  const safeRouteTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const [mapMode, setMapMode] = useState<"today" | "history">("today");
  const [events, setEvents] = useState<EventSummary[]>([]);
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);
  const [riskFillOpacity, setRiskFillOpacity] = useState(0.28);
  const [gridLineOpacity, setGridLineOpacity] = useState(0.08);
  const [routeEventType, setRouteEventType] = useState<RouteEventType>("top-rain");
  const [routeVisibility, setRouteVisibility] = useState<RouteVisibility>("both");
  const [routeSelection, setRouteSelection] = useState<RouteSelection>(emptySelection);
  const [routingLoading, setRoutingLoading] = useState(false);
  const [routingError, setRoutingError] = useState<string | null>(null);
  const [routeSource, setRouteSource] = useState<"demo" | "custom" | "custom-live">("custom-live");
  const [searchSelectedPoint, setSearchSelectedPoint] = useState<SearchResultItem | null>(null);
  const [liveWeather, setLiveWeather] = useState<LiveWeatherSummary | null>(null);
  const [dailyForecast, setDailyForecast] = useState<DailyForecastResponse | null>(null);
  const [airQuality, setAirQuality] = useState<AirQualityResponse | null>(null);
  const [liveRoutingStatus, setLiveRoutingStatus] = useState<LiveRoutingStatusResponse | null>(null);
  const [liveRiskData, setLiveRiskData] = useState<FeatureCollection | null>(null);
  const [riskDisplayMode, setRiskDisplayMode] = useState<"focus" | "all">("focus");
  const [showControlsDrawer, setShowControlsDrawer] = useState(false);

  const [layers, setLayers] = useState<LayerToggles>({
    boundary: true,
    grid: false,
    roadsLabels: true,
    hospitals: true,       // Default visible
    clinics: false,        // Default hidden
    mosques: false,        // Default hidden
    malls: false,          // Default hidden
    schools: false,        // Default hidden
    universities: false,   // Default hidden
    police: false,         // Default hidden
    fireStations: false,   // Default hidden
    emergency: true,       // Default visible
    latestRisk: false,
    topRainRisk: false,
    riskSummary: false,
    selectedRisk: false,
    liveRisk: true,
  });

  const [boundaryData, setBoundaryData] = useState<FeatureCollection | null>(null);
  const [gridData, setGridData] = useState<FeatureCollection | null>(null);
  const [placesData, setPlacesData] = useState<FeatureCollection<PlaceProperties> | null>(null);
  const [emergencyPlaceIds, setEmergencyPlaceIds] = useState<Set<string>>(new Set());
  const [latestRiskData, setLatestRiskData] = useState<FeatureCollection | null>(null);
  const [topRainRiskData, setTopRainRiskData] = useState<FeatureCollection | null>(null);
  const [riskSummaryData, setRiskSummaryData] = useState<FeatureCollection | null>(null);
  const [selectedEventRiskData, setSelectedEventRiskData] = useState<FeatureCollection | null>(null);
  const [normalRouteData, setNormalRouteData] = useState<FeatureCollection | null>(null);
  const [safeRouteData, setSafeRouteData] = useState<FeatureCollection | null>(null);
  const [comparison, setComparison] = useState<RouteComparison | null>(null);

  const [selectedZoneCode, setSelectedZoneCode] = useState<string | null>(null);
  const [zoneExplanation, setZoneExplanation] = useState<ZoneExplanationResponse | null>(null);
  const [zoneLoading, setZoneLoading] = useState(false);
  const [routeExplanation, setRouteExplanation] = useState<RouteExplanationResponse | null>(null);
  const [routeLoading, setRouteLoading] = useState(false);
  const [explainActiveTab, setExplainActiveTab] = useState<"area" | "route" | "model">("area");
  const [isRoutePlanningActive, setIsRoutePlanningActive] = useState(false);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        setLoading(true);
        const [
          _healthResponse,
          _summaryResponse,
          eventsResponse,
          boundaryResponse,
          gridResponse,
          placesResponse,
          emergencyResponse,
          latestRiskResponse,
          topRainRiskResponse,
          riskSummaryResponse,
        ] = await Promise.all([
          getHealth(),
          getSummary(),
          getEvents(),
          getBoundaryLayer(),
          getGridLayer(),
          getPlaces(),
          getPlaces("emergency"),
          getLatestRiskLayer(),
          getTopRainRiskLayer(),
          getRiskSummaryLayer(),
        ]);

        setEvents(eventsResponse);
        setBoundaryData(boundaryResponse);
        setGridData(gridResponse);
        setPlacesData(placesResponse);
        setEmergencyPlaceIds(
          new Set(emergencyResponse.features.map((feature) => feature.properties.place_id)),
        );
        setLatestRiskData(latestRiskResponse);
        setTopRainRiskData(topRainRiskResponse);
        setRiskSummaryData(riskSummaryResponse);
        if (eventsResponse.length > 0) {
          setSelectedEventId(eventsResponse[0].event_id);
        }

        // Fetch live weather data separately without blocking dashboard if it fails
        try {
          const [liveWeatherRes, liveRoutingStatusRes, liveRiskRes, forecastRes, airQualityRes] = await Promise.all([
            getLiveWeather(),
            getLiveRoutingStatus(),
            getLiveWeatherRiskLayer(),
            getSevenDayForecast(),
            getAirQuality(),
          ]);
          setLiveWeather(liveWeatherRes);
          setLiveRoutingStatus(liveRoutingStatusRes);
          setLiveRiskData(liveRiskRes);
          setDailyForecast(forecastRes);
          setAirQuality(airQualityRes);
        } catch (liveWeatherError) {
          console.warn("Failed to load live weather/routing info:", liveWeatherError);
        }

      } catch (initialError) {
        setError(
          getErrorMessage(
            initialError,
            "Failed to load dashboard data from the local backend.",
          ),
        );
      } finally {
        setLoading(false);
      }
    };

    void fetchInitialData();
  }, []);

  useEffect(() => {
    if (!selectedEventId) return;
    let cancelled = false;
    const fetchSelectedEventRisk = async () => {
      try {
        const riskResponse = await getEventRiskLayer(selectedEventId);
        if (!cancelled) {
          setSelectedEventRiskData(riskResponse);
          setLayers((current) => ({ ...current, selectedRisk: true }));
        }
      } catch (selectedRiskError) {
        console.error("Failed to load selected event risk layer:", selectedRiskError);
      }
    };
    void fetchSelectedEventRisk();
    return () => {
      cancelled = true;
    };
  }, [selectedEventId]);

  useEffect(() => {
    if (mapMode !== "history") {
      setNormalRouteData(null);
      setSafeRouteData(null);
      setComparison(null);
      return;
    }
    if (routeSelection.origin) return;
    let cancelled = false;
    const fetchDemoRouting = async () => {
      try {
        const [normalRoute, safeRoute, routeComparison] = await Promise.all([
          getDemoRoute(routeEventType, "normal"),
          getDemoRoute(routeEventType, "safe"),
          getRouteComparison(routeEventType),
        ]);
        if (!cancelled) {
          setNormalRouteData(normalRoute);
          setSafeRouteData(safeRoute);
          setComparison(routeComparison);
          setRouteSource("demo");
          setRoutingError(null);
        }
      } catch (demoRouteError) {
        console.error("Failed to load routing data:", demoRouteError);
      }
    };
    void fetchDemoRouting();
    return () => {
      cancelled = true;
    };
  }, [mapMode, routeEventType, routeSelection.origin]);

  useEffect(() => {
    const { origin, destination } = routeSelection;
    if (!origin || !destination) return;
    let cancelled = false;

    const fetchCustomRoute = async () => {
      setRoutingLoading(true);
      setRoutingError(null);
      setRouteSource("custom-live");
      setComparison(null);
      setNormalRouteData(null);
      setSafeRouteData(null);
      setRouteExplanation(null);
      try {
        const response = await requestLiveEmergencyRoute({
          origin,
          destination,
          route_preference: "both",
          refresh_live_weather: false,
        });
        if (cancelled) return;

        if (safeRouteTimerRef.current) {
          clearTimeout(safeRouteTimerRef.current);
        }
        setNormalRouteData(response.normal_route);
        setSafeRouteData(null);
        setComparison({
          ...response.comparison,
          recommendation: response.recommendation,
          rain_risk_expected: response.rain_risk_expected,
          live_weather_summary: response.live_weather_summary,
          event_type: "live",
          selected_destination_facility_name: "Selected map point",
          honesty_note: response.honesty_note,
        } as any);
        setRouteVisibility("both");

        safeRouteTimerRef.current = setTimeout(
          () => !cancelled && setSafeRouteData(response.weather_safe_route),
          prefersReducedMotion ? 0 : 360,
        );
      } catch (customRouteError) {
        if (!cancelled) {
          setNormalRouteData(null);
          setSafeRouteData(null);
          setComparison(null);
          setRoutingError(
            getErrorMessage(customRouteError, "A route could not be calculated for those points."),
          );
        }
      } finally {
        if (!cancelled) setRoutingLoading(false);
      }
    };

    void fetchCustomRoute();
    return () => {
      cancelled = true;
      if (safeRouteTimerRef.current) clearTimeout(safeRouteTimerRef.current);
    };
  }, [prefersReducedMotion, routeEventType, routeSelection]);

  const resetCustomRoute = useCallback(() => {
    if (safeRouteTimerRef.current) clearTimeout(safeRouteTimerRef.current);
    setRouteSelection(emptySelection);
    setSearchSelectedPoint(null);
    setRoutingLoading(false);
    setRoutingError(null);
    setNormalRouteData(null);
    setSafeRouteData(null);
    setComparison(null);
    setRouteSource(mapMode === "today" ? "custom-live" : "demo");
    setRouteExplanation(null);
    setIsRoutePlanningActive(false);
  }, [mapMode]);

  const handleSetStartPoint = useCallback((coordinate: RouteCoordinate) => {
    if (safeRouteTimerRef.current) clearTimeout(safeRouteTimerRef.current);
    setRouteSelection(prev => ({ origin: coordinate, destination: prev.destination }));
    setRouteSource("custom");
    setRoutingError(null);
    setIsRoutePlanningActive(true);
  }, []);

  const handleSetDestinationPoint = useCallback((coordinate: RouteCoordinate) => {
    if (!routeSelection.origin) {
      setRoutingError("Start point selected first, then choose destination.");
      return;
    }
    setRouteSelection(prev => ({ origin: prev.origin, destination: coordinate }));
  }, [routeSelection.origin]);

  const handleZoneClick = useCallback(
    (zoneCode: string, eventId?: string | null) => {
      if (!zoneCode) {
        setExplainActiveTab("area");
        setZoneExplanation({
          status: "error",
          zone_code: "",
          zone_label: "Unknown Area",
          mode: mapMode === "history" ? "historical" : "live",
          risk_score: 0,
          risk_class: "low",
          risk_label: "No Risk",
          summary: "This zone cannot be explained because it has no zone identifier.",
          top_factors: [],
          explanation_text: "Missing zone code identifier.",
          confidence_note: "Decision-support estimate only. Not an official flood report.",
          honesty_note: "Decision-support estimate only. Not an official flood report."
        });
        return;
      }

      setSelectedZoneCode(zoneCode);
      setExplainActiveTab("area");
      setZoneLoading(true);
      setZoneExplanation(null);

      const mode = mapMode === "history" ? "historical" : "live";
      const evtId = mapMode === "history" ? (eventId || selectedEventId || undefined) : undefined;

      getZoneExplanation(zoneCode, mode, evtId)
        .then((res) => {
          setZoneExplanation(res);
        })
        .catch((err) => {
          console.error("Failed to load zone explanation:", err);
          setZoneExplanation({
            status: "error",
            zone_code: zoneCode,
            zone_label: "Unknown Zone",
            mode,
            risk_score: 0,
            risk_class: "low",
            risk_label: "No Risk",
            summary: "This zone cannot be explained because it has no zone identifier or the explanation request failed.",
            top_factors: [],
            explanation_text: "Request failed.",
            confidence_note: "Decision-support estimate only. Not an official flood report.",
            honesty_note: "Decision-support estimate only. Not an official flood report."
          });
        })
        .finally(() => {
          setZoneLoading(false);
        });
    },
    [mapMode, selectedEventId],
  );

  const handleWhyThisRouteClick = useCallback(() => {
    const { origin, destination } = routeSelection;
    if (!origin || !destination) return;

    setExplainActiveTab("route");
    setRouteLoading(true);
    setRouteExplanation(null);

    const mode = mapMode === "history" ? "historical" : "live";

    explainRoute(origin, destination, mode)
      .then((res) => {
        setRouteExplanation(res);
      })
      .catch((err) => {
        console.error("Failed to load route explanation:", err);
      })
      .finally(() => {
        setRouteLoading(false);
      });
  }, [routeSelection, mapMode]);

  const handleMapModeChange = useCallback((mode: "today" | "history") => {
    setMapMode(mode);
    if (safeRouteTimerRef.current) clearTimeout(safeRouteTimerRef.current);
    setRouteSelection(emptySelection);
    setRoutingLoading(false);
    setRoutingError(null);
    setNormalRouteData(null);
    setSafeRouteData(null);
    setComparison(null);
    setRouteSource(mode === "today" ? "custom-live" : "demo");
    setRouteExplanation(null);
    setIsRoutePlanningActive(false);
    setSelectedZoneCode(null);
    setZoneExplanation(null);

    // Automatically toggle active layers
    setLayers((current) => ({
      ...current,
      liveRisk: mode === "today",
      selectedRisk: mode === "history",
      latestRisk: false,
      topRainRisk: false,
      riskSummary: false,
    }));
  }, []);

  const handleMapPointClick = useCallback(
    (coordinate: RouteCoordinate) => {
      if (routingLoading) return;
      if (routeSelection.origin && routeSelection.destination) {
        resetCustomRoute();
        return;
      }
      if (!routeSelection.origin) {
        if (safeRouteTimerRef.current) clearTimeout(safeRouteTimerRef.current);
        setRouteSelection({ origin: coordinate, destination: null });
        setRouteSource("custom");
        setRoutingError(null);
        setNormalRouteData(null);
        setSafeRouteData(null);
        setComparison(null);
        return;
      }
      setRouteSelection({ origin: routeSelection.origin, destination: coordinate });
    },
    [resetCustomRoute, routeSelection, routingLoading],
  );

  const handleToggleLayer = (key: keyof LayerToggles) => {
    setLayers((current) => ({ ...current, [key]: !current[key] }));
  };

  const selectionState = routingLoading
    ? "loading"
    : routeSelection.destination
      ? "ready"
      : routeSelection.origin
        ? "selecting-destination"
        : "idle";

  if (loading) {
    return (
      <div className="stitch-page flex h-screen w-screen flex-col items-center justify-center">
        <h1 className="sr-only">Egypt Smart City Digital Twin</h1>
        <LoadingSpinner message="Synchronizing map layers, places, and weather-aware routes..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="stitch-page flex h-screen w-screen items-center justify-center p-6">
        <div className="w-full max-w-lg"><ErrorDisplay message={error} /></div>
      </div>
    );
  }

  // Derive alert status for the map overlay pill
  const hasActiveAlerts = liveRoutingStatus?.status !== "ok";
  const currentWeatherIcon = liveWeather
    ? getWeatherIcon(liveWeather.current?.weather_code)
    : "partly_cloudy_day";
  const aqiValue = airQuality?.current?.european_aqi ?? null;
  const aqiLabel = getAqiLabel(aqiValue);
  const aqiTrendValues = (airQuality?.hourly ?? [])
    .map((item) => toFiniteNumber(item.european_aqi))
    .filter((value): value is number => value !== null)
    .slice(0, 24);
  const aqiSparklinePath = buildSparklinePath(aqiTrendValues);

  // Compute KPI values for the stacked bottom cards
  // 1. Today’s Rain Risk / Rain Risk
  let rainRiskLabel = mapMode === "today" ? "Today’s Rain Risk" : "Rain Risk";
  let rainRiskValue = "Low";
  let rainRiskTone: "low" | "medium" | "high" = "low";

  if (mapMode === "today") {
    if (liveWeather) {
      rainRiskValue = liveWeather.rain_risk_expected ? "Expected" : "No Rain Risk";
      rainRiskTone = liveWeather.rain_risk_expected ? "medium" : "low";
    } else {
      rainRiskValue = "—";
      rainRiskTone = "low";
    }
  } else {
    rainRiskValue = "Expected";
    rainRiskTone = "medium";
  }

  // 2. Rain Probability
  let probValue = "—";
  if (mapMode === "today") {
    if (liveWeather?.forecast_window) {
      probValue = `${Math.round(liveWeather.forecast_window.max_precipitation_probability ?? 0)}%`;
    }
  } else {
    probValue = comparison ? "95%" : "—";
  }

  // 3. Route Recommendation
  let recValue = "Waiting for route";
  let recTone: "blue" | "low" | "medium" = "blue";
  if (comparison) {
    if (mapMode === "today") {
      const rec = (comparison as any).recommendation;
      recValue = getRecommendationLabel(rec);
      recTone = rec === "weather_safe_route_recommended" ? "low" : "medium";
    } else {
      recValue = comparison.safe_route_available ? "Safer Route Available" : "Normal Route Recommended";
      recTone = comparison.safe_route_available ? "low" : "medium";
    }
  }

  // 4. Risk Reduction
  let reductionValue = "—";
  if (comparison) {
    reductionValue = `${(comparison.risk_reduction_percent ?? 0).toFixed(0)}%`;
  }

  return (
    <div
      className="stitch-page flex items-center justify-center h-screen w-screen overflow-hidden"
      style={{ padding: '0.5rem' }}
    >
      {/* Atmospheric background blobs */}
      <div className="stitch-bg-cloud-1" aria-hidden="true" />
      <div className="stitch-bg-cloud-2" aria-hidden="true" />

      {/* Dashboard Shell */}
      <div
        className="stitch-dashboard-shell"
        style={{ margin: '0 auto', height: 'calc(100vh - 1rem)', maxHeight: 1080 }}
      >
        <h1 className="sr-only">Egypt Smart City Digital Twin</h1>
        {/* Stitch Top Navigation Bar */}
        <nav
          className="flex items-center justify-between px-6 py-3 border-b border-glass-border bg-white/40"
          style={{ height: 60, flexShrink: 0 }}
        >
          {/* Left: Brand + Nav tabs */}
          <div className="flex items-center gap-8">
            <button
              onClick={onGoHome}
              className="flex items-center gap-1 font-headline-md text-base font-bold tracking-tight text-text-charcoal cursor-pointer border-none bg-transparent"
              title="Back to home"
            >
              <span>Geo</span>
              <span className="text-tertiary-container text-xs material-symbols-outlined font-variation-settings-['FILL'_1] text-[#ff9e2a] leading-none" style={{ fontVariationSettings: "'FILL' 1" }}>
                fiber_manual_record
              </span>
              <span>Weather</span>
            </button>
            <div className="hidden lg:flex items-center gap-6 text-xs font-semibold text-text-muted">
              <span className="text-[#006688] border-b-2 border-[#006688] pb-1 cursor-default">Overview</span>
              <span className="hover:text-text-charcoal transition-colors cursor-default">Weather Map</span>
              <span className="hover:text-text-charcoal transition-colors cursor-default">Station Logs</span>
              <span className="hover:text-text-charcoal transition-colors cursor-default">Alerts</span>
            </div>
          </div>
          {/* Center: Search */}
          <div className="hidden md:flex flex-1 max-w-sm mx-6">
            <SearchBox
              onSelectResult={setSearchSelectedPoint}
              selectedResult={searchSelectedPoint}
              onSetStart={handleSetStartPoint}
              onSetDestination={handleSetDestinationPoint}
              onClear={() => setSearchSelectedPoint(null)}
              variant="nav"
            />
          </div>
          {/* Right: Actions & Profile */}
          <div className="flex items-center gap-4 text-xs">
            <div className="hidden md:flex items-center gap-1.5 text-text-muted">
              <span className="material-symbols-outlined text-[16px]">sync</span>
              <span>Synced 2 min ago</span>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1 font-medium text-text-muted">
                <span className="material-symbols-outlined text-[16px]">thermostat</span>
                <span>C/F</span>
              </div>
              <button className="relative text-text-muted hover:text-text-charcoal bg-transparent border-none cursor-pointer p-0 flex items-center">
                <span className="material-symbols-outlined text-lg">notifications</span>
                <span className="absolute top-0 right-0 w-1.5 h-1.5 bg-[#FF7A00] rounded-full"></span>
              </button>
              <div 
                className="w-7 h-7 rounded-full bg-[#006688] border border-white/50 text-white flex items-center justify-center font-bold text-[10px]"
                title="User Profile"
              >
                MN
              </div>
            </div>
          </div>
        </nav>

        {/* Dashboard Body */}
        <div className="flex-1 overflow-hidden p-4 flex flex-col gap-4">
          {/* Live Update & Location Row */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-2 text-xs">
              <span className="font-bold text-[#006688]">LIVE UPDATE:</span>
              <span className="text-text-charcoal">
                {liveWeather?.warnings && liveWeather.warnings.length > 0 
                  ? liveWeather.warnings[0] 
                  : (liveWeather?.rain_risk_expected 
                      ? "Upcoming: Heavy rain predicted (Local)." 
                      : "No immediate storm threat detected.")}
              </span>
              <a className="text-text-muted hover:text-[#006688] underline decoration-text-muted/50 underline-offset-2" href="#" onClick={e => e.preventDefault()}>See Forecast →</a>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1 text-xs font-semibold text-text-charcoal">
                <span className="material-symbols-outlined text-base">location_on</span>
                <span>Nasr City, Cairo</span>
              </div>
              <button 
                onClick={() => {
                  alert("Weather routing report generated. Downloading...");
                }}
                className="bg-[#c2e8ff] hover:bg-[#006688] hover:text-white text-[#004d67] px-4 py-1.5 rounded-lg text-xs font-semibold hover:bg-primary transition-colors flex items-center gap-2 shadow-sm border border-[#006688]/10 cursor-pointer"
              >
                <span className="material-symbols-outlined text-[18px]">download</span>
                Export
              </button>
            </div>
          </div>

          {/* Main 12-Column Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 h-full min-h-0">
            {/* Left 9 columns: Map Card, Bottom Analytics */}
            <div className="lg:col-span-9 flex flex-col gap-4 min-h-0">

              {/* Map Card */}
              <div className="relative w-full h-[400px] lg:flex-1 rounded-[16px] overflow-hidden border border-white/60 shadow-sm bg-[#e8f1f8] stitch-map-frame">
                {/* Alerts overlay pill */}
                <div
                  style={{
                    position: 'absolute',
                    top: 12,
                    left: 12,
                    zIndex: 15,
                    background: 'rgba(255,255,255,0.85)',
                    backdropFilter: 'blur(10px)',
                    borderRadius: 999,
                    padding: '6px 14px',
                    border: '1px solid rgba(255,255,255,0.6)',
                    fontSize: 11,
                    fontWeight: 600,
                    color: hasActiveAlerts ? 'var(--stitch-alert-orange)' : 'var(--stitch-secondary)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 6,
                  }}
                >
                  {hasActiveAlerts ? '⚠️ Active Weather Alerts' : '✓ Live monitoring active'}
                </div>

                {/* Secondary Hint */}
                <div
                  style={{
                    position: 'absolute',
                    top: 50,
                    left: 12,
                    zIndex: 15,
                    background: 'rgba(255,255,255,0.7)',
                    backdropFilter: 'blur(8px)',
                    borderRadius: 999,
                    padding: '4px 10px',
                    border: '1px solid rgba(255,255,255,0.5)',
                    fontSize: 9.5,
                    fontWeight: 500,
                    color: 'var(--stitch-text-muted)',
                  }}
                >
                  💡 Click a zone for explanation
                </div>

                {/* Controls drawer toggle button */}
                <button
                  id="controls-drawer-toggle"
                  onClick={() => setShowControlsDrawer(d => !d)}
                  className="stitch-pill"
                  style={{
                    position: 'absolute',
                    top: 12,
                    right: 60,
                    zIndex: 15,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 6,
                    padding: '6px 14px',
                    fontSize: 12,
                    fontWeight: 600,
                    color: 'var(--stitch-text-charcoal)',
                    cursor: 'pointer',
                    border: 'none',
                  }}
                >
                  ≡ Controls
                </button>

                {/* Controls drawer (slides in from left) */}
                <AnimatePresence>
                  {showControlsDrawer && (
                    <motion.div
                      initial={prefersReducedMotion ? false : { x: -300, opacity: 0 }}
                      animate={{ x: 0, opacity: 1 }}
                      exit={prefersReducedMotion ? undefined : { x: -300, opacity: 0 }}
                      transition={{ duration: 0.22, ease: "easeOut" }}
                      className="stitch-glass"
                      style={{
                        position: 'absolute',
                        top: 12,
                        left: 12,
                        bottom: 12,
                        width: 300,
                        zIndex: 20,
                        padding: '1.25rem',
                        borderRadius: '20px',
                        overflowY: 'auto',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '1rem',
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                        <span style={{ fontWeight: 700, fontSize: 13, color: 'var(--stitch-text-charcoal)' }}>Map Controls</span>
                        <button
                          onClick={() => setShowControlsDrawer(false)}
                          style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: 16, color: 'var(--stitch-text-muted)' }}
                        >✕</button>
                      </div>
                      <LayerToggle
                        mapMode={mapMode}
                        onMapModeChange={handleMapModeChange}
                        selectionState={selectionState}
                        routingError={routingError}
                        onResetRoute={resetCustomRoute}
                        layers={layers}
                        onToggle={handleToggleLayer}
                        riskFillOpacity={riskFillOpacity}
                        setRiskFillOpacity={setRiskFillOpacity}
                        gridLineOpacity={gridLineOpacity}
                        setGridLineOpacity={setGridLineOpacity}
                        events={events}
                        selectedEventId={selectedEventId}
                        onSelectEvent={setSelectedEventId}
                        riskDisplayMode={riskDisplayMode}
                        setRiskDisplayMode={setRiskDisplayMode}
                        placesData={placesData}
                      />
                      <Legend />
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* MapView */}
                <MapView
                  layers={layers}
                  routeVisibility={routeVisibility}
                  boundaryData={boundaryData}
                  gridData={gridData}
                  placesData={placesData}
                  emergencyPlaceIds={emergencyPlaceIds}
                  latestRiskData={latestRiskData}
                  topRainRiskData={topRainRiskData}
                  riskSummaryData={riskSummaryData}
                  selectedEventRiskData={selectedEventRiskData}
                  liveRiskData={liveRiskData}
                  normalRouteData={normalRouteData}
                  safeRouteData={safeRouteData}
                  routeComparison={comparison}
                  routeOrigin={routeSelection.origin}
                  routeDestination={routeSelection.destination}
                  routingLoading={routingLoading}
                  routingError={routingError}
                  onMapPointClick={handleMapPointClick}
                  onResetRoute={resetCustomRoute}
                  riskFillOpacity={riskFillOpacity}
                  gridLineOpacity={gridLineOpacity}
                  riskDisplayMode={riskDisplayMode}
                  searchSelectedPoint={searchSelectedPoint}
                  onSetStartPoint={handleSetStartPoint}
                  onSetDestinationPoint={handleSetDestinationPoint}
                  onZoneClick={handleZoneClick}
                  selectedZoneCode={selectedZoneCode}
                  isRoutePlanningActive={isRoutePlanningActive}
                />

                {/* Route Planner Floating Card Over Map */}
                <AnimatePresence mode="wait">
                  {isRoutePlanningActive && (
                    <motion.div
                      key={`${routeSource}-${selectionState}`}
                      initial={prefersReducedMotion ? false : { opacity: 0, x: 14 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={prefersReducedMotion ? undefined : { opacity: 0, x: 8 }}
                      transition={{ duration: 0.2, ease: "easeOut" }}
                      className="absolute bottom-4 right-4 z-10 hidden w-[23rem] max-h-[calc(100%-2rem)] overflow-y-auto sm:block"
                    >
                      <RoutePanel
                        comparison={comparison}
                        eventType={routeEventType}
                        onEventTypeChange={setRouteEventType}
                        routeVisibility={routeVisibility}
                        onRouteVisibilityChange={setRouteVisibility}
                        selectionState={selectionState}
                        routeSource={routeSource}
                        routingError={routingError}
                        onResetRoute={resetCustomRoute}
                        onWhyThisRoute={handleWhyThisRouteClick}
                        isRoutePlanningActive={isRoutePlanningActive}
                        onToggleRoutePlanning={setIsRoutePlanningActive}
                      />
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              {/* Bottom Analytics Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 shrink-0">
                {/* 1. Regional Extremes Card */}
                <div className="stitch-card flex flex-col justify-between p-4 relative h-full">
                  <div className="flex items-center justify-between mb-2">
                    <span className="stitch-label-sm text-[10px] text-text-muted font-bold tracking-wider uppercase">Regional Extremes</span>
                    <span className="material-symbols-outlined text-[16px] text-text-muted">thermostat</span>
                  </div>
                  <div className="flex-1 flex flex-col gap-2 mt-1">
                    <div className="flex justify-between items-center text-[11.5px]">
                      <span className="text-text-muted">Max Wind Gust</span>
                      <span className="font-bold text-text-charcoal font-sans">
                        {liveWeather?.current?.wind_speed_10m != null 
                          ? `${liveWeather.current.wind_speed_10m.toFixed(1)} km/h` 
                          : "—"}
                      </span>
                    </div>
                    <div className="flex justify-between items-center text-[11.5px] border-t border-white/10 pt-1.5">
                      <span className="text-text-muted">Expected Rain</span>
                      <span className="font-bold text-text-charcoal font-sans">
                        {liveWeather?.forecast_window?.rain_24h_mm != null 
                          ? `${liveWeather.forecast_window.rain_24h_mm.toFixed(1)} mm` 
                          : "—"}
                      </span>
                    </div>
                    <div className="flex justify-between items-center text-[11.5px] border-t border-white/10 pt-1.5">
                      <span className="text-text-muted">High-Risk Zones</span>
                      <span className={`font-bold font-sans ${liveRoutingStatus?.risk_class_counts?.high ? "text-[#ba1a1a]" : "text-text-charcoal"}`}>
                        {liveRoutingStatus?.risk_class_counts?.high ?? 0} active
                      </span>
                    </div>
                    <div className="flex justify-between items-center text-[11.5px] border-t border-white/10 pt-1.5">
                      <span className="text-text-muted">Alert Summary</span>
                      <span className="font-semibold text-text-charcoal text-right text-[10px] truncate max-w-[120px]">
                        {liveWeather?.rain_risk_expected ? "Heavy Precipitation Alert" : "Normal Local Weather"}
                      </span>
                    </div>
                  </div>
                </div>

                {/* 2. Composite Card 1: Today’s Rain Risk & Rain Probability */}
                <div className="stitch-card flex flex-col justify-between p-4 relative h-full">
                  <div className="flex items-center justify-between mb-2">
                    <span className="stitch-label-sm text-[10px] text-text-muted font-bold tracking-wider uppercase">Rain & Risk Profile</span>
                    <span className="material-symbols-outlined text-[16px] text-text-muted">umbrella</span>
                  </div>
                  <div className="flex-1 flex flex-col gap-2 mt-1">
                    {/* Sub-item 1: Today's Rain Risk */}
                    <div className="flex flex-col gap-0.5">
                      <span className="text-[9px] text-text-muted font-bold uppercase">
                        {rainRiskLabel}
                      </span>
                      <div className="flex items-center justify-between mt-0.5">
                        <span className="font-bold text-text-charcoal text-xs">
                          {rainRiskValue}
                        </span>
                        <span className={`text-[8.5px] font-bold rounded-full px-1.5 py-0.5 shrink-0 ${
                          rainRiskTone === "medium" ? "bg-[#ffdcbe] text-[#ff9e2a]" :
                          "bg-[#83fba5]/30 text-[#006d36]"
                        }`}>
                          {rainRiskTone.toUpperCase()}
                        </span>
                      </div>
                    </div>
                    {/* Sub-item 2: Rain Probability */}
                    <div className="flex flex-col gap-0.5 border-t border-white/10 pt-1.5">
                      <span className="text-[9px] text-text-muted font-bold uppercase">Rain Probability</span>
                      <span className="font-bold text-text-charcoal text-xs font-sans mt-0.5">
                        {probValue}
                      </span>
                    </div>
                  </div>
                </div>

                {/* 3. Composite Card 2: Route Recommendation & Risk Reduction */}
                <div className="stitch-card flex flex-col justify-between p-4 relative h-full">
                  <div className="flex items-center justify-between mb-2">
                    <span className="stitch-label-sm text-[10px] text-text-muted font-bold tracking-wider uppercase">Route Safety</span>
                    <span className="material-symbols-outlined text-[16px] text-text-muted">shield</span>
                  </div>
                  <div className="flex-1 flex flex-col gap-2 mt-1">
                    {/* Sub-item 1: Route Recommendation */}
                    <div className="flex flex-col gap-0.5">
                      <span className="text-[9px] text-text-muted font-bold uppercase">Recommendation</span>
                      <div className="flex items-center justify-between gap-1 mt-0.5">
                        <span className="font-semibold text-text-charcoal text-[11px] truncate max-w-[110px]" title={recValue}>
                          {recValue}
                        </span>
                        <span className={`text-[8.5px] font-bold rounded-full px-1.5 py-0.5 shrink-0 ${
                          recTone === "low" ? "bg-[#83fba5]/30 text-[#006d36]" :
                          recTone === "medium" ? "bg-[#ffdcbe] text-[#ff9e2a]" :
                          "bg-[#c2e8ff]/40 text-[#006688]"
                        }`}>
                          {recTone.toUpperCase()}
                        </span>
                      </div>
                    </div>
                    {/* Sub-item 2: Risk Reduction */}
                    <div className="flex flex-col gap-0.5 border-t border-white/10 pt-1.5">
                      <span className="text-[9px] text-text-muted font-bold uppercase">Risk Reduction</span>
                      <span className="font-bold text-[#006688] text-xs font-sans mt-0.5">
                        {reductionValue}
                      </span>
                    </div>
                  </div>
                </div>

                {/* 4. Safety Guidance Card */}
                <div className="stitch-card flex flex-col justify-between p-4 relative h-full">
                  <div className="flex items-center justify-between mb-2">
                    <span className="stitch-label-sm text-[10px] text-text-muted font-bold tracking-wider uppercase">Safety Guidance</span>
                    <span className="material-symbols-outlined text-[16px] text-text-muted">security</span>
                  </div>
                  <div className="flex-1 flex flex-col justify-between mt-1 gap-2">
                    <div className="flex justify-between items-center text-[11.5px]">
                      <span className="text-text-muted">Caution Level</span>
                      {liveWeather?.rain_risk_expected ? (
                        <span className="rounded-full bg-[#FFEbee] px-2 py-0.5 text-[9.5px] font-bold text-[#ba1a1a]">
                          Elevated
                        </span>
                      ) : (
                        <span className="rounded-full bg-[#E8F5E9] px-2 py-0.5 text-[9.5px] font-bold text-[#2f6f4f]">
                          Low
                        </span>
                      )}
                    </div>
                    <div className="border-t border-white/10 pt-2 flex flex-col gap-1">
                      <span className="text-[9px] text-text-muted font-bold uppercase">Today's Advice</span>
                      <p className="text-[11px] font-semibold text-text-charcoal leading-snug font-sans">
                        {liveWeather?.rain_risk_expected 
                          ? "Heavy rain expected. Avoid low-lying streets and use weather-safe routing." 
                          : "Normal movement is acceptable. Check live updates regularly."}
                      </p>
                    </div>
                    <div className="text-[9.5px] text-text-muted italic text-right mt-1 font-sans">
                      Nasr City dispatch advisory
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Right 3 columns: Detail Overview Column */}
            <div className="lg:col-span-3 flex flex-col gap-4 overflow-y-auto pr-1 pb-2 stitch-scroll h-full">
              <div className="flex justify-between items-center px-1">
                <h2 className="text-sm font-bold text-text-charcoal uppercase tracking-wider">Detail Overview</h2>
                <span className="text-[10px] text-text-muted font-semibold font-mono">
                  {liveWeather?.current?.time 
                    ? `Updated: ${liveWeather.current.time.split('T')[1] || ''} EET` 
                    : "Live weather status"}
                </span>
              </div>

              {/* Weather Info Card */}
              <div className="stitch-card flex flex-col p-4 shadow-sm relative">
                <div className="flex justify-between items-start">
                  <div className="flex items-center gap-4">
                    <span 
                      className="material-symbols-outlined text-[42px]" 
                      style={{ 
                        fontVariationSettings: "'FILL' 1",
                        color: getWeatherIconColor(currentWeatherIcon)
                      }}
                    >
                      {currentWeatherIcon}
                    </span>
                    <div>
                      <div className="text-3xl font-bold tracking-tight text-text-charcoal font-sans">
                        {liveWeather?.current?.temperature_2m != null 
                          ? `${Math.round(liveWeather.current.temperature_2m)}` 
                          : "—"}
                        <span className="text-sm align-top font-bold block inline-block mt-0.5 ml-0.5">°C</span>
                      </div>
                    </div>
                  </div>
                  <button className="text-text-muted hover:bg-black/5 rounded-full p-0.5"><span className="material-symbols-outlined text-[16px]">more_vert</span></button>
                </div>
                <div className="mt-3">
                  <div className="text-[9px] font-bold uppercase tracking-wider text-text-muted">Current Weather</div>
                  <div className="text-sm font-bold text-text-charcoal mt-0.5">
                    {liveWeather ? (liveWeather.rain_risk_expected ? "Heavy Rain Expected" : "No meaningful rain risk") : "—"}
                  </div>
                </div>
                <p className="text-[10.5px] text-text-muted mt-2 leading-relaxed font-sans">
                  Real-time predictions based on local station observations and meteorological models.
                </p>
                <div className="grid grid-cols-3 gap-2 mt-4 border-t border-white/20 pt-3">
                  <div>
                    <div className="text-[9px] font-bold uppercase tracking-wider text-text-muted font-sans">Humidity</div>
                    <div className="font-bold text-xs text-text-charcoal mt-0.5 font-sans">
                      {liveWeather?.current?.relative_humidity_2m != null 
                        ? `${liveWeather.current.relative_humidity_2m}%` 
                        : "—"}
                    </div>
                  </div>
                  <div>
                    <div className="text-[9px] font-bold uppercase tracking-wider text-text-muted font-sans">Wind Speed</div>
                    <div className="font-bold text-xs text-text-charcoal mt-0.5 font-sans">
                      {liveWeather?.current?.wind_speed_10m != null 
                        ? `${liveWeather.current.wind_speed_10m.toFixed(1)} km/h` 
                        : "—"}
                    </div>
                  </div>
                  <div>
                    <div className="text-[9px] font-bold uppercase tracking-wider text-text-muted font-sans">Precip.</div>
                    <div className="font-bold text-xs text-text-charcoal mt-0.5 font-sans">
                      {liveWeather?.current?.precipitation != null 
                        ? `${liveWeather.current.precipitation.toFixed(1)} mm` 
                        : "—"}
                    </div>
                  </div>
                </div>
              </div>

              {/* 7-Day Forecast */}
              <div className="stitch-card flex flex-col p-4 shadow-sm relative">
                <div className="flex items-center justify-between mb-3">
                  <div className="text-[9px] font-bold uppercase tracking-wider text-[#006688]">7-Day Forecast</div>
                  <span className="text-[9px] font-semibold text-text-muted">{dailyForecast?.source ?? "Open-Meteo"}</span>
                </div>
                <div className="flex flex-col gap-2">
                  {(dailyForecast?.daily ?? []).slice(0, 7).map((day) => (
                    <div key={day.date} className="grid grid-cols-[3rem_1.5rem_1fr_auto] items-center gap-2 text-[11px]">
                      <span className="font-bold text-text-charcoal">
                        {new Date(`${day.date}T12:00:00`).toLocaleDateString(undefined, { weekday: "short" })}
                      </span>
                      <span 
                        className="material-symbols-outlined text-[17px]" 
                        style={{ 
                          fontVariationSettings: "'FILL' 1",
                          color: getWeatherIconColor(getWeatherIcon(day.weather_code))
                        }}
                      >
                        {getWeatherIcon(day.weather_code)}
                      </span>
                      <span className="text-text-muted">{formatMetric(day.precipitation_probability_max, "%")} rain</span>
                      <span className="font-bold text-text-charcoal">{formatTemperature(day.temperature_2m_max)} / {formatTemperature(day.temperature_2m_min)}</span>
                    </div>
                  ))}
                  {dailyForecast?.daily?.length ? null : (
                    <span className="text-[11px] text-text-muted">Forecast unavailable from provider.</span>
                  )}
                </div>
              </div>

              {/* AQI / Air Quality */}
              <div className="stitch-card flex flex-col p-4 shadow-sm relative">
                <div className="flex justify-between items-start gap-3">
                  <div>
                    <div className="text-[9px] font-bold uppercase tracking-wider text-[#006688]">Air Quality</div>
                    <div className="mt-1 text-3xl font-bold text-text-charcoal">{aqiValue != null ? Math.round(aqiValue) : "—"}</div>
                    <div className="text-xs font-bold text-text-charcoal">{aqiLabel}</div>
                  </div>
                  <span className="rounded-full bg-[#E8F5E9] px-2.5 py-1 text-[9px] font-bold text-[#2f6f4f]">
                    {airQuality?.status === "ok" ? "Live AQI" : "Unavailable"}
                  </span>
                </div>
                <div className="mt-3 grid grid-cols-2 gap-2 border-t border-white/20 pt-3 text-[11px]">
                  <div>
                    <span className="block text-[9px] font-bold uppercase tracking-wider text-text-muted">Major Pollutant</span>
                    <span className="font-bold text-text-charcoal">PM2.5</span>
                  </div>
                  <div>
                    <span className="block text-[9px] font-bold uppercase tracking-wider text-text-muted">PM10</span>
                    <span className="font-bold text-text-charcoal">{formatMetric(airQuality?.current?.pm10, " ug/m3", 1)}</span>
                  </div>
                </div>
                {aqiSparklinePath ? (
                  <svg viewBox="0 0 132 34" className="mt-3 h-9 w-full" role="img" aria-label="Air quality hourly trend">
                    <path d={`${aqiSparklinePath} L 132 34 L 0 34 Z`} fill="rgba(88, 169, 118, 0.18)" />
                    <path d={aqiSparklinePath} fill="none" stroke="#58A976" strokeWidth="2" strokeLinecap="round" />
                  </svg>
                ) : null}
              </div>

              {/* Route Recommendation Info */}
              <div className="stitch-card flex flex-col p-4 shadow-sm relative">
                <div className="flex justify-between items-start mb-2">
                  <div className="text-[9px] font-bold uppercase tracking-wider text-[#006688]">Route Advice</div>
                  <button className="text-text-muted hover:bg-black/5 rounded-full p-0.5"><span className="material-symbols-outlined text-[16px]">more_vert</span></button>
                </div>
                <div className="text-xs font-bold text-text-charcoal">
                  {comparison ? (() => {
                    const rec = (comparison as any).recommendation || 
                      (comparison.safe_route_available ? "weather_safe_route_recommended" : "normal_route_acceptable");
                    let title = "Normal Route Acceptable";
                    let subtitle = "No meaningful rain risk is expected on this route.";
                    if (rec === "weather_safe_route_recommended") {
                      title = "Weather-Safe Route Recommended";
                      subtitle = "The normal route crosses higher-risk areas. Use the safer route.";
                    } else if (rec === "no_distinct_safer_alternative") {
                      title = "No Distinct Safer Alternative";
                      subtitle = "The system did not find a route with lower model-estimated risk.";
                    }
                    return (
                      <>
                        {title}
                        <p className="text-[10px] text-text-muted font-normal mt-1 leading-relaxed font-sans">
                          {subtitle}
                        </p>
                      </>
                    );
                  })() : (
                    <span className="text-text-muted font-normal">Waiting for start/destination routing setup...</span>
                  )}
                </div>
              </div>

              {/* Inline Explainability Panel */}
              <div className="flex-1 shrink-0 min-h-0">
                <ExplainabilityPanel
                  zoneExplanation={zoneExplanation}
                  routeExplanation={routeExplanation}
                  onClose={() => {
                    setSelectedZoneCode(null);
                    setZoneExplanation(null);
                  }}
                  activeTab={explainActiveTab}
                  zoneLoading={zoneLoading}
                  routeLoading={routeLoading}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
