from collections.abc import Mapping
from dataclasses import dataclass, field
from threading import Thread
from typing import Any

import paho.mqtt.client as mqtt
from paho.mqtt.client import Client, MQTTMessage
from stmpy import Driver


@dataclass(slots=True)
class MqttClient:
    client = Client()
    stm_driver: Driver = field(default=None)

    def __post_init__(self) -> None:
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(
        self, client: Client, userdata: Any, flags: Mapping[str, Any], rc: int
    ) -> None:
        print(f"on_connect(): {mqtt.connack_string(rc)}")
        client.subscribe("escooter/#")

    def on_message(
        self, client: Client, userdata: Any, msg: MQTTMessage
    ) -> None:
        print(f"on_message(): {msg.topic} - {msg.payload.decode()}")

        if not self.stm_driver:
            return

        topic_parts = msg.topic.split("/")

        if len(topic_parts) <= 1:
            return

        stm_name = f"ScooterLogic({topic_parts[1]})"

        if not (trigger := msg.payload.decode()):
            return

        self.stm_driver.send(trigger, stm_name, msg.payload.decode())
        print(f"Trigger sent: {trigger} to {stm_name}")

    def start(self, broker: str, port: int) -> None:
        print(f"Connecting to {broker}:{port}")
        self.client.connect(broker, port)

        thread = Thread(target=self.client.loop_forever)

        try:
            thread.start()
        except KeyboardInterrupt:
            self.client.disconnect()
