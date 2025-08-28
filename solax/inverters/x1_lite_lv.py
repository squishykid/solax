from typing import Any, Dict, Optional

import voluptuous as vol

from solax.inverter import Inverter
from solax.units import DailyTotal, Total, Units
from solax.utils import div10, div100, pack_u16, to_signed, to_signed32, twoway_div10


class X1LiteLV(Inverter):
    # pylint: disable=duplicate-code
    _schema = vol.Schema(
        {
            vol.Required("type"): int,
            vol.Required(
                "sn",
            ): str,
            vol.Required("ver"): str,
            vol.Required("data"): vol.Schema(
                vol.All(
                    [vol.Coerce(float)],
                    vol.Length(min=200, max=200),
                )
            ),
            vol.Required("information"): vol.Schema(vol.All(vol.Length(min=1, max=15))),
        },
        extra=vol.REMOVE_EXTRA,
    )

    @classmethod
    def build_all_variants(cls, host, port, pwd=""):
        versions = [cls._build(host, port, pwd), cls._build(host, port, pwd, False)]
        return versions

    @classmethod
    def response_decoder(cls):
        """
        :return:
        """
        return {
            "AC Voltage": (0, Units.V, div10),
            "AC Output Current": (1, Units.A, twoway_div10),
            "AC Output Power": (2, Units.W, to_signed),
            "AC Frequency": (3, Units.HZ, div100),
            "Grid PF": (4, Units.PERCENT, div10),
            ###################################
            "AC Voltage Out": (97, Units.V, div10),
            # "AC current Out": (98, Units.A, twoway_div10),
            # "AC power Out": (99, Units.W, to_signed),
            "AC Frequency Out": (101, Units.HZ, div10),
            # "Inverter Status 1 ?": (15, Units.NONE),  # 2 - Normal Mode, 7 - EPSMode
            # "Inverter Status 2 ?": (16, Units.NONE),  # 4 - Normal Mode, 5 - EPSMode
            ##################################
            "Grid Power": (32, Units.W, twoway_div10),
            # "Grid power 1": (33, Units.W, twoway_div10),
            # "Grid power 2": (34, Units.W, twoway_div10),
            "Hourly Energy": (51, DailyTotal(Units.KWH), div100),
            ###############################
            "PV1 Voltage": (5, Units.V, div10),
            "PV2 Voltage": (7, Units.V, div10),
            "PV3 Voltage": (9, Units.V, div10),
            "PV1 Current": (6, Units.A, div10),
            "PV2 Current": (8, Units.A, div10),
            "PV3 Current": (10, Units.A, div10),
            "PV1 Power": (11, Units.W),
            "PV2 Power": (12, Units.W),
            "PV3 Power": (13, Units.W),
            "Total PV Power": (14, Total(Units.KWH), to_signed),
            "Today's PV Energy": (52, DailyTotal(Units.KWH), twoway_div10),
            "Total PV Energy": (53, Total(Units.KWH), twoway_div10),
            ################################
            "Battery Type": (27, Units.NONE),  # Undefined
            "Battery voltage": (23, Units.V, div10),
            "Battery current": (24, Units.A, twoway_div10),
            "Total Battery power": (25, Units.W, twoway_div10),
            ###########################
            "Battery SoC": (75, Units.PERCENT, div10),
            "Battery Temperature 1": (72, Units.C),
            "Battery Temperature 2": (73, Units.C),
            "Battery Temperature 3": (74, Units.C),
            "Battery Temperature 4": (78, Units.C),
            "Battery Temperature": (79, Units.C),
            "Battery Charge total": (pack_u16(26, 27), Units.KWH, div10),
            "Battery Discharge total": (pack_u16(28, 29), Units.KWH, div10),
            "Battery Charge today": (30, Units.KWH, div10),
            "Battery Discharge today": (31, Units.KWH, div10),
            "Charging Duration": (pack_u16(80, 81), Units.NONE, to_signed32),
            "Today's Battery Discharge": (30, DailyTotal(Units.KWH), div10),
            "Total Battery Discharge": (
                pack_u16(28, 29),
                Total(Units.KWH),
                twoway_div10,
            ),
            "Today's Battery Charge": (31, DailyTotal(Units.KWH), div10),
            "Total Battery Charge": (pack_u16(26, 27), Total(Units.KWH), twoway_div10),
            ################
            "Today's Generated Energy": (21, DailyTotal(Units.KWH), div10),
            "Total Generated Energy": (pack_u16(17, 18), Total(Units.KWH), div10),
            "Today's EPS Energy": (46, DailyTotal(Units.KWH), div10),
            "Total EPS Energy": (pack_u16(47, 48), Total(Units.KWH), div10),
            "Today's Import Energy": (40, DailyTotal(Units.KWH), div10),
            "Total Import Energy": (pack_u16(36, 37), Total(Units.KWH), div10),
        }

    @classmethod
    def inverter_serial_number_getter(cls, response: Dict[str, Any]) -> Optional[str]:
        return response["information"][2]
