import React from "react";
import { AlertCircle, MapPinned } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { ScrollArea } from "@/components/ui/scroll-area";

interface SidePanelProps {
  children: React.ReactNode;
}

export const SidePanel: React.FC<SidePanelProps> = ({ children }) => {
  return (
    <aside className="side-panel flex h-full w-[19rem] shrink-0 flex-col border-r bg-card text-foreground shadow-[8px_0_30px_rgba(44,94,173,0.05)]">
      <div className="flex items-center gap-3 border-b px-4 py-3">
        <div className="flex size-9 items-center justify-center rounded-xl bg-secondary text-secondary-foreground">
          <MapPinned />
        </div>
        <div>
          <h2 className="text-sm font-bold tracking-tight">Map Controls</h2>
          <p className="mt-0.5 text-[9px] font-semibold uppercase tracking-[0.16em] text-primary">Nasr City operations</p>
        </div>
      </div>

      <ScrollArea className="min-h-0 flex-1">
        <div className="flex flex-col gap-5 p-4">{children}</div>
      </ScrollArea>

      <div className="border-t bg-muted/50 p-3">
        <Alert className="bg-card py-2 shadow-sm">
          <AlertCircle aria-hidden="true" />
          <AlertTitle className="text-[10px]">Decision-Support Notice</AlertTitle>
          <AlertDescription className="text-[9px] leading-relaxed">
            Predictions are model-estimated weather-impact risk scores derived from real observed and satellite data. They are not verified street-level flood incident labels. Routes are decision-support prototype outputs, not official emergency dispatch instructions.
          </AlertDescription>
        </Alert>
      </div>
    </aside>
  );
};
