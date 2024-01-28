import pytest

from solax.discovery import REGISTRY
from solax.inverter import Inverter


def test_all_registered_inverters_inherit_from_base():
    assert REGISTRY
    for i in REGISTRY:
        assert issubclass(i, Inverter)


def test_unimplemented_response_decoder():
    with pytest.raises(NotImplementedError):
        versions = Inverter.build_all_variants("localhost", 80)
        next(iter(versions)).response_decoder()
