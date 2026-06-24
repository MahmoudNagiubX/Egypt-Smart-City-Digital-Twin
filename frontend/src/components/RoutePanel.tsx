import { Info, MapPin, Navigation, RotateCcw, Route, ShieldCheck } from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
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
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
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
import { getRouteQualityLabel, formatZoneLabel, getRecommendationLabel } from "../utils/labels";

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
  eventType,
  onEventTypeChange,
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

  const containsArabic = (text?: string | null): boolean => {
    if (!text) return false;
    return /[\u0600-\u06FF]/.test(text);
  };

  const getCleanDestination = (name?: string | null) => {
    if (!name) return "Selected Destination";
    if (containsArabic(name)) return "Selected Destination";
    return name;
  };

  const isLive = (comparison as any).recommendation !== undefined;
  const recommendationLabel = isLive ? getRecommendationLabel((comparison as any).recommendation) : "";
  const quality = comparison.safe_route_available
    ? getRouteQualityLabel(comparison.safe_route_quality)
    : "No Distinct Safer Alternative";
  const destination = getCleanDestination(comparison.selected_destination_facility_name);
  const customRoute = routeSource === "custom" || routeSource === "custom-live";

  return (
    <Card
      size="sm"
      className="route-panel border-0 bg-card/95 shadow-[0_18px_50px_rgba(44,94,173,0.18)] ring-1 ring-border backdrop-blur-xl"
    >
      <CardHeader className="border-b">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <CardTitle className="flex items-center gap-2 text-sm font-bold text-primary">
              <Navigation aria-hidden="true" /> {customRoute ? (isLive ? "Live Custom Route" : "Custom Route") : "Demo Route"}
            </CardTitle>
            <CardDescription className="mt-1 flex items-center gap-1 text-[10px]">
              <MapPin aria-hidden="true" /> {customRoute ? "Custom path selection" : `${formatZoneLabel(comparison.selected_origin_zone_code)} to ${destination}`}
            </CardDescription>
          </div>
          <Badge variant={comparison.safe_route_available ? "secondary" : "outline"}>
            {isLive ? recommendationLabel : (comparison.safe_route_available ? "Safer Route Available" : "Normal Route Recommended")}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="flex flex-col gap-3">
        {!isLive && (
          <div className="flex flex-col gap-1.5">
            <span className="text-[9px] font-semibold uppercase tracking-[0.12em] text-muted-foreground">
              Event Mode
            </span>
            <Tabs
              value={eventType}
              onValueChange={(value) => onEventTypeChange(value as "top-rain" | "latest")}
            >
              <TabsList className="grid w-full grid-cols-2 bg-muted">
                <TabsTrigger value="top-rain">Historic Rain</TabsTrigger>
                <TabsTrigger value="latest">Latest Observed</TabsTrigger>
              </TabsList>
            </Tabs>
          </div>
        )}

        <div className="flex items-center justify-between gap-3 rounded-lg bg-secondary/70 px-3 py-2">
          <span className="flex items-center gap-1.5 text-[10px] font-semibold text-secondary-foreground">
            <ShieldCheck aria-hidden="true" /> Route Quality
          </span>
          <strong className="text-xs text-secondary-foreground">{quality}</strong>
        </div>

        <dl className="grid grid-cols-2 gap-2">
          {isLive && (
            <Metric 
              label="Route Recommendation" 
              value={recommendationLabel} 
            />
          )}
          {isLive && (
            <Metric 
              label="Rain Risk Status" 
              value={(comparison as any).rain_risk_expected ? "Rain Risk Expected" : "No Meaningful Rain Risk"} 
            />
          )}
          <Metric label="Risk Reduction" value={formatPercent(comparison.risk_reduction_percent, 1)} />
          <Metric label="ETA Tradeoff" value={signedPercent(comparison.eta_tradeoff_percent)} />
          <Metric
            label="High-Risk Segments Avoided"
            value={formatInteger(comparison.avoided_high_risk_segments)}
          />
          <Metric label="Normal Distance" value={formatDistance(comparison.normal_distance_m)} />
          <Metric label="Safe Route Distance" value={formatDistance(comparison.safe_distance_m)} />
          <Metric label="Normal ETA" value={formatDuration(comparison.normal_weather_eta_sec)} />
          <Metric label="Safe Route ETA" value={formatDuration(comparison.safe_weather_eta_sec)} />
          {isLive && (comparison as any).live_weather_summary && (
            <>
              <Metric 
                label="24h Rainfall" 
                value={`${((comparison as any).live_weather_summary.forecast_window?.rain_24h_mm ?? (comparison as any).live_weather_summary.rain_24h_mm ?? 0).toFixed(1)} mm`} 
              />
              <Metric 
                label="Rain Probability" 
                value={`${Math.round((comparison as any).live_weather_summary.forecast_window?.max_precipitation_probability ?? (comparison as any).live_weather_summary.max_precipitation_probability ?? 0)}%`} 
              />
            </>
          )}
          {!isLive && <Metric label="Destination" value={destination} />}
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
