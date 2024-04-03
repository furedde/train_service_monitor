from abc import ABC, abstractmethod
from db import TrainStatus


class TrainMonitor(ABC):
    @abstractmethod
    def get_status(self) -> TrainStatus:
        pass

    @abstractmethod
    def operator(self) -> str:
        pass
