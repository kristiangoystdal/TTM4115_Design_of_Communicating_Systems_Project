from stmpy import Driver, Machine

from scooter.constants import BROKER, PORT
from scooter.mqtt_client import MqttClient
from scooter.scooter_logic import ScooterLogic


def main() -> None:
    scooter = ScooterLogic()
    scooter_machine = Machine(
        name=repr(scooter),
        transitions=[],
        obj=scooter,
        states=[],
    )
    scooter.stm = scooter_machine

    driver = Driver()
    driver.add_machine(scooter_machine)

    mqtt_client = MqttClient(driver)

    driver.start()
    mqtt_client.start(BROKER, PORT)


if __name__ == "__main__":
    main()
