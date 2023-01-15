from collections import namedtuple
from json import load, loads
from typing import Callable, Dict, List, Tuple, TypedDict, Union

import aiohttp
import voluptuous as vol
from typing_extensions import NotRequired
from voluptuous import Invalid, MultipleInvalid
from voluptuous.humanize import humanize_error

from solax.http_client import HttpClient, all_variations
from solax.inverter_error import InverterError
from solax.units import Measurement, Units
from solax.utils import div10, u16_packer

Transformer = Callable[[Tuple[float, ...]], float]


InverterResponse = namedtuple(
    "InverterResponse", "data, serial_number, version, type, inverter_type"
)

ALL_HTTP_CLIENT_KEYS = all_variations("localhost", 80).keys()


class InverterIdentification(TypedDict):
    inverterType: int
    type: Union[int, str]


class InverterDataValue(TypedDict):
    indexes: List[int]
    transformations: List[str]
    unit: Units
    is_monotonic: NotRequired[bool]


class InverterDefinition(TypedDict):
    name: str
    identification: InverterIdentification
    mapping: Dict[str, InverterDataValue]


class Inverter:
    """Base wrapper around Inverter HTTP API"""

    @staticmethod
    def common_response_schema():
        return vol.Schema(
            {
                vol.Required("type"): vol.Any(str, int),
                vol.Required(vol.Any("SN", "sn")): str,
                vol.Required(vol.Any("ver", "version")): str,
                vol.Required("Data"): vol.Schema(
                    vol.All(
                        [vol.Coerce(float)],
                    )
                ),
                vol.Required("Information"): list,
            },
            extra=vol.REMOVE_EXTRA,
        )

    @staticmethod
    def inverter_definition_schema():
        transformations = Inverter.transformations().keys()
        return vol.Schema(
            {
                vol.Required("name"): str,
                vol.Required("identification"): vol.Schema(
                    {
                        vol.Required("inverterType"): int,
                        vol.Required("type"): vol.Any(str, int),
                    }
                ),
                vol.Required("mapping"): vol.Schema(
                    {
                        str: vol.Schema(
                            {
                                vol.Required("indexes"): vol.All(
                                    [int], vol.Length(min=1)
                                ),
                                vol.Optional("transformations"): vol.Schema(
                                    vol.All([vol.In(transformations)])
                                ),
                                vol.Required("unit"): vol.Coerce(Units),
                                vol.Optional("is_monotonic"): bool,
                            }
                        )
                    }
                ),
            }
        )

    @staticmethod
    def transformations() -> Dict[str, Transformer]:
        return {"div10": div10, "pack_u16": u16_packer}

    @staticmethod
    def apply_transforms(
        data: List[float], mapping_instance: InverterDataValue
    ) -> float:
        indexes = mapping_instance["indexes"]
        transforms = mapping_instance.get("transformations", [])
        out = [data[i] for i in indexes]
        for t in transforms:
            f = Inverter.transformations()[t]
            if isinstance(out, list):
                out = f(*out)
            else:
                out = f(out)
        return out[0] if isinstance(out, list) else out

    async def get_data(self) -> InverterResponse:
        try:
            response = await self.make_request()
            data = self.handle_response(response)
        except vol.Invalid as ex:
            msg = "Received malformed JSON from inverter"
            raise InverterError(msg, str(self.__class__.__name__)) from ex
        return data

    async def make_request(self) -> bytearray:
        """
        Return instance of 'InverterResponse'
        Raise exception if unable to get data
        """
        return await self.http_client.request()
        # raw_response = await self.http_client.request()
        # return self.handle_response(raw_response)

    def map_response_v2(self, inverter_response: InverterResponse):
        data = inverter_response["Data"]
        bingo = {}
        for k, v in self.inverter_definition["mapping"].items():
            bingo[k] = self.apply_transforms(data, v)
        return bingo

    def handle_response(self, resp: bytes) -> InverterResponse:
        """
        Decode response and map array result using mapping definition.

        Args:
            resp (bytearray): The response

        Returns:
            InverterResponse: The decoded and mapped interver response.
        """

        raw_json = resp.decode("utf-8").replace(",,", ",0.0,").replace(",,", ",0.0,")
        json_response = loads(raw_json)
        try:
            response = self.common_response_schema()(json_response)
        except (Invalid, MultipleInvalid) as ex:
            _ = humanize_error(json_response, ex)
            raise
        return InverterResponse(
            data=self.map_response_v2(response),
            serial_number=response.get("SN", response.get("sn")),
            version=response.get("ver", response.get("version")),
            type=response["type"],
            inverter_type=response["Information"][1],
        )

    def identify(self, response: bytes) -> bool:
        inverter_response = self.handle_response(response)
        actual_inverter_type = inverter_response.inverter_type
        identification = self.inverter_definition["identification"]
        self_inverter_type = identification["inverterType"]
        if actual_inverter_type != self_inverter_type:
            return False

        actual_type = inverter_response.type
        self_type = identification["type"]
        if isinstance(self_type, str):
            return isinstance(actual_type, str) and actual_type.startswith(self_type)
        return actual_type == self_type

    def __init__(self, inverter_definition_file: str, http_client: HttpClient):
        self.inverter_definition_file_name = inverter_definition_file
        with open(inverter_definition_file, "r") as f:
            inv_def = load(f)
        inv_def_schema = self.inverter_definition_schema()
        self.inverter_definition: InverterDefinition = inv_def_schema(inv_def)
        self.http_client = http_client

    # @classmethod
    # def build_all_variants(cls, http_client):
    #     return [cls("solax/inverters/X3.json", http_client)]

    def sensor_map(self) -> Dict[str, Tuple[int, Measurement]]:
        """
        Return sensor map
        Warning, HA depends on this
        """
        sensors: Dict[str, Tuple[int, Measurement]] = {}
        for name, mapping in self.inverter_definition["mapping"].items():
            unit = mapping["unit"]
            is_monitonic = mapping.get("is_monotonic", False)
            idx = mapping["indexes"][0]
            sensors[name] = (idx, Measurement(unit, is_monitonic))

        return sensors
