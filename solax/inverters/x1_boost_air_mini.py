from typing import Any, Dict, Optional

import voluptuous as vol

from solax.inverter import Inverter
from solax.units import DailyTotal, Total, Units
from solax.utils import div10, div100, pack_u16, to_signed


class X1BoostAirMini(Inverter):
    """
    Modified to handle x1 boost, x1 air and x1 mini
    X1-Boost-Air-Mini with Wifi Pocket v2.034.06
    SolarX disabled lan access with this custom
    firmware you can access te Wifi Pocket from your internal lan:
    https://blog.chrisoft.io/2021/02/14/
    firmwares-modificados-para-solax-pocket-wifi-v2/
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
                    vol.Length(min=69, max=200),
                )
            ),
            vol.Required("information"): vol.Schema(
                vol.Any(vol.Length(min=9, max=9), vol.Length(min=10, max=10))
            ),
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
            "Total Energy": (pack_u16(11, 12), Total(Units.KWH), div10),
            "Today's Energy": (13, DailyTotal(Units.KWH), div10),
            "Inverter Temperature (Alt)": (39, Units.C),
            "Total Feed-in Energy": (41, Total(Units.KWH), div10),
            "Total Consumption": (42, Total(Units.KWH), div10),
            "Power Now": (43, Units.W, div10),
            "Exported Power": (pack_u16(48, 49), Units.W, to_signed),
            "Total Export Energy": (pack_u16(50, 51), Total(Units.KWH), div100),
            "Total Import Energy": (pack_u16(52, 53), Total(Units.KWH), div100),
            "Inverter Temperature": (55, Units.C),
        }

    # pylint: enable=duplicate-code

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
