from typing import Any, Dict, Optional

import voluptuous as vol

from solax.inverter import Inverter
from solax.units import Total, Units
from solax.utils import div10, div100, pack_u16, to_signed, twoway_div10


class X1LiteLV(Inverter):
    # pylint: disable=duplicate-code
    _schema = vol.Schema(
        {
            vol.Required("type"): int,
            vol.Required("sn"): str,
            vol.Required("ver"): str,
            vol.Required("data"): vol.Schema(
                vol.All(
                    [vol.Coerce(float)],
                    vol.Length(min=200, max=300),
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
            "AC Current": (1, Units.A, twoway_div10),
            "AC Power": (2, Units.W, to_signed),
            "AC Frequency": (3, Units.HZ, div100),
            "Grid PF": (4, Units.PERCENT, div10),
            ###################################
            "AC Voltage Out": (97, Units.V, div10),
            # "AC Current Out": (98, Units.A, twoway_div10),
            # "AC Power Out": (99, Units.W, to_signed),
            "AC Frequency Out": (101, Units.HZ, div10),
            # "Inverter Status 1 ?": (15, Units.NONE),  # 2 - Normal Mode, 7 - EPSMode
            # "Inverter Status 2 ?": (16, Units.NONE),  # 4 - Normal Mode, 5 - EPSMode
            ##################################
            "Grid Power": (32, Units.W, twoway_div10),
            # "Grid power 1": (33, Units.W, twoway_div10),
            # "Grid power 2": (34, Units.W, twoway_div10),
            "Hourly Energy": (51, Total(Units.KWH), div100),
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
            "Total PV Power": (14, Units.W),
            "Daily PV Energy": (52, Total(Units.KWH), twoway_div10),
            "Total PV Energy": (53, Total(Units.KWH), twoway_div10),
            ################################
            "Inverter Temperature": (68, Units.C, div10),
            "Inverter Temperature 1": (69, Units.C, div10),
            "Inverter Temperature 2": (70, Units.C, div10),
            "Inverter Temperature 3": (71, Units.C, div10),
            ################################
            "Battery Type": (27, Units.NONE),  # Undefined
            "Battery Voltage": (23, Units.V, div10),
            "Battery Current": (24, Units.A, twoway_div10),
            "Total Battery power": (25, Units.W, twoway_div10),
            ###########################
            "Battery SoC": (75, Units.PERCENT, div10),
            "Battery Temperature 1": (72, Units.C),
            "Battery Temperature 2": (73, Units.C),
            "Battery Temperature 3": (74, Units.C),
            "Battery Temperature 4": (78, Units.C),
            "Battery Temperature": (79, Units.C),
            ####################################
            "Daily Battery Charge": (30, Total(Units.KWH), div10),
            "Total Battery Charge": (
                pack_u16(26, 27),
                Total(Units.KWH),
                twoway_div10,
            ),
            "Daily Battery Discharge": (31, Total(Units.KWH), div10),
            "Total Battery Discharge": (
                pack_u16(28, 29),
                Total(Units.KWH),
                twoway_div10,
            ),
            ################
            "Daily Inverter Output": (21, Total(Units.KWH), div10),
            "Total Inverter Output": (
                pack_u16(17, 18),
                Total(Units.KWH),
                div10,
            ),
            "Daily Inverter EPS Energy": (46, Total(Units.KWH), div10),
            "Total Inverter EPS Energy": (
                pack_u16(47, 48),
                Total(Units.KWH),
                div10,
            ),
            "Daily Imported Energy": (40, Total(Units.KWH), div10),
            "Total Imported Energy": (
                pack_u16(36, 37),
                Total(Units.KWH),
                div10,
            ),
        }

    @classmethod
    def dongle_serial_number_getter(cls, response: Dict[str, Any]) -> Optional[str]:
        info = response.get("information", [])
        return info[2] if len(info) > 2 else None

    @classmethod
    def inverter_serial_number_getter(cls, response: Dict[str, Any]) -> Optional[str]:
        info = response.get("information", [])
        return info[2] if len(info) > 2 else None

    # @classmethod
    # def inverter_versions_getter(
    #     cls, response: Dict[str, Any]
    # ) -> Optional[Dict[str, str]]:
    #     i = response["information"]
    #     return {
    #         "Main DSP": f"{i[4]:03.2f}",
    #         "Slave DSP": f"{i[5]:03.2f}",
    #         "ARM": f"{i[6]:03.2f}-{i[7]:03.2f}",
    #         "Module version": response["ver"],
    #     }
