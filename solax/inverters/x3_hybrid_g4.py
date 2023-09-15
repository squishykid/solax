import voluptuous as vol

from solax.inverter import Inverter
from solax.units import Total, Units
from solax.utils import div10, div100, pack_u16, to_signed, to_signed32, twoway_div10


class X3HybridG4(Inverter):
    """X3 Hybrid G4 v3.006.04"""

    # pylint: disable=duplicate-code
    _schema = vol.Schema(
        {
            vol.Required("type"): vol.All(int, 14),
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
            "Grid 2 Voltage": (1, Units.V, div10),
            "Grid 3 Voltage": (2, Units.V, div10),
            "Grid 1 Current": (3, Units.A, twoway_div10),
            "Grid 2 Current": (4, Units.A, twoway_div10),
            "Grid 3 Current": (5, Units.A, twoway_div10),
            "Grid 1 Power": (6, Units.W, to_signed),
            "Grid 2 Power": (7, Units.W, to_signed),
            "Grid 3 Power": (8, Units.W, to_signed),
            "PV1 Voltage": (10, Units.V, div10),
            "PV2 Voltage": (11, Units.V, div10),
            "PV1 Current": (12, Units.A, div10),
            "PV2 Current": (13, Units.A, div10),
            "PV1 Power": (14, Units.W),
            "PV2 Power": (15, Units.W),
            "Grid 1 Frequency": (16, Units.HZ, div100),
            "Grid 2 Frequency": (17, Units.HZ, div100),
            "Grid 3 Frequency": (18, Units.HZ, div100),
            #"Run mode": (19, Units.NONE),
            "Run mode text": (19, Units.NONE, X3HybridG4._decode_run_mode),
            "EPS 1 Voltage": (23, Units.W, div10),
            "EPS 2 Voltage": (24, Units.W, div10),
            "EPS 3 Voltage": (25, Units.W, div10),
            "EPS 1 Current": (26, Units.W, twoway_div10),
            "EPS 2 Current": (27, Units.W, twoway_div10),
            "EPS 3 Current": (28, Units.W, twoway_div10),
            "EPS 1 Power": (29, Units.W, to_signed),
            "EPS 2 Power": (30, Units.W, to_signed),
            "EPS 3 Power": (31, Units.W, to_signed),
            "Feed-in Power ": (pack_u16(34, 35), Units.W, to_signed32),
            "Battery Power": (41, Units.W, to_signed),
            "Radiator Temperature": (54, Units.C, to_signed),
            "Yield total": (pack_u16(68, 69), Total(Units.KWH), div10),
            "Yield today": (70, Total(Units.KWH), div10),
            "Feed-in Energy": (pack_u16(86, 87), Total(Units.KWH), div100),
            "Consumed Energy": (pack_u16(88, 89), Total(Units.KWH), div100),
            "Battery Remaining Capacity": (103, Units.PERCENT),
            "Battery Temperature": (105, Units.C, to_signed),
            "Battery Voltage": (pack_u16(169, 170), Units.V, div100),
        }

    # pylint: enable=duplicate-code
