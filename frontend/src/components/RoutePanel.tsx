import { Info, MapPin, Navigation, RotateCcw, Route } from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { Progress } from "@/components/ui/progress";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import type { RouteComparison } from "../types/api";
import {
  EMPTY_VALUE,
  formatDistance,
  formatDuration,
  formatInteger,
  formatPercent,
  toFiniteNumber,
} from "../utils/format";

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
  <div className="rounded-lg bg-muted/70 px-2.5 py-2">
    <dt className="text-[9px] font-semibold uppercase tracking-[0.1em] text-muted-foreground">
      {label}
    </dt>
    <dd className="mt-1 break-words text-xs font-semibold text-foreground">{value}</dd>
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
}: RoutePanelProps) => {
  if (!comparison) {
    if (routeSource === "custom") {
      return (
        <Card size="sm" className="route-panel border-0 bg-card/95 shadow-xl ring-1 ring-border">
          <CardHeader className="border-b">
            <CardTitle className="flex items-center gap-2 text-primary">
              <MapPin aria-hidden="true" /> Custom Route
            </CardTitle>
            <CardDescription>
              {selectionState === "origin-set"
                ? "Origin selected. Choose a destination on the map."
                : selectionState === "routing"
                  ? "Comparing normal and weather-safe paths."
                  : "The selected points could not be routed."}
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-3">
            {selectionState === "routing" ? (
              <Progress value={68} className="route-progress" aria-label="Calculating custom route" />
            ) : null}
            {routingError ? (
              <Alert variant="destructive">
                <Info aria-hidden="true" />
                <AlertTitle>Route unavailable</AlertTitle>
                <AlertDescription>{routingError}</AlertDescription>
              </Alert>
            ) : null}
            {onResetRoute ? (
              <Button type="button" variant="outline" size="sm" onClick={onResetRoute}>
                <RotateCcw data-icon="inline-start" /> Reset Route
              </Button>
            ) : null}
          </CardContent>
        </Card>
      );
    }
    return (
      <Card size="sm" className="border-0 bg-card/95 shadow-xl ring-1 ring-border">
        <CardHeader>
          <CardTitle>Route Comparison</CardTitle>
          <CardDescription>Preparing route metrics</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-2">
          <Skeleton className="h-8 w-full" />
          <Skeleton className="h-24 w-full" />
        </CardContent>
      </Card>
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

  // Calculate metrics cleanly
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
    <Card
      size="sm"
      className="route-panel border-0 bg-card/95 shadow-[0_18px_50px_rgba(44,94,173,0.18)] ring-1 ring-border backdrop-blur-xl"
    >
      <CardHeader className="border-b bg-slate-50/50 p-4">
        <div className="flex flex-col gap-1">
          <div className="flex items-center justify-between gap-2">
            <span className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
              <Navigation className="size-3.5 text-primary" aria-hidden="true" />
              {customRoute ? "Live Route" : "Scenario Route"}
            </span>
            <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold border ${
              rec === "weather_safe_route_recommended"
                ? "bg-red-50 text-red-700 border-red-200"
                : rec === "no_distinct_safer_alternative"
                  ? "bg-slate-50 text-slate-600 border-slate-200"
                  : "bg-emerald-50 text-emerald-700 border-emerald-200"
            }`}>
              {recTitle}
            </span>
          </div>
          <h2 className="mt-2 text-sm font-bold text-foreground">
            {recTitle}
          </h2>
          <p className="text-xs text-muted-foreground">
            {recSubtitle}
          </p>
        </div>
      </CardHeader>

      <CardContent className="flex flex-col gap-3 pt-3">
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

        <Separator />

        <div className="flex items-center justify-between gap-3">
          <span className="flex items-center gap-1.5 text-[10px] font-semibold">
            <Route aria-hidden="true" /> Visible Routes
          </span>
          <ToggleGroup
            type="single"
            variant="outline"
            size="sm"
            spacing={0}
            value={routeVisibility}
            onValueChange={(value) =>
              value && onRouteVisibilityChange(value as "normal" | "safe" | "both")
            }
          >
            <ToggleGroupItem value="normal" aria-label="Show normal route">Normal</ToggleGroupItem>
            <ToggleGroupItem value="safe" aria-label="Show weather-safe route">Safe</ToggleGroupItem>
            <ToggleGroupItem value="both" aria-label="Show both routes">Both</ToggleGroupItem>
          </ToggleGroup>
        </div>

        {customRoute && onResetRoute ? (
          <Button type="button" variant="outline" size="sm" onClick={onResetRoute}>
            <RotateCcw data-icon="inline-start" /> Reset Custom Route
          </Button>
        ) : null}
      </CardContent>
    </Card>
  );
};
