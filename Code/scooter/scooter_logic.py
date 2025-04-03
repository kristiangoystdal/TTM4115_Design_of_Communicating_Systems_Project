from dataclasses import dataclass, field

from paho.mqtt.client import Client
from stmpy import Machine

from scooter.helpers import IdCounter

from .sense_hat_handler import set_led_matrix

from scooter.color import Color


@dataclass
class ScooterLogic:
    scooter_id: int = field(default_factory=IdCounter.next, init=False)
    mqtt_client: Client = field(default=None, init=False)  # type: ignore
    stm: Machine = field(default=None, init=False)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.scooter_id})"

    def lights_reserved(self) -> None:
        """Set the LED matrix to reserved color."""
        print("Entering reserved state: Setting LED matrix to reserved color.")
        set_led_matrix(Color.RED)

    def lights_free(self) -> None:
        """Set the LED matrix to free color."""
        print("Entering idle state: Setting LED matrix to free color.")
        set_led_matrix(Color.GREEN)

    def lights_driving(self) -> None:
        """Set the LED matrix to driving color."""
        print("Entering driving state: Setting LED matrix to driving color.")
        set_led_matrix(Color.BLUE)

    def lights_charging(self) -> None:
        """Set the LED matrix to charging color."""
        print("Entering charging state: Setting LED matrix to charging color.")
        set_led_matrix(Color.YELLOW)

    def start_display(self) -> None:
        """Start the display for driving mode."""
        print("Starting display for driving mode.")

    def stop_display(self) -> None:
        """Stop the display for driving mode."""
        print("Stopping display for driving mode.")

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

    def disable_charger(self) -> None:
        """Disable the charger."""
        print("Disabling charger.")
