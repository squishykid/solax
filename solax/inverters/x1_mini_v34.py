import voluptuous as vol

from solax.inverter import InverterPost
from solax.utils import div10, div100


class X1MiniV34(InverterPost):
    # pylint: disable=duplicate-code
    _schema = vol.Schema({
        vol.Required('type', 'type'): vol.All(int, 4),
        vol.Required('sn',): str,
        vol.Required('ver'): str,
        vol.Required('Data'): vol.Schema(
            vol.All(
                [vol.Coerce(float)],
                vol.Any(
                    vol.Length(min=69, max=69),
                    vol.Length(min=200, max=200),
                )
            )
        ),
        vol.Required('Information'): vol.Schema(
            vol.Any(
                vol.Length(min=9, max=9),
                vol.Length(min=10, max=10)
            )
        ),
    }, extra=vol.REMOVE_EXTRA)

    _sensor_map = {
        'Network Voltage':            (0, 'V', div10),
        'Output Current':             (1, 'A', div10),
        'AC Power':                   (2, 'W'),
        'PV1 Voltage':                (3, 'V', div10),
        'PV2 Voltage':                (4, 'V', div10),
        'PV1 Current':                (5, 'A', div10),
        'PV2 Current':                (6, 'A', div10),
        'PV1 Power':                  (7, 'W'),
        'PV2 Power':                  (8, 'W'),
        'Grid Frequency':             (9, 'Hz', div100),
        'Total Energy':               (11, 'kWh', div10),
        'Today\'s Energy':            (13, 'kWh', div10),
        'Total Feed-in Energy':       (41, 'kWh', div10),
        'Total Consumption':          (42, 'kWh', div10),
        'Power Now':                  (43, 'W', div10),
    }
    # pylint: enable=duplicate-code
