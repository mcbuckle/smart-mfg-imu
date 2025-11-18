import time

from .BaseIMU import BaseIMU, IMUData


class FakeIMU(BaseIMU):
    def __init__(self, *args, sample_filename="data/sample_data.csv", **kwargs):
        self.sample_filename = sample_filename
        self.file = open(sample_filename, "r+")

    def read_data(self):
        # "dev_id,time_ms,datetime,"
        # + "accel_x,accel_y,accel_z,"
        # + "gyro_x,gyro_y,gyro_z,"
        # + "mag_x,mag_y,mag_z,"
        # + "yaw,pitch,roll\n"
        data = self.file.readline()

        if not data:
            self.file.seek(0)
            data = self.file.readline()

        (
            accel_x,
            accel_y,
            accel_z,
            gyro_x,
            gyro_y,
            gyro_z,
            mag_x,
            mag_y,
            mag_z,
            yaw,
            pitch,
            roll,
        ) = (float(i) for i in data.split(","))

        return IMUData(
            "test-run",
            time.time_ns() / 1e6,
            accel_x,
            accel_y,
            accel_z,
            gyro_x,
            gyro_y,
            gyro_z,
            mag_x,
            mag_y,
            mag_z,
            yaw,
            pitch,
            roll,
        )


class IMU:
    _imu: FakeIMU | None = None

    @staticmethod
    def get_conn() -> FakeIMU:
        if not IMU._imu:
            IMU._imu = FakeIMU()

        return IMU._imu
