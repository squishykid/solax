from enum import Enum

import aiohttp

from solax.inverter_error import InverterError
from solax.utils import to_url


class Method(Enum):
    GET = 1
    POST = 2


class HttpClient:
    def __init__(self, url, method: Method = Method.POST, pwd=""):
        """Initialize the Http client."""
        self.url = url
        self.method = method
        self.pwd = pwd
        self.headers = None
        self.data = None
        self.query = ""

    @classmethod
    def build_w_url(cls, url, method: Method = Method.POST):
        http_client = cls(url, method, "")
        return http_client

    def with_headers(self, headers):
        self.headers = headers
        return self

    def with_default_data(self):
        data = "optType=ReadRealTimeData"
        if self.pwd:
            data = data + "&pwd=" + self.pwd
        return self.with_data(data)

    def with_data(self, data):
        self.data = data
        return self

    def with_query(self, query):
        self.query = query
        return self

    def with_default_query(self):
        if self.pwd:
            base = "optType=ReadRealTimeData&pwd={}&"
            query = base.format(self.pwd)
        else:
            query = "optType=ReadRealTimeData"

        return self.with_query(query)

    async def request(self):
        try:
            if self.method is Method.POST:
                return await self.post()
            return await self.get()
        except aiohttp.ClientError as ex:
            msg = "Could not connect to inverter endpoint"
            raise InverterError(msg, str(self.__class__.__name__)) from ex

    async def get(self):
        url = self.url + "?" + self.query if self.query else self.url
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as req:
                req.raise_for_status()
                resp = await req.read()
        return resp

    async def post(self):
        url = self.url + "?" + self.query if self.query else self.url
        data = self.data.encode("utf-8") if self.data else None
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, data=data) as req:
                req.raise_for_status()
                resp = await req.read()
        return resp

    def __str__(self) -> str:
        using = "query in url" if self.query else "data in the body"
        return f"{self.url} using {using}"


def all_variations(host, port, pwd=""):
    url = to_url(host, port)
    get = HttpClient.build_w_url(
        f"http://{host}:{port}/api/realTimeData.htm", Method.GET
    )
    post = HttpClient(url, Method.POST, pwd)
    headers = {"X-Forwarded-For": "5.8.8.8"}
    post_query = (
        HttpClient(url, Method.POST, pwd).with_default_query().with_headers(headers)
    )
    post_data = (
        HttpClient(url, Method.POST, pwd).with_default_data().with_headers(headers)
    )
    return {
        "get": get,
        "post": post,
        "post_query": post_query,
        "post_data": post_data,
    }
