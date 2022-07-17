import asyncio
from collections import namedtuple
import json
from typing import Dict, Any, Callable, Tuple, Union
import aiohttp
import voluptuous as vol
from voluptuous import Invalid, MultipleInvalid
from voluptuous.humanize import humanize_error

from solax.units import Measurement, SensorUnit, Units
from solax.utils import timeout


class InverterError(Exception):
    """Indicates error communicating with inverter"""


InverterResponse = namedtuple("InverterResponse", "data, serial_number, version, type")


class Inverter:
    """Base wrapper around Inverter HTTP API"""

    ResponseDecoderType = Union[
        Dict[str, int],
        Dict[str, Tuple[int, SensorUnit]],
        Dict[str, Tuple[int, SensorUnit, Callable[[Any, Any], Any]]],
    ]

    @classmethod
    def response_decoder(cls) -> ResponseDecoderType:
        """
        Inverter implementations should override
        this to return a decoding map
        """
        raise NotImplementedError()

    # pylint: enable=C0301
    _schema = vol.Schema({})  # type: vol.Schema

    def __init__(self, host, port, pwd=""):
        self.host = host
        self.port = port
        self.pwd = pwd
        self.manufacturer = "Solax"

    async def get_data(self) -> InverterResponse:
        try:
            async with timeout():
                data = await self.make_request(self.host, self.port, self.pwd)
        except aiohttp.ClientError as ex:
            msg = "Could not connect to inverter endpoint"
            raise InverterError(msg, str(self.__class__.__name__)) from ex
        except ValueError as ex:
            msg = "Received non-JSON data from inverter endpoint"
            raise InverterError(msg, str(self.__class__.__name__)) from ex
        except vol.Invalid as ex:
            msg = "Received malformed JSON from inverter"
            raise InverterError(msg, str(self.__class__.__name__)) from ex
        except asyncio.TimeoutError as ex:
            msg = "Connection to endpoint timed out"
            raise InverterError(msg, str(self.__class__.__name__)) from ex
        return data

    @classmethod
    async def make_request(cls, host, port, pwd="", headers=None) -> InverterResponse:
        """
        Return instance of 'InverterResponse'
        Raise exception if unable to get data
        """
        raise NotImplementedError()

    @classmethod
    def sensor_map(cls) -> Dict[str, Tuple[int, Measurement]]:
        """
        Return sensor map
        """
        sensors = {}
        for name, mapping in cls.response_decoder().items():
            unit = Measurement(Units.NONE)

            if isinstance(mapping, tuple):
                (idx, unit_or_measurement, *_) = mapping
            else:
                idx = mapping

            if isinstance(unit_or_measurement, Units):
                unit = Measurement(unit_or_measurement)
            else:
                unit = unit_or_measurement
            sensors[name] = (idx, unit)
        return sensors

    @classmethod
    def postprocess_map(cls) -> Dict[str, Callable[[Any, Any], Any]]:
        """
        Return map of functions to be applied to each sensor value
        """
        sensors = {}
        for name, mapping in cls.response_decoder().items():
            if isinstance(mapping, tuple):
                processor = None
                (_, _, *processor) = mapping
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
    def map_response(cls, resp_data) -> Dict[str, Any]:
        result = {}
        for sensor_name, (idx, _) in cls.sensor_map().items():
            if isinstance(idx, (tuple, list)):
                # Some values are expressed over 2 (or potentially
                # more 16 bit registers). Here we combine them, if the
                # index given is a list or tuple, in order of least to
                # most significant.
                val = 0
                stride = 1
                for i in idx:
                    val += resp_data[i] * stride
                    stride *= 2**16
            else:
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
    async def make_request(cls, host, port=80, pwd="", headers=None):
        if not pwd:
            base = "http://{}:{}/?optType=ReadRealTimeData"
            url = base.format(host, port)
        else:
            base = "http://{}:{}/?optType=ReadRealTimeData&pwd={}&"
            url = base.format(host, port, pwd)
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers) as req:
                resp = await req.read()

        return cls.handle_response(resp)

    @classmethod
    def handle_response(cls, resp: bytearray):
        """
        Decode response and map array result using mapping definition.

        Args:
            resp (bytearray): The response

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
            data=cls.map_response(response["Data"]),
            serial_number=response.get("SN", response.get("sn")),
            version=response["ver"],
            type=response["type"],
        )


class InverterPostData(InverterPost):
    # This is an intermediate abstract class,
    #  so we can disable the pylint warning
    # pylint: disable=W0223,R0914
    @classmethod
    async def make_request(cls, host, port=80, pwd="", headers=None):
        base = "http://{}:{}/"
        url = base.format(host, port)
        data = "optType=ReadRealTimeData"
        if pwd:
            data = data + "&pwd=" + pwd
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, headers=headers, data=data.encode("utf-8")
            ) as req:
                resp = await req.read()

        return cls.handle_response(resp)
