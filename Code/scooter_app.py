from stmpy import Driver, Machine
from scooter.constants import BROKER, PORT
from scooter.mqtt_client import MqttClient
from scooter.scooter_logic import ScooterLogic

from scooter.sense_hat_handler import get_temperature


s0 = {
    "name": "idle",
    "entry": "lights_free(); check_temperature()",
}
s1 = {
    "name": "reserved",
    "entry": "lights_reserved()",
}
s2 = {
    "name": "driving",
    "entry": "start_display(); enable_motor(); unlock_wheel()",
    "exit": "stop_display(); disable_motor(); lock_wheel()",
}
s3 = {
    "name": "charging",
    "entry": "enable_charger()",
    "exit": "disable_charger()",
}
states = [s0, s1, s2, s3]

t1 = {
    "source": "initial",
    "target": "idle",
}
t2 = {
    "source": "idle",
    "target": "reserved",
    "trigger": "reserve",
}
t3 = {
    "source": "reserved",
    "target": "idle",
    "trigger": "cancel",
}
t4 = {
    "source": "reserved",
    "target": "idle",
    "trigger": "timeout",
}
t5 = {
    "source": "reserved",
    "target": "driving",
    "trigger": "unlock",
}
t6 = {
    "source": "idle",
    "target": "driving",
    "trigger": "unlock",
}
t7 = {
    "source": "driving",
    "target": "idle",
    "trigger": "lock",
}
t8 = {
    "source": "idle",
    "target": "charging",
    "trigger": "charge",
}
t9 = {
    "source": "charging",
    "target": "idle",
    "trigger": "no_charge",
}
t10 = {
    "source": "charging",
    "target": "driving",
    "trigger": "unlock",
}
t11 = {
    "source": "idle",
    "target": "charging",
    "trigger": "too_hot",
}

transitions = [t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11]


def main() -> None:
    scooter = ScooterLogic()
    scooter_machine = Machine(
        name="ScooterLogic(2)",
        transitions=transitions,
        obj=scooter,
        states=states,
    )
    scooter.set_stm(scooter_machine)  # <- Better and safer

    driver = Driver()
    driver.add_machine(scooter_machine)

    mqtt_client = MqttClient(driver)

    driver.start()
    mqtt_client.start(BROKER, PORT)     
     


if __name__ == "__main__":
    main()
