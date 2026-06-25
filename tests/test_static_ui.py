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
    assert "/static/oil-palm-industrial-environment.html" in html


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
    assert "/static/oil-palm-industrial-environment.html" in html
    assert static_response.status_code == 200
    assert "Industrial Situations" in static_response.text


def test_oil_palm_pages_serve_process_and_stack_training() -> None:
    app = create_app(start_background=False)
    with TestClient(app) as client:
        plant_route = client.get("/oil-palm-industrial-environment")
        plant_static = client.get("/static/oil-palm-industrial-environment.html")
        analysis_route = client.get("/oil-palm-control-stack-analysis")
        analysis_static = client.get("/static/oil-palm-control-stack-analysis.html")

    assert plant_route.status_code == 200
    assert plant_static.status_code == 200
    assert analysis_route.status_code == 200
    assert analysis_static.status_code == 200

    plant_html = plant_route.text
    assert "Oil Palm Plant" in plant_html
    assert "FFB" in plant_html
    assert "CPO" in plant_html
    assert "POME" in plant_html
    assert "Sterilizer" in plant_html
    assert "WECON" in plant_html
    assert "PAC" in plant_html
    assert "Raspberry Pi" in plant_html
    assert "Arduino Opta" in plant_html
    assert "IIoT" in plant_html
    assert "VFD" in plant_html
    assert "Operating Modes" in plant_html
    assert "Manual" in plant_html
    assert "Semi-Auto" in plant_html
    assert "Auto" in plant_html
    assert "Conveyor And Handling Systems" in plant_html
    assert "Process LAD Examples By Stage" in plant_html
    assert "Mode Selection LAD" in plant_html
    assert "Handling LAD" in plant_html
    assert "Screw Press" in plant_html
    assert "Boiler / Steam / POME Support" in plant_html
    assert "<svg" in plant_html
    assert "/static/oil-palm-control-stack-analysis.html" in plant_html

    analysis_html = analysis_route.text
    assert "Control Stack Analysis" in analysis_html
    assert "OPC UA" in analysis_html
    assert "MQTT" in analysis_html
    assert "Sparkplug" in analysis_html
    assert "ISO" in analysis_html
    assert "IEC" in analysis_html
    assert "hobbyist" in analysis_html.lower()
    assert "small" in analysis_html.lower()
    assert "medium" in analysis_html.lower()
    assert "large" in analysis_html.lower()


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
    assert "process-svg" in guide_styles.text
    assert "process-lad-grid" in guide_styles.text
