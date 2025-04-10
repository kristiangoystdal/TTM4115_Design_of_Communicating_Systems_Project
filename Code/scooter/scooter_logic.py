from dataclasses import dataclass, field
from threading import Timer

from paho.mqtt.client import Client
from stmpy import Machine

from scooter.helpers import IdCounter
from .sense_hat_handler import *
from scooter.color import Color
from scooter.constants import (
    BAR,
    CHECK_MARK,
    X_MARK,
    CHARGING_MARK,
    CHARGING_ANIMATION,
)
from scooter.constants import seven_segment_display_list

import random as Random


@dataclass
class ScooterLogic:
    scooter_id: int = field(default_factory=IdCounter.next, init=False)
    mqtt_client: Client = field(default=None, init=False)  # type: ignore
    stm: Machine = field(default=None, init=False)
    animation_timer: Timer = field(default=None, init=False)
    animation_step: int = field(default=0, init=False)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.scooter_id})"

    def lights_reserved(self) -> None:
        """Set the LED matrix to reserved color."""
        print("Entering reserved state: Setting LED matrix to reserved color.")
        self.stop_animation()
        set_led_matrix()
        set_led_pixels(BAR, Color.RED)
        set_led_pixels(X_MARK, Color.RED)
        print_matrix()

    def lights_free(self) -> None:
        """Set the LED matrix to free color."""
        print("Entering idle state: Setting LED matrix to free color.")
        self.stop_animation()
        set_led_matrix()
        set_led_pixels(BAR, Color.GREEN)
        set_led_pixels(CHECK_MARK, Color.GREEN)
        print_matrix()

    def lights_driving(self) -> None:
        """Set the LED matrix to driving color."""
        print("Entering driving state: Setting LED matrix to driving color.")
        self.stop_animation()
        set_led_matrix()
        set_led_pixels(BAR, Color.BLUE)
        print_matrix()

    def lights_charging(self) -> None:
        """Set the LED matrix to charging color."""
        print("Entering charging state: Setting LED matrix to charging color.")
        self.stop_animation()
        set_led_matrix()
        set_led_pixels(BAR, Color.YELLOW)
        print_matrix()

    def start_display(self) -> None:
        """Start the display for driving mode."""
        print("Starting display for driving mode.")
        self.stop_animation()
        set_led_matrix()
        set_led_pixels(BAR, Color.BLUE)

        int_1 = Random.randint(0, 1)
        int_2 = Random.randint(0, 9)

        number_1 = seven_segment_display_list(int_1, 0, 3)
        number_2 = seven_segment_display_list(int_2, 4, 3)

        print(int_1, int_2)

        set_led_pixels(number_1, Color.WHITE)
        set_led_pixels(number_2, Color.WHITE)
        print_matrix()

    def stop_display(self) -> None:
        """Stop the display for driving mode."""
        print("Stopping display for driving mode.")
        self.stop_animation()
        set_led_matrix()
        print_matrix()

    def enable_motor(self) -> None:
        """Enable the motor for driving."""
        print("Enabling motor for driving.")

    def disable_motor(self) -> None:
        """Disable the motor."""
        print("Disabling motor.")

    def unlock_wheel(self) -> None:
        """Unlock the wheel for driving."""
        print("Unlocking wheel for driving.")

    def lock_wheel(self) -> None:
        """Lock the wheel."""
        print("Locking wheel.")

    def enable_charger(self) -> None:
        """Enable the charger for charging mode."""
        print("Enabling charger for charging mode.")
        set_led_matrix()
        set_led_pixels(BAR, Color.YELLOW)
        set_led_pixels(CHARGING_MARK, Color.GREEN)
        self.start_charging_animation()

    def disable_charger(self) -> None:
        """Disable the charger."""
        print("Disabling charger.")
        self.stop_animation()

    def start_charging_animation(self) -> None:
        """Start non-blocking charging animation."""
        self.animation_step = 0
        self.schedule_charging_animation()

    def schedule_charging_animation(self) -> None:
        """Schedule next step of the charging animation."""
        # Keep the BAR always yellow
        set_led_pixels(BAR, Color.YELLOW)

        # First clear all charging pixels
        for group in CHARGING_ANIMATION:
            for x, y in group:
                set_led_pixel(x, y, Color.BLACK)

        # Light up the current group of two pixels
        group = CHARGING_ANIMATION[
            self.animation_step % len(CHARGING_ANIMATION)
        ]
        set_led_pixels(group, Color.YELLOW)

        print_matrix()

        # Schedule next step
        self.animation_timer = Timer(0.5, self.schedule_charging_animation)
        self.animation_timer.start()
        self.animation_step += 1

    def stop_animation(self) -> None:
        """Stop any running animation."""
        if self.animation_timer:
            self.animation_timer.cancel()
            self.animation_timer = None
        # set_led_matrix()
        
    def start_temp_timer(self):
        self.stm.start_timer('temp_timer', 5000)  # Every 5 seconds

    def on_temp_timer(self):
        temp = get_temperature()
        if temp > 30:
            self.stm.send('too_hot')
        print(f"Temperature: {temp}°C")
        
        self.stm.start_timer('temp_timer', 5000)  # Restart the timer
        

