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

| Simulator Name | PLC Type | Ladder Meaning |
| --- | --- | --- |
| START | Input | Start contact |
| STOP | Input | Stop contact |
| PED_NS | Input | Pedestrian request contact |
| PED_EW | Input | Pedestrian request contact |
| VEHICLE_NS | Input | Vehicle sensor contact |
| VEHICLE_EW | Input | Vehicle sensor contact |
| EMERGENCY | Input | Emergency contact |
| NIGHT_MODE | Input | Mode selector contact |
| NS_RED | Output | Red lamp coil |
| NS_YELLOW | Output | Yellow lamp coil |
| NS_GREEN | Output | Green lamp coil |
| EW_RED | Output | Red lamp coil |
| EW_YELLOW | Output | Yellow lamp coil |
| EW_GREEN | Output | Green lamp coil |

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

| Simulator Timer | OpenPLC Timer Idea |
| --- | --- |
| green_base_s | TON for minimum green |
| green_max_s | TON for maximum green |
| yellow_s | TON for yellow phase |
| all_red_s | TON for all-red clearance |
| flash_half_period_s | repeating timer / pulse bit |

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

