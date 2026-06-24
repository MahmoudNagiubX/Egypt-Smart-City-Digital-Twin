import type { ElementType } from "react";
import {
  Activity,
  CalendarDays,
  CheckCircle2,
  CircleAlert,
  CircleGauge,
  Database,
  MapPinned,
  Navigation,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { HealthResponse, SummaryResponse } from "../types/api";
import { EMPTY_VALUE, formatInteger } from "../utils/format";

interface SummaryCardsProps {
  summary: SummaryResponse | null;
  health: HealthResponse | null;
}

interface MetricCardProps {
  label: string;
  value: string;
  icon: ElementType;
  tone?: "blue" | "purple" | "low" | "medium" | "high";
  badge?: string;
}

const toneClasses = {
  blue: "bg-accent text-primary",
  purple: "bg-secondary text-secondary-foreground",
  low: "bg-emerald-50 text-emerald-700",
  medium: "bg-amber-50 text-amber-700",
  high: "bg-red-50 text-red-700",
};

const MetricCard = ({
  label,
  value,
  icon: Icon,
  tone = "blue",
  badge,
}: MetricCardProps) => (
  <Card
    size="sm"
    className="summary-card min-w-32 border-0 bg-card shadow-[0_8px_24px_rgba(44,94,173,0.08)] ring-1 ring-border"
  >
    <CardHeader className="flex flex-row items-center justify-between gap-2 pb-0">
      <CardTitle className="text-[10px] font-semibold uppercase tracking-[0.12em] text-muted-foreground">
        {label}
      </CardTitle>
      <span className={cn("flex size-7 shrink-0 items-center justify-center rounded-lg", toneClasses[tone])}>
        <Icon aria-hidden="true" />
      </span>
    </CardHeader>
    <CardContent className="flex items-end justify-between gap-2">
      <strong className="text-lg font-semibold leading-none tracking-tight text-foreground">
        {value}
      </strong>
      {badge ? <Badge variant="secondary">{badge}</Badge> : null}
    </CardContent>
  </Card>
);

export const SummaryCards = ({ summary, health }: SummaryCardsProps) => {
  const isHealthy = health?.status === "healthy" || health?.status === "ok";
  const routingReady = isHealthy || Boolean(health?.outputs_available?.emergency_facilities);

  return (
    <section
      className="grid grid-cols-2 gap-2 px-3 py-3 sm:grid-cols-4 2xl:grid-cols-8"
      aria-label="Operational summary"
    >
      <MetricCard
        label="System Status"
        value={isHealthy ? "Online" : health ? "Attention" : EMPTY_VALUE}
        icon={isHealthy ? CheckCircle2 : CircleAlert}
        badge="Backend"
      />
      <MetricCard
        label="Zones Analyzed"
        value={formatInteger(summary?.zone_count)}
        icon={MapPinned}
      />
      <MetricCard
        label="Events"
        value={formatInteger(summary?.event_count)}
        icon={CalendarDays}
        tone="purple"
      />
      <MetricCard
        label="Prediction Rows"
        value={formatInteger(summary?.prediction_row_count)}
        icon={Database}
        tone="purple"
      />
      <MetricCard
        label="Low Risk"
        value={formatInteger(summary?.risk_class_counts?.low)}
        icon={Activity}
        tone="low"
      />
      <MetricCard
        label="Medium Risk"
        value={formatInteger(summary?.risk_class_counts?.medium)}
        icon={CircleGauge}
        tone="medium"
      />
      <MetricCard
        label="High Risk"
        value={formatInteger(summary?.risk_class_counts?.high)}
        icon={CircleAlert}
        tone="high"
      />
      <MetricCard
        label="Routing Ready"
        value={routingReady ? "Ready" : health ? "Unavailable" : EMPTY_VALUE}
        icon={Navigation}
      />
    </section>
  );
};
