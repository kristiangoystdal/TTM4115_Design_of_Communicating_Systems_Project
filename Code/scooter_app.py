from stmpy import Driver, Machine

from scooter.constants import BROKER, PORT
from scooter.mqtt_client import MqttClient
from scooter.scooter_logic import ScooterLogic


s0 = {
    "name": "idle",
    "on_enter": "lights_free()",
}
s1 = {
    "name": "reserved",
    "on_enter": "print_reserved()",
}

s2 = {
    "name": "driving",
    "on_enter": "start_display(); enable_motor(); unlock_wheel()",
    "on_exit": "stop_display(); disable_motor(); lock_wheel()",
}
s3 = {
    "name": "charging",
    "on_enter": "enable_charger()",
    "on_exit": "disable_charger()",
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
transitions = [t1, t2, t3, t4, t5, t6, t7, t8, t9]


def main() -> None:
    scooter = ScooterLogic()
    scooter_machine = Machine(
        name=repr(scooter),
        transitions=transitions,
        obj=scooter,
        states=states,
    )
    scooter.stm = scooter_machine

    driver = Driver()
    driver.add_machine(scooter_machine)

    mqtt_client = MqttClient(driver)

    driver.start()
    mqtt_client.start(BROKER, PORT)

    scooter.lights_reserved()


if __name__ == "__main__":
    main()
