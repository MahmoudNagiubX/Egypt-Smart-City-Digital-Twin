import React from "react";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { LayerToggles, EventSummary, FeatureCollection, PlaceProperties } from "../types/api";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";
import {
  Activity,
  Ambulance,
  CalendarRange,
  ChevronDown,
  ChevronUp,
  Compass,
  Flame,
  GraduationCap,
  Hospital,
  Info,
  Landmark,
  Layers3,
  Map,
  MapPin,
  RotateCcw,
  Route,
  School,
  Shield,
  ShoppingBag,
  Stethoscope,
} from "lucide-react";

interface LayerToggleProps {
  mapMode: "today" | "history";
  onMapModeChange: (mode: "today" | "history") => void;
  selectionState: "idle" | "selecting-destination" | "ready" | "loading";
  routingError: string | null;
  onResetRoute: () => void;
  layers: LayerToggles;
  onToggle: (key: keyof LayerToggles) => void;
  riskFillOpacity: number;
  setRiskFillOpacity: (val: number) => void;
  gridLineOpacity: number;
  setGridLineOpacity: (val: number) => void;
  events: EventSummary[];
  selectedEventId: string | null;
  onSelectEvent: (eventId: string) => void;
  riskDisplayMode: "focus" | "all";
  setRiskDisplayMode: (mode: "focus" | "all") => void;
  placesData?: FeatureCollection<PlaceProperties> | null;
  activeRiskLayer?: "rain" | "heat";
  onActiveRiskLayerChange?: (layer: "rain" | "heat") => void;
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
  <div className="flex items-center justify-between gap-3 rounded-lg px-2 py-1.5 transition-colors hover:bg-white/40">
    <Label htmlFor={id} className="flex min-w-0 cursor-pointer items-center gap-2">
      {Icon && <Icon className="size-4 shrink-0 text-text-muted" />}
      <span className="min-w-0 text-xs font-semibold text-text-charcoal">{label}</span>
    </Label>
    <Switch id={id} checked={checked} onCheckedChange={onChange} size="sm" className="data-[state=checked]:bg-[#006688]" />
  </div>
);

const PoiToggleRow = ({
  id,
  label,
  checked,
  onChange,
  icon: Icon,
  count,
}: {
  id: string;
  label: string;
  checked: boolean;
  onChange: () => void;
  icon?: React.ElementType;
  count?: number;
}) => (
  <div
    className={cn(
      "flex items-center justify-between gap-3 rounded-lg px-2.5 py-1.5 transition-all duration-200 border border-transparent",
      checked 
        ? "bg-[#c2e8ff]/30 border-white/50 shadow-sm" 
        : "opacity-60 hover:opacity-100 hover:bg-white/30"
    )}
  >
    <Label htmlFor={id} className="flex min-w-0 cursor-pointer items-center gap-2 w-full justify-between">
      <div className="flex min-w-0 items-center gap-2">
        {Icon && (
          <Icon 
            className={cn(
              "size-4 shrink-0 transition-colors",
              checked ? "text-[#006688]" : "text-text-muted"
            )} 
          />
        )}
        <span 
          className={cn(
            "min-w-0 text-xs font-semibold transition-colors truncate",
            checked ? "text-text-charcoal" : "text-text-muted"
          )}
        >
          {label}
        </span>
      </div>
      {typeof count === "number" && (
        <span className={cn(
          "ml-1.5 px-1.5 py-0.5 rounded text-[9px] font-bold font-mono shrink-0 transition-colors",
          checked ? "bg-[#006688]/15 text-[#006688]" : "bg-white/40 text-text-muted"
        )}>
          {count}
        </span>
      )}
    </Label>
    <Switch 
      id={id} 
      checked={checked} 
      onCheckedChange={onChange} 
      size="sm"
      className="data-[state=checked]:bg-[#006688]"
    />
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
    <Icon className="size-4 text-[#006688]" />
    <div>
      <h2 className="text-[11px] font-bold uppercase tracking-[0.14em] text-text-charcoal leading-tight">{title}</h2>
      <p className="text-[9px] text-text-muted mt-0.5 leading-none">{detail}</p>
    </div>
  </div>
);

export const LayerToggle: React.FC<LayerToggleProps> = ({
  mapMode,
  onMapModeChange,
  selectionState,
  routingError,
  onResetRoute,
  layers,
  onToggle,
  riskFillOpacity,
  setRiskFillOpacity,
  gridLineOpacity,
  setGridLineOpacity,
  events,
  selectedEventId,
  onSelectEvent,
  riskDisplayMode,
  setRiskDisplayMode,
  placesData,
  activeRiskLayer = "rain",
  onActiveRiskLayerChange,
}) => {
  const [isHistoryExpanded, setIsHistoryExpanded] = React.useState(false);

  const poiCounts = React.useMemo(() => {
    if (!placesData || !placesData.features) return null;
    const counts: Record<string, number> = {};
    placesData.features.forEach((f) => {
      let cat = f.properties?.category?.toLowerCase();
      if (cat === "doctors") cat = "clinic";
      if (cat === "place_of_worship") cat = "mosque";
      if (cat) {
        counts[cat] = (counts[cat] || 0) + 1;
      }
    });
    return counts;
  }, [placesData]);

  React.useEffect(() => {
    if (mapMode === "history") {
      setIsHistoryExpanded(true);
    }
  }, [mapMode]);

  return (
    <div className="flex flex-col gap-3.5">
      {/* 1. Map Mode Selection */}
      <section className="flex flex-col gap-2 border-b border-white/20 pb-3.5">
        <SectionTitle icon={Compass} title="Map Mode" detail="Select weather context" />
        <div className="grid grid-cols-2 gap-2 mt-2">
          <button
            type="button"
            onClick={() => onMapModeChange("today")}
            className={cn(
              "flex h-8.5 items-center justify-center rounded-lg text-xs font-bold transition-all shadow-sm",
              mapMode === "today"
                ? "bg-[#006688] text-white"
                : "bg-white/40 border border-white/60 text-text-charcoal hover:bg-white/70"
            )}
          >
            Today
          </button>
          <button
            type="button"
            onClick={() => onMapModeChange("history")}
            className={cn(
              "flex h-8.5 items-center justify-center rounded-lg text-xs font-bold transition-all shadow-sm",
              mapMode === "history"
                ? "bg-[#006688] text-white"
                : "bg-white/40 border border-white/60 text-text-charcoal hover:bg-white/70"
            )}
          >
            History
          </button>
        </div>
      </section>

      {/* 1.5 Active Risk Layer Selection */}
      <section className="flex flex-col gap-2 border-b border-white/20 pb-3.5">
        <SectionTitle icon={Flame} title="Active Mode" detail="Select predictive module" />
        <div className="grid grid-cols-2 gap-2 mt-2">
          <button
            type="button"
            onClick={() => onActiveRiskLayerChange?.("rain")}
            className={cn(
              "flex h-8.5 items-center justify-center rounded-lg text-xs font-bold transition-all shadow-sm",
              activeRiskLayer === "rain"
                ? "bg-[#006688] text-white"
                : "bg-white/40 border border-white/60 text-text-charcoal hover:bg-white/70"
            )}
          >
            Rain Risk
          </button>
          <button
            type="button"
            onClick={() => onActiveRiskLayerChange?.("heat")}
            className={cn(
              "flex h-8.5 items-center justify-center rounded-lg text-xs font-bold transition-all shadow-sm",
              activeRiskLayer === "heat"
                ? "bg-[#d97706] text-white"
                : "bg-white/40 border border-white/60 text-text-charcoal hover:bg-white/70"
            )}
          >
            Heat Risk
          </button>
        </div>
      </section>
 
      {/* 2. Today’s Rain Risk (Show Live weather controls first in Today Mode) */}
      {mapMode === "today" && activeRiskLayer === "rain" && (
        <section className="flex flex-col gap-2 border-b border-white/20 pb-3.5">
          <SectionTitle icon={Layers3} title="Today’s Rain Risk" detail="Real-time predictive overlays" />
          <div className="flex flex-col gap-0.5 mt-1">
            <ToggleRow
              id="live-risk-toggle"
              label="Today’s Rain Risk"
              checked={layers.liveRisk}
              onChange={() => onToggle("liveRisk")}
              icon={Activity}
            />
          </div>
          
          {/* Risk Display Mode Option */}
          <div className="mt-2 flex flex-col gap-1">
            <label className="text-[9px] font-bold uppercase tracking-wider text-text-muted">
              Risk Display Mode
            </label>
            <div className="grid grid-cols-2 gap-1 rounded-lg bg-white/40 border border-white/60 p-0.5">
              <button
                type="button"
                onClick={() => setRiskDisplayMode("focus")}
                className={cn(
                  "rounded-md py-1 text-[10px] font-bold transition-all",
                  riskDisplayMode === "focus"
                    ? "bg-white text-[#006688] shadow-sm"
                    : "text-text-muted hover:text-text-charcoal"
                )}
              >
                Focus Risk Areas
              </button>
              <button
                type="button"
                onClick={() => setRiskDisplayMode("all")}
                className={cn(
                  "rounded-md py-1 text-[10px] font-bold transition-all",
                  riskDisplayMode === "all"
                    ? "bg-white text-[#006688] shadow-sm"
                    : "text-text-muted hover:text-text-charcoal"
                )}
              >
                Show All Risk Zones
              </button>
            </div>
          </div>

          <div className="mt-2.5 flex flex-col gap-2.5 border-t border-white/10 pt-2.5">
            <div className="flex flex-col gap-1">
              <div className="flex justify-between text-[9px] font-bold uppercase tracking-wider text-text-muted">
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
                className="h-1 w-full cursor-pointer appearance-none rounded-lg bg-slate-200 accent-[#006688]"
              />
            </div>
            <div className="flex flex-col gap-1">
              <div className="flex justify-between text-[9px] font-bold uppercase tracking-wider text-text-muted">
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
                className="h-1 w-full cursor-pointer appearance-none rounded-lg bg-slate-200 accent-[#006688]"
              />
            </div>
          </div>
        </section>
      )}

      {/* 2b. Urban Heat (Only when activeRiskLayer === "heat") */}
      {activeRiskLayer === "heat" && (
        <section className="flex flex-col gap-2 border-b border-white/20 pb-3.5">
          <SectionTitle icon={Flame} title="Urban Heat" detail="Satellite heat estimate" />
          <div className="flex flex-col gap-0.5 mt-1">
            <div className="flex items-center justify-between gap-3 rounded-lg px-2 py-1.5 transition-colors hover:bg-white/40">
              <Label className="flex min-w-0 items-center gap-2">
                <Flame className="size-4 shrink-0 text-amber-600" />
                <span className="min-w-0 text-xs font-semibold text-text-charcoal">Heat Risk Overlay</span>
              </Label>
              <Switch checked={true} disabled size="sm" className="data-[state=checked]:bg-[#d97706]" />
            </div>
          </div>
          
          <div className="mt-2.5 flex flex-col gap-2.5 border-t border-white/10 pt-2.5">
            <div className="flex flex-col gap-1">
              <div className="flex justify-between text-[9px] font-bold uppercase tracking-wider text-text-muted">
                <span>Heat Layer Opacity</span>
                <span>{Math.round(riskFillOpacity * 100)}%</span>
              </div>
              <input
                type="range"
                min="0.10"
                max="0.80"
                step="0.05"
                value={riskFillOpacity}
                onChange={(e) => setRiskFillOpacity(parseFloat(e.target.value))}
                className="h-1 w-full cursor-pointer appearance-none rounded-lg bg-slate-200 accent-[#d97706]"
              />
            </div>
            <div className="flex flex-col gap-1">
              <div className="flex justify-between text-[9px] font-bold uppercase tracking-wider text-text-muted">
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
                className="h-1 w-full cursor-pointer appearance-none rounded-lg bg-slate-200 accent-[#d97706]"
              />
            </div>
          </div>
        </section>
      )}
 
      {/* 3. Route Setup Instructions (Only when activeRiskLayer === "rain") */}
      {activeRiskLayer === "rain" && (
        <section className="flex flex-col gap-2 border-b border-white/20 pb-3.5">
          <SectionTitle icon={Route} title="Route Setup" detail="Weather-aware routing" />
          <div className="mt-1.5 flex flex-col gap-2 px-1">
            <div className="rounded-xl bg-white/40 border border-white/60 p-3 text-[11px] leading-relaxed text-text-charcoal shadow-sm">
              <span className="font-bold text-[#006688] block mb-0.5">Instruction:</span>
              {selectionState === "idle" && "Click the map to choose your starting point"}
              {selectionState === "selecting-destination" && "Now choose your destination"}
              {selectionState === "ready" && "Route ready • click the map again to clear"}
              {selectionState === "loading" && "Calculating weather-aware route..."}
              {routingError && <span className="text-red-600 font-medium block mt-1">{routingError}</span>}
            </div>
            {(selectionState !== "idle" || routingError) && (
              <button
                type="button"
                onClick={onResetRoute}
                className="flex h-8 w-full items-center justify-center gap-1.5 rounded-lg border border-white/60 bg-white/50 text-xs font-semibold text-text-charcoal transition-all hover:bg-white/80 active:bg-white"
              >
                <RotateCcw className="size-3.5" />
                Reset Route
              </button>
            )}
          </div>
        </section>
      )}

      {/* 4. Map Reference Layers */}
      <section className="flex flex-col gap-2 border-b border-white/20 pb-3.5">
        <SectionTitle icon={Map} title="Map Layers" detail="Reference data" />
        <div className="flex flex-col gap-0.5 mt-1">
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

      {/* 5. Points of Interest */}
      <section className="flex flex-col gap-2 border-b border-white/20 pb-3.5">
        <SectionTitle icon={Landmark} title="Places" detail="Points of interest" />
        <div className="flex flex-col gap-0.5 mt-1 max-h-52 overflow-y-auto pr-1">
          <PoiToggleRow
            id="hospitals-toggle"
            label="Hospitals"
            checked={layers.hospitals}
            onChange={() => onToggle("hospitals")}
            icon={Hospital}
            count={poiCounts?.hospital}
          />
          <PoiToggleRow
            id="clinics-toggle"
            label="Clinics"
            checked={layers.clinics}
            onChange={() => onToggle("clinics")}
            icon={Stethoscope}
            count={poiCounts?.clinic}
          />
          <PoiToggleRow
            id="mosques-toggle"
            label="Mosques"
            checked={layers.mosques}
            onChange={() => onToggle("mosques")}
            icon={Landmark}
            count={poiCounts?.mosque}
          />
          <PoiToggleRow
            id="malls-toggle"
            label="Malls"
            checked={layers.malls}
            onChange={() => onToggle("malls")}
            icon={ShoppingBag}
            count={poiCounts?.mall}
          />
          <PoiToggleRow
            id="schools-toggle"
            label="Schools"
            checked={layers.schools}
            onChange={() => onToggle("schools")}
            icon={School}
            count={poiCounts?.school}
          />
          <PoiToggleRow
            id="universities-toggle"
            label="Universities"
            checked={layers.universities}
            onChange={() => onToggle("universities")}
            icon={GraduationCap}
            count={poiCounts?.university}
          />
          <PoiToggleRow
            id="police-toggle"
            label="Police"
            checked={layers.police}
            onChange={() => onToggle("police")}
            icon={Shield}
            count={poiCounts?.police}
          />
          <PoiToggleRow
            id="fire-stations-toggle"
            label="Fire Stations"
            checked={layers.fireStations}
            onChange={() => onToggle("fireStations")}
            icon={Flame}
            count={poiCounts?.fire_station}
          />
          <PoiToggleRow
            id="emergency-toggle"
            label="Emergency Facilities"
            checked={layers.emergency}
            onChange={() => onToggle("emergency")}
            icon={Ambulance}
            count={poiCounts?.emergency}
          />
        </div>
      </section>

      {/* 6. Historical Analysis Section (Only visible in History mode and Rain active) */}
      {mapMode === "history" && activeRiskLayer === "rain" && (
        <section className="flex flex-col gap-2 border-b border-white/20 pb-3.5">
          <button
            type="button"
            onClick={() => setIsHistoryExpanded(!isHistoryExpanded)}
            className="flex w-full items-center justify-between gap-2 text-left focus:outline-none"
          >
            <SectionTitle icon={CalendarRange} title="Historical Analysis" detail="Past scenarios" />
            <span className="text-text-muted">
              {isHistoryExpanded ? <ChevronUp className="size-4" /> : <ChevronDown className="size-4" />}
            </span>
          </button>

          {isHistoryExpanded && (
            <div className="mt-2 flex flex-col gap-3 border-t border-white/10 pt-2.5">
              <div className="flex flex-col gap-1.5">
                <label className="text-[10px] font-semibold text-text-muted uppercase tracking-wider">
                  Choose Historical Event
                </label>
                <Select value={selectedEventId || ""} onValueChange={onSelectEvent}>
                  <SelectTrigger className="h-8.5 w-full bg-white/70 shadow-sm text-xs border-white/60" aria-label="Observed weather event">
                    <SelectValue placeholder="Select an event…" />
                  </SelectTrigger>
                  <SelectContent className="max-h-72">
                    <SelectGroup>
                      {events.map((event) => (
                        <SelectItem key={event.event_id} value={event.event_id} className="text-xs">
                          {event.event_id === "evt_0557"
                            ? "Historic Rain Event"
                            : event.event_id === "evt_dry_009"
                              ? "Dry Weather Event"
                              : "Weather Event"}{" "}
                          · {event.mean_rain_24h_mm.toFixed(1)} mm
                        </SelectItem>
                      ))}
                    </SelectGroup>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex flex-col gap-1 border-t border-white/10 pt-2.5">
                <span className="text-[10px] font-semibold text-text-muted uppercase tracking-wider mb-1">
                  Historical Risk Layers
                </span>
                <ToggleRow
                  id="selected-toggle"
                  label="Selected Event"
                  checked={layers.selectedRisk}
                  onChange={() => onToggle("selectedRisk")}
                  icon={Layers3}
                />
                <ToggleRow
                  id="latest-toggle"
                  label="Latest Event Risk"
                  checked={layers.latestRisk}
                  onChange={() => onToggle("latestRisk")}
                  icon={Layers3}
                />
                <ToggleRow
                  id="top-rain-toggle"
                  label="Top-Rain Event"
                  checked={layers.topRainRisk}
                  onChange={() => onToggle("topRainRisk")}
                  icon={Layers3}
                />
                <ToggleRow
                  id="risk-summary-toggle"
                  label="Historic Summary"
                  checked={layers.riskSummary}
                  onChange={() => onToggle("riskSummary")}
                  icon={Layers3}
                />
              </div>
            </div>
          )}
        </section>
      )}

      {/* 7. About This Prototype (Disclaimer) */}
      <section className="flex flex-col gap-1 bg-white/30 border border-white/40 rounded-xl p-2.5">
        <div className="flex items-start gap-1.5 text-[9.5px] text-text-muted font-medium leading-normal">
          <Info className="size-3.5 text-text-muted/80 shrink-0 mt-0.5" aria-hidden="true" />
          <span>Predictions are weather-impact model estimates, not official emergency dispatch commands.</span>
        </div>
      </section>
    </div>
  );
};
