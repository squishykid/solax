import pytest
import solax
from solax import inverter

from tests import fixtures


@pytest.mark.asyncio
async def test_smoke(inverters_fixture):
    conn, inverter_class, values = inverters_fixture
    inv = inverter_class(*conn)
    rt_api = solax.RealTimeAPI(inv)
    parsed = await rt_api.get_data()

    msg = 'data size should match expected values'
    assert len(values) == len(parsed.data), msg
    for sensor, value in values.items():
        assert parsed.data[sensor] == value, \
          f"{sensor}: expected {value} but got {parsed.data[sensor]}"


@pytest.mark.asyncio
async def test_throws_when_unable_to_parse(inverters_garbage_fixture):
    conn, inverter_class = inverters_garbage_fixture
    with pytest.raises(inverter.InverterError):
        i = inverter_class(*conn)
        await i.get_data()


def test_registry_matches_inverters_under_test():
    test_inverters = {i.inverter for i in fixtures.INVERTERS_UNDER_TEST}
    registry_inverters = set(inverter.REGISTRY)
    assert test_inverters == registry_inverters, 'tests do not match registry'


def test_inverter_sensors_match():
    test_values = (
        (i.inverter, i.values)
        for i
        in fixtures.INVERTERS_UNDER_TEST
    )
    for i, expected_values in test_values:
        sensor_map = i.sensor_map()
        msg = f"""{sorted(sensor_map.keys())} vs
{sorted(expected_values.keys())}"""
        assert len(sensor_map) == len(expected_values), msg
        for name, _ in sensor_map.items():
            assert name in expected_values
