import { useEffect, useRef, useState } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { RotateCcw } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import type {
  FeatureCollection,
  LayerToggles,
  PlaceProperties,
  RouteComparison,
  RouteCoordinate,
} from "../types/api";
import { EMPTY_VALUE, formatInteger, formatNumber, formatPercent } from "../utils/format";
import {
  getCategoryLabel,
  getEventLabel,
  getFieldLabel,
  getPlaceIcon,
  getRiskLevelLabel,
  getRouteQualityLabel,
  getRouteTypeLabel,
  getZoneLabel,
} from "../utils/labels";

const BASEMAP_STYLE = "https://tiles.openfreemap.org/styles/liberty";
const emptyCollection = { type: "FeatureCollection", features: [] } as const;
type MapSourceData = Parameters<maplibregl.GeoJSONSource["setData"]>[0];

const escapeHtml = (value: unknown) =>
  String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

const toMapSourceData = (data: FeatureCollection | null): MapSourceData =>
  (data ?? emptyCollection) as MapSourceData;

const pointCoordinates = (coordinates: unknown): [number, number] | null => {
  if (!Array.isArray(coordinates) || coordinates.length < 2) return null;
  const [lon, lat] = coordinates;
  return typeof lon === "number" && typeof lat === "number" ? [lon, lat] : null;
};

const safePlaceName = (properties: PlaceProperties) => {
  const title = properties.display_name?.trim();
  if (!title || /^(?:osm[-:_ ]?)?(?:node|way|relation)?[-:_ ]?\d+$/i.test(title)) {
    return properties.category_label || getCategoryLabel(properties.category);
  }
  return title;
};

const categoryVisible = (
  category: PlaceProperties["category"],
  placeId: string,
  layers: LayerToggles,
  emergencyPlaceIds: Set<string>,
) => {
  const visibleByCategory: Record<string, boolean> = {
    hospital: layers.hospitals,
    clinic: layers.clinics,
    mosque: layers.mosques,
    mall: layers.malls,
    school: layers.schools,
    university: layers.universities,
    police: layers.police,
    fire_station: layers.fireStations,
    emergency: layers.emergency,
    landmark: false,
  };
  return visibleByCategory[category] || (layers.emergency && emergencyPlaceIds.has(placeId));
};

interface MapViewProps {
  layers: LayerToggles;
  routeVisibility: "normal" | "safe" | "both";
  boundaryData: FeatureCollection | null;
  gridData: FeatureCollection | null;
  placesData: FeatureCollection<PlaceProperties> | null;
  emergencyPlaceIds: Set<string>;
  latestRiskData: FeatureCollection | null;
  topRainRiskData: FeatureCollection | null;
  riskSummaryData: FeatureCollection | null;
  selectedEventRiskData: FeatureCollection | null;
  normalRouteData: FeatureCollection | null;
  safeRouteData: FeatureCollection | null;
  routeComparison: RouteComparison | null;
  routeOrigin: RouteCoordinate | null;
  routeDestination: RouteCoordinate | null;
  routingLoading: boolean;
  routingError: string | null;
  onMapPointClick: (coordinate: RouteCoordinate) => void;
  onResetRoute: () => void;
}

export const MapView = ({
  layers,
  routeVisibility,
  boundaryData,
  gridData,
  placesData,
  emergencyPlaceIds,
  latestRiskData,
  topRainRiskData,
  riskSummaryData,
  selectedEventRiskData,
  normalRouteData,
  safeRouteData,
  routeComparison,
  routeOrigin,
  routeDestination,
  routingLoading,
  routingError,
  onMapPointClick,
  onResetRoute,
}: MapViewProps) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const placeMarkersRef = useRef<maplibregl.Marker[]>([]);
  const routeMarkersRef = useRef<maplibregl.Marker[]>([]);
  const onMapPointClickRef = useRef(onMapPointClick);
  const routingLoadingRef = useRef(routingLoading);
  const routeComparisonRef = useRef(routeComparison);
  const [mapLoaded, setMapLoaded] = useState(false);

  useEffect(() => {
    onMapPointClickRef.current = onMapPointClick;
    routingLoadingRef.current = routingLoading;
    routeComparisonRef.current = routeComparison;
  }, [onMapPointClick, routeComparison, routingLoading]);

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
    map.addControl(
      new maplibregl.NavigationControl({ showCompass: false, visualizePitch: false }),
      "top-right",
    );
    map.addControl(new maplibregl.ScaleControl({ unit: "metric", maxWidth: 100 }), "bottom-left");

    map.on("load", () => {
      setMapLoaded(true);
      const firstSymbolLayer = map.getStyle().layers.find((layer) => layer.type === "symbol")?.id;
      const addGeoJSONSource = (id: string) => {
        map.addSource(id, { type: "geojson", data: emptyCollection });
      };

      [
        "boundary",
        "grid",
        "latest-risk",
        "top-rain-risk",
        "risk-summary",
        "selected-risk",
        "normal-route",
        "safe-route",
      ].forEach(addGeoJSONSource);

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
        paint: { "line-color": "#8186D5", "line-width": 0.7, "line-opacity": 0.42 },
      }, firstSymbolLayer);

      const riskFillColor = [
        "match",
        ["get", "predicted_risk_class"],
        "high", "#ef4444",
        "medium", "#f59e0b",
        "low", "#10b981",
        "#64748b",
      ] as maplibregl.ExpressionSpecification;
      [
        ["risk-summary-layer", "risk-summary", 0.28],
        ["latest-risk-layer", "latest-risk", 0.3],
        ["top-rain-risk-layer", "top-rain-risk", 0.3],
        ["selected-risk-layer", "selected-risk", 0.32],
      ].forEach(([id, source, opacity]) => {
        map.addLayer({
          id: id as string,
          type: "fill",
          source: source as string,
          paint: {
            "fill-color": riskFillColor,
            "fill-opacity": opacity as number,
            "fill-outline-color": "rgba(255,255,255,0.5)",
            "fill-opacity-transition": { duration: 220, delay: 0 },
          },
        }, firstSymbolLayer);
      });

      map.addLayer({
        id: "normal-route-layer",
        type: "line",
        source: "normal-route",
        layout: { "line-cap": "round", "line-join": "round" },
        paint: {
          "line-color": "#8186D5",
          "line-width": 3.5,
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
          "line-width": 11,
          "line-opacity": 0.2,
          "line-blur": 4,
        },
      });
      map.addLayer({
        id: "safe-route-layer",
        type: "line",
        source: "safe-route",
        layout: { "line-cap": "round", "line-join": "round" },
        paint: { "line-color": "#1591DC", "line-width": 5, "line-opacity": 0.96 },
      });

      if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        let emphasized = false;
        routePulseTimer = setInterval(() => {
          if (!map.getLayer("safe-route-halo-layer")) return;
          emphasized = !emphasized;
          map.setPaintProperty(
            "safe-route-halo-layer",
            "line-opacity-transition",
            { duration: 900, delay: 0 },
          );
          map.setPaintProperty("safe-route-halo-layer", "line-opacity", emphasized ? 0.28 : 0.14);
        }, 1100);
      }

      const riskLayers = [
        "latest-risk-layer",
        "top-rain-risk-layer",
        "risk-summary-layer",
        "selected-risk-layer",
      ];
      const routeLayers = ["normal-route-layer", "safe-route-layer"];
      [...riskLayers, ...routeLayers].forEach((layerId) => {
        map.on("mouseenter", layerId, () => { map.getCanvas().style.cursor = "pointer"; });
        map.on("mouseleave", layerId, () => { map.getCanvas().style.cursor = ""; });
      });

      map.on("click", (event) => {
        const interactiveLayers = [...riskLayers, ...routeLayers].filter(
          (layerId) => map.getLayer(layerId) && map.getLayoutProperty(layerId, "visibility") !== "none",
        );
        const features = interactiveLayers.length
          ? map.queryRenderedFeatures(event.point, { layers: interactiveLayers })
          : [];
        const feature = features[0];
        if (feature) {
          const properties = feature.properties ?? {};
          const isRouteFeature = routeLayers.includes(feature.layer.id);
          let html: string;
          if (isRouteFeature) {
            const comparison = routeComparisonRef.current;
            html = `
              <div class="map-popup-card">
                <h4>Route Details</h4>
                <p><strong>Route Type:</strong> ${escapeHtml(getRouteTypeLabel(properties.route_type))}</p>
                <p><strong>Risk Reduction:</strong> ${formatPercent(comparison?.risk_reduction_percent, 1)}</p>
                <p><strong>ETA Tradeoff:</strong> ${formatPercent(comparison?.eta_tradeoff_percent, 1)}</p>
                <p><strong>Destination:</strong> ${escapeHtml(comparison?.selected_destination_facility_name || "Selected map point")}</p>
                <p><strong>Route Quality:</strong> ${escapeHtml(getRouteQualityLabel(comparison?.safe_route_quality))}</p>
              </div>`;
          } else {
            const rain = properties.rain_24h_mm == null
              ? EMPTY_VALUE
              : `${formatNumber(properties.rain_24h_mm, 1)} mm`;
            html = `
              <div class="map-popup-card">
                <h4>${escapeHtml(getZoneLabel(properties.zone_code))}</h4>
                <p><strong>${getFieldLabel("predicted_risk_class")}:</strong> <span class="risk-${escapeHtml(properties.predicted_risk_class || "medium")}">${escapeHtml(getRiskLevelLabel(properties.predicted_risk_class))}</span></p>
                <p><strong>${getFieldLabel("y_pred")}:</strong> ${formatNumber(properties.y_pred, 4)}</p>
                ${properties.event_id ? `<p><strong>${getFieldLabel("event_id")}:</strong> ${escapeHtml(getEventLabel(properties.event_id))}</p>` : ""}
                <p><strong>${getFieldLabel("rain_24h_mm")}:</strong> ${rain}</p>
                <p><strong>${getFieldLabel("population_sum")}:</strong> ${formatInteger(properties.population_sum)}</p>
                <p><strong>${getFieldLabel("built_surface_mean")}:</strong> ${formatNumber(properties.built_surface_mean, 2)}</p>
              </div>`;
          }
          new maplibregl.Popup({ className: "light-map-popup", closeButton: true, maxWidth: "280px" })
            .setLngLat(event.lngLat)
            .setHTML(html)
            .addTo(map);
          if (isRouteFeature) return;
        }
        if (!routingLoadingRef.current) {
          onMapPointClickRef.current({ lat: event.lngLat.lat, lon: event.lngLat.lng });
        }
      });
    });

    return () => {
      if (routePulseTimer) clearInterval(routePulseTimer);
      placeMarkersRef.current.forEach((marker) => marker.remove());
      routeMarkersRef.current.forEach((marker) => marker.remove());
      map.remove();
    };
  }, []);

  useEffect(() => {
    if (!mapRef.current || !mapLoaded) return;
    const map = mapRef.current;
    const updateSource = (id: string, data: FeatureCollection | null) => {
      const source = map.getSource(id) as maplibregl.GeoJSONSource | undefined;
      source?.setData(toMapSourceData(data));
    };
    updateSource("boundary", boundaryData);
    updateSource("grid", gridData);
    updateSource("latest-risk", latestRiskData);
    updateSource("top-rain-risk", topRainRiskData);
    updateSource("risk-summary", riskSummaryData);
    updateSource("selected-risk", selectedEventRiskData);
    updateSource("normal-route", normalRouteData);
    updateSource("safe-route", safeRouteData);
  }, [
    boundaryData,
    gridData,
    latestRiskData,
    mapLoaded,
    normalRouteData,
    riskSummaryData,
    safeRouteData,
    selectedEventRiskData,
    topRainRiskData,
  ]);

  useEffect(() => {
    if (!mapRef.current || !mapLoaded) return;
    const map = mapRef.current;
    placeMarkersRef.current.forEach((marker) => marker.remove());
    placeMarkersRef.current = [];
    for (const feature of placesData?.features ?? []) {
      const properties = feature.properties;
      if (!categoryVisible(properties.category, properties.place_id, layers, emergencyPlaceIds)) {
        continue;
      }
      const coordinates = pointCoordinates(feature.geometry.coordinates);
      if (!coordinates) continue;

      const element = document.createElement("button");
      element.type = "button";
      element.className = "place-marker";
      element.dataset.category = properties.category;
      element.setAttribute("aria-label", `${safePlaceName(properties)}, ${properties.category_label}`);
      element.textContent = getPlaceIcon(properties.category);
      element.addEventListener("click", (event) => {
        event.stopPropagation();
        if (!routingLoadingRef.current) {
          onMapPointClickRef.current({ lat: coordinates[1], lon: coordinates[0] });
        }
      });

      const popup = new maplibregl.Popup({ offset: 20, maxWidth: "260px" }).setHTML(`
        <div class="map-popup-card">
          <h4>Place Details</h4>
          <p><strong>Place Name:</strong> ${escapeHtml(safePlaceName(properties))}</p>
          <p><strong>Category:</strong> ${escapeHtml(properties.category_label || getCategoryLabel(properties.category))}</p>
          <p><strong>Source:</strong> ${escapeHtml(properties.source || "OpenStreetMap")}</p>
        </div>`);
      const marker = new maplibregl.Marker({ element, anchor: "bottom" })
        .setLngLat(coordinates)
        .setPopup(popup)
        .addTo(map);
      placeMarkersRef.current.push(marker);
    }
    return () => {
      placeMarkersRef.current.forEach((marker) => marker.remove());
      placeMarkersRef.current = [];
    };
  }, [emergencyPlaceIds, layers, mapLoaded, placesData]);

  useEffect(() => {
    if (!mapRef.current || !mapLoaded) return;
    routeMarkersRef.current.forEach((marker) => marker.remove());
    routeMarkersRef.current = [];
    const addRouteMarker = (coordinate: RouteCoordinate, label: "A" | "B") => {
      const element = document.createElement("div");
      element.className = `route-point-marker route-point-marker--${label.toLowerCase()}`;
      element.textContent = label;
      element.setAttribute("aria-label", label === "A" ? "Route origin" : "Route destination");
      const marker = new maplibregl.Marker({ element, anchor: "center" })
        .setLngLat([coordinate.lon, coordinate.lat])
        .addTo(mapRef.current!);
      routeMarkersRef.current.push(marker);
    };
    if (routeOrigin) addRouteMarker(routeOrigin, "A");
    if (routeDestination) addRouteMarker(routeDestination, "B");
    return () => {
      routeMarkersRef.current.forEach((marker) => marker.remove());
      routeMarkersRef.current = [];
    };
  }, [mapLoaded, routeDestination, routeOrigin]);

  useEffect(() => {
    if (!mapRef.current || !mapLoaded) return;
    const map = mapRef.current;
    const setLayerVisibility = (id: string, visible: boolean) => {
      if (map.getLayer(id)) map.setLayoutProperty(id, "visibility", visible ? "visible" : "none");
    };
    setLayerVisibility("boundary-layer", layers.boundary);
    setLayerVisibility("grid-layer", layers.grid);
    setLayerVisibility("latest-risk-layer", layers.latestRisk);
    setLayerVisibility("top-rain-risk-layer", layers.topRainRisk);
    setLayerVisibility("risk-summary-layer", layers.riskSummary);
    setLayerVisibility("selected-risk-layer", layers.selectedRisk);
    map.getStyle().layers
      .filter((layer) => /^(road_|bridge_|tunnel_|highway-|label_)/.test(layer.id))
      .forEach((layer) => setLayerVisibility(layer.id, layers.roadsLabels));
    const showNormal = routeVisibility === "normal" || routeVisibility === "both";
    const showSafe = routeVisibility === "safe" || routeVisibility === "both";
    setLayerVisibility("normal-route-layer", showNormal);
    setLayerVisibility("safe-route-halo-layer", showSafe);
    setLayerVisibility("safe-route-layer", showSafe);
  }, [layers, mapLoaded, routeVisibility]);

  const routeHint = routingLoading
    ? "Calculating weather-aware routes..."
    : routingError
      ? "Choose different points or reset the route"
      : routeDestination
        ? "Route ready • click the map again to clear"
        : routeOrigin
          ? "Select destination"
          : "Click the map to set origin";

  return (
    <div className="relative size-full bg-[#e9eef4]">
      <div
        ref={mapContainerRef}
        className="size-full"
        aria-label="Interactive Nasr City weather-impact map"
      />
      {routingLoading ? (
        <div className="route-loading-bar absolute inset-x-0 top-0 z-20">
          <Progress value={68} aria-label="Calculating routes" />
        </div>
      ) : null}
      <div className="absolute left-4 top-4 z-10 flex max-w-[calc(100%-5rem)] items-center gap-2 rounded-full border border-white/80 bg-white/92 px-3 py-2 text-[10px] font-semibold text-primary shadow-md backdrop-blur">
        <span className="route-hint-dot" aria-hidden="true" />
        {routeHint}
      </div>
      {routeOrigin ? (
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="absolute left-4 top-14 z-10 bg-card/95 shadow-md"
          onClick={onResetRoute}
          disabled={routingLoading}
        >
          <RotateCcw data-icon="inline-start" /> Reset Route
        </Button>
      ) : null}
      <div className="pointer-events-none absolute bottom-7 left-4 rounded-full border border-white/80 bg-white/90 px-3 py-1.5 text-[9px] font-medium text-muted-foreground shadow-sm backdrop-blur">
        Light map • OpenStreetMap context
      </div>
    </div>
  );
};
