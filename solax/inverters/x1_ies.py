import voluptuous as vol

from solax import utils
from solax.inverter import Inverter, InverterHttpClient, Method, ResponseParser
from solax.units import Total, Units
from solax.utils import div10, div100, pack_u16, to_signed, to_signed32


class X1Ies(Inverter):
    # pylint: disable=duplicate-code
    _schema = vol.Schema(
        {
            vol.Required("type"): vol.All(int, 23),
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
            11: "Init",
        }.get(run_mode)

    @classmethod
    def response_decoder(cls):
        return {
            "Grid Voltage": (0, Units.V, div10),
            "Grid Current": (1, Units.A, div10),
            "Grid Power": (2, Units.W, to_signed),
            "Grid Frequency": (3, Units.HZ, div100),
            "PV1 Voltage": (4, Units.V, div10),
            "PV2 Voltage": (5, Units.V, div10),
            "Pv1 Current": (6, Units.A, div10),
            "Pv2 Current": (7, Units.A, div10),
            "PV1 Power": (8, Units.W, to_signed),
            "PV2 Power": (9, Units.W, to_signed),
            "Run Mode": (10, Units.NONE, X1Ies._decode_run_mode),
            "Yield Total": (pack_u16(11, 12), Total(Units.KWH), div10),
            "Yield Today": (13, Units.KWH, div10),
            "Battery Voltage": (14, Units.V, div100),
            "Battery Current": (15, Units.A, div100),
            "Battery Power": (16, Units.W, to_signed),
            "Battery Temperature": (17, Units.C, to_signed),
            "Battery Capacity": (18, Units.PERCENT),
            "Battery Discharge Total": (pack_u16(19, 20), Total(Units.KWH), div10),
            "Battery Charge Total": (pack_u16(21, 22), Total(Units.KWH), div10),
            "Battery Surplus Energy": (23, Units.W, div10),
            "Radiator Temperature": (26, Units.C, to_signed),
            "EPS Power": (28, Units.W, to_signed),
            "EPS Voltage": (29, Units.V, div10),
            "EPS Current": (30, Units.A, div10),
            "EPS Frequency": (31, Units.HZ, div100),
            "Feed in Power": (pack_u16(32, 33), Units.W, to_signed32),
            "Feed in Energy Total": (pack_u16(34, 35), Units.KWH, div100),
            "Consume Total": (pack_u16(36, 37), Total(Units.KWH), div100),
            "Selfuse Power": (38, Units.W, to_signed),
            "Invert temperature": (39, Units.C, to_signed),
            "Feed in Energy Today": (pack_u16(78, 79), Units.KWH, div100),
            "Consume Energy Today": (pack_u16(80, 81), Units.KWH, div100),
            "EPS Today": (82, Units.KWH, div10),
            "EPS Total": (pack_u16(83, 84), Units.KWH, div10),

        }

    # pylint: enable=duplicate-code
