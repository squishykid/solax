from typing import Any, Dict, Optional

import voluptuous as vol

from solax.inverter import Inverter
from solax.units import DailyTotal, Total, Units
from solax.utils import div10, div100, pack_u16, to_signed, to_signed32, twoway_div10


class X3MicProG2(Inverter):
    """X3MicProG2 v3.008.10"""

    # pylint: disable=duplicate-code
    _schema = vol.Schema(
        {
            vol.Required("type"): vol.All(int, 16),
            vol.Required("sn"): str,
            vol.Required("ver"): str,
            vol.Required("data"): vol.Schema(
                vol.All(
                    [vol.Coerce(float)],
                    vol.Length(min=100, max=100),
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
    def _decode_run_mode(cls, run_mode):
        return {
            0: "Wait",
            1: "Check",
            2: "Normal",
            3: "Fault",
            4: "Permanent Fault",
            5: "Update",
        }.get(run_mode)

    @classmethod
    def response_decoder(cls):
        return {
            "Grid 1 Voltage": (0, Units.V, div10),
            "Grid 2 Voltage": (1, Units.V, div10),
            "Grid 3 Voltage": (2, Units.V, div10),
            "Grid 1 Current": (3, Units.A, twoway_div10),
            "Grid 2 Current": (4, Units.A, twoway_div10),
            "Grid 3 Current": (5, Units.A, twoway_div10),
            "Grid 1 Power": (6, Units.W, to_signed),
            "Grid 2 Power": (7, Units.W, to_signed),
            "Grid 3 Power": (8, Units.W, to_signed),
            "PV1 Voltage": (9, Units.V, div10),
            "PV2 Voltage": (10, Units.V, div10),
            "PV3 Voltage": (11, Units.V, div10),
            "PV1 Current": (12, Units.A, div10),
            "PV2 Current": (13, Units.A, div10),
            "PV3 Current": (14, Units.A, div10),
            "PV1 Power": (15, Units.W),
            "PV2 Power": (16, Units.W),
            "PV3 Power": (17, Units.W),
            "Grid 1 Frequency": (18, Units.HZ, div100),
            "Grid 2 Frequency": (19, Units.HZ, div100),
            "Grid 3 Frequency": (20, Units.HZ, div100),
            # "Run Mode": (21, Units.NONE),
            "Run Mode": (21, Units.NONE, X3MicProG2._decode_run_mode),
            "Total Yield": (pack_u16(22, 23), Total(Units.KWH), div10),
            "Daily Yield": (24, DailyTotal(Units.KWH), div10),
            "Feed-in Power ": (pack_u16(72, 73), Units.W, to_signed32),
            "Total Feed-in Energy": (pack_u16(74, 75), Total(Units.KWH), div100),
            "Total Consumption": (pack_u16(76, 77), Total(Units.KWH), div100),
        }

    # pylint: enable=duplicate-code

    @classmethod
    def inverter_serial_number_getter(cls, response: Dict[str, Any]) -> Optional[str]:
        return response["information"][2]
