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



def set_led_pixel(x: int, y: int, color: Color) -> None:
    """Set a single pixel on the LED matrix."""
    if 0 <= x < 8 and 0 <= y < 8:
        sense.set_pixel(x, y, *color.value)
    else:
        raise ValueError("Pixel coordinates out of bounds (0-7).")


def set_led_pixels(pixels: list[tuple[int, int]], color: Color) -> None:
    """Set multiple pixels on the LED matrix."""
    for x, y in pixels:
        set_led_pixel(x, y, color)
        
        
def animate_pixels(
    pixels: list[tuple[int, int]], color: Color, duration: float = 1
) -> None:
    """Animate the pixels on the LED matrix."""
    for x, y in pixels:
        set_led_pixel(x, y, color)
        time.sleep(duration / len(pixels))
    time.sleep(duration)
    for x, y in pixels:
        set_led_pixel(x, y, Color.BLACK)  # Clear the pixel after animation
    time.sleep(duration/len(pixels))


def print_matrix() -> None:
    """Print the current state of the LED matrix using emojis with closest color matching."""
    from math import sqrt

    color_to_emoji = {
        (255, 0, 0): "🟥",    # Red
        (0, 255, 0): "🟩",    # Green
        (0, 0, 255): "🟦",    # Blue
        (255, 255, 0): "🟨",  # Yellow
        (255, 255, 255): "⬜", # White
        (0, 0, 0): "⬛",      # Black
        # Add more if needed
    }

    def closest_color(pixel):
        """Find the closest matching color."""
        r, g, b = pixel
        min_distance = float('inf')
        closest_emoji = "❓"  # Default for unknowns
        for color, emoji in color_to_emoji.items():
            cr, cg, cb = color
            distance = sqrt((r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2)
            if distance < min_distance:
                min_distance = distance
                closest_emoji = emoji
        return closest_emoji

    matrix = sense.get_pixels()
    for row in range(8):
        row_pixels = matrix[row * 8 : (row + 1) * 8]
        row_str = ""
        for pixel in row_pixels:
            color = tuple(pixel)
            emoji = closest_color(color)
            row_str += emoji
        print(row_str)
        

