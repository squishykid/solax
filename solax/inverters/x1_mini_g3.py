import voluptuous as vol

from solax import utils
from solax.inverter import Inverter, InverterHttpClient, Method, ResponseParser
from solax.units import Total, Units
from solax.utils import div10, div100, pack_u16, to_signed, to_signed32


class X1MiniG3(Inverter):
    # pylint: disable=duplicate-code
    _schema = vol.Schema(
        {
            vol.Required("type"): vol.All(int, 4),
            vol.Required(
                "sn",
            ): str,
            vol.Required("ver"): str,
            vol.Required("Data"): vol.Schema(
                vol.All(
                    [vol.Coerce(float)],
                    vol.Length(min=100, max=100),
                )
            ),

            vol.Required("Information"): vol.Schema(vol.All(vol.Length(min=9, max=10))),
        },
        extra=vol.REMOVE_EXTRA,
    )

    @classmethod
    def _build(cls, host, port, pwd="", params_in_query=True):
        cls.pwd = pwd
        cls.url = utils.to_url(host, port)
        http_client = InverterHttpClient(cls.url, Method.POST, cls.pwd).with_default_data()
        response_parser = ResponseParser(cls._schema, cls.response_decoder())
        return cls(http_client, response_parser)

    @classmethod
    def build_all_variants(cls, host, port, pwd=""):
        versions = [cls._build(host, port, pwd)]
        return versions

    @classmethod
    def _decode_run_mode(cls, run_mode):
        return {
            0: "Waiting",
            1: "Checking",
            2: "Normal",
            3: "Fault",
            4: "Permanent Fault",
            5: "Updating",
        }.get(run_mode)

    @classmethod
    def _decode_switch_statue(cls, switch_statue):
        return {
            0: "Open",
            1: "Close",

        }.get(switch_statue)

    @classmethod
    def _decode_signal_strength(cls, signal_strength):
        return {
            0: "No signal",
            1: "Very weak signal",
            2: "Weak signal",
            3: "Moderate signal",
            4: "Strong signal",
            5: "Very strong signal",

        }.get(signal_strength)

    @classmethod
    def response_decoder(cls):
        return {
            "Grid Voltage": (0, Units.V, div10),
            "Grid Current": (1, Units.A, div10),
            "Grid Power": (2, Units.W, to_signed),
            "PV1 Voltage": (3, Units.V, div10),
            "PV2 Voltage": (4, Units.V, div10),
            "Pv1 Current": (5, Units.A, div10),
            "Pv2 Current": (6, Units.A, div10),
            "PV1 Power": (7, Units.W, to_signed),
            "PV2 Power": (8, Units.W, to_signed),
            "Grid Frequency": (9, Units.HZ, div100),
            "Run Mode": (10, Units.NONE, X1MiniG3._decode_run_mode),
            "Yield Total": (pack_u16(11, 12), Total(Units.KWH), div10),
            "Yield Today": (13, Units.KWH, div10),
            "Load1 Power": (26, Units.W, to_signed),
            "Load1 Yield": (pack_u16(27, 28), Total(Units.KWH), div100),
            "Load2 Power": (32, Units.W, to_signed),
            "Load2 Yield": (pack_u16(33, 34), Total(Units.KWH), div100),
            "Feed in Power": (pack_u16(48, 49), Units.W, to_signed32),
            "Feed in Energy ": (pack_u16(50, 51), Units.KWH, div100),
            "Consume Energy": (pack_u16(52, 53), Units.KWH, div100),
            "Invert temperature": (55, Units.C, to_signed),

        }

    # pylint: enable=duplicate-code

