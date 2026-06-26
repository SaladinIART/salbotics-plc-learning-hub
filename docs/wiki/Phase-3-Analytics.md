# Phase 3 Analytics

Phase 3 teaches why dashboards matter to management and how plant data moves from OT to IT and business layers.

## What Runs Today

- Local FastAPI app.
- Simulated oil-palm line data.
- SQLite historian under `local_data/`.
- One sample every 2 seconds represents 1 minute of simulated plant time.
- Management KPI cards, trend charts, events, station states, and screw press deep dive.

## Why Dashboard Matters

Ladder logic answers: **what is the PLC logic doing?**

HMI answers: **what should the operator do now?**

SCADA answers: **what is the plant doing over time?**

Analytics answers: **what losses, repeated faults, bottlenecks, and performance patterns can we learn?**

Management does not want to read PLC rungs every morning. A dashboard summarizes production, downtime, OER, alarm frequency, tank level, energy/steam indicators, and station health.

## OT, IT, MES, ERP

- **OT**: PLC, VFD, HMI, SCADA, sensors, actuators, historian.
- **IT**: server, database, network, backup, dashboard access.
- **MES**: shift, batch, production order, downtime reason, performance tracking.
- **ERP**: costing, inventory, purchasing, sales, management reporting.

## Boundary

Phase 3 is still simulated. Real Modbus TCP, OPC UA, MQTT, ERP, MES, and pySerial/RS-232 connections come after this local analytics foundation.
