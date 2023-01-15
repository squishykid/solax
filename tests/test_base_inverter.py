import pytest

from solax.discovery import REGISTRY
from solax.inverter import Inverter

SCHEMA = Inverter.inverter_definition_schema()


def test_all_inverter_schemas_are_json():
    for i in REGISTRY:
        assert isinstance(i, str)
        assert i.endswith(".json")


def test_inverter(dynamic_inverters):
    SCHEMA(dynamic_inverters)
    print(dynamic_inverters)
