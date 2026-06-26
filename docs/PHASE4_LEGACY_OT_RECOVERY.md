# Phase 4 Overview: Legacy OT Recovery And Read-Only Data Bridging

## Purpose

Phase 4 teaches a real manufacturing problem: profitable machines often depend on obsolete PLCs, Windows XP/7 HMI PCs, missing engineering software, missing license dongles, lost backups, unsupported OEM systems, and fragile production schedules.

The professional goal is authorized recovery and safe modernization, not offensive hacking or license bypassing. Phase 4 keeps the existing machine in control while a read-only bridge collects evidence for maintenance, management, and future migration planning.

## Boundary

Included:

- Simulated obsolete screw press station from the oil-palm case study.
- Virtual Modbus TCP-style register map on `127.0.0.1`.
- Read-only Python collector behavior.
- SQLite demo storage under `local_data/phase4_legacy.sqlite3`.
- Simulated RS-232 / pySerial lesson using loop-style framing.
- XP/7 risk isolation and OT/IT boundary guidance.

Excluded:

- No real PLC connection.
- No write/force/reset commands to legacy equipment.
- No license bypassing.
- No public network exposure.
- No claim of certified industrial cybersecurity, safety, or migration sign-off.

## Teaching Workflow

1. Inventory the PLC, HMI, I/O, firmware, software, cables, drawings, and operator knowledge.
2. Backup/image the old PC and preserve authorized PLC/HMI files.
3. Isolate XP/7 and the legacy PLC behind OT firewall/VLAN boundaries.
4. Observe read-only registers/signals and compare them with machine behavior.
5. Reconstruct understanding from Ladder, HMI screens, alarms, I/O, and maintenance feedback.
6. Bridge safe data to a historian/dashboard without commanding the old controller.
7. Migrate later with HMI rebuild, PLC/PAC selection, FAT, SAT, cutover, and rollback.

## Phase 5 Direction

Phase 5 should teach modernization and migration strategy: rebuild HMI, reconstruct or rewrite control logic, select PLC/PAC hardware, perform FAT/SAT, plan cutover, verify rollback, and harden the final OT network.
