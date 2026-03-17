from typing import Any, Dict, Optional

import voluptuous as vol

from solax.inverter import Inverter
from solax.units import DailyTotal, Total, Units
from solax.utils import div10, div100, pack_u16, to_signed


class X1HybridGen4(Inverter):
    # pylint: disable=duplicate-code
    _schema = vol.Schema(
        {
            vol.Required("type"): vol.All(int, vol.Any(15, 34)),
            vol.Required(
                "sn",
            ): str,
            vol.Required("ver"): str,
            vol.Required("data"): vol.Schema(
                vol.All(
                    [vol.Coerce(float)],
                    vol.Length(min=200, max=300),
                )
            ),
            vol.Required("information"): vol.Schema(vol.All(vol.Length(min=9, max=10))),
        },
        extra=vol.REMOVE_EXTRA,
    )

    @classmethod
    def build_all_variants(cls, host, port, pwd=""):
        versions = [cls._build(host, port, pwd, False)]
        return versions

    @classmethod
    def response_decoder(cls):
        return {
            "AC voltage R": (0, Units.V, div10),
            "AC current": (1, Units.A, div10),
            "AC power": (2, Units.W, to_signed),
            "Grid frequency": (3, Units.HZ, div100),
            "PV1 voltage": (4, Units.V, div10),
            "PV2 voltage": (5, Units.V, div10),
            "PV1 current": (6, Units.A, div10),
            "PV2 current": (7, Units.A, div10),
            "PV1 power": (8, Units.W),
            "PV2 power": (9, Units.W),
            "On-grid total yield": (pack_u16(11, 12), Total(Units.KWH), div10),
            "On-grid daily yield": (13, DailyTotal(Units.KWH), div10),
            "Battery voltage": (14, Units.V, div100),
            "Battery current": (15, Units.A, to_signed, div100),
            "Battery power": (16, Units.W, to_signed),
            "Battery temperature": (17, Units.C),
            "Battery SoC": (18, Units.PERCENT),
            "Inverter Temperature": (26, Units.C),
            "Grid power": (32, Units.W, to_signed),
            "Total feed-in energy": (pack_u16(34, 35), Total(Units.KWH), div100),
            "Total consumption": (pack_u16(36, 37), Total(Units.KWH), div100),
            "Run mode": (10, Units.NONE),
            "Battery remaining energy": (23, Units.KWH, div10),
            "EPS power": (28, Units.W, to_signed),
            "EPS voltage": (29, Units.V, div10),
            "EPS current": (30, Units.A, to_signed, div10),
            "Total PV Energy": (54, Total(Units.KWH), div10),
            "EPS Energy total": (83, Total(Units.KWH), div10),
            "EPS Energy today": (84, DailyTotal(Units.KWH), div10),
            "Total battery discharge energy": (19, Total(Units.KWH), div10),
            "Total battery charge energy": (21, Total(Units.KWH), div10),
            "PV daily yield": (85, DailyTotal(Units.KWH), div10),
            "Battery discharge energy today": (86, DailyTotal(Units.KWH), div10),
            "Battery charge energy today": (87, DailyTotal(Units.KWH), div10),
            "Battery health": (24, Units.PERCENT),
            "Radiator temperature": (39, Units.C, to_signed),
            "Load power": (38, Units.W),
            "Feed-in energy today": (78, DailyTotal(Units.KWH), div100),
            "Grid import energy today": (80, DailyTotal(Units.KWH), div100),
            "Consumption today": (52, DailyTotal(Units.KWH), div100),
            # 40: 256 (0x100), possible status/fault bitmask
            # 41-42: unknown, possibly redundant battery charge/discharge counters
            # 44: ~= Battery charge energy today * 100, likely redundant
            # 45-46: unknown, slowly changing values
            # 47: similar to Load power [38], likely redundant
            # 76: /10=0.4, likely redundant with Grid import energy today [80]
            # 56-59: large values (60928, 65535...), possibly encoded firmware/timestamp data
        }

    @classmethod
    def inverter_serial_number_getter(cls, response: Dict[str, Any]) -> Optional[str]:
        return response["information"][2]
