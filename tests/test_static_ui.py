from fastapi.testclient import TestClient

from main import create_app


def test_root_serves_industrial_trainer_ui() -> None:
    app = create_app(start_background=False)
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    html = response.text
    assert "PLC TRAINER" in html
    assert "4-WAY TRAFFIC LIGHT CONTROLLER" in html
    assert "timer-table" in html
    assert "alarm-summary" in html
    assert "data-field-lamp" in html


def test_static_assets_are_served() -> None:
    app = create_app(start_background=False)
    with TestClient(app) as client:
        app_js = client.get("/static/app.js")
        styles = client.get("/static/styles.css")

    assert app_js.status_code == 200
    assert "renderTimerRows" in app_js.text
    assert styles.status_code == 200
    assert "field-controls" in styles.text

