import re

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)
RAW_OSM_ID = re.compile(r"^(?:osm[:_ -]?)?(?:node|way|relation)?[:_ -]?\d+$", re.I)


def test_places_returns_frontend_ready_feature_collection():
    response = client.get("/api/weather-impact/places")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert data["features"]
    for feature in data["features"]:
        properties = feature["properties"]
        assert properties["display_name"]
        assert properties["category_label"]
        assert not RAW_OSM_ID.match(properties["display_name"])


def test_places_support_category_and_limit_filters():
    response = client.get("/api/weather-impact/places?category=hospital&limit=2")
    assert response.status_code == 200
    features = response.json()["features"]
    assert len(features) <= 2
    assert all(feature["properties"]["category"] == "hospital" for feature in features)


def test_places_summary_reports_sources_and_counts():
    response = client.get("/api/weather-impact/places/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in {"ok", "ok_with_warnings"}
    assert data["total_places"] > 0
    assert data["source"] == "OpenStreetMap / existing processed data"
    assert set(data["categories"]) >= {
        "hospital",
        "clinic",
        "mosque",
        "mall",
        "school",
        "university",
        "police",
        "fire_station",
        "emergency",
        "landmark",
    }


def test_invalid_place_category_is_rejected():
    response = client.get("/api/weather-impact/places?category=not-a-category")
    assert response.status_code == 400
