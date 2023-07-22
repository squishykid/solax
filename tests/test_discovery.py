import pytest
import voluptuous as vol

import solax
from solax import Inverter
from solax.discovery import DiscoveryError, discover


@pytest.mark.asyncio
async def test_discovery(inverters_fixture):
    conn, inverter_class, _, _ = inverters_fixture
    rt_api = await solax.real_time_api(*conn)
    assert rt_api.inverter.__class__ == inverter_class


@pytest.mark.asyncio
async def test_discovery_no_host():
    with pytest.raises(DiscoveryError):
        await solax.real_time_api("localhost", 2)


@pytest.mark.asyncio
async def test_discovery_no_host_with_pwd():
    with pytest.raises(DiscoveryError):
        await solax.real_time_api("localhost", 2, "pwd")


@pytest.mark.asyncio
async def test_discovery_unknown_webserver(simple_http_fixture):
    with pytest.raises(DiscoveryError):
        await solax.real_time_api(*simple_http_fixture)


class DummyMatchAllInverter(Inverter):
    @classmethod
    def response_decoder(cls):
        return {
            "Dummy": ([0, 1000], None, [lambda x: x + 1]),
        }

    _schema = vol.Schema({}, extra=vol.ALLOW_EXTRA)


@pytest.mark.asyncio
async def test_throws_when_inverter_parsing_throws(
    inverters_less_garbage_fixture, monkeypatch
):
    monkeypatch.setattr("solax.discovery.REGISTRY", {DummyMatchAllInverter})
    conn, _, _ = inverters_less_garbage_fixture
    host, port = conn
    with pytest.raises(DiscoveryError):
        await discover(host, port, "")
