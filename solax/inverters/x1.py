import voluptuous as vol

from solax.inverter import Inverter, InverterDefinition, InverterIdentification, InverterDataValue
from solax.units import Total, Units, Measurement
from solax.utils import startswith


class X1(Inverter):
    # pylint: disable=duplicate-code
    _schema = vol.Schema(
        {
            vol.Required("type"): vol.All(str, startswith("X1-")),
            vol.Required("SN"): str,
            vol.Required("ver"): str,
            vol.Required("Data"): vol.Schema(
                vol.All(
                    [vol.Coerce(float)],
                    vol.Any(
                        vol.Length(min=102, max=102),
                        vol.Length(min=103, max=103),
                        vol.Length(min=107, max=107),
                    ),
                )
            ),
            vol.Required("Information"): vol.Schema(vol.All(vol.Length(min=9, max=9))),
        },
        extra=vol.REMOVE_EXTRA,
    )

    @classmethod
    def inverter_definition(cls) -> InverterDefinition:
        return InverterDefinition(
            "X1",
            InverterIdentification(3, "X1-"),
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
                "Battery Voltage": InverterDataValue((13,), Measurement(Units.V)),
                "Battery Current": InverterDataValue((14,), Measurement(Units.A)),
                "Battery Power": InverterDataValue((15,), Measurement(Units.W)),
                "Battery Temperature": InverterDataValue((16,), Measurement(Units.C)),
                "Battery Remaining Capacity": InverterDataValue((21,), Measurement(Units.PERCENT)),
                "Total Feed-in Energy": InverterDataValue((41,), Total(Units.KWH)),
                "Total Consumption": InverterDataValue((42,), Total(Units.KWH)),
                "Power Now": InverterDataValue((43,), Measurement(Units.W)),
                "Grid Frequency": InverterDataValue((50,), Measurement(Units.HZ)),
                "EPS Voltage": InverterDataValue((53,), Measurement(Units.V)),
                "EPS Current": InverterDataValue((54,), Measurement(Units.A)),
                "EPS Power": InverterDataValue((55,), Measurement(Units.W)),
                "EPS Frequency": InverterDataValue((56,), Measurement(Units.HZ)),
            })

    # pylint: enable=duplicate-code
