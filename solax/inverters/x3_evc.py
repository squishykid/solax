from typing import Any, Dict, Optional

import voluptuous as vol

from solax.inverter import Inverter
from solax.units import Total, Units
from solax.utils import (
    div10,
    div100,
    pack_u16,
    to_signed,
    to_signed32,
    twoway_div10,
    twoway_div100,
)


class X3EVC(Inverter):
    """X3 EVC"""

    # pylint: disable=duplicate-code
    _schema = vol.Schema(
        {
            vol.Required("type"): vol.All(int, 1),
            vol.Required("sn"): str,
            vol.Required("ver"): str,
            vol.Required("data"): vol.Schema(
                vol.All(
                    [vol.Coerce(float)],
                    vol.Length(min=96, max=96),
                )
            ),
            vol.Required("information"): vol.Schema(
                vol.All(vol.Length(min=10, max=10))
            ),
        },
        extra=vol.REMOVE_EXTRA,
    )

    @classmethod
    def build_all_variants(cls, host, port, pwd=""):
        return [cls._build(host, port, pwd, False)]

    @classmethod
    def _decode_device_state(cls, device_state):
        return {
            0: "Preparing",
            1: "Preparing",
            2: "Charging",
            3: "Finishing",
            4: "Faulted",
            5: "Unavailable",
            6: "Reserved",
            7: "SuspendedEV",
            8: "SuspendedEVSE",
        }.get(device_state)

    @classmethod
    def _decode_device_mode(cls, device_mode):
        return {
            0: "STOP",
            1: "FAST",
            2: "ECO",
            3: "GREEN",
        }.get(device_mode)

    @classmethod
    def response_decoder(cls):
        return {
            "Device State": (0, Units.NONE, X3EVC._decode_device_state),
            "Device Mode": (1, Units.NONE, X3EVC._decode_device_mode),
            "EQ Single": (12, Total(Units.KWH), div10),
            "EQ Total": (
                pack_u16(14, 15),
                Total(Units.KWH),
                twoway_div10,
            ),  # not sure if correct
            "Total Charger Power": (11, Units.W),
            "Voltage A": (2, Units.V, div100),
            "Voltage B": (3, Units.V, div100),
            "Voltage C": (4, Units.V, div100),
            "Current A": (5, Units.A, div100),
            "Current B": (6, Units.A, div100),
            "Current C": (7, Units.A, div100),
            "Charger Power A": (8, Units.W),
            "Charger Power B": (9, Units.W),
            "Charger Power C": (10, Units.W),
            "Extern Current A": (16, Units.W, twoway_div100),
            "Extern Current B": (17, Units.W, twoway_div100),
            "Extern Current C": (18, Units.W, twoway_div100),
            "Extern Power A": (19, Units.W, to_signed),
            "Extern Power B": (20, Units.W, to_signed),
            "Extern Power C": (21, Units.W, to_signed),
            "Extern Total Power": (22, Units.W, to_signed),
            "Temperature Plug": (23, Units.C),
            "Temperature PCB": (24, Units.C),
            "CP State": (26, Units.NONE),
            "Charging Duration": (pack_u16(80, 81), Units.NONE, to_signed32),
            "OCPP Offline Mode": (85, Units.NONE),
            "Type Power": (87, Units.NONE),
            "Type Phase": (88, Units.NONE),
            "Type Charger": (89, Units.NONE),
        }

    # pylint: enable=duplicate-code

    @classmethod
    def inverter_serial_number_getter(cls, response: Dict[str, Any]) -> Optional[str]:
        return response["information"][2]
