from enum import Enum

import aiohttp


class Method(Enum):
    GET = 1
    POST = 2


class InverterHttpClient:
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
        if self.method is Method.POST:
            return await self.post()
        return await self.get()

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
