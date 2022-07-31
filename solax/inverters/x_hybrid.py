import json
import aiohttp
import voluptuous as vol
from solax.inverter import Inverter, InverterResponse
from solax.units import Total, Units


class XHybrid(Inverter):
    """
    Tested with:
    * SK-TL5000E
    """

    _schema = vol.Schema(
        {
            vol.Required("method"): str,
            vol.Required("version"): str,
            vol.Required("type"): str,
            vol.Required("SN"): str,
            vol.Required("Data"): vol.Schema(
                vol.All(
                    [vol.Coerce(float)],
                    vol.Any(vol.Length(min=58, max=58), vol.Length(min=68, max=68)),
                )
            ),
            vol.Required("Status"): vol.All(vol.Coerce(int), vol.Range(min=0)),
        },
        extra=vol.REMOVE_EXTRA,
    )

    # key: name of sensor
    # value.0: index
    # value.1: unit (String) or None
    # from https://github.com/GitHobi/solax/wiki/direct-data-retrieval
    @classmethod
    def response_decoder(cls):
        return {
            "PV1 Current": (0, Units.A),
            "PV2 Current": (1, Units.A),
            "PV1 Voltage": (2, Units.V),
            "PV2 Voltage": (3, Units.V),
            "Output Current": (4, Units.A),
            "Network Voltage": (5, Units.V),
            "Power Now": (6, Units.W),
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
            "Battery Remaining Capacity": (17, Units.PERCENT),
            "Month's Energy": (19, Units.KWH),
            "Grid Frequency": (50, Units.HZ),
            "EPS Voltage": (53, Units.V),
            "EPS Current": (54, Units.A),
            "EPS Power": (55, Units.W),
            "EPS Frequency": (56, Units.HZ),
        }

    @classmethod
    async def make_request(cls, host, port=80, pwd="", headers=None):
        base = "http://{}:{}/api/realTimeData.htm"
        url = base.format(host, port)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as req:
                garbage = await req.read()
        formatted = garbage.decode("utf-8")
        formatted = formatted.replace(",,", ",0.0,").replace(",,", ",0.0,")
        json_response = json.loads(formatted)
        response = cls.schema()(json_response)
        return InverterResponse(
            data=cls.map_response(response["Data"]),
            serial_number=response["SN"],
            version=response["version"],
            type=response["type"],
        )
