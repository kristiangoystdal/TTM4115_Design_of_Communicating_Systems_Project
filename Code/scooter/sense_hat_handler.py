import time
from datetime import datetime

try:
    from sense_hat import SenseHat  # Real hardware
except ImportError:
    from sense_emu import SenseHat  # Emulator

from scooter.color import Color


sense = SenseHat()
try:
    sense.set_imu_config(True, True, True)
except OSError:
    print("⚠️ IMU init failed – continuing without IMU (dev mode)")



def get_acceleration() -> tuple[float, float, float]:
    acceleration = sense.accel
    return acceleration["roll"], acceleration["pitch"], acceleration["yaw"]


def get_orientation() -> tuple[float, float, float]:
    orientation = sense.orientation
    return orientation["roll"], orientation["pitch"], orientation["yaw"]


def blink(color: Color, duration: float = 0.25) -> None:
    set_led_matrix(color)
    time.sleep(duration)
    set_led_matrix()
    time.sleep(duration)


def blink_and_wait(
    color: Color, duration: float = 0.25, timeout: float = 60.0
) -> None:
    start_time = datetime.now()

    while (datetime.now() - start_time).total_seconds() < timeout:
        blink(color, duration)

        if sense.stick.get_events():
            break
    else:
        set_led_matrix()


def set_led_matrix(color: Color | None = None) -> None:
    if color is None:
        sense.clear()
    else:
        sense.clear(*color.value)
