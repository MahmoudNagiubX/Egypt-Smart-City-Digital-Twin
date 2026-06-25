import { Info, MapPin, Navigation, RotateCcw, Route } from "lucide-react";
import { cn } from "@/lib/utils";
import type { RouteComparison } from "../types/api";
import {
  EMPTY_VALUE,
  formatDistance,
  formatDuration,
  formatInteger,
  formatPercent,
  toFiniteNumber,
} from "../utils/format";

import { Switch } from "@/components/ui/switch";

interface RoutePanelProps {
  comparison: RouteComparison | null;
  eventType: "top-rain" | "latest";
  onEventTypeChange: (type: "top-rain" | "latest") => void;
  routeVisibility: "normal" | "safe" | "both";
  onRouteVisibilityChange: (visibility: "normal" | "safe" | "both") => void;
  selectionState?: "idle" | "origin-set" | "routing" | "complete" | "error" | "selecting-destination" | "ready" | "loading";
  routeSource?: "demo" | "custom" | "custom-live";
  routingError?: string | null;
  onResetRoute?: () => void;
  onWhyThisRoute?: () => void;
  isRoutePlanningActive?: boolean;
  onToggleRoutePlanning?: (active: boolean) => void;
}

const signedPercent = (value: unknown) => {
  const number = toFiniteNumber(value);
  if (number === null) {
    return EMPTY_VALUE;
  }
  const prefix = number > 0 ? "+" : "";
  return `${prefix}${formatPercent(number, 1)}`;
};

const Metric = ({ label, value }: { label: string; value: string }) => (
  <div className="rounded-lg bg-white/40 border border-white/40 px-2 py-1.5 flex flex-col justify-between">
    <dt className="text-[9px] font-bold uppercase tracking-[0.08em] text-text-muted">
      {label}
    </dt>
    <dd className="mt-0.5 break-words text-xs font-bold text-text-charcoal">{value}</dd>
  </div>
);

export const RoutePanel = ({
  comparison,
  routeVisibility,
  onRouteVisibilityChange,
  selectionState = "idle",
  routeSource = "demo",
  routingError,
  onResetRoute,
  onWhyThisRoute,
  isRoutePlanningActive = false,
  onToggleRoutePlanning,
}: RoutePanelProps) => {
  if (!comparison) {
    if (routeSource === "custom" || routeSource === "custom-live") {
      return (
        <div className="stitch-card flex flex-col gap-3 shadow-lg pointer-events-auto p-4 max-w-sm">
          <div className="flex flex-col gap-1">
            <div className="flex items-center gap-1.5 text-xs font-bold text-[#006688]">
              <MapPin className="size-4" aria-hidden="true" />
              <span>Custom Route Planner</span>
            </div>
            <p className="text-[11px] text-text-muted mt-1 leading-normal">
              {selectionState === "idle"
                ? (isRoutePlanningActive 
                    ? "Click the map to select the starting point." 
                    : "Toggle planning mode to select start/destination on the map.")
                : selectionState === "selecting-destination"
                  ? "Origin selected. Choose a destination on the map."
                  : selectionState === "routing" || selectionState === "loading"
                    ? "Comparing normal and weather-safe paths."
                    : "The selected points could not be routed."}
            </p>
          </div>
          
          {(selectionState === "routing" || selectionState === "loading") && (
            <div className="w-full bg-white/40 h-1.5 rounded-full overflow-hidden relative">
              <div 
                className="bg-gradient-to-r from-[#006688] to-[#00c2ff] h-full absolute top-0 bottom-0"
                style={{
                  width: '50%',
                  animation: 'route-loading-sweep 1.1s ease-in-out infinite'
                }}
              />
            </div>
          )}

          {routingError && (
            <div className="rounded-lg border border-red-200 bg-red-50/80 p-2.5 text-xs text-red-700 flex flex-col gap-1">
              <div className="flex items-center gap-1 font-bold">
                <Info className="size-3.5" aria-hidden="true" />
                <span>Route unavailable</span>
              </div>
              <p className="text-[10px] leading-normal">{routingError}</p>
            </div>
          )}

          {selectionState === "idle" && onToggleRoutePlanning && (
            <div className="flex items-center justify-between border border-white/60 rounded-xl p-2.5 bg-white/40">
              <span className="text-[11px] font-bold text-text-charcoal">Route Planning Mode</span>
              <Switch 
                checked={isRoutePlanningActive} 
                onCheckedChange={onToggleRoutePlanning}
                size="sm"
                className="data-[state=checked]:bg-[#006688]"
              />
            </div>
          )}

          {(selectionState !== "idle" || routingError) && onResetRoute && (
            <button 
              type="button" 
              onClick={onResetRoute}
              className="flex h-9 items-center justify-center gap-1.5 rounded-lg border border-white/60 bg-white/50 text-xs font-semibold text-text-charcoal hover:bg-white/80 transition-colors"
            >
              <RotateCcw className="size-3.5" /> 
              <span>Reset Route</span>
            </button>
          )}
        </div>
      );
    }

    return (
      <div className="stitch-card flex flex-col gap-3 shadow-lg pointer-events-auto p-4 max-w-sm">
        <div className="flex flex-col gap-1">
          <span className="text-xs font-bold text-text-charcoal">Route Comparison</span>
          <span className="text-[10px] text-text-muted">Preparing route metrics...</span>
        </div>
        <div className="animate-pulse flex flex-col gap-2">
          <div className="h-6 bg-white/40 rounded w-3/4"></div>
          <div className="h-20 bg-white/40 rounded"></div>
        </div>
      </div>
    );
  }

  const isLive = (comparison as any).recommendation !== undefined;
  const customRoute = routeSource === "custom" || routeSource === "custom-live";

  const rec = (comparison as any).recommendation || 
    (comparison.safe_route_available ? "weather_safe_route_recommended" : "normal_route_acceptable");

  let recTitle = "Normal Route Acceptable";
  let recSubtitle = "No meaningful rain risk is expected on this route.";

  if (rec === "weather_safe_route_recommended") {
    recTitle = "Weather-Safe Route Recommended";
    recSubtitle = "The normal route crosses higher-risk areas. Use the safer route.";
  } else if (rec === "no_distinct_safer_alternative") {
    recTitle = "No Distinct Safer Alternative";
    recSubtitle = "The system did not find a route with lower model-estimated risk.";
  }

  // Calculate metrics
  const riskRedVal = toFiniteNumber(comparison.risk_reduction_percent);
  const riskReductionText = riskRedVal !== null && riskRedVal <= 0
    ? "No change"
    : formatPercent(comparison.risk_reduction_percent, 1);

  const rain24 = isLive
    ? `${((comparison as any).live_weather_summary?.forecast_window?.rain_24h_mm ?? (comparison as any).live_weather_summary?.rain_24h_mm ?? 0).toFixed(1)} mm`
    : (comparison as any).rain_24h_mm != null ? `${(comparison as any).rain_24h_mm.toFixed(1)} mm` : EMPTY_VALUE;

  const rainProb = isLive
    ? `${Math.round((comparison as any).live_weather_summary?.forecast_window?.max_precipitation_probability ?? (comparison as any).live_weather_summary?.max_precipitation_probability ?? 0)}%`
    : EMPTY_VALUE;

  return (
    <div
      className={cn(
        "stitch-card flex flex-col gap-3 shadow-lg pointer-events-auto p-4 max-w-sm border-t-[3px] transition-all duration-200",
        rec === "weather_safe_route_recommended"
          ? "border-t-[#ba1a1a]"
          : rec === "no_distinct_safer_alternative"
            ? "border-t-[#8b5000]"
            : "border-t-[#006688]"
      )}
    >
      <div className="flex flex-col gap-1 border-b border-white/20 pb-3">
        <div className="flex items-center justify-between gap-2">
          <span className="flex items-center gap-1.5 text-[9px] font-bold uppercase tracking-wider text-text-muted">
            <Navigation className="size-3 text-[#006688]" aria-hidden="true" />
            {customRoute ? "Live Route" : "Scenario Route"}
          </span>
          <span className={cn(
            "rounded-full px-2 py-0.5 text-[9px] font-bold border",
            rec === "weather_safe_route_recommended"
              ? "bg-[#ffdad6]/80 text-[#ba1a1a] border-[#ffdad6]"
              : rec === "no_distinct_safer_alternative"
                ? "bg-white/40 text-[#8b5000] border-[#ffdcbe]"
                : "bg-[#83fba5]/20 text-[#006d36] border-[#83fba5]/50"
          )}>
            {recTitle}
          </span>
        </div>
        <h2 className="mt-2 text-xs font-bold text-text-charcoal">
          {recTitle}
        </h2>
        <p className="text-[10px] leading-normal text-text-muted mt-0.5">
          {recSubtitle}
        </p>
      </div>

      <div className="max-h-48 overflow-y-auto pr-1">
        <dl className="grid grid-cols-2 gap-2">
          <Metric label="Risk Reduction" value={riskReductionText} />
          <Metric label="ETA Tradeoff" value={signedPercent(comparison.eta_tradeoff_percent)} />
          <Metric label="24h Rainfall" value={rain24} />
          <Metric label="Rain Probability" value={rainProb} />
          <Metric label="Normal Distance" value={formatDistance(comparison.normal_distance_m)} />
          <Metric label="Safe Route Distance" value={formatDistance(comparison.safe_distance_m)} />
          <Metric label="Normal ETA" value={formatDuration(comparison.normal_weather_eta_sec)} />
          <Metric label="Safe Route ETA" value={formatDuration(comparison.safe_weather_eta_sec)} />
          <Metric label="High-Risk Segments Avoided" value={formatInteger(comparison.avoided_high_risk_segments)} />
        </dl>
      </div>

      <div className="flex flex-col gap-2.5 border-t border-white/20 pt-3 mt-1.5">
        <div className="flex items-center justify-between gap-3">
          <span className="flex items-center gap-1.5 text-[10px] font-bold text-text-charcoal">
            <Route className="size-3.5 text-text-muted" aria-hidden="true" /> 
            <span>Visible Routes</span>
          </span>
          <div className="inline-flex rounded-lg bg-white/40 border border-white/60 p-0.5">
            {(["normal", "safe", "both"] as const).map((mode) => (
              <button
                key={mode}
                type="button"
                onClick={() => onRouteVisibilityChange(mode)}
                className={cn(
                  "rounded px-2.5 py-1 text-[10px] font-bold uppercase transition-all",
                  routeVisibility === mode
                    ? "bg-[#006688] text-white shadow-sm"
                    : "text-text-muted hover:text-text-charcoal"
                )}
              >
                {mode === "both" ? "Both" : mode === "safe" ? "Safe" : "Normal"}
              </button>
            ))}
          </div>
        </div>

        {onWhyThisRoute && (
          <button
            type="button"
            onClick={onWhyThisRoute}
            className="w-full bg-[#006688] hover:bg-[#00526e] text-white flex items-center justify-center gap-1.5 py-2 rounded-lg font-bold text-xs shadow-sm transition-colors"
          >
            <Info className="size-3.5" /> 
            <span>Why this route?</span>
          </button>
        )}

        {customRoute && onResetRoute && (
          <button 
            type="button" 
            onClick={onResetRoute}
            className="w-full flex h-8 items-center justify-center gap-1.5 rounded-lg border border-white/60 bg-white/40 text-xs font-semibold text-text-charcoal hover:bg-white/80 transition-colors"
          >
            <RotateCcw className="size-3.5" /> 
            <span>Reset Custom Route</span>
          </button>
        )}
      </div>
    </div>
  );
};
