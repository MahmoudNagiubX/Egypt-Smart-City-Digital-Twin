import React from "react";
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { EventSummary } from "../types/api";
import { CalendarRange } from "lucide-react";
import { formatNumber } from "../utils/format";

interface EventSelectorProps {
  events: EventSummary[];
  selectedEventId: string | null;
  onSelectEvent: (eventId: string) => void;
}


export const EventSelector: React.FC<EventSelectorProps> = ({ 
  events, 
  selectedEventId, 
  onSelectEvent 
}) => {
  return (
    <div className="space-y-2">
      <div className="flex items-center space-x-1.5 mb-1.5">
        <CalendarRange className="h-4 w-4 text-cyan-400" />
        <Label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Simulated Event Selector</Label>
      </div>
      
      <Select 
        value={selectedEventId || ""} 
        onValueChange={onSelectEvent}
      >
        <SelectTrigger className="w-full bg-slate-900 border-slate-800 text-slate-200 text-xs">
          <SelectValue placeholder="Select historical event..." />
        </SelectTrigger>
        <SelectContent className="bg-slate-900 border-slate-800 text-slate-200 max-h-60">
          {events.map((evt) => {
            const dateStr = new Date(evt.timestamp).toLocaleDateString(undefined, {
              month: "short",
              day: "numeric",
              hour: "2-digit",
              minute: "2-digit"
            });
            return (
              <SelectItem 
                key={evt.event_id} 
                value={evt.event_id}
                className="hover:bg-slate-800 focus:bg-slate-800 text-xs"
              >
                {evt.event_id} ({formatNumber(evt.rain_sum_mm, 1)} mm) - {dateStr}
              </SelectItem>
            );
          })}
        </SelectContent>
      </Select>
    </div>
  );
};
