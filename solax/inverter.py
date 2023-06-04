from typing import Dict, Tuple

import aiohttp
import voluptuous as vol

from solax import utils
from solax.inverter_http_client import InverterHttpClient, Method
from solax.response_parser import InverterResponse, ResponseDecoder, ResponseParser
from solax.units import Measurement, Units


class InverterError(Exception):
    """Indicates error communicating with inverter"""


class Inverter:
    """Base wrapper around Inverter HTTP API"""

    @classmethod
    def response_decoder(cls) -> ResponseDecoder:
        """
        Inverter implementations should override
        this to return a decoding map
        """
        raise NotImplementedError()

    # pylint: enable=C0301
    _schema = vol.Schema({})  # type: vol.Schema

    def __init__(
        self, http_client: InverterHttpClient, response_parser: ResponseParser
    ):
        self.manufacturer = "Solax"
        self.response_parser = response_parser
        self.http_client = http_client

    @classmethod
    def _build(cls, host, port, pwd="", params_in_query=True):
        url = utils.to_url(host, port)
        http_client = InverterHttpClient(url, Method.POST, pwd)
        if params_in_query:
            http_client.with_default_query()
        else:
            http_client.with_default_data()

        schema = cls.schema()
        response_decoder = cls.response_decoder()
        response_parser = ResponseParser(schema, response_decoder)
        return cls(http_client, response_parser)

    @classmethod
    def build_all_variants(cls, host, port, pwd=""):
        versions = [
            cls._build(host, port, pwd, True),
            cls._build(host, port, pwd, False),
        ]
        return versions

    async def get_data(self) -> InverterResponse:
        try:
            data = await self.make_request()
        except aiohttp.ClientError as ex:
            msg = "Could not connect to inverter endpoint"
            raise InverterError(msg, str(self.__class__.__name__)) from ex
        except vol.Invalid as ex:
            msg = "Received malformed JSON from inverter"
            raise InverterError(msg, str(self.__class__.__name__)) from ex
        return data

    async def make_request(self) -> InverterResponse:
        """
        Return instance of 'InverterResponse'
        Raise exception if unable to get data
        """
        raw_response = await self.http_client.request()
        return self.response_parser.handle_response(raw_response)

    @classmethod
    def sensor_map(cls) -> Dict[str, Tuple[int, Measurement]]:
        """
        Return sensor map
        Warning, HA depends on this
        """
        sensors: Dict[str, Tuple[int, Measurement]] = {}
        for idx, (name, mapping) in enumerate(cls.response_decoder().items()):
            unit = Measurement(Units.NONE)
            unit_or_measurement = mapping[1]

            if isinstance(unit_or_measurement, Units):
                unit = Measurement(unit_or_measurement)
            else:
                unit = unit_or_measurement

            sensors[name] = (idx, unit)
        return sensors

    @classmethod
    def schema(cls) -> vol.Schema:
        """
        Return schema
        """
        return cls._schema

    def __str__(self) -> str:
        return f"{self.__class__.__name__} :: {self.http_client}"
