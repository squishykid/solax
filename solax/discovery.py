from typing import Type

from solax.http_client import all_variations
from solax.inverter import Inverter, InverterError
from solax.inverters import X1, X3, X3V34, X1Mini, X3HybridG4, XHybrid

REGISTRY: list[Type[Inverter]] = [
    XHybrid,
    X3,
    X3V34,
    X3HybridG4,
    X1,
    X1Mini,
    # X1Smart,
    # QVOLTHYBG33P,
    # X1Boost,
    # X1HybridGen4,
]


class DiscoveryError(Exception):
    """Raised when unable to discover inverter"""


async def discover(host, port, pwd="") -> Inverter:
    failures: list = []
    clients = all_variations(host, port, pwd)
    for client_name, client in clients.items():
        try:
            response = await client.request()
        except InverterError as ex:
            failures.append(
                (
                    client_name,
                    ex,
                )
            )
            continue
        for inverter_class in REGISTRY:
            try:
                inverter = inverter_class(client)
                if inverter.identify(response):
                    return inverter
                else:
                    failures.append(
                        (
                            client_name,
                            inverter_class.__name__,
                            "did not identify",
                        )
                    )
            except InverterError as ex:
                failures.append(
                    (
                        client_name,
                        inverter_class.__name__,
                        ex,
                    )
                )
    msg = (
        "Unable to connect to the inverter at "
        f"host={host} port={port}, or your inverter is not supported yet.\n"
        "Please see https://github.com/squishykid/solax/wiki/DiscoveryError\n"
        f"Failures={str(failures)}"
    )
    raise DiscoveryError(msg)
