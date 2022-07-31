""" Units and different measrement types"""
from enum import Enum
from typing import NamedTuple, Union


class Units(Enum):
    """All known Units."""

    W = "W"
    KWH = "kWh"
    A = "A"
    V = "V"
    C = "°C"
    HZ = "Hz"
    PERCENT = "%"
    NONE = ""


class Measurement(NamedTuple):
    """Respresention of measurement with a given unit and arbitrary values."""

    unit: Units
    is_monotonic: bool = False


class Total(Measurement):
    """A Measuremeant where the values are continuously increasing."""

    is_monotonic: bool = True


SensorUnit = Union[Measurement, Total]
