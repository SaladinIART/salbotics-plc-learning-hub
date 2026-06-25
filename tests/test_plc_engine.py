from plc_engine import PLCEngine


def tick_many(engine: PLCEngine, seconds: float) -> None:
    steps = round(seconds / 0.1)
    for _ in range(steps):
        engine.tick(0.1)


def test_startup_defaults_to_safe_all_red() -> None:
    engine = PLCEngine()
    state = engine.snapshot()

    assert state["mode"] == "stopped"
    assert state["phase"] == "STOPPED"
    assert state["outputs"]["NS_RED"] is True
    assert state["outputs"]["EW_RED"] is True
    assert state["outputs"]["NS_GREEN"] is False
    assert state["outputs"]["EW_GREEN"] is False


def test_auto_sequence_moves_through_safe_phases() -> None:
    engine = PLCEngine()
    engine.command("start")

    assert engine.phase == "NS_GREEN"
    tick_many(engine, 5.1)
    assert engine.phase == "NS_YELLOW"
    tick_many(engine, 2.1)
    assert engine.phase == "ALL_RED_TO_EW"
    tick_many(engine, 1.1)
    assert engine.phase == "EW_GREEN"
    tick_many(engine, 5.1)
    assert engine.phase == "EW_YELLOW"


def test_overrides_disable_green_outputs() -> None:
    engine = PLCEngine()
    engine.command("start")

    engine.set_input("EMERGENCY", True)
    engine.tick()
    assert engine.snapshot()["mode"] == "emergency"
    assert engine.outputs["NS_GREEN"] is False
    assert engine.outputs["EW_GREEN"] is False
    assert engine.outputs["NS_RED"] is True
    assert engine.outputs["EW_RED"] is True

    engine.set_input("EMERGENCY", False)
    engine.set_input("NIGHT_MODE", True)
    engine.tick()
    assert engine.snapshot()["mode"] == "night"
    assert engine.outputs["NS_GREEN"] is False
    assert engine.outputs["EW_GREEN"] is False

    engine.set_input("NIGHT_MODE", False)
    engine.set_input("STOP", True)
    engine.tick()
    assert engine.snapshot()["mode"] == "stopped"
    assert engine.outputs["NS_GREEN"] is False
    assert engine.outputs["EW_GREEN"] is False


def test_never_allows_both_green_outputs_during_normal_scans() -> None:
    engine = PLCEngine()
    engine.command("start")

    for _ in range(250):
        engine.tick(0.1)
        assert not (engine.outputs["NS_GREEN"] and engine.outputs["EW_GREEN"])


def test_pedestrian_request_latches_and_is_serviced() -> None:
    engine = PLCEngine()
    engine.set_input("PED_EW", True)
    engine.tick()

    assert engine.snapshot()["registers"]["PED_EW_REQUEST"] is True

    engine.command("start")
    tick_many(engine, 8.5)

    state = engine.snapshot()
    assert state["phase"] == "EW_GREEN"
    assert state["registers"]["PED_EW_REQUEST"] is False
    assert state["registers"]["PED_EW_SERVICE"] is True


def test_vehicle_sensor_extends_green_until_max_limit() -> None:
    engine = PLCEngine()
    engine.command("start")
    engine.set_input("VEHICLE_NS", True)

    tick_many(engine, 5.1)
    assert engine.phase == "NS_GREEN"
    assert engine.snapshot()["registers"]["VEHICLE_EXTENSION_ACTIVE"] is True

    tick_many(engine, 4.1)
    assert engine.phase == "NS_YELLOW"


def test_manual_step_uses_safe_sequence() -> None:
    engine = PLCEngine()

    phases = []
    for _ in range(7):
        engine.command("manual_step")
        phases.append(engine.phase)
        engine.tick()
        assert not (engine.outputs["NS_GREEN"] and engine.outputs["EW_GREEN"])

    assert phases[:6] == [
        "NS_GREEN",
        "NS_YELLOW",
        "ALL_RED_TO_EW",
        "EW_GREEN",
        "EW_YELLOW",
        "ALL_RED_TO_NS",
    ]
    assert phases[6] == "NS_GREEN"


def test_fault_reset_requires_conflicting_inputs_cleared() -> None:
    engine = PLCEngine()
    engine.set_input("START", True)
    engine.set_input("STOP", True)
    engine.tick()

    assert engine.snapshot()["registers"]["FAULT_ACTIVE"] is True

    engine.command("reset_fault")
    assert engine.snapshot()["registers"]["FAULT_ACTIVE"] is True

    engine.set_input("STOP", False)
    engine.command("reset_fault")
    assert engine.snapshot()["registers"]["FAULT_ACTIVE"] is False
