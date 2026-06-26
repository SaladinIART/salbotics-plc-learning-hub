from __future__ import annotations

import math
import sqlite3
from importlib.metadata import PackageNotFoundError, version
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Lock
from typing import Any


@dataclass(frozen=True)
class LegacyRegister:
    address: int
    name: str
    scale: float
    unit: str
    description: str
    writable: bool = False


REGISTER_MAP: tuple[LegacyRegister, ...] = (
    LegacyRegister(40001, "PRESS_RUN_FB", 1, "bool", "Screw press run feedback from obsolete PLC."),
    LegacyRegister(40002, "PRESS_FAULT", 1, "bool", "Legacy alarm bit from press overload or jam."),
    LegacyRegister(40003, "PRESS_CURRENT_A_X10", 10, "A", "Motor current scaled by 10."),
    LegacyRegister(40004, "PRESS_LOAD_PCT_X10", 10, "%", "Press load percentage scaled by 10."),
    LegacyRegister(40005, "PRESS_VIBRATION_X100", 100, "mm/s", "Vibration estimate scaled by 100."),
    LegacyRegister(40006, "OUTPUT_FLOW_TPH_X100", 100, "t/h", "CPO slurry/output flow scaled by 100."),
    LegacyRegister(40007, "STERILIZER_TEMP_C_X10", 10, "deg C", "Sterilizer temperature scaled by 10."),
    LegacyRegister(40008, "STEAM_PRESSURE_BAR_X100", 100, "bar", "Steam pressure scaled by 100."),
    LegacyRegister(40009, "HMI_HEARTBEAT", 1, "count", "XP/7 HMI heartbeat counter observed by bridge."),
    LegacyRegister(40010, "COMMS_QUALITY_PCT", 1, "%", "Read-only bridge communication quality."),
    LegacyRegister(40011, "DOWNTIME_MIN_TOTAL", 1, "min", "Accumulated downtime minutes seen by bridge."),
    LegacyRegister(40012, "ALARM_COUNT_TOTAL", 1, "events", "Accumulated alarm count seen by bridge."),
)


def package_version(package_name: str) -> str:
    try:
        return version(package_name)
    except PackageNotFoundError:
        return "not installed"


class LegacyOTBridge:
    """Read-only simulated legacy OT bridge for obsolete oil-palm station training."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.lock = Lock()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()
        self.ensure_seeded()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS samples (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    plant_minute INTEGER NOT NULL,
                    press_run_fb INTEGER NOT NULL,
                    press_fault INTEGER NOT NULL,
                    press_current_a REAL NOT NULL,
                    press_load_percent REAL NOT NULL,
                    press_vibration_mm_s REAL NOT NULL,
                    output_flow_tph REAL NOT NULL,
                    sterilizer_temp_c REAL NOT NULL,
                    steam_pressure_bar REAL NOT NULL,
                    hmi_heartbeat INTEGER NOT NULL,
                    comms_quality_percent INTEGER NOT NULL,
                    downtime_minutes_total INTEGER NOT NULL,
                    alarm_count_total INTEGER NOT NULL,
                    read_status TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    source TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    detail TEXT NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_legacy_samples_timestamp ON samples(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_legacy_events_timestamp ON events(timestamp)")

    def ensure_seeded(self) -> None:
        with self.lock:
            with self._connect() as conn:
                count = conn.execute("SELECT COUNT(*) FROM samples").fetchone()[0]
            if count == 0:
                self._reset_unlocked(seed_count=90)

    def reset(self, seed_count: int = 90) -> dict[str, Any]:
        with self.lock:
            self._reset_unlocked(seed_count)
        return self.summary()

    def _reset_unlocked(self, seed_count: int) -> None:
        base_time = datetime.now(timezone.utc) - timedelta(minutes=seed_count)
        downtime_total = 0
        alarm_total = 0
        with self._connect() as conn:
            conn.execute("DELETE FROM samples")
            conn.execute("DELETE FROM events")
            for minute in range(seed_count):
                values = self._sample_values(minute, base_time + timedelta(minutes=minute), downtime_total, alarm_total)
                if values["press_fault"]:
                    downtime_total += 1
                    alarm_total += 1
                    values["downtime_minutes_total"] = downtime_total
                    values["alarm_count_total"] = alarm_total
                self._insert_sample(conn, values)
            self._insert_event(
                conn,
                "reset",
                "Legacy OT bridge",
                "info",
                "Demo legacy bridge seeded",
                "Read-only simulated register samples reseeded for obsolete screw press training.",
            )

    def collect_sample(self) -> dict[str, Any]:
        with self.lock:
            with self._connect() as conn:
                row = conn.execute(
                    """
                    SELECT plant_minute, downtime_minutes_total, alarm_count_total
                    FROM samples ORDER BY id DESC LIMIT 1
                    """
                ).fetchone()
                if row is None:
                    minute = 0
                    downtime_total = 0
                    alarm_total = 0
                else:
                    minute = int(row["plant_minute"]) + 1
                    downtime_total = int(row["downtime_minutes_total"])
                    alarm_total = int(row["alarm_count_total"])

                values = self._sample_values(minute, datetime.now(timezone.utc), downtime_total, alarm_total)
                if values["press_fault"]:
                    values["downtime_minutes_total"] += 1
                    values["alarm_count_total"] += 1
                    self._insert_event(
                        conn,
                        "alarm",
                        "Obsolete screw press PLC",
                        "warning",
                        "Legacy press fault bit is ON",
                        "Bridge records the fault but does not reset, force, or command the PLC.",
                    )
                elif values["read_status"] != "OK":
                    self._insert_event(
                        conn,
                        "communication",
                        "Read-only collector",
                        "warning",
                        "Legacy read quality degraded",
                        "Simulated timeout/stale-read condition; engineer checks adapter, cable, and polling interval.",
                    )
                elif minute % 40 == 0:
                    self._insert_event(
                        conn,
                        "observation",
                        "Read-only collector",
                        "info",
                        "Shadow monitoring checkpoint",
                        "Production remains controlled by the legacy PLC while the bridge records evidence.",
                    )

                self._insert_sample(conn, values)
                return dict(values)

    def summary(self) -> dict[str, Any]:
        with self.lock:
            with self._connect() as conn:
                latest = conn.execute("SELECT * FROM samples ORDER BY id DESC LIMIT 1").fetchone()
                first = conn.execute("SELECT * FROM samples ORDER BY id ASC LIMIT 1").fetchone()
                if latest is None:
                    self._reset_unlocked(seed_count=90)
                    latest = conn.execute("SELECT * FROM samples ORDER BY id DESC LIMIT 1").fetchone()
                    first = conn.execute("SELECT * FROM samples ORDER BY id ASC LIMIT 1").fetchone()
                latest_dict = self._row_to_dict(latest)
                first_dict = self._row_to_dict(first)
                sample_count = conn.execute("SELECT COUNT(*) FROM samples").fetchone()[0]
                event_count = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]

        downtime_delta = int(latest_dict["downtime_minutes_total"] - first_dict["downtime_minutes_total"])
        alarm_delta = int(latest_dict["alarm_count_total"] - first_dict["alarm_count_total"])
        health = self._health(latest_dict)
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "boundary": {
                "mode": "read-only shadow monitoring",
                "localhost_only": True,
                "real_plc_connection": False,
                "write_endpoints": False,
                "license_bypass": False,
            },
            "storage": {
                "engine": "SQLite",
                "path": str(self.db_path),
                "sample_count": sample_count,
                "event_count": event_count,
                "simulated": True,
            },
            "legacy_station": {
                "name": "Obsolete Screw Press Station",
                "process": "Oil-palm screw press",
                "legacy_plc": "Unknown / obsolete PLC class",
                "legacy_hmi": "Windows XP/7 HMI with missing installer/license",
                "adapter": "Virtual Modbus TCP on 127.0.0.1; RS-232 simulated lesson only",
                "control_authority": "Existing PLC remains in control",
            },
            "communication": {
                "transport": "Virtual Modbus TCP",
                "host": "127.0.0.1",
                "port": 15020,
                "modbus_library": f"pymodbus {package_version('pymodbus')}",
                "quality_percent": latest_dict["comms_quality_percent"],
                "read_status": latest_dict["read_status"],
                "health": health,
            },
            "latest_sample": latest_dict,
            "headline_cards": [
                {
                    "label": "Bridge mode",
                    "value": "READ ONLY",
                    "unit": "no writes",
                    "status": "normal",
                    "explanation": "The bridge observes legacy registers and never commands PLC outputs.",
                },
                {
                    "label": "Comms quality",
                    "value": latest_dict["comms_quality_percent"],
                    "unit": "%",
                    "status": "normal" if latest_dict["comms_quality_percent"] >= 90 else "watch",
                    "explanation": "Cable, adapter, baud/timeout, or polling issues show up here first.",
                },
                {
                    "label": "Press current",
                    "value": latest_dict["press_current_a"],
                    "unit": "A",
                    "status": "alarm" if latest_dict["press_fault"] else "watch" if latest_dict["press_current_a"] > 82 else "normal",
                    "explanation": "High current hints at jam, feed rate, cage restriction, or VFD stress.",
                },
                {
                    "label": "Fault count",
                    "value": alarm_delta,
                    "unit": "events",
                    "status": "watch" if alarm_delta else "normal",
                    "explanation": "A bridge can prove repeated faults before PLC replacement is approved.",
                },
                {
                    "label": "Downtime observed",
                    "value": downtime_delta,
                    "unit": "min",
                    "status": "alarm" if downtime_delta > 6 else "watch" if downtime_delta else "normal",
                    "explanation": "Shadow historian records losses without changing the old controller.",
                },
                {
                    "label": "XP/7 HMI risk",
                    "value": "ISOLATE",
                    "unit": "zone",
                    "status": "watch",
                    "explanation": "Treat the old PC as a fragile appliance; no internet and strict network rules.",
                },
            ],
            "workflow": [
                {"step": "Inventory", "meaning": "Record PLC, HMI, I/O cards, cables, firmware, software, and machine drawings."},
                {"step": "Backup/Image", "meaning": "Clone the old PC drive and preserve PLC/HMI backups where authorized."},
                {"step": "Isolate", "meaning": "Place XP/7 and legacy PLC behind OT firewall/VLAN; keep internet away."},
                {"step": "Observe", "meaning": "Read registers/signals only; confirm values against operators and maintenance."},
                {"step": "Reconstruct", "meaning": "Compare extracted Ladder, HMI screens, alarm list, and machine behavior."},
                {"step": "Bridge", "meaning": "Publish safe historian/dashboard data without commanding the machine."},
                {"step": "Migrate later", "meaning": "Plan HMI/PLC replacement with FAT, SAT, cutover, and rollback."},
            ],
            "real_situations": [
                {
                    "problem": "XP/7 HMI works but cannot be reinstalled.",
                    "solution": "Disk image it, isolate it, keep it as reference, and build a read-only dashboard beside it.",
                },
                {
                    "problem": "PLC software and license are gone.",
                    "solution": "Avoid bypassing licenses; recover backups, contact OEM, document behavior, and plan replacement.",
                },
                {
                    "problem": "RS-232 protocol is unclear.",
                    "solution": "Identify baud/parity/stop bits, observe traffic, decode frames, then build a reader before any command.",
                },
                {
                    "problem": "Production cannot stop.",
                    "solution": "Run shadow monitoring first, test during scheduled windows, and keep rollback ready.",
                },
            ],
            "rs232_lesson": self.rs232_lesson(),
        }

    def registers(self) -> dict[str, Any]:
        latest = self.summary()["latest_sample"]
        raw = self._register_values(latest)
        rows = []
        for register in REGISTER_MAP:
            raw_value = raw[register.address]
            rows.append(
                {
                    "address": register.address,
                    "name": register.name,
                    "raw_value": raw_value,
                    "engineering_value": self._engineering_value(register, raw_value),
                    "unit": register.unit,
                    "scale": register.scale,
                    "description": register.description,
                    "writable": register.writable,
                }
            )
        return {
            "transport": "Virtual Modbus TCP",
            "host": "127.0.0.1",
            "port": 15020,
            "read_only": True,
            "rows": rows,
        }

    def events(self, limit: int = 20) -> dict[str, Any]:
        bounded_limit = max(1, min(int(limit), 100))
        with self.lock:
            with self._connect() as conn:
                rows = conn.execute(
                    """
                    SELECT timestamp, event_type, source, severity, message, detail
                    FROM events ORDER BY id DESC LIMIT ?
                    """,
                    (bounded_limit,),
                ).fetchall()
        return {"events": [self._row_to_dict(row) for row in rows]}

    def rs232_lesson(self) -> dict[str, Any]:
        return {
            "port": "loop://",
            "baudrate": 9600,
            "library": f"pyserial {package_version('pyserial')}",
            "parity": "N",
            "stop_bits": 1,
            "timeout_seconds": 1,
            "sample_frame": ":P040003?\\r\\n",
            "sample_response": ":P040003=0785\\r\\n",
            "meaning": "Simulated pySerial loopback frame for press current register 40003; no real COM port is opened by default.",
            "warning": "Real RS-232/RFC2217 links are not encrypted or authenticated; use only in trusted, authorized environments.",
        }

    def _sample_values(
        self,
        minute: int,
        timestamp: datetime,
        downtime_total: int,
        alarm_total: int,
    ) -> dict[str, Any]:
        wave = math.sin(minute / 7)
        slow_wave = math.sin(minute / 23)
        fault = minute % 41 in (0, 1)
        stale = minute % 29 == 0
        press_current = round(70 + 10 * abs(wave) + (22 if fault else 0), 1)
        load = round(min(100, 64 + 20 * abs(wave) + (16 if fault else 0)), 1)
        comms_quality = 74 if stale else 92 if fault else 98
        return {
            "timestamp": timestamp.isoformat(),
            "plant_minute": minute,
            "press_run_fb": 0 if fault else 1,
            "press_fault": 1 if fault else 0,
            "press_current_a": press_current,
            "press_load_percent": load,
            "press_vibration_mm_s": round(2.5 + 0.7 * abs(wave) + (1.8 if fault else 0), 2),
            "output_flow_tph": round(max(6.2 + 0.8 * slow_wave - (1.4 if fault else 0), 0), 2),
            "sterilizer_temp_c": round(132 + 4 * math.sin(minute / 9), 1),
            "steam_pressure_bar": round(3.2 + 0.18 * math.sin(minute / 5), 2),
            "hmi_heartbeat": minute % 10000,
            "comms_quality_percent": comms_quality,
            "downtime_minutes_total": downtime_total,
            "alarm_count_total": alarm_total,
            "read_status": "STALE" if stale else "OK",
        }

    def _register_values(self, latest: dict[str, Any]) -> dict[int, int]:
        return {
            40001: int(latest["press_run_fb"]),
            40002: int(latest["press_fault"]),
            40003: int(round(latest["press_current_a"] * 10)),
            40004: int(round(latest["press_load_percent"] * 10)),
            40005: int(round(latest["press_vibration_mm_s"] * 100)),
            40006: int(round(latest["output_flow_tph"] * 100)),
            40007: int(round(latest["sterilizer_temp_c"] * 10)),
            40008: int(round(latest["steam_pressure_bar"] * 100)),
            40009: int(latest["hmi_heartbeat"]),
            40010: int(latest["comms_quality_percent"]),
            40011: int(latest["downtime_minutes_total"]),
            40012: int(latest["alarm_count_total"]),
        }

    def _engineering_value(self, register: LegacyRegister, raw_value: int) -> float | int | bool:
        if register.unit == "bool":
            return bool(raw_value)
        if register.scale == 1:
            return raw_value
        return round(raw_value / register.scale, 3)

    def _health(self, latest: dict[str, Any]) -> str:
        if latest["press_fault"]:
            return "ALARM"
        if latest["read_status"] != "OK" or latest["comms_quality_percent"] < 90:
            return "DEGRADED"
        return "HEALTHY"

    def _insert_sample(self, conn: sqlite3.Connection, values: dict[str, Any]) -> None:
        keys = list(values.keys())
        placeholders = ", ".join("?" for _ in keys)
        conn.execute(
            f"INSERT INTO samples ({', '.join(keys)}) VALUES ({placeholders})",
            tuple(values[key] for key in keys),
        )

    def _insert_event(
        self,
        conn: sqlite3.Connection,
        event_type: str,
        source: str,
        severity: str,
        message: str,
        detail: str,
    ) -> None:
        conn.execute(
            """
            INSERT INTO events (timestamp, event_type, source, severity, message, detail)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (datetime.now(timezone.utc).isoformat(), event_type, source, severity, message, detail),
        )

    def _row_to_dict(self, row: sqlite3.Row | None) -> dict[str, Any]:
        if row is None:
            return {}
        return {key: row[key] for key in row.keys()}
