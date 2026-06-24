import type { ElementType } from "react";
import {
  CalendarDays,
  CircleAlert,
  CircleGauge,
  Clock,
  ShieldCheck,
  TrendingDown,
} from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { EventSummary, RouteComparison, SummaryResponse, LiveWeatherSummary } from "../types/api";
import { formatInteger } from "../utils/format";

interface SummaryCardsProps {
  summary: SummaryResponse | null;
  selectedEventId: string | null;
  events: EventSummary[];
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
  blue: "bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400",
  purple: "bg-purple-50 text-purple-700 dark:bg-purple-900/20 dark:text-purple-400",
  low: "bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-400",
  medium: "bg-amber-50 text-amber-700 dark:bg-amber-900/20 dark:text-amber-400",
  high: "bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-400",
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
    className="summary-card min-w-32 border-0 bg-card shadow-[0_8px_24px_rgba(44,94,173,0.06)] ring-1 ring-border"
  >
    <CardHeader className="flex flex-row items-center justify-between gap-2 pb-0">
      <CardTitle className="text-[10px] font-semibold uppercase tracking-[0.12em] text-muted-foreground">
        {label}
      </CardTitle>
      <span className={cn("flex size-7 shrink-0 items-center justify-center rounded-lg", toneClasses[tone])}>
        <Icon className="size-4" aria-hidden="true" />
      </span>
    </CardHeader>
    <CardContent className="flex flex-col gap-0.5 pt-1">
      <strong className="text-base font-semibold leading-none tracking-tight text-foreground truncate max-w-full">
        {value}
      </strong>
      {secondaryText ? (
        <span className="text-[10px] text-muted-foreground truncate">{secondaryText}</span>
      ) : null}
    </CardContent>
  </Card>
);

export const SummaryCards = ({ summary, selectedEventId, events, comparison, liveWeather }: SummaryCardsProps) => {
  // Find currently active weather event summary to format nicely
  const activeEvent = events.find((e) => e.event_id === selectedEventId);
  const activeEventName = activeEvent
    ? (activeEvent.event_id === "evt_0557"
        ? "Historic Rain Event"
        : activeEvent.event_id === "evt_dry_009"
          ? "Dry Weather Event"
          : "Weather Event")
    : "No Active Event";

  const eventTime = activeEvent?.timestamp
    ? new Date(activeEvent.timestamp).toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
        year: "numeric",
      })
    : undefined;

  // Decide on safety status text
  let safetyStatus = "No Route Selected";
  let safetyTone: "blue" | "low" | "medium" | "high" = "blue";

  if (comparison) {
    if (comparison.safe_route_available) {
      safetyStatus = "Safer Route Available";
      safetyTone = "low";
    } else {
      safetyStatus = "No Distinct Safer Alternative";
      safetyTone = "medium";
    }
  }

  const showComparison = comparison !== null;

  return (
    <section
      className="grid grid-cols-2 gap-2 px-3 py-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6"
      aria-label="Operational summary"
    >
      <MetricCard
        label="Medium Risk Areas"
        value={summary ? formatInteger(summary.risk_class_counts?.medium) : "0"}
        icon={CircleGauge}
        tone="medium"
      />
      <MetricCard
        label="High Risk Areas"
        value={summary ? formatInteger(summary.risk_class_counts?.high) : "0"}
        icon={CircleAlert}
        tone="high"
      />
      <MetricCard
        label="Active Weather Event"
        value={activeEventName}
        icon={CalendarDays}
        tone="purple"
        secondaryText={eventTime}
      />
      <MetricCard
        label="Route Safety"
        value={safetyStatus}
        icon={ShieldCheck}
        tone={safetyTone}
      />
      {showComparison && (
        <MetricCard
          label="Risk Reduction"
          value={`${(comparison.risk_reduction_percent ?? 0).toFixed(0)}%`}
          icon={TrendingDown}
          tone="low"
        />
      )}
      {showComparison && (
        <MetricCard
          label="ETA Tradeoff"
          value={`${comparison.eta_tradeoff_percent >= 0 ? "+" : ""}${(comparison.eta_tradeoff_percent ?? 0).toFixed(0)}%`}
          icon={Clock}
          tone={comparison.eta_tradeoff_percent > 15 ? "medium" : "blue"}
        />
      )}
      {liveWeather && (
        <>
          <MetricCard
            label="Rain Risk Expected"
            value={liveWeather.rain_risk_expected ? "Yes" : "No"}
            icon={CircleAlert}
            tone={liveWeather.rain_risk_expected ? "medium" : "low"}
          />
          <MetricCard
            label="24h Rainfall"
            value={liveWeather.forecast_window ? `${(liveWeather.forecast_window.rain_24h_mm ?? 0).toFixed(1)} mm` : "—"}
            icon={CircleGauge}
            tone="blue"
          />
          <MetricCard
            label="Rain Probability"
            value={liveWeather.forecast_window ? `${Math.round(liveWeather.forecast_window.max_precipitation_probability ?? 0)}%` : "—"}
            icon={TrendingDown}
            tone="blue"
          />
          <MetricCard
            label="Live Weather Mode"
            value={liveWeather.recommended_event_mode === "live" ? "Live Forecast" : "Normal Mode"}
            icon={CalendarDays}
            tone="purple"
            secondaryText={liveWeather.source}
          />
        </>
      )}
    </section>
  );
};
