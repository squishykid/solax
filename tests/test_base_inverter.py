import pytest

from solax.discovery import REGISTRY
from solax.http_client import HttpClient
from solax.inverter import Inverter
from solax.inverter_error import InverterError


class BogusInverter(Inverter):
    @classmethod
    def response_decoder(cls):
        return {
            "Screwed Up!": "bogus",
        }


class DummyInverter(Inverter):
    @classmethod
    def response_decoder(cls):
        return {
            "Dummy": ([0, 1], None, [lambda x: x + 1]),
        }


bogus_response = {
    "Data": [
        0,
    ],
    "type": "",
}


def test_all_registered_inverters_inherit_from_base():
    for i in REGISTRY:
        assert issubclass(i, Inverter)


def test_bogus_inverter_throws():
    inv = BogusInverter(HttpClient(""))
    with pytest.raises(TypeError):
        inv.sensor_map()


def test_base_class_needs_override():
    with pytest.raises(NotImplementedError):
        Inverter(HttpClient("")).response_decoder()


def test_bogus_response_raises_error():
    with pytest.raises(InverterError):
        DummyInverter(HttpClient("")).map_response_v2(bogus_response)
