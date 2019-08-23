import pytest
from solax import inverter


@pytest.mark.asyncio
async def test_xhybrid_hit_endpoint(XHybridFixture):
    i = inverter.XHybrid(*XHybridFixture)
    await run_get_data(i)


@pytest.mark.asyncio
async def test_x3_hit_endpoint(X3Fixture):
    i = inverter.X3(*X3Fixture)
    await run_get_data(i)


async def run_get_data(i):
    data = await i.get_data()
    assert data is not None
