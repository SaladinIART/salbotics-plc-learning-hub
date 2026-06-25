from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from threading import Lock

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from plc_engine import INPUT_NAMES, PLCEngine, SCAN_INTERVAL_SECONDS


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


class InputPayload(BaseModel):
    value: bool


async def scan_loop(engine: PLCEngine, lock: Lock) -> None:
    while True:
        await asyncio.sleep(SCAN_INTERVAL_SECONDS)
        with lock:
            engine.tick(SCAN_INTERVAL_SECONDS)


def create_app(start_background: bool = True) -> FastAPI:
    engine = PLCEngine()
    lock = Lock()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.engine = engine
        app.state.lock = lock
        task: asyncio.Task[None] | None = None
        if start_background:
            task = asyncio.create_task(scan_loop(engine, lock))
        try:
            yield
        finally:
            if task is not None:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

    app = FastAPI(title="PLC Traffic-Light Trainer", lifespan=lifespan)

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/api/state")
    def get_state(request: Request) -> dict:
        with request.app.state.lock:
            return request.app.state.engine.snapshot()

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

