import { useCallback, useEffect, useRef, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { CloudSun } from "lucide-react";
import {
  getBoundaryLayer,
  getCustomEmergencyRoute,
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
} from "../api/client";
import type {
  EventSummary,
  FeatureCollection,
  LayerToggles,
  PlaceProperties,
  RouteComparison,
  RouteCoordinate,
  SummaryResponse,
} from "../types/api";
import { EventSelector } from "./EventSelector";
import { LayerToggle } from "./LayerToggle";
import { Legend } from "./Legend";
import { ErrorDisplay, LoadingSpinner } from "./LoadingError";
import { MapView } from "./MapView";
import { RoutePanel } from "./RoutePanel";
import { SidePanel } from "./SidePanel";
import { SummaryCards } from "./SummaryCards";

type RouteEventType = "top-rain" | "latest";
type RouteVisibility = "normal" | "safe" | "both";

interface RouteSelection {
  origin: RouteCoordinate | null;
  destination: RouteCoordinate | null;
}

const emptySelection: RouteSelection = { origin: null, destination: null };

const getErrorMessage = (error: unknown, fallback: string) =>
  error instanceof Error && error.message ? error.message : fallback;

export const Dashboard = () => {
  const prefersReducedMotion = useReducedMotion();
  const safeRouteTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [events, setEvents] = useState<EventSummary[]>([]);
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);
  const [riskFillOpacity, setRiskFillOpacity] = useState(0.35);
  const [gridLineOpacity, setGridLineOpacity] = useState(0.20);
  const [routeEventType, setRouteEventType] = useState<RouteEventType>("top-rain");
  const [routeVisibility, setRouteVisibility] = useState<RouteVisibility>("both");
  const [routeSelection, setRouteSelection] = useState<RouteSelection>(emptySelection);
  const [routingLoading, setRoutingLoading] = useState(false);
  const [routingError, setRoutingError] = useState<string | null>(null);
  const [routeSource, setRouteSource] = useState<"demo" | "custom">("demo");

  const [layers, setLayers] = useState<LayerToggles>({
    boundary: true,
    grid: false,
    roadsLabels: true,
    hospitals: true,
    clinics: true,
    mosques: true,
    malls: true,
    schools: true,
    universities: true,
    police: true,
    fireStations: true,
    emergency: true,
    latestRisk: true,
    topRainRisk: false,
    riskSummary: false,
    selectedRisk: false,
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
          summaryResponse,
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

        setSummary(summaryResponse);
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
  }, [routeEventType, routeSelection.origin]);

  useEffect(() => {
    const { origin, destination } = routeSelection;
    if (!origin || !destination) return;
    let cancelled = false;

    const fetchCustomRoute = async () => {
      setRoutingLoading(true);
      setRoutingError(null);
      setRouteSource("custom");
      setComparison(null);
      setNormalRouteData(null);
      setSafeRouteData(null);
      try {
        const response = await getCustomEmergencyRoute({
          origin,
          destination,
          event_type: routeEventType,
          route_preference: "both",
        });
        if (cancelled) return;

        if (safeRouteTimerRef.current) {
          clearTimeout(safeRouteTimerRef.current);
        }
        setNormalRouteData(response.normal_route);
        setSafeRouteData(null);
        setComparison({
          ...response.comparison,
          event_type: response.event_type,
          selected_destination_facility_name: "Selected map point",
          honesty_note: response.honesty_note,
        });
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
    setRoutingLoading(false);
    setRoutingError(null);
    setNormalRouteData(null);
    setSafeRouteData(null);
    setComparison(null);
    setRouteSource("demo");
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
    ? "routing"
    : routingError
      ? "error"
      : routeSelection.destination
        ? "complete"
        : routeSelection.origin
          ? "origin-set"
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
          <div className="flex size-9 items-center justify-center rounded-xl bg-[#2C5EAD] text-white shadow-sm"><CloudSun /></div>
          <div>
            <h1 className="text-sm font-bold tracking-tight text-[#2C5EAD]">Egypt Smart City Digital Twin</h1>
            <p className="text-[10px] font-medium text-muted-foreground">Nasr City Weather-Impact Emergency Mobility Module</p>
          </div>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        <SidePanel>
          <EventSelector events={events} selectedEventId={selectedEventId} onSelectEvent={setSelectedEventId} />
          <LayerToggle
            layers={layers}
            onToggle={handleToggleLayer}
            riskFillOpacity={riskFillOpacity}
            setRiskFillOpacity={setRiskFillOpacity}
            gridLineOpacity={gridLineOpacity}
            setGridLineOpacity={setGridLineOpacity}
          />
          <Legend />
        </SidePanel>

        <main className="relative flex flex-1 flex-col overflow-hidden">
          <div className="shrink-0 pt-2">
            <SummaryCards
              summary={summary}
              selectedEventId={selectedEventId}
              events={events}
              comparison={comparison}
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
