import React from "react";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { LayerToggles } from "../types/api";

interface LayerToggleProps {
  layers: LayerToggles;
  onToggle: (key: keyof LayerToggles) => void;
}

export const LayerToggle: React.FC<LayerToggleProps> = ({ layers, onToggle }) => {
  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2.5">Map Base Layers</h3>
        <div className="space-y-3 bg-slate-900/30 p-3 rounded border border-slate-900">
          <div className="flex items-center justify-between">
            <Label htmlFor="boundary-toggle" className="text-xs text-slate-300 font-medium">Nasr City Boundary</Label>
            <Switch 
              id="boundary-toggle" 
              checked={layers.boundary} 
              onCheckedChange={() => onToggle("boundary")}
            />
          </div>
          <div className="flex items-center justify-between">
            <Label htmlFor="grid-toggle" className="text-xs text-slate-300 font-medium">500m Elevation Grid</Label>
            <Switch 
              id="grid-toggle" 
              checked={layers.grid} 
              onCheckedChange={() => onToggle("grid")}
            />
          </div>
          <div className="flex items-center justify-between">
            <Label htmlFor="facilities-toggle" className="text-xs text-slate-300 font-medium">Emergency Facilities</Label>
            <Switch 
              id="facilities-toggle" 
              checked={layers.facilities} 
              onCheckedChange={() => onToggle("facilities")}
            />
          </div>
        </div>
      </div>

      <div>
        <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2.5">ML Risk Assessments</h3>
        <div className="space-y-3 bg-slate-900/30 p-3 rounded border border-slate-900">
          <div className="flex items-center justify-between">
            <Label htmlFor="risk-summary-toggle" className="text-xs text-slate-300 font-medium">Historic Risk Summary</Label>
            <Switch 
              id="risk-summary-toggle" 
              checked={layers.riskSummary} 
              onCheckedChange={() => onToggle("riskSummary")}
            />
          </div>
          <div className="flex items-center justify-between">
            <Label htmlFor="top-rain-toggle" className="text-xs text-slate-300 font-medium">Top Rain Event Risk (Historic)</Label>
            <Switch 
              id="top-rain-toggle" 
              checked={layers.topRainRisk} 
              onCheckedChange={() => onToggle("topRainRisk")}
            />
          </div>
          <div className="flex items-center justify-between">
            <Label htmlFor="latest-toggle" className="text-xs text-slate-300 font-medium">Latest Rainfall Event Risk</Label>
            <Switch 
              id="latest-toggle" 
              checked={layers.latestRisk} 
              onCheckedChange={() => onToggle("latestRisk")}
            />
          </div>
          <div className="flex items-center justify-between">
            <Label htmlFor="selected-toggle" className="text-xs text-slate-300 font-medium">Selected Event Risk</Label>
            <Switch 
              id="selected-toggle" 
              checked={layers.selectedRisk} 
              onCheckedChange={() => onToggle("selectedRisk")}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
