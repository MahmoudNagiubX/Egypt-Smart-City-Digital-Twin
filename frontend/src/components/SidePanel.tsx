import React from "react";
import { AlertCircle, MapPinned } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";

interface SidePanelProps {
  children: React.ReactNode;
}

export const SidePanel: React.FC<SidePanelProps> = ({ children }) => {
  return (
    <aside className="side-panel flex h-full w-[19rem] shrink-0 flex-col border-r bg-white text-foreground shadow-[8px_0_30px_rgba(44,94,173,0.05)]">
      <div className="flex items-center gap-3 border-b px-4 py-3">
        <div className="flex size-9 items-center justify-center rounded-xl bg-secondary text-secondary-foreground">
          <MapPinned />
        </div>
        <div>
          <h1 className="text-sm font-bold tracking-tight">Nasr City Weather-Impact</h1>
          <p className="mt-0.5 text-[9px] font-semibold uppercase tracking-[0.16em] text-primary">Emergency mobility module</p>
        </div>
      </div>

      <ScrollArea className="min-h-0 flex-1">
        <div className="flex flex-col gap-5 p-4">{children}</div>
      </ScrollArea>

      <div className="border-t bg-slate-50/80 p-3">
        <div className="flex items-start gap-2 rounded-xl border bg-white p-2.5 text-[9px] leading-relaxed text-muted-foreground shadow-sm">
          <AlertCircle className="mt-0.5 shrink-0 text-primary" />
          <p>
            <strong className="mb-0.5 block font-bold text-foreground">Decision-support notice</strong>
            Predictions are model-estimated weather-impact risk scores derived from real observed and satellite data. They are not verified street-level flood incident labels. Routes are decision-support prototype outputs, not official emergency dispatch instructions.
          </p>
        </div>
      </div>
    </aside>
  );
};
