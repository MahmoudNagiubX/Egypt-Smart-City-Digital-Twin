import { useEffect, useRef, useState } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { Cross, Flame, GraduationCap, Landmark, MapPin, RotateCcw, School, Shield, ShoppingBag, Siren } from "lucide-react";
import { createRoot, type Root } from "react-dom/client";

import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import type {
  FeatureCollection,
  GeoJsonFeature,
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
  getRiskLevelLabel,
  getRouteQualityLabel,
  getRouteTypeLabel,
  getZoneLabel,
} from "../utils/labels";

const BASEMAP_STYLE = "https://tiles.openfreemap.org/styles/positron";
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

const polygonCentroid = (geometry: GeoJsonFeature["geometry"]): [number, number] | null => {
  const coordinates = geometry.coordinates;
  if (!Array.isArray(coordinates)) return null;
  const ring =
    geometry.type === "Polygon"
      ? coordinates[0]
      : geometry.type === "MultiPolygon"
        ? coordinates[0]?.[0]
        : null;
  if (!Array.isArray(ring) || ring.length === 0) return null;

  const points = ring.filter(
    (point): point is [number, number] =>
      Array.isArray(point) &&
      point.length >= 2 &&
      typeof point[0] === "number" &&
      typeof point[1] === "number",
  );
  if (!points.length) return null;

  const [lonSum, latSum] = points.reduce(
    ([lonTotal, latTotal], [lon, lat]) => [lonTotal + lon, latTotal + lat],
    [0, 0],
  );
  return [lonSum / points.length, latSum / points.length];
};

const riskScoreFromProperties = (properties: Record<string, unknown>) => {
  const numericScore = Number(
    properties.live_predicted_score ?? properties.predicted_score ?? properties.y_pred,
  );
  if (Number.isFinite(numericScore)) return Math.max(0, Math.min(1, numericScore));

  const riskClass = String(
    properties.live_risk_class ?? properties.predicted_risk_class ?? "low",
  ).toLowerCase();
  if (riskClass === "high") return 0.9;
  if (riskClass === "medium") return 0.55;
  return 0.18;
};

const toRiskCentroidCollection = (data: FeatureCollection | null): FeatureCollection => ({
  type: "FeatureCollection",
  features: (data?.features ?? [])
    .reduce<GeoJsonFeature[]>((features, feature) => {
      const coordinates = polygonCentroid(feature.geometry);
      if (!coordinates) return features;
      const score = riskScoreFromProperties(feature.properties ?? {});
      features.push({
        type: "Feature" as const,
        properties: {
          ...feature.properties,
          weather_intensity: score,
        },
        geometry: {
          type: "Point",
          coordinates,
        },
      });
      return features;
    }, []),
});

const placeIconMap = {
  hospital: Cross,
  clinic: Cross,
  doctors: Cross,
  police: Shield,
  fire_station: Flame,
  mall: ShoppingBag,
  mosque: Landmark,
  place_of_worship: Landmark,
  school: School,
  university: GraduationCap,
  emergency: Siren,
  default: MapPin,
} as const;

const markerCategory = (category: unknown) =>
  typeof category === "string" ? category.toLowerCase() : "default";


const containsArabic = (text?: string | null): boolean => {
  if (!text) return false;
  return /[\u0600-\u06FF]/.test(text);
};

const safePlaceName = (properties: PlaceProperties) => {
  const title = properties.display_name?.trim();
  if (
    !title ||
    /^(?:osm[-:_ ]?)?(?:node|way|relation)?[-:_ ]?\d+$/i.test(title) ||
    containsArabic(title)
  ) {
    return properties.category_label || getCategoryLabel(properties.category);
  }
  return title;
};

const categoryVisible = (
  rawCategory: PlaceProperties["category"],
  placeId: string,
  layers: LayerToggles,
  emergencyPlaceIds: Set<string>,
) => {
  let category = rawCategory?.toLowerCase();
  if (category === "doctors") category = "clinic";
  if (category === "place_of_worship") category = "mosque";

  // If a category has its own toggle, that toggle must be true for it to be visible.
  if (category === "hospital" && !layers.hospitals) return false;
  if (category === "clinic" && !layers.clinics) return false;
  if (category === "mosque" && !layers.mosques) return false;
  if (category === "mall" && !layers.malls) return false;
  if (category === "school" && !layers.schools) return false;
  if (category === "university" && !layers.universities) return false;
  if (category === "police" && !layers.police) return false;
  if (category === "fire_station" && !layers.fireStations) return false;
  if (category === "emergency" && !layers.emergency) return false;

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

  return !!visibleByCategory[category] || (layers.emergency && emergencyPlaceIds.has(placeId));
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
  liveRiskData: FeatureCollection | null;
  normalRouteData: FeatureCollection | null;
  safeRouteData: FeatureCollection | null;
  routeComparison: RouteComparison | null;
  routeOrigin: RouteCoordinate | null;
  routeDestination: RouteCoordinate | null;
  routingLoading: boolean;
  routingError: string | null;
  onMapPointClick: (coordinate: RouteCoordinate) => void;
  onResetRoute: () => void;
  riskFillOpacity: number;
  gridLineOpacity: number;
  riskDisplayMode: "focus" | "all";
  searchSelectedPoint: any;
  onSetStartPoint: (coordinate: RouteCoordinate) => void;
  onSetDestinationPoint: (coordinate: RouteCoordinate) => void;
  onZoneClick?: (zoneCode: string, eventId?: string | null) => void;
  selectedZoneCode?: string | null;
  isRoutePlanningActive?: boolean;
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
  liveRiskData,
  normalRouteData,
  safeRouteData,
  routeComparison,
  routeOrigin,
  routeDestination,
  routingLoading,
  routingError,
  onMapPointClick,
  onResetRoute,
  riskFillOpacity,
  gridLineOpacity,
  riskDisplayMode,
  searchSelectedPoint,
  onSetStartPoint,
  onSetDestinationPoint,
  onZoneClick,
  selectedZoneCode = null,
  isRoutePlanningActive = false,
}: MapViewProps) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const placeMarkersRef = useRef<maplibregl.Marker[]>([]);
  const placeMarkerRootsRef = useRef<Root[]>([]);
  const routeMarkersRef = useRef<maplibregl.Marker[]>([]);
  const searchMarkerRef = useRef<maplibregl.Marker | null>(null);
  const onMapPointClickRef = useRef(onMapPointClick);
  const routingLoadingRef = useRef(routingLoading);
  const routeComparisonRef = useRef(routeComparison);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [zoom, setZoom] = useState(12.2);

  useEffect(() => {
    if (!mapRef.current || !mapLoaded) return;
    const map = mapRef.current;
    const updateZoom = () => setZoom(map.getZoom());
    map.on("zoom", updateZoom);
    return () => {
      map.off("zoom", updateZoom);
    };
  }, [mapLoaded]);

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
        "latest-risk-heat",
        "top-rain-risk",
        "top-rain-risk-heat",
        "risk-summary",
        "risk-summary-heat",
        "selected-risk",
        "selected-risk-heat",
        "live-risk",
        "live-risk-heat",
        "normal-route",
        "safe-route",
      ].forEach(addGeoJSONSource);

      // Improve label language handling to force English labels or hide Arabic labels
      try {
        const styleLayers = map.getStyle().layers;
        styleLayers.forEach((layer) => {
          if (layer.type === "symbol") {
            const textField = map.getLayoutProperty(layer.id, "text-field");
            if (textField) {
              map.setLayoutProperty(layer.id, "text-field", [
                "coalesce",
                ["get", "name:en"],
                ["get", "name_en"],
                "",
              ]);
            }
          }
        });
      } catch (err) {
        console.warn("Could not modify map text labels to English/empty:", err);
      }

      map.addLayer({
        id: "boundary-layer",
        type: "line",
        source: "boundary",
        paint: {
          "line-color": "#4ca6bd",
          "line-width": 2,
          "line-opacity": Math.min(0.65, gridLineOpacity * 2.6),
          "line-dasharray": [2.4, 2],
        },
      }, firstSymbolLayer);
      map.addLayer({
        id: "grid-layer",
        type: "line",
        source: "grid",
        paint: { "line-color": "#8ab9c8", "line-width": 0.45, "line-opacity": gridLineOpacity * 0.55 },
      }, firstSymbolLayer);

      const riskFillColor = [
        "interpolate",
        ["linear"],
        ["coalesce", ["get", "live_predicted_score"], ["get", "predicted_score"], ["get", "y_pred"], 0],
        0, "rgba(20, 184, 166, 0.02)",
        0.35, "rgba(20, 184, 166, 0.05)",
        0.55, "rgba(245, 221, 86, 0.06)",
        0.75, "rgba(255, 145, 77, 0.08)",
        1, "rgba(226, 80, 73, 0.1)",
      ] as maplibregl.ExpressionSpecification;
      const weatherHeatColor = [
        "interpolate",
        ["linear"],
        ["heatmap-density"],
        0, "rgba(109, 213, 250, 0)",
        0.14, "rgba(103, 210, 245, 0.34)",
        0.32, "rgba(57, 196, 177, 0.42)",
        0.54, "rgba(173, 218, 103, 0.5)",
        0.72, "rgba(255, 219, 88, 0.58)",
        0.88, "rgba(255, 147, 79, 0.6)",
        1, "rgba(226, 82, 73, 0.65)",
      ] as maplibregl.ExpressionSpecification;
      const weatherHeatWeight = [
        "interpolate",
        ["linear"],
        ["get", "weather_intensity"],
        0, 0.12,
        0.25, 0.32,
        0.5, 0.68,
        0.75, 1.15,
        1, 1.55,
      ] as maplibregl.ExpressionSpecification;
      [
        ["risk-summary-heat-layer", "risk-summary-heat"],
        ["latest-risk-heat-layer", "latest-risk-heat"],
        ["top-rain-risk-heat-layer", "top-rain-risk-heat"],
        ["selected-risk-heat-layer", "selected-risk-heat"],
        ["live-risk-heat-layer", "live-risk-heat"],
      ].forEach(([id, source]) => {
        map.addLayer({
          id: id as string,
          type: "heatmap",
          source: source as string,
          maxzoom: 15.5,
          paint: {
            "heatmap-weight": weatherHeatWeight,
            "heatmap-intensity": ["interpolate", ["linear"], ["zoom"], 10, 0.65, 13, 1.15, 15, 1.55],
            "heatmap-radius": ["interpolate", ["linear"], ["zoom"], 10, 22, 12, 34, 14, 54, 15.5, 74],
            "heatmap-opacity": ["interpolate", ["linear"], ["zoom"], 10, 0.62, 14, 0.5, 16, 0.34],
            "heatmap-color": weatherHeatColor,
          },
        }, firstSymbolLayer);
      });
      [
        ["risk-summary-layer", "risk-summary"],
        ["latest-risk-layer", "latest-risk"],
        ["top-rain-risk-layer", "top-rain-risk"],
        ["selected-risk-layer", "selected-risk"],
      ].forEach(([id, source]) => {
        map.addLayer({
          id: id as string,
          type: "fill",
          source: source as string,
          paint: {
            "fill-color": riskFillColor,
            "fill-opacity": 0.015,
            "fill-outline-color": "rgba(255,255,255,0)",
            "fill-opacity-transition": { duration: 220, delay: 0 },
          },
        }, firstSymbolLayer);
      });

      const liveRiskFillColor = [
        "interpolate",
        ["linear"],
        ["coalesce", ["get", "live_predicted_score"], 0],
        0, "rgba(103, 210, 245, 0.02)",
        0.45, "rgba(57, 196, 177, 0.04)",
        0.7, "rgba(255, 219, 88, 0.06)",
        1, "rgba(226, 82, 73, 0.1)",
      ] as maplibregl.ExpressionSpecification;

      map.addLayer({
        id: "live-risk-layer",
        type: "fill",
        source: "live-risk",
        paint: {
          "fill-color": liveRiskFillColor,
          "fill-opacity": 0.015,
          "fill-outline-color": "rgba(255,255,255,0)",
          "fill-opacity-transition": { duration: 220, delay: 0 },
        },
      }, firstSymbolLayer);

      map.addLayer({
        id: "live-risk-contour-layer",
        type: "line",
        source: "live-risk",
        paint: {
          "line-color": [
            "match",
            ["coalesce", ["get", "live_risk_class"], "low"],
            "high", "#e25049",
            "medium", "#f3b43f",
            "low", "#46c5d8",
            "#46c5d8",
          ],
          "line-width": [
            "interpolate",
            ["linear"],
            ["coalesce", ["get", "live_predicted_score"], 0],
            0.35, 0,
            0.55, 0.55,
            0.75, 1.1,
            1, 1.8,
          ],
          "line-opacity": 0.22,
          "line-blur": 2.5,
        },
      }, firstSymbolLayer);

      // Glow layer for high risk (thick blurred line)
      map.addLayer({
        id: "live-risk-glow-layer",
        type: "line",
        source: "live-risk",
        paint: {
          "line-color": "#e25049",
          "line-width": 9,
          "line-opacity": 0.18,
          "line-blur": 7,
        },
        filter: ["==", ["coalesce", ["get", "live_risk_class"], "low"], "high"]
      }, firstSymbolLayer);

      // Selected zone highlight layer
      map.addLayer({
        id: "selected-zone-highlight",
        type: "line",
        source: "grid",
        paint: {
          "line-color": "#006688",
          "line-width": 2.4,
          "line-opacity": 0.9,
          "line-blur": 0.4,
        },
        filter: ["==", ["get", "zone_code"], ""]
      }, firstSymbolLayer);

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
        "live-risk-layer",
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
            const dest = comparison?.selected_destination_facility_name || "Selected map point";
            const cleanDest = containsArabic(dest) ? "Selected Destination" : dest;
            const quality = comparison?.safe_route_available
              ? getRouteQualityLabel(comparison?.safe_route_quality)
              : "No Distinct Safer Alternative";
            html = `
              <div class="map-popup-card">
                <h4>Route Details</h4>
                <p><strong>Route Type:</strong> ${escapeHtml(getRouteTypeLabel(properties.route_type))}</p>
                <p><strong>Risk Reduction:</strong> ${formatPercent(comparison?.risk_reduction_percent, 1)}</p>
                <p><strong>ETA Tradeoff:</strong> ${formatPercent(comparison?.eta_tradeoff_percent, 1)}</p>
                <p><strong>Destination:</strong> ${escapeHtml(cleanDest)}</p>
                <p><strong>Route Quality:</strong> ${escapeHtml(quality)}</p>
              </div>`;
          } else if (properties.live_risk_class !== undefined) {
            const rain = properties.rain_24h_mm == null
              ? EMPTY_VALUE
              : `${formatNumber(properties.rain_24h_mm, 1)} mm`;
            const prob = properties.max_precipitation_probability == null
              ? EMPTY_VALUE
              : `${formatPercent(properties.max_precipitation_probability, 0)}`;
            html = `
              <div class="map-popup-card">
                <h4>${escapeHtml(getZoneLabel(properties.zone_code))}</h4>
                <p><strong>Live Risk Level:</strong> <span class="risk-${escapeHtml(properties.live_risk_class || "medium")}">${escapeHtml(getRiskLevelLabel(properties.live_risk_class))}</span></p>
                <p><strong>Live Predicted Risk:</strong> ${formatNumber(properties.live_predicted_score, 4)}</p>
                <p><strong>24h Rainfall:</strong> ${rain}</p>
                <p><strong>Rain Probability:</strong> ${prob}</p>
              </div>`;
          } else {
            const rain = properties.rain_24h_mm == null
              ? EMPTY_VALUE
              : `${formatNumber(properties.rain_24h_mm, 1)} mm`;
            html = `
              <div class="map-popup-card">
                <h4>${escapeHtml(getZoneLabel(properties.zone_code))}</h4>
                <p><strong>${escapeHtml(getFieldLabel("predicted_risk_class"))}:</strong> <span class="risk-${escapeHtml(properties.predicted_risk_class || "medium")}">${escapeHtml(getRiskLevelLabel(properties.predicted_risk_class))}</span></p>
                <p><strong>${escapeHtml(getFieldLabel("y_pred"))}:</strong> ${formatNumber(properties.y_pred, 4)}</p>
                ${properties.event_id ? `<p><strong>${escapeHtml(getFieldLabel("event_id"))}:</strong> ${escapeHtml(getEventLabel(properties.event_id))}</p>` : ""}
                <p><strong>${escapeHtml(getFieldLabel("rain_24h_mm"))}:</strong> ${rain}</p>
                <p><strong>${escapeHtml(getFieldLabel("population_sum"))}:</strong> ${formatInteger(properties.population_sum)}</p>
                <p><strong>${escapeHtml(getFieldLabel("built_surface_mean"))}:</strong> ${formatNumber(properties.built_surface_mean, 2)}</p>
              </div>`;
          }
          new maplibregl.Popup({ className: "light-map-popup", closeButton: true, maxWidth: "280px" })
            .setLngLat(event.lngLat)
            .setHTML(html)
            .addTo(map);
          if (isRouteFeature) return;
        }
        
        let zoneClicked = false;
        let clickedZoneCode: string | null = null;
        let clickedEventId: string | null = null;
        
        if (feature) {
          const properties = feature.properties ?? {};
          const isRouteFeature = routeLayers.includes(feature.layer.id);
          if (!isRouteFeature && properties.zone_code) {
            zoneClicked = true;
            clickedZoneCode = properties.zone_code;
            clickedEventId = properties.event_id || null;
          }
        }
        
        const routingActive = routeOrigin || isRoutePlanningActive;
        if (zoneClicked && clickedZoneCode && !routingActive) {
          if (onZoneClick) {
            onZoneClick(clickedZoneCode, clickedEventId);
          }
          return;
        }
        
        if (!routingLoadingRef.current) {
          onMapPointClickRef.current({ lat: event.lngLat.lat, lon: event.lngLat.lng });
        }
      });
    });

    return () => {
      if (routePulseTimer) clearInterval(routePulseTimer);
      placeMarkersRef.current.forEach((marker) => {
        marker.getPopup()?.remove();
        marker.remove();
      });
      placeMarkerRootsRef.current.forEach((root) => root.unmount());
      placeMarkerRootsRef.current = [];
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
    const updateHeatSource = (id: string, data: FeatureCollection | null) => {
      const source = map.getSource(id) as maplibregl.GeoJSONSource | undefined;
      source?.setData(toRiskCentroidCollection(data) as MapSourceData);
    };
    updateSource("boundary", boundaryData);
    updateSource("grid", gridData);
    updateSource("latest-risk", latestRiskData);
    updateHeatSource("latest-risk-heat", latestRiskData);
    updateSource("top-rain-risk", topRainRiskData);
    updateHeatSource("top-rain-risk-heat", topRainRiskData);
    updateSource("risk-summary", riskSummaryData);
    updateHeatSource("risk-summary-heat", riskSummaryData);
    updateSource("selected-risk", selectedEventRiskData);
    updateHeatSource("selected-risk-heat", selectedEventRiskData);
    updateSource("live-risk", liveRiskData);
    updateHeatSource("live-risk-heat", liveRiskData);
    updateSource("normal-route", normalRouteData);
    updateSource("safe-route", safeRouteData);
  }, [
    boundaryData,
    gridData,
    latestRiskData,
    liveRiskData,
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
    placeMarkersRef.current.forEach((marker) => {
      marker.getPopup()?.remove();
      marker.remove();
    });
    placeMarkerRootsRef.current.forEach((root) => root.unmount());
    placeMarkerRootsRef.current = [];
    placeMarkersRef.current = [];
    for (const feature of placesData?.features ?? []) {
      const properties = feature.properties;
      if (!categoryVisible(properties.category, properties.place_id, layers, emergencyPlaceIds)) {
        continue;
      }
      const coordinates = pointCoordinates(feature.geometry.coordinates);
      if (!coordinates) continue;

      const isImportant = properties.category === "hospital" || properties.category === "emergency" || emergencyPlaceIds.has(properties.place_id);
      if (zoom < 13.0 && !isImportant) {
        continue;
      }

      const element = document.createElement("button");
      element.type = "button";
      element.className = "place-marker";
      const category = markerCategory(properties.category);
      element.dataset.category = category;
      element.setAttribute("aria-label", `${safePlaceName(properties)}, ${properties.category_label}`);
      const Icon = placeIconMap[category as keyof typeof placeIconMap] ?? placeIconMap.default;
      const markerRoot = createRoot(element);
      markerRoot.render(<Icon aria-hidden="true" strokeWidth={2.2} />);
      placeMarkerRootsRef.current.push(markerRoot);
      element.addEventListener("click", (event) => {
        event.stopPropagation();
        if (!routingLoadingRef.current) {
          onMapPointClickRef.current({ lat: coordinates[1], lon: coordinates[0] });
        }
      });

      const popup = new maplibregl.Popup({ offset: 20, maxWidth: "260px" }).setHTML(`
        <div class="map-popup-card">
          <h4>${escapeHtml(safePlaceName(properties))}</h4>
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
      placeMarkersRef.current.forEach((marker) => {
        marker.getPopup()?.remove();
        marker.remove();
      });
      placeMarkerRootsRef.current.forEach((root) => root.unmount());
      placeMarkerRootsRef.current = [];
      placeMarkersRef.current = [];
    };
  }, [emergencyPlaceIds, layers, mapLoaded, placesData, zoom]);

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

  // Handle search point flyTo and marker
  useEffect(() => {
    if (!mapRef.current || !mapLoaded) return;
    const map = mapRef.current;
    
    // Clear previous search marker
    if (searchMarkerRef.current) {
      searchMarkerRef.current.remove();
      searchMarkerRef.current = null;
    }
    
    if (!searchSelectedPoint) return;
    
    // Create new search marker (blue/purple pin)
    const element = document.createElement("div");
    element.className = "search-result-marker";
    element.style.cursor = "pointer";
    element.innerHTML = `
      <div style="background-color: white; border-radius: 9999px; padding: 4px; box-shadow: 0 4px 10px rgba(0,0,0,0.15); border: 2px solid #4f46e5;">
        <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#4f46e5" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="display: block;">
          <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
          <circle cx="12" cy="10" r="3" />
        </svg>
      </div>
    `;
    
    const marker = new maplibregl.Marker({ element, anchor: "bottom" })
      .setLngLat([searchSelectedPoint.lon, searchSelectedPoint.lat])
      .addTo(map);
      
    searchMarkerRef.current = marker;
    
    // Determine zoom level depending on category
    const zoomLevel = searchSelectedPoint.category === "road" || searchSelectedPoint.category === "zone" ? 14.0 : 15.5;
    
    // Fly to location
    map.flyTo({
      center: [searchSelectedPoint.lon, searchSelectedPoint.lat],
      zoom: zoomLevel,
      speed: 1.2,
      essential: true
    });
    
    // Add popup with options
    const popupHTML = `
      <div style="padding: 10px; font-family: sans-serif; min-width: 180px;">
        <h4 style="font-size: 12px; font-weight: bold; margin: 0; color: #1e293b;">${escapeHtml(searchSelectedPoint.display_name)}</h4>
        <p style="font-size: 10px; color: #64748b; margin: 2px 0 0 0;">${escapeHtml(searchSelectedPoint.category_label)}</p>
        ${!searchSelectedPoint.inside_project_area ? `
          <div style="margin-top: 8px; font-size: 9px; font-weight: 600; color: #b45309; background-color: #fffbeb; border: 1px solid #fef3c7; border-radius: 4px; padding: 4px; line-height: 1.3;">
            This location is outside the current Nasr City study area.
          </div>
        ` : ""}
        <div style="margin-top: 10px; display: flex; gap: 8px;">
          <button id="btn-set-start" style="padding: 4px 8px; border: none; border-radius: 4px; background-color: #2C5EAD; color: white; font-size: 10px; font-weight: bold; cursor: pointer; transition: background-color 0.2s;">Set Start</button>
          <button id="btn-set-dest" style="padding: 4px 8px; border: none; border-radius: 4px; background-color: #10b981; color: white; font-size: 10px; font-weight: bold; cursor: pointer; transition: background-color 0.2s;">Set Dest</button>
        </div>
      </div>
    `;
    
    const popup = new maplibregl.Popup({ offset: [0, -25], closeButton: true })
      .setLngLat([searchSelectedPoint.lon, searchSelectedPoint.lat])
      .setHTML(popupHTML)
      .addTo(map);
      
    // Set popup listener
    setTimeout(() => {
      const btnStart = document.getElementById("btn-set-start");
      const btnDest = document.getElementById("btn-set-dest");
      
      if (btnStart) {
        btnStart.addEventListener("click", () => {
          onSetStartPoint({ lat: searchSelectedPoint.lat, lon: searchSelectedPoint.lon });
          popup.remove();
        });
      }
      if (btnDest) {
        btnDest.addEventListener("click", () => {
          onSetDestinationPoint({ lat: searchSelectedPoint.lat, lon: searchSelectedPoint.lon });
          popup.remove();
        });
      }
    }, 50);
    
    return () => {
      popup.remove();
      if (searchMarkerRef.current) {
        searchMarkerRef.current.remove();
        searchMarkerRef.current = null;
      }
    };
  }, [mapLoaded, searchSelectedPoint, onSetStartPoint, onSetDestinationPoint]);

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
    setLayerVisibility("live-risk-layer", layers.liveRisk);
    setLayerVisibility("latest-risk-heat-layer", layers.latestRisk);
    setLayerVisibility("top-rain-risk-heat-layer", layers.topRainRisk);
    setLayerVisibility("risk-summary-heat-layer", layers.riskSummary);
    setLayerVisibility("selected-risk-heat-layer", layers.selectedRisk);
    setLayerVisibility("live-risk-heat-layer", layers.liveRisk);
    setLayerVisibility("live-risk-contour-layer", layers.liveRisk);
    setLayerVisibility("live-risk-glow-layer", layers.liveRisk);
    map.getStyle().layers
      .filter((layer) => /^(road_|bridge_|tunnel_|highway-|label_)/.test(layer.id))
      .forEach((layer) => setLayerVisibility(layer.id, layers.roadsLabels));
  }, [layers, mapLoaded]);

  useEffect(() => {
    if (!mapRef.current || !mapLoaded) return;
    const map = mapRef.current;
    
    // Check recommendation
    const recommendation = (routeComparison as any)?.recommendation;
    
    // Default fallback values (e.g. before calculation or for historical)
    let normalColor = "#8186D5";
    let normalWidth = 3.5;
    let normalDash: [number, number] | null = [2, 2];
    let normalOpacity = 0.72;
    
    let safeColor = "#1591DC";
    let safeWidth = 5;
    let safeDash: [number, number] | null = null;
    let safeOpacity = 0.96;
    let haloOpacity = 0.2;
    let haloColor = "#4BB8FA";
    
    let showSafeRoute = routeVisibility === "safe" || routeVisibility === "both";
    let showNormalRoute = routeVisibility === "normal" || routeVisibility === "both";

    if (recommendation === "normal_route_acceptable") {
      // Normal route is safe and blue
      normalColor = "#1591DC";
      normalWidth = 5;
      normalDash = null; // solid
      normalOpacity = 0.96;
      
      // Safe route can be hidden by default or shown as optional
      if (routeVisibility === "both") {
        showSafeRoute = false;
      }
      safeColor = "#8186D5";
      safeWidth = 3.5;
      safeDash = [2, 2];
      safeOpacity = 0.5;
      haloOpacity = 0;
    } else if (recommendation === "weather_safe_route_recommended") {
      // Normal route is risky and red
      normalColor = "#E63946";
      normalWidth = 3.5;
      normalDash = [2, 2];
      normalOpacity = 0.8;
      
      // Safe route is strong solid blue
      safeColor = "#1591DC";
      safeWidth = 5.5;
      safeDash = null;
      safeOpacity = 0.96;
      haloOpacity = 0.22;
      haloColor = "#4BB8FA";
    } else if (recommendation === "no_distinct_safer_alternative") {
      // Both routes are neutral blue/purple
      normalColor = "#8186D5";
      normalWidth = 5;
      normalDash = null; // solid
      normalOpacity = 0.9;
      
      safeColor = "#8186D5";
      safeWidth = 3.5;
      safeDash = [2, 2]; // dashed/secondary
      safeOpacity = 0.6;
      haloOpacity = 0;
    }

    try {
      if (map.getLayer("normal-route-layer")) {
        map.setPaintProperty("normal-route-layer", "line-color", normalColor);
        map.setPaintProperty("normal-route-layer", "line-width", normalWidth);
        map.setPaintProperty("normal-route-layer", "line-opacity", normalOpacity);
        if (normalDash) {
          map.setPaintProperty("normal-route-layer", "line-dasharray", normalDash);
        } else {
          map.setPaintProperty("normal-route-layer", "line-dasharray", [1, 0]);
        }
        map.setLayoutProperty("normal-route-layer", "visibility", showNormalRoute ? "visible" : "none");
      }
      
      if (map.getLayer("safe-route-layer")) {
        map.setPaintProperty("safe-route-layer", "line-color", safeColor);
        map.setPaintProperty("safe-route-layer", "line-width", safeWidth);
        map.setPaintProperty("safe-route-layer", "line-opacity", safeOpacity);
        if (safeDash) {
          map.setPaintProperty("safe-route-layer", "line-dasharray", safeDash);
        } else {
          map.setPaintProperty("safe-route-layer", "line-dasharray", [1, 0]);
        }
        map.setLayoutProperty("safe-route-layer", "visibility", showSafeRoute ? "visible" : "none");
      }
      
      if (map.getLayer("safe-route-halo-layer")) {
        map.setPaintProperty("safe-route-halo-layer", "line-color", haloColor);
        map.setPaintProperty("safe-route-halo-layer", "line-opacity", haloOpacity);
        map.setLayoutProperty("safe-route-halo-layer", "visibility", showSafeRoute ? "visible" : "none");
      }
    } catch (err) {
      console.warn("Failed to update route layers styling:", err);
    }
  }, [mapLoaded, routeComparison, routeVisibility]);


  useEffect(() => {
    if (!mapRef.current || !mapLoaded) return;
    const map = mapRef.current;
    try {
      if (map.getLayer("grid-layer")) {
        map.setPaintProperty("grid-layer", "line-opacity", gridLineOpacity);
      }
      if (map.getLayer("boundary-layer")) {
        map.setPaintProperty("boundary-layer", "line-opacity", Math.min(1.0, gridLineOpacity * 3));
      }
    } catch (err) {
      console.warn("Failed to update line opacity:", err);
    }
  }, [gridLineOpacity, mapLoaded]);

  useEffect(() => {
    if (!mapRef.current || !mapLoaded) return;
    const map = mapRef.current;
    try {
      const riskLayers = [
        "risk-summary-layer",
        "latest-risk-layer",
        "top-rain-risk-layer",
        "selected-risk-layer",
      ];
      riskLayers.forEach((layerId) => {
        if (map.getLayer(layerId)) {
          map.setPaintProperty(layerId, "fill-opacity", Math.min(0.04, riskFillOpacity * 0.12));
        }
      });

      if (map.getLayer("live-risk-layer")) {
        map.setPaintProperty("live-risk-layer", "fill-opacity", [
          "match",
          ["coalesce", ["get", "live_risk_class"], "low"],
          "high", Math.min(0.05, riskFillOpacity * 0.14),
          "medium", Math.min(0.04, riskFillOpacity * 0.1),
          "low", riskDisplayMode === "focus" ? 0.005 : Math.min(0.025, riskFillOpacity * 0.07),
          0
        ]);
      }

      [
        "risk-summary-heat-layer",
        "latest-risk-heat-layer",
        "top-rain-risk-heat-layer",
        "selected-risk-heat-layer",
        "live-risk-heat-layer",
      ].forEach((layerId) => {
        if (map.getLayer(layerId)) {
          map.setPaintProperty(layerId, "heatmap-opacity", riskDisplayMode === "focus" ? 0.56 : 0.68);
        }
      });

      if (map.getLayer("live-risk-glow-layer")) {
        map.setPaintProperty("live-risk-glow-layer", "line-opacity", riskFillOpacity * 0.52);
      }
    } catch (err) {
      console.warn("Failed to update fill opacity:", err);
    }
  }, [riskFillOpacity, riskDisplayMode, mapLoaded]);

  useEffect(() => {
    if (!mapRef.current || !mapLoaded) return;
    const map = mapRef.current;
    try {
      if (map.getLayer("selected-zone-highlight")) {
        map.setFilter("selected-zone-highlight", [
          "==",
          ["get", "zone_code"],
          selectedZoneCode || "",
        ]);
      }
    } catch (err) {
      console.warn("Failed to update selected zone filter:", err);
    }
  }, [selectedZoneCode, mapLoaded]);

  const routeHint = routingLoading
    ? "Calculating weather-aware route..."
    : routingError
      ? "Choose different points or reset the route"
      : routeDestination
        ? "Route ready • click the map again to clear"
        : routeOrigin
          ? "Now choose your destination"
          : "Click the map to choose your starting point";

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
      <div className="absolute left-4 top-4 z-10 flex max-w-[calc(100%-5rem)] items-center gap-2 rounded-full border border-[#C6CBEF]/45 bg-gradient-to-r from-white/95 to-[#C4E2F5]/90 px-3 py-2 text-[10px] font-semibold text-[#2C5EAD] shadow-md backdrop-blur">
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

    </div>
  );
};
