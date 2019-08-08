
from abc import ABC, abstractmethod
import numpy as np

class IInstrument(ABC):
    name = "Virtual Instrument"
    protocol = "Unknown"
    address = 0

    @abstractmethod
    def read(self, parameter_name):
        raise NotImplementedError

    @abstractmethod
    def write(self, parameter_name, value):
        raise NotImplementedError


class MockupInstrument(IInstrument):
    name = "Mock-up Instrument"
    t = 0
    freq = np.pi / 100

    def _get_next_sin(self):
        value = np.sin(self.freq * self.t)
        self.t += 1
        return value

    def read(self, parameter_name):
        return self._get_next_sin()

    def write(self, parameter_name, value):
        pass
