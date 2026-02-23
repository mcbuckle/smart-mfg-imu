from datetime import datetime
import time
from typing import Any, ContextManager

try:
    from curses import window
except ModuleNotFoundError:
    window = Any

from package.client import Client

from .BaseIMU import IMUData


class DataWriter(ContextManager):
    """Writes IMU samples to CSV and MQTT.

    Output schema is intentionally stable and starts with `counter`.
    """

    def __init__(
        self,
        csv_fname=f"data/bno08X-{datetime.now().isoformat()}.csv",
        mqtt_broker_ip="127.0.0.1",
        mqtt_broker_port=1883,
        device_id="joint-1",  # TODO: Add config files or smth
        scr: window | None = None,
    ):
        self.csv_fname = csv_fname
        self.mqtt_broker_ip = mqtt_broker_ip
        self.mqtt_broker_port = mqtt_broker_port
        self.device_id = device_id
        self.scr = scr

    def __enter__(self):
        self.csv_file = open(self.csv_fname, "w+")
        self.csv_file.write(
            "counter,capture_time_ms,recorded_at_time_ms,"
            + "accel_x,accel_y,accel_z,"
            + "gyro_x,gyro_y,gyro_z,"
            + "mag_x,mag_y,mag_z,"
            + "yaw,pitch,roll\n"
        )
        try:
            if self.scr:
                self.scr.addstr(20, 0, "Initializing MQTT connection...")
                self.scr.refresh()
            else:
                print("Initializing MQTT connection...")
            self.mqtt_client = Client(
                broker_ip=self.mqtt_broker_ip,
                broker_port=self.mqtt_broker_port,
                client_type=Client.IMU,
                device_id=self.device_id,
            )
            if self.scr:
                self.scr.addstr(
                    21,
                    0,
                    f"Established MQTT connection to {self.mqtt_broker_ip}:{self.mqtt_broker_port}",
                )
            else:
                print(
                    f"Established MQTT connection to {self.mqtt_broker_ip}:{self.mqtt_broker_port}"
                )
        except Exception as _:
            self.mqtt_client = None
            if self.scr:
                self.scr.addstr(
                    22,
                    0,
                    f"Could not establish MQTT connection to {self.mqtt_broker_ip}:{self.mqtt_broker_port}",
                )
            else:
                print(
                    f"Could not establish MQTT connection to {self.mqtt_broker_ip}:{self.mqtt_broker_port}"
                )
        finally:
            if self.scr:
                self.scr.refresh()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.csv_file.close()

        if self.mqtt_client:
            self.mqtt_client.disconnect()
        return False

    def write_data(self, data: IMUData):
        data.recorded_at_time_ms = int(time.time_ns() / 1e6)
        self._output_to_csv(data)

        if self.mqtt_client:
            self._output_mqtt(data)

    def _output_to_csv(self, data: IMUData):
        """Write one CSV row.

        CSV field order:
        counter,capture_time_ms,recorded_at_time_ms,
        accel_x,accel_y,accel_z,
        gyro_x,gyro_y,gyro_z,
        mag_x,mag_y,mag_z,
        yaw,pitch,roll
        """
        out = (
            f"{data.counter},{data.capture_time_ms},{data.recorded_at_time_ms},{data.accel_x},{data.accel_y},{data.accel_z},"
            + f"{data.gyro_x},{data.gyro_y},{data.gyro_z},{data.mag_x},{data.mag_y},"
            + f"{data.mag_z},{data.yaw},{data.pitch},{data.roll}"
        )
        self.csv_file.write(out + "\n")

    def _output_mqtt(self, data: IMUData):
        """Publish one MQTT payload.

        MQTT field order:
        counter,capture_time_ms,recorded_at_time_ms,
        accel_x,accel_y,accel_z,
        gyro_x,gyro_y,gyro_z,
        mag_x,mag_y,mag_z,
        yaw,pitch,roll
        """
        self.mqtt_client.publish(
            f"{data.counter},{data.capture_time_ms},{data.recorded_at_time_ms},{data.accel_x},{data.accel_y},{data.accel_z},"
            + f"{data.gyro_x},{data.gyro_y},{data.gyro_z},{data.mag_x},{data.mag_y},"
            + f"{data.mag_z},{data.yaw},{data.pitch},{data.roll}"
        )
