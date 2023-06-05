from solax.inverter import (
    Inverter,
    InverterDefinition,
    InverterIdentification,
    InverterDataValue,
)
from solax.units import Total, Units, Measurement
from solax.utils import div10, div100, to_signed


class X1Smart(Inverter):
    """
    X1-Smart with Pocket WiFi v2.033.20
    Includes X-Forwarded-For for direct LAN API access
    """

    @classmethod
    def inverter_definition(cls) -> InverterDefinition:
        return InverterDefinition(
            "X1",
            InverterIdentification(8),
            {
                "Network Voltage": InverterDataValue(
                    (0,), Measurement(Units.V), (div10,)
                ),
                "Output Current": InverterDataValue(
                    (1,), Measurement(Units.A), (div10,)
                ),
                "AC Power": InverterDataValue((2,), Measurement(Units.W)),
                "PV1 Voltage": InverterDataValue((3,), Measurement(Units.V), (div10,)),
                "PV2 Voltage": InverterDataValue((4,), Measurement(Units.V), (div10,)),
                "PV1 Current": InverterDataValue((5,), Measurement(Units.A), (div10,)),
                "PV2 Current": InverterDataValue((6,), Measurement(Units.A), (div10,)),
                "PV1 Power": InverterDataValue((7,), Measurement(Units.W)),
                "PV2 Power": InverterDataValue((8,), Measurement(Units.W)),
                "Grid Frequency": InverterDataValue(
                    (9,), Measurement(Units.HZ), (div100,)
                ),
                "Total Energy": InverterDataValue((11,), Total(Units.KWH), (div10,)),
                "Today's Energy": InverterDataValue(
                    (13,), Measurement(Units.KWH), (div10,)
                ),
                "Inverter Temperature": InverterDataValue((39,), Measurement(Units.C)),
                "Exported Power": InverterDataValue(
                    (48,), Measurement(Units.W), (to_signed,)
                ),
                "Total Feed-in Energy": InverterDataValue(
                    (50,), Total(Units.KWH), (div100,)
                ),
                "Total Consumption": InverterDataValue(
                    (52,), Total(Units.KWH), (div100,)
                ),
            },
        )
