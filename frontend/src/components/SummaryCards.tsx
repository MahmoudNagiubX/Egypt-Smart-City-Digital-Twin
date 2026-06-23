import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { SummaryResponse, HealthResponse } from "../types/api";
import { Database, ShieldAlert, Heart, Compass } from "lucide-react";
import { formatInteger } from "../utils/format";

interface SummaryCardsProps {
  summary: SummaryResponse | null;
  health: HealthResponse | null;
}

export const SummaryCards: React.FC<SummaryCardsProps> = ({ summary, health }) => {
  const isHealthy = health?.status === "ok";
  
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 px-4 pb-4">
      {/* Backend Status Card */}
      <Card className="bg-slate-950/40 border-slate-800/80 text-slate-100 backdrop-blur-md shadow-lg">
        <CardContent className="p-4 flex items-center space-x-4">
          <div className="p-3 bg-slate-900/80 rounded-lg text-cyan-400 border border-slate-800">
            <Heart className="h-5 w-5" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">System Health</p>
            <h4 className="text-sm font-bold truncate mt-0.5 text-slate-200">FastAPI Backend</h4>
            <div className="mt-1 flex items-center space-x-1.5">
              <Badge className={isHealthy ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20 text-[9px]" : "bg-red-500/10 text-red-400 border-red-500/20 text-[9px]"}>
                {isHealthy ? "ONLINE" : "OFFLINE"}
              </Badge>
              <Badge className="bg-slate-900/60 text-slate-400 border-slate-800 text-[9px]">
                {health?.module || "weather_impact"}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Dataset & Preds Card */}
      <Card className="bg-slate-950/40 border-slate-800/80 text-slate-100 backdrop-blur-md shadow-lg">
        <CardContent className="p-4 flex items-center space-x-4">
          <div className="p-3 bg-slate-900/80 rounded-lg text-teal-400 border border-slate-800">
            <Database className="h-5 w-5" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Geospatial Data</p>
            <h4 className="text-sm font-bold truncate mt-0.5 text-slate-200">
              {summary ? `${formatInteger(summary.grid_cells)} Zones | ${formatInteger(summary.road_segments)} Roads` : "Loading..."}
            </h4>
            <p className="text-[10px] text-slate-400 mt-1 truncate">
              {summary ? `${formatInteger(summary.real_training_rows)} Obs Rows | ${formatInteger(summary.emergency_facilities)} Facilities` : "API Sync pending"}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Risks Counts Card */}
      <Card className="bg-slate-950/40 border-slate-800/80 text-slate-100 backdrop-blur-md shadow-lg">
        <CardContent className="p-4 flex items-center space-x-4">
          <div className="p-3 bg-slate-900/80 rounded-lg text-amber-400 border border-slate-800">
            <ShieldAlert className="h-5 w-5" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Simulated Risk Levels</p>
            <h4 className="text-sm font-bold truncate mt-0.5 text-slate-200">
              {summary ? `${formatInteger(summary.prediction_rows)} Predictions` : "Loading..."}
            </h4>
            <div className="mt-1 flex items-center gap-1.5 flex-wrap">
              <span className="text-[9px] px-1 py-0.2 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">
                LOW: {summary ? formatInteger(summary.risk_class_counts?.low) : "—"}
              </span>
              <span className="text-[9px] px-1 py-0.2 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 font-bold">
                MED: {summary ? formatInteger(summary.risk_class_counts?.medium) : "—"}
              </span>
              <span className="text-[9px] px-1 py-0.2 rounded bg-red-500/10 text-red-400 border border-red-500/20 font-bold">
                HIGH: {summary ? formatInteger(summary.risk_class_counts?.high) : "—"}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Routing & Events Card */}
      <Card className="bg-slate-950/40 border-slate-800/80 text-slate-100 backdrop-blur-md shadow-lg">
        <CardContent className="p-4 flex items-center space-x-4">
          <div className="p-3 bg-slate-900/80 rounded-lg text-purple-400 border border-slate-800">
            <Compass className="h-5 w-5" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Mobility Routing</p>
            <h4 className="text-sm font-bold truncate mt-0.5 text-slate-200">
              {summary?.routing_readiness?.routing_validation_status === "ok" ? "Emergency Safe Routing" : "Routing Warnings"}
            </h4>
            <div className="mt-1 flex items-center space-x-1.5">
              <Badge className={summary?.routing_readiness?.top_rain_safe_route_available ? "bg-cyan-500/10 text-cyan-400 border-cyan-500/20 text-[9px]" : "bg-red-500/10 text-red-400 border-red-500/20 text-[9px]"}>
                Rain Safe: {summary?.routing_readiness?.top_rain_safe_route_available ? "READY" : "NO"}
              </Badge>
              <Badge className="bg-slate-900/60 text-slate-400 border-slate-800 text-[9px]">
                {summary ? formatInteger(summary.events) : "—"} Events
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

