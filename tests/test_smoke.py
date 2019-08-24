import pytest
import solax
from solax import inverter

from tests import fixtures


def test_parse_response():
    resp = {'method': 'uploadsn',
            'version': 'Solax_SI_CH_2nd_20160912_DE02',
            'type': 'AL_SE',
            'SN': 'XXXXXXX',
            'Data': [0.5, 0.4, 202.0, 194.3, 2.0, 234.0, 444, 40, 17.0, 238.2,
                     -15, 101, 77, 56.01, -6.36, -357, 27, 92, 0.0, 126.0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     0, 373.90, 38.60, 0, 0, 0, 0, 0, 0, 0, 50.02, 0, 0, 0.0,
                     0, 0, 0, 0, 0, 0, 0.0, 0, 8, 0, 0, 0.00, 0, 8],
            'Status': 2}
    parsed = solax.parse_solax_real_time_response(resp)

    for sensor, value in fixtures.XHYBRID_VALUES.items():
        assert parsed.data[sensor] == value
    assert parsed.serial_number == 'XXXXXXX'
    assert parsed.version == 'Solax_SI_CH_2nd_20160912_DE02'
    assert parsed.type == 'AL_SE'
    assert parsed.status == 2


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
    assert parsed.status == 2
