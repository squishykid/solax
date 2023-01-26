""" Units and different measrement types"""
from dataclasses import dataclass
from enum import Enum
from typing import Union


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


@dataclass
class Measurement:
    """Respresention of measurement with a given unit and arbitrary values."""

    unit: Units
    is_monotonic: bool = False


@dataclass
class Total:
    """A Measuremeant where the values are continuously increasing."""

    unit: Units
    is_monotonic: bool = True


SensorUnit = Union[Measurement, Total]
