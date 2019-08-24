from unittest.mock import Mock
import asyncio
import pytest
import solax


@pytest.mark.asyncio
async def test_waits_when_asked(monkeypatch):
    sleep_f = asyncio.Future()
    sleep_f.set_result(None)
    mock_sleep = Mock(return_value=sleep_f)
    monkeypatch.setattr(asyncio, 'sleep', mock_sleep)

    inv = Mock()
    get_data_f = asyncio.Future()
    get_data_f.set_result({})
    inv.get_data = Mock(return_value=get_data_f)

    wait_time = 2
    await solax.rt_request(inv, 10, wait_time)

    mock_sleep.assert_called_once_with(wait_time)
    inv.get_data.assert_called_once()


@pytest.mark.asyncio
async def test_tries_again_on_timeout(monkeypatch):
    sleep_f = asyncio.Future()
    sleep_f.set_result(None)
    mock_sleep = Mock(return_value=sleep_f)
    monkeypatch.setattr(asyncio, 'sleep', mock_sleep)

    inv = Mock()
    get_data_f = asyncio.Future()
    get_data_f.set_exception(asyncio.TimeoutError)
    inv.get_data = Mock(return_value=get_data_f)

    wait_time = 2
    with pytest.raises(asyncio.TimeoutError):
        await solax.rt_request(inv, 2, wait_time)

    assert mock_sleep.call_count == 2
    assert inv.get_data.call_count == 2
