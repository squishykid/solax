import voluptuous as vol
import aiohttp
from solax.inverter import InverterPost
from solax.units import Total, Units
from solax.utils import (
    div10,
    div100,
    pack_u16,
    twoway_div10,
    to_signed,
    twoway_div100,
)


class QVOLTHYBG31P(InverterPost):
    """
    QCells
    Q.VOLT HYB-G3-1P
    """

    class Processors:
        """
        Postprocessors used only in the QVOLTHYBG31P inverter sensor_map.
        """

        @staticmethod
        def inverter_modes(value):
            return {
                0: "Waiting",
                1: "Checking",
                2: "Normal",
                3: "Off",
                4: "Permanent Fault",
                5: "Updating",
                6: "EPS Check",
                7: "EPS Mode",
                8: "Self Test",
                9: "Idle",
                10: "Standby",
            }.get(value, f"unmapped value '{value}'")

        @staticmethod
        def battery_modes(value):
            return {
                0: "Self Use Mode",
                1: "Force Time Use",
                2: "Back Up Mode",
                3: "Feed-in Priority",
            }.get(value, f"unmapped value '{value}'")

    def __init__(self, host, port, pwd=""):
        super().__init__(host, port, pwd)
        self.manufacturer = "Qcells"

    _schema = vol.Schema(
        {
            vol.Required("type"): vol.All(int, 15),
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
            "Network Voltage": (0, Units.V, div10),
            "Inverter output current": (1, Units.A, twoway_div10),
            "Inverter output power": (2, Units.W, to_signed),
            "Grid Frequency": (3, Units.HZ, div100),
            "PV1 Voltage": (4, Units.V, div10),
            "PV2 Voltage": (5, Units.V, div10),
            "PV1 Current": (6, Units.A, div10),
            "PV2 Current": (7, Units.A, div10),
            "PV1 Power": (8, Units.W),
            "PV2 Power": (9, Units.W),
            "Inverter Operation mode": (10, Units.NONE, cls.Processors.inverter_modes),
            "Total inverter yield": (pack_u16(11, 12), Total(Units.KWH), div10),
            "Today's inverter output yield": (13, Units.KWH, div10),
            "Battery Voltage": (14, Units.V, div100),
            "Battery Current": (15, Units.A, twoway_div100),
            "Battery Power": (16, Units.W, to_signed),
            "Battery Temperature": (17, Units.C),
            "Battery Remaining Capacity": (18, Units.PERCENT),
            # 19: seemingly monotonic, slowly growing
            # 20: always 0
            # 21: always 4313
            # 22: always 0
            "Battery Remaining Energy": (23, Units.KWH, div10),
            # 24: always 100
            # 25: always 0
            # 26-27: jumping around
            # 28-31: always 0
            # 32-33: realtime feed-in/grid power?
            "Total output to grid": (pack_u16(34, 35), Total(Units.KWH), div100),
            "Total input from grid": (pack_u16(36, 37), Total(Units.KWH), div100),
            "Current power usage": (38, Units.W, to_signed),
            # 39-115: mix of steady values, 0s, FFFFs and changing mysteries
            "Total battery energy throughput": (pack_u16(116, 117), Total(Units.WH)),
            # 118-124: BMS serial number, ASCII, little-endian, 2 chars per register
            # 125-131: Battery 1 serial number, ASCII, little-endian, 2 chars per register
            # 132-138: Battery 2 serial number, ASCII, little-endian, 2 chars per register
            # 139-145: Battery 3 serial number, ASCII, little-endian, 2 chars per register
            # 146-152: Battery 4 serial number, ASCII, little-endian, 2 chars per register
            # 153-156: ???
            "Battery Operation mode": (157, Units.NONE, cls.Processors.battery_modes),
            # 158 - 199: always 0
        }

    @classmethod
    async def make_request(cls, host, port=80, pwd="", headers=None):

        url = f"http://{host}:{port}/"
        data = f"optType=ReadRealTimeData&pwd={pwd}"

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data) as req:
                resp = await req.read()

        return cls.handle_response(resp)
