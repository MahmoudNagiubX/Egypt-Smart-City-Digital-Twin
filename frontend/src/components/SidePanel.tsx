import React from "react";
import { AlertCircle } from "lucide-react";

interface SidePanelProps {
  children: React.ReactNode;
}

export const SidePanel: React.FC<SidePanelProps> = ({ children }) => {
  return (
    <div className="w-80 h-full flex flex-col bg-slate-950/70 border-r border-slate-900/60 backdrop-blur-md text-slate-100 shrink-0">
      <div className="p-4 border-b border-slate-900/60 flex items-center justify-between">
        <div>
          <h1 className="text-sm font-bold text-slate-100 tracking-wide">Nasr City Weather-Impact</h1>
          <p className="text-[9px] text-cyan-400 font-bold tracking-widest mt-0.5">EMERGENCY MOBILITY MODULE</p>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {children}
      </div>

      <div className="p-3 border-t border-slate-900/60 bg-slate-950/50">
        <div className="flex items-start space-x-2 text-[9px] text-slate-400 bg-slate-900/40 p-2.5 rounded border border-slate-900">
          <AlertCircle className="h-3.5 w-3.5 text-cyan-500 shrink-0 mt-0.5" />
          <p className="leading-relaxed">
            <strong className="text-slate-300 font-bold block mb-0.5">SYSTEM DISCLAIMER:</strong>
            Predictions are model-estimated weather-impact risk scores derived from real observed and satellite data. They are not verified street-level flood incident labels. Routes are decision-support prototype outputs, not official emergency dispatch instructions.
          </p>
        </div>
      </div>
    </div>
  );
};
