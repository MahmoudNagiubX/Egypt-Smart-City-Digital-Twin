import React from "react";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { LayerToggles } from "../types/api";
import {
  Ambulance,
  Flame,
  GraduationCap,
  Hospital,
  Landmark,
  Layers3,
  Map,
  MapPin,
  Route,
  School,
  Shield,
  ShoppingBag,
  Stethoscope,
} from "lucide-react";

interface LayerToggleProps {
  layers: LayerToggles;
  onToggle: (key: keyof LayerToggles) => void;
  riskFillOpacity: number;
  setRiskFillOpacity: (val: number) => void;
  gridLineOpacity: number;
  setGridLineOpacity: (val: number) => void;
}

const ToggleRow = ({
  id,
  label,
  checked,
  onChange,
  icon: Icon,
}: {
  id: string;
  label: string;
  checked: boolean;
  onChange: () => void;
  icon?: React.ElementType;
}) => (
  <div className="flex items-center justify-between gap-3 rounded-lg px-1 py-1.5 transition-colors hover:bg-slate-100/50">
    <Label htmlFor={id} className="flex min-w-0 cursor-pointer items-center gap-2">
      {Icon && <Icon className="size-4 shrink-0 text-muted-foreground" />}
      <span className="min-w-0 text-xs font-semibold text-foreground/80">{label}</span>
    </Label>
    <Switch id={id} checked={checked} onCheckedChange={onChange} size="sm" />
  </div>
);

const SectionTitle = ({
  icon: Icon,
  title,
  detail,
}: {
  icon: React.ElementType;
  title: string;
  detail: string;
}) => (
  <div className="flex items-center gap-2">
    <Icon className="size-4 text-primary" />
    <div>
      <h2 className="text-[11px] font-bold uppercase tracking-[0.14em] text-foreground">{title}</h2>
      <p className="text-[9px] text-muted-foreground">{detail}</p>
    </div>
  </div>
);

export const LayerToggle: React.FC<LayerToggleProps> = ({
  layers,
  onToggle,
  riskFillOpacity,
  setRiskFillOpacity,
  gridLineOpacity,
  setGridLineOpacity,
}) => (
  <div className="flex flex-col gap-4">
    <section className="flex flex-col gap-2 rounded-xl border border-slate-200/50 bg-white/70 p-3 shadow-sm transition-all hover:bg-white/80">
      <SectionTitle icon={Map} title="Map Layers" detail="Reference data" />
      <div className="flex flex-col gap-0.5 mt-1.5">
        <ToggleRow
          id="boundary-toggle"
          label="Boundary"
          checked={layers.boundary}
          onChange={() => onToggle("boundary")}
          icon={MapPin}
        />
        <ToggleRow
          id="grid-toggle"
          label="Grid Overlay"
          checked={layers.grid}
          onChange={() => onToggle("grid")}
          icon={Layers3}
        />
        <ToggleRow
          id="roads-labels-toggle"
          label="Streets & Labels"
          checked={layers.roadsLabels}
          onChange={() => onToggle("roadsLabels")}
          icon={Route}
        />
      </div>
    </section>

    <section className="flex flex-col gap-2 rounded-xl border border-slate-200/50 bg-white/70 p-3 shadow-sm transition-all hover:bg-white/80">
      <SectionTitle icon={Layers3} title="Risk Layers" detail="Impact surfaces" />
      <div className="flex flex-col gap-0.5 mt-1.5">
        <ToggleRow
          id="live-risk-toggle"
          label="Live Weather Risk"
          checked={layers.liveRisk}
          onChange={() => onToggle("liveRisk")}
        />
        <ToggleRow
          id="selected-toggle"
          label="Selected Event"
          checked={layers.selectedRisk}
          onChange={() => onToggle("selectedRisk")}
        />
        <ToggleRow
          id="latest-toggle"
          label="Latest Event"
          checked={layers.latestRisk}
          onChange={() => onToggle("latestRisk")}
        />
        <ToggleRow
          id="top-rain-toggle"
          label="Highest-Rain Event"
          checked={layers.topRainRisk}
          onChange={() => onToggle("topRainRisk")}
        />
        <ToggleRow
          id="risk-summary-toggle"
          label="Historic Summary"
          checked={layers.riskSummary}
          onChange={() => onToggle("riskSummary")}
        />
      </div>
      <div className="mt-2.5 flex flex-col gap-2.5 border-t pt-2.5">
        <div className="flex flex-col gap-1">
          <div className="flex justify-between text-[9px] font-bold uppercase tracking-wider text-muted-foreground">
            <span>Risk Fill Opacity</span>
            <span>{Math.round(riskFillOpacity * 100)}%</span>
          </div>
          <input
            type="range"
            min="0.10"
            max="0.70"
            step="0.05"
            value={riskFillOpacity}
            onChange={(e) => setRiskFillOpacity(parseFloat(e.target.value))}
            className="h-1 w-full cursor-pointer appearance-none rounded-lg bg-slate-200/80 accent-[#1591DC]"
          />
        </div>
        <div className="flex flex-col gap-1">
          <div className="flex justify-between text-[9px] font-bold uppercase tracking-wider text-muted-foreground">
            <span>Grid Line Opacity</span>
            <span>{Math.round(gridLineOpacity * 100)}%</span>
          </div>
          <input
            type="range"
            min="0.05"
            max="0.50"
            step="0.05"
            value={gridLineOpacity}
            onChange={(e) => setGridLineOpacity(parseFloat(e.target.value))}
            className="h-1 w-full cursor-pointer appearance-none rounded-lg bg-slate-200/80 accent-[#1591DC]"
          />
        </div>
      </div>
    </section>

    <Separator className="my-1" />

    <section className="flex flex-col gap-2 rounded-xl border border-slate-200/50 bg-white/70 p-3 shadow-sm transition-all hover:bg-white/80">
      <SectionTitle icon={Landmark} title="Places" detail="Points of interest" />
      <div className="flex flex-col gap-0.5 mt-1.5 max-h-56 overflow-y-auto pr-1">
        <ToggleRow
          id="hospitals-toggle"
          label="Hospitals"
          checked={layers.hospitals}
          onChange={() => onToggle("hospitals")}
          icon={Hospital}
        />
        <ToggleRow
          id="clinics-toggle"
          label="Clinics"
          checked={layers.clinics}
          onChange={() => onToggle("clinics")}
          icon={Stethoscope}
        />
        <ToggleRow
          id="mosques-toggle"
          label="Mosques"
          checked={layers.mosques}
          onChange={() => onToggle("mosques")}
          icon={Landmark}
        />
        <ToggleRow
          id="malls-toggle"
          label="Malls"
          checked={layers.malls}
          onChange={() => onToggle("malls")}
          icon={ShoppingBag}
        />
        <ToggleRow
          id="schools-toggle"
          label="Schools"
          checked={layers.schools}
          onChange={() => onToggle("schools")}
          icon={School}
        />
        <ToggleRow
          id="universities-toggle"
          label="Universities"
          checked={layers.universities}
          onChange={() => onToggle("universities")}
          icon={GraduationCap}
        />
        <ToggleRow
          id="police-toggle"
          label="Police"
          checked={layers.police}
          onChange={() => onToggle("police")}
          icon={Shield}
        />
        <ToggleRow
          id="fire-stations-toggle"
          label="Fire Stations"
          checked={layers.fireStations}
          onChange={() => onToggle("fireStations")}
          icon={Flame}
        />
        <ToggleRow
          id="emergency-toggle"
          label="Emergency Facilities"
          checked={layers.emergency}
          onChange={() => onToggle("emergency")}
          icon={Ambulance}
        />
      </div>
    </section>

    <section className="flex flex-col gap-2 rounded-xl border border-slate-200/50 bg-white/70 p-3 shadow-sm transition-all hover:bg-white/80">
      <SectionTitle icon={Route} title="Routing" detail="Compare safe paths" />
      <p className="px-1 text-[10px] leading-relaxed text-muted-foreground mt-1">
        Click the map for origin and destination. Route visibility controls stay in the floating panel.
      </p>
    </section>
  </div>
);
