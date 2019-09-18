import json
from collections import namedtuple

import aiohttp
import voluptuous as vol


class InverterError(Exception):
    """Indicates error communicating with inverter"""


class DiscoveryError(Exception):
    """Raised when unable to discover inverter"""


InverterResponse = namedtuple('InverterResponse',
                              'data, serial_number, version, type')


class Inverter:
    """Base wrapper around Inverter HTTP API"""
    def __init__(self, host, port):
        self.host = host
        self.port = port

    async def get_data(self):
        try:
            data = await self.make_request(
                self.host, self.port
            )
        except aiohttp.ClientError as ex:
            msg = "Could not connect to inverter endpoint"
            raise InverterError(msg) from ex
        except ValueError as ex:
            msg = "Received non-JSON data from inverter endpoint"
            raise InverterError(msg) from ex
        except vol.Invalid as ex:
            msg = "Received malformed JSON from inverter"
            raise InverterError(msg) from ex
        return data

    @classmethod
    async def make_request(cls, host, port):
        """
        Return instance of 'InverterResponse'
        Raise exception if unable to get data
        """
        raise NotImplementedError()

    @classmethod
    def sensor_map(cls):
        """
        Return sensor map
        """
        raise NotImplementedError()

    @staticmethod
    def map_response(resp_data, sensor_map):
        return {
            sensor_name: resp_data[i]
            for sensor_name, (i, _)
            in sensor_map.items()
        }


async def discover(host, port) -> Inverter:
    for inverter in REGISTRY:
        i = inverter(host, port)
        try:
            await i.get_data()
            return i
        except InverterError:
            pass
    raise DiscoveryError()


class XHybrid(Inverter):
    """
    Tested with:
    * SK-TL5000E
    """
    __schema = vol.Schema({
        vol.Required('method'): str,
        vol.Required('version'): str,
        vol.Required('type'): str,
        vol.Required('SN'): str,
        vol.Required('Data'): vol.Schema(
            vol.All(
                [vol.Coerce(float)],
                vol.Any(vol.Length(min=58, max=58), vol.Length(min=68, max=68))
                )
            ),
        vol.Required('Status'): vol.All(vol.Coerce(int), vol.Range(min=0)),
    }, extra=vol.REMOVE_EXTRA)

    # key: name of sensor
    # value.0: index
    # value.1: unit (String) or None
    # from https://github.com/GitHobi/solax/wiki/direct-data-retrieval
    __sensor_map = {
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

    @classmethod
    async def make_request(cls, host, port=80):
        base = 'http://{}:{}/api/realTimeData.htm'
        url = base.format(host, port)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as req:
                garbage = await req.read()
        formatted = garbage.decode("utf-8")
        formatted = formatted.replace(",,", ",0.0,").replace(",,", ",0.0,")
        json_response = json.loads(formatted)
        response = cls.__schema(json_response)
        return InverterResponse(
            data=cls.map_response(response['Data'], cls.__sensor_map),
            serial_number=response['SN'],
            version=response['version'],
            type=response['type']
        )

    @classmethod
    def sensor_map(cls):
        """
        Return sensor map
        """
        return cls.__sensor_map


# registry of inverters
REGISTRY = [XHybrid]
