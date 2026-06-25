import React from "react";
import { Map as MapIcon } from "lucide-react";

interface LegendProps {
  activeRiskLayer?: "rain" | "heat";
}

export const Legend: React.FC<LegendProps> = ({ activeRiskLayer = "rain" }) => (
  <section className="flex flex-col gap-2.5" aria-labelledby="legend-title">
    <div className="flex items-center gap-2">
      <MapIcon className="size-4 text-[#006688]" />
      <div>
        <h2 id="legend-title" className="text-[11px] font-bold uppercase tracking-[0.14em] text-text-charcoal">Legend</h2>
        <p className="text-[9px] text-text-muted">
          {activeRiskLayer === "heat" ? "Heat exposure and indicators" : "Risk, routes, and facilities"}
        </p>
      </div>
    </div>
    <div className="flex flex-col gap-3.5 pl-1.5 mt-1 border-t border-white/20 pt-2.5">
      {activeRiskLayer === "heat" ? (
        <div className="flex flex-col gap-2">
          <span className="text-[9px] font-bold uppercase tracking-wider text-text-muted">Satellite Heat Estimate</span>
          <div className="flex flex-col gap-1.5">
            <span className="flex items-center gap-2.5 text-[10px] font-medium text-text-muted">
              <span className="size-2.5 rounded-sm bg-[#fef08a] border border-black/5" />
              <span>Low Heat</span>
            </span>
            <span className="flex items-center gap-2.5 text-[10px] font-medium text-text-muted">
              <span className="size-2.5 rounded-sm bg-[#f97316] border border-black/5" />
              <span>Medium Heat</span>
            </span>
            <span className="flex items-center gap-2.5 text-[10px] font-medium text-text-muted">
              <span className="size-2.5 rounded-sm bg-[#dc2626] border border-black/5" />
              <span>High Heat</span>
            </span>
          </div>
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          <span className="text-[9px] font-bold uppercase tracking-wider text-text-muted">Today’s Rain Risk</span>
          <div className="flex flex-col gap-1.5">
            <span className="flex items-center gap-2.5 text-[10px] font-medium text-text-muted">
              <span className="size-2.5 rounded-sm bg-[#83fba5] border border-black/5" />
              <span>Low: Minimal risk</span>
            </span>
            <span className="flex items-center gap-2.5 text-[10px] font-medium text-text-muted">
              <span className="size-2.5 rounded-sm bg-[#ff9e2a] border border-black/5" />
              <span>Medium: Caution area</span>
            </span>
            <span className="flex items-center gap-2.5 text-[10px] font-medium text-text-muted">
              <span className="size-2.5 rounded-sm bg-[#ba1a1a] border border-black/5" />
              <span>High: Avoid if possible</span>
            </span>
          </div>
        </div>
      )}
      
      {activeRiskLayer === "rain" && (
        <div className="flex flex-col gap-2 border-t border-white/20 pt-2.5">
          <span className="text-[9px] font-bold uppercase tracking-wider text-text-muted">Routes</span>
          <div className="flex flex-col gap-1.5 text-[10px] text-text-muted">
            <span className="flex items-center gap-2.5">
              <span className="h-0.75 w-5 bg-[#006688] rounded-full" />
              <span>Blue: Recommended / safe route</span>
            </span>
            <span className="flex items-center gap-2.5">
              <span className="h-0.75 w-5 bg-[#ba1a1a] rounded-full" />
              <span>Red: Risky normal route</span>
            </span>
            <span className="flex items-center gap-2.5">
              <span className="w-5 border-t border-dashed border-[#8b5000]" />
              <span>Dashed: Alternative comparison route</span>
            </span>
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 gap-2 border-t border-white/20 pt-2.5 text-[10px] text-text-muted">
        <span className="flex items-center gap-2">
          <span className="flex size-4 items-center justify-center rounded-full bg-[#006688] text-[9px] font-bold text-white">A</span>
          Origin
        </span>
        <span className="flex items-center gap-2">
          <span className="flex size-4 items-center justify-center rounded-full bg-[#006d36] text-[9px] font-bold text-white">B</span>
          Destination
        </span>
        <span className="col-span-2 flex items-center gap-2 mt-1">
          <span aria-hidden="true" className="tracking-wide">🏥 🚑 🚓</span>
          <span>Places use category icons</span>
        </span>
      </div>
    </div>
  </section>
);
