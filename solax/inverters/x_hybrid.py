from typing import Any, Dict, Optional

import voluptuous as vol

from solax.inverter import Inverter, InverterHttpClient, Method
from solax.units import DailyTotal, Total, Units


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
            vol.Required("sn"): str,
            vol.Required("data"): vol.Schema(
                vol.All(
                    [vol.Coerce(float)],
                    vol.Any(vol.Length(min=58, max=58), vol.Length(min=68, max=68)),
                )
            ),
            vol.Required("status"): vol.All(vol.Coerce(int), vol.Range(min=0)),
        },
        extra=vol.REMOVE_EXTRA,
    )

    @classmethod
    def _build(cls, host, port, pwd="", params_in_query=True):
        base = "http://{}:{}/api/realTimeData.htm"
        url = base.format(host, port)
        http_client = InverterHttpClient(url=url, method=Method.GET, pwd="")

        return cls(http_client)

    @classmethod
    def build_all_variants(cls, host, port, pwd=""):
        versions = [cls._build(host, port)]
        return versions

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
            "Today's Energy": (8, DailyTotal(Units.KWH)),
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
            "Grid Exported Energy": (41, Units.KWH),
            "Grid Imported Energy": (42, Units.KWH),
            "Grid Frequency": (50, Units.HZ),
            "EPS Voltage": (53, Units.V),
            "EPS Current": (54, Units.A),
            "EPS Power": (55, Units.W),
            "EPS Frequency": (56, Units.HZ),
        }

    @classmethod
    def inverter_serial_number_getter(cls, response: Dict[str, Any]) -> Optional[str]:
        return None
