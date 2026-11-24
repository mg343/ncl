# Handoff: NCL RC car

The previous student left no handoff documentation (no passwords, 3D print files, or notes), and the car sat idle for most of a year. This file exists so that never happens again. Keep it current; anyone taking over the car should be able to run it from this file alone.

Status: scaffold. To be filled during the hardware audit (see `hardware/audit.md`). Everything marked TBD is unknown until checked on the car.

11/24: partly filled in from the pi 4 backup (old code + configs)

## Overview

- 4 wheel diff drive rover (skid steer). NO steering servo, turns by spinning left/right wheels at diff speeds
- ROS 2 + ros2_control on the pi 4 (bottom pi)
- old code is in 2 github repos (also on the pi 4 under the old user):
  - `github.com/onurcalisir27/LearningAdaptive` - newer (aug-sep 2025), has a decent README. rover_hardware (pi 4 drivers), rover_control (controllers, self tuning regulator, nav2 stuff), rover_sim (gazebo)
  - `github.com/onurcalisir27/Beigi_ControlsResearch` - older (feb-jul 2025), branch `Autonomous-Vehicle`. hw tests, real_ws / sim_ws, object tracker
- theres a self tuning regulator (`rover_control/src/self_tuning_regulator.cpp`, RLS w/ forgetting factor) + `matlab/LSTR.m` but only ever ran on a sim inverted pendulum, never the car
- backup of the pi 4 home folder is local in `backup/rpi4/` (git ignored)

## Hardware inventory

| Part | Model | Connection | Status |
|---|---|---|---|
| Raspberry Pi 4 | TBD | eth to modem | works, main computer |
| Raspberry Pi 5 | TBD | TBD | not using (see below) |
| Depth camera | OAK-D Lite (from code) | usb | TBD |
| Time-of-flight sensor | TBD | TBD | TBD |
| IMU (unconfirmed) | MPU6050 (from code) | i2c | in the code, not checked on car |
| Steering servo | none | - | car is diff drive, no servo |
| Drive motor / ESC | 4x DC w/ encoders + h-bridge, models TBD | gpio (pins below), same side motors wired together | TBD |
| Battery | some ups board, TBD (old `battery/ups.py`) | TBD | TBD |

Measured: wheelbase TBD, track width TBD, mass TBD.

numbers from old config, need to measure:
- wheel separation 0.24 m (comment next to it says 125 mm?? one of these is wrong)
- wheel radius 32.5 mm (encoder config says wheel diameter 0.205, doesnt match either)

## Wiring and power

- basic setup: eth cable from the bottom pi (pi 4) port to the modem
- pi 4 lights: solid red = power ok, green flashing = sd card activity
- pi 5 light (just one): green = running, solid red = powered but off/standby
- TBD: photos, how the pi 4 gets power

pins (BCM), from `LearningAdaptive/src/rover_hardware/description/ros2_control.xacro`, havent checked on the car:

| what | pins (fwd, rev, en/pwm) | notes |
|---|---|---|
| left motor | 16, 20, 12 | pwm 1700 Hz |
| right motor | 6, 5, 13 | pwm 1700 Hz |
| left front enc | 17, 4 | 1920 counts/rev |
| left back enc | 22, 27 | |
| right front enc | 23, 24 | |
| right back enc | 25, 8 | |

careful: `DiffDrivePi.cpp` has a different default pin map (encoders swapped L/R). the xacro one is whats actually loaded

## Pi 4 setup

- "bottom" pi
- old user: `beigi-raspi4`
- new user (11/24): `columbiacontrols`
- ip `192.168.1.11`
  ```
  ssh columbiacontrols@192.168.1.11
  ```
- old code: `~/Projects/Beigi_ControlsResearch`, `~/LearningAdaptive` (both have build/ install/ so they got built on here)
- motors go through `pigpio`, need the `pigpiod` daemon running
- control loop 30 Hz, diff_drive_controller, PID per wheel (kp 4.5, ki ~0.95, kd 0.1)
- limits 1.0 m/s, 4 rad/s, accel 0.4 m/s^2. wheels wont move under ~0.38 m/s
- `cmd_vel` timeout 0.5 s -> car stops if commands stop (kind of a watchdog already)
- EKF = wheel odom + imu yaw rate. RTAB-Map for SLAM (old map `rtabmap.db` in old home)
- TBD: OS version, ROS distro, services/cron, does pigpiod start on boot

## Pi 5 setup

- 11/24 decided not to use it. nothing on it we need, last guy only used the 4, and it doesnt get enough power on the car anyway. beigi agrees
- didnt back it up
- just in case: "top" pi, hostname `raspi5`, ubuntu 24.04.3 (aarch64), user `columbiacontrols`, was at `192.168.1.12`

## Pi 4 ↔ Pi 5 network

TBD. Planned: gigabit Ethernet crossover, Pi 5 sends steering/speed commands to Pi 4, watchdog on Pi 4 stops the car if commands stop. Record IPs, ports, message format.

- not doing this anymore since no pi 5

## Credentials and access

Never write the passwords themselves in this file or the repo.

- user `columbiacontrols` (pi 4, also exists on pi 5). pw = same as the ControlSystems lab wifi, ask beigi / mihir
- old pi 4 user `beigi-raspi4` is still there

## How to run the car

1. connect to modem (eth from pi 4 to modem), power on. solid red on pi 4 = ok
2. ssh in:
   ```
   ssh columbiacontrols@192.168.1.11
   ```
3. from the old README, havent tried yet:
   ```
   sudo pigpiod
   cd ~/LearningAdaptive && source install/setup.bash
   ros2 launch rover_hardware robot_launch.py   # motors + sensors + cam
   ```
   then teleop (`scripts/teleop.sh` in the old repo)
4. e-stop TBD. for now kill the launch / stop sending cmd_vel and it stops within 0.5 s

## Known issues

TBD.
