import json
from collections import namedtuple

import aiohttp
import voluptuous as vol
from voluptuous import Invalid, MultipleInvalid
from voluptuous.humanize import humanize_error


class InverterError(Exception):
    """Indicates error communicating with inverter"""


class DiscoveryError(Exception):
    """Raised when unable to discover inverter"""


InverterResponse = namedtuple('InverterResponse',
                              'data, serial_number, version, type')


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
        result = {}
        for sensor_name, (idx, unit, *conv) in sensor_map.items():
          if conv:
            val = conv[0](resp_data[idx])
          else:
            val = resp_data[idx]
          result[sensor_name] = val
        return result

    @classmethod
    def postprocess_response(cls, response):
      return response


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
        response = {}
        try:
          response = cls.schema()(json_response)
        except (Invalid, MultipleInvalid) as ex:
          msg = humanize_error(json_response, ex)
          # print(msg)
          raise
        if 'SN' in response:
          serial_number = response['SN']
        else:
          serial_number = response['sn']
        return InverterResponse(
            data=cls.postprocess_response(
              cls.map_response(response['Data'], cls.sensor_map())
            ),
            serial_number=serial_number,
            version=response['ver'],
            type=response['type']
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
        'PV1 Current':                (0, 'A'),
        'PV2 Current':                (1, 'A'),
        'PV1 Voltage':                (2, 'V'),
        'PV2 Voltage':                (3, 'V'),

        'Output Current Phase 1':     (4, 'A'),
        'Network Voltage Phase 1':    (5, 'V'),
        'AC Power':                   (6, 'W'),

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
        'Battery Remaining Capacity': (21, '%'),

        'Total Feed-in Energy':       (41, 'kWh'),
        'Total Consumption':          (42, 'kWh'),

        'Power Now Phase 1':          (43, 'W'),
        'Power Now Phase 2':          (44, 'W'),
        'Power Now Phase 3':          (45, 'W'),
        'Output Current Phase 2':     (46, 'A'),
        'Output Current Phase 3':     (47, 'A'),
        'Network Voltage Phase 2':    (48, 'V'),
        'Network Voltage Phase 3':    (49, 'V'),

        'Grid Frequency Phase 1':     (50, 'Hz'),
        'Grid Frequency Phase 2':     (51, 'Hz'),
        'Grid Frequency Phase 3':     (52, 'Hz'),

        'EPS Voltage':                (53, 'V'),
        'EPS Current':                (54, 'A'),
        'EPS Power':                  (55, 'W'),
        'EPS Frequency':              (56, 'Hz'),
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


def _div10(x):
  return x / 10


def _div100(x):
  return x / 100


def _toSigned(x):
  if x > 32767:
    return x - 65535
  else:
    return x


class X3_V34(InverterPost):
    __schema = vol.Schema({
        vol.Required('type'): vol.All(int, 5),
        vol.Required('sn'): str,
        vol.Required('ver'): str,
        vol.Required('Data'): vol.Schema(
            vol.All(
                [vol.Coerce(float)],
                vol.Length(min=200, max=200),
                )
            ),
        vol.Required('Information'): vol.Schema(
            vol.All(
                vol.Length(min=10, max=10)
                )
            ),
    }, extra=vol.REMOVE_EXTRA)

    __sensor_map = {
        'Network Voltage Phase 1':    (0, 'V', _div10),
        'Network Voltage Phase 2':    (1, 'V', _div10),
        'Network Voltage Phase 3':    (2, 'V', _div10),

        'Output Current Phase 1':     (3, 'A', _div10),
        'Output Current Phase 2':     (4, 'A', _div10),
        'Output Current Phase 3':     (5, 'A', _div10),

        'Power Now Phase 1':          (6, 'W'),
        'Power Now Phase 2':          (7, 'W'),
        'Power Now Phase 3':          (8, 'W'),

        'PV1 Voltage':                (9, 'V', _div10),
        'PV2 Voltage':                (10, 'V', _div10),
        'PV1 Current':                (11, 'A', _div10),
        'PV2 Current':                (12, 'A', _div10),
        'PV1 Power':                  (13, 'W'),
        'PV2 Power':                  (14, 'W'),

        'Grid Frequency Phase 1':     (15, 'Hz', _div100),
        'Grid Frequency Phase 2':     (16, 'Hz', _div100),
        'Grid Frequency Phase 3':     (17, 'Hz', _div100),

        'Total Energy':               (19, 'kWh', _div10),
        'Today\'s Energy':            (21, 'kWh', _div10),

        'Battery Voltage':            (24, 'V', _div100),
        'Battery Current':            (25, 'A', lambda x: _div10(_toSigned(x))),
        'Battery Power':              (26, 'W', _toSigned),
        'Battery Temperature':        (27, 'C'),
        'Battery Remaining Capacity': (28, '%'),

        'Exported Power':             (65, 'W', _toSigned),
        'Total Feed-in Energy':       (67, 'kWh'),
        'Total Feed-in Energy Resets':(68, ''),
        'Total Consumption':          (69, 'kWh'),
        'Total Consumption Resets':   (70, ''),

        'AC Power':                   (181, 'W'),
    }

    @classmethod
    def postprocess_response(cls, response):
      response['Total Feed-in Energy'] += \
          response['Total Feed-in Energy Resets'] * 65535
      response['Total Feed-in Energy'] /= 100
      response['Total Consumption'] += \
          response['Total Consumption Resets'] * 65535
      response['Total Consumption'] /= 100
      return response

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
        'PV1 Current':                (0, 'A'),
        'PV2 Current':                (1, 'A'),
        'PV1 Voltage':                (2, 'V'),
        'PV2 Voltage':                (3, 'V'),

        'Output Current':             (4, 'A'),
        'Network Voltage':            (5, 'V'),
        'AC Power':                   (6, 'W'),

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
        'Battery Remaining Capacity': (21, '%'),

        'Total Feed-in Energy':       (41, 'kWh'),
        'Total Consumption':          (42, 'kWh'),

        'Power Now':                  (43, 'W'),
        'Grid Frequency':             (50, 'Hz'),

        'EPS Voltage':                (53, 'V'),
        'EPS Current':                (54, 'A'),
        'EPS Power':                  (55, 'W'),
        'EPS Frequency':              (56, 'Hz'),
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
        'PV1 Current':                (0, 'A'),
        'PV2 Current':                (1, 'A'),
        'PV1 Voltage':                (2, 'V'),
        'PV2 Voltage':                (3, 'V'),

        'Output Current':             (4, 'A'),
        'Network Voltage':            (5, 'V'),
        'AC Power':                   (6, 'W'),

        'Inverter Temperature':       (7, 'C'),
        'Today\'s Energy':            (8, 'kWh'),
        'Total Energy':               (9, 'kWh'),
        'Exported Power':             (10, 'W'),
        'PV1 Power':                  (11, 'W'),
        'PV2 Power':                  (12, 'W'),

        'Total Feed-in Energy':       (41, 'kWh'),
        'Total Consumption':          (42, 'kWh'),

        'Power Now':                  (43, 'W'),
        'Grid Frequency':             (50, 'Hz'),
    }

    @classmethod
    def sensor_map(cls):
        return cls.__sensor_map

    @classmethod
    def schema(cls):
        return cls.__schema


# registry of inverters
REGISTRY = [XHybrid, X3, X3_V34, X1, X1Mini]
