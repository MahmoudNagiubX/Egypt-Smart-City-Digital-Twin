import React from "react";

export const Legend: React.FC = () => {
  return (
    <div className="space-y-2">
      <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5">Map Legend</h3>
      <div className="bg-slate-900/30 p-3 rounded border border-slate-900 space-y-2.5">
        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-300 font-medium">Predicted Risk</span>
          <div className="flex items-center space-x-2">
            <span className="flex items-center space-x-1">
              <span className="h-2 w-2 rounded-full bg-emerald-500 block"></span>
              <span className="text-[10px] text-emerald-400 font-semibold">Low</span>
            </span>
            <span className="flex items-center space-x-1">
              <span className="h-2 w-2 rounded-full bg-amber-500 block"></span>
              <span className="text-[10px] text-amber-400 font-semibold">Med</span>
            </span>
            <span className="flex items-center space-x-1">
              <span className="h-2 w-2 rounded-full bg-red-500 block"></span>
              <span className="text-[10px] text-red-400 font-semibold">High</span>
            </span>
          </div>
        </div>
        
        <div className="border-t border-slate-900 pt-2.5 space-y-1.5">
          <div className="flex items-center justify-between text-[10px] text-slate-400">
            <span className="flex items-center space-x-2">
              <span className="h-0.5 w-4 border-t-2 border-dashed border-slate-400 block"></span>
              <span>Normal Route</span>
            </span>
            <span className="flex items-center space-x-2">
              <span className="h-0.5 w-4 bg-cyan-400 block shadow-[0_0_8px_#22d3ee]"></span>
              <span className="text-cyan-400 font-medium">Weather-Safe</span>
            </span>
          </div>
          <div className="flex items-center space-x-2 text-[10px] text-slate-400">
            <span className="h-2.5 w-2.5 rounded-full bg-red-500 border border-slate-100 flex items-center justify-center shrink-0"></span>
            <span>Emergency Facility</span>
          </div>
        </div>
      </div>
    </div>
  );
};
