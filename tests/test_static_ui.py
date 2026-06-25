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
    assert "/static/how-it-works.html" in html
    assert "/static/industrial-situations.html" in html


def test_how_it_works_page_serves_ladder_scenarios() -> None:
    app = create_app(start_background=False)
    with TestClient(app) as client:
        response = client.get("/how-it-works")
        static_response = client.get("/static/how-it-works.html")

    assert response.status_code == 200
    html = response.text
    assert "How This PLC Trainer Works" in html
    assert "Scenario 1: Auto Cycle" in html
    assert "Scenario 4: Emergency All-Red" in html
    assert "Full Ladder View" in html
    assert "ladder-diagram" in html
    assert "/static/industrial-situations.html" in html
    assert static_response.status_code == 200
    assert "How This PLC Trainer Works" in static_response.text


def test_industrial_situations_page_serves_realistic_training_scenarios() -> None:
    app = create_app(start_background=False)
    with TestClient(app) as client:
        response = client.get("/industrial-situations")
        static_response = client.get("/static/industrial-situations.html")

    assert response.status_code == 200
    html = response.text
    assert "Industrial Situations" in html
    assert "Omron" in html
    assert "Siemens" in html
    assert "Analog Modules" in html
    assert "VFD / PWM Motor Control" in html
    assert "NPN / PNP Sensor Troubleshooting" in html
    assert "Robust System Design" in html
    assert "troubleshooting" in html.lower()
    assert static_response.status_code == 200
    assert "Industrial Situations" in static_response.text


def test_static_assets_are_served() -> None:
    app = create_app(start_background=False)
    with TestClient(app) as client:
        app_js = client.get("/static/app.js")
        styles = client.get("/static/styles.css")
        guide_styles = client.get("/static/guide.css")

    assert app_js.status_code == 200
    assert "renderTimerRows" in app_js.text
    assert styles.status_code == 200
    assert "field-controls" in styles.text
    assert guide_styles.status_code == 200
    assert "ladder-diagram" in guide_styles.text
    assert "industrial-nav" in guide_styles.text
