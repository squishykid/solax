import voluptuous as vol
from solax import utils
from solax.inverter import Inverter, InverterHttpClient, Method, ResponseParser
from solax.units import Units, Total
from solax.utils import div10, div100, to_signed


class X1Boost(Inverter):
    """
    X1-Boost with Pocket WiFi 2.034.06
    Includes X-Forwarded-For for direct LAN API access
    """

    # pylint: disable=duplicate-code
    _schema = vol.Schema(
        {
            vol.Required("type", "type"): vol.All(int, 4),
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
            vol.Required("Information"): vol.Schema(
                vol.All(vol.Length(min=10, max=10))
            ),
        },
        extra=vol.REMOVE_EXTRA,
    )

    @classmethod
    def response_decoder(cls):
        return {
            "AC Voltage": (0, Units.V, div10),
            "AC Output Current": (1, Units.A, div10),
            "AC Output Power": (2, Units.W),
            "PV1 Voltage": (3, Units.V, div10),
            "PV2 Voltage": (4, Units.V, div10),
            "PV1 Current": (5, Units.A, div10),
            "PV2 Current": (6, Units.A, div10),
            "PV1 Power": (7, Units.W),
            "PV2 Power": (8, Units.W),
            "AC Frequency": (9, Units.HZ, div100),
            "Total Generated Energy": (11, Total(Units.KWH), div10),
            "Today's Generated Energy": (13, Total(Units.KWH), div10),
            "Inverter Temperature": (39, Units.C),
            "Exported Power": (48, Units.W, to_signed),
            "Total Export Energy": (50, Total(Units.KWH), div100),
            "Total Import Energy": (52, Total(Units.KWH), div100),
        }

    @classmethod
    def _build(cls, host, port, pwd="", params_in_query=True):
        url = utils.to_url(host, port)
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
