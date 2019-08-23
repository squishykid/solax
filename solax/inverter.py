import aiohttp
import json
import voluptuous as vol

class InverterError(Exception):
    """Indicates error communicating with inverter"""

class DiscoveryError(Exception):
    """Raised when unable to discover inverter"""

class Inverter:
    """Base wrapper around Inverter HTTP API"""
    def __init__(self, host, port):
        self.host = host
        self.port = port

    async def get_data(self):
        try:
            data = await self.make_request(
                self.host, self.port
            )
        except aiohttp.ClientError as ex:
            msg = "Could not connect to inverter endpoint"
            raise InverterError(msg) from ex
        except ValueError as ex:
            msg = "Received non-JSON data from inverter endpoint"
            raise InverterError(msg) from ex
        except vol.Invalid as ex:
            msg = "Received malformed JSON from inverter"
            raise InverterError(msg) from ex
        return data

    @classmethod
    async def make_request(cls, host, port):
        """
        Return dictionary of named sensor values
        Raise exception if unable to get data
        """
        raise NotImplementedError()

async def discover(host, port) -> Inverter:
    for inverter in REGISTRY:
        i = inverter(host, port)
        try:
            await i.get_data()
            return i
        except InverterError:
            pass
    raise DiscoveryError()

class XHybrid(Inverter):
    """
    Tested with:
    * SK-TL5000E
    """
    __schema = vol.Schema({
        vol.Required('method'): str,
        vol.Required('version'): str,
        vol.Required('type'): str,
        vol.Required('SN'): str,
        vol.Required('Data'): vol.Schema(
            vol.All(
                [vol.Coerce(float)],
                vol.Length(min=68, max=68)
                )
            ),
        vol.Required('Status'): vol.All(vol.Coerce(int), vol.Range(min=0)),
    }, extra=vol.REMOVE_EXTRA)

    @classmethod
    async def make_request(cls, hostname, port=80):
        base = 'http://{}:{}/api/realTimeData.htm'
        url = base.format(hostname, port)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as req:
                garbage = await req.read()
        formatted = garbage.decode("utf-8")
        formatted = formatted.replace(",,", ",0.0,").replace(",,", ",0.0,")
        json_response = json.loads(formatted)
        return cls.__schema(json_response)

class X3(Inverter):
    __schema = vol.Schema({
        vol.Required('type'): str,
        vol.Required('SN'): str,
        vol.Required('ver'): str,
        vol.Required('Data'): vol.Schema(
            vol.All(
                [vol.Coerce(float)],
                vol.Length(min=103, max=103)
                )
            ),
        vol.Required('Information'): vol.Schema(
            vol.All(
                vol.Length(min=9, max=9)
                )
            ),
    }, extra=vol.REMOVE_EXTRA)

    @classmethod
    async def make_request(cls, hostname, port=80):
        base = 'http://{}:{}/?optType=ReadRealTimeData'
        url = base.format(hostname, port)
        async with aiohttp.ClientSession() as session:
            async with session.post(url) as req:
                resp = await req.read()
        raw_json = resp.decode("utf-8")
        json_response = json.loads(raw_json)
        return cls.__schema(json_response)

# registry of inverters
REGISTRY = [XHybrid, X3]
