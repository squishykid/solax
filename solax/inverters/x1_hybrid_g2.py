import voluptuous as vol

from solax import utils
from solax.inverter import Inverter, InverterHttpClient, Method, ResponseParser
from solax.units import Total, Units
from solax.utils import div10, div100, pack_u16, to_signed, to_signed32


class X1HybridG2(Inverter):
    # pylint: disable=duplicate-code
    _schema = vol.Schema(
        {
            vol.Required("type"): vol.All(int, 19),
            vol.Required(
                "sn",
            ): str,
            vol.Required("ver"): str,
            vol.Required("Data"): vol.Schema(
                vol.All(
                    [vol.Coerce(float)],
                    vol.Length(min=290, max=300),
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
            6: "EPS Check",
            7: "EPS Mode",
            8: "Self Test",
            9: "Idle",
            10: "Standby",
            11: "Gen Check Mode",
            12: "Gen Run Mode",
            13: "RSD Standby",
        }.get(run_mode)

    @classmethod
    def response_decoder(cls):
        return {
            "Grid Voltage": (4, Units.V, div10),
            "Grid Current": (5, Units.A, div10),
            "Grid Power": (6, Units.W, to_signed),
            "Grid Frequency": (7, Units.HZ, div100),
            "Run Mode": (10, Units.NONE, X1HybridG2._decode_run_mode),
            "PV1 Voltage": (11, Units.V, div10),
            "PV2 Voltage": (12, Units.V, div10),
            "PV3 Voltage": (13, Units.V, div10),
            "Pv1 Current": (15, Units.A, div10),
            "Pv2 Current": (16, Units.A, div10),
            "Pv3 Current": (17, Units.A, div10),
            "PV1 Power": (19, Units.W, to_signed),
            "PV2 Power": (20, Units.W, to_signed),
            "PV3 Power": (21, Units.W, to_signed),
            "EPS Apparent Power": (23, Units.W, to_signed),
            "EPS Voltage": (24, Units.V, div10),
            "EPS Current": (25, Units.A, div10),
            "EPS Frequency": (26, Units.HZ, div100),
            "EPS Active Power": (27, Units.W, to_signed),
            "Feed in Power": (pack_u16(28, 29), Units.W, to_signed32),
            "Selfuse Power": (30, Units.W, to_signed),
            "Active Power": (31, Units.W, to_signed),
            "ReactivePower": (32, Units.W, to_signed),
            "Feed in Energy ": (pack_u16(33, 34), Units.KWH, div10),
            "Consume Energy": (pack_u16(35, 36), Units.KWH, div10),
            "Feedin Energy Today": (pack_u16(37, 38), Units.KWH, div10),
            "Consume Energy Today": (pack_u16(39, 40), Units.KWH, div10),
            "Yield Total": (pack_u16(41, 42), Total(Units.KWH), div10),
            "Yield Today": (43, Units.KWH, div10),
            "Solar Yield Total": (pack_u16(44, 45), Units.KWH, div10),
            "Solar Yield Today": (46, Units.KWH, div10),
            "Eps Yield Total": (pack_u16(47, 48), Units.KWH, div10),
            "Eps Yield Today": (49, Units.KWH, div10),
            "BatCharge Yield Total": (pack_u16(50, 51), Units.KWH, div10),
            "OutputEnergy Charge Today": (52, Units.W, div10),
            "InputEnergy Charge Today": (53, Units.W, div10),
            "Green Solar Yield Total": (pack_u16(54, 55), Units.KWH, div10),
            "Green Solar Yield Today": (56, Units.W, div10),
            "Battery Voltage": (89, Units.V, div100),
            "Battery Current": (90, Units.A, div100),
            "Battery Power": (91, Units.W, to_signed),
            "Battery Temperature": (92, Units.C, to_signed),
            "Battery Capacity": (93, Units.PERCENT),
            "Battery OutputEnergy": (pack_u16(94, 95), Units.KWH, div10),
            "Battery SurplusEnergy": (99, Units.KWH, div10),
        }
    # pylint: enable=duplicate-code
