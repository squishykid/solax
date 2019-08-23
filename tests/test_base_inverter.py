import pytest

from solax import inverter


@pytest.mark.asyncio
async def test_unimplemented_make_request():
    with pytest.raises(NotImplementedError):
        await inverter.Inverter.make_request('localhost', 80)


def test_all_registered_inverters_inherit_from_base():
    for i in inverter.REGISTRY:
        assert issubclass(i, inverter.Inverter)
