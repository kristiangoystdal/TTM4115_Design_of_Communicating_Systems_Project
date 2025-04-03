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
        set_led_matrix(Color.YELLOW)
        
    def lights_free(self) -> None:
        """Set the LED matrix to free color."""
        print("Entering idle state: Setting LED matrix to free color.")
        set_led_matrix(Color.GREEN)

    def print_reserved(self):
        print(">>> ENTERED reserved state!")
