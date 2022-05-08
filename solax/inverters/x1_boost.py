import voluptuous as vol
from solax.inverter import InverterPost
from solax.utils import div10, div100, to_signed


class X1Boost(InverterPost):
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

    _sensor_map = {
        "AC Voltage": (0, "V", div10),
        "AC Output Current": (1, "A", div10),
        "AC Output Power": (2, "W"),
        "PV1 Voltage": (3, "V", div10),
        "PV2 Voltage": (4, "V", div10),
        "PV1 Current": (5, "A", div10),
        "PV2 Current": (6, "A", div10),
        "PV1 Power": (7, "W"),
        "PV2 Power": (8, "W"),
        "AC Frequency": (9, "Hz", div100),
        "Total Generated Energy": (11, "kWh", div10),
        "Today's Generated Energy": (13, "kWh", div10),
        "Inverter Temperature": (39, "C"),
        "Exported Power": (48, "W", to_signed),
        "Total Export Energy": (50, "kWh", div100),
        "Total Import Energy": (52, "kWh", div100),
    }

    @classmethod
    async def make_request(cls, host, port=80, pwd="", headers=None):
        headers = {"X-Forwarded-For": "5.8.8.8"}
        return await super().make_request(host, port, pwd, headers=headers)
