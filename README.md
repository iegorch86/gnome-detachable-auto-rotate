# Dell Latitude 7210 2-in-1 Auto Rotation Fix

Small workaround for Dell Latitude 7210 2-in-1 running Fedora GNOME Wayland.

Problem was simple:

If tablet boots with keyboard attached everything works.
Detach keyboard later -> auto rotation works.

If tablet boots without keyboard attached, GNOME correctly enters tablet mode.

The "Auto Rotation" toggle appears in Quick Settings and is enabled by default.

However, display rotation never happens even though:

- monitor-sensor reports orientation changes
- iio-sensor-proxy works
- accelerometer works
- touch screen works
- Auto Rotation toggle is enabled

So tablet mode itself is not the problem.

Something between accelerometer events and GNOME display rotation does not work correctly on this hardware.

Instead trying to fake tablet mode, this project simply listens to accelerometer events and rotates display directly using `gdctl`.

For me this ended up much more reliable than trying to emulate hardware switch.

---

## Tested on

Hardware

- Dell Latitude 7210 2-in-1
- detachable keyboard
- built-in accelerometer

Software

- Fedora 44 Workstation
- GNOME 50
- Wayland
- Python 3

Probably should work on newer Fedora/GNOME versions too as long as `gdctl` is available.

---

## How it works

The script starts as user service after login.

It does two jobs:

- watches accelerometer using `monitor-sensor`
- checks if keyboard base is attached

If keyboard is attached:

- display stays in normal landscape

If keyboard is detached:

- display follows accelerometer
- touch screen rotates correctly too

No kernel modules.
No fake input devices.
No tablet mode emulation.

Just using components already available in GNOME.

---

## Files

```
dell-auto-rotate.py
```

Main Python script.

```
dell-auto-rotate.service
```

systemd user service.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR-USERNAME/dell-7210-auto-rotate.git
cd dell-7210-auto-rotate
```

Run installer:
```bash
./install.sh
```
The installer will:

 - copy dell-auto-rotate.py to ~/.local/bin/
 - copy the systemd user service to ~/.config/systemd/user/
 - reload systemd
 - enable and start the service

Check status:
```bash
systemctl --user status dell-auto-rotate.service
```
Live logs:
```bash
journalctl --user -u dell-auto-rotate.service -f
```
--- 

## Manual installation

Copy files

```
~/.local/bin/dell-auto-rotate.py
~/.config/systemd/user/dell-auto-rotate.service
```

Reload systemd

```bash
systemctl --user daemon-reload
systemctl --user enable --now dell-auto-rotate.service
```

Check status

```bash
systemctl --user status dell-auto-rotate.service
```

Live logs

```bash
journalctl --user -u dell-auto-rotate.service -f
```

---

## Configuration

Inside Python script you can change:

```python
CONNECTOR = "eDP-1"
SCALE = "1.25"
TOUCHPAD_NAME = "Alps Alps Touchpad"
```

Most people only need to change connector name if display is different.

---

## Why not use GNOME auto rotation?

Normally GNOME already does this.

Unfortunately on my Dell 7210, booting without keyboard attached never exposes Intel HID tablet switch.

Accelerometer still works.

GNOME just never rotates.

This script bypasses that part completely.

---

## Future

Maybe one day GNOME or kernel will fix this.

If that happens this project is no longer needed.

Until then this workaround works really well.

---

## Story

I spent about 6 hours trying different ideas.

Tried virtual tablet mode switches, uinput devices, and emulating SW_TABLET_MODE. Everything looked correct in libinput, but GNOME still refused to rotate after booting detached.

Finally I stopped trying to convince GNOME that it was in tablet mode and instead rotated the display directly with gdctl.

Sometimes the simplest solution is the right one.

---

## License

MIT
