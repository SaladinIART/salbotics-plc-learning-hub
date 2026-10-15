# Learning Roadmap

## Start Here: Beginner Guide

Goal: understand what a PLC does before any wiring, protocols or software.

Topics:

- The read-decide-act scan loop.
- Inputs (buttons, sensors) and outputs (motors, valves, lamps); on/off versus analog.
- Sequences and timers (washing machine), latches and interlocks (lift), safety inputs (automatic gate), fail-safe wiring (escalator), setpoint and hysteresis (rice cooker), interlock with a road sensor (car-park barrier).

Read it on the [live site](https://salbotics.uk/salbotics-plc-learning-hub/) or see [Beginner Guide](Beginner-Guide.md).

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

## Phase 4: Legacy OT Recovery And Read-Only Data Bridging

Goal: teach how engineers stabilize and monitor obsolete machines without disturbing production.

Topics:

- Obsolete PLC and Windows XP/7 HMI situations.
- Missing installer, missing license, and lost backup risk.
- Disk image, isolation, inventory, and read-only observation.
- Virtual Modbus TCP-style register map.
- SQLite local bridge evidence.
- Simulated RS-232 / pySerial framing lesson.
- No write, force, reset, or real PLC command endpoint.

## Phase 5: Modernization And Migration Strategy

Goal: replace the risk after the plant understands the current machine.

Topics:

- Rebuild HMI screens.
- Reconstruct Ladder/state logic from extracted diagrams and observed behavior.
- Select PLC/PAC and I/O.
- Perform FAT and SAT.
- Plan cutover and rollback.
- Harden network, users, backup, and release process.
