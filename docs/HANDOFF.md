# Handoff: NCL RC car

The previous student left no handoff documentation (no passwords, 3D print files, or notes), and the car sat idle for most of a year. This file exists so that never happens again. Keep it current; anyone taking over the car should be able to run it from this file alone.

Status: scaffold. To be filled during the hardware audit (see `hardware/audit.md`). Everything marked TBD is unknown until checked on the car.

## Overview

TBD. What the car is, what it's used for, current state.

## Hardware inventory

| Part | Model | Connection | Status |
|---|---|---|---|
| Raspberry Pi 4 | TBD | TBD | TBD |
| Raspberry Pi 5 | TBD | TBD | TBD |
| Depth camera | TBD | TBD | TBD |
| Time-of-flight sensor | TBD | TBD | TBD |
| IMU (unconfirmed) | TBD | TBD | TBD |
| Steering servo | TBD | TBD | TBD |
| Drive motor / ESC | TBD | TBD | TBD |
| Battery | TBD | TBD | TBD |

Measured: wheelbase TBD, track width TBD, mass TBD.

## Wiring and power

TBD. Photos, which pins drive the servo and ESC, how each Pi is powered.

## Pi 4 setup

TBD. OS, hostname, user, installed packages, services, where the code lives.

## Pi 5 setup

TBD. Same as above.

## Pi 4 ↔ Pi 5 network

TBD. Planned: gigabit Ethernet crossover, Pi 5 sends steering/speed commands to Pi 4, watchdog on Pi 4 stops the car if commands stop. Record IPs, ports, message format.

## Credentials and access

TBD. Where the credentials are stored and who holds them. Never write the passwords themselves in this file or the repo.

## How to run the car

TBD. Power-on order, login, start commands, emergency stop.

## Known issues

TBD.
