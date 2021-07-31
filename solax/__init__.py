"""Support for Solax inverter via local API."""
import asyncio

import logging

import async_timeout

from solax import inverter

_LOGGER = logging.getLogger(__name__)


REQUEST_TIMEOUT = 5


async def rt_request(inv, retry, t_wait=0):
    """Make call to inverter endpoint."""
    if t_wait > 0:
        msg = "Timeout connecting to Solax inverter, waiting %d to retry."
        _LOGGER.error(msg, t_wait)
        await asyncio.sleep(t_wait)
    new_wait = (t_wait*2)+5
    retry = retry - 1
    try:
        with async_timeout.timeout(REQUEST_TIMEOUT):
            return await inv.get_data()
    except asyncio.TimeoutError:
        if retry > 0:
            return await rt_request(inv,
                                    retry,
                                    new_wait)
        _LOGGER.error("Too many timeouts connecting to Solax.")
        raise


async def real_time_api(ip_address, port=80, pwd=''):
    i = await inverter.discover(ip_address, port, pwd)
    return RealTimeAPI(i)


class RealTimeAPI:
    """Solax inverter real time API"""
    # pylint: disable=too-few-public-methods

    def __init__(self, inv):
        """Initialize the API client."""
        self.inverter = inv

    async def get_data(self):
        """Query the real time API"""
        return await rt_request(self.inverter,
                                3)
