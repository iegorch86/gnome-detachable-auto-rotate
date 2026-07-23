mkdir -p ~/.local/bin

cat > ~/.local/bin/dell-auto-rotate.py <<'PY'
#!/usr/bin/python3

import glob
import logging
import signal
import subprocess
import threading
import time
from pathlib import Path

CONNECTOR = "eDP-1"
SCALE = "1.25"
TOUCHPAD_NAME = "Alps Alps Touchpad"
POLL_INTERVAL = 1.0

ORIENTATION_TO_TRANSFORM = {
    "normal": "normal",
    "bottom-up": "180",
    "left-up": "90",
    "right-up": "270",
}

running = True
current_orientation = None
current_transform = None
base_attached_previous = None
lock = threading.Lock()


def stop_handler(signum, frame):
    global running
    running = False


def input_device_names():
    names = []

    for path in glob.glob("/sys/class/input/event*/device/name"):
        try:
            names.append(Path(path).read_text().strip())
        except OSError:
            continue

    return names


def keyboard_base_attached():
    return TOUCHPAD_NAME in input_device_names()


def apply_transform(transform):
    global current_transform

    with lock:
        if transform == current_transform:
            return

        command = [
            "gdctl",
            "set",
            "--logical-monitor",
            "--monitor",
            CONNECTOR,
            "--primary",
            "--scale",
            SCALE,
            "--transform",
            transform,
        ]

        logging.info("Applying display transform: %s", transform)

        result = subprocess.run(
            command,
            text=True,
            capture_output=True,
        )

        if result.returncode != 0:
            logging.error(
                "gdctl failed with status %d: %s",
                result.returncode,
                result.stderr.strip(),
            )
            return

        current_transform = transform


def base_monitor():
    global base_attached_previous

    while running:
        attached = keyboard_base_attached()

        if attached != base_attached_previous:
            base_attached_previous = attached

            if attached:
                logging.info("Keyboard base attached; forcing normal orientation")
                apply_transform("normal")
            else:
                logging.info("Keyboard base detached; enabling sensor rotation")

                if current_orientation in ORIENTATION_TO_TRANSFORM:
                    apply_transform(
                        ORIENTATION_TO_TRANSFORM[current_orientation]
                    )

        time.sleep(POLL_INTERVAL)


def sensor_monitor():
    global current_orientation

    while running:
        logging.info("Starting monitor-sensor")

        process = subprocess.Popen(
            ["stdbuf", "-oL", "monitor-sensor", "--accel"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        try:
            if process.stdout is None:
                raise RuntimeError("monitor-sensor stdout is unavailable")

            for line in process.stdout:
                if not running:
                    break

                line = line.strip()
                logging.debug("monitor-sensor: %s", line)

                marker = "Accelerometer orientation changed:"

                if marker not in line:
                    continue

                orientation = line.split(marker, 1)[1].strip()

                if orientation not in ORIENTATION_TO_TRANSFORM:
                    logging.warning(
                        "Unknown accelerometer orientation: %s",
                        orientation,
                    )
                    continue

                current_orientation = orientation

                logging.info(
                    "Accelerometer orientation: %s",
                    orientation,
                )

                if not keyboard_base_attached():
                    apply_transform(
                        ORIENTATION_TO_TRANSFORM[orientation]
                    )

        except Exception:
            logging.exception("Sensor monitor failed")

        finally:
            if process.poll() is None:
                process.terminate()

                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()

        if running:
            logging.warning(
                "monitor-sensor stopped; restarting in 2 seconds"
            )
            time.sleep(2)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    signal.signal(signal.SIGTERM, stop_handler)
    signal.signal(signal.SIGINT, stop_handler)

    logging.info("Dell automatic rotation service starting")

    base_thread = threading.Thread(
        target=base_monitor,
        name="base-monitor",
        daemon=True,
    )
    base_thread.start()

    sensor_monitor()

    logging.info("Dell automatic rotation service stopped")


if __name__ == "__main__":
    main()
PY

chmod 755 ~/.local/bin/dell-auto-rotate.py
