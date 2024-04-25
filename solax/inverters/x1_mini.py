from typing import Any, Dict, Optional

import voluptuous as vol

from solax.inverter import Inverter
from solax.units import DailyTotal, Total, Units
from solax.utils import startswith


class X1Mini(Inverter):
    # pylint: disable=duplicate-code
    _schema = vol.Schema(
        {
            vol.Required("type"): vol.All(str, startswith("X1-")),
            vol.Required("sn"): str,
            vol.Required("ver"): str,
            vol.Required("data"): vol.Schema(
                vol.All(
                    [vol.Coerce(float)],
                    vol.Length(min=69, max=69),
                )
            ),
            vol.Required("information"): vol.Schema(vol.All(vol.Length(min=9, max=9))),
        },
        extra=vol.REMOVE_EXTRA,
    )

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
            "Today's Energy": (8, DailyTotal(Units.KWH)),
            "Total Energy": (9, Total(Units.KWH)),
            "Exported Power": (10, Units.W),
            "PV1 Power": (11, Units.W),
            "PV2 Power": (12, Units.W),
            "Total Feed-in Energy": (41, Total(Units.KWH)),
            "Total Consumption": (42, Total(Units.KWH)),
            "Power Now": (43, Units.W),
            "Grid Frequency": (50, Units.HZ),
        }

    # pylint: enable=duplicate-code

    @classmethod
    def inverter_serial_number_getter(cls, response: Dict[str, Any]) -> Optional[str]:
        return response["information"][3]
