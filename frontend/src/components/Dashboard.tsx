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
  getLiveWeatherRiskLayer,
  getLiveRoutingStatus,
  requestLiveEmergencyRoute,
} from "../api/client";
import type {
  EventSummary,
  FeatureCollection,
  LayerToggles,
  PlaceProperties,
  RouteComparison,
  RouteCoordinate,
  LiveWeatherSummary,
  LiveRoutingStatusResponse,
  SearchResultItem,
} from "../types/api";
import { LayerToggle } from "./LayerToggle";
import { Legend } from "./Legend";
import { ErrorDisplay, LoadingSpinner } from "./LoadingError";
import { MapView } from "./MapView";
import { RoutePanel } from "./RoutePanel";
import { SidePanel } from "./SidePanel";
import { SummaryCards } from "./SummaryCards";
import { SearchBox } from "./SearchBox";

type RouteEventType = "top-rain" | "latest";
type RouteVisibility = "normal" | "safe" | "both";

interface RouteSelection {
  origin: RouteCoordinate | null;
  destination: RouteCoordinate | null;
}

const emptySelection: RouteSelection = { origin: null, destination: null };

const getErrorMessage = (error: unknown, fallback: string) =>
  error instanceof Error && error.message ? error.message : fallback;

const BrandLogo = () => (
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2.5"
    strokeLinecap="round"
    strokeLinejoin="round"
    className="size-6 text-[#2C5EAD] shrink-0"
    aria-hidden="true"
  >
    <path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0z" />
    <path d="M9 10.5c1-1.5 2.5-1.5 3.5 0s2.5 1.5 3.5 0" strokeWidth="2" className="text-[#1591DC]" />
    <circle cx="12" cy="10" r="1.5" fill="currentColor" />
  </svg>
);

export const Dashboard = () => {
  const prefersReducedMotion = useReducedMotion();
  const safeRouteTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const [mapMode, setMapMode] = useState<"today" | "history">("today");
  const [events, setEvents] = useState<EventSummary[]>([]);
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);
  const [riskFillOpacity, setRiskFillOpacity] = useState(0.35);
  const [gridLineOpacity, setGridLineOpacity] = useState(0.20);
  const [routeEventType, setRouteEventType] = useState<RouteEventType>("top-rain");
  const [routeVisibility, setRouteVisibility] = useState<RouteVisibility>("both");
  const [routeSelection, setRouteSelection] = useState<RouteSelection>(emptySelection);
  const [routingLoading, setRoutingLoading] = useState(false);
  const [routingError, setRoutingError] = useState<string | null>(null);
  const [routeSource, setRouteSource] = useState<"demo" | "custom" | "custom-live">("custom-live");
  const [searchSelectedPoint, setSearchSelectedPoint] = useState<SearchResultItem | null>(null);
  const [liveWeather, setLiveWeather] = useState<LiveWeatherSummary | null>(null);
  const [liveRoutingStatus, setLiveRoutingStatus] = useState<LiveRoutingStatusResponse | null>(null);
  const [liveRiskData, setLiveRiskData] = useState<FeatureCollection | null>(null);
  const [liveWeatherError, setLiveWeatherError] = useState<string | null>(null);
  const [riskDisplayMode, setRiskDisplayMode] = useState<"focus" | "all">("focus");

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
          const [liveWeatherRes, liveRoutingStatusRes, liveRiskRes] = await Promise.all([
            getLiveWeather(),
            getLiveRoutingStatus(),
            getLiveWeatherRiskLayer(),
          ]);
          setLiveWeather(liveWeatherRes);
          setLiveRoutingStatus(liveRoutingStatusRes);
          setLiveRiskData(liveRiskRes);
          setLiveWeatherError(null);
        } catch (liveWeatherError) {
          console.warn("Failed to load live weather/routing info:", liveWeatherError);
          setLiveWeatherError("Unable to fetch live weather details. Showing offline/historical layers.");
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
  }, [mapMode]);

  const handleSetStartPoint = useCallback((coordinate: RouteCoordinate) => {
    if (safeRouteTimerRef.current) clearTimeout(safeRouteTimerRef.current);
    setRouteSelection(prev => ({ origin: coordinate, destination: prev.destination }));
    setRouteSource("custom");
    setRoutingError(null);
  }, []);

  const handleSetDestinationPoint = useCallback((coordinate: RouteCoordinate) => {
    if (!routeSelection.origin) {
      setRoutingError("Start point selected first, then choose destination.");
      return;
    }
    setRouteSelection(prev => ({ origin: prev.origin, destination: coordinate }));
  }, [routeSelection.origin]);

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
      <div className="flex h-screen w-screen flex-col items-center justify-center bg-background">
        <LoadingSpinner message="Synchronizing map layers, places, and weather-aware routes..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-background p-6">
        <div className="w-full max-w-lg"><ErrorDisplay message={error} /></div>
      </div>
    );
  }

  return (
    <div className="flex h-screen w-screen flex-col overflow-hidden bg-background font-sans text-foreground">
      <header className="dashboard-header flex h-16 shrink-0 items-center justify-between border-b bg-card px-4 shadow-[0_1px_10px_rgba(44,94,173,0.05)]">
        <div className="flex items-center gap-3">
          <BrandLogo />
          <div>
            <h1 className="text-sm font-bold tracking-tight text-[#2C5EAD]">Egypt Smart City Digital Twin</h1>
            <p className="text-[10px] font-medium text-muted-foreground">Nasr City Weather-Impact Emergency Mobility Module</p>
          </div>
        </div>
        {liveRoutingStatus && (
          <div className="flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1 text-[10px] font-medium text-slate-600">
            <span className={`h-1.5 w-1.5 rounded-full ${liveRoutingStatus.status === "ok" ? "bg-emerald-500" : "bg-amber-500 animate-pulse"}`} />
            Live Routing: {liveRoutingStatus.status === "ok" ? "Ready" : "Degraded"}
          </div>
        )}
      </header>

      <div className="flex flex-1 overflow-hidden">
        <SidePanel>
          <SearchBox
            onSelectResult={setSearchSelectedPoint}
            selectedResult={searchSelectedPoint}
            onSetStart={handleSetStartPoint}
            onSetDestination={handleSetDestinationPoint}
            onClear={() => setSearchSelectedPoint(null)}
          />
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
        </SidePanel>

        <main className="relative flex flex-1 flex-col overflow-hidden">
          {liveWeatherError && (
            <div className="mx-3 mt-2 flex items-center gap-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-1.5 text-[10px] font-semibold text-amber-800">
              <span className="h-1.5 w-1.5 rounded-full bg-amber-500 animate-pulse" />
              {liveWeatherError}
            </div>
          )}
          <div className="shrink-0 pt-2">
            <SummaryCards
              mapMode={mapMode}
              comparison={comparison}
              liveWeather={liveWeather}
            />
          </div>
          <div className="relative flex-1 overflow-hidden border-t">
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
            />

            <AnimatePresence mode="wait">
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
                />
              </motion.div>
            </AnimatePresence>
          </div>
        </main>
      </div>
    </div>
  );
};
