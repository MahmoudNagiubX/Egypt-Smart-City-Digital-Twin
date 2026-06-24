import React from "react";
import { Map as MapIcon } from "lucide-react";

export const Legend: React.FC = () => (
  <section className="flex flex-col gap-2" aria-labelledby="legend-title">
    <div className="flex items-center gap-2">
      <MapIcon className="size-4 text-primary" />
      <div>
        <h2 id="legend-title" className="text-[11px] font-bold uppercase tracking-[0.14em]">Legend</h2>
        <p className="text-[10px] text-muted-foreground">Risk, routes, and facilities</p>
      </div>
    </div>
    <div className="flex flex-col gap-3 rounded-xl border border-slate-200/50 bg-gradient-to-b from-white to-[#C4E2F5]/10 p-3 shadow-sm">
      <div className="flex flex-col gap-1.5">
        <span className="text-[9px] font-bold uppercase tracking-wider text-muted-foreground">Today’s Rain Risk</span>
        <div className="flex flex-col gap-1">
          <span className="flex items-center gap-2 text-[10px] font-medium text-muted-foreground">
            <span className="size-2.5 rounded-sm bg-[#34d399]" />
            <span>Low: Minimal risk</span>
          </span>
          <span className="flex items-center gap-2 text-[10px] font-medium text-muted-foreground">
            <span className="size-2.5 rounded-sm bg-amber-500" />
            <span>Medium: Caution area</span>
          </span>
          <span className="flex items-center gap-2 text-[10px] font-medium text-muted-foreground">
            <span className="size-2.5 rounded-sm bg-red-500" />
            <span>High: Avoid if possible</span>
          </span>
        </div>
      </div>
      <div className="flex flex-col gap-1.5 border-t pt-2.5">
        <span className="text-[9px] font-bold uppercase tracking-wider text-muted-foreground">Routes</span>
        <div className="flex flex-col gap-1 text-[10px] text-muted-foreground">
          <span className="flex items-center gap-2">
            <span className="h-0.5 w-5 bg-[#1591DC]" />
            <span>Blue: Recommended / safe route</span>
          </span>
          <span className="flex items-center gap-2">
            <span className="h-0.5 w-5 bg-[#E63946]" />
            <span>Red: Risky normal route</span>
          </span>
          <span className="flex items-center gap-2">
            <span className="w-5 border-t border-dashed border-[#8186D5]" />
            <span>Dashed: Alternative comparison route</span>
          </span>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-2 border-t pt-2.5 text-[10px] text-muted-foreground">
        <span className="flex items-center gap-2"><span className="flex size-4 items-center justify-center rounded-full bg-primary text-[9px] font-bold text-primary-foreground">A</span>Origin</span>
        <span className="flex items-center gap-2"><span className="flex size-4 items-center justify-center rounded-full bg-secondary text-[9px] font-bold text-secondary-foreground font-mono">B</span>Destination</span>
        <span className="col-span-2 flex items-center gap-2"><span aria-hidden="true">🏥 🚑 🚓</span>Places use category icons</span>
      </div>
    </div>
  </section>
);
