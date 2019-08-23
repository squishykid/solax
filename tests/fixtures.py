import pytest

XHYBRID_RESPONSE = {
    'method': 'uploadsn',
    'version': 'Solax_SI_CH_2nd_20160912_DE02',
    'type': 'AL_SE',
    'SN': 'XXXXXXX',
    'Data': [0.5, 0.4, 202.0, 194.3, 2.0, 234.0, 444, 40, 17.0, 238.2,
             -15, 101, 77, 56.01, -6.36, -357, 27, 92, 0.0, 126.0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 373.90, 38.60, 0, 0, 0, 0, 0, 0, 0,
             50.02, 0, 0, 0.0, 0, 0, 0, 0, 0, 0,
             0.0, 0, 8, 0, 0, 0.00, 0, 8],
    'Status': 2
}


XHYBRID_VALUES = {
    'Today\'s Energy': 17.0,
    'Battery Current': -6.36,
    'Month\'s Energy': 126.0,
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
    'Total Energy': 238.2
}


X3_MIC_RESPONSE = {
    "type": "X3-MIC",
    "SN": "X3X3ZZYYXX",
    "ver": "2.033.20",
    "Data": [8.0, 8.7, 457.8, 454.8, 10.6, 236.9, 7299, 30, 0.0, 10.9,
             0, 3620, 3928, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0.00, 0.00, 2488, 2392, 2419, 10.4, 10.6, 232.4, 231.0,
             50.03, 50.03, 50.02, 0, 0, 0, 0, 0, 0, 0,
             0.00, 0, 8, 0, 0, 0.00, 0, 8, 2, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0],
    "Information": [8.000, 7, "X3-MIC", "MC802TF3194008",
                    1, 1.10, 1.02, 1.09, 1.02]
}


@pytest.fixture()
def x_hybrid_fixture(httpserver):
    httpserver.expect_request(
        uri="/api/realTimeData.htm",
        method='GET'
    ).respond_with_json(XHYBRID_RESPONSE)
    yield (httpserver.host, httpserver.port)


@pytest.fixture()
def x_hybrid_garbage_fixture(httpserver):
    httpserver.expect_request(
        uri="/api/realTimeData.htm",
        method='GET'
    ).respond_with_json({'hello': 'world'})
    yield (httpserver.host, httpserver.port)


@pytest.fixture()
def x3_fixture(httpserver):
    httpserver.expect_request(
        uri="/",
        method='POST',
        query_string='optType=ReadRealTimeData'
    ).respond_with_json(X3_MIC_RESPONSE)
    yield (httpserver.host, httpserver.port)


@pytest.fixture()
def simple_http_fixture(httpserver):
    httpserver.expect_request(
        uri="/",
        method='GET',
        query_string='index.html'
    ).respond_with_json({'hello': 'world'})
    yield (httpserver.host, httpserver.port)
