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
Phase 3 starts with virtual Modbus TCP because it teaches PLC registers/tags and Python polling without requiring real hardware.

Recommended sequence:

1. Virtual Modbus TCP simulator.
2. Python collector polling registers.
3. Local data storage.
4. Local historian/trend page.
5. Production counters, alarm statistics, and simple analytics.
6. OPC UA/MQTT after students understand tags and polling.
7. pySerial/RS-232 later as a focused legacy machinery track.

## Success Criteria
- A beginner can choose a path without reading every page.
- A technician can trace PLC -> HMI -> SCADA -> local server.
- A developer can explain why Phase 3 starts with virtual Modbus TCP.
- The project remains safe by default on localhost.
- Any LAN access is clearly taught as a security and training topic, not the default operating mode.
