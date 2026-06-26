# Phase 2/3 Overview: Communications, SCADA, Local Server, And Analytics

## Purpose
Phase 2 teaches how PLCs, HMI screens, SCADA, plant networks, and local servers fit together before the learner touches real protocol drivers or hardware.

The goal is to prevent beginner paralysis. A newcomer should not feel they must understand Ladder, Ethernet, Modbus, Python, databases, and SCADA all at once. Phase 2 separates the learning into three paths:

- Operator path: read the plant overview, station status, alarms, trends, and manual/semi-auto/auto state.
- Technician path: trace I/O, VFDs, sensors, network health, communication faults, and maintenance clues.
- Developer path: understand Browser -> FastAPI -> simulator state now, then Python polling -> local historian -> analytics in Phase 3.

## Phase 2 Boundary
Phase 2 remains simulated and beginner-safe.

Included:

- Industrial communications notes for RS-232, RS-485, Ethernet, Modbus RTU/TCP, OPC UA, MQTT, and Sparkplug.
- Computer network notes for `127.0.0.1`, localhost, LAN IP, ports, firewall prompts, and safe local hosting.
- Oil-palm SCADA/HMI design examples using plant overview, station, alarm, trend, maintenance, and network screens.
- Simulated screen data only.

Excluded until Phase 3:

- No real PLC connection.
- No pySerial runtime.
- No Modbus driver runtime.
- No MQTT broker runtime.
- No OPC UA server/client runtime.
- No local database or historian runtime.
- No public network exposure of live HMI controls.

## Teaching Angle
Ladder shows what the PLC logic is doing. HMI shows what the operator should do now. SCADA shows what the whole plant is doing over time. Analytics shows patterns, losses, faults, and production performance.

Oil-palm mill examples should keep using reception, sterilizer, thresher, digester, screw press, clarification, tank farm, boiler, POME, conveyors, pumps, VFDs, alarms, trends, and station handshakes.

## Phase 3 Direction
Phase 3 starts with a simulated local data pipeline because learners should understand why historians and dashboards matter before protocol runtime becomes the hard part.

Recommended sequence:

1. Simulated oil-palm collector.
2. SQLite local historian.
3. Management dashboard with FFB, CPO, OER, downtime, alarms, station states, and trends.
4. OT, IT, MES, and ERP beginner architecture lesson.
5. Phase 4 legacy OT recovery with a read-only virtual register bridge.
6. Simulated RS-232 / pySerial lesson.
7. Virtual Modbus TCP and real adapter labs only after learners understand read-only boundaries.
8. OPC UA/MQTT after students understand tags and polling.

## Phase 4 Direction
Phase 4 teaches obsolete PLC and Windows XP/7 HMI situations through a simulated screw press legacy station. It introduces safe recovery habits: inventory, backup/image, isolate, observe, reconstruct, bridge, and migrate later.

The Phase 4 runtime remains local and simulated. It exposes `/api/legacy/*` read-only endpoints, SQLite demo storage, and a virtual Modbus TCP-style register map. It intentionally does not expose write, force, reset, or real machine command endpoints.

## Success Criteria
- A beginner can choose a path without reading every page.
- A technician can trace PLC -> HMI -> SCADA -> local server.
- A developer can explain why Phase 3 starts with virtual Modbus TCP.
- The project remains safe by default on localhost.
- Any LAN access is clearly taught as a security and training topic, not the default operating mode.
