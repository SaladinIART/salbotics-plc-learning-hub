from __future__ import annotations

from dataclasses import dataclass
from typing import Any


SCAN_INTERVAL_SECONDS = 0.1

INPUT_NAMES = (
    "START",
    "STOP",
    "PED_NS",
    "PED_EW",
    "VEHICLE_NS",
    "VEHICLE_EW",
    "EMERGENCY",
    "NIGHT_MODE",
)

OUTPUT_NAMES = (
    "NS_RED",
    "NS_YELLOW",
    "NS_GREEN",
    "EW_RED",
    "EW_YELLOW",
    "EW_GREEN",
)

AUTO_SEQUENCE = (
    "NS_GREEN",
    "NS_YELLOW",
    "ALL_RED_TO_EW",
    "EW_GREEN",
    "EW_YELLOW",
    "ALL_RED_TO_NS",
)

MANUAL_SEQUENCE = AUTO_SEQUENCE


@dataclass(frozen=True)
class TimerConfig:
    green_base_s: float = 5.0
    green_max_s: float = 9.0
    yellow_s: float = 2.0
    all_red_s: float = 1.0
    flash_half_period_s: float = 0.5


class PLCEngine:
    """Small educational PLC scan-cycle model for a traffic-light trainer."""

    def __init__(self, timers: TimerConfig | None = None) -> None:
        self.timers = timers or TimerConfig()
        self.inputs = {name: False for name in INPUT_NAMES}
        self.outputs = {name: False for name in OUTPUT_NAMES}
        self.mode = "stopped"
        self.phase = "STOPPED"
        self.phase_elapsed_s = 0.0
        self.simulation_time_s = 0.0
        self.scan_count = 0
        self.running = False
        self.manual_mode = False
        self.fault_active = False
        self.fault_message = ""
        self.ped_request_ns = False
        self.ped_request_ew = False
        self.ped_service_ns = False
        self.ped_service_ew = False
        self.night_flash_on = False
        self.event_log: list[dict[str, Any]] = []
        self._set_all_red()
        self._log("Trainer powered up. Outputs are safe all-red.", "system")

    def set_input(self, name: str, value: bool) -> None:
        self._validate_input(name)
        value = bool(value)
        if self.inputs[name] == value:
            return
        self.inputs[name] = value
        self._log(f"Input {name} set to {'ON' if value else 'OFF'}.", "input")

    def command(self, command: str) -> None:
        handlers = {
            "start": self._command_start,
            "stop": self._command_stop,
            "manual_step": self._command_manual_step,
            "reset_fault": self._command_reset_fault,
        }
        handler = handlers.get(command)
        if handler is None:
            raise ValueError(f"Unknown command: {command}")
        handler()

    def tick(self, delta_s: float = SCAN_INTERVAL_SECONDS) -> None:
        delta_s = max(float(delta_s), 0.0)
        self.simulation_time_s += delta_s
        self.scan_count += 1
        self._latch_operator_requests()

        if self.inputs["START"] and self.inputs["STOP"]:
            self._raise_fault("START and STOP are both active. Check stuck pushbuttons.")

        if self.fault_active:
            self.mode = "fault"
            self.phase = "FAULT_ALL_RED"
            self._set_all_red()
            return

        if self.inputs["EMERGENCY"]:
            if self.phase != "EMERGENCY_ALL_RED":
                self._log("Emergency input active. Forcing all-red.", "alarm")
            self.mode = "emergency"
            self.phase = "EMERGENCY_ALL_RED"
            self._set_all_red()
            return

        if self.inputs["NIGHT_MODE"]:
            if self.phase != "NIGHT_FLASH":
                self._log("Night mode active. Red lamps flashing.", "mode")
                self.phase_elapsed_s = 0.0
            self.mode = "night"
            self.phase = "NIGHT_FLASH"
            self.phase_elapsed_s += delta_s
            self._apply_night_flash_outputs()
            return

        if self.inputs["STOP"] and (self.running or self.manual_mode or self.phase != "STOPPED"):
            self._stop("Stop input active. Returning to all-red.")

        if self.inputs["START"] and not self.running and not self.manual_mode and not self.inputs["STOP"]:
            self._start_auto("Start input active. Auto cycle started.")

        if self.manual_mode:
            self.mode = "manual"
            self._apply_outputs_for_phase()
            self._service_pedestrian_requests()
            return

        if not self.running:
            self.mode = "stopped"
            self.phase = "STOPPED"
            self._set_all_red()
            return

        self.mode = "auto"
        if self.phase not in AUTO_SEQUENCE:
            self._set_phase("NS_GREEN")

        self.phase_elapsed_s += delta_s
        self._service_pedestrian_requests()
        self._apply_outputs_for_phase()

        if self._phase_should_advance():
            self._advance_auto_phase()
            self._service_pedestrian_requests()
            self._apply_outputs_for_phase()

    def snapshot(self) -> dict[str, Any]:
        return {
            "inputs": dict(self.inputs),
            "outputs": dict(self.outputs),
            "mode": self.mode,
            "phase": self.phase,
            "timers": {
                "scan_interval_ms": int(SCAN_INTERVAL_SECONDS * 1000),
                "phase_elapsed_s": round(self.phase_elapsed_s, 1),
                "phase_target_s": round(self._phase_target_seconds(), 1),
                "phase_remaining_s": round(max(self._phase_target_seconds() - self.phase_elapsed_s, 0.0), 1),
                "green_base_s": self.timers.green_base_s,
                "green_max_s": self.timers.green_max_s,
                "yellow_s": self.timers.yellow_s,
                "all_red_s": self.timers.all_red_s,
                "scan_count": self.scan_count,
            },
            "registers": {
                "RUN_LATCH": self.running,
                "MANUAL_MODE": self.manual_mode,
                "FAULT_ACTIVE": self.fault_active,
                "PED_NS_REQUEST": self.ped_request_ns,
                "PED_EW_REQUEST": self.ped_request_ew,
                "PED_NS_SERVICE": self.ped_service_ns,
                "PED_EW_SERVICE": self.ped_service_ew,
                "VEHICLE_EXTENSION_ACTIVE": self._vehicle_extension_active(),
                "NIGHT_FLASH_ON": self.night_flash_on,
            },
            "alarms": self._alarms(),
            "ladder_rungs": self._ladder_rungs(),
            "event_log": list(self.event_log),
            "plc": {
                "model": "AutomationDirect CLICK C0-00DR-D training model",
                "scan_time_ms": int(SCAN_INTERVAL_SECONDS * 1000),
                "note": "Educational software model, not a safety controller.",
            },
        }

    def _command_start(self) -> None:
        if self.fault_active:
            self._log("Start blocked by active fault.", "alarm")
            return
        if self.inputs["EMERGENCY"]:
            self._log("Start blocked by emergency input.", "alarm")
            return
        if self.inputs["STOP"]:
            self._log("Start blocked while STOP input is ON.", "alarm")
            return
        self._start_auto("Auto cycle started from HMI command.")

    def _command_stop(self) -> None:
        self._stop("Stop command received. Returning to all-red.")

    def _command_manual_step(self) -> None:
        if self.fault_active:
            self._log("Manual step blocked by active fault.", "alarm")
            return
        if self.inputs["EMERGENCY"]:
            self._log("Manual step blocked by emergency input.", "alarm")
            return
        if self.inputs["NIGHT_MODE"]:
            self._log("Manual step blocked by night mode.", "alarm")
            return
        self.running = False
        self.manual_mode = True
        next_phase = self._next_manual_phase()
        self._set_phase(next_phase)
        self._log(f"Manual safe-step moved to {next_phase}.", "mode")

    def _command_reset_fault(self) -> None:
        if not self.fault_active:
            self._log("Reset fault command received. No active fault.", "system")
            return
        if self.inputs["START"] and self.inputs["STOP"]:
            self._log("Fault reset blocked. Clear START or STOP first.", "alarm")
            return
        self.fault_active = False
        self.fault_message = ""
        self.running = False
        self.manual_mode = False
        self._set_phase("STOPPED")
        self._set_all_red()
        self._log("Fault reset complete. Controller stopped in all-red.", "system")

    def _start_auto(self, reason: str) -> None:
        self.running = True
        self.manual_mode = False
        if self.phase not in AUTO_SEQUENCE:
            self._set_phase("NS_GREEN")
        self._log(reason, "mode")

    def _stop(self, reason: str) -> None:
        self.running = False
        self.manual_mode = False
        self._set_phase("STOPPED")
        self._set_all_red()
        self._log(reason, "mode")

    def _set_phase(self, phase: str) -> None:
        if self.phase == phase:
            return
        self.phase = phase
        self.phase_elapsed_s = 0.0
        self.ped_service_ns = False
        self.ped_service_ew = False
        self._log(f"Phase changed to {phase}.", "phase")

    def _advance_auto_phase(self) -> None:
        current_index = AUTO_SEQUENCE.index(self.phase)
        self._set_phase(AUTO_SEQUENCE[(current_index + 1) % len(AUTO_SEQUENCE)])

    def _next_manual_phase(self) -> str:
        if self.phase not in MANUAL_SEQUENCE:
            return "NS_GREEN"
        current_index = MANUAL_SEQUENCE.index(self.phase)
        return MANUAL_SEQUENCE[(current_index + 1) % len(MANUAL_SEQUENCE)]

    def _phase_should_advance(self) -> bool:
        target_s = self._phase_target_seconds()
        return target_s > 0 and self.phase_elapsed_s + 1e-9 >= target_s

    def _phase_target_seconds(self) -> float:
        if self.phase == "NS_GREEN":
            return self.timers.green_max_s if self.inputs["VEHICLE_NS"] else self.timers.green_base_s
        if self.phase == "EW_GREEN":
            return self.timers.green_max_s if self.inputs["VEHICLE_EW"] else self.timers.green_base_s
        if self.phase in ("NS_YELLOW", "EW_YELLOW"):
            return self.timers.yellow_s
        if self.phase in ("ALL_RED_TO_EW", "ALL_RED_TO_NS"):
            return self.timers.all_red_s
        return 0.0

    def _latch_operator_requests(self) -> None:
        if self.inputs["PED_NS"] and not self.ped_request_ns:
            self.ped_request_ns = True
            self._log("PED_NS request latched.", "input")
        if self.inputs["PED_EW"] and not self.ped_request_ew:
            self.ped_request_ew = True
            self._log("PED_EW request latched.", "input")

    def _service_pedestrian_requests(self) -> None:
        if self.phase == "NS_GREEN" and self.ped_request_ns:
            self.ped_request_ns = False
            self.ped_service_ns = True
            self._log("PED_NS request serviced during NS green.", "phase")
        if self.phase == "EW_GREEN" and self.ped_request_ew:
            self.ped_request_ew = False
            self.ped_service_ew = True
            self._log("PED_EW request serviced during EW green.", "phase")

    def _apply_outputs_for_phase(self) -> None:
        self.outputs = {name: False for name in OUTPUT_NAMES}
        if self.phase in ("STOPPED", "ALL_RED_TO_EW", "ALL_RED_TO_NS", "EMERGENCY_ALL_RED", "FAULT_ALL_RED"):
            self._set_all_red()
        elif self.phase == "NS_GREEN":
            self.outputs["NS_GREEN"] = True
            self.outputs["EW_RED"] = True
        elif self.phase == "NS_YELLOW":
            self.outputs["NS_YELLOW"] = True
            self.outputs["EW_RED"] = True
        elif self.phase == "EW_GREEN":
            self.outputs["EW_GREEN"] = True
            self.outputs["NS_RED"] = True
        elif self.phase == "EW_YELLOW":
            self.outputs["EW_YELLOW"] = True
            self.outputs["NS_RED"] = True
        else:
            self._set_all_red()
        self._detect_output_conflict()

    def _apply_night_flash_outputs(self) -> None:
        half_period = self.timers.flash_half_period_s
        flash_index = int(self.phase_elapsed_s / half_period) if half_period > 0 else 0
        self.night_flash_on = flash_index % 2 == 0
        self.outputs = {name: False for name in OUTPUT_NAMES}
        if self.night_flash_on:
            self.outputs["NS_RED"] = True
            self.outputs["EW_RED"] = True

    def _set_all_red(self) -> None:
        self.outputs = {name: False for name in OUTPUT_NAMES}
        self.outputs["NS_RED"] = True
        self.outputs["EW_RED"] = True
        self.night_flash_on = False

    def _detect_output_conflict(self) -> None:
        if self.outputs["NS_GREEN"] and self.outputs["EW_GREEN"]:
            self._raise_fault("Safety fault: NS_GREEN and EW_GREEN are both energized.")
            self._set_all_red()

    def _vehicle_extension_active(self) -> bool:
        return (
            self.phase == "NS_GREEN"
            and self.inputs["VEHICLE_NS"]
            and self.phase_elapsed_s >= self.timers.green_base_s
            and self.phase_elapsed_s < self.timers.green_max_s
        ) or (
            self.phase == "EW_GREEN"
            and self.inputs["VEHICLE_EW"]
            and self.phase_elapsed_s >= self.timers.green_base_s
            and self.phase_elapsed_s < self.timers.green_max_s
        )

    def _alarms(self) -> list[str]:
        alarms = []
        if self.fault_active:
            alarms.append(self.fault_message)
        if self.inputs["EMERGENCY"]:
            alarms.append("Emergency input active")
        if self.inputs["START"] and self.inputs["STOP"]:
            alarms.append("START and STOP both active")
        return alarms

    def _ladder_rungs(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "RUNG 001 RUN LATCH",
                "description": "START seals in RUN unless STOP, EMERGENCY, or FAULT breaks it.",
                "energized": self.running,
            },
            {
                "name": "RUNG 002 STOP SAFE",
                "description": "STOP or no RUN forces both directions red.",
                "energized": self.inputs["STOP"] or not self.running,
            },
            {
                "name": "RUNG 003 EMERGENCY",
                "description": "EMERGENCY overrides every normal phase.",
                "energized": self.inputs["EMERGENCY"],
            },
            {
                "name": "RUNG 004 NIGHT FLASH",
                "description": "NIGHT_MODE flashes red lamps and disables greens.",
                "energized": self.inputs["NIGHT_MODE"],
            },
            {
                "name": "RUNG 010 NS GREEN",
                "description": "NS green coil energizes only during NS_GREEN phase.",
                "energized": self.outputs["NS_GREEN"],
            },
            {
                "name": "RUNG 020 EW GREEN",
                "description": "EW green coil energizes only during EW_GREEN phase.",
                "energized": self.outputs["EW_GREEN"],
            },
            {
                "name": "RUNG 900 GREEN CONFLICT CHECK",
                "description": "Faults if both green coils are energized together.",
                "energized": not (self.outputs["NS_GREEN"] and self.outputs["EW_GREEN"]),
            },
        ]

    def _raise_fault(self, message: str) -> None:
        if self.fault_active and self.fault_message == message:
            return
        self.fault_active = True
        self.fault_message = message
        self.running = False
        self.manual_mode = False
        self._log(message, "fault")

    def _log(self, message: str, kind: str) -> None:
        entry = {
            "time_s": round(self.simulation_time_s, 1),
            "kind": kind,
            "message": message,
        }
        self.event_log.insert(0, entry)
        del self.event_log[80:]

    @staticmethod
    def _validate_input(name: str) -> None:
        if name not in INPUT_NAMES:
            raise ValueError(f"Unknown input: {name}")
