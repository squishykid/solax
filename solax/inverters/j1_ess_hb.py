import voluptuous as vol

from solax.inverter import Inverter
from solax.units import Total, Units
from solax.utils import div10, div100, pack_u16, to_signed, to_signed32, twoway_div10


class J1EssHb(Inverter):
    # pylint: disable=duplicate-code
    _schema = vol.Schema(
        {
            vol.Required("type"): int,
            vol.Required("sn"): str,
            vol.Required("ver"): str,
            vol.Required("Data"): vol.Schema(
                vol.All(
                    [vol.Coerce(float)],
                    vol.Length(min=300, max=300),
                )
            ),
            vol.Required("Information"): vol.Schema(
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
            0: "Waiting",
            1: "Checking",
            2: "Normal",
            3: "Fault",
            4: "Permanent Fault",
            5: "Updating",
            6: "EPS Check",
            7: "EPS Mode",
            8: "Self Test",
            9: "Idle",
            10: "Standby",
        }.get(run_mode)

    @classmethod
    def response_decoder(cls):
        return {
            "Grid 1 Voltage": (0, Units.V, div10),
            "Grid 1 Current": (1, Units.A, div10),
            "Grid 1 Power": (2, Units.W, to_signed),
            "Grid 2 Voltage": (3, Units.V, div10),
            "Grid 2 Current": (4, Units.A, div10),
            "Grid 2 Power": (5, Units.W, to_signed),
            "Grid Power Total": (6, Units.W, to_signed),
            "Grid Frequency": (7, Units.HZ, div100),
            "PV1 Voltage": (8, Units.V, div10),
            "PV1 Current": (9, Units.A, div10),
            "PV1 Power": (10, Units.W),
            "PV2 Voltage": (11, Units.V, div10),
            "PV2 Current": (12, Units.A, div10),
            "PV2 Power": (13, Units.W),
            "PV3 Voltage": (14, Units.V, div10),
            "PV3 Current": (15, Units.A, div10),
            "PV3 Power": (16, Units.W),
            "Run Mode": (17, Units.NONE, J1EssHb._decode_run_mode),
            "EPS 1 Voltage": (19, Units.V, div10),
            "EPS 1 Current": (20, Units.A, twoway_div10),
            "EPS 1 Power": (21, Units.W, to_signed),
            "EPS 2 Voltage": (23, Units.V, div10),
            "EPS 2 Current": (24, Units.A, twoway_div10),
            "EPS 2 Power": (25, Units.W, to_signed),
            "EPS Frequency": (26, Units.HZ, div100),
            "Feed-in 1 Power ": (27, Units.W, to_signed),
            "Feed-in 2 Power ": (28, Units.W, to_signed),
            "Feed-in Power Total ": (29, Units.W, to_signed),
            "Yield total": (pack_u16(34, 35), Total(Units.KWH), div10),
            "Yield today": (36, Units.KWH, div10),
            "Battery Remaining Capacity": (80, Units.PERCENT),
            "Battery Temperature": (82, Units.C),
            "Battery Surplus Energy": (83, Units.KWH, div10),
        }

    # pylint: enable=duplicate-code
