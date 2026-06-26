from pathlib import Path

from fastapi.testclient import TestClient

from legacy_ot_bridge import LegacyOTBridge, REGISTER_MAP
from main import create_app


def test_legacy_register_map_is_read_only_and_deterministic(tmp_path: Path) -> None:
    bridge = LegacyOTBridge(tmp_path / "legacy.sqlite3")

    registers = bridge.registers()

    assert registers["read_only"] is True
    assert registers["host"] == "127.0.0.1"
    assert registers["port"] == 15020
    assert len(registers["rows"]) == len(REGISTER_MAP)
    assert registers["rows"][0]["address"] == 40001
    assert registers["rows"][0]["name"] == "PRESS_RUN_FB"
    assert all(row["writable"] is False for row in registers["rows"])


def test_legacy_collector_persists_samples_and_reports_health(tmp_path: Path) -> None:
    db_path = tmp_path / "legacy.sqlite3"
    bridge = LegacyOTBridge(db_path)
    before = bridge.summary()["storage"]["sample_count"]

    bridge.collect_sample()
    reloaded = LegacyOTBridge(db_path)
    summary = reloaded.summary()

    assert summary["storage"]["sample_count"] == before + 1
    assert summary["boundary"]["mode"] == "read-only shadow monitoring"
    assert summary["boundary"]["write_endpoints"] is False
    assert summary["communication"]["health"] in {"HEALTHY", "DEGRADED", "ALARM"}
    assert summary["legacy_station"]["control_authority"] == "Existing PLC remains in control"
    assert summary["communication"]["modbus_library"].startswith("pymodbus ")


def test_legacy_reset_reseeds_demo_data(tmp_path: Path) -> None:
    bridge = LegacyOTBridge(tmp_path / "legacy.sqlite3")
    bridge.collect_sample()

    summary = bridge.reset(seed_count=8)
    events = bridge.events(limit=2)["events"]

    assert summary["storage"]["sample_count"] == 8
    assert events[0]["event_type"] == "reset"
    assert "Demo legacy bridge seeded" in events[0]["message"]


def test_legacy_api_returns_summary_registers_events_and_reset(tmp_path: Path) -> None:
    app = create_app(start_background=False, legacy_db_path=tmp_path / "legacy.sqlite3")
    with TestClient(app) as client:
        summary_response = client.get("/api/legacy/summary")
        registers_response = client.get("/api/legacy/registers")
        events_response = client.get("/api/legacy/events?limit=3")
        reset_response = client.post("/api/legacy/reset")

    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["boundary"]["localhost_only"] is True
    assert summary["boundary"]["real_plc_connection"] is False
    assert summary["boundary"]["license_bypass"] is False
    assert summary["legacy_station"]["name"] == "Obsolete Screw Press Station"
    assert summary["rs232_lesson"]["port"] == "loop://"
    assert summary["rs232_lesson"]["library"].startswith("pyserial ")

    assert registers_response.status_code == 200
    assert registers_response.json()["rows"][2]["name"] == "PRESS_CURRENT_A_X10"

    assert events_response.status_code == 200
    assert len(events_response.json()["events"]) <= 3

    assert reset_response.status_code == 200
    assert reset_response.json()["storage"]["sample_count"] == 90


def test_legacy_api_has_no_write_or_force_endpoint(tmp_path: Path) -> None:
    app = create_app(start_background=False, legacy_db_path=tmp_path / "legacy.sqlite3")
    with TestClient(app) as client:
        write_response = client.post("/api/legacy/write", json={"address": 40001, "value": 1})
        force_response = client.post("/api/legacy/force", json={"name": "PRESS_RUN_FB", "value": True})
        command_response = client.post("/api/legacy/commands/reset_fault")

    assert write_response.status_code == 404
    assert force_response.status_code == 404
    assert command_response.status_code == 404
