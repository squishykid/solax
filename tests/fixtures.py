from collections import namedtuple
import pytest
from solax import inverter

XHYBRID_DE01_RESPONSE = {
    'method': 'uploadsn',
    'version': 'Solax_SI_CH_2nd_20160912_DE02',
    'type': 'AL_SE',
    'SN': 'XXXXXXX',
    'Data': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
             10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
             30, 31, 32, 33, 34, 35, 36, 37, 38, 39,
             40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
             50, 51, 52, 53, 54, 55, 56, 57],
    'Status': 2
}

XHYBRID_DE02_RESPONSE = {
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

X1_BOOST_AIR_MINI_RESPONSE = {
    "type": "X1-Boost-Air-Mini",
    "SN": "XXXXXXX",
    "ver": "2.32.6",
    "Data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
             10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
             30, 31, 32, 33, 34, 35, 36, 37, 38, 39,
             40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
             50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
             60, 61, 62, 63, 64, 65, 66, 67, 68],
    "Information": [2.500, 4, "X1-Boost-Air-Mini", "XXXXXXX",
                    1, 3.25, 1.09, 1.10, 0.00]
}

X3_MIC_RESPONSE = {
    "type": "X3-MIC",
    "SN": "XXXXXXX",
    "ver": "2.033.20",
    "Data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
             10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
             30, 31, 32, 33, 34, 35, 36, 37, 38, 39,
             40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
             50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
             60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
             70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
             80, 81, 82, 83, 84, 85, 86, 87, 88, 89,
             90, 91, 92, 93, 94, 95, 96, 97, 98, 99,
             100, 101, 102],
    "Information": [8.000, 7, "X3-MIC", "XXXXXXX",
                    1, 1.10, 1.02, 1.09, 1.02]
}

X1_HYBRID_G3_RESPONSE = {
    "type": "X1-Hybiyd-G3",
    "SN": "XXXXXXX",
    "ver": "2.033.20",
    "Data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
             10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
             30, 31, 32, 33, 34, 35, 36, 37, 38, 39,
             40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
             50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
             60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
             70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
             80, 81, 82, 83, 84, 85, 86, 87, 88, 89,
             90, 91, 92, 93, 94, 95, 96, 97, 98, 99,
             100, 101],
    "Information": [8.000, 7, "X3-MIC", "XXXXXXX",
                    1, 1.10, 1.02, 1.09, 1.02]
}

X1_HYBRID_G3_2X_MPPT_RESPONSE = {
    "type": "X1-Hybiyd-G3",
    "SN": "XXXXXXXXXX",
    "ver": "2.033.20",
    "Data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
             10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
             30, 31, 32, 33, 34, 35, 36, 37, 38, 39,
             40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
             50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
             60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
             70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
             80, 81, 82, 83, 84, 85, 86, 87, 88, 89,
             90, 91, 92, 93, 94, 95, 96, 97, 98, 99,
             100, 101, 102, 103, 104, 105, 106],
    "Information": [3.000, 3, "X1-Hybiyd-G3", "YYYYYYYYYYYYYY",
                    1, 3.11, 0.00, 3.13, 1.05],
    "battery": {
        "brand": "0",
        "masterVer": "0.00",
        "slaveNum": "0",
        "slaveVer": [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
        "slaveType": [0, 0, 0, 0, 0, 0, 0, 0]
    }
}

X3_HYBRID_G3_RESPONSE = {
    "type": "X3-Hybiyd-G3",
    "SN": "XXXXXXX",
    "ver": "2.32.6",
    "Data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
             10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
             30, 31, 32, 33, 34, 35, 36, 37, 38, 39,
             40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
             50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
             60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
             70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
             80, 81, 82, 83, 84, 85, 86, 87, 88, 89,
             90, 91, 92, 93, 94, 95, 96, 97, 98, 99,
             100, 101],
    "Information": [0.000, 5, "X3-Hybiyd-G3", "XXXXXXX",
                    1, 3.00, 0.00, 3.17, 1.01]
}

X3_HYBRID_G3_2X_MPPT_RESPONSE = {
    "type": "X3-Hybiyd-G3",
    "SN": "XXXXXXXXXX",
    "ver": "2.033.20",
    "Data": [0.0, 0.0, 0.0, 0.0, 0.9, 234.0, 3189, 42, 15.2, 27.0, -25, 0, 0,
             210.30, -15.70, -3321, 24, 8.6, 0, 11.0, 1, 68, 232.4, 170.0,
             31.0, 35.0, 22.6, 20.7, 3.8, 3.8, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             2.03, 23.41, 123, 1344, 1722, 5.4, 6.9, 250.0, 251.9, 50.01,
             50.01, 50.01, 0.0, 0.0, 0, 0.00, 0, 0, 0, 0.00, 0, 0, 0, 0, 0.00,
             0, 0, 2, 1, 26, 1.00, 0, 100, 10, 25.00, 25.00, 0, 0, 0, 0, 0.0,
             10.8, 24.4, 0.0, 0, 2, 0.0, 0.0, 0, 0.0, 0.0, 0, 0, 0, 0, 1, 1,
             0, 0, 0.00, 0.00, 1, 273, 212.3, -16.2, -3439],
    "Information": [8.000, 5, "X3-Hybiyd-G3", "XXXXXXXX", 1, 4.47, 0.00, 4.34,
                    1.05],
    "battery": {
      "brand": "83",
      "masterVer": "1.11",
      "slaveNum": "4",
      "slaveVer": [1.13, 1.13, 1.13, 1.13]
    }
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


X3_VALUES = {
    'PV1 Current': 0,
    'PV2 Current': 1,
    'PV1 Voltage': 2,
    'PV2 Voltage': 3,

    'Output Current Phase 1': 4,
    'Network Voltage Phase 1': 5,
    'AC Power': 6,

    'Inverter Temperature': 7,
    'Today\'s Energy': 8,
    'Total Energy': 9,
    'Exported Power': 10,
    'PV1 Power': 11,
    'PV2 Power': 12,

    'Battery Voltage': 13,
    'Battery Current': 14,
    'Battery Power': 15,
    'Battery Temperature': 16,
    'Battery Remaining Capacity': 21,

    'Total Feed-in Energy': 41,
    'Total Consumption': 42,

    'Output Current Phase 2': 46,
    'Output Current Phase 3': 47,
    'Network Voltage Phase 2': 48,
    'Network Voltage Phase 3': 49,
    'Grid Frequency Phase 1': 50,
    'Grid Frequency Phase 2': 51,
    'Grid Frequency Phase 3': 52,
    'Power Now Phase 1': 43,
    'Power Now Phase 2': 44,
    'Power Now Phase 3': 45,



    'EPS Voltage': 53,
    'EPS Current': 54,
    'EPS Power': 55,
    'EPS Frequency': 56,
}

X3_HYBRID_VALUES = {
    'PV1 Current': 0,
    'PV2 Current': 0,
    'PV1 Voltage': 0,
    'PV2 Voltage': 0,

    'Output Current Phase 1': 0.9,
    'Network Voltage Phase 1': 234,
    'AC Power': 3189,

    'Inverter Temperature': 42,
    'Today\'s Energy': 15.2,
    'Total Energy': 27,
    'Exported Power': -25,
    'PV1 Power': 0,
    'PV2 Power': 0,

    'Battery Voltage': 210.3,
    'Battery Current': -15.7,
    'Battery Power': -3321,
    'Battery Temperature': 24,
    'Battery Remaining Capacity': 68,

    'Total Feed-in Energy': 2.03,
    'Total Consumption': 23.41,

    'Output Current Phase 2': 5.4,
    'Output Current Phase 3': 6.9,
    'Network Voltage Phase 2': 250,
    'Network Voltage Phase 3': 251.9,
    'Grid Frequency Phase 1': 50.01,
    'Grid Frequency Phase 2': 50.01,
    'Grid Frequency Phase 3': 50.01,
    'Power Now Phase 1': 123,
    'Power Now Phase 2': 1344,
    'Power Now Phase 3': 1722,

    'EPS Voltage': 0,
    'EPS Current': 0,
    'EPS Power': 0,
    'EPS Frequency': 0,
}

X1_VALUES = {
    'PV1 Current': 0,
    'PV2 Current': 1,
    'PV1 Voltage': 2,
    'PV2 Voltage': 3,

    'Output Current': 4,
    'Network Voltage': 5,
    'AC Power': 6,

    'Inverter Temperature': 7,
    'Today\'s Energy': 8,
    'Total Energy': 9,
    'Exported Power': 10,
    'PV1 Power': 11,
    'PV2 Power': 12,

    'Battery Voltage': 13,
    'Battery Current': 14,
    'Battery Power': 15,
    'Battery Temperature': 16,
    'Battery Remaining Capacity': 21,

    'Total Feed-in Energy': 41,
    'Total Consumption': 42,

    'Grid Frequency': 50,
    'Power Now': 43,

    'EPS Voltage': 53,
    'EPS Current': 54,
    'EPS Power': 55,
    'EPS Frequency': 56,
}

X1_MINI_VALUES = {
    'PV1 Current': 0,
    'PV2 Current': 1,
    'PV1 Voltage': 2,
    'PV2 Voltage': 3,

    'Output Current': 4,
    'Network Voltage': 5,
    'AC Power': 6,

    'Inverter Temperature': 7,
    'Today\'s Energy': 8,
    'Total Energy': 9,
    'Exported Power': 10,
    'PV1 Power': 11,
    'PV2 Power': 12,

    'Total Feed-in Energy': 41,
    'Total Consumption': 42,

    'Power Now': 43,
    'Grid Frequency': 50,
}


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
    'uri, method, query_string, response, inverter, values'
)

INVERTERS_UNDER_TEST = [
    InverterUnderTest(
        uri='/api/realTimeData.htm',
        method='GET',
        query_string=None,
        response=XHYBRID_DE01_RESPONSE,
        inverter=inverter.XHybrid,
        values=XHYBRID_VALUES,
    ),
    InverterUnderTest(
        uri='/api/realTimeData.htm',
        method='GET',
        query_string=None,
        response=XHYBRID_DE02_RESPONSE,
        inverter=inverter.XHybrid,
        values=XHYBRID_VALUES,
    ),
    InverterUnderTest(
        uri="/",
        method='POST',
        query_string='optType=ReadRealTimeData',
        response=X1_BOOST_AIR_MINI_RESPONSE,
        inverter=inverter.X1Mini,
        values=X1_MINI_VALUES,
    ),
    InverterUnderTest(
        uri="/",
        method='POST',
        query_string='optType=ReadRealTimeData',
        response=X3_MIC_RESPONSE,
        inverter=inverter.X3,
        values=X3_VALUES,
    ),
    InverterUnderTest(
        uri="/",
        method='POST',
        query_string='optType=ReadRealTimeData',
        response=X3_HYBRID_G3_RESPONSE,
        inverter=inverter.X3,
        values=X3_VALUES,
    ),
    InverterUnderTest(
        uri="/",
        method='POST',
        query_string='optType=ReadRealTimeData',
        response=X1_HYBRID_G3_RESPONSE,
        inverter=inverter.X1,
        values=X1_VALUES,
    ),
    InverterUnderTest(
        uri="/",
        method='POST',
        query_string='optType=ReadRealTimeData',
        response=X1_HYBRID_G3_2X_MPPT_RESPONSE,
        inverter=inverter.X1,
        values=X1_VALUES,
    ),
    InverterUnderTest(
        uri="/",
        method='POST',
        query_string='optType=ReadRealTimeData',
        response=X3_HYBRID_G3_2X_MPPT_RESPONSE,
        inverter=inverter.X3,
        values=X3_HYBRID_VALUES,
    )
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
