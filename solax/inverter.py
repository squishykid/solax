from dataclasses import dataclass, field
from json import loads
from typing import Any, Callable, Dict, List, Optional, Tuple, TypedDict, Union

import voluptuous as vol
from mypy_extensions import VarArg
from voluptuous import Invalid, MultipleInvalid
from voluptuous.humanize import humanize_error

from solax.http_client import HttpClient
from solax.inverter_error import InverterError
from solax.units import Measurement, Total, Units
from solax.units import SensorUnit, Units

Transformer = Callable[[VarArg(float)], float]

SensorIndexSpec = Union[int, Tuple[int, ...]]
ResponseDecoder = Dict[
    str,
    Union[
        Tuple[SensorIndexSpec, Units],
        Tuple[SensorIndexSpec, Units, Union[Transformer, Tuple[Transformer, ...]]],
        Tuple[SensorIndexSpec, SensorUnit],
        Tuple[SensorIndexSpec, SensorUnit, Union[Transformer, Tuple[Transformer, ...]]],
    ],
]


class InverterRawResponse(TypedDict):
    Data: list[float]
    sn: Optional[str]
    SN: Optional[str]
    version: Optional[str]
    ver: Optional[str]
    type: Union[int, str]
    Information: Optional[list[Any]]


@dataclass
class InverterResponse:
    data: dict[str, float]
    serial_number: str
    version: str
    type: Union[int, str]
    inverter_type: int


@dataclass
class InverterIdentification:
    inverter_type: int
    old_type_prefix: Optional[str] = None


@dataclass
class InverterDataValue:
    indexes: tuple[int, ...]
    unit: Union[Measurement, Total]
    transformations: tuple[Transformer, ...] = field(default_factory=tuple)


@dataclass
class InverterDefinition:
    identification: InverterIdentification
    mapping: Dict[str, InverterDataValue]


class Inverter:
    """Base wrapper around Inverter HTTP API"""

    @staticmethod
    def common_response_schema() -> Callable[[Any], InverterRawResponse]:
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
                vol.Optional("Information"): list,
            },
            extra=vol.REMOVE_EXTRA,
        )

    @classmethod
    def response_decoder(cls) -> ResponseDecoder:
        """
        Inverter implementations should override
        this to return a decoding map
        """
        raise NotImplementedError()

    @classmethod
    def inverter_identification(cls) -> InverterIdentification:
        return InverterIdentification(99999)
        raise NotImplementedError()

    @classmethod
    def inverter_definition(cls) -> InverterDefinition:
        old_mapping = cls.response_decoder()
        mapping: Dict[str, InverterDataValue] = {}
        for k, v in old_mapping.items():
            indexes = v[0]
            if isinstance(indexes, (tuple, list)):
                indexes = tuple(indexes)
            elif isinstance(indexes, int):
                indexes = (indexes,)
            else:
                raise TypeError("unexpected index type")

            unit = v[1]
            if isinstance(unit, Units):
                unit = Measurement(unit)

            if len(v) < 3:
                mapping[k] = InverterDataValue(indexes, unit)
                continue
            transformers: Union[Transformer, Tuple[Transformer, ...]] = v[2]  # type: ignore
            if not isinstance(transformers, tuple):
                transformers = (transformers,)
            mapping[k] = InverterDataValue(indexes, unit, transformers)
        return InverterDefinition(cls.inverter_identification(), mapping)

    @staticmethod
    def apply_transforms(
        data: List[float], mapping_instance: InverterDataValue
    ) -> float:
        indexes = mapping_instance.indexes
        transforms = mapping_instance.transformations
        out = [data[i] for i in indexes]
        for transform in transforms:
            if isinstance(out, list):
                out = [transform(*out)]
            else:
                out = [transform(out)]
        return out[0] if isinstance(out, list) else out

    async def get_data(self) -> InverterResponse:
        try:
            response = await self.http_client.request()
            data = self.handle_response(response)
        except vol.Invalid as ex:
            msg = "Received malformed JSON from inverter"
            raise InverterError(msg, str(self.__class__.__name__)) from ex
        return data

    def map_response_v2(
        self, inverter_response: InverterRawResponse
    ) -> dict[str, float]:
        data = inverter_response["Data"]
        highest_index = max(
            (max(v.indexes) for v in self.inverter_definition().mapping.values())
        )
        if highest_index >= len(data):
            raise InverterError("unable to map response")
        accumulator = {}
        for k, mapping_instance in self.inverter_definition().mapping.items():
            accumulator[k] = self.apply_transforms(data, mapping_instance)
        return accumulator

    _schema: vol.Schema = vol.Schema({})

    @classmethod
    def schema(cls) -> vol.Schema:
        """
        Return schema
        """
        return cls._schema

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
            response = self.schema()(json_response)
        except (Invalid, MultipleInvalid) as ex:
            _ = humanize_error(json_response, ex)
            raise
        serial = response.get("SN", response.get("sn"))
        version = response.get("ver", response.get("version"))
        information = response.get("Information")
        return InverterResponse(
            self.map_response_v2(response),
            serial if serial else "unknown serial",
            version if version else "unknown version",
            response["type"],
            information[1] if information and len(information) > 1 else -1,
        )

    def identify(self, response: bytes) -> bool:
        try:
            inverter_response = self.handle_response(response)
        except (Invalid, MultipleInvalid) as ex:
            _ = humanize_error(response, ex)
            return False
        return True

    def __init__(self, http_client: HttpClient):
        self.http_client = http_client

    def sensor_map(self) -> Dict[str, Tuple[int, Union[Measurement, Total]]]:
        """
        Return sensor map
        Warning, HA depends on this
        """
        sensors: Dict[str, Tuple[int, Union[Measurement, Total]]] = {}
        for name, mapping in self.inverter_definition().mapping.items():
            unit = mapping.unit
            idx = mapping.indexes[0]
            sensors[name] = (idx, unit)

        return sensors
