import pytest
from solax import inverter
from collections import namedtuple

XHYBRID_RESPONSE = {
    'method': 'uploadsn',
    'version': 'Solax_SI_CH_2nd_20160912_DE02',
    'type': 'AL_SE',
    'SN': 'XXXXXXX',
    'Data': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
             10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
             30, 31, 32, 33, 34, 35, 36, 37, 38, 39,
             40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
             50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
             60, 61, 62, 63, 64, 65, 66, 67],
    'Status': 2
}


XHYBRID_VALUES = {
    'Today\'s Energy': 8.0,
    'Battery Current': 14.0,
    'Month\'s Energy': 19.0,
    'Battery Power': 15,
    'Battery Remaining Capacity': 17,
    'Battery Temperature': 16,
    'Battery Voltage': 13,
    'EPS Current': 54,
    'EPS Frequency': 56,
    'EPS Power': 55,
    'EPS Voltage': 53,
    'Exported Power': 10,
    'Grid Frequency': 50,
    'Inverter Temperature': 7,
    'Network Voltage': 5,
    'Output Current': 4,
    'PV1 Current': 0,
    'PV1 Power': 11,
    'PV1 Voltage': 2,
    'PV2 Current': 1,
    'PV2 Power': 12,
    'PV2 Voltage': 3,
    'Power Now': 6,
    'Total Energy': 9
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
def simple_http_fixture(httpserver):
    httpserver.expect_request(
        uri="/",
        method='GET',
        query_string='index.html'
    ).respond_with_json({'hello': 'world'})
    yield (httpserver.host, httpserver.port)


InverterUnderTest = namedtuple('InverterUnderTest',
                               'uri, method, query_string, response, inverter, values')

INVERTERS_UNDER_TEST = [
    InverterUnderTest(
        uri='/api/realTimeData.htm',
        method='GET',
        query_string=None,
        response=XHYBRID_RESPONSE,
        inverter=inverter.XHybrid,
        values=XHYBRID_VALUES,
    ),
]


@pytest.fixture(params=INVERTERS_UNDER_TEST)
def inverters_fixture(httpserver, request):
    httpserver.expect_request(
        uri=request.param.uri,
        method=request.param.method,
        query_string=request.param.query_string
    ).respond_with_json(request.param.response)
    yield (
        (httpserver.host, httpserver.port),
        request.param.inverter,
        request.param.values
    )
