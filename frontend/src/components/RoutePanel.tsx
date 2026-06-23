import React from "react";
import { RouteComparison } from "../types/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { Clock3, Info, Navigation, Route, ShieldCheck } from "lucide-react";
import { formatNumber, formatPercent } from "../utils/format";

interface RoutePanelProps {
  comparison: RouteComparison | null;
  eventType: "top-rain" | "latest";
  onEventTypeChange: (type: "top-rain" | "latest") => void;
  routeVisibility: "normal" | "safe" | "both";
  onRouteVisibilityChange: (vis: "normal" | "safe" | "both") => void;
}

const formatDistance = (meters: number) => {
  const value = formatNumber(meters / 1000, 2);
  return value === "—" ? "—" : `${value} km`;
};

const formatDuration = (seconds: number) => Number.isFinite(Number(seconds)) ? `${Math.round(Number(seconds) / 60)} min` : "—";

const RouteRow = ({ safe, distance, eta, risk }: { safe?: boolean; distance: number; eta: number; risk: number }) => (
  <div className="grid grid-cols-[1fr_auto] items-center gap-x-3 gap-y-1 rounded-xl border bg-white p-3">
    <div className="flex items-center gap-2">
      <span className={safe ? "h-0.5 w-8 bg-[#1591DC] shadow-[0_0_7px_rgba(21,145,220,0.55)]" : "w-8 border-t-2 border-dashed border-[#8186D5]"} />
      <span className={safe ? "text-xs font-semibold text-primary" : "text-xs font-semibold text-secondary-foreground"}>
        {safe ? "Weather-safe" : "Normal"}
      </span>
    </div>
    <strong className="text-xs">{formatDistance(distance)}</strong>
    <span className="flex items-center gap-1 text-[10px] text-muted-foreground"><Clock3 /> {formatDuration(eta)}</span>
    <span className="text-[10px] text-muted-foreground">Mean risk <strong className="text-foreground">{formatNumber(risk, 3)}</strong></span>
  </div>
);

export const RoutePanel: React.FC<RoutePanelProps> = ({
  comparison,
  eventType,
  onEventTypeChange,
  routeVisibility,
  onRouteVisibilityChange,
}) => {
  if (!comparison) {
    return (
      <Card size="sm" className="border-0 bg-white/95 shadow-xl ring-1 ring-slate-200/80 backdrop-blur">
        <CardContent className="text-xs text-muted-foreground">Loading route comparison…</CardContent>
      </Card>
    );
  }

  const riskReduction = Number(comparison.risk_reduction_percent);
  const etaTradeoff = Number(comparison.eta_tradeoff_percent);
  const quality = comparison.safe_route_quality || "pending";

  return (
    <Card size="sm" className="route-panel border-0 bg-white/94 shadow-[0_18px_50px_rgba(44,94,173,0.2)] ring-1 ring-slate-200/90 backdrop-blur-xl">
      <CardHeader className="border-b">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <CardTitle className="flex items-center gap-2 text-sm font-bold text-primary"><Navigation /> Safer route</CardTitle>
            <CardDescription className="mt-1 truncate text-[10px]">
              {comparison.selected_origin_zone_code || "Origin zone"} → {comparison.selected_destination_facility_name || "Nearest facility"}
            </CardDescription>
          </div>
          <Badge variant={comparison.safe_route_available ? "secondary" : "destructive"} className="shrink-0 text-[9px]">
            {comparison.safe_route_available ? quality.replaceAll("_", " ") : "normal only"}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="flex flex-col gap-3">
        <Tabs value={eventType} onValueChange={(value) => onEventTypeChange(value as "top-rain" | "latest")}>
          <TabsList className="grid w-full grid-cols-2 bg-muted">
            <TabsTrigger value="top-rain" className="text-[10px]">Highest rain</TabsTrigger>
            <TabsTrigger value="latest" className="text-[10px]">Latest event</TabsTrigger>
          </TabsList>
        </Tabs>

        <div className="grid grid-cols-2 gap-2">
          <div className="rounded-xl border border-blue-100 bg-accent/45 p-3">
            <span className="flex items-center gap-1 text-[9px] font-semibold uppercase tracking-wider text-primary"><ShieldCheck /> Risk reduction</span>
            <strong className="mt-1 block text-xl text-primary">{Number.isFinite(riskReduction) && riskReduction > 0 ? `-${formatPercent(riskReduction, 1)}` : "0.0%"}</strong>
            <span className="text-[9px] text-muted-foreground">Avoided Segs: {formatNumber(comparison.avoided_high_risk_segments, 0)}</span>
          </div>
          <div className="rounded-xl border border-purple-100 bg-secondary/65 p-3">
            <span className="flex items-center gap-1 text-[9px] font-semibold uppercase tracking-wider text-secondary-foreground"><Clock3 /> ETA tradeoff</span>
            <strong className="mt-1 block text-xl text-secondary-foreground">{Number.isFinite(etaTradeoff) && etaTradeoff > 0 ? `+${formatPercent(etaTradeoff, 1)}` : "0.0%"}</strong>
            <span className="text-[9px] text-muted-foreground">Weather delay added</span>
          </div>
        </div>

        <div className="flex flex-col gap-2">
          <RouteRow distance={comparison.normal_distance_m} eta={comparison.normal_weather_eta_sec} risk={comparison.normal_mean_risk_score} />
          <RouteRow safe distance={comparison.safe_distance_m} eta={comparison.safe_weather_eta_sec} risk={comparison.safe_mean_risk_score} />
        </div>

        <Separator />

        <div className="flex items-center justify-between gap-3">
          <span className="flex items-center gap-1.5 text-[10px] font-semibold"><Route /> Show routes</span>
          <ToggleGroup
            type="single"
            variant="outline"
            size="sm"
            spacing={0}
            value={routeVisibility}
            onValueChange={(value) => value && onRouteVisibilityChange(value as "normal" | "safe" | "both")}
          >
            <ToggleGroupItem value="normal" aria-label="Show normal route" className="text-[9px]">Normal</ToggleGroupItem>
            <ToggleGroupItem value="safe" aria-label="Show weather-safe route" className="text-[9px]">Safe</ToggleGroupItem>
            <ToggleGroupItem value="both" aria-label="Show both routes" className="text-[9px]">Both</ToggleGroupItem>
          </ToggleGroup>
        </div>

        <p className="flex items-start gap-1.5 rounded-lg bg-slate-50 p-2 text-[8px] leading-relaxed text-muted-foreground">
          <Info className="mt-0.5 shrink-0" />
          Routes are decision-support prototype outputs, not official emergency dispatch instructions.
        </p>
      </CardContent>
    </Card>
  );
};
