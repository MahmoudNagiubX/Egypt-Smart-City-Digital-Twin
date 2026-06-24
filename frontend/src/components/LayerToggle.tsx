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
}

const ToggleRow = ({ id, label, description, checked, onChange, icon: Icon }: {
  id: string;
  label: string;
  description?: string;
  checked: boolean;
  onChange: () => void;
  icon?: React.ElementType;
}) => (
  <div className="flex items-center justify-between gap-3 rounded-lg px-1 py-1.5">
    <Label htmlFor={id} className="flex min-w-0 cursor-pointer items-center gap-2.5">
      {Icon && <Icon className="shrink-0 text-muted-foreground" />}
      <span className="min-w-0">
        <span className="block text-xs font-medium">{label}</span>
        {description && <span className="block truncate text-[9px] font-normal text-muted-foreground">{description}</span>}
      </span>
    </Label>
    <Switch id={id} checked={checked} onCheckedChange={onChange} size="sm" />
  </div>
);

const SectionTitle = ({ icon: Icon, title, detail }: { icon: React.ElementType; title: string; detail: string }) => (
  <div className="flex items-center gap-2">
    <Icon className="text-primary" />
    <div>
      <h2 className="text-[11px] font-bold uppercase tracking-[0.14em]">{title}</h2>
      <p className="text-[10px] text-muted-foreground">{detail}</p>
    </div>
  </div>
);

export const LayerToggle: React.FC<LayerToggleProps> = ({ layers, onToggle }) => (
  <div className="flex flex-col gap-5">
    <section className="flex flex-col gap-2">
      <SectionTitle icon={Map} title="Map Layers" detail="City structure and reference data" />
      <div className="rounded-xl border bg-slate-50/70 p-2">
        <ToggleRow id="boundary-toggle" label="Nasr City boundary" checked={layers.boundary} onChange={() => onToggle("boundary")} icon={MapPin} />
        <ToggleRow id="grid-toggle" label="Analysis grid" description="500-meter model zones" checked={layers.grid} onChange={() => onToggle("grid")} icon={Layers3} />
        <ToggleRow id="roads-labels-toggle" label="Roads & labels" description="Basemap streets and place names" checked={layers.roadsLabels} onChange={() => onToggle("roadsLabels")} icon={Route} />
      </div>
    </section>

    <section className="flex flex-col gap-2">
      <SectionTitle icon={Layers3} title="Risk Layers" detail="Model-estimated impact surfaces" />
      <div className="rounded-xl border bg-slate-50/70 p-2">
        <ToggleRow id="selected-toggle" label="Selected event" checked={layers.selectedRisk} onChange={() => onToggle("selectedRisk")} />
        <ToggleRow id="latest-toggle" label="Latest event" checked={layers.latestRisk} onChange={() => onToggle("latestRisk")} />
        <ToggleRow id="top-rain-toggle" label="Highest-rain event" checked={layers.topRainRisk} onChange={() => onToggle("topRainRisk")} />
        <ToggleRow id="risk-summary-toggle" label="Historic summary" checked={layers.riskSummary} onChange={() => onToggle("riskSummary")} />
      </div>
    </section>

    <Separator />

    <section className="flex flex-col gap-2">
      <SectionTitle icon={Landmark} title="Places" detail="OpenStreetMap points of interest" />
      <div className="rounded-xl border bg-slate-50/70 p-2">
        <ToggleRow id="hospitals-toggle" label="Hospitals" checked={layers.hospitals} onChange={() => onToggle("hospitals")} icon={Hospital} />
        <ToggleRow id="clinics-toggle" label="Clinics" checked={layers.clinics} onChange={() => onToggle("clinics")} icon={Stethoscope} />
        <ToggleRow id="mosques-toggle" label="Mosques" checked={layers.mosques} onChange={() => onToggle("mosques")} icon={Landmark} />
        <ToggleRow id="malls-toggle" label="Malls" checked={layers.malls} onChange={() => onToggle("malls")} icon={ShoppingBag} />
        <ToggleRow id="schools-toggle" label="Schools" checked={layers.schools} onChange={() => onToggle("schools")} icon={School} />
        <ToggleRow id="universities-toggle" label="Universities" checked={layers.universities} onChange={() => onToggle("universities")} icon={GraduationCap} />
        <ToggleRow id="police-toggle" label="Police" checked={layers.police} onChange={() => onToggle("police")} icon={Shield} />
        <ToggleRow id="fire-stations-toggle" label="Fire stations" checked={layers.fireStations} onChange={() => onToggle("fireStations")} icon={Flame} />
        <ToggleRow id="emergency-toggle" label="Emergency facilities" description="Medical, safety, and fire response network" checked={layers.emergency} onChange={() => onToggle("emergency")} icon={Ambulance} />
      </div>
    </section>

    <section className="flex flex-col gap-2">
      <SectionTitle icon={Route} title="Routing" detail="Compare normal and weather-safe paths" />
      <p className="rounded-xl border border-purple-100 bg-secondary/60 px-3 py-2 text-[10px] leading-relaxed text-secondary-foreground">
        Click the map once for origin and again for destination. Route visibility and event mode stay in the floating panel.
      </p>
    </section>
  </div>
);
