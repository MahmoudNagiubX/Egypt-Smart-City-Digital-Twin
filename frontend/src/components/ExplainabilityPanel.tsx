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
  X
} from "lucide-react";
import { cn } from "@/lib/utils";
import type { 
  ZoneExplanationResponse, 
  RouteExplanationResponse, 
  ModelExplainabilitySummaryResponse,
  HeatZoneExplanationResponse,
  HeatModelSummaryResponse
} from "../types/api";
import { getModelExplainabilitySummary } from "../api/client";

interface ExplainabilityPanelProps {
  zoneExplanation: ZoneExplanationResponse | null;
  routeExplanation: RouteExplanationResponse | null;
  onClose: () => void;
  activeTab?: "area" | "route" | "model";
  zoneLoading?: boolean;
  routeLoading?: boolean;
  activeRiskLayer?: "rain" | "heat";
  heatZoneExplanation?: HeatZoneExplanationResponse | null;
  heatModelSummary?: HeatModelSummaryResponse | null;
}

export const ExplainabilityPanel: React.FC<ExplainabilityPanelProps> = ({
  zoneExplanation,
  routeExplanation,
  onClose,
  activeTab: initialTab = "area",
  zoneLoading = false,
  routeLoading = false,
  activeRiskLayer = "rain",
  heatZoneExplanation = null,
  heatModelSummary = null,
}) => {
  const [activeTab, setActiveTab] = useState<"area" | "route" | "model">(initialTab);
  const [modelSummary, setModelSummary] = useState<ModelExplainabilitySummaryResponse | null>(null);
  const [modelLoading, setModelLoading] = useState(false);
  const [limitationsOpen, setLimitationsOpen] = useState(false);

  // Sync activeTab if initialTab changes
  useEffect(() => {
    setActiveTab(initialTab);
  }, [initialTab]);

  // Load model summary once on mount or when switching to model tab
  useEffect(() => {
    if (activeTab === "model" && activeRiskLayer === "rain" && !modelSummary && !modelLoading) {
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
  }, [activeTab, modelSummary, modelLoading, activeRiskLayer]);

  // Get factor icon
  const getFactorIcon = (factorName: string) => {
    const name = factorName.toLowerCase();
    if (name.includes("rain")) return <CloudRain className="size-4 text-sky-500" />;
    if (name.includes("built_surface") || name.includes("builtup") || name.includes("ndbi")) return <Building2 className="size-4 text-amber-500" />;
    if (name.includes("population")) return <Users className="size-4 text-purple-500" />;
    if (name.includes("road")) return <RouteIcon className="size-4 text-emerald-500" />;
    if (name.includes("elevation") || name.includes("slope") || name.includes("bare_sparse")) return <Mountain className="size-4 text-orange-500" />;
    if (name.includes("vegetation") || name.includes("tree") || name.includes("grass") || name.includes("ndvi")) return <Trees className="size-4 text-green-500" />;
    return <Info className="size-4 text-blue-500" />;
  };

  const getRiskClassBadgeColor = (riskClass?: string) => {
    if (!riskClass) return "bg-emerald-50 text-[#006d36] border-emerald-200";
    switch (riskClass.toLowerCase()) {
      case "high":
        return "bg-red-50 text-[#ba1a1a] border-red-200";
      case "medium":
        return "bg-amber-50 text-[#ff9e2a] border-amber-200";
      default:
        return "bg-emerald-50 text-[#006d36] border-emerald-200";
    }
  };

  return (
    <div 
      className="stitch-card shadow-lg flex flex-col pointer-events-auto max-h-[22rem] w-full border-t-[3px] border-t-[#006688] p-3"
    >
      <div className="border-b border-white/20 pb-1 shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <Cpu className="size-3.5 text-[#006688]" />
            <h2 className="text-xs font-bold text-text-charcoal">Explainability</h2>
          </div>
          <button 
            type="button" 
            onClick={onClose}
            className="flex size-6 items-center justify-center rounded-full hover:bg-black/5 text-text-muted transition-colors"
            aria-label="Close Explainability Panel"
          >
            <X className="size-4" />
          </button>
        </div>
        {/* Tabs navigation */}
        <div className="flex gap-1 border-b border-white/10 mt-1.5">
          <button
            type="button"
            onClick={() => setActiveTab("area")}
            className={cn(
              "px-2 py-1 text-[10px] font-bold transition-all border-b-2 -mb-[1px]",
              activeTab === "area" 
                ? "border-[#006688] text-[#006688]" 
                : "border-transparent text-text-muted hover:text-text-charcoal"
            )}
          >
            Area Info
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("route")}
            className={cn(
              "px-2 py-1 text-[10px] font-bold transition-all border-b-2 -mb-[1px]",
              activeTab === "route" 
                ? "border-[#006688] text-[#006688]" 
                : "border-transparent text-text-muted hover:text-text-charcoal"
            )}
          >
            Route Tradeoff
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("model")}
            className={cn(
              "px-2 py-1 text-[10px] font-bold transition-all border-b-2 -mb-[1px]",
              activeTab === "model" 
                ? "border-[#006688] text-[#006688]" 
                : "border-transparent text-text-muted hover:text-text-charcoal"
            )}
          >
            Model Insight
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto min-h-0 pt-3">
        {/* AREA TAB */}
        {activeTab === "area" && (
          <div className="flex flex-col gap-2">
            {zoneLoading ? (
              <div className="flex flex-col gap-2 py-4 items-center justify-center text-xs text-text-muted">
                <div className="size-5 border-2 border-[#006688] border-t-transparent animate-spin rounded-full mb-1" />
                Fetching area risk metrics...
              </div>
            ) : activeRiskLayer === "heat" ? (
              heatZoneExplanation ? (
                <>
                  <div className="flex flex-col gap-1">
                    <div className="flex items-center justify-between">
                      <h3 className="text-xs font-bold text-slate-800">{heatZoneExplanation.zone_label} Heat Explainability</h3>
                      <span className={cn("px-2 py-0.5 rounded-full text-[9px] font-bold border uppercase tracking-wider", getRiskClassBadgeColor(heatZoneExplanation.predicted_heat_risk_class))}>
                        {heatZoneExplanation.predicted_heat_risk_class}
                      </span>
                    </div>
                    <div className="flex justify-between items-center text-[10px] text-text-muted mt-0.5 font-sans">
                      <span className="font-mono">{heatZoneExplanation.zone_code}</span>
                      <span>Date: {heatZoneExplanation.date}</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2 mt-0.5 bg-white/40 border border-white/60 rounded-xl p-2 text-[10px]">
                    <div>
                      <span className="text-text-muted block font-sans">Predicted Anomaly</span>
                      <span className="font-bold text-[#ba1a1a]">+{heatZoneExplanation.predicted_heat_anomaly_c.toFixed(1)}°C</span>
                    </div>
                    <div>
                      <span className="text-text-muted block font-sans">Heat Risk Score</span>
                      <span className="font-bold text-text-charcoal font-sans">{heatZoneExplanation.predicted_heat_risk_score.toFixed(4)}</span>
                    </div>
                  </div>

                  <div className="text-[10px] bg-white/40 border border-white/60 rounded-xl p-2 leading-relaxed text-text-charcoal font-sans">
                    <p className="font-bold text-text-charcoal mb-0.5">Why this heat risk?</p>
                    <p className="mb-1 font-bold">{heatZoneExplanation.summary}</p>
                    <p className="text-text-muted border-t border-white/25 pt-1 mt-1 font-normal leading-normal">{heatZoneExplanation.explanation_text}</p>
                  </div>

                  <div className="flex flex-col gap-1.5 mt-0.5">
                    <h4 className="text-[10px] font-bold uppercase tracking-wider text-text-muted">Main Risk Drivers</h4>
                    
                    {heatZoneExplanation.top_factors.map((factor, idx) => (
                      <div key={factor.factor + idx} className="flex flex-col gap-0.5 border border-white/60 bg-white/40 rounded-xl p-2 shadow-sm transition-all hover:shadow-md">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-1.5 min-w-0">
                            {getFactorIcon(factor.factor)}
                            <span className="text-[11px] font-bold text-slate-700 truncate">{factor.label}</span>
                          </div>
                          <span className="text-[11px] font-bold font-mono text-text-charcoal bg-white/60 px-1.5 py-0.5 rounded shrink-0 border border-white/50">
                            {factor.value.toLocaleString()}
                          </span>
                        </div>
                        <p className="text-[10px] text-text-muted mt-0.5 leading-snug">{factor.reason}</p>
                        {factor.impact !== "neutral" && (
                          <div className="mt-1">
                            <span className={cn(
                              "px-1.5 py-0.5 rounded text-[8px] font-bold uppercase tracking-wider border",
                              factor.impact.includes("increases") 
                                ? "bg-[#ffdad6]/80 text-[#ba1a1a] border-[#ffdad6]" 
                                : "bg-[#83fba5]/20 text-[#006d36] border-[#83fba5]/40"
                            )}>
                              {factor.impact}
                            </span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>

                  <div className="border-t border-white/20 my-2" />

                  {/* Footer Notes Removed */}
                </>
              ) : (
                <div className="flex flex-col py-3 items-center text-center justify-center text-[10px] text-text-muted leading-normal font-sans">
                  <Info className="size-4.5 text-text-muted/60 mb-1" />
                  <p className="font-bold text-text-charcoal mb-0.5 font-sans">No Area Selected</p>
                  Select a heat zone to see what drives the heat estimate.
                </div>
              )
            ) : zoneExplanation ? (
              <>
                <div className="flex flex-col gap-1">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xs font-bold text-slate-800">{zoneExplanation.zone_label} Explainability</h3>
                    <span className={cn("px-2 py-0.5 rounded-full text-[9px] font-bold border uppercase tracking-wider", getRiskClassBadgeColor(zoneExplanation.risk_class))}>
                      {zoneExplanation.risk_label}
                    </span>
                  </div>
                  <p className="text-[10px] text-text-muted font-mono mt-0.5">{zoneExplanation.zone_code}</p>
                </div>

                <div className="text-[10px] bg-white/40 border border-white/60 rounded-xl p-2 leading-relaxed text-text-charcoal">
                  <p className="font-bold text-text-charcoal mb-0.5">Why this area?</p>
                  {zoneExplanation.summary}
                </div>

                <div className="flex flex-col gap-1.5 mt-0.5">
                  <h4 className="text-[10px] font-bold uppercase tracking-wider text-text-muted">Main Risk Drivers</h4>
                  
                  {zoneExplanation.top_factors.map((factor, idx) => (
                    <div key={factor.factor + idx} className="flex flex-col gap-0.5 border border-white/60 bg-white/40 rounded-xl p-2 shadow-sm transition-all hover:shadow-md">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1.5 min-w-0">
                          {getFactorIcon(factor.factor)}
                          <span className="text-[11px] font-bold text-slate-700 truncate">{factor.label}</span>
                        </div>
                        <span className="text-[11px] font-bold font-mono text-text-charcoal bg-white/60 px-1.5 py-0.5 rounded shrink-0 border border-white/50">
                          {factor.value.toLocaleString()}
                        </span>
                      </div>
                      <p className="text-[10px] text-text-muted mt-0.5 leading-snug">{factor.reason}</p>
                      {factor.impact !== "neutral" && (
                        <div className="mt-1">
                          <span className={cn(
                            "px-1.5 py-0.5 rounded text-[8px] font-bold uppercase tracking-wider border",
                            factor.impact.includes("increases") 
                              ? "bg-[#ffdad6]/80 text-[#ba1a1a] border-[#ffdad6]" 
                              : "bg-[#83fba5]/20 text-[#006d36] border-[#83fba5]/40"
                          )}>
                            {factor.impact}
                          </span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                <div className="border-t border-white/20 my-2" />

                {/* Footer Notes Removed */}
              </>
            ) : (
              <div className="flex flex-col py-3 items-center text-center justify-center text-[10px] text-text-muted leading-normal">
                <Info className="size-4.5 text-text-muted/60 mb-1" />
                <p className="font-bold text-text-charcoal mb-0.5">No Area Selected</p>
                Click a risk zone on the map to see explainability.
              </div>
            )}
          </div>
        )}

        {/* ROUTE TAB */}
        {activeTab === "route" && (
          <div className="flex flex-col gap-2">
            {activeRiskLayer === "heat" ? (
              <div className="flex flex-col py-3 items-center text-center justify-center text-[10px] text-text-muted leading-normal">
                <RouteIcon className="size-4.5 text-text-muted/60 mb-1" />
                <p className="font-bold text-text-charcoal mb-0.5">Route Tradeoff Unavailable</p>
                Route tradeoff analysis is optimized for Rain Risk routing. Switch to Rain mode to view route comparisons.
              </div>
            ) : routeLoading ? (
              <div className="flex flex-col gap-2 py-4 items-center justify-center text-xs text-text-muted">
                <div className="size-5 border-2 border-[#006688] border-t-transparent animate-spin rounded-full mb-1" />
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
                        ? "bg-[#ffdad6]/80 text-[#ba1a1a] border-[#ffdad6]"
                        : routeExplanation.recommendation === "no_distinct_safer_alternative"
                          ? "bg-white/40 text-[#8b5000] border-[#ffdcbe]"
                          : "bg-[#83fba5]/20 text-[#006d36] border-[#83fba5]/40"
                    )}>
                      {routeExplanation.recommendation_label}
                    </span>
                  </div>
                </div>

                <div className="text-[10px] bg-white/40 border border-white/60 rounded-xl p-2 leading-relaxed text-text-charcoal">
                  {routeExplanation.summary}
                </div>

                <div className="flex flex-col gap-1.5 mt-0.5">
                  <h4 className="text-[10px] font-bold uppercase tracking-wider text-text-muted">Tradeoff Drivers</h4>
                  
                  {routeExplanation.route_reasons.map((reason, idx) => {
                    const isRiskRed = reason.label.includes("Risk");
                    const percentVal = parseFloat(reason.value);
                    const isNeutral = isRiskRed && percentVal <= 0;
                    
                    return (
                      <div key={reason.label + idx} className="flex flex-col gap-0.5 border border-white/60 bg-white/40 rounded-xl p-2 shadow-sm">
                        <div className="flex items-center justify-between">
                          <span className="text-[11px] font-bold text-slate-700">{reason.label}</span>
                          <span className={cn(
                            "text-[11px] font-bold font-mono px-1.5 py-0.5 rounded shrink-0",
                            isNeutral 
                              ? "bg-white/50 text-text-muted" 
                              : isRiskRed 
                                ? "bg-[#83fba5]/30 text-[#006d36]" 
                                : "bg-[#ffdcbe]/40 text-[#8b5000]"
                          )}>
                            {reason.value}
                          </span>
                        </div>
                        <p className="text-[10px] text-text-muted mt-0.5 leading-snug">{reason.reason}</p>
                      </div>
                    );
                  })}
                </div>

                <div className="grid grid-cols-2 gap-2 mt-1.5">
                  <div className="border border-white/60 bg-white/30 rounded-xl p-2 flex flex-col gap-0.5">
                    <p className="text-[10px] font-bold text-text-charcoal">Normal Route</p>
                    <p className="text-[10px] text-text-muted leading-normal">{routeExplanation.normal_route_explanation.summary}</p>
                    <div className="flex justify-between items-center mt-auto pt-1 text-[9px] font-bold text-text-muted border-t border-white/10">
                      <span>Segments: {routeExplanation.normal_route_explanation.high_risk_segments}</span>
                      <span>Risk: {routeExplanation.normal_route_explanation.mean_risk_score.toFixed(3)}</span>
                    </div>
                  </div>

                  <div className="border border-white/60 bg-white/30 rounded-xl p-2 flex flex-col gap-0.5">
                    <p className="text-[10px] font-bold text-[#006688]">Weather-Safe</p>
                    <p className="text-[10px] text-text-muted leading-normal">{routeExplanation.safe_route_explanation.summary}</p>
                    <div className="flex justify-between items-center mt-auto pt-1 text-[9px] font-bold text-text-muted border-t border-white/10">
                      <span>Segments: {routeExplanation.safe_route_explanation.high_risk_segments}</span>
                      <span>Risk: {routeExplanation.safe_route_explanation.mean_risk_score.toFixed(3)}</span>
                    </div>
                  </div>
                </div>

                {/* Disclaimer Removed */}
              </>
            ) : (
              <div className="flex flex-col py-3 items-center text-center justify-center text-[10px] text-text-muted leading-normal">
                <RouteIcon className="size-4.5 text-text-muted/60 mb-1" />
                <p className="font-bold text-text-charcoal mb-0.5">No Active Route</p>
                Plan custom points on the map to see route tradeoffs.
              </div>
            )}
          </div>
        )}

        {/* MODEL TAB */}
        {activeTab === "model" && (
          <div className="flex flex-col gap-2">
            {activeRiskLayer === "heat" ? (
              heatModelSummary ? (
                <>
                  <div className="flex flex-col gap-1 border-b border-white/10 pb-2">
                    <h3 className="text-xs font-bold text-text-charcoal">Model: {heatModelSummary.model_name}</h3>
                    <p className="text-[10px] text-text-muted mt-0.5 leading-snug">
                      Target: {heatModelSummary.target} &bull; Feature count: {heatModelSummary.feature_count}
                    </p>
                  </div>

                  <div className="flex flex-col gap-2">
                    <h4 className="text-[10px] font-bold uppercase tracking-wider text-text-muted">Top Heat Drivers</h4>
                    
                    {heatModelSummary.top_global_features.slice(0, 5).map((feat, idx) => (
                      <div key={feat.feature + idx} className="flex flex-col gap-0.5 border border-white/60 bg-white/40 rounded-xl p-2 shadow-sm">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-1.5 min-w-0">
                            {getFactorIcon(feat.feature)}
                            <span className="text-[11px] font-bold text-slate-700 truncate">{feat.label}</span>
                          </div>
                          <span className="text-[11px] font-bold font-mono text-text-charcoal bg-white/60 px-1.5 py-0.5 rounded shrink-0 border border-white/50">
                            {feat.importance.toFixed(4)}
                          </span>
                        </div>
                        <p className="text-[10px] text-text-muted mt-0.5 leading-snug">{feat.reason}</p>
                      </div>
                    ))}
                  </div>

                  <div className="border-t border-white/20 my-2" />

                  <div className="flex flex-col gap-1 bg-white/40 border border-white/60 rounded-xl p-2">
                    <div className="text-[10px] font-bold text-text-charcoal mb-1">Data Authenticity</div>
                    <div className="flex flex-col gap-1 text-[9.5px] text-text-muted">
                      <div className="flex justify-between">
                        <span>Landsat Observed Rows:</span>
                        <span className="font-bold text-text-charcoal">{heatModelSummary.data_authenticity.landsat_rows}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Fallback Simulated Rows:</span>
                        <span className="font-bold text-text-charcoal">{heatModelSummary.data_authenticity.fallback_rows}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Ready For Training:</span>
                        <span className="font-bold text-text-charcoal">{heatModelSummary.data_authenticity.ready_for_training ? "Yes" : "No"}</span>
                      </div>
                    </div>
                  </div>

                  {/* Honesty Note Removed */}
                </>
              ) : (
                <div className="text-[11px] text-rose-500 py-4 font-semibold">
                  Unable to load heat model summary parameters.
                </div>
              )
            ) : modelLoading ? (
              <div className="flex flex-col gap-2 py-4 items-center justify-center text-xs text-text-muted">
                <div className="size-5 border-2 border-[#006688] border-t-transparent animate-spin rounded-full mb-1" />
                Loading model configuration...
              </div>
            ) : modelSummary ? (
              <>
                <div className="flex flex-col gap-1 border-b border-white/10 pb-2">
                  <h3 className="text-xs font-bold text-text-charcoal">Model: {modelSummary.model_name}</h3>
                  <p className="text-[10px] text-text-muted mt-0.5 leading-snug">
                    Type: {modelSummary.model_type} &bull; Target: {modelSummary.target}
                  </p>
                </div>

                <div className="flex flex-col gap-2">
                  <h4 className="text-[10px] font-bold uppercase tracking-wider text-text-muted">Top Risk Factor Weights</h4>
                  
                  {modelSummary.top_global_features.slice(0, 5).map((feat, idx) => (
                    <div key={feat.feature + idx} className="flex flex-col gap-0.5 border border-white/60 bg-white/40 rounded-xl p-2 shadow-sm">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1.5 min-w-0">
                          {getFactorIcon(feat.feature)}
                          <span className="text-[11px] font-bold text-slate-700 truncate">{feat.label}</span>
                        </div>
                        <span className="text-[11px] font-bold font-mono text-text-charcoal bg-white/60 px-1.5 py-0.5 rounded shrink-0 border border-white/50">
                          {feat.importance.toFixed(4)}
                        </span>
                      </div>
                      <p className="text-[10px] text-text-muted mt-0.5 leading-snug">{feat.reason}</p>
                    </div>
                  ))}
                </div>

                <div className="border-t border-white/20 my-2" />

                <div className="flex flex-col gap-1 bg-white/40 border border-white/60 rounded-xl p-2">
                  <button
                    type="button"
                    onClick={() => setLimitationsOpen(!limitationsOpen)}
                    className="flex justify-between items-center w-full text-[10px] font-bold text-text-charcoal hover:text-black"
                  >
                    <span>Known Model Limitations</span>
                    <span>{limitationsOpen ? "▲" : "▼"}</span>
                  </button>
                  
                  {limitationsOpen && (
                    <ul className="list-disc pl-4 text-[9.5px] text-text-muted leading-normal flex flex-col gap-1 mt-1 border-t border-white/10 pt-1.5">
                      {modelSummary.known_limitations.map((limit, idx) => (
                        <li key={idx}>{limit}</li>
                      ))}
                    </ul>
                  )}
                </div>

                {/* Honesty Note Removed */}
              </>
            ) : (
              <div className="text-[11px] text-rose-500 py-4 font-semibold">
                Unable to load model summary parameters.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
