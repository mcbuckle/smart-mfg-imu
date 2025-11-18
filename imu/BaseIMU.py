from abc import ABC, abstractmethod

from .IMUData import IMUData


class BaseIMU(ABC):
    @abstractmethod
    def read_data(self) -> IMUData:
        pass
