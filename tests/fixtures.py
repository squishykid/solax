from collections import namedtuple
from copy import copy

import pytest

import solax.inverters as inverter
from tests.samples.expected_values import (
    QVOLTHYBG33P_VALUES,
    X1_BOOST_VALUES,
    X1_BOOST_VALUES_G4_V3,
    X1_BOOST_VALUES_OVERFLOWN,
    X1_BOOST_VALUES_V3,
    X1_HYBRID_G4_V_3_018_VALUES,
    X1_HYBRID_G4_VALUES,
    X1_MINI_VALUES,
    X1_MINI_VALUES_V34,
    X1_MINI_VALUES_V34_VER3,
    X1_SMART_VALUES,
    X1_VALUES,
    X3_EVC_VALUES,
    X3_HYBRID_G4_VALUES,
    X3_HYBRID_VALUES,
    X3_MICPRO_G2_VALUES,
    X3_ULTRA_VALUES,
    X3_VALUES,
    X3V34_HYBRID_VALUES,
    X3V34_HYBRID_VALUES_EPS_MODE,
    X3V34_HYBRID_VALUES_NEGATIVE_POWER,
    XHYBRID_VALUES,
)
from tests.samples.responses import (
    QVOLTHYBG33P_RESPONSE_V34,
    X1_BOOST_AIR_MINI_RESPONSE,
    X1_BOOST_RESPONSE,
    X1_BOOST_RESPONSE_G4_V3,
    X1_BOOST_RESPONSE_OVERFLOWN,
    X1_BOOST_RESPONSE_V3,
    X1_HYBRID_G3_2X_MPPT_RESPONSE,
    X1_HYBRID_G3_RESPONSE,
    X1_HYBRID_G4_RESPONSE,
    X1_HYBRID_G4_V_3_018_RESPONSE,
    X1_MINI_RESPONSE_V34,
    X1_MINI_RESPONSE_V34_VER3,
    X1_SMART_RESPONSE,
    X3_EVC_RESPONSE,
    X3_HYBRID_G3_2X_MPPT_RESPONSE,
    X3_HYBRID_G3_2X_MPPT_RESPONSE_V34,
    X3_HYBRID_G3_2X_MPPT_RESPONSE_V34_EPS_MODE,
    X3_HYBRID_G3_2X_MPPT_RESPONSE_V34_NEGATIVE_POWER,
    X3_HYBRID_G3_RESPONSE,
    X3_HYBRID_G4_RESPONSE,
    X3_MIC_RESPONSE,
    X3_MICPRO_G2_RESPONSE,
    X3_ULTRA_RESPONSE,
    XHYBRID_DE01_RESPONSE,
    XHYBRID_DE02_RESPONSE,
)

X_FORWARDED_HEADER = {"X-Forwarded-For": "5.8.8.8"}


@pytest.fixture()
def simple_http_fixture(httpserver):
    httpserver.expect_request(
        uri="/", method="GET", query_string="index.html"
    ).respond_with_json({"hello": "world"})
    yield (httpserver.host, httpserver.port)


InverterUnderTest = namedtuple(
    "InverterUnderTest",
    "uri, method, query_string, response, inverter, values, headers, data",
)

INVERTERS_UNDER_TEST = [
    InverterUnderTest(
        uri="/api/realTimeData.htm",
        method="GET",
        query_string=None,
        response=XHYBRID_DE01_RESPONSE,
        inverter=inverter.XHybrid,
        values=XHYBRID_VALUES,
        headers=None,
        data=None,
    ),
    InverterUnderTest(
        uri="/api/realTimeData.htm",
        method="GET",
        query_string=None,
        response=XHYBRID_DE02_RESPONSE,
        inverter=inverter.XHybrid,
        values=XHYBRID_VALUES,
        headers=None,
        data=None,
    ),
    InverterUnderTest(
        uri="/",
        method="POST",
        query_string=None,
        response=X1_HYBRID_G4_RESPONSE,
        inverter=inverter.X1HybridGen4,
        values=X1_HYBRID_G4_VALUES,
        headers=None,
        data="optType=ReadRealTimeData",
    ),
    InverterUnderTest(
        uri="/",
        method="POST",
        query_string="optType=ReadRealTimeData",
        response=X1_BOOST_AIR_MINI_RESPONSE,
        inverter=inverter.X1Mini,
        values=X1_MINI_VALUES,
        headers=None,
        data=None,
    ),
    InverterUnderTest(
        uri="/",
        method="POST",
        query_string="optType=ReadRealTimeData",
        response=X1_MINI_RESPONSE_V34,
        inverter=inverter.X1MiniV34,
        values=X1_MINI_VALUES_V34,
        headers=None,
        data=None,
    ),
    InverterUnderTest(
        uri="/",
        method="POST",
        query_string="optType=ReadRealTimeData",
        response=X1_SMART_RESPONSE,
        inverter=inverter.X1Smart,
        values=X1_SMART_VALUES,
        headers=X_FORWARDED_HEADER,
        data=None,
    ),
    InverterUnderTest(
        uri="/",
        method="POST",
        query_string="optType=ReadRealTimeData",
        response=X1_BOOST_RESPONSE,
        inverter=inverter.X1Boost,
        values=X1_BOOST_VALUES,
        headers=X_FORWARDED_HEADER,
        data=None,
    ),
    InverterUnderTest(
        uri="/",
        method="POST",
        query_string="optType=ReadRealTimeData",
        response=X1_BOOST_RESPONSE_V3,
        inverter=inverter.X1Boost,
        values=X1_BOOST_VALUES_V3,
        headers=X_FORWARDED_HEADER,
        data=None,
    ),
    InverterUnderTest(
        uri="/",
        method="POST",
        query_string="optType=ReadRealTimeData",
        response=X1_BOOST_RESPONSE_G4_V3,
        inverter=inverter.X1BoostG4,
        values=X1_BOOST_VALUES_G4_V3,
        headers=X_FORWARDED_HEADER,
        data=None,
    ),
    InverterUnderTest(
        uri="/",
        method="POST",
        query_string="optType=ReadRealTimeData",
        response=X1_BOOST_RESPONSE_OVERFLOWN,
        inverter=inverter.X1Boost,
        values=X1_BOOST_VALUES_OVERFLOWN,
        headers=X_FORWARDED_HEADER,
        data=None,
    ),
    InverterUnderTest(
        uri="/",
        method="POST",
        query_string="optType=ReadRealTimeData",
        response=X3_MIC_RESPONSE,
        inverter=inverter.X3,
        values=X3_VALUES,
        headers=None,
        data=None,
    ),
    InverterUnderTest(
        uri="/",
        method="POST",
        query_string="optType=ReadRealTimeData",
        response=X3_HYBRID_G3_RESPONSE,
        inverter=inverter.X3,
        values=X3_VALUES,
        headers=None,
        data=None,
    ),
    InverterUnderTest(
        uri="/",
        method="POST",
        query_string="optType=ReadRealTimeData",
        response=X1_HYBRID_G3_RESPONSE,
        inverter=inverter.X1,
        values=X1_VALUES,
        headers=None,
        data=None,
    ),
    InverterUnderTest(
        uri="/",
        method="POST",
        query_string="optType=ReadRealTimeData",
        response=X1_HYBRID_G3_2X_MPPT_RESPONSE,
        inverter=inverter.X1,
        values=X1_VALUES,
        headers=None,
        data=None,
    ),
    InverterUnderTest(
        uri="/",
        method="POST",
        query_string="optType=ReadRealTimeData",
        response=X3_HYBRID_G3_2X_MPPT_RESPONSE,
        inverter=inverter.X3,
        values=X3_HYBRID_VALUES,
        headers=None,
        data=None,
    ),
    InverterUnderTest(
        uri="/",
        method="POST",
        query_string="optType=ReadRealTimeData",
        response=X3_HYBRID_G3_2X_MPPT_RESPONSE_V34,
        inverter=inverter.X3V34,
        values=X3V34_HYBRID_VALUES,
        headers=None,
        data=None,
    ),
    InverterUnderTest(
        uri="/",
        method="POST",
        query_string="optType=ReadRealTimeData",
        response=X3_HYBRID_G3_2X_MPPT_RESPONSE_V34_NEGATIVE_POWER,
        inverter=inverter.X3V34,
        values=X3V34_HYBRID_VALUES_NEGATIVE_POWER,
        headers=None,
        data=None,
    ),
    InverterUnderTest(
        uri="/",
        method="POST",
        query_string="optType=ReadRealTimeData",
        response=X3_HYBRID_G3_2X_MPPT_RESPONSE_V34_EPS_MODE,
        inverter=inverter.X3V34,
        values=X3V34_HYBRID_VALUES_EPS_MODE,
        headers=None,
        data=None,
    ),
    InverterUnderTest(
        uri="/",
        method="POST",
        query_string=None,
        response=X3_HYBRID_G4_RESPONSE,
        inverter=inverter.X3HybridG4,
        values=X3_HYBRID_G4_VALUES,
        headers=None,
        data="optType=ReadRealTimeData",
    ),
    InverterUnderTest(
        uri="/",
        method="POST",
        query_string=None,
        response=X3_EVC_RESPONSE,
        inverter=inverter.X3EVC,
        values=X3_EVC_VALUES,
        headers=None,
        data="optType=ReadRealTimeData",
    ),
    InverterUnderTest(
        uri="/",
        method="POST",
        query_string=None,
        response=X3_MICPRO_G2_RESPONSE,
        inverter=inverter.X3MicProG2,
        values=X3_MICPRO_G2_VALUES,
        headers=None,
        data="optType=ReadRealTimeData",
    ),
    InverterUnderTest(
        uri="/",
        method="POST",
        query_string=None,
        response=X3_ULTRA_RESPONSE,
        inverter=inverter.X3Ultra,
        values=X3_ULTRA_VALUES,
        headers=None,
        data="optType=ReadRealTimeData",
    ),
    InverterUnderTest(
        uri="/",
        method="POST",
        query_string="",
        response=QVOLTHYBG33P_RESPONSE_V34,
        inverter=inverter.QVOLTHYBG33P,
        values=QVOLTHYBG33P_VALUES,
        headers=None,
        data=None,
    ),
    InverterUnderTest(
        uri="/",
        method="POST",
        query_string=None,
        response=X1_MINI_RESPONSE_V34_VER3,
        inverter=inverter.X1MiniV34,
        values=X1_MINI_VALUES_V34_VER3,
        headers=None,
        data="optType=ReadRealTimeData",
    ),
    InverterUnderTest(
        uri="/",
        method="POST",
        query_string=None,
        response=X1_HYBRID_G4_V_3_018_RESPONSE,
        inverter=inverter.X1HybridGen4,
        values=X1_HYBRID_G4_V_3_018_VALUES,
        headers=None,
        data="optType=ReadRealTimeData",
    ),
]


@pytest.fixture(params=INVERTERS_UNDER_TEST)
def inverters_under_test(request):
    yield request.param.inverter


@pytest.fixture(params=INVERTERS_UNDER_TEST)
def inverters_fixture(httpserver, request):
    httpserver.expect_request(
        uri=request.param.uri,
        method=request.param.method,
        query_string=request.param.query_string,
        headers=request.param.headers,
        data=request.param.data,
    ).respond_with_json(request.param.response)
    yield (
        (httpserver.host, httpserver.port),
        request.param.inverter,
        request.param.values,
    )


@pytest.fixture(params=INVERTERS_UNDER_TEST)
def inverters_garbage_fixture(httpserver, request):
    httpserver.expect_request(
        uri=request.param.uri,
        method=request.param.method,
        query_string=request.param.query_string,
    ).respond_with_json({"bingo": "bango"})
    yield ((httpserver.host, httpserver.port), request.param.inverter)


@pytest.fixture(params=INVERTERS_UNDER_TEST)
def inverters_fixture_all_zero(httpserver, request):
    """Use defined responses but replace the data with all zero values.
    Testing incorrect responses.
    """

    response = request.param.response
    response = copy(response)
    response["Data"] = [0] * (len(response["Data"]))

    httpserver.expect_request(
        uri=request.param.uri,
        method=request.param.method,
        query_string=request.param.query_string,
        headers=request.param.headers,
        data=request.param.data,
    ).respond_with_json(response)
    yield (
        (httpserver.host, httpserver.port),
        request.param.inverter,
        request.param.values,
    )
