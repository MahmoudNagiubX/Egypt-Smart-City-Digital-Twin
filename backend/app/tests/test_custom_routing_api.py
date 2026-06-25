from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)
HONESTY_TEXT = "not official emergency dispatch instructions"


def test_custom_emergency_route_returns_both_route_options():
    response = client.post(
        "/api/weather-impact/routing/custom/emergency-route",
        json={
            "origin": {"lat": 30.066338613244326, "lon": 31.378400758098667},
            "destination": {"lat": 30.06811215, "lon": 31.349160765426888},
            "event_type": "top-rain",
            "route_preference": "both",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in {"ok", "ok_with_warnings"}
    assert data["normal_route"]["type"] == "FeatureCollection"
    assert data["weather_safe_route"]["type"] == "FeatureCollection"
    assert data["comparison"]["safe_route_available"] is True
    assert data["comparison"]["safe_route_quality"] == "weak_but_valid"
    assert data["comparison"]["risk_reduction_percent"] > 0
    assert "risk_reduction_percent" in data["comparison"]
    assert "snap_distance_m" in data["origin"]
    assert HONESTY_TEXT in data["honesty_note"].lower()
    for route_key in ("normal_route", "weather_safe_route"):
        properties = data[route_key]["features"][0]["properties"]
        assert {
            "route_type",
            "distance_m",
            "weather_eta_sec",
            "mean_risk_score",
            "high_risk_segment_count",
        } <= set(properties)
        assert HONESTY_TEXT in properties["honesty_note"].lower()


def test_custom_route_invalid_event_type_returns_400():
    response = client.post(
        "/api/weather-impact/routing/custom/emergency-route",
        json={
            "origin": {"lat": 30.05, "lon": 31.34},
            "destination": {"lat": 30.07, "lon": 31.35},
            "event_type": "forecast",
        },
    )
    assert response.status_code == 400


def test_custom_route_missing_coordinates_returns_422():
    response = client.post(
        "/api/weather-impact/routing/custom/emergency-route",
        json={"origin": {"lat": 30.05}, "event_type": "latest"},
    )
    assert response.status_code == 422


def test_custom_route_outside_graph_returns_clear_404():
    response = client.post(
        "/api/weather-impact/routing/custom/emergency-route",
        json={
            "origin": {"lat": 31.2, "lon": 29.9},
            "destination": {"lat": 30.07, "lon": 31.35},
            "event_type": "latest",
        },
    )
    assert response.status_code == 404
    assert "outside" in response.json()["detail"].lower()
