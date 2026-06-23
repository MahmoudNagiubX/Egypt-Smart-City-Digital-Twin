import React from "react";
import { RouteComparison } from "../types/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { Navigation, Clock, ShieldCheck, CornerUpRight, Info } from "lucide-react";

interface RoutePanelProps {
  comparison: RouteComparison | null;
  eventType: "top-rain" | "latest";
  onEventTypeChange: (type: "top-rain" | "latest") => void;
  routeVisibility: "normal" | "safe" | "both";
  onRouteVisibilityChange: (vis: "normal" | "safe" | "both") => void;
}

export const RoutePanel: React.FC<RoutePanelProps> = ({
  comparison,
  eventType,
  onEventTypeChange,
  routeVisibility,
  onRouteVisibilityChange,
}) => {
  if (!comparison) {
    return (
      <Card className="bg-slate-950/80 border-slate-900/60 text-slate-100 backdrop-blur-md shadow-2xl p-4">
        <p className="text-xs text-slate-400">Loading route comparisons...</p>
      </Card>
    );
  }

  const formatDistance = (m: number) => {
    return `${(m / 1000).toFixed(2)} km`;
  };

  const formatDuration = (sec: number) => {
    const mins = Math.round(sec / 60);
    return `${mins} min`;
  };

  const isSafeAvailable = comparison.safe_route_available;
  const quality = comparison.safe_route_quality;
  const riskRed = comparison.risk_reduction_percent;
  const etaTradeoff = comparison.eta_tradeoff_percent;

  const getQualityBadgeClass = (q: string) => {
    switch (q.toLowerCase()) {
      case "strong":
        return "bg-cyan-500/10 text-cyan-400 border-cyan-500/30 text-[9px]";
      case "weak_but_valid":
      case "accepted":
        return "bg-emerald-500/10 text-emerald-400 border-emerald-500/30 text-[9px]";
      default:
        return "bg-amber-500/10 text-amber-400 border-amber-500/30 text-[9px]";
    }
  };

  return (
    <Card className="bg-slate-950/80 border-slate-900/60 text-slate-100 backdrop-blur-md shadow-2xl w-full">
      <CardHeader className="p-4 pb-2 border-b border-slate-900/60">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <CardTitle className="text-xs font-bold text-slate-200 flex items-center gap-1.5 uppercase tracking-wider">
              <Navigation className="h-4 w-4 text-cyan-400" />
              Emergency Safe Route Comparison
            </CardTitle>
            <p className="text-[10px] text-slate-400 mt-0.5">
              Simulating origin: <span className="text-slate-300 font-medium">{comparison.selected_origin_zone_code || "Unknown Zone"}</span> to{" "}
              <span className="text-slate-300 font-medium">{comparison.selected_destination_facility_name || "Closest Facility"}</span>
            </p>
          </div>
          <Tabs 
            value={eventType} 
            onValueChange={(val) => onEventTypeChange(val as "top-rain" | "latest")}
          >
            <TabsList className="bg-slate-900 border border-slate-800 h-8 p-0.5">
              <TabsTrigger value="top-rain" className="text-[10px] px-2.5 h-7">Top Rain</TabsTrigger>
              <TabsTrigger value="latest" className="text-[10px] px-2.5 h-7">Latest Event</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>
      </CardHeader>

      <CardContent className="p-4 space-y-4">
        {/* Quality status */}
        <div className="flex items-center justify-between bg-slate-900/40 p-2.5 rounded border border-slate-900/60">
          <span className="text-[9px] text-slate-400 font-bold uppercase tracking-wider">Route Status</span>
          <div className="flex items-center space-x-2">
            <Badge className={getQualityBadgeClass(quality)}>
              {quality.toUpperCase()}
            </Badge>
            <Badge className={isSafeAvailable ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20 text-[9px]" : "bg-red-500/10 text-red-400 border-red-500/20 text-[9px]"}>
              {isSafeAvailable ? "SAFE ROUTE RECOMMENDED" : "NORMAL ROUTE ONLY"}
            </Badge>
          </div>
        </div>

        {/* Comparison table / values */}
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-slate-900/20 p-3 rounded border border-slate-900/60 flex flex-col justify-center">
            <span className="text-[9px] text-slate-400 font-semibold uppercase tracking-wider mb-1 flex items-center gap-1">
              <ShieldCheck className="h-3 w-3 text-cyan-400" />
              Risk Reduction
            </span>
            <span className={`text-base font-bold ${riskRed > 0 ? "text-cyan-400" : "text-slate-400"}`}>
              {riskRed > 0 ? `-${riskRed.toFixed(1)}%` : "0.0%"}
            </span>
            <span className="text-[9px] text-slate-500 mt-0.5">
              Avoided Segs: {comparison.avoided_high_risk_segments}
            </span>
          </div>

          <div className="bg-slate-900/20 p-3 rounded border border-slate-900/60 flex flex-col justify-center">
            <span className="text-[9px] text-slate-400 font-semibold uppercase tracking-wider mb-1 flex items-center gap-1">
              <Clock className="h-3 w-3 text-cyan-400" />
              ETA Tradeoff
            </span>
            <span className={`text-base font-bold ${etaTradeoff > 0 ? "text-amber-400" : "text-cyan-400"}`}>
              {etaTradeoff > 0 ? `+${etaTradeoff.toFixed(1)}%` : "0.0%"}
            </span>
            <span className="text-[9px] text-slate-500 mt-0.5">
              Weather delay added
            </span>
          </div>

          <div className="bg-slate-900/20 p-3 rounded border border-slate-900/60 flex flex-col justify-center">
            <span className="text-[9px] text-slate-400 font-semibold uppercase tracking-wider mb-1 flex items-center gap-1">
              <CornerUpRight className="h-3 w-3 text-cyan-400" />
              Route Display
            </span>
            <ToggleGroup 
              type="single" 
              value={routeVisibility} 
              onValueChange={(val) => {
                if (val) onRouteVisibilityChange(val as "normal" | "safe" | "both");
              }}
              className="justify-start mt-0.5 h-7"
            >
              <ToggleGroupItem value="normal" className="text-[9px] px-1.5 h-6">Normal</ToggleGroupItem>
              <ToggleGroupItem value="safe" className="text-[9px] px-1.5 h-6">Safe</ToggleGroupItem>
              <ToggleGroupItem value="both" className="text-[9px] px-1.5 h-6">Both</ToggleGroupItem>
            </ToggleGroup>
          </div>
        </div>

        <Separator className="bg-slate-900/60" />

        {/* Detailed Metrics List */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="space-y-1.5">
            <div className="text-[9px] text-slate-400 font-bold uppercase tracking-wider mb-1">Normal Route (Risk-Unaware)</div>
            <div className="flex justify-between">
              <span className="text-slate-400">Total Distance:</span>
              <span className="text-slate-200 font-medium">{formatDistance(comparison.normal_distance_m)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Est Weather ETA:</span>
              <span className="text-slate-200 font-medium">{formatDuration(comparison.normal_weather_eta_sec)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Mean Risk Score:</span>
              <span className="text-red-400 font-bold">{comparison.normal_mean_risk_score.toFixed(3)}</span>
            </div>
          </div>

          <div className="space-y-1.5 border-t md:border-t-0 md:border-l border-slate-900/60 pt-3 md:pt-0 md:pl-4">
            <div className="text-[9px] text-cyan-400 font-bold uppercase tracking-wider mb-1">Weather-Safe Route (Optimized)</div>
            <div className="flex justify-between">
              <span className="text-slate-400">Total Distance:</span>
              <span className="text-slate-200 font-medium">{formatDistance(comparison.safe_distance_m)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Est Weather ETA:</span>
              <span className="text-slate-200 font-medium">{formatDuration(comparison.safe_weather_eta_sec)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Mean Risk Score:</span>
              <span className="text-emerald-400 font-bold">{comparison.safe_mean_risk_score.toFixed(3)}</span>
            </div>
          </div>
        </div>

        {/* Visibility note */}
        <div className="flex items-start gap-1.5 text-[8.5px] text-slate-500 bg-slate-950/60 p-2 rounded border border-slate-900/60">
          <Info className="h-3 w-3 text-slate-400 shrink-0 mt-0.5" />
          <p className="leading-normal">
            Predictions are model-estimated weather-impact risk scores derived from real observed and satellite data. They are not verified street-level flood incident labels. Routes are decision-support prototype outputs, not official emergency dispatch instructions.
          </p>
        </div>
      </CardContent>
    </Card>
  );
};
