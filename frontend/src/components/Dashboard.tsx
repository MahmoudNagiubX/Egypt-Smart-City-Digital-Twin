import React, { useEffect, useState } from "react";
import { 
  getHealth, 
  getSummary, 
  getEvents, 
  getBoundaryLayer, 
  getGridLayer, 
  getEmergencyFacilities, 
  getLatestRiskLayer, 
  getTopRainRiskLayer, 
  getRiskSummaryLayer, 
  getEventRiskLayer, 
  getRouteComparison, 
  getDemoRoute 
} from "../api/client";
import { 
  HealthResponse, 
  SummaryResponse, 
  EventSummary, 
  RouteComparison, 
  LayerToggles, 
  FeatureCollection 
} from "../types/api";
import { SidePanel } from "./SidePanel";
import { SummaryCards } from "./SummaryCards";
import { MapView } from "./MapView";
import { LayerToggle } from "./LayerToggle";
import { EventSelector } from "./EventSelector";
import { Legend } from "./Legend";
import { RoutePanel } from "./RoutePanel";
import { LoadingSpinner, ErrorDisplay } from "./LoadingError";
import { CloudSun, ShieldCheck } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export const Dashboard: React.FC = () => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [events, setEvents] = useState<EventSummary[]>([]);
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);
  const [routeEventType, setRouteEventType] = useState<"top-rain" | "latest">("top-rain");
  const [routeVisibility, setRouteVisibility] = useState<"normal" | "safe" | "both">("both");
  
  const [layers, setLayers] = useState<LayerToggles>({
    boundary: true,
    grid: false,
    facilities: true,
    roadsLabels: true,
    hospitals: true,
    mosques: true,
    malls: true,
    education: true,
    latestRisk: true,
    topRainRisk: false,
    riskSummary: false,
    selectedRisk: false
  });

  // Layer data states
  const [boundaryData, setBoundaryData] = useState<FeatureCollection | null>(null);
  const [gridData, setGridData] = useState<FeatureCollection | null>(null);
  const [facilitiesData, setFacilitiesData] = useState<FeatureCollection | null>(null);
  const [latestRiskData, setLatestRiskData] = useState<FeatureCollection | null>(null);
  const [topRainRiskData, setTopRainRiskData] = useState<FeatureCollection | null>(null);
  const [riskSummaryData, setRiskSummaryData] = useState<FeatureCollection | null>(null);
  const [selectedEventRiskData, setSelectedEventRiskData] = useState<FeatureCollection | null>(null);
  
  // Route data states
  const [normalRouteData, setNormalRouteData] = useState<FeatureCollection | null>(null);
  const [safeRouteData, setSafeRouteData] = useState<FeatureCollection | null>(null);
  const [comparison, setComparison] = useState<RouteComparison | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Initial load
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        setLoading(true);
        const [
          healthRes, 
          summaryRes, 
          eventsRes, 
          boundaryRes, 
          gridRes, 
          facilitiesRes,
          latestRiskRes,
          topRainRiskRes,
          riskSummaryRes
        ] = await Promise.all([
          getHealth(),
          getSummary(),
          getEvents(),
          getBoundaryLayer(),
          getGridLayer(),
          getEmergencyFacilities(),
          getLatestRiskLayer(),
          getTopRainRiskLayer(),
          getRiskSummaryLayer()
        ]);

        setHealth(healthRes);
        setSummary(summaryRes);
        setEvents(eventsRes);
        setBoundaryData(boundaryRes);
        setGridData(gridRes);
        setFacilitiesData(facilitiesRes);
        setLatestRiskData(latestRiskRes);
        setTopRainRiskData(topRainRiskRes);
        setRiskSummaryData(riskSummaryRes);

        if (eventsRes.length > 0) {
          // Set default selected event
          setSelectedEventId(eventsRes[0].event_id);
        }
      } catch (err: any) {
        setError(err.message || "Failed to load dashboard parameters from local backend.");
      } finally {
        setLoading(false);
      }
    };

    fetchInitialData();
  }, []);

  // Fetch selected event risk
  useEffect(() => {
    if (!selectedEventId) return;

    const fetchSelectedEventRisk = async () => {
      try {
        const riskRes = await getEventRiskLayer(selectedEventId);
        setSelectedEventRiskData(riskRes);
        // Automatically enable selectedRisk layer if user explicitly changes selection
        setLayers(prev => ({ ...prev, selectedRisk: true }));
      } catch (err: any) {
        console.error("Failed to load selected event risk layer:", err);
      }
    };

    fetchSelectedEventRisk();
  }, [selectedEventId]);

  // Fetch demo routes and comparisons
  useEffect(() => {
    const fetchRoutingData = async () => {
      try {
        const [routeNormal, routeSafe, comparisonRes] = await Promise.all([
          getDemoRoute(routeEventType, "normal"),
          getDemoRoute(routeEventType, "safe"),
          getRouteComparison(routeEventType)
        ]);

        setNormalRouteData(routeNormal);
        setSafeRouteData(routeSafe);
        setComparison(comparisonRes);
      } catch (err: any) {
        console.error("Failed to load routing data:", err);
      }
    };

    fetchRoutingData();
  }, [routeEventType]);

  const handleToggleLayer = (key: keyof LayerToggles) => {
    setLayers(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const backendOnline = health?.status === "healthy" || health?.status === "ok";

  if (loading) {
    return (
      <div className="flex h-screen w-screen flex-col items-center justify-center bg-background">
        <LoadingSpinner message="Synchronizing geospatial layers, prediction models, and safe routes..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-background p-6">
        <div className="max-w-lg w-full">
          <ErrorDisplay message={error} />
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen w-screen flex-col overflow-hidden bg-background font-sans text-foreground">
      {/* Top Header Bar */}
      <header className="dashboard-header flex h-16 shrink-0 items-center justify-between border-b bg-card px-4 shadow-[0_1px_10px_rgba(44,94,173,0.05)]">
        <div className="flex items-center gap-3">
          <div className="flex size-9 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-sm">
            <CloudSun />
          </div>
          <div>
            <h1 className="text-sm font-bold tracking-tight text-primary">Egypt Smart City Digital Twin</h1>
            <p className="text-[10px] font-medium text-muted-foreground">Nasr City Weather-Impact Emergency Mobility Module</p>
          </div>
        </div>
        <Badge variant={backendOnline ? "secondary" : "outline"} className="gap-1.5 px-3 py-1.5">
          <ShieldCheck aria-hidden="true" />
          {backendOnline ? "Backend Online" : "Backend Unavailable"}
        </Badge>
      </header>

      {/* Main Layout Workspace */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidepanel Controls */}
        <SidePanel>
          <EventSelector 
            events={events}
            selectedEventId={selectedEventId}
            onSelectEvent={setSelectedEventId}
          />
          <LayerToggle 
            layers={layers}
            onToggle={handleToggleLayer}
          />
          <Legend />
        </SidePanel>

        {/* Right Dashboard Area (Map + Top Cards + Floating Route Comparison) */}
        <div className="flex-1 flex flex-col overflow-hidden relative">
          {/* Top Summary Cards */}
          <div className="shrink-0 pt-4">
            <SummaryCards 
              summary={summary}
              health={health}
            />
          </div>

          {/* Large Map Area */}
          <div className="relative flex-1 overflow-hidden border-t">
            <MapView 
              layers={layers}
              routeVisibility={routeVisibility}
              boundaryData={boundaryData}
              gridData={gridData}
              facilitiesData={facilitiesData}
              latestRiskData={latestRiskData}
              topRainRiskData={topRainRiskData}
              riskSummaryData={riskSummaryData}
              selectedEventRiskData={selectedEventRiskData}
              normalRouteData={normalRouteData}
              safeRouteData={safeRouteData}
            />

            {/* Floating Glassy Route Panel in bottom right */}
            <div className="absolute bottom-4 right-4 z-10 hidden w-[22rem] max-h-[calc(100%-2rem)] overflow-y-auto sm:block">
              <RoutePanel 
                comparison={comparison}
                eventType={routeEventType}
                onEventTypeChange={setRouteEventType}
                routeVisibility={routeVisibility}
                onRouteVisibilityChange={setRouteVisibility}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
