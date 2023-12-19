import voluptuous as vol

from solax import utils
from solax.inverter import Inverter, InverterHttpClient, Method, ResponseParser
from solax.units import Total, Units
from solax.utils import div10, div100, pack_u16, to_signed, to_signed32


class X1MiniG4(Inverter):
    # pylint: disable=duplicate-code
    _schema = vol.Schema(
        {
            vol.Required("type"): vol.All(int, 22),
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
            6: "EpsCheck",
            7: "Eps",
        }.get(run_mode)



    @classmethod
    def response_decoder(cls):
        return {
            "Grid Voltage": (0, Units.V, div10),
            "Grid Current": (1, Units.A, div10),
            "Grid Frequency": (2, Units.HZ, div100),
            "Grid Power": (3, Units.W, to_signed),
            "PV1 Voltage": (4, Units.V, div10),
            "PV2 Voltage": (5, Units.V, div10),
            "PV3 Voltage": (6, Units.V, div10),
            "PV4 Voltage": (7, Units.V, div10),
            "Pv1 Current": (8, Units.A, div10),
            "Pv2 Current": (9, Units.A, div10),
            "Run Mode": (10, Units.NONE, X1MiniG4._decode_run_mode),
            "Pv3 Current": (11, Units.A, div10),
            "Pv4 Current": (12, Units.A, div10),
            "PV1 Power": (13, Units.W, to_signed),
            "PV2 Power": (14, Units.W, to_signed),
            "PV3 Power": (15, Units.W, to_signed),
            "PV4 Power": (16, Units.W, to_signed),
            "Yield Total": (pack_u16(19, 20), Total(Units.KWH), div10),
            "Yield Today": (21, Units.KWH, div10),
            "Rate Power": (22, Units.KWH, to_signed),
            "Radiator Temperature": (23, Units.C, to_signed),
            "Invert temperature": (24, Units.C, to_signed),
            "Feed in Power": (pack_u16(72, 73), Units.W, to_signed32),
            "Feed in Energy ": (pack_u16(74, 75), Units.KWH, div100),
            "Consume Energy": (pack_u16(76, 77), Units.KWH, div100),


        }

    # pylint: enable=duplicate-code

