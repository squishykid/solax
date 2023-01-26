from solax.inverter import Inverter, InverterDefinition, InverterIdentification, InverterDataValue
from solax.units import Total, Units, Measurement


class X1Mini(Inverter):
    @classmethod
    def inverter_definition(cls) -> InverterDefinition:
        return InverterDefinition(
            "X1",
            InverterIdentification(4, "X1-"),
            {
                "PV1 Current": InverterDataValue((0,), Measurement(Units.A)),
                "PV2 Current": InverterDataValue((1,), Measurement(Units.A)),
                "PV1 Voltage": InverterDataValue((2,), Measurement(Units.V)),
                "PV2 Voltage": InverterDataValue((3,), Measurement(Units.V)),
                "Output Current": InverterDataValue((4,), Measurement(Units.A)),
                "Network Voltage": InverterDataValue((5,), Measurement(Units.V)),
                "AC Power": InverterDataValue((6,), Measurement(Units.W)),
                "Inverter Temperature": InverterDataValue((7,), Measurement(Units.C)),
                "Today's Energy": InverterDataValue((8,), Measurement(Units.KWH)),
                "Total Energy": InverterDataValue((9,), Total(Units.KWH)),
                "Exported Power": InverterDataValue((10,), Measurement(Units.W)),
                "PV1 Power": InverterDataValue((11,), Measurement(Units.W)),
                "PV2 Power": InverterDataValue((12,), Measurement(Units.W)),
                "Total Feed-in Energy": InverterDataValue((41,), Total(Units.KWH)),
                "Total Consumption": InverterDataValue((42,), Total(Units.KWH)),
                "Power Now": InverterDataValue((43,), Measurement(Units.W)),
                "Grid Frequency": InverterDataValue((50,), Measurement(Units.HZ)),
            })