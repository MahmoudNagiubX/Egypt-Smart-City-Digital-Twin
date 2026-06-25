import React, { useState, useEffect, useRef } from "react";
import { Search, X, MapPin, Hospital, Landmark, Map, Navigation } from "lucide-react";
import { searchLocalPlaces } from "../api/client";
import type { SearchResultItem, RouteCoordinate } from "../types/api";

interface SearchBoxProps {
  onSelectResult: (result: SearchResultItem | null) => void;
  selectedResult: SearchResultItem | null;
  onSetStart: (coord: RouteCoordinate) => void;
  onSetDestination: (coord: RouteCoordinate) => void;
  onClear: () => void;
}

export const SearchBox: React.FC<SearchBoxProps> = ({
  onSelectResult,
  selectedResult,
  onSetStart,
  onSetDestination,
  onClear,
}) => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResultItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Debounced search query
  useEffect(() => {
    if (query.trim().length < 2) {
      setResults([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    const delayDebounce = setTimeout(async () => {
      try {
        const response = await searchLocalPlaces(query);
        if (response.status === "ok") {
          setResults(response.results);
        } else {
          setResults([]);
        }
      } catch (err) {
        console.error("Error fetching search results:", err);
        setError("Search is temporarily unavailable.");
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => clearTimeout(delayDebounce);
  }, [query]);

  // Handle clicking outside of dropdown to close it
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSelectResult = (result: SearchResultItem) => {
    onSelectResult(result);
    setQuery(result.display_name);
    setDropdownOpen(false);
  };

  const handleClear = () => {
    setQuery("");
    setResults([]);
    onClear();
  };

  // Icon chooser
  const getCategoryIcon = (category: string) => {
    const cat = category.toLowerCase();
    if (cat.includes("hospital") || cat.includes("clinic")) {
      return <Hospital className="size-4 text-emerald-500 shrink-0" />;
    }
    if (cat === "road") {
      return <MapPin className="size-4 text-sky-500 shrink-0" />;
    }
    if (cat === "zone") {
      return <Map className="size-4 text-purple-500 shrink-0" />;
    }
    return <Landmark className="size-4 text-amber-500 shrink-0" />;
  };

  return (
    <div className="relative flex flex-col gap-2 rounded-xl border border-slate-200/60 bg-white/60 p-3 shadow-sm backdrop-blur-md">
      <label htmlFor="map-search-input" className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
        Search Map
      </label>
      
      {/* Input container */}
      <div className="relative flex items-center">
        <input
          id="map-search-input"
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setDropdownOpen(true);
          }}
          onFocus={() => setDropdownOpen(true)}
          placeholder="Search street, place, hospital..."
          className="h-10 w-full rounded-lg border border-slate-200 bg-white pl-9 pr-9 text-xs shadow-inner outline-none transition-all placeholder:text-muted-foreground/70 focus:border-primary/50 focus:ring-2 focus:ring-primary/10"
        />
        <Search className="absolute left-3 size-4 text-muted-foreground/60" />
        
        {query && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute right-3 flex size-5 items-center justify-center rounded-full hover:bg-slate-100 text-muted-foreground/80 transition-colors"
            aria-label="Clear search input"
          >
            <X className="size-3" />
          </button>
        )}
      </div>

      {/* Autocomplete Dropdown */}
      {dropdownOpen && (query.trim().length >= 2 || results.length > 0) && (
        <div
          ref={dropdownRef}
          className="absolute left-0 right-0 top-20 z-50 mt-1 max-h-60 overflow-y-auto rounded-lg border border-slate-200/80 bg-white py-1 shadow-lg"
        >
          {loading && (
            <div className="flex items-center justify-center py-4 text-[10px] text-muted-foreground">
              Searching local index...
            </div>
          )}
          
          {!loading && results.length === 0 && (
            <div className="px-4 py-3 text-center text-[10px] text-muted-foreground">
              No places found
            </div>
          )}

          {!loading && results.length > 0 && (
            <ul className="flex flex-col">
              {results.map((result) => (
                <li key={result.id}>
                  <button
                    type="button"
                    onClick={() => handleSelectResult(result)}
                    className="flex w-full items-start gap-2.5 px-3 py-2 text-left hover:bg-slate-50 transition-colors"
                  >
                    {getCategoryIcon(result.category)}
                    <div className="flex-1 min-w-0">
                      <p className="truncate text-xs font-semibold text-slate-800">{result.display_name}</p>
                      <p className="text-[9px] text-muted-foreground mt-0.5 uppercase tracking-wider">
                        {result.category_label} &bull; {result.source}
                      </p>
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          )}
          
          {error && (
            <div className="px-4 py-2 text-[10px] text-rose-500 font-semibold">
              {error}
            </div>
          )}
        </div>
      )}

      {/* Selected Action Panel */}
      {selectedResult && (
        <div className="flex flex-col gap-2 rounded-lg bg-[#F1F5F9]/50 border border-slate-200/40 p-2.5 mt-1 transition-all">
          <div className="flex items-start gap-2">
            <div className="mt-0.5">{getCategoryIcon(selectedResult.category)}</div>
            <div className="flex-1 min-w-0">
              <h4 className="text-xs font-bold text-slate-700 truncate">{selectedResult.display_name}</h4>
              <p className="text-[9px] text-muted-foreground mt-0.5">{selectedResult.category_label}</p>
            </div>
          </div>
          
          {!selectedResult.inside_project_area && (
            <div className="text-[9px] font-semibold text-amber-700 bg-amber-50 rounded border border-amber-200/50 px-2 py-1 leading-snug">
              This location is outside the current Nasr City study area.
            </div>
          )}

          <div className="flex gap-2 border-t border-slate-200/50 pt-2 mt-1">
            <button
              type="button"
              onClick={() => onSetStart({ lat: selectedResult.lat, lon: selectedResult.lon })}
              className="flex-1 flex items-center justify-center gap-1 rounded bg-[#2C5EAD] text-white text-[10px] font-bold py-1.5 px-2 hover:bg-[#1a4a91] shadow-sm transition-all"
            >
              <Navigation className="size-3" />
              Set Start
            </button>
            <button
              type="button"
              onClick={() => onSetDestination({ lat: selectedResult.lat, lon: selectedResult.lon })}
              className="flex-1 flex items-center justify-center gap-1 rounded bg-[#10b981] text-white text-[10px] font-bold py-1.5 px-2 hover:bg-[#0d9480] shadow-sm transition-all"
            >
              <Navigation className="size-3" />
              Set Destination
            </button>
            <button
              type="button"
              onClick={handleClear}
              className="rounded bg-slate-200 text-slate-700 text-[10px] font-bold py-1.5 px-2 hover:bg-slate-300 transition-all"
            >
              Clear
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
