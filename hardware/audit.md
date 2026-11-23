# Car access and audit checklist

Planned for Tue 11/24, once Professor Beigi has set up the car account. Results go in `docs/HANDOFF.md`.

## 0. Before Tuesday (Mon 11/23, in lab)

- [ ] Measure wheelbase, track width, mass; update `L` and `M` in `sim/figure8_baseline.py`
- [ ] Photograph car and electronics
- [ ] List visible parts
- [ ] Start `docs/HANDOFF.md`

## 1. Back up first

- [ ] Image the SD card (`dd`) or copy `/home` and project folders
- [ ] Note where the backup is stored

## 2. Hardware

- [ ] `lsusb`
- [ ] `i2cdetect -y 1`
- [ ] `v4l2-ctl --list-devices`

## 3. Software

- [ ] `pip list`
- [ ] `ls ~/`
- [ ] `printenv | grep ROS`
- [ ] `crontab -l`
- [ ] `systemctl list-units --type=service`

## 4. Record

- [ ] Everything above recorded in `docs/HANDOFF.md`
- [ ] Inventory sent to Beigi and Venkat the same day

Do the above on both the Pi 4 and the Pi 5.
