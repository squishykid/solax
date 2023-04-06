from solax.inverter import (
    Inverter,
    InverterDataValue,
    InverterDefinition,
    InverterIdentification,
)
from solax.units import Measurement, Total, Units
from solax.utils import div10, div100


class X1MiniV34(Inverter):
    @classmethod
    def inverter_definition(cls) -> InverterDefinition:
        return InverterDefinition(
            "X1",
            InverterIdentification(4),
            {
                "Network Voltage": InverterDataValue((0,), Measurement(Units.V), (div10,)),
                "Output Current": InverterDataValue((1,), Measurement(Units.A), (div10,)),
                "AC Power": InverterDataValue((2,), Measurement(Units.W)),
                "PV1 Voltage": InverterDataValue((3,), Measurement(Units.V), (div10,)),
                "PV2 Voltage": InverterDataValue((4,), Measurement(Units.V), (div10,)),
                "PV1 Current": InverterDataValue((5,), Measurement(Units.A), (div10,)),
                "PV2 Current": InverterDataValue((6,), Measurement(Units.A), (div10,)),
                "PV1 Power": InverterDataValue((7,), Measurement(Units.W)),
                "PV2 Power": InverterDataValue((8,), Measurement(Units.W)),
                "Grid Frequency": InverterDataValue((9,), Measurement(Units.HZ), (div100,)),
                "Total Energy": InverterDataValue((11,), Total(Units.KWH), (div10,)),
                "Today's Energy": InverterDataValue((13,), Measurement(Units.KWH), (div10,)),
                "Total Feed-in Energy": InverterDataValue((41,), Total(Units.KWH), (div10,)),
                "Total Consumption": InverterDataValue((42,), Total(Units.KWH), (div10,)),
                "Power Now": InverterDataValue((43,), Measurement(Units.W), (div10,)),
                "Inverter Temperature": InverterDataValue((55,), Measurement(Units.C)),
            },
        )
