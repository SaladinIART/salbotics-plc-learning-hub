from pathlib import Path

from fastapi.testclient import TestClient

from analytics_historian import AnalyticsHistorian
from main import create_app


def test_historian_initializes_and_persists_samples(tmp_path: Path) -> None:
    db_path = tmp_path / "phase3.sqlite3"
    historian = AnalyticsHistorian(db_path)
    before = historian.summary()["storage"]["sample_count"]

    historian.collect_sample()
    reloaded = AnalyticsHistorian(db_path)
    summary = reloaded.summary()

    assert summary["storage"]["engine"] == "SQLite"
    assert summary["storage"]["sample_count"] == before + 1
    assert summary["latest_sample"]["ffb_tph"] > 0
    assert summary["screw_press"]["maintenance_hint"]


def test_historian_reset_reseeds_demo_data(tmp_path: Path) -> None:
    historian = AnalyticsHistorian(tmp_path / "phase3.sqlite3")
    historian.collect_sample()

    summary = historian.reset(seed_count=12)
    events = historian.events(limit=5)["events"]

    assert summary["storage"]["sample_count"] == 12
    assert events[0]["event_type"] == "reset"
    assert "Demo historian seeded" in events[0]["message"]


def test_historian_trends_are_ordered_and_bounded(tmp_path: Path) -> None:
    historian = AnalyticsHistorian(tmp_path / "phase3.sqlite3")

    trend = historian.trends("press_current_a", minutes=8)

    assert trend["metric"] == "press_current_a"
    assert trend["unit"] == "A"
    assert len(trend["points"]) == 8
    timestamps = [point["timestamp"] for point in trend["points"]]
    assert timestamps == sorted(timestamps)


def test_analytics_api_returns_management_summary(tmp_path: Path) -> None:
    app = create_app(start_background=False, analytics_db_path=tmp_path / "phase3.sqlite3")
    with TestClient(app) as client:
        response = client.get("/api/analytics/summary")

    assert response.status_code == 200
    payload = response.json()
    assert payload["storage"]["engine"] == "SQLite"
    assert payload["storage"]["simulated"] is True
    assert payload["shift"]["ffb_processed_t"] > 0
    assert payload["shift"]["downtime_minutes"] >= 0
    assert payload["management_cards"][0]["label"] == "FFB processed"
    assert payload["station_states"][2]["name"] == "Screw Press"
    assert payload["architecture_layers"][0]["layer"] == "OT"
    assert payload["architecture_layers"][3]["layer"] == "ERP"


def test_version_endpoint_identifies_phase_3_capable_build(tmp_path: Path) -> None:
    app = create_app(start_background=False, analytics_db_path=tmp_path / "phase3.sqlite3")
    with TestClient(app) as client:
        response = client.get("/api/version")

    assert response.status_code == 200
    payload = response.json()
    assert payload["product"] == "Salbotics PLC Learning Hub"
    assert payload["phase_3_analytics"] is True
    assert payload["phase_4_legacy_ot"] is True
    assert payload["localhost_only_default"] is True


def test_analytics_api_returns_trends_events_and_reset(tmp_path: Path) -> None:
    app = create_app(start_background=False, analytics_db_path=tmp_path / "phase3.sqlite3")
    with TestClient(app) as client:
        trend_response = client.get("/api/analytics/trends?metric=oer_percent&minutes=6")
        events_response = client.get("/api/analytics/events?limit=3")
        reset_response = client.post("/api/analytics/reset")

    assert trend_response.status_code == 200
    trend_payload = trend_response.json()
    assert trend_payload["metric"] == "oer_percent"
    assert len(trend_payload["points"]) == 6

    assert events_response.status_code == 200
    assert len(events_response.json()["events"]) <= 3

    assert reset_response.status_code == 200
    assert reset_response.json()["storage"]["sample_count"] == 120


def test_analytics_api_rejects_unknown_metric(tmp_path: Path) -> None:
    app = create_app(start_background=False, analytics_db_path=tmp_path / "phase3.sqlite3")
    with TestClient(app) as client:
        response = client.get("/api/analytics/trends?metric=bad_metric")

    assert response.status_code == 404
