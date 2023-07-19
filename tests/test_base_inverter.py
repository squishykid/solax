from solax.discovery import REGISTRY
from solax.inverter import Inverter


def test_all_registered_inverters_inherit_from_base():
    for i in REGISTRY:
        assert issubclass(i, Inverter)
