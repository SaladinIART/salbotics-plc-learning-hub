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

