import voluptuous as vol
from solax.inverter import InverterPost
from solax.units import Total, Units
from solax.utils import (
    div10,
    div100,
    twoway_div10,
    to_signed,
    pv_energy,
    twoway_div100,
    total_energy,
    discharge_energy,
    charge_energy,
    feedin_energy,
    consumption,
    eps_total_energy,
)


class X3V34(InverterPost):
    """X3 v2.034.06"""

    # pylint: disable=duplicate-code
    _schema = vol.Schema(
        {
            vol.Required("type"): vol.All(int, 5),
            vol.Required("sn"): str,
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
            "Network Voltage Phase 1": (0, Units.V, div10),
            "Network Voltage Phase 2": (1, Units.V, div10),
            "Network Voltage Phase 3": (2, Units.V, div10),
            "Output Current Phase 1": (3, Units.A, twoway_div10),
            "Output Current Phase 2": (4, Units.A, twoway_div10),
            "Output Current Phase 3": (5, Units.A, twoway_div10),
            "Power Now Phase 1": (6, Units.W, to_signed),
            "Power Now Phase 2": (7, Units.W, to_signed),
            "Power Now Phase 3": (8, Units.W, to_signed),
            "PV1 Voltage": (9, Units.V, div10),
            "PV2 Voltage": (10, Units.V, div10),
            "PV1 Current": (11, Units.A, div10),
            "PV2 Current": (12, Units.A, div10),
            "PV1 Power": (13, Units.W),
            "PV2 Power": (14, Units.W),
            "Total PV Energy": (89, Total(Units.KWH), pv_energy),
            "Total PV Energy Resets": (90),
            "Today's PV Energy": (112, Units.KWH, div10),
            "Grid Frequency Phase 1": (15, Units.HZ, div100),
            "Grid Frequency Phase 2": (16, Units.HZ, div100),
            "Grid Frequency Phase 3": (17, Units.HZ, div100),
            "Total Energy": (19, Total(Units.KWH), total_energy),
            "Total Energy Resets": (20),
            "Today's Energy": (21, Units.KWH, div10),
            "Battery Voltage": (24, Units.V, div100),
            "Battery Current": (25, Units.A, twoway_div100),
            "Battery Power": (26, Units.W, to_signed),
            "Battery Temperature": (27, Units.C),
            "Battery Remaining Capacity": (28, Units.PERCENT),
            "Total Battery Discharge Energy": (30, Total(Units.KWH), discharge_energy),
            "Total Battery Discharge Energy Resets": (31),
            "Today's Battery Discharge Energy": (113, Units.KWH, div10),
            "Battery Remaining Energy": (32, Units.KWH, div10),
            "Total Battery Charge Energy": (87, Total(Units.KWH), charge_energy),
            "Total Battery Charge Energy Resets": (88),
            "Today's Battery Charge Energy": (114, Units.KWH, div10),
            "Exported Power": (65, Units.W, to_signed),
            "Total Feed-in Energy": (67, Total(Units.KWH), feedin_energy),
            "Total Feed-in Energy Resets": (68),
            "Total Consumption": (69, Total(Units.KWH), consumption),
            "Total Consumption Resets": (70),
            "AC Power": (181, Units.W, to_signed),
            "EPS Frequency": (63, Units.HZ, div100),
            "EPS Total Energy": (110, Units.KWH, eps_total_energy),
            "EPS Total Energy Resets": (111, Units.HZ),
        }

    # pylint: enable=duplicate-code
