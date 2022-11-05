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
    to_signed32,
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
            "Inverter status": (10, Units.NONE, cls.Processors.inverter_modes),
            "Total inverter yield": (pack_u16(11, 12), Total(Units.KWH), div10),
            "Today's inverter yield": (13, Units.KWH, div10),
            "Battery Voltage": (14, Units.V, div100),
            "Battery Current": (15, Units.A, twoway_div100),
            "Battery Power": (16, Units.W, to_signed),
            "Battery Temperature": (17, Units.C),
            "Battery Remaining Capacity": (18, Units.PERCENT),
            "Total battery discharged energy": (pack_u16(19, 20), Total(Units.KWH), div10),
            "Total battery charged energy": (pack_u16(21, 22), Total(Units.KWH), div10),
            "Battery Remaining Energy": (23, Units.KWH, div10),
            # 24: always 100. probably 10.0%, minimum charge left before switching to grid
            # 25: always 0
            # 26-27: jumping around
            # 28-31: always 0
            "Current grid power": (pack_u16(32, 33), Units.W, to_signed32),
            "Total grid export": (pack_u16(34, 35), Total(Units.KWH), div100),
            "Total grid import": (pack_u16(36, 37), Total(Units.KWH), div100),
            "Current power usage": (38, Units.W, to_signed),
            # 39: observed range 0-38. something about the inverter
            # 40: 256 when inverter is running, 0 when it's idle
            # 41-42: fixed values
            # 43-49: no idea, varying values
            # 50-51: always 1. possibly an inverter setting
            # 52: idk, max 4, min 0
            # 53: always 0
            "Total self-used solar": (pack_u16(54, 55), Total(Units.KWH), div10),
            # 56-57: 32 bit pack? mostly negative, went positive briefly
            # 58-59: 32 bit pack? always negative, between -144 and -175
            # 60-69: always 0
            # 70: fluctuates quite wildly
            # 72-73: 32 bit pack?
            # 74-77: fixed values
            "Today's grid export": (pack_u16(78, 79), Units.KWH, div100),
            "Today's grid import": (pack_u16(80, 81), Units.KWH, div100),
            # 82-84: always 0
            "Today's solar yield": (85, Units.KWH, div10),
            # 86: something daily
            # 87: something else daily
            # 88-89: always 0
            # 90: min 350, max 360
            # 91: always 0
            # 92: always 230
            # 93-95: something daily
            # 97-98: always 0
            # 99-100: weird counter. rtc?
            # 101-109: fixed values
            # 110: battery type!?
            # 111-115: mysterious stuff
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
