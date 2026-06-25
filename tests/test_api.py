from fastapi.testclient import TestClient

from main import create_app


def test_state_endpoint_returns_plc_snapshot() -> None:
    app = create_app(start_background=False)
    with TestClient(app) as client:
        response = client.get("/api/state")

    assert response.status_code == 200
    payload = response.json()
    assert payload["phase"] == "STOPPED"
    assert payload["outputs"]["NS_RED"] is True
    assert payload["plc"]["model"] == "AutomationDirect CLICK C0-00DR-D training model"


def test_state_endpoint_returns_timer_and_register_rows() -> None:
    app = create_app(start_background=False)
    with TestClient(app) as client:
        response = client.get("/api/state")

    payload = response.json()
    assert response.status_code == 200
    assert payload["timer_rows"][0]["address"] == "T0"
    assert payload["timer_rows"][0]["type"] == "TON"
    assert payload["register_rows"][0]["address"] == "R0"
    assert payload["register_rows"][0]["name"] == "PHASE_STEP"
    assert payload["register_rows"][0]["value_dec"] == 0


def test_state_endpoint_returns_alarm_summary() -> None:
    app = create_app(start_background=False)
    with TestClient(app) as client:
        response = client.get("/api/state")

    payload = response.json()
    assert response.status_code == 200
    assert payload["alarm_summary"] == {
        "alarms": 0,
        "warnings": 0,
        "events": 1,
        "total": 1,
    }


def test_input_endpoint_sets_input_bit() -> None:
    app = create_app(start_background=False)
    with TestClient(app) as client:
        response = client.post("/api/inputs/vehicle_ns", json={"value": True})

    assert response.status_code == 200
    assert response.json()["inputs"]["VEHICLE_NS"] is True


def test_command_endpoint_starts_auto_cycle() -> None:
    app = create_app(start_background=False)
    with TestClient(app) as client:
        response = client.post("/api/commands/start")

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "stopped" or payload["mode"] == "auto"
    assert payload["phase"] == "NS_GREEN"


def test_unknown_input_returns_404() -> None:
    app = create_app(start_background=False)
    with TestClient(app) as client:
        response = client.post("/api/inputs/bad_input", json={"value": True})

    assert response.status_code == 404
