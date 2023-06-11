import voluptuous as vol

from solax.inverter import Inverter, InverterHttpClient, Method, ResponseParser
from solax.units import Total, Units
from solax.utils import startswith, to_url


class X1(Inverter):
    """
    X1 with Pocket WiFi 2.034.06
    Includes X-Forwarded-For for direct LAN API access
    """

    # pylint: disable=duplicate-code
    _schema = vol.Schema(
        {
            vol.Required("type"): vol.All(str, startswith("X1-")),
            vol.Required("SN"): str,
            vol.Required("ver"): str,
            vol.Required("Data"): vol.Schema(
                vol.All(
                    [vol.Coerce(float)],
                    vol.Any(
                        vol.Length(min=102, max=102),
                        vol.Length(min=103, max=103),
                        vol.Length(min=107, max=107),
                    ),
                )
            ),
            vol.Required("Information"): vol.Schema(vol.All(vol.Length(min=9, max=9))),
        },
        extra=vol.REMOVE_EXTRA,
    )

    @classmethod
    def _decode_work_mode(cls, work_mode):
        return {
            0: "Self Use",
            1: "Force Time Use",
            2: "Backup Mode",
            3: "Feed In Priority",
        }.get(work_mode)

    @classmethod
    def response_decoder(cls):
        return {
            "PV1 Current": (0, Units.A),
            "PV2 Current": (1, Units.A),
            "PV1 Voltage": (2, Units.V),
            "PV2 Voltage": (3, Units.V),
            "Output Current": (4, Units.A),
            "Network Voltage": (5, Units.V),
            "AC Power": (6, Units.W),
            "Inverter Temperature": (7, Units.C),
            "Today's Energy": (8, Units.KWH),
            "Total Energy": (9, Total(Units.KWH)),
            "Exported Power": (10, Units.W),
            "PV1 Power": (11, Units.W),
            "PV2 Power": (12, Units.W),
            "Battery Voltage": (13, Units.V),
            "Battery Current": (14, Units.A),
            "Battery Power": (15, Units.W),
            "Battery Temperature": (16, Units.C),
            "Battery Remaining Capacity": (21, Units.PERCENT),
            "Total Feed-in Energy": (41, Total(Units.KWH)),
            "Total Consumption": (42, Total(Units.KWH)),
            "Power Now": (43, Units.W),
            "Grid Frequency": (50, Units.HZ),
            "EPS Voltage": (53, Units.V),
            "EPS Current": (54, Units.A),
            "EPS Power": (55, Units.W),
            "EPS Frequency": (56, Units.HZ),
            "Export Limit": (72, Units.W),
            "Battery Minimum Capacity": (74, Units.PERCENT),
            "Charge Max Current": (75, Units.A),
            "Discharge Max Current": (76, Units.A),
            "Work Mode": (77, Units.NONE, X1._decode_work_mode),
        }

    @classmethod
    def _build(cls, host, port, pwd="", params_in_query=True):
        url = to_url(host, port)
        http_client = InverterHttpClient(url, Method.POST, pwd)
        if params_in_query:
            http_client.with_default_query()
        else:
            http_client.with_default_data()

        headers = {"X-Forwarded-For": "5.8.8.8"}
        http_client.with_headers(headers)
        schema = cls._schema
        response_decoder = cls.response_decoder()
        response_parser = ResponseParser(schema, response_decoder)
        return cls(http_client, response_parser)

    @classmethod
    def build_all_variants(cls, host, port, pwd=""):
        versions = [
            cls._build(host, port, pwd, True),
            cls._build(host, port, pwd, False),
        ]
        return versions

    # pylint: enable=duplicate-code
