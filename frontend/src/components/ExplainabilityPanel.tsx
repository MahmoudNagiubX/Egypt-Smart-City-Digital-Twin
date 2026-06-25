import React, { useState, useEffect } from "react";
import { 
  CloudRain, 
  Building2, 
  Users, 
  Route as RouteIcon, 
  Mountain, 
  Trees, 
  Info, 
  Cpu, 
  AlertTriangle, 
  X,
  Compass,
  ArrowRight,
  TrendingDown
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";
import type { 
  ZoneExplanationResponse, 
  RouteExplanationResponse, 
  ModelExplainabilitySummaryResponse 
} from "../types/api";
import { getModelExplainabilitySummary } from "../api/client";

interface ExplainabilityPanelProps {
  zoneExplanation: ZoneExplanationResponse | null;
  routeExplanation: RouteExplanationResponse | null;
  onClose: () => void;
  activeTab?: "area" | "route" | "model";
  zoneLoading?: boolean;
  routeLoading?: boolean;
}

export const ExplainabilityPanel: React.FC<ExplainabilityPanelProps> = ({
  zoneExplanation,
  routeExplanation,
  onClose,
  activeTab: initialTab = "area",
  zoneLoading = false,
  routeLoading = false,
}) => {
  const [activeTab, setActiveTab] = useState<"area" | "route" | "model">(initialTab);
  const [modelSummary, setModelSummary] = useState<ModelExplainabilitySummaryResponse | null>(null);
  const [modelLoading, setModelLoading] = useState(false);
  const [honestyOpen, setHonestyOpen] = useState(false);
  const [limitationsOpen, setLimitationsOpen] = useState(false);

  // Sync activeTab if initialTab changes
  useEffect(() => {
    setActiveTab(initialTab);
  }, [initialTab]);

  // Load model summary once on mount or when switching to model tab
  useEffect(() => {
    if (activeTab === "model" && !modelSummary && !modelLoading) {
      const fetchModelSummary = async () => {
        setModelLoading(true);
        try {
          const res = await getModelExplainabilitySummary();
          setModelSummary(res);
        } catch (err) {
          console.error("Failed to load model explainability summary:", err);
        } finally {
          setModelLoading(false);
        }
      };
      void fetchModelSummary();
    }
  }, [activeTab, modelSummary, modelLoading]);

  // Get factor icon
  const getFactorIcon = (factorName: string) => {
    const name = factorName.toLowerCase();
    if (name.includes("rain")) return <CloudRain className="size-4 text-sky-500" />;
    if (name.includes("built_surface") || name.includes("builtup")) return <Building2 className="size-4 text-amber-500" />;
    if (name.includes("population")) return <Users className="size-4 text-purple-500" />;
    if (name.includes("road")) return <RouteIcon className="size-4 text-emerald-500" />;
    if (name.includes("elevation") || name.includes("slope")) return <Mountain className="size-4 text-orange-500" />;
    if (name.includes("vegetation") || name.includes("tree") || name.includes("grass")) return <Trees className="size-4 text-green-500" />;
    return <Info className="size-4 text-blue-500" />;
  };

  const getRiskClassBadgeColor = (riskClass: string) => {
    switch (riskClass.toLowerCase()) {
      case "high":
        return "bg-red-50 text-red-700 border-red-200";
      case "medium":
        return "bg-amber-50 text-amber-700 border-amber-200";
      default:
        return "bg-emerald-50 text-emerald-700 border-emerald-200";
    }
  };

  return (
    <Card 
      size="sm"
      className="explain-panel border-0 bg-gradient-to-br from-white to-[#F1F5F9]/60 shadow-[0_15px_40px_rgba(44,94,173,0.15)] ring-1 ring-border backdrop-blur-xl border-t-[4px] border-t-primary transition-all flex flex-col max-h-[35rem] w-full"
    >
      <CardHeader className="p-4 border-b shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Cpu className="size-4.5 text-primary" />
            <CardTitle className="text-sm font-bold text-foreground">Explainability</CardTitle>
          </div>
          <button 
            type="button" 
            onClick={onClose}
            className="flex size-6 items-center justify-center rounded-full hover:bg-slate-100 text-muted-foreground transition-colors"
            aria-label="Close Explainability Panel"
          >
            <X className="size-4" />
          </button>
        </div>
        {/* Tabs navigation */}
        <div className="flex gap-1 border-b border-slate-200/50 mt-3">
          <button
            type="button"
            onClick={() => setActiveTab("area")}
            className={cn(
              "px-3 py-1.5 text-[11px] font-bold transition-all border-b-2 -mb-[1px]",
              activeTab === "area" 
                ? "border-primary text-primary" 
                : "border-transparent text-muted-foreground hover:text-foreground"
            )}
          >
            Area Info
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("route")}
            className={cn(
              "px-3 py-1.5 text-[11px] font-bold transition-all border-b-2 -mb-[1px]",
              activeTab === "route" 
                ? "border-primary text-primary" 
                : "border-transparent text-muted-foreground hover:text-foreground"
            )}
          >
            Route Tradeoff
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("model")}
            className={cn(
              "px-3 py-1.5 text-[11px] font-bold transition-all border-b-2 -mb-[1px]",
              activeTab === "model" 
                ? "border-primary text-primary" 
                : "border-transparent text-muted-foreground hover:text-foreground"
            )}
          >
            Model Insight
          </button>
        </div>
      </CardHeader>

      <div className="flex-1 overflow-y-auto min-h-0 p-4">
        {/* AREA TAB */}
        {activeTab === "area" && (
          <div className="flex flex-col gap-3">
            {zoneLoading ? (
              <div className="flex flex-col gap-2 py-4 items-center justify-center text-xs text-muted-foreground">
                <div className="size-5 border-2 border-primary border-t-transparent animate-spin rounded-full mb-1" />
                Fetching area risk metrics...
              </div>
            ) : zoneExplanation ? (
              <>
                <div className="flex flex-col gap-1">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xs font-bold text-slate-800">{zoneExplanation.zone_label} Explainability</h3>
                    <span className={cn("px-2 py-0.5 rounded-full text-[9px] font-bold border uppercase tracking-wider", getRiskClassBadgeColor(zoneExplanation.risk_class))}>
                      {zoneExplanation.risk_label}
                    </span>
                  </div>
                  <p className="text-[10px] text-muted-foreground font-mono mt-0.5">{zoneExplanation.zone_code}</p>
                </div>

                <div className="text-[11px] bg-slate-100/70 border border-slate-200/40 rounded-lg p-2.5 leading-relaxed text-slate-700">
                  <p className="font-semibold text-slate-800 mb-1">Why this area?</p>
                  {zoneExplanation.summary}
                </div>

                <div className="flex flex-col gap-2 mt-1">
                  <h4 className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Main Risk Drivers</h4>
                  
                  {zoneExplanation.top_factors.map((factor, idx) => (
                    <div key={factor.factor + idx} className="flex flex-col gap-1 border border-slate-200/40 bg-white/70 rounded-lg p-2.5 shadow-sm transition-all hover:shadow-md">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1.5 min-w-0">
                          {getFactorIcon(factor.factor)}
                          <span className="text-[11px] font-bold text-slate-700 truncate">{factor.label}</span>
                        </div>
                        <span className="text-[11px] font-bold font-mono text-slate-800 bg-slate-100 px-1.5 py-0.5 rounded shrink-0">
                          {factor.value.toLocaleString()}
                        </span>
                      </div>
                      <p className="text-[10px] text-muted-foreground mt-0.5 leading-snug">{factor.reason}</p>
                      {factor.impact !== "neutral" && (
                        <div className="mt-1">
                          <span className={cn(
                            "px-1.5 py-0.5 rounded text-[8px] font-bold uppercase tracking-wider border",
                            factor.impact.includes("increases") 
                              ? "bg-red-50/50 text-red-600 border-red-200/45" 
                              : "bg-emerald-50/50 text-emerald-600 border-emerald-200/45"
                          )}>
                            {factor.impact}
                          </span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                <Separator className="my-2" />

                {/* Footer Notes */}
                <div className="flex flex-col gap-1.5 mt-1 bg-amber-50/20 border border-amber-200/20 rounded-lg p-2">
                  <p className="text-[9px] font-semibold text-amber-700 leading-snug">
                    <Info className="size-3 inline mr-1 shrink-0" />
                    {zoneExplanation.confidence_note || "Decision-support estimate only. Not an official flood report."}
                  </p>
                  
                  <button
                    type="button"
                    onClick={() => setHonestyOpen(!honestyOpen)}
                    className="text-[9px] text-slate-500 hover:text-slate-700 underline text-left font-semibold mt-1"
                  >
                    {honestyOpen ? "Hide limitations note" : "Show limitations note"}
                  </button>
                  {honestyOpen && (
                    <p className="text-[9px] text-muted-foreground/95 leading-normal mt-1 border-t border-slate-200/50 pt-1.5 transition-all">
                      {zoneExplanation.honesty_note}
                    </p>
                  )}
                </div>
              </>
            ) : (
              <div className="flex flex-col py-8 items-center text-center justify-center text-[11px] text-muted-foreground leading-normal">
                <Info className="size-6 text-muted-foreground/60 mb-2" />
                <p className="font-bold text-slate-600 mb-1">No Area Selected</p>
                Click a risk zone on the map to see its explainability details.
              </div>
            )}
          </div>
        )}

        {/* ROUTE TAB */}
        {activeTab === "route" && (
          <div className="flex flex-col gap-3">
            {routeLoading ? (
              <div className="flex flex-col gap-2 py-4 items-center justify-center text-xs text-muted-foreground">
                <div className="size-5 border-2 border-primary border-t-transparent animate-spin rounded-full mb-1" />
                Analyzing routing tradeoffs...
              </div>
            ) : routeExplanation ? (
              <>
                <div className="flex flex-col gap-1">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xs font-bold text-slate-800">Why this route?</h3>
                    <span className={cn(
                      "px-2 py-0.5 rounded-full text-[9px] font-bold border uppercase tracking-wider",
                      routeExplanation.recommendation === "weather_safe_route_recommended"
                        ? "bg-red-50 text-red-700 border-red-200"
                        : routeExplanation.recommendation === "no_distinct_safer_alternative"
                          ? "bg-slate-50 text-slate-600 border-slate-200"
                          : "bg-emerald-50 text-emerald-700 border-emerald-200"
                    )}>
                      {routeExplanation.recommendation_label}
                    </span>
                  </div>
                </div>

                <div className="text-[11px] bg-slate-100/70 border border-slate-200/40 rounded-lg p-2.5 leading-relaxed text-slate-700">
                  {routeExplanation.summary}
                </div>

                <div className="flex flex-col gap-2 mt-1">
                  <h4 className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Tradeoff Drivers</h4>
                  
                  {routeExplanation.route_reasons.map((reason, idx) => {
                    const isRiskRed = reason.label.includes("Risk");
                    const percentVal = parseFloat(reason.value);
                    const isNeutral = isRiskRed && percentVal <= 0;
                    
                    return (
                      <div key={reason.label + idx} className="flex flex-col gap-1 border border-slate-200/40 bg-white/70 rounded-lg p-2.5 shadow-sm">
                        <div className="flex items-center justify-between">
                          <span className="text-[11px] font-bold text-slate-700">{reason.label}</span>
                          <span className={cn(
                            "text-[11px] font-bold font-mono px-1.5 py-0.5 rounded shrink-0",
                            isNeutral 
                              ? "bg-slate-100 text-slate-600" 
                              : isRiskRed 
                                ? "bg-emerald-100 text-emerald-800" 
                                : "bg-amber-100 text-amber-800"
                          )}>
                            {reason.value}
                          </span>
                        </div>
                        <p className="text-[10px] text-muted-foreground mt-0.5 leading-snug">{reason.reason}</p>
                      </div>
                    );
                  })}
                </div>

                <div className="grid grid-cols-2 gap-2 mt-2">
                  <div className="border border-slate-200/50 bg-slate-50/50 rounded-lg p-2 flex flex-col gap-1">
                    <p className="text-[10px] font-bold text-slate-600">Normal Route</p>
                    <p className="text-[10px] text-muted-foreground leading-normal">{routeExplanation.normal_route_explanation.summary}</p>
                    <div className="flex justify-between items-center mt-auto pt-1 text-[9px] font-semibold text-slate-500">
                      <span>Segments: {routeExplanation.normal_route_explanation.high_risk_segments}</span>
                      <span>Risk: {routeExplanation.normal_route_explanation.mean_risk_score.toFixed(3)}</span>
                    </div>
                  </div>

                  <div className="border border-slate-200/50 bg-slate-50/50 rounded-lg p-2 flex flex-col gap-1">
                    <p className="text-[10px] font-bold text-primary">Weather-Safe Route</p>
                    <p className="text-[10px] text-muted-foreground leading-normal">{routeExplanation.safe_route_explanation.summary}</p>
                    <div className="flex justify-between items-center mt-auto pt-1 text-[9px] font-semibold text-slate-500">
                      <span>Segments: {routeExplanation.safe_route_explanation.high_risk_segments}</span>
                      <span>Risk: {routeExplanation.safe_route_explanation.mean_risk_score.toFixed(3)}</span>
                    </div>
                  </div>
                </div>

                <Separator className="my-2" />

                <div className="bg-slate-100/80 border border-slate-200/50 rounded-lg p-2 flex gap-1.5 items-start">
                  <AlertTriangle className="size-3.5 text-amber-600 mt-0.5 shrink-0" />
                  <p className="text-[9px] text-slate-500 leading-snug">
                    <strong>Wording Disclaimer:</strong> {routeExplanation.honesty_note || "Prototype route guidance only. Not official dispatch instructions."}
                  </p>
                </div>
              </>
            ) : (
              <div className="flex flex-col py-8 items-center text-center justify-center text-[11px] text-muted-foreground leading-normal">
                <RouteIcon className="size-6 text-muted-foreground/60 mb-2" />
                <p className="font-bold text-slate-600 mb-1">No Active Route</p>
                Plan custom start and destination points on the map to see routing tradeoff explainability.
              </div>
            )}
          </div>
        )}

        {/* MODEL TAB */}
        {activeTab === "model" && (
          <div className="flex flex-col gap-3">
            {modelLoading ? (
              <div className="flex flex-col gap-2 py-4 items-center justify-center text-xs text-muted-foreground">
                <div className="size-5 border-2 border-primary border-t-transparent animate-spin rounded-full mb-1" />
                Loading model configuration...
              </div>
            ) : modelSummary ? (
              <>
                <div className="flex flex-col gap-1 border-b pb-2">
                  <h3 className="text-xs font-bold text-slate-800">Model: {modelSummary.model_name}</h3>
                  <p className="text-[10px] text-muted-foreground mt-0.5 leading-snug">
                    Type: {modelSummary.model_type} &bull; Target: {modelSummary.target}
                  </p>
                </div>

                <div className="flex flex-col gap-2">
                  <h4 className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Top Risk Factor Weights</h4>
                  
                  {modelSummary.top_global_features.slice(0, 5).map((feat, idx) => (
                    <div key={feat.feature + idx} className="flex flex-col gap-1 border border-slate-200/40 bg-white/70 rounded-lg p-2 shadow-sm">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1.5 min-w-0">
                          {getFactorIcon(feat.feature)}
                          <span className="text-[11px] font-bold text-slate-700 truncate">{feat.label}</span>
                        </div>
                        <span className="text-[11px] font-bold font-mono text-slate-800 bg-slate-100 px-1.5 py-0.5 rounded shrink-0">
                          {feat.importance.toFixed(4)}
                        </span>
                      </div>
                      <p className="text-[10px] text-muted-foreground mt-0.5 leading-snug">{feat.reason}</p>
                    </div>
                  ))}
                </div>

                <Separator className="my-2" />

                <div className="flex flex-col gap-1.5 bg-slate-100/70 border border-slate-200/50 rounded-lg p-2">
                  <button
                    type="button"
                    onClick={() => setLimitationsOpen(!limitationsOpen)}
                    className="flex justify-between items-center w-full text-[10px] font-bold text-slate-700 hover:text-slate-900"
                  >
                    <span>Known Model Limitations</span>
                    <span>{limitationsOpen ? "▲" : "▼"}</span>
                  </button>
                  
                  {limitationsOpen && (
                    <ul className="list-disc pl-4 text-[9px] text-slate-600 leading-normal flex flex-col gap-1 mt-1 border-t pt-1.5">
                      {modelSummary.known_limitations.map((limit, idx) => (
                        <li key={idx}>{limit}</li>
                      ))}
                    </ul>
                  )}
                </div>

                <div className="bg-amber-50/20 border border-amber-200/25 rounded-lg p-2.5 mt-1 flex gap-1.5 items-start">
                  <Info className="size-3.5 text-amber-600 mt-0.5 shrink-0" />
                  <p className="text-[9px] text-amber-700 leading-snug">
                    {modelSummary.honesty_note}
                  </p>
                </div>
              </>
            ) : (
              <div className="text-[11px] text-rose-500 py-4 font-semibold">
                Unable to load model summary parameters.
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  );
};
