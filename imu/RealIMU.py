import math
import time
from dataclasses import dataclass

import board
import busio
import numpy as np
from adafruit_bno08x import (
    BNO_REPORT_GYROSCOPE,
    BNO_REPORT_LINEAR_ACCELERATION,
    BNO_REPORT_MAGNETOMETER,
    BNO_REPORT_ROTATION_VECTOR,
)
from adafruit_bno08x.i2c import BNO08X_I2C
from typing_extensions import override

from .BaseIMU import BaseIMU
from .IMUData import IMUData


class BNO08X_YPR(BNO08X_I2C, BaseIMU):
    def __init__(
        self,
        *args,
        report_interval_ms=10,
        **kwargs,
    ):
        # The BNO08X can be at either address 0x4A or 0x4B
        # The adafruit library expects 0x4A, but we typically use 0x4B
        try:
            super().__init__(address=0x4B, *args, **kwargs)
        except ValueError as _:
            try:
                super().__init__(*args, **kwargs)
            except ValueError as _:
                print(
                    "Could not establish connection to the IMU.\n"
                    + "Please check the physical connection!"
                )

        try:
            # report_interval is in microseconds
            # the library's default is 50ms, but ours is 10ms
            self.enable_feature(
                BNO_REPORT_LINEAR_ACCELERATION,
                report_interval=report_interval_ms * 1000,
            )
            self.enable_feature(
                BNO_REPORT_GYROSCOPE, report_interval=report_interval_ms * 1000
            )
            self.enable_feature(
                BNO_REPORT_MAGNETOMETER, report_interval=report_interval_ms * 1000
            )
            self.enable_feature(
                BNO_REPORT_ROTATION_VECTOR, report_interval=report_interval_ms * 1000
            )

            print("IMU connection successfully initialized")
        except RuntimeError as e:
            feature_names = {
                BNO_REPORT_LINEAR_ACCELERATION: "Linear Acceleration",
                BNO_REPORT_GYROSCOPE: "Gyroscope",
                BNO_REPORT_MAGNETOMETER: "Magnetometer",
                BNO_REPORT_ROTATION_VECTOR: "Rotation Vector",
            }
            print(
                "One of the features couldn't be enabled. Check the physical connection to the IMU"
            )
            print(
                "Feature that could not be enabled: "
                + f"{feature_names[e.args[1]] if e.args[1] in feature_names else e.args[1]}"
            )

    def read_data(self) -> IMUData:
        """
        Read accelerometer, gyroscope, magnetometer, and orientation data from the IMU

        start_time: The first value of time.perf_counter_ns before this function is run
        """
        self._process_available_packets()

        read_time = int(time.time_ns() / 1e6)
        accel_x, accel_y, accel_z = self.linear_acceleration
        gyro_x, gyro_y, gyro_z = self.gyro
        mag_x, mag_y, mag_z = self.magnetic
        rot_y, rot_p, rot_r = self._quat_to_ypr(self.quaternion)

        return IMUData(
            "bno085-testing",
            read_time,
            accel_x,
            accel_y,
            accel_z,
            math.degrees(gyro_x),
            math.degrees(gyro_y),
            math.degrees(gyro_z),
            mag_x,
            mag_y,
            mag_z,
            rot_y,
            rot_p,
            rot_r,
        )

    @property
    def rotation(self) -> tuple[float, float, float] | None:
        """The IMU's rotation in terms of yaw, pitch, and roll"""
        self._process_available_packets()
        try:
            return self._quat_to_ypr(self._readings[BNO_REPORT_ROTATION_VECTOR])
        except KeyError:
            raise RuntimeError("No quaternion report found, is it enabled?") from None

    def _normalize_quaternion(self, q: tuple[float, float, float, float]):
        w, x, y, z = q
        magnitude = np.sqrt(w**2 + x**2 + y**2 + z**2)

        if magnitude == 0:
            raise ValueError("Cannot normalize a zero quaternion.")

        return w / magnitude, x / magnitude, y / magnitude, z / magnitude

    # @cache
    def _quat_to_ypr(
        self, q: tuple[float, float, float, float]
    ) -> tuple[float, float, float]:
        """
        Internal function to convert the quaternion rotation to yaw, pitch, and roll
        quat: quaternion in the form of (w, x, y, z)
        """
        # r = R.from_quat(q)
        #
        # yaw, pitch, roll = r.as_euler("zyx", degrees=True)
        # return (yaw, pitch, roll)
        w, x, y, z = self._normalize_quaternion(q)

        # Calculate the yaw, pitch, and roll in radians
        yaw = np.arctan2(2.0 * (y * z + w * x), 1 - 2 * (x * x + y * y))
        pitch = np.arcsin(2.0 * (w * y - x * z))
        roll = np.arctan2(2.0 * (x * y + w * z), 1 - 2 * (y * y + z * z))

        # Convert from radians to degrees
        yaw = np.degrees(yaw)
        pitch = np.degrees(pitch)
        roll = np.degrees(roll)

        # I would wrap the yaw, but it gives incorrect results if I do that
        # if pitch > 0:
        #     pitch = 180 - pitch
        # else:
        #     pitch = abs(pitch)
        # if roll > 0:
        #     roll = 180 - roll
        # else:
        #     roll = abs(roll)

        return yaw, pitch, roll


class IMU:
    _imu: BNO08X_YPR | None = None

    @staticmethod
    def get_conn() -> BNO08X_YPR:
        if not IMU._imu:
            i2c = busio.I2C(board.SCL, board.SDA)
            IMU._imu = BNO08X_YPR(i2c)

        return IMU._imu
