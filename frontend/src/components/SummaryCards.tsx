import type { ElementType } from "react";
import {
  CircleAlert,
  CircleGauge,
  ShieldCheck,
  TrendingDown,
  MoreVertical,
} from "lucide-react";

import { cn } from "@/lib/utils";
import type { RouteComparison, LiveWeatherSummary } from "../types/api";
import { getRecommendationLabel } from "../utils/labels";

interface SummaryCardsProps {
  mapMode: "today" | "history";
  comparison: RouteComparison | null;
  liveWeather?: LiveWeatherSummary | null;
}

interface MetricCardProps {
  label: string;
  value: string;
  icon: ElementType;
  tone?: "blue" | "purple" | "low" | "medium" | "high";
  secondaryText?: string;
}

const toneClasses = {
  blue: "text-[#006688] bg-[#c2e8ff]/40",
  purple: "text-[#8b5000] bg-[#ffdcbe]/40",
  low: "text-[#006d36] bg-[#83fba5]/30",
  medium: "text-[#ff9e2a] bg-[#ffdcbe]/40",
  high: "text-[#ba1a1a] bg-[#ffdad6]/60",
};

const MetricCard = ({
  label,
  value,
  icon: Icon,
  tone = "blue",
  secondaryText,
}: MetricCardProps) => (
  <div className="stitch-card flex flex-col justify-between relative overflow-hidden transition-all duration-200 hover:-translate-y-0.5 shadow-sm p-4 h-full">
    <div className="flex items-start justify-between">
      <span className="stitch-label-sm text-[10px] text-text-muted font-semibold tracking-wider uppercase truncate max-w-[70%]">
        {label}
      </span>
      <div className="flex items-center gap-1">
        <span className={cn("flex size-5 items-center justify-center rounded-full", toneClasses[tone])}>
          <Icon className="size-3" aria-hidden="true" />
        </span>
        <button className="text-text-muted hover:bg-black/5 rounded-full p-0.5 transition-colors">
          <MoreVertical className="size-3" />
        </button>
      </div>
    </div>
    <div className="mt-3 flex flex-col justify-end flex-1">
      <strong className="text-sm font-bold tracking-tight text-text-charcoal truncate">
        {value}
      </strong>
      {secondaryText ? (
        <span className="text-[9px] text-text-muted truncate mt-0.5 leading-normal">{secondaryText}</span>
      ) : null}
    </div>
  </div>
);

export const SummaryCards = ({ mapMode, comparison, liveWeather }: SummaryCardsProps) => {
  // 1. Today’s Rain Risk / Rain Risk
  let rainRiskLabel = mapMode === "today" ? "Today’s Rain Risk" : "Rain Risk";
  let rainRiskValue = "Low";
  let rainRiskTone: "low" | "medium" | "high" = "low";
  let rainRiskSecondary = undefined;

  if (mapMode === "today") {
    if (liveWeather) {
      rainRiskValue = liveWeather.rain_risk_expected ? "Expected" : "No meaningful rain risk";
      rainRiskTone = liveWeather.rain_risk_expected ? "medium" : "low";
      rainRiskSecondary = `Source: ${liveWeather.source || "Live"}`;
    } else {
      rainRiskValue = "—";
      rainRiskTone = "low";
    }
  } else {
    // In historical analysis, event indicates risk
    rainRiskValue = "Expected";
    rainRiskTone = "medium";
    rainRiskSecondary = "Historical Scenario";
  }

  // 2. Rain Probability
  let probValue = "—";
  if (mapMode === "today") {
    if (liveWeather?.forecast_window) {
      probValue = `${Math.round(liveWeather.forecast_window.max_precipitation_probability ?? 0)}%`;
    }
  } else {
    probValue = comparison ? "95%" : "—";
  }

  // 3. Route Recommendation
  let recValue = "Waiting for route";
  let recTone: "blue" | "low" | "medium" = "blue";
  if (comparison) {
    if (mapMode === "today") {
      const rec = (comparison as any).recommendation;
      recValue = getRecommendationLabel(rec);
      recTone = rec === "weather_safe_route_recommended" ? "low" : "medium";
    } else {
      recValue = comparison.safe_route_available ? "Safer Route Available" : "Normal Route Recommended";
      recTone = comparison.safe_route_available ? "low" : "medium";
    }
  }

  // 4. Risk Reduction
  let reductionValue = "—";
  let reductionTone: "blue" | "low" = "blue";
  if (comparison) {
    reductionValue = `${(comparison.risk_reduction_percent ?? 0).toFixed(0)}%`;
    reductionTone = comparison.risk_reduction_percent > 0 ? "low" : "blue";
  }

  return (
    <section
      className="grid grid-cols-2 gap-3 px-3 py-1 lg:grid-cols-4"
      aria-label="Operational summary"
    >
      <MetricCard
        label={rainRiskLabel}
        value={rainRiskValue}
        icon={CircleAlert}
        tone={rainRiskTone}
        secondaryText={rainRiskSecondary}
      />
      <MetricCard
        label="Rain Probability"
        value={probValue}
        icon={CircleGauge}
        tone="blue"
      />
      <MetricCard
        label="Route Recommendation"
        value={recValue}
        icon={ShieldCheck}
        tone={recTone}
      />
      <MetricCard
        label="Risk Reduction"
        value={reductionValue}
        icon={TrendingDown}
        tone={reductionTone}
      />
    </section>
  );
};
