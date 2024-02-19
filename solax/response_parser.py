import json
import logging
from collections import namedtuple
from typing import Any, Callable, Dict, Tuple, Union

import voluptuous as vol
from voluptuous import Invalid, MultipleInvalid
from voluptuous.humanize import humanize_error

from solax.units import SensorUnit
from solax.utils import PackerBuilderResult

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.INFO)

InverterResponse = namedtuple("InverterResponse", "data, serial_number, version, type")

SensorIndexSpec = Union[int, PackerBuilderResult]
ResponseDecoder = Dict[
    str,
    Union[
        Tuple[SensorIndexSpec, SensorUnit],
        Tuple[SensorIndexSpec, SensorUnit, Callable[[Any], Any]],
    ],
]


class ResponseParser:
    def __init__(self, schema: vol.Schema, decoder: ResponseDecoder):
        self.schema = schema
        self.response_decoder = decoder

    def _decode_map(self) -> Dict[str, SensorIndexSpec]:
        sensors: Dict[str, SensorIndexSpec] = {}
        for name, mapping in self.response_decoder.items():
            if isinstance(mapping, dict):
                mapping = mapping["decoder"]
            sensors[name] = mapping[0]
        return sensors

    def _postprocess_map(self) -> Dict[str, Callable[[Any], Any]]:
        """
        Return map of functions to be applied to each sensor value
        """
        sensors: Dict[str, Callable[[Any], Any]] = {}
        for name, mapping in self.response_decoder.items():
            if isinstance(mapping, dict):
                mapping = mapping["decoder"]
            processor = None
            (_, _, *processor) = mapping
            if processor:
                sensors[name] = processor[0]
        return sensors

    def map_response(self, resp_data) -> Dict[str, Any]:
        result = {}
        for sensor_name, decode_info in self._decode_map().items():
            if isinstance(decode_info, (tuple, list)):
                indexes = decode_info[0]
                packer = decode_info[1]
                values = tuple(resp_data[i] for i in indexes)
                val = packer(*values)
            else:
                val = resp_data[decode_info]
            result[sensor_name] = val
        for sensor_name, processor in self._postprocess_map().items():
            result[sensor_name] = processor(result[sensor_name])
        return result

    def handle_response(self, resp: bytearray):
        """
        Decode response and map array result using mapping definition.

        Args:
            resp (bytearray): The response

        Returns:
            InverterResponse: The decoded and mapped interver response.
        """

        raw_json = resp.decode("utf-8").replace(",,", ",0.0,").replace(",,", ",0.0,")
        json_response = json.loads(raw_json)
        try:
            response = self.schema(json_response)
        except (Invalid, MultipleInvalid) as ex:
            _ = humanize_error(json_response, ex)
            raise
        return InverterResponse(
            data=self.map_response(response["Data"]),
            serial_number=response.get("SN", response.get("sn")),
            version=response.get("ver", response.get("version")),
            type=response["type"],
        )
