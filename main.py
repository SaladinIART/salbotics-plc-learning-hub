from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from threading import Lock

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from analytics_historian import AnalyticsHistorian
from plc_engine import INPUT_NAMES, PLCEngine, SCAN_INTERVAL_SECONDS


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DEFAULT_ANALYTICS_DB = BASE_DIR / "local_data" / "phase3_analytics.sqlite3"


class InputPayload(BaseModel):
    value: bool


async def scan_loop(engine: PLCEngine, lock: Lock) -> None:
    while True:
        await asyncio.sleep(SCAN_INTERVAL_SECONDS)
        with lock:
            engine.tick(SCAN_INTERVAL_SECONDS)


async def analytics_loop(historian: AnalyticsHistorian) -> None:
    while True:
        await asyncio.sleep(2)
        historian.collect_sample()


def create_app(start_background: bool = True, analytics_db_path: Path | None = None) -> FastAPI:
    engine = PLCEngine()
    lock = Lock()
    historian = AnalyticsHistorian(analytics_db_path or DEFAULT_ANALYTICS_DB)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.engine = engine
        app.state.lock = lock
        app.state.analytics = historian
        tasks: list[asyncio.Task[None]] = []
        if start_background:
            tasks.append(asyncio.create_task(scan_loop(engine, lock)))
            tasks.append(asyncio.create_task(analytics_loop(historian)))
        try:
            yield
        finally:
            for task in tasks:
                task.cancel()
            for task in tasks:
                try:
                    await task
                except asyncio.CancelledError:
                    pass

    app = FastAPI(title="Salbotics PLC Learning Hub", lifespan=lifespan)

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/how-it-works")
    def how_it_works() -> FileResponse:
        return FileResponse(STATIC_DIR / "how-it-works.html")

    @app.get("/industrial-situations")
    def industrial_situations() -> FileResponse:
        return FileResponse(STATIC_DIR / "industrial-situations.html")

    @app.get("/oil-palm-industrial-environment")
    def oil_palm_industrial_environment() -> FileResponse:
        return FileResponse(STATIC_DIR / "oil-palm-industrial-environment.html")

    @app.get("/oil-palm-control-stack-analysis")
    def oil_palm_control_stack_analysis() -> FileResponse:
        return FileResponse(STATIC_DIR / "oil-palm-control-stack-analysis.html")

    @app.get("/plc-programming-methods")
    def plc_programming_methods() -> FileResponse:
        return FileResponse(STATIC_DIR / "plc-programming-methods.html")

    @app.get("/risk-assessment-certification")
    def risk_assessment_certification() -> FileResponse:
        return FileResponse(STATIC_DIR / "risk-assessment-certification.html")

    @app.get("/phase-2-start-here")
    def phase_2_start_here() -> FileResponse:
        return FileResponse(STATIC_DIR / "phase-2-start-here.html")

    @app.get("/phase-3-data-analytics")
    def phase_3_data_analytics() -> FileResponse:
        return FileResponse(STATIC_DIR / "phase-3-data-analytics.html")

    @app.get("/api/state")
    def get_state(request: Request) -> dict:
        with request.app.state.lock:
            return request.app.state.engine.snapshot()

    @app.get("/api/analytics/summary")
    def analytics_summary(request: Request) -> dict:
        return request.app.state.analytics.summary()

    @app.get("/api/analytics/trends")
    def analytics_trends(request: Request, metric: str = "ffb_tph", minutes: int = 60) -> dict:
        try:
            return request.app.state.analytics.trends(metric, minutes)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=f"Unknown analytics metric: {metric}") from exc

    @app.get("/api/analytics/events")
    def analytics_events(request: Request, limit: int = 20) -> dict:
        return request.app.state.analytics.events(limit)

    @app.post("/api/analytics/reset")
    def analytics_reset(request: Request) -> dict:
        return request.app.state.analytics.reset()

    @app.post("/api/inputs/{name}")
    def set_input(name: str, payload: InputPayload, request: Request) -> dict:
        normalized = name.upper()
        if normalized not in INPUT_NAMES:
            raise HTTPException(status_code=404, detail=f"Unknown input: {name}")
        with request.app.state.lock:
            request.app.state.engine.set_input(normalized, payload.value)
            return request.app.state.engine.snapshot()

    @app.post("/api/commands/{command}")
    def run_command(command: str, request: Request) -> dict:
        normalized = command.lower()
        try:
            with request.app.state.lock:
                request.app.state.engine.command(normalized)
                return request.app.state.engine.snapshot()
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    return app


app = create_app()
