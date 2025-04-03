from dataclasses import dataclass, field

from paho.mqtt.client import Client
from stmpy import Machine

from scooter.helpers import IdCounter

from .sense_hat_handler import set_led_matrix


@dataclass(slots=True)
class ScooterLogic:
    scooter_id: int = field(default_factory=IdCounter.next, init=False)
    mqtt_client: Client = field(default=None, init=False)  # type: ignore
    stm: Machine = field(default=None, init=False)

    # Define colors as class variables
    IDLE_COLOR = (0, 255, 0)
    RESERVED_COLOR = (255, 255, 0)
    DRIVING_COLOR = (0, 0, 255)
    CHARGING_COLOR = (255, 0, 0)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.scooter_id})"

    def lights_reserved(self) -> None:
        """Set the LED matrix to reserved color."""
        print("Entering reserved state: Setting LED matrix to reserved color.")
        set_led_matrix(self.RESERVED_COLOR)
