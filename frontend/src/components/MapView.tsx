import React, { useEffect, useRef, useState } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { FeatureCollection, LayerToggles } from "../types/api";
import { formatNumber, formatInteger } from "../utils/format";

const BASEMAP_STYLE = "https://tiles.openfreemap.org/styles/liberty";

const escapeHtml = (value: unknown) => String(value ?? "")
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;")
  .replaceAll("'", "&#039;");

const emptyCollection = { type: "FeatureCollection", features: [] } as const;

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
    let routePulseTimer: ReturnType<typeof setInterval> | undefined;

    const map = new maplibregl.Map({
      container: mapContainerRef.current,
      style: BASEMAP_STYLE,
      center: [31.365, 30.055],
      zoom: 12.2,
      minZoom: 10,
      attributionControl: { compact: true },
    });

    mapRef.current = map;

    map.addControl(new maplibregl.NavigationControl({ showCompass: false, visualizePitch: false }), "top-right");
    map.addControl(new maplibregl.ScaleControl({ unit: "metric", maxWidth: 100 }), "bottom-left");

    map.on("load", () => {
      setMapLoaded(true);

      const firstSymbolLayer = map.getStyle().layers.find((layer) => layer.type === "symbol")?.id;

      const addGeoJSONSource = (id: string, data: any) => {
        map.addSource(id, {
          type: "geojson",
          data: data || emptyCollection,
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

      map.addLayer({
        id: "boundary-layer",
        type: "line",
        source: "boundary",
        paint: {
          "line-color": "#2C5EAD",
          "line-width": 2.5,
          "line-opacity": 0.88,
          "line-dasharray": [3, 1.5],
        },
      }, firstSymbolLayer);

      map.addLayer({
        id: "grid-layer",
        type: "line",
        source: "grid",
        paint: {
          "line-color": "#8186D5",
          "line-width": 0.7,
          "line-opacity": 0.42,
        },
      }, firstSymbolLayer);

      // Common risk colors expression
      const riskFillColor = [
        "match",
        ["get", "predicted_risk_class"],
        "high", "#ef4444",
        "medium", "#f59e0b",
        "low", "#10b981",
        "#64748b"
      ] as any;

      map.addLayer({
        id: "risk-summary-layer",
        type: "fill",
        source: "risk-summary",
        paint: {
          "fill-color": riskFillColor,
          "fill-opacity": 0.28,
          "fill-outline-color": "rgba(255,255,255,0.45)",
        },
      }, firstSymbolLayer);

      map.addLayer({
        id: "latest-risk-layer",
        type: "fill",
        source: "latest-risk",
        paint: {
          "fill-color": riskFillColor,
          "fill-opacity": 0.3,
          "fill-outline-color": "rgba(255,255,255,0.5)",
        },
      }, firstSymbolLayer);

      map.addLayer({
        id: "top-rain-risk-layer",
        type: "fill",
        source: "top-rain-risk",
        paint: {
          "fill-color": riskFillColor,
          "fill-opacity": 0.3,
          "fill-outline-color": "rgba(255,255,255,0.5)",
        },
      }, firstSymbolLayer);

      map.addLayer({
        id: "selected-risk-layer",
        type: "fill",
        source: "selected-risk",
        paint: {
          "fill-color": riskFillColor,
          "fill-opacity": 0.32,
          "fill-outline-color": "rgba(255,255,255,0.55)",
        },
      }, firstSymbolLayer);

      map.addLayer({
        id: "facilities-layer",
        type: "circle",
        source: "facilities",
        paint: {
          "circle-color": "#494CA2",
          "circle-radius": ["interpolate", ["linear"], ["zoom"], 10, 4.5, 15, 7],
          "circle-stroke-color": "#ffffff",
          "circle-stroke-width": 2.5,
          "circle-opacity": 0.96,
        },
      });

      map.addLayer({
        id: "facilities-label-layer",
        type: "symbol",
        source: "facilities",
        minzoom: 12.5,
        layout: {
          "text-field": ["coalesce", ["get", "name"], "Emergency facility"],
          "text-size": 11,
          "text-offset": [0, 1.25],
          "text-anchor": "top",
          "text-allow-overlap": false,
        },
        paint: {
          "text-color": "#494CA2",
          "text-halo-color": "#ffffff",
          "text-halo-width": 2,
        },
      });

      const poiCategories = [
        { id: "hospitals", values: ["hospital", "clinic", "doctors", "pharmacy"], color: "#2C5EAD" },
        { id: "mosques", values: ["mosque", "place_of_worship"], color: "#494CA2" },
        { id: "malls", values: ["mall", "department_store", "supermarket", "marketplace"], color: "#1591DC" },
        { id: "education", values: ["school", "college", "university", "kindergarten"], color: "#8186D5" },
      ];

      poiCategories.forEach(({ id, values, color }) => {
        const categoryFilter: maplibregl.FilterSpecification = [
          "any",
          ["match", ["get", "class"], values, true, false],
          ["match", ["get", "subclass"], values, true, false],
        ];
        map.addLayer({
          id: `poi-${id}-halo`,
          type: "circle",
          source: "openmaptiles",
          "source-layer": "poi",
          minzoom: 11.5,
          filter: categoryFilter,
          paint: {
            "circle-color": "#ffffff",
            "circle-radius": 6.5,
            "circle-opacity": 0.9,
          },
        });
        map.addLayer({
          id: `poi-${id}-layer`,
          type: "circle",
          source: "openmaptiles",
          "source-layer": "poi",
          minzoom: 11.5,
          filter: categoryFilter,
          paint: {
            "circle-color": color,
            "circle-radius": 4.25,
            "circle-stroke-color": "#ffffff",
            "circle-stroke-width": 1,
          },
        });
      });

      map.addLayer({
        id: "normal-route-layer",
        type: "line",
        source: "normal-route",
        paint: {
          "line-color": "#8186D5",
          "line-width": 3,
          "line-dasharray": [2, 2],
          "line-opacity": 0.72,
        },
      });

      map.addLayer({
        id: "safe-route-halo-layer",
        type: "line",
        source: "safe-route",
        layout: { "line-cap": "round", "line-join": "round" },
        paint: {
          "line-color": "#4BB8FA",
          "line-width": 10,
          "line-opacity": 0.22,
          "line-blur": 4,
        },
      });

      map.addLayer({
        id: "safe-route-layer",
        type: "line",
        source: "safe-route",
        paint: {
          "line-color": "#1591DC",
          "line-width": 5,
          "line-opacity": 0.95,
        },
      });

      let haloEmphasis = false;
      routePulseTimer = setInterval(() => {
        if (!map.getLayer("safe-route-halo-layer")) return;
        haloEmphasis = !haloEmphasis;
        map.setPaintProperty("safe-route-halo-layer", "line-opacity-transition", { duration: 900, delay: 0 });
        map.setPaintProperty("safe-route-halo-layer", "line-opacity", haloEmphasis ? 0.28 : 0.16);
      }, 1100);

      // Hover feedback cursor on layers
      const interactiveLayers = [
        "latest-risk-layer",
        "top-rain-risk-layer",
        "risk-summary-layer",
        "selected-risk-layer",
        "facilities-layer",
        "poi-hospitals-layer",
        "poi-mosques-layer",
        "poi-malls-layer",
        "poi-education-layer",
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
            <div class="map-popup-card">
              <h4>${escapeHtml(props.name || "Emergency Facility")}</h4>
              <p><strong>Type:</strong> ${escapeHtml(props.facility_type || props.amenity || "emergency facility")}</p>
              <p><strong>Source:</strong> ${escapeHtml(props.source || "OpenStreetMap")}</p>
            </div>
          `;
        } else if (feature.layer.id.startsWith("poi-")) {
          html = `
            <div class="map-popup-card">
              <h4>${escapeHtml(props.name || props.name_en || "Map place")}</h4>
              <p><strong>Category:</strong> ${escapeHtml(props.subclass || props.class || "point of interest")}</p>
              <p><strong>Source:</strong> OpenStreetMap basemap</p>
            </div>
          `;
        } else {
          const score = formatNumber(props.y_pred, 4);
          const rain = props.rain_24h_mm !== undefined && props.rain_24h_mm !== null ? `${formatNumber(props.rain_24h_mm, 1)} mm` : "—";
          const pop = formatInteger(props.population_sum);
          const built = formatNumber(props.built_surface_mean, 2);
          
          html = `
            <div class="map-popup-card">
              <h4>Zone: ${escapeHtml(props.zone_code || "Unknown")}</h4>
              <p><strong>Predicted risk:</strong> <span class="risk-${escapeHtml(props.predicted_risk_class || "medium")}">${escapeHtml(props.predicted_risk_class || "medium")}</span></p>
              <p><strong class="text-slate-400">Risk Score:</strong> ${score}</p>
              ${props.event_id ? `<p><strong>Event:</strong> ${escapeHtml(props.event_id)}</p>` : ""}
              <p><strong>Rain (24h):</strong> ${rain}</p>
              <p><strong>Population:</strong> ${pop}</p>
              <p><strong>Built surface mean:</strong> ${built}</p>
            </div>
          `;
        }

        new maplibregl.Popup({ className: "light-map-popup", closeButton: true, maxWidth: "280px" })
          .setLngLat(coords)
          .setHTML(html)
          .addTo(map);
      });
    });

    return () => {
      if (routePulseTimer) clearInterval(routePulseTimer);
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
        source.setData(data || emptyCollection);
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
    setLayerVisibility("facilities-label-layer", layers.facilities);
    setLayerVisibility("latest-risk-layer", layers.latestRisk);
    setLayerVisibility("top-rain-risk-layer", layers.topRainRisk);
    setLayerVisibility("risk-summary-layer", layers.riskSummary);
    setLayerVisibility("selected-risk-layer", layers.selectedRisk);

    const roadAndLabelLayers = map.getStyle().layers.filter((layer) =>
      layer.id.startsWith("road_") ||
      layer.id.startsWith("bridge_") ||
      layer.id.startsWith("tunnel_") ||
      layer.id.startsWith("highway-") ||
      layer.id.startsWith("label_")
    );
    roadAndLabelLayers.forEach((layer) => setLayerVisibility(layer.id, layers.roadsLabels));

    (["hospitals", "mosques", "malls", "education"] as const).forEach((category) => {
      setLayerVisibility(`poi-${category}-halo`, layers[category]);
      setLayerVisibility(`poi-${category}-layer`, layers[category]);
    });

    const showNormal = routeVisibility === "normal" || routeVisibility === "both";
    const showSafe = routeVisibility === "safe" || routeVisibility === "both";
    setLayerVisibility("normal-route-layer", showNormal);
    setLayerVisibility("safe-route-halo-layer", showSafe);
    setLayerVisibility("safe-route-layer", showSafe);
  }, [mapLoaded, layers, routeVisibility]);

  return (
    <div className="relative size-full bg-[#e9eef4]">
      <div ref={mapContainerRef} className="size-full" aria-label="Interactive Nasr City weather-impact map" />
      <div className="pointer-events-none absolute left-4 top-4 rounded-full border border-white/80 bg-white/90 px-3 py-1.5 text-[10px] font-semibold text-primary shadow-md backdrop-blur">
        Light city map · OpenStreetMap context
      </div>
    </div>
  );
};
