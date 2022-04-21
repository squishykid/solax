from collections import namedtuple
import json
from typing import Any, Callable, Optional, Tuple
import aiohttp
import voluptuous as vol
from voluptuous import Invalid, MultipleInvalid
from voluptuous.humanize import humanize_error


class InverterError(Exception):
    """Indicates error communicating with inverter"""


InverterResponse = namedtuple('InverterResponse',
                              'data, serial_number, version, type')


class Inverter:
    """Base wrapper around Inverter HTTP API"""

    # pylint: disable=C0301
    _sensor_map = {}  # type: dict[str,Tuple[int,Optional[str],Optional[Callable[[Any,Any,Any],Any]]]] # noqa: E501
    # pylint: enable=C0301
    _schema = vol.Schema({})  # type: vol.Schema

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
        sensors = {}
        for name, (idx, unit, *_) in cls._sensor_map.items():
            sensors[name] = (idx, unit)
        return sensors

    @classmethod
    def postprocess_map(cls):
        """
        Return map of functions to be applied to each sensor value
        """
        sensors = {}
        for name, (_, _, *processor) in cls._sensor_map.items():
            if processor:
                sensors[name] = processor[0]
        return sensors

    @classmethod
    def schema(cls) -> vol.Schema:
        """
        Return schema
        """
        return cls._schema

    @classmethod
    def map_response(cls, resp_data):
        result = {}
        for sensor_name, (idx, _) in cls.sensor_map().items():
            val = resp_data[idx]
            result[sensor_name] = val
        for sensor_name, processor in cls.postprocess_map().items():
            result[sensor_name] = processor(result[sensor_name], result)
        return result


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

        return cls.handle_response(resp)

    @classmethod
    def handle_response(cls, resp):
        """
        Decode response and map array result using mapping definition.

        Args:
            resp (_type_): The response

        Returns:
            InverterResponse: The decoded and mapped interver response.
        """

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
