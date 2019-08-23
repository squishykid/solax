import pytest

from solax import inverter


@pytest.mark.asyncio
async def test_unimplemented_make_request():
    with pytest.raises(NotImplementedError):
        await inverter.Inverter.make_request('localhost', 80)


def test_all_registered_inverters_inherit_from_base():
    for i in inverter.REGISTRY:
        assert issubclass(i, inverter.Inverter)


@pytest.mark.asyncio
async def test_throws_when_unable_to_parse(x_hybrid_garbage_fixture):
    with pytest.raises(inverter.InverterError):
        i = inverter.XHybrid(*x_hybrid_garbage_fixture)
        await i.get_data()
