import pytest

import solax
from solax.discovery import REGISTRY
from solax.http_client import all_variations
from solax.inverter import Inverter, InverterError
from solax.units import Measurement, Total
from tests import fixtures


async def build_right_variant(inverter, conn) -> Inverter:
    last_error: BaseException = BaseException("anticipating errors")
    for i in inverter.build_all_variants(*conn):
        try:
            await i.get_data()
            return i
        except InverterError as ex:
            last_error = ex
    raise last_error


@pytest.mark.asyncio
async def test_smoke(inverters_fixture):
    conn, inverter_class, client, values = inverters_fixture
    host, port = conn
    http_client = all_variations(host, port)[client]
    inv = inverter_class(http_client)

    rt_api = solax.RealTimeAPI(inv)
    parsed = await rt_api.get_data()

    msg = "data size should match expected values"
    assert len(values) == len(parsed.data), msg
    for sensor, value in values.items():
        assert (
            parsed.data[sensor] == value
        ), f"{sensor}: expected {value} but got {parsed.data[sensor]}"


@pytest.mark.asyncio
async def test_throws_when_unable_to_parse(inverters_garbage_fixture):
    conn, inverter_class, client_name = inverters_garbage_fixture
    host, port = conn
    http_client = all_variations(host, port)[client_name]
    with pytest.raises(InverterError):
        i = inverter_class(http_client)
        await i.get_data()


def test_registry_matches_inverters_under_test():
    test_inverters = {i.inverter for i in fixtures.INVERTERS_UNDER_TEST}
    registry_inverters = set(REGISTRY)
    assert test_inverters == registry_inverters, "tests do not match registry"


def test_inverter_sensors_match():
    test_values = ((i.inverter, i.values) for i in fixtures.INVERTERS_UNDER_TEST)
    for i, expected_values in test_values:
        inverter = i(None)
        sensor_map = inverter.sensor_map()
        msg = f"""{sorted(sensor_map.keys())} vs
{sorted(expected_values.keys())}"""
        assert len(sensor_map) == len(expected_values), msg
        for name, _ in sensor_map.items():
            assert name in expected_values


def test_inverter_sensors_define_valid_units(inverters_under_test):
    inverter = inverters_under_test(None)
    sensor_map = inverter.sensor_map()
    for name, (_, unit, *_) in sensor_map.items():
        msg = (
            f"provided unit '{unit}'({type(unit)}) "
            f"is not a proper Unit on sensor '{name}' of Inverter '{inverters_under_test}'"
        )
        assert isinstance(unit, (Measurement, Total)), msg
