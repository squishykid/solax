import voluptuous as vol

from solax.inverter import InverterPost
from solax.units import Units, Total
from solax.utils import div10, div100


class X1MiniV34(InverterPost):
    """
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
            vol.Required("Data"): vol.Schema(
                vol.All(
                    [vol.Coerce(float)],
                    vol.Any(
                        vol.Length(min=69, max=69),
                        vol.Length(min=200, max=200),
                    ),
                )
            ),
            vol.Required("Information"): vol.Schema(
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
            "Total Energy": (11, Total(Units.KWH), div10),
            "Today's Energy": (13, Units.KWH, div10),
            "Total Feed-in Energy": (41, Total(Units.KWH), div10),
            "Total Consumption": (42, Total(Units.KWH), div10),
            "Power Now": (43, Units.W, div10),
            "Inverter Temperature": (55, Units.C),
        }

    # pylint: enable=duplicate-code
