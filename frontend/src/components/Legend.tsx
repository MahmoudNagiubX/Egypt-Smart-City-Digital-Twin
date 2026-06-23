import React from "react";
import { Map as MapIcon } from "lucide-react";

const RiskKey = ({ color, label }: { color: string; label: string }) => (
  <span className="flex items-center gap-1.5 text-[10px] font-medium text-muted-foreground">
    <span className={`size-2.5 rounded-sm ${color}`} />{label}
  </span>
);

export const Legend: React.FC = () => (
  <section className="flex flex-col gap-2" aria-labelledby="legend-title">
    <div className="flex items-center gap-2">
      <MapIcon className="text-primary" />
      <div>
        <h2 id="legend-title" className="text-[11px] font-bold uppercase tracking-[0.14em]">Legend</h2>
        <p className="text-[10px] text-muted-foreground">Risk, routes, and facilities</p>
      </div>
    </div>
    <div className="flex flex-col gap-3 rounded-xl border bg-slate-50/70 p-3">
      <div className="flex items-center justify-between gap-2">
        <RiskKey color="bg-emerald-500" label="Low" />
        <RiskKey color="bg-amber-500" label="Medium" />
        <RiskKey color="bg-red-500" label="High" />
      </div>
      <div className="grid grid-cols-2 gap-2 border-t pt-3 text-[10px] text-muted-foreground">
        <span className="flex items-center gap-2"><span className="w-5 border-t-2 border-dashed border-[#8186D5]" />Normal</span>
        <span className="flex items-center gap-2 font-medium text-primary"><span className="h-0.5 w-5 bg-[#1591DC] shadow-[0_0_6px_rgba(21,145,220,0.5)]" />Weather-safe</span>
        <span className="col-span-2 flex items-center gap-2"><span className="size-3 rounded-full border-2 border-white bg-[#494CA2] shadow-sm" />Emergency facility</span>
      </div>
    </div>
  </section>
);
