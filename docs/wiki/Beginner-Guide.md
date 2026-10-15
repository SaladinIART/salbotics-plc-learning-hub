# Beginner Guide

New to automation? This page of the learning hub explains PLCs in plain language first, then
gives the technical name beside each idea.

- Live: https://salbotics.uk/salbotics-plc-learning-hub/
- Source: `static/beginner-guide.html`

![Beginner guide start page](https://raw.githubusercontent.com/SaladinIART/salbotics-plc-learning-hub/main/docs/screenshots/beginner-guide.png)

## What It Covers

| Section | Everyday example | Technical idea |
|---|---|---|
| The 3-step loop | Look, think, step | Input scan, logic solve, output update = scan cycle (0.1 s in the trainer) |
| Inputs and outputs | Buttons, beams, motors | Digital versus analog; sensors versus actuators |
| Washing machine | Fill, wash, drain, spin | Sequence / state machine, timer, interlock |
| Lift | The floor button stays lit | Latch (seal-in), door interlock, limit switch, priority |
| Automatic gate | Beam blocked, gate reopens | High-priority safety input |
| Escalator | Runs when someone arrives | Run timer, fail-safe emergency stop |
| Rice cooker | Cook, then keep warm | Setpoint, on/off control, hysteresis |
| Car-park barrier | Never lowers on a car | Inductive loop sensor, interlock, timer |
| Key words | - | Glossary in plain language |
| Use the trainer | Traffic light | START, pedestrian latch, EMERGENCY, START+STOP fault |

Each example ends with a collapsible **Try it** question and answer. Two diagrams show the scan
loop and the washing-machine sequence; on phones they switch to a stacked layout.

## How To Use It

1. Read one example at a time; answer its Try it question before opening the answer.
2. Learn the plain-language idea first, then the technical term.
3. Finish with "Now use the trainer" and try the steps in the local simulator.

## Boundary

The examples are simplified to teach ideas. Real lifts, gates, escalators and barriers use
certified safety devices and follow national rules. This guide is not safety or design guidance.
