import type { ElementType } from "react";
import {
  CircleAlert,
  CircleGauge,
  ShieldCheck,
  TrendingDown,
} from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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
  blue: "text-blue-600 dark:text-blue-400",
  purple: "text-purple-600 dark:text-purple-400",
  low: "text-emerald-600 dark:text-emerald-400",
  medium: "text-amber-600 dark:text-amber-400",
  high: "text-red-600 dark:text-red-400",
};

const MetricCard = ({
  label,
  value,
  icon: Icon,
  tone = "blue",
  secondaryText,
}: MetricCardProps) => (
  <Card
    size="sm"
    className="summary-card min-w-32 border-0 bg-card shadow-[0_4px_12px_rgba(44,94,173,0.03)] ring-1 ring-border transition-all hover:shadow-[0_6px_18px_rgba(44,94,173,0.06)]"
  >
    <CardHeader className="flex flex-row items-center justify-between gap-2 pb-0">
      <CardTitle className="text-[10px] font-bold uppercase tracking-[0.12em] text-muted-foreground">
        {label}
      </CardTitle>
      <span className={cn("flex size-5 shrink-0 items-center justify-center", toneClasses[tone])}>
        <Icon className="size-4" aria-hidden="true" />
      </span>
    </CardHeader>
    <CardContent className="flex flex-col gap-0.5 pt-1.5 pb-2.5">
      <strong className="text-xs font-bold leading-none tracking-tight text-foreground truncate max-w-full">
        {value}
      </strong>
      {secondaryText ? (
        <span className="text-[9px] text-muted-foreground truncate mt-0.5">{secondaryText}</span>
      ) : null}
    </CardContent>
  </Card>
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
  if (comparison) {
    reductionValue = `${(comparison.risk_reduction_percent ?? 0).toFixed(0)}%`;
  }

  return (
    <section
      className="grid grid-cols-2 gap-2 px-3 py-1.5 lg:grid-cols-4"
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
        tone={comparison && comparison.risk_reduction_percent > 0 ? "low" : "blue"}
      />
    </section>
  );
};
