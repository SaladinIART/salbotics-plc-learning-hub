# PLC Traffic-Light Trainer

Beginner training project for PLC logic, Ladder thinking, and industrial-style traffic-light control.

The app simulates one 4-way junction using a small PLC mental model: AutomationDirect CLICK `C0-00DR-D`. It is educational software, not a safety controller.

## What You Will Learn

- PLC scan cycle: read inputs, solve logic, write outputs.
- Ladder basics: contacts, coils, run latch, timers, interlocks.
- Safe traffic phases: green, yellow, all-red.
- Industrial inputs: start, stop, pedestrian buttons, vehicle sensors, emergency, night mode.
- Browser HMI basics: status bar, I/O address tables, timer/register tables, rung monitor, field view, alarms, and event log.

## Run Locally

Windows single-click launcher:

```text
start-plc-trainer.bat
```

It uses port `8733` to avoid Salbotics port collisions.

Manual run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8733 --reload
```

Open:

```text
http://127.0.0.1:8733
```

## Test

```powershell
pytest
```

## Learning Order

1. Read `docs/PLC_TRAINING_GUIDE.md`.
2. Run the app.
3. Press `START`.
4. Watch the top status bar, I/O rack, timers, registers, rungs, outputs, and event log.
5. Toggle vehicle sensors, pedestrian requests, emergency, night mode.
6. Read `plc_engine.py` slowly from top to bottom.
7. Compare code logic to Ladder concepts in the guide.
