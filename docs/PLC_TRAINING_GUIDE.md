# PLC Training Guide

This guide assumes you are new to PLCs and programming.

## 1. What A PLC Does

A PLC is an industrial computer. It repeats this loop:

1. Read inputs.
2. Solve logic.
3. Write outputs.
4. Repeat.

This is called the scan cycle.

In this project, the scan runs every `100ms`.

## 2. Our Training PLC

Mental model:

```text
AutomationDirect CLICK C0-00DR-D
```

Why this PLC model:

- Small enough for beginner training.
- 8 digital inputs fit our simulator.
- 6 relay outputs fit two traffic directions.
- Built-in serial communication matches future RS-232 / Modbus lessons.

## 3. Inputs

Inputs are signals coming into the PLC.

```text
START       start pushbutton
STOP        stop pushbutton
PED_NS      pedestrian request for NS phase
PED_EW      pedestrian request for EW phase
VEHICLE_NS  vehicle sensor on north/south road
VEHICLE_EW  vehicle sensor on east/west road
EMERGENCY   emergency override
NIGHT_MODE  night red-flash selector
```

In Ladder, inputs are usually drawn as contacts.

## 4. Outputs

Outputs are devices controlled by the PLC.

```text
NS_RED
NS_YELLOW
NS_GREEN
EW_RED
EW_YELLOW
EW_GREEN
```

In Ladder, outputs are usually drawn as coils.

## 5. Traffic Phases

Normal auto sequence:

```text
NS_GREEN
NS_YELLOW
ALL_RED_TO_EW
EW_GREEN
EW_YELLOW
ALL_RED_TO_NS
repeat
```

All-red phases matter. They create a short safety gap before traffic changes direction.

## 6. Ladder Concepts In This Project

### Contact

Contact means input condition.

Example:

```text
If START is ON
```

### Coil

Coil means output or internal bit.

Example:

```text
Turn on RUN_LATCH
```

### Seal-In / Latch

A start button is usually momentary. PLC logic remembers that the machine is running by sealing in a run bit.

In this project:

```text
RUN_LATCH = controller is running in auto mode
```

### Timer

Timer waits for a duration before logic moves forward.

In this project:

```text
green base = 5s
green max  = 9s
yellow     = 2s
all-red    = 1s
```

### Interlock

Interlock prevents unsafe combinations.

Most important rule:

```text
NS_GREEN and EW_GREEN must never be ON together.
```

## 7. Industrial Modes

### Auto Cycle

Press `START`. The PLC moves through normal phases.

### Stop

Press `STOP`. The PLC returns to all-red.

### Pedestrian Request

Toggle `PED_NS` or `PED_EW`.

The request latches. It clears when the matching green phase services it.

### Vehicle Sensor

Toggle `VEHICLE_NS` or `VEHICLE_EW`.

If a vehicle is waiting during that direction's green phase, the green extends from base time to max time.

### Emergency

Toggle `EMERGENCY`.

All greens turn off. Both red outputs turn on.

### Night Mode

Toggle `NIGHT_MODE`.

Both red lamps flash. Normal green/yellow sequence pauses.

### Manual Step

Press `MANUAL STEP`.

The PLC advances one safe phase at a time. It still uses all-red gaps and never allows both greens.

### Fault

Turn `START` and `STOP` on at the same time.

The simulator treats this as a stuck-pushbutton fault. Clear one input, then press `RESET FAULT`.

## 8. How To Study The Code

Read in this order:

1. `README.md`
2. `plc_engine.py`
3. `main.py`
4. `static/app.js`
5. `static/index.html`
6. `static/styles.css`

Focus on one concept at a time:

```text
inputs -> registers -> phase -> outputs -> browser display
```

Do not memorize everything. Trace one scan cycle slowly.

