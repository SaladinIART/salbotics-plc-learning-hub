from fastapi.testclient import TestClient
from pathlib import Path

from main import create_app


def test_root_serves_industrial_trainer_ui() -> None:
    app = create_app(start_background=False)
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    html = response.text
    assert "SALBOTICS PLC HUB" in html
    assert "PORTABLE PLC LEARNING PLATFORM" in html
    assert "Salbotics Solutions" in html
    assert "timer-table" in html
    assert "alarm-summary" in html
    assert "data-field-lamp" in html
    assert "/static/how-it-works.html" in html
    assert "/static/industrial-situations.html" in html
    assert "/static/oil-palm-industrial-environment.html" in html
    assert "/static/plc-programming-methods.html" in html
    assert "/static/risk-assessment-certification.html" in html


def test_how_it_works_page_serves_ladder_scenarios() -> None:
    app = create_app(start_background=False)
    with TestClient(app) as client:
        response = client.get("/how-it-works")
        static_response = client.get("/static/how-it-works.html")

    assert response.status_code == 200
    html = response.text
    assert "How This PLC Learning Hub Works" in html
    assert "Scenario 1: Auto Cycle" in html
    assert "Scenario 4: Emergency All-Red" in html
    assert "Full Ladder View" in html
    assert "ladder-diagram" in html
    assert "/static/industrial-situations.html" in html
    assert "/static/plc-programming-methods.html" in html
    assert static_response.status_code == 200
    assert "How This PLC Learning Hub Works" in static_response.text


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
    assert "/static/plc-programming-methods.html" in html
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
    assert "/static/plc-programming-methods.html" in plant_html
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
    assert "/static/plc-programming-methods.html" in analysis_html


def test_plc_programming_methods_page_serves_reliable_programming_guide() -> None:
    app = create_app(start_background=False)
    with TestClient(app) as client:
        response = client.get("/plc-programming-methods")
        static_response = client.get("/static/plc-programming-methods.html")

    assert response.status_code == 200
    assert static_response.status_code == 200
    html = response.text
    assert "How To Write A Reliable PLC Program From Scratch" in html
    assert "Flowcharts Before Ladder" in html
    assert "Reliable Ladder Structure" in html
    assert "LAD / LD" in html
    assert "FBD" in html
    assert "Structured Text" in html
    assert "SFC" in html
    assert "IEC 61131" in html
    assert "IEC 61499" in html
    assert "Conveyor Train" in html
    assert "Sterilizer Batch Cycle" in html
    assert "Clarifier Temperature" in html
    assert "scan time" in html.lower()
    assert "<svg" in html
    assert "<pre><code>" in html
    assert "/static/risk-assessment-certification.html" in html


def test_risk_assessment_certification_page_serves_training_path() -> None:
    app = create_app(start_background=False)
    with TestClient(app) as client:
        response = client.get("/risk-assessment-certification")
        static_response = client.get("/static/risk-assessment-certification.html")

    assert response.status_code == 200
    assert static_response.status_code == 200
    html = response.text
    assert "How To Become Qualified For Machinery Risk Assessment" in html
    assert "ISO 12100" in html
    assert "ISO 13849" in html
    assert "IEC 62061" in html
    assert "IEC 61508" in html
    assert "CMSE" in html
    assert "TUV SUD" in html
    assert "TUV Rheinland" in html
    assert "exida" in html
    assert "Cost Planning" in html
    assert "Malaysia" in html
    assert "DOSH" in html


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
    assert "method-nav" in guide_styles.text
    assert "cert-path-grid" in guide_styles.text


def test_frontend_astro_spike_files_are_present() -> None:
    root = Path(__file__).resolve().parents[1]
    package_json = (root / "frontend" / "package.json").read_text()
    layout = (root / "frontend" / "src" / "layouts" / "LearningLayout.astro").read_text()
    guide_page = (root / "frontend" / "src" / "pages" / "how-it-works.astro").read_text()
    island = (root / "frontend" / "src" / "components" / "ScanCycleIsland.astro").read_text()

    assert '"astro": "^7.0.3"' in package_json
    assert "Salbotics PLC Learning Hub" in layout
    assert "Migrated guide page spike" in guide_page
    assert "Interactive Scan-Cycle SVG Island" in island
