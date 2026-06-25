# OpenPLC Mapping Notes

This project starts with a custom simulator so the logic is easier to see.

Later, the same idea can be rebuilt in OpenPLC using Ladder Diagram.

## Suggested OpenPLC Learning Path

1. Recreate the I/O names.
2. Build a RUN latch rung.
3. Add timers for each phase.
4. Add output coils.
5. Add interlocks.
6. Add pedestrian request latches.
7. Add emergency and night mode overrides.

## I/O Mapping

Use the trainer address table as the first bridge to OpenPLC. The exact OpenPLC address syntax can change by target runtime, but the mental model is stable: inputs are contacts and outputs are coils.

| Simulator Name | Trainer Address | PLC Type | Ladder Meaning |
| --- | --- | --- | --- |
| START | I0.0 | Input | Start contact |
| STOP | I0.1 | Input | Stop contact |
| PED_NS | I0.2 | Input | Pedestrian request contact |
| PED_EW | I0.3 | Input | Pedestrian request contact |
| VEHICLE_NS | I0.4 | Input | Vehicle sensor contact |
| VEHICLE_EW | I0.5 | Input | Vehicle sensor contact |
| EMERGENCY | I0.6 | Input | Emergency contact |
| NIGHT_MODE | I0.7 | Input | Mode selector contact |
| NS_RED | Q0.0 | Output | Red lamp coil |
| NS_YELLOW | Q0.1 | Output | Yellow lamp coil |
| NS_GREEN | Q0.2 | Output | Green lamp coil |
| EW_RED | Q0.3 | Output | Red lamp coil |
| EW_YELLOW | Q0.4 | Output | Yellow lamp coil |
| EW_GREEN | Q0.5 | Output | Green lamp coil |

## Internal Bits

| Simulator Register | OpenPLC Equivalent |
| --- | --- |
| RUN_LATCH | Internal coil / memory bit |
| MANUAL_MODE | Internal coil / memory bit |
| FAULT_ACTIVE | Internal coil / memory bit |
| PED_NS_REQUEST | Internal latch bit |
| PED_EW_REQUEST | Internal latch bit |
| VEHICLE_EXTENSION_ACTIVE | Internal status bit |
| NIGHT_FLASH_ON | Internal flasher bit |

## Timers

The trainer exposes timer rows as `T0` through `T6`. In OpenPLC, recreate these with TON timers or equivalent Ladder timer blocks.

| Trainer Address | Simulator Timer | OpenPLC Timer Idea |
| --- | --- | --- |
| T0 | NS_GREEN | TON for north/south green |
| T1 | NS_YELLOW | TON for north/south yellow |
| T2 | ALL_RED_1 | TON for clearance before east/west green |
| T3 | EW_GREEN | TON for east/west green |
| T4 | EW_YELLOW | TON for east/west yellow |
| T5 | ALL_RED_2 | TON for clearance before north/south green |
| T6 | NIGHT_FLASH | repeating timer / pulse bit |

## Monitor Registers

The trainer also exposes register rows as `R0` through `R4`. These are for learning and diagnostics.

| Trainer Address | Meaning |
| --- | --- |
| R0 | Current phase step |
| R1 | Current system mode code |
| R2 | Bitmask of pending pedestrian requests |
| R3 | Bitmask of active vehicle demand |
| R4 | Active alarm count |

## Future pySerial Lesson

Do not add serial first. First learn logic.

Future layer:

```text
PLC simulator state -> serial message -> pySerial reader -> FastAPI -> browser HMI
```

Possible message shape:

```text
PHASE=NS_GREEN;NS_RED=0;NS_YELLOW=0;NS_GREEN=1;EW_RED=1;EW_YELLOW=0;EW_GREEN=0
```

After that, replace the simulator with a real PLC or OpenPLC runtime.
