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
import { ShieldCheck } from "lucide-react";

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

  if (loading) {
    return (
      <div className="h-screen w-screen bg-slate-950 flex flex-col items-center justify-center">
        <LoadingSpinner message="Synchronizing geospatial layers, prediction models, and safe routes..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-screen w-screen bg-slate-950 flex items-center justify-center p-6">
        <div className="max-w-lg w-full">
          <ErrorDisplay message={error} />
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen w-screen bg-slate-950 flex flex-col overflow-hidden font-sans">
      {/* Top Header Bar */}
      <header className="bg-slate-950 border-b border-slate-900/60 h-12 flex items-center justify-between px-4 shrink-0">
        <div className="flex items-center space-x-2">
          <ShieldCheck className="h-5 w-5 text-cyan-400" />
          <h2 className="text-sm font-bold text-slate-100 uppercase tracking-wider">Egypt Smart City Digital Twin</h2>
        </div>
        <div className="flex items-center space-x-2">
          <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span className="text-[10px] text-slate-400 font-medium">Operations Center Local Link</span>
        </div>
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
          <div className="pt-4 shrink-0">
            <SummaryCards 
              summary={summary}
              health={health}
            />
          </div>

          {/* Large Map Area */}
          <div className="flex-1 relative overflow-hidden border-t border-slate-900/60">
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
            <div className="absolute bottom-4 right-4 w-96 max-h-[calc(100%-2rem)] z-10 overflow-y-auto hidden sm:block">
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
