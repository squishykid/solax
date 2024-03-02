import asyncio

import pytest

import solax
from solax import InverterResponse
from solax.discovery import REGISTRY, DiscoveryError
from solax.inverter import InverterError
from solax.inverters import X1Boost


class DelayedX1Boost(X1Boost):
    async def get_data(self) -> InverterResponse:
        await asyncio.sleep(10)
        return await super().get_data()


class DelayedFailedX1Boost(X1Boost):
    async def make_request(self) -> InverterResponse:
        await asyncio.sleep(5)
        raise InverterError


@pytest.mark.asyncio
async def test_discovery(inverters_fixture):
    conn, inverter_class, _ = inverters_fixture
    inverters = await solax.discover(*conn, return_when=asyncio.ALL_COMPLETED)
    assert inverter_class in {type(inverter) for inverter in inverters}

    for inverter in inverters:
        if isinstance(inverter, inverter_class):
            data = await inverter.get_data()
            assert "X" * 7 in (data.inverter_serial_number or "X" * 7)
            assert data.serial_number == data.dongle_serial_number


@pytest.mark.asyncio
async def test_real_time_api(inverters_fixture):
    conn, inverter_class, _ = inverters_fixture

    if inverter_class is not X1Boost:
        pytest.skip()

    rt_api = await solax.real_time_api(*conn)
    assert rt_api.inverter.__class__ is inverter_class


@pytest.mark.asyncio
async def test_discovery_cancelled_error_while_staggering(
    inverters_fixture,
):
    conn, inverter_class, _ = inverters_fixture

    if inverter_class is not X1Boost:
        pytest.skip()

    task = asyncio.create_task(
        solax.discover(*conn, return_when=asyncio.FIRST_EXCEPTION)
    )
    await asyncio.sleep(1)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


@pytest.mark.asyncio
async def test_discovery_cancelled_error_after_staggering(
    inverters_fixture,
):
    conn, inverter_class, _ = inverters_fixture

    if inverter_class is not X1Boost:
        pytest.skip()

    inverters = set(REGISTRY)
    inverters.add(DelayedX1Boost)

    task = asyncio.create_task(
        solax.discover(*conn, inverters=inverters, return_when=asyncio.FIRST_EXCEPTION)
    )
    await asyncio.sleep(7)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


@pytest.mark.asyncio
async def test_discovery_first_completed_after_staggering(
    inverters_fixture,
):
    conn, inverter_class, _ = inverters_fixture

    if inverter_class is not X1Boost:
        pytest.skip()

    inverter = await solax.discover(
        *conn, inverters=[DelayedX1Boost], return_when=asyncio.FIRST_COMPLETED
    )
    assert inverter.__class__ is DelayedX1Boost


@pytest.mark.asyncio
async def test_discovery_not_first_completed_after_staggering(
    inverters_fixture,
):
    conn, inverter_class, _ = inverters_fixture

    if inverter_class is not X1Boost:
        pytest.skip()

    inverters = await solax.discover(
        *conn,
        inverters=[DelayedX1Boost, DelayedFailedX1Boost],
        return_when=asyncio.FIRST_EXCEPTION
    )
    assert DelayedX1Boost in {type(inverter) for inverter in inverters}


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


@pytest.mark.asyncio
async def test_discovery_empty_inverter_class_iterable():
    with pytest.raises(DiscoveryError):
        await solax.discover("localhost", 2, inverters=[])
