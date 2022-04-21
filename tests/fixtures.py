from collections import namedtuple
import pytest
import solax.inverters as inverter
from tests.samples.expected_values import (
    QVOLTHYBG33P_VALUES, X1_MINI_VALUES, X1_MINI_VALUES_V34,
    X1_SMART_VALUES, X1_VALUES, X3_HYBRID_VALUES, X3_VALUES,
    X3V34_HYBRID_VALUES, X3V34_HYBRID_VALUES_EPS_MODE,
    X3V34_HYBRID_VALUES_NEGATIVE_POWER, XHYBRID_VALUES,
)
from tests.samples.responses import (
    QVOLTHYBG33P_RESPONSE_V34, X1_BOOST_AIR_MINI_RESPONSE,
    X1_HYBRID_G3_2X_MPPT_RESPONSE, X1_HYBRID_G3_RESPONSE,
    X1_MINI_RESPONSE_V34, X1_SMART_RESPONSE,
    X3_HYBRID_G3_2X_MPPT_RESPONSE,  X3_HYBRID_G3_2X_MPPT_RESPONSE_V34,
    X3_HYBRID_G3_2X_MPPT_RESPONSE_V34_EPS_MODE,
    X3_HYBRID_G3_2X_MPPT_RESPONSE_V34_NEGATIVE_POWER,
    X3_HYBRID_G3_RESPONSE, X3_MIC_RESPONSE,
    XHYBRID_DE01_RESPONSE, XHYBRID_DE02_RESPONSE,
)

X_FORWARDED_HEADER = {"X-Forwarded-For": "5.8.8.8"}


@pytest.fixture()
def simple_http_fixture(httpserver):
    httpserver.expect_request(
        uri="/",
        method='GET',
        query_string='index.html'
    ).respond_with_json({'hello': 'world'})
    yield (httpserver.host, httpserver.port)


InverterUnderTest = namedtuple(
    'InverterUnderTest',
    'uri, method, query_string, response, inverter, values, headers'
)

INVERTERS_UNDER_TEST = [
    InverterUnderTest(
        uri='/api/realTimeData.htm',
        method='GET',
        query_string=None,
        response=XHYBRID_DE01_RESPONSE,
        inverter=inverter.XHybrid,
        values=XHYBRID_VALUES,
        headers=None,
    ),
    InverterUnderTest(
        uri='/api/realTimeData.htm',
        method='GET',
        query_string=None,
        response=XHYBRID_DE02_RESPONSE,
        inverter=inverter.XHybrid,
        values=XHYBRID_VALUES,
        headers=None,
    ),
    InverterUnderTest(
        uri="/",
        method='POST',
        query_string='optType=ReadRealTimeData',
        response=X1_BOOST_AIR_MINI_RESPONSE,
        inverter=inverter.X1Mini,
        values=X1_MINI_VALUES,
        headers=None,
    ),
    InverterUnderTest(
        uri="/",
        method='POST',
        query_string='optType=ReadRealTimeData',
        response=X1_MINI_RESPONSE_V34,
        inverter=inverter.X1MiniV34,
        values=X1_MINI_VALUES_V34,
        headers=None,
    ),
    InverterUnderTest(
        uri="/",
        method='POST',
        query_string='optType=ReadRealTimeData',
        response=X1_SMART_RESPONSE,
        inverter=inverter.X1Smart,
        values=X1_SMART_VALUES,
        headers=X_FORWARDED_HEADER,
    ),
    InverterUnderTest(
        uri="/",
        method='POST',
        query_string='optType=ReadRealTimeData',
        response=X3_MIC_RESPONSE,
        inverter=inverter.X3,
        values=X3_VALUES,
        headers=None,
    ),
    InverterUnderTest(
        uri="/",
        method='POST',
        query_string='optType=ReadRealTimeData',
        response=X3_HYBRID_G3_RESPONSE,
        inverter=inverter.X3,
        values=X3_VALUES,
        headers=None,
    ),
    InverterUnderTest(
        uri="/",
        method='POST',
        query_string='optType=ReadRealTimeData',
        response=X1_HYBRID_G3_RESPONSE,
        inverter=inverter.X1,
        values=X1_VALUES,
        headers=None,
    ),
    InverterUnderTest(
        uri="/",
        method='POST',
        query_string='optType=ReadRealTimeData',
        response=X1_HYBRID_G3_2X_MPPT_RESPONSE,
        inverter=inverter.X1,
        values=X1_VALUES,
        headers=None,
    ),
    InverterUnderTest(
        uri="/",
        method='POST',
        query_string='optType=ReadRealTimeData',
        response=X3_HYBRID_G3_2X_MPPT_RESPONSE,
        inverter=inverter.X3,
        values=X3_HYBRID_VALUES,
        headers=None,
    ),
    InverterUnderTest(
        uri="/",
        method='POST',
        query_string='optType=ReadRealTimeData',
        response=X3_HYBRID_G3_2X_MPPT_RESPONSE_V34,
        inverter=inverter.X3V34,
        values=X3V34_HYBRID_VALUES,
        headers=None,
    ),
    InverterUnderTest(
        uri="/",
        method='POST',
        query_string='optType=ReadRealTimeData',
        response=X3_HYBRID_G3_2X_MPPT_RESPONSE_V34_NEGATIVE_POWER,
        inverter=inverter.X3V34,
        values=X3V34_HYBRID_VALUES_NEGATIVE_POWER,
        headers=None,
    ),
    InverterUnderTest(
        uri="/",
        method='POST',
        query_string='optType=ReadRealTimeData',
        response=X3_HYBRID_G3_2X_MPPT_RESPONSE_V34_EPS_MODE,
        inverter=inverter.X3V34,
        values=X3V34_HYBRID_VALUES_EPS_MODE,
        headers=None,
    ),
    InverterUnderTest(
        uri="/",
        method='POST',
        query_string='',
        response=QVOLTHYBG33P_RESPONSE_V34,
        inverter=inverter.QVOLTHYBG33P,
        values=QVOLTHYBG33P_VALUES,
        headers=None,
    ),
]


@pytest.fixture(params=INVERTERS_UNDER_TEST)
def inverters_fixture(httpserver, request):
    httpserver.expect_request(
        uri=request.param.uri,
        method=request.param.method,
        query_string=request.param.query_string,
        headers=request.param.headers
    ).respond_with_json(request.param.response)
    yield (
        (httpserver.host, httpserver.port),
        request.param.inverter,
        request.param.values
    )


@pytest.fixture(params=INVERTERS_UNDER_TEST)
def inverters_garbage_fixture(httpserver, request):
    httpserver.expect_request(
        uri=request.param.uri,
        method=request.param.method,
        query_string=request.param.query_string
    ).respond_with_json({'bingo': 'bango'})
    yield (
        (httpserver.host, httpserver.port),
        request.param.inverter
    )
