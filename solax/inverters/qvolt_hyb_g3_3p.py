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


class QVOLTHYBG33P(InverterPost):
    """
    QCells
    Q.VOLT HYB-G3-3P
    """

    class Processors:
        """
        Postprocessors used only in the QVOLTHYBG33P inverter sensor_map.
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
            vol.Required("type"): vol.All(int, 14),
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
            "Network Voltage Phase 1": (0, Units.V, div10),
            "Network Voltage Phase 2": (1, Units.V, div10),
            "Network Voltage Phase 3": (2, Units.V, div10),
            "Output Current Phase 1": (3, Units.A, twoway_div10),
            "Output Current Phase 2": (4, Units.A, twoway_div10),
            "Output Current Phase 3": (5, Units.A, twoway_div10),
            "Power Now Phase 1": (6, Units.W, to_signed),
            "Power Now Phase 2": (7, Units.W, to_signed),
            "Power Now Phase 3": (8, Units.W, to_signed),
            "AC Power": (9, Units.W, to_signed),
            "PV1 Voltage": (10, Units.V, div10),
            "PV2 Voltage": (11, Units.V, div10),
            "PV1 Current": (12, Units.A, div10),
            "PV2 Current": (13, Units.A, div10),
            "PV1 Power": (14, Units.W),
            "PV2 Power": (15, Units.W),
            "Grid Frequency Phase 1": (16, Units.HZ, div100),
            "Grid Frequency Phase 2": (17, Units.HZ, div100),
            "Grid Frequency Phase 3": (18, Units.HZ, div100),
            "Inverter Operation mode": (19, Units.NONE, cls.Processors.inverter_modes),
            # 20 - 32: always 0
            # 33: always 1
            # instead of to_signed this is actually 34 - 35,
            # because 35 =  if 34>32767: 0 else: 65535
            "Exported Power": (34, Units.W, to_signed),
            # 35: if 34>32767: 0 else: 65535
            # 36 - 38    : always  0
            "Battery Voltage": (39, Units.V, div100),
            "Battery Current": (40, Units.A, twoway_div100),
            "Battery Power": (41, Units.W, to_signed),
            # 42: div10, almost identical to [39]
            # 43: twoway_div10,  almost the same as "40" (battery current)
            # 44: twoway_div100, almost the same as "41" (battery power),
            # 45: always 1
            # 46: follows PV Output, idles around 44, peaks at 52,
            "Power Now": (47, Units.W, to_signed),
            # 48: always 256
            # 49,50: [49] + [50] * 15160 some increasing counter
            # 51: always 5634
            # 52: always 100
            # 53: always 0
            # 54: follows PV Output, idles around 35, peaks at 54,
            # 55-67: always 0
            "Total Energy": (pack_u16(68, 69), Total(Units.KWH), div10),
            # 70: div10, today's energy including battery usage
            # 71-73: 0
            "Total Battery Discharge Energy": (
                pack_u16(74, 75),
                Total(Units.KWH),
                div10,
            ),
            "Total Battery Charge Energy": (
                pack_u16(76, 77),
                Total(Units.KWH),
                div10,
            ),
            "Today's Battery Discharge Energy": (78, Units.KWH, div10),
            "Today's Battery Charge Energy": (79, Units.KWH, div10),
            "Total PV Energy": (pack_u16(80, 81), Total(Units.KWH), div10),
            "Today's Energy": (82, Units.KWH, div10),
            # 83-85: always 0
            "Total Feed-in Energy": (pack_u16(86, 87), Total(Units.KWH), div100),
            "Total Consumption": (pack_u16(88, 89), Total(Units.KWH), div100),
            "Today's Feed-in Energy": (90, Units.KWH, div100),
            # 91: always 0
            "Today's Consumption": (92, Units.KWH, div100),
            # 93-101: always 0
            # 102: always 1
            "Battery Remaining Capacity": (103, Units.PERCENT),
            # 104: always 1
            "Battery Temperature": (105, Units.C),
            "Battery Remaining Energy": (106, Units.KWH, div10),
            # 107: always 256 or 0
            # 108: always 3504
            # 109: always 2400
            # 110: around rise to 300 if battery not full, 0 if battery is full
            # 112, 113: range [250,350]; looks like 113 + offset = 112,
            #   peaks if battery is full
            # 114, 115: something around 33; Some temperature?!
            # 116: increases slowly [2,5]
            # 117-121: 1620	773	12850	12850	12850
            # 122-124: always 0
            # 125,126: some curve, look very similar to "42"(Battery Power),
            # with offset around 15
            # 127,128 resetting counter /1000, around battery charge + discharge
            # 164,165,166 some curves
            "Battery Operation mode": (168, Units.NONE, cls.Processors.battery_modes),
            # 169: div100 same as [39]
            # 170-199: always 0
        }

    @classmethod
    async def make_request(cls, host, port=80, pwd="", headers=None):

        url = f"http://{host}:{port}/"
        data = f"optType=ReadRealTimeData&pwd={pwd}"

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data) as req:
                resp = await req.read()

        return cls.handle_response(resp)
