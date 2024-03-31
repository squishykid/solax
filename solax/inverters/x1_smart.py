from typing import Any, Dict, Optional

import voluptuous as vol

from solax.inverter import Inverter
from solax.units import DailyTotal, Total, Units
from solax.utils import div10, div100, to_signed


class X1Smart(Inverter):
    """
    X1-Smart with Pocket WiFi v2.033.20
    Includes X-Forwarded-For for direct LAN API access
    """

    # pylint: disable=duplicate-code
    _schema = vol.Schema(
        {
            vol.Required("type", "type"): vol.All(int, 8),
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
            vol.Required("information"): vol.Schema(vol.All(vol.Length(min=8, max=8))),
        },
        extra=vol.REMOVE_EXTRA,
    )

    @classmethod
    def response_decoder(cls):
        return {
            "Network Voltage": (0, Units.V, div10),
            "Output Current": (1, Units.A, div10),
            "AC Power": (2, Units.W),
            "PV1 Voltage": (3, Units.V, div10),
            "PV2 Voltage": (4, Units.V, div10),
            "PV1 Current": (5, Units.A, div10),
            "PV2 Current": (6, Units.A, div10),
            "PV1 Power": (7, Units.W),
            "PV2 Power": (8, Units.W),
            "Grid Frequency": (9, Units.HZ, div100),
            "Total Energy": (11, Total(Units.KWH), div10),
            "Today's Energy": (13, DailyTotal(Units.KWH), div10),
            "Inverter Temperature": (39, Units.C),
            "Exported Power": (48, Units.W, to_signed),
            "Total Feed-in Energy": (50, Total(Units.KWH), div100),
            "Total Consumption": (52, Total(Units.KWH), div100),
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
