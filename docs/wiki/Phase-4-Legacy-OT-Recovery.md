# Phase 4 Legacy OT Recovery

Phase 4 is about obsolete industrial equipment that still matters to production.

Typical situation:

- The PLC is obsolete.
- The HMI computer runs Windows XP or Windows 7.
- The installer is missing.
- The license dongle or activation is gone.
- The OEM may no longer support the machine.
- Production says the machine cannot stop.

## Teaching Position

This is authorized recovery and safe modernization training, not offensive hacking or license bypassing.

The Phase 4 demo is simulated-first and read-only:

- Virtual legacy register map.
- Localhost-only bridge.
- SQLite evidence storage.
- No real PLC connection.
- No write, force, reset, or command endpoint.

## Recovery Workflow

1. Inventory PLC, HMI, I/O, cables, firmware, drawings, and software.
2. Backup/image the old PC and preserve authorized PLC/HMI files.
3. Isolate XP/7 and legacy PLC assets behind OT boundaries.
4. Observe read-only registers and compare with real machine behavior.
5. Reconstruct logic understanding from Ladder, HMI, alarms, and maintenance feedback.
6. Bridge safe data to historian/dashboard.
7. Migrate later using FAT, SAT, cutover, and rollback planning.

## Simulated Legacy Station

The current case study uses an obsolete oil-palm screw press station.

Signals include:

- Press run feedback.
- Fault bit.
- Motor current.
- Press load.
- Vibration estimate.
- Output flow.
- Steam/sterilizer context.
- HMI heartbeat.
- Communication quality.
- Downtime and alarm counters.

## RS-232 Lesson

The RS-232 section uses a simulated pySerial-style loopback concept:

- Baud rate.
- Parity.
- Stop bits.
- Timeout.
- Request frame.
- Response frame.

Real COM-port work is a future lab and must be authorized, isolated, and read-only first.
