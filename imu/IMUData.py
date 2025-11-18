from dataclasses import dataclass

from typing_extensions import override


@dataclass
class IMUData:
    """Convenience class for keeping data read from the IMU"""

    dev_id: str
    time: float

    accel_x: float
    accel_y: float
    accel_z: float

    gyro_x: float
    gyro_y: float
    gyro_z: float

    mag_x: float
    mag_y: float
    mag_z: float

    yaw: float
    pitch: float
    roll: float

    @override
    def __str__(self):
        return (
            f"{self.dev_id},{self.time},{self.accel_x},{self.accel_y},{self.accel_z},"
            + f"{self.gyro_x},{self.gyro_y},{self.gyro_z},{self.mag_x},{self.mag_y},"
            + f"{self.mag_z},{self.yaw},{self.pitch},{self.roll}"
        )
