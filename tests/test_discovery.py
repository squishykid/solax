import pytest
from solax import inverter

@pytest.mark.asyncio
async def test_discovery_xhybrid(XHybridFixture):
    i = await inverter.discover(*XHybridFixture)
    assert i.__class__ == inverter.XHybrid

@pytest.mark.asyncio
async def test_discovery_x3(X3Fixture):
    i = await inverter.discover(*X3Fixture)
    assert i.__class__ == inverter.X3

@pytest.mark.asyncio
async def test_discovery_no_host():
    with pytest.raises(inverter.DiscoveryError):
        await inverter.discover('localhost', 2)

@pytest.mark.asyncio
async def test_discovery_unknown_webserver(SimpleHttpFixture):
    with pytest.raises(inverter.DiscoveryError):
        await inverter.discover(*SimpleHttpFixture)
