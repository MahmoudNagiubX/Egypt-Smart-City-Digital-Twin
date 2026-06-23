import React, { useEffect, useRef, useState } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { FeatureCollection, LayerToggles } from "../types/api";
import { formatNumber, formatInteger } from "../utils/format";


interface MapViewProps {
  layers: LayerToggles;
  routeVisibility: "normal" | "safe" | "both";
  boundaryData: FeatureCollection | null;
  gridData: FeatureCollection | null;
  facilitiesData: FeatureCollection | null;
  latestRiskData: FeatureCollection | null;
  topRainRiskData: FeatureCollection | null;
  riskSummaryData: FeatureCollection | null;
  selectedEventRiskData: FeatureCollection | null;
  normalRouteData: FeatureCollection | null;
  safeRouteData: FeatureCollection | null;
}

export const MapView: React.FC<MapViewProps> = ({
  layers,
  routeVisibility,
  boundaryData,
  gridData,
  facilitiesData,
  latestRiskData,
  topRainRiskData,
  riskSummaryData,
  selectedEventRiskData,
  normalRouteData,
  safeRouteData,
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const [mapLoaded, setMapLoaded] = useState(false);

  useEffect(() => {
    if (!mapContainerRef.current) return;

    // Dark Matter basemap GL style that is token-free and highly performant
    const map = new maplibregl.Map({
      container: mapContainerRef.current,
      style: "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
      center: [31.365, 30.055],
      zoom: 11.8,
      attributionControl: false,
    });

    mapRef.current = map;

    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");

    map.on("load", () => {
      setMapLoaded(true);

      // Add all sources
      const addGeoJSONSource = (id: string, data: any) => {
        map.addSource(id, {
          type: "geojson",
          data: data || { type: "FeatureCollection", features: [] },
        });
      };

      addGeoJSONSource("boundary", boundaryData);
      addGeoJSONSource("grid", gridData);
      addGeoJSONSource("facilities", facilitiesData);
      addGeoJSONSource("latest-risk", latestRiskData);
      addGeoJSONSource("top-rain-risk", topRainRiskData);
      addGeoJSONSource("risk-summary", riskSummaryData);
      addGeoJSONSource("selected-risk", selectedEventRiskData);
      addGeoJSONSource("normal-route", normalRouteData);
      addGeoJSONSource("safe-route", safeRouteData);

      // 1. Boundary layer (cyan outline)
      map.addLayer({
        id: "boundary-layer",
        type: "line",
        source: "boundary",
        paint: {
          "line-color": "#22d3ee",
          "line-width": 2,
          "line-opacity": 0.8,
        },
      });

      // 2. Grid outline layer (thin slate)
      map.addLayer({
        id: "grid-layer",
        type: "line",
        source: "grid",
        paint: {
          "line-color": "#475569",
          "line-width": 0.5,
          "line-opacity": 0.4,
        },
      });

      // Common risk colors expression
      const riskFillColor = [
        "match",
        ["get", "predicted_risk_class"],
        "high", "#ef4444",
        "medium", "#f59e0b",
        "low", "#10b981",
        "#64748b"
      ] as any;

      // 3. Risk Summary Layer
      map.addLayer({
        id: "risk-summary-layer",
        type: "fill",
        source: "risk-summary",
        paint: {
          "fill-color": riskFillColor,
          "fill-opacity": 0.4,
        },
      });

      // 4. Latest Event Risk Layer
      map.addLayer({
        id: "latest-risk-layer",
        type: "fill",
        source: "latest-risk",
        paint: {
          "fill-color": riskFillColor,
          "fill-opacity": 0.45,
        },
      });

      // 5. Top Rain Risk Layer
      map.addLayer({
        id: "top-rain-risk-layer",
        type: "fill",
        source: "top-rain-risk",
        paint: {
          "fill-color": riskFillColor,
          "fill-opacity": 0.45,
        },
      });

      // 6. Selected Event Risk Layer
      map.addLayer({
        id: "selected-risk-layer",
        type: "fill",
        source: "selected-risk",
        paint: {
          "fill-color": riskFillColor,
          "fill-opacity": 0.45,
        },
      });

      // 7. Facilities layer (circles)
      map.addLayer({
        id: "facilities-layer",
        type: "circle",
        source: "facilities",
        paint: {
          "circle-color": "#ef4444",
          "circle-radius": 6,
          "circle-stroke-color": "#ffffff",
          "circle-stroke-width": 1.5,
          "circle-opacity": 0.9,
        },
      });

      // 8. Normal Route (dashed white/gray)
      map.addLayer({
        id: "normal-route-layer",
        type: "line",
        source: "normal-route",
        paint: {
          "line-color": "#94a3b8",
          "line-width": 3,
          "line-dasharray": [2, 2],
          "line-opacity": 0.8,
        },
      });

      // 9. Safe Route (glowing cyan line)
      map.addLayer({
        id: "safe-route-layer",
        type: "line",
        source: "safe-route",
        paint: {
          "line-color": "#06b6d4",
          "line-width": 5.5,
          "line-opacity": 0.95,
        },
      });

      // Hover feedback cursor on layers
      const interactiveLayers = [
        "latest-risk-layer",
        "top-rain-risk-layer",
        "risk-summary-layer",
        "selected-risk-layer",
        "facilities-layer"
      ];

      interactiveLayers.forEach(l => {
        map.on("mouseenter", l, () => {
          map.getCanvas().style.cursor = "pointer";
        });
        map.on("mouseleave", l, () => {
          map.getCanvas().style.cursor = "";
        });
      });

      // Popup on click
      map.on("click", (e) => {
        const activeLayers = interactiveLayers.filter(l => {
          return map.getLayer(l) && map.getLayoutProperty(l, "visibility") !== "none";
        });

        if (!activeLayers.length) return;

        const features = map.queryRenderedFeatures(e.point, { layers: activeLayers });
        if (!features.length) return;

        const feature = features[0];
        const props = feature.properties;
        const coords = e.lngLat;

        let html = "";
        if (feature.layer.id === "facilities-layer") {
          html = `
            <div class="p-2 text-slate-100 bg-slate-950 border border-slate-800 rounded text-xs max-w-xs leading-relaxed font-sans">
              <h4 class="font-bold text-cyan-400 text-sm border-b border-slate-900 pb-1 mb-1">${props.name || "Emergency Facility"}</h4>
              <p><strong class="text-slate-400">Type:</strong> ${props.facility_type || props.amenity || "emergency_facility"}</p>
              <p><strong class="text-slate-400">Source:</strong> ${props.source || "OSM"}</p>
            </div>
          `;
        } else {
          const score = formatNumber(props.y_pred, 4);
          const rain = props.rain_24h_mm !== undefined && props.rain_24h_mm !== null ? `${formatNumber(props.rain_24h_mm, 1)} mm` : "—";
          const pop = formatInteger(props.population_sum);
          const built = formatNumber(props.built_surface_mean, 2);
          
          html = `
            <div class="p-2 text-slate-100 bg-slate-950 border border-slate-800 rounded text-xs max-w-xs leading-normal font-sans space-y-1">
              <h4 class="font-bold text-cyan-400 text-sm border-b border-slate-900 pb-1 mb-1">Zone: ${props.zone_code || "Unknown"}</h4>
              <p><strong class="text-slate-400">Predicted Risk:</strong> <span class="uppercase font-bold text-red-400">${props.predicted_risk_class || "medium"}</span></p>
              <p><strong class="text-slate-400">Risk Score:</strong> ${score}</p>
              ${props.event_id ? `<p><strong class="text-slate-400">Event:</strong> ${props.event_id}</p>` : ""}
              <p><strong class="text-slate-400">Rain (24h):</strong> ${rain}</p>
              <p><strong class="text-slate-400">Population:</strong> ${pop}</p>
              <p><strong class="text-slate-400">Built Surf Mean:</strong> ${built}</p>
            </div>
          `;
        }

        new maplibregl.Popup({ className: "dark-map-popup" })
          .setLngLat(coords)
          .setHTML(html)
          .addTo(map);
      });
    });

    return () => {
      map.remove();
    };
  }, []);

  // Update GeoJSON source data
  useEffect(() => {
    if (!mapRef.current || !mapLoaded) return;
    const map = mapRef.current;

    const updateSource = (id: string, data: any) => {
      const source = map.getSource(id) as maplibregl.GeoJSONSource;
      if (source) {
        source.setData(data || { type: "FeatureCollection", features: [] });
      }
    };

    updateSource("boundary", boundaryData);
    updateSource("grid", gridData);
    updateSource("facilities", facilitiesData);
    updateSource("latest-risk", latestRiskData);
    updateSource("top-rain-risk", topRainRiskData);
    updateSource("risk-summary", riskSummaryData);
    updateSource("selected-risk", selectedEventRiskData);
    updateSource("normal-route", normalRouteData);
    updateSource("safe-route", safeRouteData);
  }, [
    mapLoaded,
    boundaryData,
    gridData,
    facilitiesData,
    latestRiskData,
    topRainRiskData,
    riskSummaryData,
    selectedEventRiskData,
    normalRouteData,
    safeRouteData,
  ]);

  // Update visibilities based on layer toggles and route modes
  useEffect(() => {
    if (!mapRef.current || !mapLoaded) return;
    const map = mapRef.current;

    const setLayerVisibility = (id: string, visible: boolean) => {
      if (map.getLayer(id)) {
        map.setLayoutProperty(id, "visibility", visible ? "visible" : "none");
      }
    };

    setLayerVisibility("boundary-layer", layers.boundary);
    setLayerVisibility("grid-layer", layers.grid);
    setLayerVisibility("facilities-layer", layers.facilities);
    setLayerVisibility("latest-risk-layer", layers.latestRisk);
    setLayerVisibility("top-rain-risk-layer", layers.topRainRisk);
    setLayerVisibility("risk-summary-layer", layers.riskSummary);
    setLayerVisibility("selected-risk-layer", layers.selectedRisk);

    const showNormal = routeVisibility === "normal" || routeVisibility === "both";
    const showSafe = routeVisibility === "safe" || routeVisibility === "both";
    setLayerVisibility("normal-route-layer", showNormal);
    setLayerVisibility("safe-route-layer", showSafe);
  }, [mapLoaded, layers, routeVisibility]);

  return (
    <div className="relative w-full h-full bg-slate-950">
      <div ref={mapContainerRef} className="w-full h-full" />
    </div>
  );
};
