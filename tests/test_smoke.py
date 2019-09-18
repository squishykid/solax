import pytest
import solax
from solax import inverter

from tests import fixtures


@pytest.mark.asyncio
async def test_x_hybrid_smoke(x_hybrid_fixture):
    inv = inverter.XHybrid(*x_hybrid_fixture)
    rt_api = solax.RealTimeAPI(inv)
    parsed = await rt_api.get_data()

    for sensor, value in fixtures.XHYBRID_VALUES.items():
        assert parsed.data[sensor] == value
    assert parsed.serial_number == 'XXXXXXX'
    assert parsed.version == 'Solax_SI_CH_2nd_20160912_DE02'
    assert parsed.type == 'AL_SE'


@pytest.mark.asyncio
async def test_x3_smoke(x3_fixture):
    inv = inverter.X3(*x3_fixture)
    rt_api = solax.RealTimeAPI(inv)
    parsed = await rt_api.get_data()

    for sensor, value in fixtures.X3_VALUES.items():
        assert parsed.data[sensor] == value
    assert parsed.serial_number == 'X3X3ZZYYXX'
    assert parsed.version == '2.033.20'
    assert parsed.type == 'X3-MIC'


@pytest.mark.asyncio
async def test_smoke(inverters_fixture):
    conn, inverter_class, values = inverters_fixture
    inv = inverter_class(*conn)
    rt_api = solax.RealTimeAPI(inv)
    parsed = await rt_api.get_data()

    for sensor, value in values.items():
        assert parsed.data[sensor] == value
    assert parsed.serial_number == 'XXXXXXX'
    assert parsed.version == 'Solax_SI_CH_2nd_20160912_DE02'
    assert parsed.type == 'AL_SE'
