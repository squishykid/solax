import solax


def test_parse_response():
    resp = {'method': 'uploadsn',
            'version': 'Solax_SI_CH_2nd_20160912_DE02',
            'type': 'AL_SE',
            'SN': 'XXXXXXX',
            'Data': [0.5, 0.4, 202.0, 194.3, 2.0, 234.0, 444, 40, 17.0, 238.2,
                     -15, 101, 77, 56.01, -6.36, -357, 27, 92, 0.0, 126.0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     0, 373.90, 38.60, 0, 0, 0, 0, 0, 0, 0, 50.02, 0, 0, 0.0,
                     0, 0, 0, 0, 0, 0, 0.0, 0, 8, 0, 0, 0.00, 0, 8],
            'Status': 2}
    parsed = solax.parse_solax_real_time_response(resp)

    expected = {'Today\'s Energy': 17.0,
                'Battery Current': -6.36,
                'Battery Energy': 126.0,
                'Battery Power': -357,
                'Battery Remaining Capacity': 92,
                'Battery Temperature': 27,
                'Battery Voltage': 56.01,
                'EPS Current': 0,
                'EPS Frequency': 0,
                'EPS Power': 0,
                'EPS Voltage': 0.0,
                'Exported Power': -15,
                'Grid Frequency': 50.02,
                'Inverter Temperature': 40,
                'Network Voltage': 234.0,
                'Output Current': 2.0,
                'PV1 Current': 0.5,
                'PV1 Power': 101,
                'PV1 Voltage': 202.0,
                'PV2 Current': 0.4,
                'PV2 Power': 77,
                'PV2 Voltage': 194.3,
                'Power Now': 444,
                'Total Energy': 238.2}

    for sensor, value in expected.items():
        assert parsed.data[sensor] == value
    assert parsed.serial_number == 'XXXXXXX'
    assert parsed.version == 'Solax_SI_CH_2nd_20160912_DE02'
    assert parsed.type == 'AL_SE'
    assert parsed.status == 2
