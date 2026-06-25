# Phase 1 Launch QA

Date: 2026-06-26

Product identity:

```text
Salbotics PLC Learning Hub
```

## Verification Completed

Python simulator tests:

```text
.\.venv\Scripts\python.exe -m pytest -q
23 passed
```

Astro static build:

```text
cd frontend
npm run build
2 page(s) built
```

Windows launcher:

```text
cmd /c start-plc-trainer.bat
Server already running on port 8733.
Opening browser...
```

Local browser QA:

- Desktop `1440x900` loaded `http://127.0.0.1:8733/`.
- Mobile `390x844` loaded `http://127.0.0.1:8733/`.
- Page title: `Salbotics PLC Learning Hub`.
- Header brand: `SALBOTICS PLC HUB`.
- Dashboard rendered I/O rack, rung monitor, junction, alarm summary, and event log.
- Programming methods guide loaded with product footer.
- No browser console errors.
- No page-level horizontal overflow on desktop or mobile.

Static demo artifact check:

- `frontend/dist/index.html` exists after `npm run build`.
- `frontend/dist/how-it-works/index.html` exists after `npm run build`.
- Public static demo remains separate from the local FastAPI PLC-control runtime.

Repository hygiene:

- Remote now points to `https://github.com/SaladinIART/salbotics-plc-learning-hub.git`.
- `LICENSE` and `NOTICE` are present.
- README contains public links, screenshots, safety boundary, roadmap, and frontend spike notes.
- `docs/PROJECT_SWOT_ANALYSIS.md` remains private/untracked and was not committed.

## Final Phase 1 Boundary

Phase 1 is ready for public polishing and publication as an open learning hub.

Phase 2 remains on hold:

- No pySerial runtime.
- No Modbus runtime.
- No OpenPLC runtime bridge.
- No MQTT/OPC UA runtime gateway.
- No public hosted live-control API.

