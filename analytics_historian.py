from __future__ import annotations

import math
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Lock
from typing import Any


METRIC_COLUMNS: dict[str, tuple[str, str]] = {
    "ffb_tph": ("ffb_tph", "t/h"),
    "cpo_tph": ("cpo_tph", "t/h"),
    "oer_percent": ("oer_percent", "%"),
    "tank_level_percent": ("tank_level_percent", "%"),
    "steam_pressure_bar": ("steam_pressure_bar", "bar"),
    "sterilizer_temp_c": ("sterilizer_temp_c", "deg C"),
    "press_current_a": ("press_current_a", "A"),
    "press_load_percent": ("press_load_percent", "%"),
    "press_vibration_mm_s": ("press_vibration_mm_s", "mm/s"),
    "output_flow_tph": ("output_flow_tph", "t/h"),
    "energy_kw": ("energy_kw", "kW"),
    "quality_moisture_percent": ("quality_moisture_percent", "%"),
    "quality_ffa_percent": ("quality_ffa_percent", "%"),
}


class AnalyticsHistorian:
    """Small local historian for Phase 3 simulated oil-palm analytics."""

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
                    ffb_tph REAL NOT NULL,
                    cpo_tph REAL NOT NULL,
                    oer_percent REAL NOT NULL,
                    tank_level_percent REAL NOT NULL,
                    steam_pressure_bar REAL NOT NULL,
                    sterilizer_temp_c REAL NOT NULL,
                    press_current_a REAL NOT NULL,
                    press_load_percent REAL NOT NULL,
                    press_vibration_mm_s REAL NOT NULL,
                    output_flow_tph REAL NOT NULL,
                    energy_kw REAL NOT NULL,
                    downtime_minutes_total INTEGER NOT NULL,
                    alarm_count_total INTEGER NOT NULL,
                    station_reception TEXT NOT NULL,
                    station_sterilizer TEXT NOT NULL,
                    station_press TEXT NOT NULL,
                    quality_moisture_percent REAL NOT NULL,
                    quality_ffa_percent REAL NOT NULL
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
            conn.execute("CREATE INDEX IF NOT EXISTS idx_samples_timestamp ON samples(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)")

    def ensure_seeded(self) -> None:
        with self.lock:
            with self._connect() as conn:
                count = conn.execute("SELECT COUNT(*) FROM samples").fetchone()[0]
            if count == 0:
                self._reset_unlocked(seed_count=120)

    def reset(self, seed_count: int = 120) -> dict[str, Any]:
        with self.lock:
            self._reset_unlocked(seed_count)
        return self.summary()

    def _reset_unlocked(self, seed_count: int) -> None:
        base_time = datetime.now(timezone.utc) - timedelta(minutes=seed_count)
        with self._connect() as conn:
            conn.execute("DELETE FROM events")
            conn.execute("DELETE FROM samples")
            downtime_total = 0
            alarm_total = 0
            for minute in range(seed_count):
                values = self._sample_values(minute, base_time + timedelta(minutes=minute), downtime_total, alarm_total)
                if values["station_press"] == "FAULT":
                    downtime_total += 1
                    alarm_total += 1
                    values["downtime_minutes_total"] = downtime_total
                    values["alarm_count_total"] = alarm_total
                self._insert_sample(conn, values)
            conn.execute(
                """
                INSERT INTO events (timestamp, event_type, source, severity, message, detail)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.now(timezone.utc).isoformat(),
                    "reset",
                    "Phase 3 historian",
                    "info",
                    "Demo historian seeded",
                    "SQLite historian reset with simulated oil-palm samples.",
                ),
            )

    def collect_sample(self) -> dict[str, Any]:
        with self.lock:
            with self._connect() as conn:
                row = conn.execute(
                    """
                    SELECT plant_minute, downtime_minutes_total, alarm_count_total
                    FROM samples
                    ORDER BY id DESC
                    LIMIT 1
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
                if values["station_press"] == "FAULT":
                    values["downtime_minutes_total"] += 1
                    values["alarm_count_total"] += 1
                    self._insert_event(
                        conn,
                        "alarm",
                        "Screw Press",
                        "warning",
                        "Press current high",
                        "Management sees this as downtime risk; technician checks load, cage, and VFD feedback.",
                    )
                elif minute % 45 == 0:
                    self._insert_event(
                        conn,
                        "production",
                        "Line summary",
                        "info",
                        "Shift production checkpoint",
                        "FFB, CPO, OER, and tank level snapshot recorded for management dashboard.",
                    )

                self._insert_sample(conn, values)
                return dict(values)

    def summary(self) -> dict[str, Any]:
        with self.lock:
            with self._connect() as conn:
                latest = conn.execute("SELECT * FROM samples ORDER BY id DESC LIMIT 1").fetchone()
                first = conn.execute("SELECT * FROM samples ORDER BY id ASC LIMIT 1").fetchone()
                if latest is None:
                    self._reset_unlocked(seed_count=120)
                    latest = conn.execute("SELECT * FROM samples ORDER BY id DESC LIMIT 1").fetchone()
                    first = conn.execute("SELECT * FROM samples ORDER BY id ASC LIMIT 1").fetchone()
                latest_dict = self._row_to_dict(latest)
                first_dict = self._row_to_dict(first)

                sample_count = conn.execute("SELECT COUNT(*) FROM samples").fetchone()[0]
                event_count = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]

        minutes = max(sample_count, 1)
        ffb_processed_t = round(latest_dict["ffb_tph"] * minutes / 60, 2)
        cpo_output_t = round(latest_dict["cpo_tph"] * minutes / 60, 2)
        downtime = int(latest_dict["downtime_minutes_total"] - first_dict["downtime_minutes_total"])
        alarms = int(latest_dict["alarm_count_total"] - first_dict["alarm_count_total"])
        uptime_percent = round(max(0, (minutes - downtime) / minutes) * 100, 1)
        quality_status = "watch" if latest_dict["quality_moisture_percent"] > 0.22 else "normal"

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "storage": {
                "engine": "SQLite",
                "path": str(self.db_path),
                "sample_count": sample_count,
                "event_count": event_count,
                "simulated": True,
            },
            "latest_sample": latest_dict,
            "management_cards": [
                {
                    "label": "FFB processed",
                    "value": ffb_processed_t,
                    "unit": "t demo shift",
                    "status": "normal",
                    "explanation": "Raw material throughput visible without reading PLC logic.",
                },
                {
                    "label": "CPO output",
                    "value": cpo_output_t,
                    "unit": "t demo shift",
                    "status": "normal",
                    "explanation": "Management sees product output and can compare against plan.",
                },
                {
                    "label": "OER",
                    "value": latest_dict["oer_percent"],
                    "unit": "%",
                    "status": "watch" if latest_dict["oer_percent"] < 20.5 else "normal",
                    "explanation": "Oil extraction rate connects process performance to business value.",
                },
                {
                    "label": "Downtime",
                    "value": downtime,
                    "unit": "min",
                    "status": "alarm" if downtime > 8 else "watch" if downtime > 3 else "normal",
                    "explanation": "Downtime turns hidden stoppages into management-visible loss.",
                },
                {
                    "label": "Alarm count",
                    "value": alarms,
                    "unit": "events",
                    "status": "watch" if alarms else "normal",
                    "explanation": "Repeated alarms show where maintenance and training should focus.",
                },
                {
                    "label": "Uptime",
                    "value": uptime_percent,
                    "unit": "%",
                    "status": "normal" if uptime_percent >= 95 else "watch",
                    "explanation": "Simple OEE-style availability signal for daily review.",
                },
            ],
            "shift": {
                "ffb_processed_t": ffb_processed_t,
                "cpo_output_t": cpo_output_t,
                "oer_percent": latest_dict["oer_percent"],
                "uptime_percent": uptime_percent,
                "downtime_minutes": downtime,
                "alarm_count": alarms,
                "quality_status": quality_status,
                "energy_kwh_estimate": round(latest_dict["energy_kw"] * minutes / 60, 1),
            },
            "station_states": [
                {"name": "Reception", "state": latest_dict["station_reception"], "business_meaning": "FFB arrival and feed availability."},
                {"name": "Sterilizer", "state": latest_dict["station_sterilizer"], "business_meaning": "Batch cycle bottleneck and steam demand."},
                {"name": "Screw Press", "state": latest_dict["station_press"], "business_meaning": "Extraction output, motor load, and downtime risk."},
                {"name": "CPO Tank", "state": f'{latest_dict["tank_level_percent"]:.1f}%', "business_meaning": "Storage and dispatch readiness."},
            ],
            "screw_press": {
                "motor_current_a": latest_dict["press_current_a"],
                "load_percent": latest_dict["press_load_percent"],
                "vibration_mm_s": latest_dict["press_vibration_mm_s"],
                "output_flow_tph": latest_dict["output_flow_tph"],
                "status": latest_dict["station_press"],
                "maintenance_hint": self._press_hint(latest_dict),
            },
            "architecture_layers": [
                {"layer": "OT", "meaning": "PLC, sensors, VFD, HMI, SCADA, historian", "dashboard_value": "Trusted plant data source."},
                {"layer": "IT", "meaning": "Server, database, network, backup, dashboard access", "dashboard_value": "Makes local data available and recoverable."},
                {"layer": "MES", "meaning": "Production order, downtime reason, batch/shift tracking, performance", "dashboard_value": "Connects machine events to operations."},
                {"layer": "ERP", "meaning": "Planning, inventory, costing, sales, management reporting", "dashboard_value": "Turns production reality into business decisions."},
            ],
        }

    def trends(self, metric: str, minutes: int = 60) -> dict[str, Any]:
        if metric not in METRIC_COLUMNS:
            raise KeyError(metric)
        column, unit = METRIC_COLUMNS[metric]
        limit = max(1, min(int(minutes), 240))
        with self.lock:
            with self._connect() as conn:
                rows = conn.execute(
                    f"SELECT timestamp, {column} AS value FROM samples ORDER BY id DESC LIMIT ?",
                    (limit,),
                ).fetchall()
        points = [{"timestamp": row["timestamp"], "value": row["value"]} for row in reversed(rows)]
        return {"metric": metric, "unit": unit, "points": points}

    def events(self, limit: int = 20) -> dict[str, Any]:
        bounded_limit = max(1, min(int(limit), 100))
        with self.lock:
            with self._connect() as conn:
                rows = conn.execute(
                    """
                    SELECT timestamp, event_type, source, severity, message, detail
                    FROM events
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (bounded_limit,),
                ).fetchall()
        return {"events": [self._row_to_dict(row) for row in rows]}

    def _sample_values(
        self,
        minute: int,
        timestamp: datetime,
        downtime_total: int,
        alarm_total: int,
    ) -> dict[str, Any]:
        wave = math.sin(minute / 8)
        slow_wave = math.sin(minute / 19)
        press_fault = minute % 37 in (0, 1, 2)
        sterilizer_hold = minute % 30 in range(0, 6)
        ffb_tph = round(34 + 4.5 * wave - (7 if press_fault else 0), 2)
        oer = round(21.4 + 0.35 * slow_wave - (0.45 if press_fault else 0), 2)
        cpo_tph = round(max(ffb_tph * oer / 100, 0), 2)
        press_current = round(68 + 11 * abs(wave) + (19 if press_fault else 0), 1)
        press_load = round(min(100, 62 + 18 * abs(wave) + (18 if press_fault else 0)), 1)
        station_press = "FAULT" if press_fault else "RUN"
        return {
            "timestamp": timestamp.isoformat(),
            "plant_minute": minute,
            "ffb_tph": ffb_tph,
            "cpo_tph": cpo_tph,
            "oer_percent": oer,
            "tank_level_percent": round(58 + (minute % 80) * 0.28 + 4 * slow_wave, 1),
            "steam_pressure_bar": round(3.1 + 0.2 * math.sin(minute / 5), 2),
            "sterilizer_temp_c": round(132 + 4 * math.sin(minute / 6), 1),
            "press_current_a": press_current,
            "press_load_percent": press_load,
            "press_vibration_mm_s": round(2.8 + 0.4 * abs(wave) + (1.7 if press_fault else 0), 2),
            "output_flow_tph": cpo_tph,
            "energy_kw": round(420 + 34 * abs(slow_wave) + (45 if press_fault else 0), 1),
            "downtime_minutes_total": downtime_total,
            "alarm_count_total": alarm_total,
            "station_reception": "RUN" if ffb_tph > 28 else "SLOW",
            "station_sterilizer": "HOLD" if sterilizer_hold else "RUN",
            "station_press": station_press,
            "quality_moisture_percent": round(0.18 + 0.05 * abs(slow_wave) + (0.03 if press_fault else 0), 3),
            "quality_ffa_percent": round(3.1 + 0.2 * abs(wave), 2),
        }

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

    def _press_hint(self, latest: dict[str, Any]) -> str:
        if latest["station_press"] == "FAULT":
            return "Check screw press load, cage restriction, VFD current, and fruit feed rate."
        if latest["press_current_a"] > 78:
            return "Watch motor current trend; prepare maintenance inspection if it keeps rising."
        return "Press load normal; continue monitoring current, vibration, and output flow."

    def _row_to_dict(self, row: sqlite3.Row | None) -> dict[str, Any]:
        if row is None:
            return {}
        return {key: row[key] for key in row.keys()}
