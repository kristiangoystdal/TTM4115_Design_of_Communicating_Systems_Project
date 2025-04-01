from stmpy import Driver, Machine

from scooter.constants import BROKER, PORT
from scooter.mqtt_client import MqttClient
from scooter.scooter import Scooter


def main() -> None:
    scooter = Scooter()
    scooter_machine = Machine(
        name=repr(scooter),
        transitions=[],
        obj=scooter,
        states=[],
    )
    scooter.stm = scooter_machine

    driver = Driver()
    driver.add_machine(scooter_machine)

    mqtt_client = MqttClient()
    mqtt_client.stm_driver = driver

    driver.start()
    mqtt_client.start(BROKER, PORT)


if __name__ == "__main__":
    main()
