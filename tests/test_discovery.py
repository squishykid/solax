import pytest

import solax
from solax.discovery import DiscoveryError


@pytest.mark.asyncio
async def test_discovery(inverters_fixture):
    conn, inverter_definition_file_name, _, _ = inverters_fixture
    rt_api = await solax.real_time_api(*conn)
    assert rt_api.inverter.inverter_definition_file_name.endswith(
        f"/{inverter_definition_file_name}"
    )


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
