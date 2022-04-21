import pytest

from solax import inverter
from solax.discovery import REGISTRY


@pytest.mark.asyncio
async def test_unimplemented_make_request():
    with pytest.raises(NotImplementedError):
        await inverter.Inverter.make_request('localhost', 80)


@pytest.mark.asyncio
async def test_unimplemented_make_request_with_pwd():
    with pytest.raises(NotImplementedError):
        await inverter.Inverter.make_request('localhost', 80, 'pwd')


def test_all_registered_inverters_inherit_from_base():
    for i in REGISTRY:
        assert issubclass(i, inverter.Inverter)
