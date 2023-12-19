import voluptuous as vol

from solax import utils
from solax.inverter import Inverter, InverterHttpClient, Method, ResponseParser
from solax.units import Total, Units
from solax.utils import div10, div100, pack_u16, to_signed, to_signed32


class X1HybridLv(Inverter):
    # pylint: disable=duplicate-code
    _schema = vol.Schema(
        {
            vol.Required("type"): vol.All(int, 102),
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
    def _build(cls, host, port, pwd="", params_in_query=True):
        cls.url = utils.to_url(host, port)
        cls.pwd = pwd
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
            6: "EpsCheck",
            7: "Eps",
            8: "Self Test",
            9: "Idle",
            10: "Standby",
        }.get(run_mode)

    @classmethod
    def response_decoder(cls):
        return {
            "Grid Voltage": (0, Units.V, div10),
            "Grid Current": (1, Units.A, div10),
            "Grid Power": (2, Units.W, to_signed),
            "Grid Frequency": (3, Units.HZ, div100),
            "PV1 Voltage": (5, Units.V, div10),
            "Pv1 Current": (6, Units.A, div10),
            "PV2 Voltage": (7, Units.V, div10),
            "Pv2 Current": (8, Units.A, div10),
            "PV1 Power": (9, Units.W, to_signed),
            "PV2 Power": (10, Units.W, to_signed),
            "Run Mode": (12, Units.NONE, X1HybridLv._decode_run_mode),
            "Yield Total": (pack_u16(14, 15), Total(Units.KWH), div10),
            "Consume Total": (pack_u16(16, 17), Total(Units.KWH), div10),
            "Yield Today": (18, Units.KWH, div10),
            "Consume Today": (19, Units.KWH, div10),
            "Battery Voltage": (20, Units.V, div10),
            "Battery Current": (21, Units.A, div10),
            "Battery Power": (22, Units.W, to_signed),
            "Battery Charge Total": (pack_u16(23, 24), Total(Units.KWH), div10),
            "Battery Discharge Total": (pack_u16(25, 26), Total(Units.KWH), div10),
            "Battery Charge Today": (27, Total(Units.KWH), div10),
            "Battery Discharge Today": (28, Total(Units.KWH), div10),
            "Feed in Power": (pack_u16(29, 30), Units.W, to_signed32),
            "Feed in Energy Total": (pack_u16(31, 32), Units.KWH, div10),
            "Consume Energy Total": (pack_u16(33, 34), Units.KWH, div10),
            "Feed in Energy Today": (pack_u16(35, 36), Units.KWH, div10),
            "Consume Energy Today": (pack_u16(37, 38), Units.KWH, div10),
            "Invert temperature": (39, Units.C, div10),
            "Radiator Temperature": (40, Units.C, div10),
            "EPS Voltage": (41, Units.V, div10),
            "EPS Current": (42, Units.A, div10),
            "EPS Power": (43, Units.W, div10),
            "EPS Frequency": (44, Units.HZ, div100),
            "EPS Today": (45, Units.KWH, div10),
            "EPS Total": (pack_u16(46, 47), Units.KWH, div10),
            "PV Today": (51, Units.KWH, div10),
            "PV Total": (pack_u16(52, 53), Units.KWH, div10),

        }

    # pylint: enable=duplicate-code
