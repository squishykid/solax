from __future__ import annotations

import dataclasses
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional
from weakref import WeakValueDictionary

import aiohttp

__all__ = ("InverterHttpClient", "Method")

if sys.version_info >= (3, 10):
    from dataclasses import KW_ONLY


REQUEST_TIMEOUT = 5.0
_CACHE: WeakValueDictionary[int, InverterHttpClient] = WeakValueDictionary()


class Method(Enum):
    GET = 1
    POST = 2


_kwargs: Dict[str, bool] = {}

if sys.version_info >= (3, 11):
    _kwargs["slots"] = True
    _kwargs["weakref_slot"] = True


@dataclass(frozen=True, **_kwargs)
class InverterHttpClient:
    """Initialize the Http client."""

    if sys.version_info >= (3, 10):
        _: KW_ONLY

    url: str
    method: Method
    pwd: str
    headers: Dict[str, str] = field(default_factory=dict)
    data: Optional[bytes] = None
    query: str = ""

    def __hash__(self):
        return id(self)

    def replace(self, **kwargs) -> InverterHttpClient:
        fields = dataclasses.fields(InverterHttpClient)
        data = {}
        values = []

        for fld in fields:
            if fld.name in kwargs:
                value = kwargs.pop(fld.name)
            else:
                value = getattr(self, fld.name)

            data[fld.name] = value

            if isinstance(value, dict):
                value = dict(value)
                values.append(tuple(value.items()))
            else:
                values.append(value)

            data[fld.name] = value

        key = hash(tuple(values))
        cached = _CACHE.get(key)

        if cached is None:
            cached = _CACHE[key] = InverterHttpClient(**data)

        return cached

    def with_headers(self, headers) -> InverterHttpClient:
        return self.replace(headers=dict(headers))

    def with_default_data(self) -> InverterHttpClient:
        data = "optType=ReadRealTimeData"
        if self.pwd:
            data = data + "&pwd=" + self.pwd
        return self.with_data(data)

    def with_data(self, data) -> InverterHttpClient:
        return self.replace(data=data)

    def with_query(self, query) -> InverterHttpClient:
        return self.replace(query=query)

    def with_default_query(self) -> InverterHttpClient:
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
            async with session.get(
                url, headers=self.headers, timeout=REQUEST_TIMEOUT
            ) as req:
                req.raise_for_status()
                resp = await req.read()
        return resp

    async def post(self):
        url = self.url + "?" + self.query if self.query else self.url
        data = self.data.encode("utf-8") if self.data else None
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, headers=self.headers, data=data, timeout=REQUEST_TIMEOUT
            ) as req:
                req.raise_for_status()
                resp = await req.read()
        return resp

    def __str__(self) -> str:
        using = "query in url" if self.query else "data in the body"
        return f"{self.url} using {using}"
