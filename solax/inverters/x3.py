import voluptuous as vol
from solax.inverter import InverterPost
from solax.utils import startswith


class X3(InverterPost):
    _schema = vol.Schema({
        vol.Required('type'): vol.All(
            str,
            startswith("X3-")
        ),
        vol.Required('SN'): str,
        vol.Required('ver'): str,
        vol.Required('Data'): vol.Schema(
            vol.All(
                [vol.Coerce(float)],
                vol.Any(
                    vol.Length(min=102, max=103),
                    vol.Length(min=107, max=107)),
                )
            ),
        vol.Required('Information'): vol.Schema(
            vol.All(
                vol.Length(min=9, max=9)
                )
            ),
    }, extra=vol.REMOVE_EXTRA)

    # pylint: disable=duplicate-code
    _sensor_map = {
        'PV1 Current':                (0, 'A'),
        'PV2 Current':                (1, 'A'),
        'PV1 Voltage':                (2, 'V'),
        'PV2 Voltage':                (3, 'V'),

        'Output Current Phase 1':     (4, 'A'),
        'Network Voltage Phase 1':    (5, 'V'),
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

        'Power Now Phase 1':          (43, 'W'),
        'Power Now Phase 2':          (44, 'W'),
        'Power Now Phase 3':          (45, 'W'),
        'Output Current Phase 2':     (46, 'A'),
        'Output Current Phase 3':     (47, 'A'),
        'Network Voltage Phase 2':    (48, 'V'),
        'Network Voltage Phase 3':    (49, 'V'),

        'Grid Frequency Phase 1':     (50, 'Hz'),
        'Grid Frequency Phase 2':     (51, 'Hz'),
        'Grid Frequency Phase 3':     (52, 'Hz'),

        'EPS Voltage':                (53, 'V'),
        'EPS Current':                (54, 'A'),
        'EPS Power':                  (55, 'W'),
        'EPS Frequency':              (56, 'Hz'),
    }
