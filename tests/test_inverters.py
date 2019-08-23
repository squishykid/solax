import pytest
from solax import inverter


@pytest.mark.asyncio
async def test_xhybrid_hit_endpoint(x_hybrid_fixture):
    i = inverter.XHybrid(*x_hybrid_fixture)
    await run_get_data(i)


@pytest.mark.asyncio
async def test_x3_hit_endpoint(x3_fixture):
    i = inverter.X3(*x3_fixture)
    await run_get_data(i)


async def run_get_data(i):
    data = await i.get_data()
    assert data is not None
