# Industrial UI Revision Target

This revision upgrades the trainer from a functional browser dashboard into a stronger industrial/SCADA-style PLC training panel.

## Target

- Keep the app beginner-readable.
- Make the screen feel like a control-room HMI / PLC monitor.
- Use the generated concept as visual direction, not a pixel-perfect contract.
- Preserve working PLC logic and existing API fields.
- Add PLC-style metadata only where it teaches real control-system concepts.

## Current Gap

The first implementation works, but it looks like a clean web app:

- I/O rows are card-like, not rack/table-like.
- Header lacks PLC-connected, scan-time, cycle-count, and mode indicators.
- Timers/registers are split into simple cards instead of diagnostic tables.
- Ladder rows read like status cards instead of rung monitor rows.
- Junction view is schematic but not yet SCADA-like.
- Event log is functional but not industrial enough.

## Design Direction

- Dark outer shell with compact light data surfaces.
- Strong section bars and table grids.
- PLC address language: `I0.0`, `Q0.0`, `T0`, `R0`.
- Semantic state colors:
  - green = running / energized / healthy
  - amber = warning / transition / yellow lamp
  - red = emergency / alarm / fault
  - gray = stopped / inactive
- Code-native junction view. No raster assets.

## QA Checklist

Each checkpoint should pass:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Visual checkpoints should also verify:

- page loads at `http://127.0.0.1:8733`
- no blank screen
- no browser console errors
- START changes state visibly
- EMERGENCY forces all-red visibly
- desktop layout has no clipping or overlap
- mobile layout remains readable

## Checkpoint Rule

Each checkpoint must be committed before the next checkpoint starts.

## CP20 Final QA Notes

Date: 2026-06-25.

Rendered QA used `http://127.0.0.1:8740/` because that was the current-code test server during the Codex run. The committed launcher and docs still use `127.0.0.1:8733`.

Verification completed:

- `.\.venv\Scripts\python.exe -m pytest -q` passed: 17 tests.
- Browser page identity passed: title `PLC Traffic-Light Trainer`.
- Blank-screen check passed: app shell, I/O rack, ladder monitor, and junction rendered.
- Framework overlay check passed: no framework error overlay.
- Console health passed: no browser errors or warnings.
- Interaction check passed:
  - `STOP` moved the controller to stopped/all-red.
  - `START` returned the controller to auto mode.
  - `EMERGENCY` forced emergency all-red, turned both red directions on, turned both greens off, and displayed an active alarm.
- Desktop viewport `1440x900` passed: no page horizontal overflow, no topbar overflow, no control text clipping, no I/O tag clipping.
- Mobile viewport `390x844` passed: no page horizontal overflow; wide I/O tables scroll inside the rack so PLC tag names stay readable.

Concept comparison result:

- Matches target mood: dark SCADA shell, compact light data surfaces, section headers, PLC address rows, timer/register tables, ladder-style rung monitor, field controls, alarm state colors, and event/alarm area.
- Intentional deviation: the junction is code-native instead of raster/photorealistic, per the project assumption.
- Intentional deviation: the trainer uses the CLICK-style 8 input / 6 output teaching model, so it has fewer I/O points than the broader concept image.
- Intentional deviation: scan time displays the simulator interval (`100ms`) rather than a measured hardware scan time.
- Intentional deviation: manual override controls are visible disabled training placeholders until backend override logic is added.
