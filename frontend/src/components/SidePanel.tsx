import React, { useCallback, useEffect, useRef, useState } from "react";
import {
  CalendarRange,
  ChevronLeft,
  ChevronRight,
  Info,
  Landmark,
  Layers3,
  Map,
  MapPinned,
  Route,
} from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface SidePanelProps {
  children: React.ReactNode;
}

export const SidePanel: React.FC<SidePanelProps> = ({ children }) => {
  const [width, setWidth] = useState(300);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const isResizing = useRef(false);

  const startResizing = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    isResizing.current = true;
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
  }, []);

  const stopResizing = useCallback(() => {
    if (isResizing.current) {
      isResizing.current = false;
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    }
  }, []);

  const resize = useCallback((e: MouseEvent) => {
    if (isResizing.current) {
      const newWidth = e.clientX;
      if (newWidth >= 260 && newWidth <= 420) {
        setWidth(newWidth);
      }
    }
  }, []);

  useEffect(() => {
    window.addEventListener("mousemove", resize);
    window.addEventListener("mouseup", stopResizing);
    return () => {
      window.removeEventListener("mousemove", resize);
      window.removeEventListener("mouseup", stopResizing);
    };
  }, [resize, stopResizing]);

  const handleExpand = () => setIsCollapsed(false);

  if (isCollapsed) {
    return (
      <aside
        aria-label="Map and routing controls"
        className="relative flex h-full w-[60px] shrink-0 flex-col border-r border-slate-200 bg-gradient-to-b from-white via-[#F7FBFF] to-[#E3E7F1] text-foreground transition-all shadow-[4px_0_15px_rgba(44,94,173,0.05)]"
      >
        <div className="flex h-16 items-center justify-center border-b border-slate-200/50">
          <button
            type="button"
            onClick={handleExpand}
            className="flex size-9 items-center justify-center rounded-xl bg-primary/10 text-primary transition-all hover:bg-primary/20"
            aria-label="Expand sidebar"
          >
            <ChevronRight className="size-5" />
          </button>
        </div>

        <div className="flex flex-1 flex-col items-center gap-6 py-6">
          <button
            type="button"
            onClick={handleExpand}
            className="flex size-9 items-center justify-center rounded-lg text-muted-foreground hover:bg-slate-200/50 hover:text-foreground"
            title="Event Selector"
          >
            <CalendarRange className="size-5" />
          </button>
          <button
            type="button"
            onClick={handleExpand}
            className="flex size-9 items-center justify-center rounded-lg text-muted-foreground hover:bg-slate-200/50 hover:text-foreground"
            title="Map Layers"
          >
            <Map className="size-5" />
          </button>
          <button
            type="button"
            onClick={handleExpand}
            className="flex size-9 items-center justify-center rounded-lg text-muted-foreground hover:bg-slate-200/50 hover:text-foreground"
            title="Risk Layers"
          >
            <Layers3 className="size-5" />
          </button>
          <button
            type="button"
            onClick={handleExpand}
            className="flex size-9 items-center justify-center rounded-lg text-muted-foreground hover:bg-slate-200/50 hover:text-foreground"
            title="Places"
          >
            <Landmark className="size-5" />
          </button>
          <button
            type="button"
            onClick={handleExpand}
            className="flex size-9 items-center justify-center rounded-lg text-muted-foreground hover:bg-slate-200/50 hover:text-foreground"
            title="Routing"
          >
            <Route className="size-5" />
          </button>
        </div>

        <div className="mt-auto border-t border-slate-200/50 bg-white/20 p-3 flex justify-center">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <button
                  type="button"
                  className="flex size-8 items-center justify-center rounded-md text-primary/80 transition-colors hover:bg-slate-200/50 hover:text-primary"
                >
                  <Info className="size-4" />
                </button>
              </TooltipTrigger>
              <TooltipContent side="right" align="center" className="max-w-xs p-3 text-[10px] leading-relaxed shadow-lg">
                Predictions are model-estimated weather-impact risk scores derived from real observed and satellite data. They are not verified street-level flood incident labels. Routes are decision-support prototype outputs, not official emergency dispatch instructions.
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
      </aside>
    );
  }

  return (
    <aside
      aria-label="Map and routing controls"
      style={{ width: `${width}px` }}
      className="relative flex h-full shrink-0 flex-col border-r border-slate-200 bg-gradient-to-b from-white via-[#F7FBFF] to-[#E3E7F1] text-foreground shadow-[8px_0_30px_rgba(44,94,173,0.06)]"
    >
      {/* Header */}
      <div className="flex h-16 items-center justify-between border-b border-slate-200/50 px-4 py-3">
        <div className="flex items-center gap-3">
          <MapPinned className="size-5 text-[#2C5EAD] shrink-0" aria-hidden="true" />
          <div>
            <h2 className="text-xs font-bold tracking-tight text-foreground">Map & Route Controls</h2>
            <p className="mt-0.5 text-[9px] font-bold uppercase tracking-[0.16em] text-[#2C5EAD]">Nasr City Operations</p>
          </div>
        </div>
        <button
          type="button"
          onClick={() => setIsCollapsed(true)}
          className="flex size-7 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-slate-200/50 hover:text-foreground"
          aria-label="Collapse sidebar"
        >
          <ChevronLeft className="size-4.5" />
        </button>
      </div>

      {/* Main Content */}
      <ScrollArea className="min-h-0 flex-1">
        <div className="flex flex-col gap-4 p-4">{children}</div>
      </ScrollArea>

      {/* Footer Info tooltip */}
      <div className="mt-auto border-t border-slate-200/50 bg-white/20 p-2.5 flex justify-center shrink-0">
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                type="button"
                className="flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-[10px] font-bold text-primary/80 transition-colors hover:bg-slate-200/50 hover:text-primary"
              >
                <Info className="size-3.5" />
                About this prototype
              </button>
            </TooltipTrigger>
            <TooltipContent side="top" align="center" className="max-w-xs p-3 text-[10px] leading-relaxed shadow-lg">
              Predictions are model-estimated weather-impact risk scores derived from real observed and satellite data. They are not verified street-level flood incident labels. Routes are decision-support prototype outputs, not official emergency dispatch instructions.
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>

      {/* Resize Handle */}
      <div
        onMouseDown={startResizing}
        className="absolute bottom-0 right-0 top-0 w-1 cursor-col-resize hover:bg-[#1591DC]/40 active:bg-[#1591DC] transition-colors"
        aria-hidden="true"
      />
    </aside>
  );
};
