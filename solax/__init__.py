"""Support for Solax inverter via local API."""

import asyncio
import logging

from solax.discovery import discover
from solax.inverter import Inverter, InverterResponse
from solax.inverter_http_client import REQUEST_TIMEOUT

_LOGGER = logging.getLogger(__name__)

__all__ = (
    "discover",
    "real_time_api",
    "rt_request",
    "Inverter",
    "InverterResponse",
    "RealTimeAPI",
    "REQUEST_TIMEOUT",
)


async def rt_request(inv: Inverter, retry, t_wait=0) -> InverterResponse:
    """Make call to inverter endpoint."""
    if t_wait > 0:
        msg = "Timeout connecting to Solax inverter, waiting %d to retry."
        _LOGGER.error(msg, t_wait)
        await asyncio.sleep(t_wait)
    new_wait = (t_wait * 2) + 5
    retry = retry - 1
    try:
        return await inv.get_data()
    except asyncio.TimeoutError:
        if retry > 0:
            return await rt_request(inv, retry, new_wait)
        _LOGGER.error("Too many timeouts connecting to Solax.")
        raise


async def real_time_api(ip_address, port=80, pwd=""):
    i = await discover(ip_address, port, pwd, return_when=asyncio.FIRST_COMPLETED)
    return RealTimeAPI(i)


class RealTimeAPI:
    """Solax inverter real time API"""

    # pylint: disable=too-few-public-methods

    def __init__(self, inv: Inverter):
        """Initialize the API client."""
        self.inverter = inv

    async def get_data(self) -> InverterResponse:
        """Query the real time API"""
        return await rt_request(self.inverter, 3)
