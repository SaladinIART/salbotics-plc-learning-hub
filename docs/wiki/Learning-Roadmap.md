# Learning Roadmap

## Phase 1: PLC And HMI Basics

Goal: learn how PLC scan-cycle logic becomes a visible browser HMI.

Topics:

- Inputs, outputs, timers, registers, alarms.
- Ladder concepts: contacts, coils, latches, interlocks, timer done bits.
- 4-way traffic-light trainer.
- Industrial panel reading.
- Safe all-red and emergency behavior.

## Phase 2: Communications And SCADA

Goal: understand how PLCs, HMIs, SCADA, plant networks, and local servers fit together.

Topics:

- RS-232, RS-485, Ethernet.
- Modbus RTU/TCP, OPC UA, MQTT/Sparkplug.
- Localhost, `127.0.0.1`, LAN IP, ports, firewall basics.
- HMI vs Ladder vs SCADA.
- Oil-palm SCADA screen design.

## Phase 3: Local Data Collection And Analytics

Goal: see simulated plant data become a historian, dashboard, and management summary.

Topics:

- SQLite historian.
- Simulated oil-palm production samples.
- FFB, CPO, OER, downtime, alarms, tank level, and screw press data.
- OT, IT, MES, ERP concepts.
- Why management dashboards matter.

## Future Phase 4 Suggestion

Recommended Phase 4 topic: **real industrial connectivity, cybersecurity, and deployment readiness**.

Possible modules:

- Virtual Modbus TCP first.
- OPC UA and MQTT after tags/registers are understood.
- pySerial/RS-232 for legacy machinery.
- Authentication and role-based screens.
- Network segmentation and firewall practice.
- Backup, restore, audit log, and release packaging.
- Data quality checks before analytics decisions.
