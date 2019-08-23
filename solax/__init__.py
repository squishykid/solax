"""Support for Solax inverter via local API."""
import asyncio
import json

import logging
from collections import namedtuple

import aiohttp
import async_timeout
import voluptuous as vol

from solax import inverter

_LOGGER = logging.getLogger(__name__)

# key: name of sensor
# value.0: index
# value.1: unit (String) or None
# from https://github.com/GitHobi/solax/wiki/direct-data-retrieval
INVERTER_SENSORS = {
    'PV1 Current':                (0, 'A'),
    'PV2 Current':                (1, 'A'),
    'PV1 Voltage':                (2, 'V'),
    'PV2 Voltage':                (3, 'V'),

    'Output Current':             (4, 'A'),
    'Network Voltage':            (5, 'V'),
    'Power Now':                  (6, 'W'),

    'Inverter Temperature':       (7, 'C'),
    'Today\'s Energy':            (8, 'kWh'),
    'Total Energy':               (9, 'kWh'),
    'Exported Power':             (10, 'W'),
    'PV1 Power':                  (11, 'W'),
    'PV2 Power':                  (12, 'W'),

    'Battery Voltage':            (13, 'V'),
    'Battery Current':            (14, 'A'),
    'Battery Power':              (15, 'W'),
    'Battery Temperature':        (16, 'C'),
    'Battery Remaining Capacity': (17, '%'),

    'Month\'s Energy':            (19, 'kWh'),

    'Grid Frequency':             (50, 'Hz'),
    'EPS Voltage':                (53, 'V'),
    'EPS Current':                (54, 'A'),
    'EPS Power':                  (55, 'W'),
    'EPS Frequency':              (56, 'Hz'),
}

REQUEST_TIMEOUT = 5

class SolaxRequestError(Exception):
    """Error to indicate a Solax API request has failed."""


async def rt_request(inverter, retry, t_wait=0):
    """Make call to inverter endpoint."""
    if t_wait > 0:
        msg = "Timeout connecting to Solax inverter, waiting %d to retry."
        _LOGGER.error(msg, t_wait)
        await asyncio.sleep(t_wait)
    new_wait = (t_wait*2)+5
    retry = retry - 1
    try:
        with async_timeout.timeout(REQUEST_TIMEOUT):
            return await inverter.get_data()
    except asyncio.TimeoutError:
        if retry > 0:
            return await rt_request(inverter,
                                    retry,
                                    new_wait)
        _LOGGER.error("Too many timeouts connecting to Solax.")
        raise


RealTimeResponse = namedtuple('RealTimeResponse',
                              'data, serial_number, version, type, status')


def parse_solax_real_time_response(response):
    """Manipulate the response from solax real time api."""
    data_list = response['Data']
    result = {}
    for name, index in INVERTER_SENSORS.items():
        response_index = index[0]
        result[name] = data_list[response_index]
    return RealTimeResponse(data=result,
                            serial_number=response['SN'],
                            version=response['version'],
                            type=response['type'],
                            status=response['Status'])


class RealTimeAPI:  # pragma: no cover
    """Solax inverter real time API"""
    # pylint: disable=too-few-public-methods

    async def __init__(self, ip_address):
        """Initialize the API client."""
        self.inverter = await inverter.discover(ip_address, 80)

    async def get_data(self):
        """Query the real time API"""
        resp = await rt_request(self.inverter,
                                3)
        return parse_solax_real_time_response(resp)
