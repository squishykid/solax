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
    to_signed32,
    twoway_div10,
    u16_packer,
)


class X3HybridG4(Inverter):
    """X3 Hybrid G4 v3.006.04"""

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
        }.get(run_mode)

    @classmethod
    def inverter_definition(cls):
        return InverterDefinition(
            "X3 Hybrid G4",
            InverterIdentification(14),
            {
                "Grid 1 Voltage": InverterDataValue(
                    (0,), Measurement(Units.V), (div10,)
                ),
                "Grid 2 Voltage": InverterDataValue(
                    (1,), Measurement(Units.V), (div10,)
                ),
                "Grid 3 Voltage": InverterDataValue(
                    (2,), Measurement(Units.V), (div10,)
                ),
                "Grid 1 Current": InverterDataValue(
                    (3,), Measurement(Units.A), (twoway_div10,)
                ),
                "Grid 2 Current": InverterDataValue(
                    (4,), Measurement(Units.A), (twoway_div10,)
                ),
                "Grid 3 Current": InverterDataValue(
                    (5,), Measurement(Units.A), (twoway_div10,)
                ),
                "Grid 1 Power": InverterDataValue(
                    (6,), Measurement(Units.W), (to_signed,)
                ),
                "Grid 2 Power": InverterDataValue(
                    (7,), Measurement(Units.W), (to_signed,)
                ),
                "Grid 3 Power": InverterDataValue(
                    (8,), Measurement(Units.W), (to_signed,)
                ),
                "PV1 Voltage": InverterDataValue((10,), Measurement(Units.V), (div10,)),
                "PV2 Voltage": InverterDataValue((11,), Measurement(Units.V), (div10,)),
                "PV1 Current": InverterDataValue((12,), Measurement(Units.A), (div10,)),
                "PV2 Current": InverterDataValue((13,), Measurement(Units.A), (div10,)),
                "PV1 Power": InverterDataValue((14,), Measurement(Units.W)),
                "PV2 Power": InverterDataValue((15,), Measurement(Units.W)),
                "Grid 1 Frequency": InverterDataValue(
                    (16,), Measurement(Units.HZ), (div100,)
                ),
                "Grid 2 Frequency": InverterDataValue(
                    (17,), Measurement(Units.HZ), (div100,)
                ),
                "Grid 3 Frequency": InverterDataValue(
                    (18,), Measurement(Units.HZ), (div100,)
                ),
                "Run mode": InverterDataValue((19,), Measurement(Units.NONE)),
                "Run mode text": InverterDataValue(
                    (19,), Measurement(Units.NONE), (X3HybridG4._decode_run_mode,)
                ),
                "EPS 1 Voltage": InverterDataValue(
                    (23,), Measurement(Units.W), (div10,)
                ),
                "EPS 2 Voltage": InverterDataValue(
                    (24,), Measurement(Units.W), (div10,)
                ),
                "EPS 3 Voltage": InverterDataValue(
                    (25,), Measurement(Units.W), (div10,)
                ),
                "EPS 1 Current": InverterDataValue(
                    (26,), Measurement(Units.W), (twoway_div10,)
                ),
                "EPS 2 Current": InverterDataValue(
                    (27,), Measurement(Units.W), (twoway_div10,)
                ),
                "EPS 3 Current": InverterDataValue(
                    (28,), Measurement(Units.W), (twoway_div10,)
                ),
                "EPS 1 Power": InverterDataValue(
                    (29,), Measurement(Units.W), (to_signed,)
                ),
                "EPS 2 Power": InverterDataValue(
                    (30,), Measurement(Units.W), (to_signed,)
                ),
                "EPS 3 Power": InverterDataValue(
                    (31,), Measurement(Units.W), (to_signed,)
                ),
                "Feed-in Power ": InverterDataValue(
                    (34, 35),
                    Measurement(Units.W),
                    (
                        u16_packer,
                        to_signed32,
                    ),
                ),
                "Battery Power": InverterDataValue(
                    (41,), Measurement(Units.W), (to_signed,)
                ),
                "Yield total": InverterDataValue(
                    (68, 69),
                    Total(Units.KWH),
                    (
                        u16_packer,
                        div10,
                    ),
                ),
                "Yield today": InverterDataValue(
                    (70,), Measurement(Units.HZ), (div10,)
                ),
                "Feed-in Energy": InverterDataValue(
                    (86, 87),
                    Total(Units.KWH),
                    (
                        u16_packer,
                        div100,
                    ),
                ),
                "Consumed Energy": InverterDataValue(
                    (88, 89),
                    Total(Units.KWH),
                    (
                        u16_packer,
                        div100,
                    ),
                ),
                "Battery Remaining Capacity": InverterDataValue(
                    (103,), Measurement(Units.PERCENT)
                ),
                "Battery Temperature": InverterDataValue(
                    (105,), Measurement(Units.C), (to_signed,)
                ),
                "Battery Voltage": InverterDataValue(
                    (169, 170),
                    Measurement(Units.V),
                    (
                        u16_packer,
                        div100,
                    ),
                ),
            },
        )
