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
    # Same stage menu as the lessons (Home, Basics, Skills, Factory, Data, Safety)
    # plus the guide to this simulator; the control-panel look stays.
    for target in ("start.html", "beginner-guide.html", "plc-programming-methods.html",
                   "oil-palm-industrial-environment.html", "phase-2-start-here.html",
                   "risk-assessment-certification.html", "how-it-works.html"):
        assert f"/static/{target}" in html, target


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
    # Shared menu + learning path (hub-flow.js) link it to the next stages.
    assert "/static/plc-programming-methods.html" in html
    assert 'data-lesson="how-it-works.html"' in html and "/static/hub-flow.js" in html
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
        (out / "start.html").read_text(encoding="utf-8")
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
    # Every long lesson folds its topics; the two live-dashboard pages stay open.
    opted = {"oil-palm-industrial-environment.html", "industrial-situations.html",
             "phase-2-start-here.html", "plc-programming-methods.html", "beginner-guide.html",
             "how-it-works.html", "oil-palm-control-stack-analysis.html",
             "risk-assessment-certification.html"}
    for page in static.glob("*.html"):
        html = page.read_text(encoding="utf-8")
        assert ("data-collapsible-sections" in html) == (page.name in opted), page.name
    script = (static / "mobile-nav.js").read_text(encoding="utf-8")
    assert "main[data-collapsible-sections]" in script and "Jump to section" in script
    css = (static / "guide.css").read_text(encoding="utf-8")
    block = css[css.index("/* M-4:"):]
    assert "@media (max-width: 760px)" in block
    assert "section.section-collapsed > :not(.panel-heading)" in block


def test_swipe_hint_for_sideways_scrolling_boxes_on_phones() -> None:
    from pathlib import Path

    static = Path(__file__).resolve().parent.parent / "static"
    script = (static / "mobile-nav.js").read_text(encoding="utf-8")
    assert "Swipe sideways to see more" in script and "scrollWidth" in script
    css = (static / "styles.css").read_text(encoding="utf-8")
    block = css[css.index("/* M-5:"):]
    assert "@media (max-width: 760px)" in block and ".swipe-hint-done" in block
    for page in static.glob("*.html"):
        assert "mobile-nav.js?v=m5-" in page.read_text(encoding="utf-8"), page.name


def test_start_page_explains_idea_in_plain_words() -> None:
    import html as html_lib
    import re
    from pathlib import Path

    app = create_app(start_background=False)
    with TestClient(app) as client:
        response = client.get("/start")
        static_response = client.get("/static/start.html")
    assert response.status_code == 200
    assert static_response.status_code == 200
    page = response.text
    # Story order: why, big picture, inputs/outputs, 3 steps, who, path.
    for section in ("why", "picture", "action", "io", "steps", "who", "path", "roadmap"):
        assert f'id="{section}"' in page, section
        assert f'href="#{section}"' in page, section
    for phrase in ("Learn how factory machines think.", "senses, brain, muscles",
                   "Inputs: what the PLC senses", "Outputs: what the PLC controls",
                   "Palm-oil mill example", "In our trainer: 8 inputs", "In our trainer: 6 outputs",
                   "Beginners and students", "Technicians and operators",
                   "Employers and recruiters", "not certified", "The hub at a glance",
                   "Traffic light: our trainer", "Car-park barrier: never lower on a car",
                   "Palm-oil mill: emergency pull-cord", "Where the hub is going."):
        assert phrase in page, phrase
    # Modern look lives in its own stylesheet; other pages keep the industrial style.
    assert "/static/start.css" in page and "guide.css" not in page
    static = Path(__file__).resolve().parent.parent / "static"
    css = (static / "start.css").read_text(encoding="utf-8")
    assert "prefers-color-scheme: dark" in css and "@media (max-width: 760px)" in css
    # The inputs -> PLC -> outputs picture (desktop + phone) plus 3 animated scenes.
    assert page.count("<svg") == 5 and page.count('role="img"') == 5
    assert page.count("<title id=") == 5
    assert "beginner-svg-wide" in page and "beginner-svg-tall" in page
    assert page.count('class="sp-anim ') == 3 and page.count('class="sp-play"') == 3
    # Animations respect reduced motion and can be paused.
    scenes = (static / "scenes.css").read_text(encoding="utf-8")
    assert "/static/scenes.css" in page
    assert "prefers-reduced-motion: reduce" in scenes and ".is-paused" in scenes
    assert "/static/start.js" in page
    script = (static / "start.js").read_text(encoding="utf-8")
    assert "prefers-reduced-motion: reduce" in script and "is-paused" in script
    # Roadmap: every phase is shown with a status.
    for phase in ("Phase 1 ", "Phase 2 ", "Phase 3 ", "Phase 4 ", "Phase 5 "):
        assert phase in html_lib.unescape(page), phase
    assert page.count('class="sp-status"') == 6
    # The beginner guide links back to the overview page.
    beginner = (Path(__file__).resolve().parent.parent / "static" /
                "beginner-guide.html").read_text(encoding="utf-8")
    assert "/static/start.html" in beginner
    # Plain language: short sentences only.
    main = re.sub(r"<svg.*?</svg>", "", page[page.index("<main"):], flags=re.S)
    long_sentences = []
    for block in re.findall(r"<(?:p|li|td|h3)[^>]*>(.*?)</(?:p|li|td|h3)>", main, flags=re.S):
        text = re.sub(r"\s+", " ", html_lib.unescape(re.sub(r"<[^>]+>", "", block))).strip()
        for sentence in re.split(r"(?<=[.?!])\s+", text):
            if len(sentence.split()) > 22:
                long_sentences.append(sentence)
    assert long_sentences == []


def test_learning_path_is_one_list_used_everywhere() -> None:
    import re
    from pathlib import Path

    static = Path(__file__).resolve().parent.parent / "static"
    flow = (static / "hub-flow.js").read_text(encoding="utf-8")
    lessons = re.findall(r'file: "([a-z0-9-]+\.html)"', flow)
    assert len(lessons) == 10 and len(set(lessons)) == 10
    start = (static / "start.html").read_text(encoding="utf-8")
    path = start[start.index('<section id="path"'):]
    path = path[:path.index("</section>")]
    # The start page lesson map lists the same lessons in the same order.
    assert re.findall(r'href="/static/([a-z0-9-]+\.html)"', path) == lessons
    for name in lessons:
        page = (static / name).read_text(encoding="utf-8")
        # Every lesson: shared menu, learning-path script, modern layer, 30-second summary.
        assert f'data-lesson="{name}"' in page, name
        assert "/static/hub-flow.js" in page and "/static/hub.css" in page, name
        assert 'class="hub-summary"' in page and "In 30 seconds" in page, name
        # Summary first: it sits right under the page title, before the long intro.
        assert page.index('class="hub-summary"') < page.index("intro-grid") if "intro-grid" in page else True
        for stage in ("basics", "skills", "factory", "data", "safety"):
            assert f'data-stage="{stage}"' in page, (name, stage)
    # "Up next" card, progress bar and the website-preview note are built by the script.
    for hook in ("hub-progress", "hub-next", "Up next", "hub-offline", "data-needs-trainer"):
        assert hook in flow, hook
    css = (static / "hub.css").read_text(encoding="utf-8")
    assert "prefers-reduced-motion: reduce" in css
    # Dashboards show a calm preview on the public website instead of API errors.
    for script in ("phase3-analytics.js", "phase4-legacy.js"):
        assert "onTrainerPage()" in (static / script).read_text(encoding="utf-8"), script


def test_every_topic_has_plain_view_and_details_toggle() -> None:
    import re
    from pathlib import Path

    static = Path(__file__).resolve().parent.parent / "static"
    wrapped = ["how-it-works", "plc-programming-methods", "industrial-situations",
               "oil-palm-industrial-environment", "oil-palm-control-stack-analysis",
               "phase-2-start-here", "risk-assessment-certification"]
    dashboards = ["phase-3-data-analytics", "phase-4-legacy-ot-recovery"]
    for name in wrapped + dashboards:
        page = (static / f"{name}.html").read_text(encoding="utf-8")
        sections = re.findall(r'<section id="([^"]+)"', page)
        assert sections, name
        # Every topic opens with plain words (and an everyday comparison on most).
        assert page.count('class="plain-view"') == len(sections), name
        assert "/static/hub-ui.js" in page, name
        if name in wrapped:
            # Engineer detail is kept, but behind a native, keyboard-friendly toggle.
            assert page.count('<details class="tech-details">') == len(sections), name
            assert page.count("Show technical details") == len(sections), name
        else:
            # Live dashboards stay visible; they just gain the plain explanation.
            assert "tech-details" not in page, name
    # Key pictures stay outside the toggle; wide ones get a phone step list.
    mill = (static / "oil-palm-industrial-environment.html").read_text(encoding="utf-8")
    flow = mill[mill.index('<section id="process-flow"'):]
    assert flow.index("phone-flow") < flow.index("process-svg") < flow.index("tech-details")
    css = (static / "hub.css").read_text(encoding="utf-8")
    for hook in (".plain-view", ".tech-details", ".phone-flow", ".term-tip",
                 "table.stack-on-phone", "table.pairs-on-phone"):
        assert hook in css, hook


def test_tap_to_explain_glossary() -> None:
    import re
    from pathlib import Path

    script = (Path(__file__).resolve().parent.parent / "static" / "hub-ui.js").read_text(
        encoding="utf-8")
    terms = dict(re.findall(r'\["([^"]+)", "([^"]+)"\]', script))
    for word in ("PLC", "VFD", "FFB", "CPO", "SCADA", "HMI", "NPN", "PNP", "interlock"):
        assert word in terms, word
        assert len(terms[word].split()) <= 22, word
    # Only the first use on a page is marked, and the tip is a real button + note.
    assert "pending.splice" in script and 'aria-expanded' in script and 'role", "note"' in script


def test_start_page_helps_people_find_their_way() -> None:
    import importlib.util
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    static = root / "static"
    start = (static / "start.html").read_text(encoding="utf-8")
    # Goal chooser, search box and "welcome back" banner.
    assert "What do you want to do?" in start and start.count('class="sp-goal"') == 8
    for hook in ('id="search"', 'id="hub-search-input"', 'id="continue"',
                 "/static/search-index.js", "/static/hub-home.js"):
        assert hook in start, hook
    # The search index is generated from the lessons and must be up to date.
    script = root / "scripts" / "build_search_index.py"
    spec = importlib.util.spec_from_file_location("build_search_index", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.main(["--check"]) == 0
    # Lesson pages and the start page share one progress record in the browser.
    flow = (static / "hub-flow.js").read_text(encoding="utf-8")
    home = (static / "hub-home.js").read_text(encoding="utf-8")
    assert '"salbotics-hub-progress"' in flow and '"salbotics-hub-progress"' in home
    assert "IntersectionObserver" in flow and '"Search"' in flow and "Start over" in home
    # Storage can fail (private mode); both scripts must keep working.
    assert flow.count("try {") >= 2 and home.count("try {") >= 2


def test_dashboards_show_recorded_samples_on_the_website() -> None:
    import json
    from pathlib import Path

    static = Path(__file__).resolve().parent.parent / "static"
    analytics = json.loads((static / "sample-analytics.json").read_text(encoding="utf-8"))
    legacy = json.loads((static / "sample-legacy.json").read_text(encoding="utf-8"))
    assert "/api/analytics/summary" in analytics and "/api/analytics/events?limit=12" in analytics
    for metric in ("oer_percent", "press_current_a", "tank_level_percent"):
        assert analytics[f"/api/analytics/trends?metric={metric}&minutes=60"]["points"], metric
    for url in ("/api/legacy/summary", "/api/legacy/registers", "/api/legacy/events?limit=10"):
        assert url in legacy, url
    # No machine-specific temporary paths leak into the published files.
    assert "/tmp" not in json.dumps(analytics) + json.dumps(legacy)
    assert "sample-analytics.json" in (static / "phase3-analytics.js").read_text(encoding="utf-8")
    assert "sample-legacy.json" in (static / "phase4-legacy.js").read_text(encoding="utf-8")


def test_every_lesson_follows_the_same_skeleton() -> None:
    import re
    from pathlib import Path

    static = Path(__file__).resolve().parent.parent / "static"
    lessons = ["how-it-works", "plc-programming-methods", "industrial-situations",
               "oil-palm-industrial-environment", "oil-palm-control-stack-analysis",
               "phase-2-start-here", "phase-3-data-analytics", "phase-4-legacy-ot-recovery",
               "risk-assessment-certification"]
    flow = (static / "hub-flow.js").read_text(encoding="utf-8")
    titles = dict(re.findall(r'file: "([a-z0-9-]+)\.html", stage: "[a-z]+", title: "([^"]+)"', flow))
    for name in lessons:
        page = (static / f"{name}.html").read_text(encoding="utf-8")
        # Plain title (same as the learning path) with the old title kept as a technical name.
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", page).group(1)
        assert h1 == titles[name], name
        assert "Technical name:" in page and 'class="hub-lead"' in page, name
        # Long intro and safety note fold into one compact safety line.
        assert page.count('<details class="hub-safety">') == 1 and "Read more" in page, name
        # Title -> In 30 seconds -> safety -> topics -> Check yourself.
        order = [page.index("<h1"), page.index('class="hub-summary"'), page.index("hub-safety"),
                 page.index("<section id="), page.index('class="panel hub-check"')]
        assert order == sorted(order), name
        assert page.count('<details class="hub-q">') == 3, name
    # Every tag on every page stays balanced after the edits.
    for page in static.glob("*.html"):
        text = page.read_text(encoding="utf-8")
        for tag in ("h1", "h2", "span", "div", "section", "details", "summary", "p", "li"):
            assert len(re.findall(rf"<{tag}\b", text)) == text.count(f"</{tag}>"), (page.name, tag)


def test_dark_mode_follows_device_and_has_a_switch() -> None:
    from pathlib import Path

    static = Path(__file__).resolve().parent.parent / "static"
    for css_name in ("hub.css", "start.css"):
        css = (static / css_name).read_text(encoding="utf-8")
        assert "prefers-color-scheme: dark" in css and ':root:not([data-theme="light"])' in css
        assert ':root[data-theme="dark"]' in css, css_name
    prefs = (static / "hub-prefs.js").read_text(encoding="utf-8")
    assert '"salbotics-hub-theme"' in prefs and '"auto", "light", "dark"' in prefs
    # Loaded in <head> without defer so the theme applies before first paint.
    for page in ["start"] + ["beginner-guide", "how-it-works", "industrial-situations",
                             "phase-3-data-analytics", "risk-assessment-certification"]:
        html = (static / f"{page}.html").read_text(encoding="utf-8")
        head = html[:html.index("</head>")]
        assert '<script src="/static/hub-prefs.js' in head and "defer" not in head.split("hub-prefs.js")[1][:30]
        assert "/static/prefs.css" in head, page
    # Diagrams, Ladder rungs and tables stay on light "paper" cards.
    assert 'Light "paper" cards' in (static / "hub.css").read_text(encoding="utf-8")



def test_language_switch_has_complete_malay_and_german_text() -> None:
    import json
    import re
    import subprocess
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    static = root / "static"
    lang = {code: json.loads((static / "lang" / f"{code}.json").read_text(encoding="utf-8"))
            for code in ("en", "ms", "de")}
    # Same keys everywhere, nothing left empty or untranslated by accident.
    assert set(lang["ms"]) == set(lang["en"]) == set(lang["de"])
    tags = re.compile(r"<[^>]+>")
    holes = re.compile(r"\{[a-z]+\}")
    for key, english in lang["en"].items():
        for code in ("ms", "de"):
            value = lang[code][key]
            assert value.strip(), (code, key)
            assert tags.findall(value) == tags.findall(english), (code, key)
            assert sorted(holes.findall(value)) == sorted(holes.findall(english)), (code, key)

    # Every key used in a page exists in the translation files.
    pages = ["start", "beginner-guide", "how-it-works", "industrial-situations",
             "plc-programming-methods", "oil-palm-industrial-environment",
             "oil-palm-control-stack-analysis", "risk-assessment-certification",
             "phase-2-start-here", "phase-3-data-analytics", "phase-4-legacy-ot-recovery"]
    for page in pages:
        html = (static / f"{page}.html").read_text(encoding="utf-8")
        keys = re.findall(r'data-i18n(?:-html)?="([^"]+)"', html)
        keys += [pair.split(":")[1] for attr in re.findall(r'data-i18n-attr="([^"]+)"', html)
                 for pair in attr.split(";")]
        assert len(keys) > 20, page
        missing = [k for k in keys if k not in lang["en"]]
        assert not missing, (page, missing[:5])
        assert "hub-prefs.js" in html and "data-i18n-in" not in html, page

    # The switch offers English (default), Bahasa Malaysia and Deutsch.
    prefs = (static / "hub-prefs.js").read_text(encoding="utf-8")
    assert '"salbotics-hub-lang"' in prefs
    for code in ('code: "en"', 'code: "ms"', 'code: "de"'):
        assert code in prefs
    assert 'lang = "en"' in prefs

    # Generated files are current: en.json matches the pages, search has BM/DE.
    for script in ("i18n_keys.py", "build_search_index.py"):
        result = subprocess.run([sys.executable, str(root / "scripts" / script), "--check"],
                                capture_output=True, text=True)
        assert result.returncode == 0, result.stdout
    index = (static / "search-index.js").read_text(encoding="utf-8")
    data = json.loads(index[index.index("{"):index.rindex("}") + 1])
    assert len(data["topics"]) > 60
    assert all("ms" in item["tr"] and "de" in item["tr"] for item in data["lessons"] + data["words"])
