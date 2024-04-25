from typing import Any, Dict, Optional

import voluptuous as vol

from solax.inverter import Inverter
from solax.units import DailyTotal, Total, Units
from solax.utils import div10, div100, pack_u16, to_signed


class X1Boost(Inverter):
    """
    X1-Boost with Pocket WiFi 2.034.06
    Includes X-Forwarded-For for direct LAN API access
    """

    # pylint: disable=duplicate-code
    _schema = vol.Schema(
        {
            vol.Required("type", "type"): vol.All(int, 4),
            vol.Required(
                "sn",
            ): str,
            vol.Required("ver"): str,
            vol.Required("data"): vol.Schema(
                vol.All(
                    [vol.Coerce(float)],
                    vol.Length(min=200, max=200),
                )
            ),
            vol.Required("information"): vol.Schema(
                vol.All(vol.Length(min=10, max=10))
            ),
        },
        extra=vol.REMOVE_EXTRA,
    )

    @classmethod
    def response_decoder(cls):
        return {
            "AC Voltage": (0, Units.V, div10),
            "AC Output Current": (1, Units.A, div10),
            "AC Output Power": (2, Units.W),
            "PV1 Voltage": (3, Units.V, div10),
            "PV2 Voltage": (4, Units.V, div10),
            "PV1 Current": (5, Units.A, div10),
            "PV2 Current": (6, Units.A, div10),
            "PV1 Power": (7, Units.W),
            "PV2 Power": (8, Units.W),
            "AC Frequency": (9, Units.HZ, div100),
            "Total Generated Energy": (pack_u16(11, 12), Total(Units.KWH), div10),
            "Today's Generated Energy": (13, DailyTotal(Units.KWH), div10),
            "Inverter Temperature": (39, Units.C),
            "Exported Power": (48, Units.W, to_signed),
            "Total Export Energy": (pack_u16(50, 51), Total(Units.KWH), div100),
            "Total Import Energy": (pack_u16(52, 53), Total(Units.KWH), div100),
        }

    @classmethod
    def inverter_serial_number_getter(cls, response: Dict[str, Any]) -> Optional[str]:
        return response["information"][2]

    @classmethod
    def build_all_variants(cls, host, port, pwd=""):
        versions = [
            cls._build(host, port, pwd, True),
            cls._build(host, port, pwd, False),
        ]
        for inverter in versions:
            inverter.http_client = inverter.http_client.with_headers(
                {"X-Forwarded-For": "5.8.8.8"}
            )
        return versions
