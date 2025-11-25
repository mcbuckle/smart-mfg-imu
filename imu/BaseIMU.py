from abc import ABC, abstractmethod

import numpy as np

from .IMUData import IMUData


class BaseIMU(ABC):
    @abstractmethod
    def read_data(self) -> IMUData:
        pass

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

        return tuple(np.round((yaw, pitch, roll), decimals=3))


