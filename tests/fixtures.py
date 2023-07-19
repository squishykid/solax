import inspect
from collections import namedtuple

import pytest

from solax import inverters
from tests.samples.expected_values import (
    QVOLTHYBG33P_VALUES,
    X1_BOOST_VALUES,
    X1_HYBRID_G4_VALUES,
    X1_MINI_VALUES,
    X1_MINI_VALUES_V34,
    X1_SMART_VALUES,
    X1_VALUES,
    X3_HYBRID_G4_VALUES,
    X3_HYBRID_VALUES,
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
    X1_HYBRID_G3_2X_MPPT_RESPONSE,
    X1_HYBRID_G3_RESPONSE,
    X1_HYBRID_G4_RESPONSE,
    X1_MINI_RESPONSE_V34,
    X1_SMART_RESPONSE,
    X3_HYBRID_G3_2X_MPPT_RESPONSE,
    X3_HYBRID_G3_2X_MPPT_RESPONSE_V34,
    X3_HYBRID_G3_2X_MPPT_RESPONSE_V34_EPS_MODE,
    X3_HYBRID_G3_2X_MPPT_RESPONSE_V34_NEGATIVE_POWER,
    X3_HYBRID_G3_RESPONSE,
    X3_HYBRID_G4_RESPONSE,
    X3_MIC_RESPONSE,
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
    "uri, method, query_string, response, inverter, values, headers, data, client, id",
)


# pylint: disable=too-many-arguments
def inverter_under_test_maker(
    uri: str, method, query_string, response, inverter, values, headers, data, client
):
    callers_local_vars = inspect.currentframe().f_back.f_locals.items()  # type: ignore
    response_var_name = [
        var_name for var_name, var_val in callers_local_vars if var_val is response
    ]
    assert len(response_var_name) == 1
    values_var_name = [
        var_name for var_name, var_val in callers_local_vars if var_val is values
    ]
    assert len(values_var_name) == 1
    unique_id = f"{inverter.__name__}_http({client})_\
    {response_var_name[0]}_produces_{values_var_name[0]}"

    return InverterUnderTest(
        uri,
        method,
        query_string,
        response,
        inverter,
        values,
        headers,
        data,
        client,
        unique_id,
    )


INVERTERS_UNDER_TEST = [
    inverter_under_test_maker(
        uri="/api/realTimeData.htm",
        method="GET",
        query_string=None,
        response=XHYBRID_DE01_RESPONSE,
        inverter=inverters.XHybrid,
        values=XHYBRID_VALUES,
        headers=None,
        data=None,
        client="get",
    ),
    inverter_under_test_maker(
        uri="/api/realTimeData.htm",
        method="GET",
        query_string=None,
        response=XHYBRID_DE02_RESPONSE,
        inverter=inverters.XHybrid,
        values=XHYBRID_VALUES,
        headers=None,
        data=None,
        client="get",
    ),
    inverter_under_test_maker(
        uri="/",
        method="POST",
        query_string=None,
        response=X1_HYBRID_G4_RESPONSE,
        inverter=inverters.X1HybridGen4,
        values=X1_HYBRID_G4_VALUES,
        headers=None,
        data="optType=ReadRealTimeData",
        client="post_data",
    ),
    inverter_under_test_maker(
        uri="/",
        method="POST",
        query_string="optType=ReadRealTimeData",
        response=X1_BOOST_AIR_MINI_RESPONSE,
        inverter=inverters.X1Mini,
        values=X1_MINI_VALUES,
        headers=None,
        data=None,
        client="post_query",
    ),
    inverter_under_test_maker(
        uri="/",
        method="POST",
        query_string="optType=ReadRealTimeData",
        response=X1_MINI_RESPONSE_V34,
        inverter=inverters.X1MiniV34,
        values=X1_MINI_VALUES_V34,
        headers=None,
        data=None,
        client="post_query",
    ),
    inverter_under_test_maker(
        uri="/",
        method="POST",
        query_string="optType=ReadRealTimeData",
        response=X1_SMART_RESPONSE,
        inverter=inverters.X1Smart,
        values=X1_SMART_VALUES,
        headers=X_FORWARDED_HEADER,
        data=None,
        client="post_query",
    ),
    inverter_under_test_maker(
        uri="/",
        method="POST",
        query_string="optType=ReadRealTimeData",
        response=X1_BOOST_RESPONSE,
        inverter=inverters.X1MiniV34,
        values=X1_BOOST_VALUES,
        headers=X_FORWARDED_HEADER,
        data=None,
        client="post_query",
    ),
    inverter_under_test_maker(
        uri="/",
        method="POST",
        query_string="optType=ReadRealTimeData",
        response=X3_MIC_RESPONSE,
        inverter=inverters.X3,
        values=X3_VALUES,
        headers=None,
        data=None,
        client="post_query",
    ),
    inverter_under_test_maker(
        uri="/",
        method="POST",
        query_string="optType=ReadRealTimeData",
        response=X3_HYBRID_G3_RESPONSE,
        inverter=inverters.X3,
        values=X3_VALUES,
        headers=None,
        data=None,
        client="post_query",
    ),
    inverter_under_test_maker(
        uri="/",
        method="POST",
        query_string="optType=ReadRealTimeData",
        response=X1_HYBRID_G3_RESPONSE,
        inverter=inverters.X1,
        values=X1_VALUES,
        headers=None,
        data=None,
        client="post_query",
    ),
    inverter_under_test_maker(
        uri="/",
        method="POST",
        query_string="optType=ReadRealTimeData",
        response=X1_HYBRID_G3_2X_MPPT_RESPONSE,
        inverter=inverters.X1,
        values=X1_VALUES,
        headers=None,
        data=None,
        client="post_query",
    ),
    inverter_under_test_maker(
        uri="/",
        method="POST",
        query_string="optType=ReadRealTimeData",
        response=X3_HYBRID_G3_2X_MPPT_RESPONSE,
        inverter=inverters.X3,
        values=X3_HYBRID_VALUES,
        headers=None,
        data=None,
        client="post_query",
    ),
    inverter_under_test_maker(
        uri="/",
        method="POST",
        query_string="optType=ReadRealTimeData",
        response=X3_HYBRID_G3_2X_MPPT_RESPONSE_V34,
        inverter=inverters.X3V34,
        values=X3V34_HYBRID_VALUES,
        headers=None,
        data=None,
        client="post_query",
    ),
    inverter_under_test_maker(
        uri="/",
        method="POST",
        query_string="optType=ReadRealTimeData",
        response=X3_HYBRID_G3_2X_MPPT_RESPONSE_V34_NEGATIVE_POWER,
        inverter=inverters.X3V34,
        values=X3V34_HYBRID_VALUES_NEGATIVE_POWER,
        headers=None,
        data=None,
        client="post_query",
    ),
    inverter_under_test_maker(
        uri="/",
        method="POST",
        query_string="optType=ReadRealTimeData",
        response=X3_HYBRID_G3_2X_MPPT_RESPONSE_V34_EPS_MODE,
        inverter=inverters.X3V34,
        values=X3V34_HYBRID_VALUES_EPS_MODE,
        headers=None,
        data=None,
        client="post_query",
    ),
    inverter_under_test_maker(
        uri="/",
        method="POST",
        query_string=None,
        response=X3_HYBRID_G4_RESPONSE,
        inverter=inverters.X3HybridG4,
        values=X3_HYBRID_G4_VALUES,
        headers=None,
        data="optType=ReadRealTimeData",
        client="post_query",
    ),
    inverter_under_test_maker(
        uri="/",
        method="POST",
        query_string="",
        response=QVOLTHYBG33P_RESPONSE_V34,
        inverter=inverters.QVOLTHYBG33P,
        values=QVOLTHYBG33P_VALUES,
        headers=None,
        data=None,
        client="post",
    ),
]


def inverter_id_getter(val):
    if isinstance(val, (InverterUnderTest,)):
        return val.id
    return None


@pytest.fixture(params=INVERTERS_UNDER_TEST, ids=inverter_id_getter)
def inverters_under_test(request):
    yield request.param.inverter


@pytest.fixture(params=INVERTERS_UNDER_TEST, ids=inverter_id_getter)
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
        request.param.client,
        request.param.values,
    )


@pytest.fixture(params=INVERTERS_UNDER_TEST, ids=inverter_id_getter)
def inverters_garbage_fixture(httpserver, request):
    httpserver.expect_request(
        uri=request.param.uri,
        method=request.param.method,
        query_string=request.param.query_string,
    ).respond_with_json({"bingo": "bango"})
    yield (
        (httpserver.host, httpserver.port),
        request.param.inverter,
        request.param.client,
    )
