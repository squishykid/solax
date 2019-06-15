"""Support for Solax inverter via local API."""
import asyncio
import json

import logging

import aiohttp
import async_timeout
import voluptuous as vol

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

    'Battery Energy':             (19, 'kWh'),

    'Grid Frequency':             (50, 'Hz'),
    'EPS Voltage':                (53, 'V'),
    'EPS Current':                (54, 'A'),
    'EPS Power':                  (55, 'W'),
    'EPS Frequency':              (56, 'Hz'),
}

REQUEST_TIMEOUT = 5

REAL_TIME_DATA_ENDPOINT = 'http://{ip_address}/api/realTimeData.htm'

DATA_SCHEMA = vol.Schema(
    vol.All([vol.Coerce(float)], vol.Length(min=68, max=68))
)

REAL_TIME_DATA_SCHEMA = vol.Schema({
    vol.Required('method'): str,
    vol.Required('version'): str,
    vol.Required('type'): str,
    vol.Required('SN'): str,
    vol.Required('Data'): DATA_SCHEMA,
    vol.Required('Status'): vol.All(vol.Coerce(int), vol.Range(min=0)),
}, extra=vol.REMOVE_EXTRA)


class SolaxRequestError(Exception):
    """Error to indicate a Solax API request has failed."""


async def async_solax_real_time_request(schema, ip_address, retry,
                                        t_wait=0):  # pragma: no cover
    """Make call to inverter endpoint."""
    if t_wait > 0:
        msg = "Timeout connecting to Solax inverter, waiting %d to retry."
        _LOGGER.error(msg, t_wait)
        await asyncio.sleep(t_wait)
    new_wait = (t_wait*2)+5
    retry = retry - 1
    try:
        async with aiohttp.ClientSession() as session:
            with async_timeout.timeout(REQUEST_TIMEOUT):
                url = REAL_TIME_DATA_ENDPOINT.format(ip_address=ip_address)
                req = await session.get(url)
        garbage = await req.read()
        formatted = garbage.decode("utf-8")
        formatted = formatted.replace(",,", ",0.0,").replace(",,", ",0.0,")
        json_response = json.loads(formatted)
        return schema(json_response)
    except asyncio.TimeoutError:
        if retry > 0:
            return await async_solax_real_time_request(schema,
                                                       ip_address,
                                                       retry,
                                                       new_wait)
        _LOGGER.error("Too many timeouts connecting to Solax.")
    except (aiohttp.ClientError) as client_err:
        _LOGGER.error("Could not connect to Solax API endpoint")
        _LOGGER.error(client_err)
    except ValueError:
        _LOGGER.error("Received non-JSON data from Solax API endpoint")
    except vol.Invalid as err:
        _LOGGER.error("Received unexpected JSON from Solax"
                      " API endpoint: %s", err)
        _LOGGER.error(json_response)
    raise SolaxRequestError


def parse_solax_real_time_response(response):
    """Manipulate the response from solax real time api."""
    data_list = response['Data']
    result = {}
    for name, index in INVERTER_SENSORS.items():
        response_index = index[0]
        result[name] = data_list[response_index]
    return result


class RealTimeAPI:  # pragma: no cover
    """Solax inverter real time API"""
    # pylint: disable=too-few-public-methods

    def __init__(self, ip_address):
        """Initialize the API client."""
        self.ip_address = ip_address

    async def get_data(self):
        """Query the real time API"""
        resp = await async_solax_real_time_request(REAL_TIME_DATA_SCHEMA,
                                                   self.ip_address,
                                                   3)
        return parse_solax_real_time_response(resp)
