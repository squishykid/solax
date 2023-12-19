import voluptuous as vol

from solax.inverter import Inverter
from solax.units import Total, Units
from solax.utils import div10, div100, pack_u16, to_signed, to_signed32, twoway_div10


class X3Forth(Inverter):
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
            0: "Init",
            1: "Idle",
            2: "Start",
            3: "Run",
            4: "Fault Fault",
            5: "Update"
        }.get(run_mode)

    @classmethod
    def response_decoder(cls):
        return {
            "Grid Voltage Line AB": (24, Units.V, div10),
            "Grid Voltage Line BC": (25, Units.V, div10),
            "Grid Voltage Line CA": (26, Units.V, div10),
            "Grid A Voltage": (27, Units.V, div10),
            "Grid B Voltage": (28, Units.V, div10),
            "Grid C Voltage": (29, Units.V, div10),
            "Grid A Current": (30, Units.A, div10),
            "Grid B Current": (31, Units.A, div10),
            "Grid C Current": (32, Units.A, div10),
            "Grid A Power": (pack_u16(33, 34), Units.W, to_signed),
            "Grid B Power": (pack_u16(35, 36), Units.W, to_signed),
            "Grid C Power": (pack_u16(37, 38), Units.W, to_signed),
            "GridFrequency": (39, Units.HZ, div100),
            "Yield_Total": (pack_u16(46, 47), Units.KWH, div10),
            "Yield_Today": (48, Units.KWH, div10),
            "Run Mode": (56, Units.NONE, X3Forth._decode_run_mode),
            "PV1 Voltage": (87, Units.V, div10),
            "PV1 Current": (88, Units.A, div10),
            "PV2 Voltage": (89, Units.V, div10),
            "PV2 Current": (90, Units.A, div10),
            "PV3 Voltage": (91, Units.V, div10),
            "PV3 Current": (92, Units.A, div10),
            "PV4 Voltage": (93, Units.V, div10),
            "PV4 Current": (94, Units.A, div10),
            "PV5 Voltage": (95, Units.V, div10),
            "PV5 Current": (96, Units.A, div10),
            "PV6 Voltage": (97, Units.V, div10),
            "PV6 Current": (98, Units.A, div10),
            "PV7 Voltage": (99, Units.V, div10),
            "PV7 Current": (100, Units.A, div10),
            "PV8 Voltage": (101, Units.V, div10),
            "PV8 Current": (102, Units.A, div10),
            "PV9 Voltage": (103, Units.V, div10),
            "PV9 Current": (104, Units.A, div10),
            "PV10 Voltage": (105, Units.V, div10),
            "PV10 Current": (106, Units.A, div10),
            "PV11 Voltage": (107, Units.V, div10),
            "PV11 Current": (108, Units.A, div10),
            "PV12 Voltage": (109, Units.V, div10),
            "PV12 Current": (110, Units.A, div10),

        }

    # pylint: enable=duplicate-code
