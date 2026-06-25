# Salbotics PLC Learning Hub

An open educational product by Salbotics Solutions: one portable place to learn PLC logic, Ladder thinking, industrial HMI basics, oil-palm automation context, and safety-awareness basics.

The app simulates one 4-way junction using a small PLC mental model: AutomationDirect CLICK `C0-00DR-D`. It is educational software, not a safety controller.

## License, Attribution, And Safety Boundary

- Licensed under the MIT License. See `LICENSE`.
- Original product and training concept by **Salbotics Solutions**. See `NOTICE`.
- Please credit **Salbotics PLC Learning Hub by Salbotics Solutions** when teaching from, demonstrating, or publishing derived work based on this project.
- Contributions should preserve the educational boundary: this project is not certified traffic-control, machinery-safety, process-safety, or industrial-control software.
- Phase 2 communication layers such as pySerial, Modbus, OpenPLC runtime, MQTT, and OPC UA are intentionally on hold while Phase 1 is polished for public learning.

## What You Will Learn

- PLC scan cycle: read inputs, solve logic, write outputs.
- Ladder basics: contacts, coils, run latch, timers, interlocks.
- Safe traffic phases: green, yellow, all-red.
- Industrial inputs: start, stop, pedestrian buttons, vehicle sensors, emergency, night mode.
- Browser HMI basics: status bar, I/O address tables, timer/register tables, rung monitor, field view, alarms, and event log.
- Industrial realism basics: Omron/Siemens examples, analog signals, VFD motor control, NPN/PNP sensors, and troubleshooting.
- Oil-palm factory basics: FFB to CPO process flow, WECON/PAC/Raspberry Pi/Arduino stations, IIoT, edge AI, and safety/regulatory awareness.
- Plant operation modes: manual, semi-auto, auto, conveyor handling, and Ladder-style process control.
- Reliable PLC programming method: flowcharts, LAD structure, ST/FBD/SFC comparisons, and case-study implementation choices.
- Machinery safety learning path: risk-assessment qualification meaning, certification options, timing, cost ranges, and deliverables.

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
3. Open `http://127.0.0.1:8733/static/how-it-works.html` for scenario walkthroughs and ladder diagrams.
4. Open `http://127.0.0.1:8733/static/industrial-situations.html` for realistic PLC brand, analog, VFD, and sensor troubleshooting situations.
5. Open `http://127.0.0.1:8733/static/oil-palm-industrial-environment.html` for a factory-scale oil-palm process, conveyor handling, operating modes, LAD examples, and IIoT training module.
6. Open `http://127.0.0.1:8733/static/oil-palm-control-stack-analysis.html` for WECON, PAC, Raspberry Pi industrial, and Arduino Opta/Portenta comparisons.
7. Open `http://127.0.0.1:8733/static/plc-programming-methods.html` for reliable PLC programming workflow, flowcharts, language comparisons, and case studies.
8. Open `http://127.0.0.1:8733/static/risk-assessment-certification.html` for machinery risk-assessment certification paths and budget ranges.
9. Press `START`.
10. Watch the top status bar, I/O rack, timers, registers, rungs, outputs, and event log.
11. Toggle vehicle sensors, pedestrian requests, emergency, night mode.
12. Read `plc_engine.py` slowly from top to bottom.
13. Compare code logic to Ladder concepts in the guide.
