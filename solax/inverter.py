import json
from collections import namedtuple

import aiohttp
import voluptuous as vol
from voluptuous import Invalid, MultipleInvalid
from voluptuous.humanize import humanize_error
from solax.utils import (
    div10, div100, feedin_energy, total_energy, charge_energy, pv_energy,
    discharge_energy, consumption, twoway_div10, twoway_div100, to_signed,
    eps_total_energy, inverter_modes, battery_modes
)


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
    async def make_request(cls, host, port, pwd='', headers=None):
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
    def postprocess_map(cls):
        """
        Return map of functions to be applied to each sensor value
        """
        return {}

    @classmethod
    def schema(cls):
        """
        Return schema
        """
        raise NotImplementedError()

    @classmethod
    def map_response(cls, resp_data):
        result = {}
        for sensor_name, (idx, _) in cls.sensor_map().items():
            val = resp_data[idx]
            result[sensor_name] = val
        for sensor_name, processor in cls.postprocess_map().items():
            result[sensor_name] = processor(result[sensor_name], result)
        return result


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
    async def make_request(cls, host, port=80, pwd='', headers=None):
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
            data=cls.map_response(response['Data']),
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
    # pylint: disable=W0223,R0914
    @classmethod
    async def make_request(cls, host, port=80, pwd='', headers=None):
        if not pwd:
            base = 'http://{}:{}/?optType=ReadRealTimeData'
            url = base.format(host, port)
        else:
            base = 'http://{}:{}/?optType=ReadRealTimeData&pwd={}&'
            url = base.format(host, port, pwd)
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers) as req:
                resp = await req.read()
        raw_json = resp.decode("utf-8")
        json_response = json.loads(raw_json)
        response = {}
        try:
            response = cls.schema()(json_response)
        except (Invalid, MultipleInvalid) as ex:
            _ = humanize_error(json_response, ex)
            raise
        return InverterResponse(
            data=cls.map_response(response['Data']),
            serial_number=response.get('SN', response.get('sn')),
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


class X3V34(InverterPost):
    """X3 v2.034.06"""
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
        'Network Voltage Phase 1':               (0, 'V', div10),
        'Network Voltage Phase 2':               (1, 'V', div10),
        'Network Voltage Phase 3':               (2, 'V', div10),

        'Output Current Phase 1':                (3, 'A', twoway_div10),
        'Output Current Phase 2':                (4, 'A', twoway_div10),
        'Output Current Phase 3':                (5, 'A', twoway_div10),

        'Power Now Phase 1':                     (6, 'W', to_signed),
        'Power Now Phase 2':                     (7, 'W', to_signed),
        'Power Now Phase 3':                     (8, 'W', to_signed),

        'PV1 Voltage':                           (9, 'V', div10),
        'PV2 Voltage':                           (10, 'V', div10),
        'PV1 Current':                           (11, 'A', div10),
        'PV2 Current':                           (12, 'A', div10),
        'PV1 Power':                             (13, 'W'),
        'PV2 Power':                             (14, 'W'),

        'Total PV Energy':                       (89, 'kWh', pv_energy),
        'Total PV Energy Resets':                (90, ''),
        'Today\'s PV Energy':                    (112, 'kWh', div10),

        'Grid Frequency Phase 1':                (15, 'Hz', div100),
        'Grid Frequency Phase 2':                (16, 'Hz', div100),
        'Grid Frequency Phase 3':                (17, 'Hz', div100),

        'Total Energy':                          (19, 'kWh', total_energy),
        'Total Energy Resets':                   (20, ''),
        'Today\'s Energy':                       (21, 'kWh', div10),

        'Battery Voltage':                       (24, 'V', div100),
        'Battery Current':                       (25, 'A', twoway_div100),
        'Battery Power':                         (26, 'W', to_signed),
        'Battery Temperature':                   (27, 'C'),
        'Battery Remaining Capacity':            (28, '%'),

        'Total Battery Discharge Energy':        (30, 'kWh',
                                                  discharge_energy),
        'Total Battery Discharge Energy Resets': (31, ''),
        'Today\'s Battery Discharge Energy':     (113, 'kWh', div10),
        'Battery Remaining Energy':              (32, 'kWh', div10),
        'Total Battery Charge Energy':           (87, 'kWh', charge_energy),
        'Total Battery Charge Energy Resets':    (88, ''),
        'Today\'s Battery Charge Energy':        (114, 'kWh', div10),

        'Exported Power':                        (65, 'W', to_signed),
        'Total Feed-in Energy':                  (67, 'kWh', feedin_energy),
        'Total Feed-in Energy Resets':           (68, ''),
        'Total Consumption':                     (69, 'kWh', consumption),
        'Total Consumption Resets':              (70, ''),

        'AC Power':                              (181, 'W', to_signed),

        'EPS Frequency':                         (63, 'Hz', div100),
        'EPS Total Energy':                      (110, 'kWh',
                                                  eps_total_energy),
        'EPS Total Energy Resets':               (111, 'Hz'),
    }

    @classmethod
    def sensor_map(cls):
        """
        Return sensor map
        """
        sensors = {}
        for name, (idx, unit, *_) in cls.__sensor_map.items():
            sensors[name] = (idx, unit)
        return sensors

    @classmethod
    def postprocess_map(cls):
        """
        Return postprocessing map
        """
        sensors = {}
        for name, (_, _, *processor) in cls.__sensor_map.items():
            if processor:
                sensors[name] = processor[0]
        return sensors

    @classmethod
    def schema(cls):
        return cls.__schema


class QVOLTHYBG33P(InverterPost):
    """
    QCells
    Q.VOLT HYB-G3-3P
    """
    __schema = vol.Schema({
        vol.Required('type'): vol.All(int, 14),
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

        'Network Voltage Phase 1':               (0, 'V', div10),
        'Network Voltage Phase 2':               (1, 'V', div10),
        'Network Voltage Phase 3':               (2, 'V', div10),

        'Output Current Phase 1':                (3, 'A', twoway_div10),
        'Output Current Phase 2':                (4, 'A', twoway_div10),
        'Output Current Phase 3':                (5, 'A', twoway_div10),

        'Power Now Phase 1':                     (6, 'W', to_signed),
        'Power Now Phase 2':                     (7, 'W', to_signed),
        'Power Now Phase 3':                     (8, 'W', to_signed),

        'AC Power':                              (9, 'W', to_signed),

        'PV1 Voltage':                           (10, 'V', div10),
        'PV2 Voltage':                           (11, 'V', div10),

        'PV1 Current':                           (12, 'A', div10),
        'PV2 Current':                           (13, 'A', div10),

        'PV1 Power':                             (14, 'W'),
        'PV2 Power':                             (15, 'W'),

        'Grid Frequency Phase 1':                (16, 'Hz', div100),
        'Grid Frequency Phase 2':                (17, 'Hz', div100),
        'Grid Frequency Phase 3':                (18, 'Hz', div100),

        'Inverter Operation mode':               (19, '', inverter_modes),
        # 20 - 32: always 0
        # 33: always 1
        # instead of to_signed this is actually 34 - 35,
        # because 35 =  if 34>32767: 0 else: 65535
        'Exported Power':                        (34, 'W', to_signed),
        # 35: if 34>32767: 0 else: 65535
        # 36 - 38    : always  0
        'Battery Voltage':                       (39, 'V', div100),
        'Battery Current':                       (40, 'A', twoway_div100),
        'Battery Power':                         (41, 'W', to_signed),
        # 42: div10, almost identical to [39]
        # 43: twoway_div10,  almost the same as "40" (battery current)
        # 44: twoway_div100, almost the same as "41" (battery power),
        # 45: always 1
        # 46: follows PV Output, idles around 44, peaks at 52,
        'Power Now':                             (47, 'W', to_signed),
        # 48: always 256
        # 49,50: [49] + [50] * 15160 some increasing counter
        # 51: always 5634
        # 52: always 100
        # 53: always 0
        # 54: follows PV Output, idles around 35, peaks at 54,
        # 55-67: always 0
        'Total Energy':                          (68, 'kWh', total_energy),
        'Total Energy Resets':                   (69, ''),
        # 70: div10, today's energy including battery usage
        # 71-73: 0
        'Total Battery Discharge Energy':        (74, 'kWh', discharge_energy),
        'Total Battery Discharge Energy Resets': (75, ''),
        'Total Battery Charge Energy':           (76, 'kWh', charge_energy),
        'Total Battery Charge Energy Resets':    (77, ''),
        'Today\'s Battery Discharge Energy':     (78, 'kWh', div10),
        'Today\'s Battery Charge Energy':        (79, 'kWh', div10),
        'Total PV Energy':                       (80, 'kWh', pv_energy),
        'Total PV Energy Resets':                (81, ''),
        'Today\'s Energy':                       (82, 'kWh', div10),
        # 83-85: always 0
        'Total Feed-in Energy':                  (86, 'kWh', feedin_energy),
        'Total Feed-in Energy Resets':           (87, ''),
        'Total Consumption':                     (88, 'kWh', consumption),
        'Total Consumption Resets':              (89, ''),
        'Today\'s Feed-in Energy':               (90, 'kWh', div100),
        # 91: always 0
        'Today\'s Consumption':                  (92, 'kWh', div100),
        # 93-101: always 0
        # 102: always 1
        'Battery Remaining Capacity':            (103, '%'),
        # 104: always 1
        'Battery Temperature':                   (105, 'C'),
        'Battery Remaining Energy':              (106, 'kWh', div10),
        # 107: always 256 or 0
        # 108: always 3504
        # 109: always 2400
        # 110: around rise to 300 if battery not full, 0 if battery is full
        # 112, 113: range [250,350]; looks like 113 + offset = 112,
        #   peaks if battery is full
        # 114, 115: something around 33; Some temperature?!
        # 116: increases slowly [2,5]
        # 117-121: 1620	773	12850	12850	12850
        # 122-124: always 0
        # 125,126: some curve, look very similar to "42"(Battery Power),
        # with offset around 15
        # 127,128 resetting counter /1000, around battery charge + discharge
        # 164,165,166 some curves
        'Battery Operation mode':                (168, '', battery_modes),
        # 169: div100 same as [39]
        # 170-199: always 0

    }

    @classmethod
    def sensor_map(cls):
        """
        Return sensor map
        """
        sensors = {}
        for name, (idx, unit, *_) in cls.__sensor_map.items():
            sensors[name] = (idx, unit)
        return sensors

    @classmethod
    def postprocess_map(cls):
        """
        Return postprocessing map
        """
        sensors = {}
        for name, (_, _, *processor) in cls.__sensor_map.items():
            if processor:
                sensors[name] = processor[0]
        return sensors

    @classmethod
    def schema(cls):
        return cls.__schema

    @classmethod
    async def make_request(cls, host, port=80, pwd='', headers=None):

        url = f'http://{host}:{port}/'
        data = f'optType=ReadRealTimeData&pwd={pwd}'

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data) as req:
                resp = await req.read()

        raw_json = resp.decode("utf-8")
        json_response = json.loads(raw_json)
        response = {}
        try:
            response = cls.schema()(json_response)
        except (Invalid, MultipleInvalid) as ex:
            _ = humanize_error(json_response, ex)
            raise
        return InverterResponse(
            data=cls.map_response(response['Data']),
            serial_number=response.get('SN', response.get('sn')),
            version=response['ver'],
            type=response['type']
        )


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


class X1MiniV34(InverterPost):
    __schema = vol.Schema({
        vol.Required('type', 'type'): vol.All(int, 4),
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
        'Network Voltage':            (0, 'V', div10),
        'Output Current':             (1, 'A', div10),
        'AC Power':                   (2, 'W'),
        'PV1 Voltage':                (3, 'V', div10),
        'PV2 Voltage':                (4, 'V', div10),
        'PV1 Current':                (5, 'A', div10),
        'PV2 Current':                (6, 'A', div10),
        'PV1 Power':                  (7, 'W'),
        'PV2 Power':                  (8, 'W'),
        'Grid Frequency':             (9, 'Hz', div100),
        'Total Energy':               (11, 'kWh', div10),
        'Today\'s Energy':            (13, 'kWh', div10),
        'Total Feed-in Energy':       (41, 'kWh', div10),
        'Total Consumption':          (42, 'kWh', div10),
        'Power Now':                  (43, 'W', div10),
    }

    @classmethod
    def sensor_map(cls):
        """
        Return sensor map
        """
        sensors = {}
        for name, (idx, unit, *_) in cls.__sensor_map.items():
            sensors[name] = (idx, unit)
        return sensors

    @classmethod
    def postprocess_map(cls):
        """
        Return postprocessing map
        """
        sensors = {}
        for name, (_, _, *processor) in cls.__sensor_map.items():
            if processor:
                sensors[name] = processor[0]
        return sensors

    @classmethod
    def schema(cls):
        return cls.__schema


class X1Smart(InverterPost):
    """
    X1-Smart with Pocket WiFi v2.033.20
    Includes X-Forwarded-For for direct LAN API access
    """
    __schema = vol.Schema({
        vol.Required('type', 'type'): vol.All(int, 8),
        vol.Required('sn',): str,
        vol.Required('ver'): str,
        vol.Required('Data'): vol.Schema(
            vol.All(
                [vol.Coerce(float)],
                vol.Length(min=200, max=200),
            )
        ),
        vol.Required('Information'): vol.Schema(
            vol.All(
                vol.Length(min=8, max=8)
            )
        ),
    }, extra=vol.REMOVE_EXTRA)

    __sensor_map = {
        'Network Voltage':            (0, 'V', div10),
        'Output Current':             (1, 'A', div10),
        'AC Power':                   (2, 'W'),
        'PV1 Voltage':                (3, 'V', div10),
        'PV2 Voltage':                (4, 'V', div10),
        'PV1 Current':                (5, 'A', div10),
        'PV2 Current':                (6, 'A', div10),
        'PV1 Power':                  (7, 'W'),
        'PV2 Power':                  (8, 'W'),
        'Grid Frequency':             (9, 'Hz', div100),
        'Total Energy':               (11, 'kWh', div10),
        'Today\'s Energy':            (13, 'kWh', div10),
        'Inverter Temperature':       (39, 'C'),
        'Exported Power':             (48, 'W', to_signed),
        'Total Feed-in Energy':       (50, 'kWh', div100),
        'Total Consumption':          (52, 'kWh', div100),
    }

    @classmethod
    async def make_request(cls, host, port=80, pwd='', headers=None):
        headers = {'X-Forwarded-For': '5.8.8.8'}
        return await super().make_request(host, port, pwd, headers=headers)

    @classmethod
    def sensor_map(cls):
        """
        Return sensor map
        """
        sensors = {}
        for name, (idx, unit, *_) in cls.__sensor_map.items():
            sensors[name] = (idx, unit)
        return sensors

    @classmethod
    def postprocess_map(cls):
        """
        Return postprocessing map
        """
        sensors = {}
        for name, (_, _, *processor) in cls.__sensor_map.items():
            if processor:
                sensors[name] = processor[0]
        return sensors

    @classmethod
    def schema(cls):
        return cls.__schema


# registry of inverters
REGISTRY = [XHybrid, X3, X3V34, X1, X1Mini, X1MiniV34, X1Smart,
            QVOLTHYBG33P]
