import numpy as np
from traits.api import ABCHasTraits, Any, Dict, Event, Instance, Int


class IDataContainer(ABCHasTraits):
    data = Any
    meta_data = Dict
    updated = Event

class CurveData(IDataContainer):
    index = Int(0)

    @classmethod
    def create_blank(cls, size=1024, dtype=np.float64) :
        return cls(data=np.zeros(size, dtype=dtype))

    def append(self, value):
        self.data[self.index] = value
        self.index += 1
        self.updated = value