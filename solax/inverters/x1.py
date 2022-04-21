import voluptuous as vol
from solax.inverter import InverterPost
from solax.utils import startswith


class X1(InverterPost):
    # pylint: disable=duplicate-code
    _schema = vol.Schema({
        vol.Required('type'): vol.All(
            str,
            startswith("X1-")
        ),
        vol.Required('SN'): str,
        vol.Required('ver'): str,
        vol.Required('Data'): vol.Schema(
            vol.All(
                [vol.Coerce(float)],
                vol.Any(
                    vol.Length(min=102, max=102),
                    vol.Length(min=103, max=103),
                    vol.Length(min=107, max=107),
                ),
            )
        ),
        vol.Required('Information'): vol.Schema(
            vol.All(
                vol.Length(min=9, max=9)
                )
            ),
    }, extra=vol.REMOVE_EXTRA)

    _sensor_map = {
        'PV1 Current':                (0, 'A'),
        'PV2 Current':                (1, 'A'),
        'PV1 Voltage':                (2, 'V'),
        'PV2 Voltage':                (3, 'V'),

        'Output Current':             (4, 'A'),
        'Network Voltage':            (5, 'V'),
        'AC Power':                   (6, 'W'),

        'Inverter Temperature':       (7, 'C'),
        'Today\'s Energy':            (8, 'kWh'),
        'Total Energy':               (9, 'kWh'),
        'Exported Power':             (10, 'W'),
        'PV1 Power':                  (11, 'W'),
        'PV2 Power':                  (12, 'W'),

        'Battery Voltage':            (13, 'V'),
        'Battery Current':            (14, 'A'),
        'Battery Power':              (15, 'W'),
        'Battery Temperature':        (16, 'C'),
        'Battery Remaining Capacity': (21, '%'),

        'Total Feed-in Energy':       (41, 'kWh'),
        'Total Consumption':          (42, 'kWh'),

        'Power Now':                  (43, 'W'),
        'Grid Frequency':             (50, 'Hz'),

        'EPS Voltage':                (53, 'V'),
        'EPS Current':                (54, 'A'),
        'EPS Power':                  (55, 'W'),
        'EPS Frequency':              (56, 'Hz'),
    }
    # pylint: enable=duplicate-code
