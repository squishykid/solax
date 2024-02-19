import voluptuous as vol

from solax import utils
from solax.inverter import Inverter, InverterHttpClient, Method, ResponseParser
from solax.units import Total, Units
from solax.utils import div10, div100, pack_u16, to_signed, to_signed32


class X3Ultra(Inverter):
    # pylint: disable=duplicate-code
    _schema = vol.Schema(
        {
            vol.Required("type"): vol.All(int, 25),
            vol.Required(
                "sn",
            ): str,
            vol.Required("ver"): str,
            vol.Required("Data"): vol.Schema(
                vol.All(
                    [vol.Coerce(float)],
                    vol.Length(min=300, max=300),
                )
            ),

            vol.Required("Information"): vol.Schema(vol.All(vol.Length(min=9, max=10))),
        },
        extra=vol.REMOVE_EXTRA,
    )
    pwd: str = ''
    url: str = ''

    @classmethod
    def _build(cls, host, port, pwd="", params_in_query=True):
        cls.pwd = pwd
        cls.url = utils.to_url(host, port)
        http_client = InverterHttpClient(cls.url, Method.POST, pwd).with_default_data()

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
            6: "EpsCheck",
            7: "Eps",
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
            "Grid 1 Current": (3, Units.A, div10),
            "Grid 2 Current": (4, Units.A, div10),
            "Grid 3 Current": (5, Units.A, div10),
            "Grid 1 Power": (6, Units.W, to_signed),
            "Grid 2 Power": (7, Units.W, to_signed),
            "Grid 3 Power": (8, Units.W, to_signed),
            "PV1 Voltage": (10, Units.V, div10),
            "PV2 Voltage": (11, Units.V, div10),
            "Pv1 Current": (12, Units.A, div10),
            "Pv2 Current": (13, Units.A, div10),
            "PV1 Power": (14, Units.W, to_signed),
            "PV2 Power": (15, Units.W, to_signed),
            "Grid 1 Frequency": (16, Units.HZ, div100),
            "Grid 2 Frequency": (17, Units.HZ, div100),
            "Grid 3 Frequency": (18, Units.HZ, div100),
            "Run Mode": (19, Units.NONE, X3Ultra._decode_run_mode),
            "EPS 1 Voltage": (23, Units.V, div10),
            "EPS 2 Voltage": (24, Units.V, div10),
            "EPS 3 Voltage": (25, Units.V, div10),
            "EPS 1 Current": (26, Units.A, div10),
            "EPS 2 Current": (27, Units.A, div10),
            "EPS 3 Current": (28, Units.A, div10),
            "EPS 1 Power": (29, Units.W, to_signed),
            "EPS 2 Power": (30, Units.W, to_signed),
            "EPS 3 Power": (31, Units.W, to_signed),
            "EPS Frequency": (32, Units.HZ, div100),
            "Invert temperature": (46, Units.C, to_signed),
            "Selfuse Power": (47, Units.W, to_signed),
            "Radiator Temperature": (54, Units.C, to_signed),
            "Yield Output Today": (70, Units.KWH, div10),
            "Yield Input Total": (pack_u16(71, 72), Total(Units.KWH), div10),
            "Yield Input Today": (73, Units.KWH, div10),
            "Battery Discharge Total": (pack_u16(74, 75), Total(Units.KWH), div10),
            "Battery Charge Total": (pack_u16(76, 77), Total(Units.KWH), div10),
            "Output Energy Charge Today": (78, Units.KWH, div10),
            "Input Energy Charge Today": (79, Units.KWH, div10),
            "Pv Yield Total": (pack_u16(80, 81), Total(Units.KWH), div10),
            "Solar Energy Today": (82, Units.KWH, div10),
            "Eps Yield Total": (pack_u16(83, 84), Total(Units.KWH), div10),
            "Eps Yield Today": (85, Units.KWH, div10),
            "Feed in Energy Total": (pack_u16(86, 87), Units.KWH, div100),
            "Consume Total": (pack_u16(88, 89), Total(Units.KWH), div100),
            "Feed in Energy Today": (pack_u16(90, 91), Units.KWH, div100),
            "Consume Today": (pack_u16(92, 93), Total(Units.KWH), div100),
            "Battery 1 Capacity": (103, Units.PERCENT),
            "Battery 1 Temperature": (105, Units.C, to_signed),
            "Battery 1 Surplus Energy": (106, Units.KWH, div10),
            "PV3 Voltage": (129, Units.V, div10),
            "Pv3 Current": (130, Units.A, div10),
            "PV3 Power": (131, Units.W, to_signed),
            "Battery 2 Capacity": (140, Units.PERCENT),
            "Battery 2 Temperature": (142, Units.C, to_signed),
            "Battery 2 Surplus Energy": (143, Units.W, div10),

        }

    # pylint: enable=duplicate-code
