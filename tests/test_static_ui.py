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
    assert "/static/phase-2-start-here.html" in html
    assert "/static/phase-3-data-analytics.html" in html
    assert "/static/phase-4-legacy-ot-recovery.html" in html
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
    assert "/static/phase-2-start-here.html" in html
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
    assert "/static/phase-2-start-here.html" in plant_html
    assert "/static/phase-4-legacy-ot-recovery.html" in plant_html
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


def test_phase_2_start_here_page_serves_scada_and_communications_overview() -> None:
    app = create_app(start_background=False)
    with TestClient(app) as client:
        response = client.get("/phase-2-start-here")
        static_response = client.get("/static/phase-2-start-here.html")

    assert response.status_code == 200
    assert static_response.status_code == 200
    html = response.text
    assert "Phase 2 Start Here" in html
    assert "Operator Path" in html
    assert "Technician Path" in html
    assert "Developer Path" in html
    assert "SCADA" in html
    assert "HMI" in html
    assert "Modbus TCP" in html
    assert "OPC UA" in html
    assert "MQTT" in html
    assert "Sparkplug" in html
    assert "RS-232" in html
    assert "RS-485" in html
    assert "localhost" in html
    assert "127.0.0.1" in html
    assert "LAN IP" in html
    assert "oil palm" in html.lower()
    assert "alarms" in html
    assert "trends" in html
    assert "Virtual Modbus TCP" in html
    assert "Python collector" in html
    assert "local historian" in html.lower()
    assert "<svg" in html
    assert "/static/oil-palm-industrial-environment.html" in html
    assert "/static/phase-3-data-analytics.html" in html
    assert "/static/phase-4-legacy-ot-recovery.html" in html


def test_phase_3_data_analytics_page_serves_management_dashboard() -> None:
    app = create_app(start_background=False)
    with TestClient(app) as client:
        response = client.get("/phase-3-data-analytics")
        static_response = client.get("/static/phase-3-data-analytics.html")

    assert response.status_code == 200
    assert static_response.status_code == 200
    html = response.text
    assert "Phase 3: Local Data Collection" in html
    assert "management dashboard" in html.lower()
    assert "SQLite" in html
    assert "historian" in html
    assert "FFB" in html
    assert "CPO" in html
    assert "downtime" in html
    assert "OER" in html
    assert "screw press" in html.lower()
    assert "OT" in html
    assert "IT" in html
    assert "MES" in html
    assert "ERP" in html
    assert "phase3-analytics.js" in html
    assert "phase3-diagram-note-20260626" in html
    assert "<svg" in html
    assert "/static/phase-2-start-here.html" in html
    assert "/static/phase-4-legacy-ot-recovery.html" in html


def test_phase_4_legacy_ot_page_serves_recovery_and_bridge_training() -> None:
    app = create_app(start_background=False)
    with TestClient(app) as client:
        response = client.get("/phase-4-legacy-ot-recovery")
        static_response = client.get("/static/phase-4-legacy-ot-recovery.html")

    assert response.status_code == 200
    assert static_response.status_code == 200
    html = response.text
    assert "Phase 4: Legacy OT Recovery" in html
    assert "read-only" in html.lower()
    assert "obsolete PLC" in html
    assert "Windows XP/7" in html
    assert "missing installer" in html
    assert "missing software" in html
    assert "license" in html
    assert "Virtual Modbus TCP" in html
    assert "RS-232" in html
    assert "pySerial" in html
    assert "Do not write" in html or "does not expose write" in html
    assert "Phase 5 Preview" in html
    assert "phase4-legacy.js" in html
    assert "<svg" in html


def test_static_assets_are_served() -> None:
    app = create_app(start_background=False)
    with TestClient(app) as client:
        app_js = client.get("/static/app.js")
        phase3_js = client.get("/static/phase3-analytics.js")
        phase4_js = client.get("/static/phase4-legacy.js")
        styles = client.get("/static/styles.css")
        guide_styles = client.get("/static/guide.css")

    assert app_js.status_code == 200
    assert "renderTimerRows" in app_js.text
    assert phase3_js.status_code == 200
    assert "refreshDashboard" in phase3_js.text
    assert "renderApiError" in phase3_js.text
    assert "ANALYTICS API UNAVAILABLE" in phase3_js.text
    assert phase4_js.status_code == 200
    assert "refreshLegacy" in phase4_js.text
    assert "api/legacy/registers" in phase4_js.text
    assert styles.status_code == 200
    assert "field-controls" in styles.text
    assert guide_styles.status_code == 200
    assert "ladder-diagram" in guide_styles.text
    assert "industrial-nav" in guide_styles.text
    assert "process-svg" in guide_styles.text
    assert "process-lad-grid" in guide_styles.text
    assert "method-nav" in guide_styles.text
    assert "cert-path-grid" in guide_styles.text
    assert "phase2-roadmap" in guide_styles.text
    assert "analytics-kpi-grid" in guide_styles.text
    assert "legacy-workflow-grid" in guide_styles.text


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


def test_beginner_guide_page_serves_layman_explanations() -> None:
    app = create_app(start_background=False)
    with TestClient(app) as client:
        response = client.get("/beginner-guide")
        static_response = client.get("/static/beginner-guide.html")

    assert response.status_code == 200
    assert static_response.status_code == 200
    html = response.text
    for phrase in ("New to automation? Start here.", "Washing machine", "Lift (elevator)",
                   "Automatic gate", "Escalator", "Scan cycle", "Interlock", "fail-safe",
                   "not certified"):
        assert phrase in html, phrase


def test_every_static_page_links_to_the_beginner_guide() -> None:
    from pathlib import Path

    pages = sorted((Path(__file__).resolve().parent.parent / "static").glob("*.html"))
    assert len(pages) >= 10
    for page in pages:
        if page.name == "beginner-guide.html":
            continue
        assert "/static/beginner-guide.html" in page.read_text(encoding="utf-8"), page.name


def test_pages_site_build_has_relative_links_and_landing_page(tmp_path) -> None:
    import importlib.util
    from pathlib import Path

    script = Path(__file__).resolve().parent.parent / "scripts" / "build_pages_site.py"
    spec = importlib.util.spec_from_file_location("build_pages_site", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    out = module.build(tmp_path / "site")
    assert module.check(out) == []
    assert (out / "index.html").read_text(encoding="utf-8") == \
        (out / "beginner-guide.html").read_text(encoding="utf-8")
    assert (out / ".nojekyll").exists()
    for page in out.glob("*.html"):
        text = page.read_text(encoding="utf-8")
        assert 'href="/static/' not in text and 'src="/static/' not in text
    # The live simulator panel must not be published as a static page.
    assert "simulator-panel" not in (out / "how-it-works.html").read_text(encoding="utf-8")
    try:
        module.build(out)
    except FileExistsError:
        pass
    else:
        raise AssertionError("existing output directory must be refused")


def test_beginner_guide_has_diagrams_and_try_it_boxes() -> None:
    from pathlib import Path

    html = (Path(__file__).resolve().parent.parent / "static" / "beginner-guide.html").read_text(
        encoding="utf-8")
    # Each diagram has a wide (desktop) and a stacked (phone) version.
    assert html.count("<svg") == 4
    assert html.count('role="img"') == 4
    assert html.count("beginner-svg-wide") == 2
    assert html.count("beginner-svg-tall") == 2
    for title_id in ("beginner-loop-title", "beginner-washer-title",
                     "beginner-loop-title-m", "beginner-washer-title-m"):
        assert f'aria-labelledby="{title_id}"' in html
        assert f'<title id="{title_id}">' in html
    # One "try it" question per example: loop, washer, lift, gate, escalator, cooker, barrier.
    assert html.count('<details class="try-it">') == 7
    assert html.count("</details>") == 7
    for term in ("Technical term:",):
        assert html.count(term) >= 7 + 3  # 7 try-it boxes + the 3 loop cards


def test_beginner_guide_covers_everyday_examples_and_short_sentences() -> None:
    import html as html_lib
    import re
    from pathlib import Path

    page = (Path(__file__).resolve().parent.parent / "static" / "beginner-guide.html").read_text(
        encoding="utf-8")
    for section in ("loop", "parts", "washer", "lift", "gate", "escalator", "cooker", "barrier",
                    "words", "trainer"):
        assert f'id="{section}"' in page, section
        assert f'href="#{section}"' in page, section
    main = re.sub(r"<svg.*?</svg>", "", page[page.index("<main"):], flags=re.S)
    long_sentences = []
    for block in re.findall(r"<(?:p|li|summary)[^>]*>(.*?)</(?:p|li|summary)>", main, flags=re.S):
        text = re.sub(r"\s+", " ", html_lib.unescape(re.sub(r"<[^>]+>", "", block))).strip()
        for sentence in re.split(r"(?<=[.?!])\s+", text):
            if len(sentence.split()) > 22:
                long_sentences.append(sentence)
    assert long_sentences == []
    # Plain-language wording check: technical terms are glossed, not left bare.
    for term in ("Hysteresis", "Setpoint", "interlock", "latch"):
        assert term.lower() in page.lower()


def test_every_page_loads_mobile_nav_and_css_collapses_menu() -> None:
    from pathlib import Path

    static = Path(__file__).resolve().parent.parent / "static"
    for page in sorted(static.glob("*.html")):
        assert "/static/mobile-nav.js" in page.read_text(encoding="utf-8"), page.name
    script = (static / "mobile-nav.js").read_text(encoding="utf-8")
    assert "aria-expanded" in script and "js-nav" in script
    css = (static / "styles.css").read_text(encoding="utf-8")
    assert ".js-nav .topbar:not(.menu-open) .top-actions" in css
    # Live simulator status (index.html) must stay visible; only guide strips collapse.
    assert ".topbar:not(.menu-open) .status-strip," not in css


def test_calmer_phone_typography_is_scoped_to_guide_pages_on_phones() -> None:
    from pathlib import Path

    static = Path(__file__).resolve().parent.parent / "static"
    css = (static / "guide.css").read_text(encoding="utf-8")
    block = css[css.index("/* M-3:"):]
    assert "@media (max-width: 760px)" in block.split("{", 1)[0]
    assert "text-transform: none" in block and "font-size: 15px" in block
    # The live simulator page does not load guide.css, so it is unaffected.
    assert "guide.css" not in (static / "index.html").read_text(encoding="utf-8")


def test_long_guide_pages_opt_in_to_collapsible_sections_on_phones() -> None:
    from pathlib import Path

    static = Path(__file__).resolve().parent.parent / "static"
    opted = {"oil-palm-industrial-environment.html", "industrial-situations.html",
             "phase-2-start-here.html", "plc-programming-methods.html"}
    for page in static.glob("*.html"):
        html = page.read_text(encoding="utf-8")
        assert ("data-collapsible-sections" in html) == (page.name in opted), page.name
    script = (static / "mobile-nav.js").read_text(encoding="utf-8")
    assert "main[data-collapsible-sections]" in script and "Jump to section" in script
    css = (static / "guide.css").read_text(encoding="utf-8")
    block = css[css.index("/* M-4:"):]
    assert "@media (max-width: 760px)" in block
    assert "section.section-collapsed > :not(.panel-heading)" in block
