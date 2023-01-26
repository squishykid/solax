from solax.inverter import (
    Inverter,
    InverterDataValue,
    InverterDefinition,
    InverterIdentification,
)
from solax.units import Measurement, Total, Units


class X3(Inverter):
    @classmethod
    def inverter_definition(cls) -> InverterDefinition:
        return InverterDefinition(
            "X3",
            InverterIdentification(7, "X3"),
            {
                "PV1 Current": InverterDataValue((0,), Measurement(Units.A)),
                "PV2 Current": InverterDataValue((1,), Measurement(Units.A)),
                "PV1 Voltage": InverterDataValue((2,), Measurement(Units.V)),
                "PV2 Voltage": InverterDataValue((3,), Measurement(Units.V)),
                "Output Current Phase 1": InverterDataValue((4,), Measurement(Units.A)),
                "Network Voltage Phase 1": InverterDataValue(
                    (5,), Measurement(Units.V)
                ),
                "AC Power": InverterDataValue((6,), Measurement(Units.W)),
                "Inverter Temperature": InverterDataValue((7,), Measurement(Units.C)),
                "Today's Energy": InverterDataValue((8,), Measurement(Units.KWH)),
                "Total Energy": InverterDataValue((9,), Total(Units.KWH)),
                "Exported Power": InverterDataValue((10,), Measurement(Units.W)),
                "PV1 Power": InverterDataValue((11,), Measurement(Units.W)),
                "PV2 Power": InverterDataValue((12,), Measurement(Units.W)),
                "Battery Voltage": InverterDataValue((13,), Measurement(Units.V)),
                "Battery Current": InverterDataValue((14,), Measurement(Units.A)),
                "Battery Power": InverterDataValue((15,), Measurement(Units.W)),
                "Battery Temperature": InverterDataValue((16,), Measurement(Units.C)),
                "Battery Remaining Capacity": InverterDataValue(
                    (21,), Measurement(Units.PERCENT)
                ),
                "Total Feed-in Energy": InverterDataValue((41,), Total(Units.KWH)),
                "Total Consumption": InverterDataValue((42,), Total(Units.KWH)),
                "Power Now Phase 1": InverterDataValue((43,), Measurement(Units.W)),
                "Power Now Phase 2": InverterDataValue((44,), Measurement(Units.W)),
                "Power Now Phase 3": InverterDataValue((45,), Measurement(Units.W)),
                "Output Current Phase 2": InverterDataValue(
                    (46,), Measurement(Units.A)
                ),
                "Output Current Phase 3": InverterDataValue(
                    (47,), Measurement(Units.A)
                ),
                "Network Voltage Phase 2": InverterDataValue(
                    (48,), Measurement(Units.V)
                ),
                "Network Voltage Phase 3": InverterDataValue(
                    (49,), Measurement(Units.V)
                ),
                "Grid Frequency Phase 1": InverterDataValue(
                    (50,), Measurement(Units.HZ)
                ),
                "Grid Frequency Phase 2": InverterDataValue(
                    (51,), Measurement(Units.HZ)
                ),
                "Grid Frequency Phase 3": InverterDataValue(
                    (52,), Measurement(Units.HZ)
                ),
                "EPS Voltage": InverterDataValue((53,), Measurement(Units.V)),
                "EPS Current": InverterDataValue((54,), Measurement(Units.A)),
                "EPS Power": InverterDataValue((55,), Measurement(Units.W)),
                "EPS Frequency": InverterDataValue((56,), Measurement(Units.HZ)),
            },
        )
