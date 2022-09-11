import voluptuous as vol
from solax.inverter import InverterPostData
from solax.units import Units, Total
from solax.utils import div10, div100, pack_u16, to_signed


class X1HybridGen4(InverterPostData):
    # pylint: disable=duplicate-code
    _schema = vol.Schema(
        {
            vol.Required("type"): vol.All(int, 15),
            vol.Required(
                "sn",
            ): str,
            vol.Required("ver"): str,
            vol.Required("Data"): vol.Schema(
                vol.All(
                    [vol.Coerce(float)],
                    vol.Length(min=200, max=200),
                )
            ),
            vol.Required("Information"): vol.Schema(vol.All(vol.Length(min=9, max=10))),
        },
        extra=vol.REMOVE_EXTRA,
    )

    @classmethod
    def response_decoder(cls):
        return {
            "AC voltage R": (0, Units.V, div10),
            "AC current": (1, Units.A, div10),
            "AC power": (2, Units.W),
            "Grid frequency": (3, Units.HZ, div100),
            "PV1 voltage": (4, Units.V, div10),
            "PV2 voltage": (5, Units.V, div10),
            "PV1 current": (6, Units.A, div10),
            "PV2 current": (7, Units.A, div10),
            "PV1 power": (8, Units.W),
            "PV2 power": (9, Units.W),
            "On-grid total yield": (pack_u16(11, 12), Total(Units.KWH), div10),
            "On-grid daily yield": (13, Units.KWH, div10),
            "Battery voltage": (14, Units.V, div100),
            "Battery current": (15, Units.A, div100),
            "Battery power": (16, Units.W),
            "Battery temperature": (17, Units.C),
            "Battery SoC": (18, Units.PERCENT),
            "Grid power": (32, Units.W, to_signed),
            "Total feed-in energy": (pack_u16(34, 35), Total(Units.KWH), div100),
            "Total consumption": (pack_u16(36, 37), Total(Units.KWH), div100),
        }
