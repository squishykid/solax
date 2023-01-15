import glob
from pathlib import Path

from solax.http_client import all_variations
from solax.inverter import Inverter, InverterError

path = Path(__file__).parent
REGISTRY = glob.glob(f"{path}/inverters/*.json")


class DiscoveryError(Exception):
    """Raised when unable to discover inverter"""


async def discover(host, port, pwd="") -> Inverter:
    failures = []
    clients = all_variations(host, port, pwd)
    for name, client in clients.items():
        try:
            response = await client.request()
            for inverter_definition in REGISTRY:
                inverter = Inverter(inverter_definition, client)
                if inverter.identify(response):
                    return inverter
        except InverterError as ex:
            failures.append(ex)
    msg = (
        "Unable to connect to the inverter at "
        f"host={host} port={port}, or your inverter is not supported yet.\n"
        "Please see https://github.com/squishykid/solax/wiki/DiscoveryError\n"
        f"Failures={str(failures)}"
    )
    raise DiscoveryError(msg)
