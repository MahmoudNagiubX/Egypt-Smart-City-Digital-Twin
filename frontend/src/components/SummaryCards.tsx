import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { SummaryResponse, HealthResponse } from "../types/api";
import { Database, ShieldAlert, HeartPulse, Navigation } from "lucide-react";
import { formatInteger } from "../utils/format";

interface SummaryCardsProps {
  summary: SummaryResponse | null;
  health: HealthResponse | null;
}

const metricCardClass = "summary-card border-0 bg-white/94 shadow-[0_8px_30px_rgba(44,94,173,0.08)] ring-1 ring-slate-200/80";
const iconClass = "flex size-10 shrink-0 items-center justify-center rounded-xl bg-accent text-primary";

export const SummaryCards: React.FC<SummaryCardsProps> = ({ summary, health }) => {
  const isHealthy = health?.status === "ok";

  return (
    <div className="grid grid-cols-2 gap-3 px-4 pb-4 xl:grid-cols-4">
      <Card size="sm" className={metricCardClass}>
        <CardContent className="flex items-center gap-3">
          <div className={iconClass}><HeartPulse /></div>
          <div className="min-w-0 flex-1">
            <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">System health</p>
            <p className="mt-0.5 truncate text-sm font-semibold">FastAPI backend</p>
            <Badge variant={isHealthy ? "secondary" : "destructive"} className="mt-1 text-[9px]">
              {isHealthy ? "Online" : "Offline"}
            </Badge>
          </div>
        </CardContent>
      </Card>

      <Card size="sm" className={metricCardClass}>
        <CardContent className="flex items-center gap-3">
          <div className={iconClass}><Database /></div>
          <div className="min-w-0 flex-1">
            <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">City coverage</p>
            <p className="mt-0.5 truncate text-sm font-semibold">
              {summary ? `${formatInteger(summary.grid_cells)} Zones | ${formatInteger(summary.road_segments)} Roads` : "Loading…"}
            </p>
            <p className="mt-1 truncate text-[10px] text-muted-foreground">
              {summary ? `${formatInteger(summary.real_training_rows)} observations · ${formatInteger(summary.emergency_facilities)} facilities` : "API sync pending"}
            </p>
          </div>
        </CardContent>
      </Card>

      <Card size="sm" className={metricCardClass}>
        <CardContent className="flex items-center gap-3">
          <div className={iconClass}><ShieldAlert /></div>
          <div className="min-w-0 flex-1">
            <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">Risk estimates</p>
            <p className="mt-0.5 truncate text-sm font-semibold">
              {summary ? `${formatInteger(summary.prediction_rows)} Predictions` : "Loading…"}
            </p>
            <div className="mt-1 flex flex-wrap items-center gap-1">
              <Badge className="border-emerald-200 bg-emerald-50 text-[9px] text-emerald-700">LOW: {summary ? formatInteger(summary.risk_class_counts?.low) : "—"}</Badge>
              <Badge className="border-amber-200 bg-amber-50 text-[9px] text-amber-700">MED: {summary ? formatInteger(summary.risk_class_counts?.medium) : "—"}</Badge>
              <Badge className="border-red-200 bg-red-50 text-[9px] text-red-700">HIGH: {summary ? formatInteger(summary.risk_class_counts?.high) : "—"}</Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card size="sm" className={metricCardClass}>
        <CardContent className="flex items-center gap-3">
          <div className={iconClass}><Navigation /></div>
          <div className="min-w-0 flex-1">
            <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">Mobility routing</p>
            <p className="mt-0.5 truncate text-sm font-semibold">
              {summary?.routing_readiness?.routing_validation_status === "ok" ? "Weather-aware routes ready" : "Routing warnings"}
            </p>
            <p className="mt-1 text-[10px] text-muted-foreground">{summary ? formatInteger(summary.events) : "—"} observed events</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
