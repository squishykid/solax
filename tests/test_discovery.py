import pytest

import solax
from solax import inverter


@pytest.mark.asyncio
async def test_discovery_xhybrid(x_hybrid_fixture):
    rt_api = await solax.real_time_api(*x_hybrid_fixture)
    assert rt_api.inverter.__class__ == inverter.XHybrid


@pytest.mark.asyncio
async def test_discovery_no_host():
    with pytest.raises(inverter.DiscoveryError):
        await solax.real_time_api('localhost', 2)


@pytest.mark.asyncio
async def test_discovery_unknown_webserver(simple_http_fixture):
    with pytest.raises(inverter.DiscoveryError):
        await solax.real_time_api(*simple_http_fixture)
