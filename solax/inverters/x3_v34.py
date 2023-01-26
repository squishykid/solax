from solax.inverter import (
    Inverter,
    InverterDataValue,
    InverterDefinition,
    InverterIdentification,
)
from solax.units import Measurement, Total, Units
from solax.utils import (
    div10,
    div100,
    to_signed,
    twoway_div10,
    twoway_div100,
    u16_packer,
)


class X3V34(Inverter):
    """X3 v2.034.06"""

    @classmethod
    def inverter_definition(cls) -> InverterDefinition:
        return InverterDefinition(
            "XHybrid",
            InverterIdentification(5),
            {
                "Network Voltage Phase 1": InverterDataValue(
                    (0,), Measurement(Units.V), (div10,)
                ),
                "Network Voltage Phase 2": InverterDataValue(
                    (1,), Measurement(Units.V), (div10,)
                ),
                "Network Voltage Phase 3": InverterDataValue(
                    (2,), Measurement(Units.V), (div10,)
                ),
                "Output Current Phase 1": InverterDataValue(
                    (3,), Measurement(Units.A), (twoway_div10,)
                ),
                "Output Current Phase 2": InverterDataValue(
                    (4,), Measurement(Units.A), (twoway_div10,)
                ),
                "Output Current Phase 3": InverterDataValue(
                    (5,), Measurement(Units.A), (twoway_div10,)
                ),
                "Power Now Phase 1": InverterDataValue(
                    (6,), Measurement(Units.W), (to_signed,)
                ),
                "Power Now Phase 2": InverterDataValue(
                    (7,), Measurement(Units.W), (to_signed,)
                ),
                "Power Now Phase 3": InverterDataValue(
                    (8,), Measurement(Units.W), (to_signed,)
                ),
                "PV1 Voltage": InverterDataValue((9,), Measurement(Units.V), (div10,)),
                "PV2 Voltage": InverterDataValue((10,), Measurement(Units.V), (div10,)),
                "PV1 Current": InverterDataValue((11,), Measurement(Units.A), (div10,)),
                "PV2 Current": InverterDataValue((12,), Measurement(Units.A), (div10,)),
                "PV1 Power": InverterDataValue((13,), Measurement(Units.W)),
                "PV2 Power": InverterDataValue((14,), Measurement(Units.W)),
                "Total PV Energy": InverterDataValue(
                    (89, 90),
                    Total(Units.KWH),
                    (
                        u16_packer,
                        div10,
                    ),
                ),
                "Today's PV Energy": InverterDataValue(
                    (112,), Measurement(Units.KWH), (div10,)
                ),
                "Grid Frequency Phase 1": InverterDataValue(
                    (15,), Measurement(Units.HZ), (div100,)
                ),
                "Grid Frequency Phase 2": InverterDataValue(
                    (16,), Measurement(Units.HZ), (div100,)
                ),
                "Grid Frequency Phase 3": InverterDataValue(
                    (17,), Measurement(Units.HZ), (div100,)
                ),
                "Total Energy": InverterDataValue(
                    (19, 20),
                    Total(Units.KWH),
                    (
                        u16_packer,
                        div10,
                    ),
                ),
                "Today's Energy": InverterDataValue(
                    (21,), Measurement(Units.KWH), (div10,)
                ),
                "Battery Voltage": InverterDataValue(
                    (24,), Measurement(Units.V), (div100,)
                ),
                "Battery Current": InverterDataValue(
                    (25,), Measurement(Units.A), (twoway_div100,)
                ),
                "Battery Power": InverterDataValue(
                    (26,), Measurement(Units.W), (to_signed,)
                ),
                "Battery Temperature": InverterDataValue((27,), Measurement(Units.C)),
                "Battery Remaining Capacity": InverterDataValue(
                    (28,), Measurement(Units.PERCENT)
                ),
                "Total Battery Discharge Energy": InverterDataValue(
                    (30, 31),
                    Total(Units.KWH),
                    (
                        u16_packer,
                        div10,
                    ),
                ),
                "Today's Battery Discharge Energy": InverterDataValue(
                    (113,), Measurement(Units.KWH), (div10,)
                ),
                "Battery Remaining Energy": InverterDataValue(
                    (32,), Measurement(Units.KWH), (div10,)
                ),
                "Total Battery Charge Energy": InverterDataValue(
                    (87, 88),
                    Total(Units.KWH),
                    (
                        u16_packer,
                        div10,
                    ),
                ),
                "Today's Battery Charge Energy": InverterDataValue(
                    (114,), Measurement(Units.KWH), (div10,)
                ),
                "Exported Power": InverterDataValue(
                    (65,), Measurement(Units.W), (to_signed,)
                ),
                "Total Feed-in Energy": InverterDataValue(
                    (67, 68),
                    Total(Units.KWH),
                    (
                        u16_packer,
                        div100,
                    ),
                ),
                "Total Consumption": InverterDataValue(
                    (69, 70),
                    Total(Units.KWH),
                    (
                        u16_packer,
                        div100,
                    ),
                ),
                "AC Power": InverterDataValue(
                    (181,), Measurement(Units.W), (to_signed,)
                ),
                "EPS Frequency": InverterDataValue(
                    (63,), Measurement(Units.HZ), (div100,)
                ),
                "EPS Total Energy": InverterDataValue(
                    (110, 111),
                    Measurement(Units.KWH),
                    (
                        u16_packer,
                        div10,
                    ),
                ),
            },
        )

    # pylint: enable=duplicate-code
