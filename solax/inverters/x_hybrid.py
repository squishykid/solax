from solax.inverter import (
    Inverter,
    InverterDataValue,
    InverterDefinition,
    InverterIdentification,
)
from solax.units import Measurement, Total, Units


class XHybrid(Inverter):
    # key: name of sensor
    # value.0: index
    # value.1: unit (String) or None
    # from https://github.com/GitHobi/solax/wiki/direct-data-retrieval
    @classmethod
    def inverter_definition(cls) -> InverterDefinition:
        return InverterDefinition(
            "XHybrid",
            InverterIdentification(-1, "AL_SE"),
            {
                "PV1 Current": InverterDataValue((0,), Measurement(Units.A)),
                "PV2 Current": InverterDataValue((1,), Measurement(Units.A)),
                "PV1 Voltage": InverterDataValue((2,), Measurement(Units.V)),
                "PV2 Voltage": InverterDataValue((3,), Measurement(Units.V)),
                "Output Current": InverterDataValue((4,), Measurement(Units.A)),
                "Network Voltage": InverterDataValue((5,), Measurement(Units.V)),
                "Power Now": InverterDataValue((6,), Measurement(Units.W)),
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
                    (17,), Measurement(Units.PERCENT)
                ),
                "Month's Energy": InverterDataValue((19,), Measurement(Units.KWH)),
                "Grid Frequency": InverterDataValue((50,), Measurement(Units.HZ)),
                "EPS Voltage": InverterDataValue((53,), Measurement(Units.V)),
                "EPS Current": InverterDataValue((54,), Measurement(Units.A)),
                "EPS Power": InverterDataValue((55,), Measurement(Units.W)),
                "EPS Frequency": InverterDataValue((56,), Measurement(Units.HZ)),
            },
        )
