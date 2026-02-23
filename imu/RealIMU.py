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
    PacketError,
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
        BaseIMU.__init__(self)
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

        capture_time_ms = int(time.time_ns() / 1e6)
        accel_x, accel_y, accel_z = self.linear_acceleration
        gyro_x, gyro_y, gyro_z = self.gyro
        mag_x, mag_y, mag_z = self.magnetic
        rot_y, rot_p, rot_r = self._quat_to_ypr(self.quaternion)

        return IMUData(
            self._next_counter(),
            capture_time_ms,
            0,
            accel_x,
            accel_y,
            accel_z,
            gyro_x,
            gyro_y,
            gyro_z,
            mag_x,
            mag_y,
            mag_z,
            rot_y,
            rot_p,
            rot_r,
        )

    def _process_available_packets(self, max_packets: int | None = None) -> None:
        """
        Work around intermittent short packets on the SHTP command channels.

        Some BNO086 firmwares may emit 2-byte command-channel packets while features
        are being enabled. The upstream parser treats these as batched sensor reports
        and raises RuntimeError("Unprocessable Batch bytes", 2).
        """
        processed_count = 0
        while self._data_ready:
            if max_packets and processed_count > max_packets:
                return

            try:
                new_packet = self._read_packet()
            except PacketError:
                continue

            if new_packet.channel_number in (0, 1):
                continue

            try:
                self._handle_packet(new_packet)
            except RuntimeError as error:
                if error.args and error.args[0] == "Unprocessable Batch bytes":
                    continue
                raise

            processed_count += 1

    @property
    def rotation(self) -> tuple[float, float, float] | None:
        """The IMU's rotation in terms of yaw, pitch, and roll"""
        self._process_available_packets()
        try:
            return self._quat_to_ypr(self._readings[BNO_REPORT_ROTATION_VECTOR])
        except KeyError:
            raise RuntimeError("No quaternion report found, is it enabled?") from None

    
class IMU:
    _imu: BNO08X_YPR | None = None

    @staticmethod
    def get_conn() -> BNO08X_YPR:
        if not IMU._imu:
            i2c = busio.I2C(board.SCL, board.SDA)
            IMU._imu = BNO08X_YPR(i2c)

        return IMU._imu
