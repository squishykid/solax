import json
from collections import namedtuple

import aiohttp
import voluptuous as vol
from voluptuous import Invalid


class InverterError(Exception):
    """Indicates error communicating with inverter"""


class DiscoveryError(Exception):
    """Raised when unable to discover inverter"""


InverterResponse = namedtuple('InverterResponse',
                              'data, serial_number, version, type')

InterverTypes = {
    1: 'X1-LX',
    2: 'X-Hybrid',
    3: 'X1-Hybiyd/Fit',
    4: 'X1-Boost/Air/Mini',
    5: 'X3-Hybiyd/Fit',
    6: 'X3-20K/30K',
    7: 'X3-MIC/PRO',
    8: 'X1-Smart',
    9: 'X1-AC',
    10: 'A1-Hybrid',
    11: 'A1-Fit',
    12: 'A1-Grid',
    13: 'J1-ESS',
}


class Inverter:
    """Base wrapper around Inverter HTTP API"""

    def __init__(self, host, port, pwd=''):
        self.host = host
        self.port = port
        self.pwd = pwd

    async def get_data(self):
        try:
            data = await self.make_request(
                self.host, self.port, self.pwd
            )
        except aiohttp.ClientError as ex:
            msg = "Could not connect to inverter endpoint"
            raise InverterError(msg, str(self.__class__.__name__)) from ex
        except ValueError as ex:
            msg = "Received non-JSON data from inverter endpoint"
            raise InverterError(msg, str(self.__class__.__name__)) from ex
        except vol.Invalid as ex:
            msg = "Received malformed JSON from inverter"
            raise InverterError(msg, str(self.__class__.__name__)) from ex
        return data

    @classmethod
    async def make_request(cls, host, port, pwd=''):
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

    @classmethod
    def schema(cls):
        """
        Return schema
        """
        raise NotImplementedError()

    @staticmethod
    def map_response(resp_data, sensor_map):
        return {
            sensor_name: round(resp_data[i] * factor, 2)
            for sensor_name, (i, _, factor)
            in sensor_map.items()
        }


async def discover(host, port, pwd='') -> Inverter:
    failures = []
    for inverter in REGISTRY:
        i = inverter(host, port, pwd)
        try:
            await i.get_data()
            return i
        except InverterError as ex:
            failures.append(ex)
    msg = (
        "Unable to connect to the inverter at "
        f"host={host} port={port}, or your inverter is not supported yet.\n"
        "Please see https://github.com/squishykid/solax/wiki/DiscoveryError\n"
        f"Failures={str(failures)}"
    )
    raise DiscoveryError(msg)


def startswith(something):
    def inner(actual):
        if isinstance(actual, str):
            if actual.startswith(something):
                return actual
        raise Invalid(f"{str(actual)} does not start with {something}")
    return inner


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
        'PV1 Current':                (0, 'A', 1),
        'PV2 Current':                (1, 'A', 1),
        'PV1 Voltage':                (2, 'V', 1),
        'PV2 Voltage':                (3, 'V', 1),

        'Output Current':             (4, 'A', 1),
        'Network Voltage':            (5, 'V', 1),
        'Power Now':                  (6, 'W', 1),

        'Inverter Temperature':       (7, 'C', 1),
        'Today\'s Energy':            (8, 'kWh', 1),
        'Total Energy':               (9, 'kWh', 1),
        'Exported Power':             (10, 'W', 1),
        'PV1 Power':                  (11, 'W', 1),
        'PV2 Power':                  (12, 'W', 1),

        'Battery Voltage':            (13, 'V', 1),
        'Battery Current':            (14, 'A', 1),
        'Battery Power':              (15, 'W', 1),
        'Battery Temperature':        (16, 'C', 1),
        'Battery Remaining Capacity': (17, '%', 1),

        'Month\'s Energy':            (19, 'kWh', 1),

        'Grid Frequency':             (50, 'Hz', 1),
        'EPS Voltage':                (53, 'V', 1),
        'EPS Current':                (54, 'A', 1),
        'EPS Power':                  (55, 'W', 1),
        'EPS Frequency':              (56, 'Hz', 1),
    }

    @classmethod
    async def make_request(cls, host, port=80, pwd=''):
        base = 'http://{}:{}/api/realTimeData.htm'
        url = base.format(host, port)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as req:
                garbage = await req.read()
        formatted = garbage.decode("utf-8")
        formatted = formatted.replace(",,", ",0.0,").replace(",,", ",0.0,")
        json_response = json.loads(formatted)
        response = cls.schema()(json_response)
        return InverterResponse(
            data=cls.map_response(response['Data'], cls.__sensor_map),
            serial_number=response['SN'],
            version=response['version'],
            type=response['type']
        )

    @classmethod
    def sensor_map(cls):
        return cls.__sensor_map

    @classmethod
    def schema(cls):
        return cls.__schema


class InverterPost(Inverter):
    # This is an intermediate abstract class,
    #  so we can disable the pylint warning
    # pylint: disable=W0223
    @classmethod
    async def make_request(cls, host, port=80, pwd=''):
        if not pwd:
            base = 'http://{}:{}/?optType=ReadRealTimeData'
            url = base.format(host, port)
        else:
            base = 'http://{}:{}/?optType=ReadRealTimeData&pwd={}&'
            url = base.format(host, port, pwd)
        async with aiohttp.ClientSession() as session:
            async with session.post(url) as req:
                resp = await req.read()
        raw_json = resp.decode("utf-8")
        json_response = json.loads(raw_json)
        response = cls.schema()(json_response)
        return InverterResponse(
            data=cls.map_response(response['Data'], cls.sensor_map()),
            serial_number=response.get('SN') or response.get('sn', 1),
            version=response['ver'],
            type=response['type'] if not isinstance(
                response['type'], int) else InterverTypes[response['type']]
        )


class X3(InverterPost):
    __schema = vol.Schema({
        vol.Required('type'): vol.All(
            str,
            startswith("X3-")
        ),
        vol.Required('SN'): str,
        vol.Required('ver'): str,
        vol.Required('Data'): vol.Schema(
            vol.All(
                [vol.Coerce(float)],
                vol.Any(
                    vol.Length(min=102, max=103),
                    vol.Length(min=107, max=107)),
                )
            ),
        vol.Required('Information'): vol.Schema(
            vol.All(
                vol.Length(min=9, max=9)
                )
            ),
    }, extra=vol.REMOVE_EXTRA)

    __sensor_map = {
        'PV1 Current':                (0, 'A', 1),
        'PV2 Current':                (1, 'A', 1),
        'PV1 Voltage':                (2, 'V', 1),
        'PV2 Voltage':                (3, 'V', 1),

        'Output Current Phase 1':     (4, 'A', 1),
        'Network Voltage Phase 1':    (5, 'V', 1),
        'AC Power':                   (6, 'W', 1),

        'Inverter Temperature':       (7, 'C', 1),
        'Today\'s Energy':            (8, 'kWh', 1),
        'Total Energy':               (9, 'kWh', 1),
        'Exported Power':             (10, 'W', 1),
        'PV1 Power':                  (11, 'W', 1),
        'PV2 Power':                  (12, 'W', 1),

        'Battery Voltage':            (13, 'V', 1),
        'Battery Current':            (14, 'A', 1),
        'Battery Power':              (15, 'W', 1),
        'Battery Temperature':        (16, 'C', 1),
        'Battery Remaining Capacity': (21, '%', 1),

        'Total Feed-in Energy':       (41, 'kWh', 1),
        'Total Consumption':          (42, 'kWh', 1),

        'Power Now Phase 1':          (43, 'W', 1),
        'Power Now Phase 2':          (44, 'W', 1),
        'Power Now Phase 3':          (45, 'W', 1),
        'Output Current Phase 2':     (46, 'A', 1),
        'Output Current Phase 3':     (47, 'A', 1),
        'Network Voltage Phase 2':    (48, 'V', 1),
        'Network Voltage Phase 3':    (49, 'V', 1),

        'Grid Frequency Phase 1':     (50, 'Hz', 1),
        'Grid Frequency Phase 2':     (51, 'Hz', 1),
        'Grid Frequency Phase 3':     (52, 'Hz', 1),

        'EPS Voltage':                (53, 'V', 1),
        'EPS Current':                (54, 'A', 1),
        'EPS Power':                  (55, 'W', 1),
        'EPS Frequency':              (56, 'Hz', 1),
    }

    @classmethod
    def sensor_map(cls):
        """
        Return sensor map
        """
        return cls.__sensor_map

    @classmethod
    def schema(cls):
        return cls.__schema


class X1(InverterPost):
    __schema = vol.Schema({
        vol.Required('type'): vol.All(
            str,
            startswith("X1-")
        ),
        vol.Required('SN'): str,
        vol.Required('ver'): str,
        vol.Required('Data'): vol.Schema(
            vol.All(
                [vol.Coerce(float)],
                vol.Any(
                    vol.Length(min=102, max=102),
                    vol.Length(min=103, max=103),
                    vol.Length(min=107, max=107),
                ),
            )
        ),
        vol.Required('Information'): vol.Schema(
            vol.All(
                vol.Length(min=9, max=9)
                )
            ),
    }, extra=vol.REMOVE_EXTRA)

    __sensor_map = {
        'PV1 Current':                (0, 'A', 1),
        'PV2 Current':                (1, 'A', 1),
        'PV1 Voltage':                (2, 'V', 1),
        'PV2 Voltage':                (3, 'V', 1),

        'Output Current':             (4, 'A', 1),
        'Network Voltage':            (5, 'V', 1),
        'AC Power':                   (6, 'W', 1),

        'Inverter Temperature':       (7, 'C', 1),
        'Today\'s Energy':            (8, 'kWh', 1),
        'Total Energy':               (9, 'kWh', 1),
        'Exported Power':             (10, 'W', 1),
        'PV1 Power':                  (11, 'W', 1),
        'PV2 Power':                  (12, 'W', 1),

        'Battery Voltage':            (13, 'V', 1),
        'Battery Current':            (14, 'A', 1),
        'Battery Power':              (15, 'W', 1),
        'Battery Temperature':        (16, 'C', 1),
        'Battery Remaining Capacity': (21, '%', 1),

        'Total Feed-in Energy':       (41, 'kWh', 1),
        'Total Consumption':          (42, 'kWh', 1),

        'Power Now':                  (43, 'W', 1),
        'Grid Frequency':             (50, 'Hz', 1),

        'EPS Voltage':                (53, 'V', 1),
        'EPS Current':                (54, 'A', 1),
        'EPS Power':                  (55, 'W', 1),
        'EPS Frequency':              (56, 'Hz', 1),
    }

    @classmethod
    def sensor_map(cls):
        return cls.__sensor_map

    @classmethod
    def schema(cls):
        return cls.__schema


class X1Mini(InverterPost):
    __schema = vol.Schema({
        vol.Required('type'): vol.All(
            str,
            startswith("X1-")
        ),
        vol.Required('SN'): str,
        vol.Required('ver'): str,
        vol.Required('Data'): vol.Schema(
            vol.All(
                [vol.Coerce(float)],
                vol.Length(min=69, max=69),
            )
        ),
        vol.Required('Information'): vol.Schema(
            vol.All(
                vol.Length(min=9, max=9)
                )
            ),
    }, extra=vol.REMOVE_EXTRA)

    __sensor_map = {
        'PV1 Current':                (0, 'A', 1),
        'PV2 Current':                (1, 'A', 1),
        'PV1 Voltage':                (2, 'V', 1),
        'PV2 Voltage':                (3, 'V', 1),

        'Output Current':             (4, 'A', 1),
        'Network Voltage':            (5, 'V', 1),
        'AC Power':                   (6, 'W', 1),

        'Inverter Temperature':       (7, 'C', 1),
        'Today\'s Energy':            (8, 'kWh', 1),
        'Total Energy':               (9, 'kWh', 1),
        'Exported Power':             (10, 'W', 1),
        'PV1 Power':                  (11, 'W', 1),
        'PV2 Power':                  (12, 'W', 1),

        'Total Feed-in Energy':       (41, 'kWh', 1),
        'Total Consumption':          (42, 'kWh', 1),

        'Power Now':                  (43, 'W', 1),
        'Grid Frequency':             (50, 'Hz', 1),
    }

    @ classmethod
    def sensor_map(cls):
        return cls.__sensor_map

    @ classmethod
    def schema(cls):
        return cls.__schema


class X1MiniV34(InverterPost):
    __schema = vol.Schema({
        vol.Required('type', 'type'): vol.All(int, vol.Equal(4)),
        vol.Required('sn',): str,
        vol.Required('ver'): str,
        vol.Required('Data'): vol.Schema(
            vol.All(
                [vol.Coerce(float)],
                vol.Any(
                    vol.Length(min=69, max=69),
                    vol.Length(min=200, max=200),
                )
            )
        ),
        vol.Required('Information'): vol.Schema(
            vol.Any(
                vol.Length(min=9, max=9),
                vol.Length(min=10, max=10)
            )
        ),
    }, extra=vol.REMOVE_EXTRA)

    __sensor_map = {
        'Network Voltage':            (0, 'V', 0.1),
        'Output Current':             (1, 'A', 0.1),
        'AC Power':                   (2, 'W', 1),
        'PV1 Voltage':                (3, 'V', 0.1),
        'PV2 Voltage':                (4, 'V', 0.1),
        'PV1 Current':                (5, 'A', 0.1),
        'PV2 Current':                (6, 'A', 0.1),
        'PV1 Power':                  (7, 'W', 1),
        'PV2 Power':                  (8, 'W', 1),
        'Grid Frequency':             (9, 'Hz', 0.01),
        'Total Energy':               (11, 'kWh', 0.1),
        'Today\'s Energy':            (13, 'kWh', 0.1),
        # 'Exported Power':             (8, 'W', 0.1),
        # 'Inverter Temperature':       (7, 'C', 0.1),
        'Total Feed-in Energy':       (41, 'kWh', 0.1),
        'Total Consumption':          (42, 'kWh', 0.1),
        'Power Now':                  (43, 'W', 0.1),
    }

    @ classmethod
    def sensor_map(cls):
        return cls.__sensor_map

    @ classmethod
    def schema(cls):
        return cls.__schema


# registry of inverters
REGISTRY = [XHybrid, X3, X1, X1MiniV34, X1Mini]
