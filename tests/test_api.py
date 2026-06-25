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

