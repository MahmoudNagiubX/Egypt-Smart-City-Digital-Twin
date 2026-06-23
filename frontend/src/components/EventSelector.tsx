import React from "react";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { EventSummary } from "../types/api";
import { CalendarRange, CloudRain } from "lucide-react";
import { formatNumber } from "../utils/format";

interface EventSelectorProps {
  events: EventSummary[];
  selectedEventId: string | null;
  onSelectEvent: (eventId: string) => void;
}

export const EventSelector: React.FC<EventSelectorProps> = ({ events, selectedEventId, onSelectEvent }) => {
  const selectedEvent = events.find((event) => event.event_id === selectedEventId);

  return (
    <section className="flex flex-col gap-2.5" aria-labelledby="event-section-title">
      <div className="flex items-center gap-2">
        <CalendarRange className="text-primary" />
        <div>
          <h2 id="event-section-title" className="text-[11px] font-bold uppercase tracking-[0.14em]">Event</h2>
          <p className="text-[10px] text-muted-foreground">Choose an observed weather event</p>
        </div>
      </div>

      <Select value={selectedEventId || ""} onValueChange={onSelectEvent}>
        <SelectTrigger className="h-10 w-full bg-white shadow-sm" aria-label="Observed weather event">
          <SelectValue placeholder="Select an event…" />
        </SelectTrigger>
        <SelectContent className="max-h-72">
          <SelectGroup>
            {events.map((event) => {
              const date = new Date(event.timestamp).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
              return (
                <SelectItem key={event.event_id} value={event.event_id}>
                  {event.event_id} · {formatNumber(event.mean_rain_24h_mm, 1)} mm · {date}
                </SelectItem>
              );
            })}
          </SelectGroup>
        </SelectContent>
      </Select>

      {selectedEvent && (
        <div className="flex items-center justify-between rounded-xl border border-blue-100 bg-accent/45 px-3 py-2 text-[10px]">
          <span className="flex items-center gap-1.5 font-medium text-primary"><CloudRain /> Rain accumulation</span>
          <strong>{formatNumber(selectedEvent.mean_rain_24h_mm, 1)} mm</strong>
        </div>
      )}
    </section>
  );
};
