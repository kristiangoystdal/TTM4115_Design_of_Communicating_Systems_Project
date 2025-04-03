from dataclasses import dataclass, field

from paho.mqtt.client import Client
from stmpy import Machine

from scooter.helpers import IdCounter


@dataclass(slots=True)
class ScooterLogic:
    scooter_id: int = field(default_factory=IdCounter.next, init=False)
    mqtt_client: Client = field(default=None, init=False)  # type: ignore
    stm: Machine = field(default=None, init=False)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.scooter_id})"
