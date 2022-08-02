import time

import pytest

from solax import inverter, inverters, utils
from solax.discovery import REGISTRY


@pytest.mark.asyncio
async def test_unimplemented_make_request():
    with pytest.raises(NotImplementedError):
        await inverter.Inverter.make_request("localhost", 80)


@pytest.mark.asyncio
async def test_unimplemented_make_request_with_pwd():
    with pytest.raises(NotImplementedError):
        await inverter.Inverter.make_request("localhost", 80, "pwd")


def test_all_registered_inverters_inherit_from_base():
    for i in REGISTRY:
        assert issubclass(i, inverter.Inverter)


def test_unimplemented_response_decoder():
    with pytest.raises(NotImplementedError):
        inverter.Inverter.response_decoder()


def sleeping(_):
    time.sleep(0.5)


@pytest.mark.asyncio
async def test_timeout(monkeypatch, httpserver):
    monkeypatch.setattr(utils, "REQUEST_TIMEOUT", 0.1)
    httpserver.expect_request("/").respond_with_handler(sleeping)
    with pytest.raises(inverter.InverterError) as ex_info:
        arbitrary_inverter = inverters.X3(httpserver.host, httpserver.port)
        await arbitrary_inverter.get_data()
    assert ex_info.value.args[0] == "Connection to endpoint timed out"
