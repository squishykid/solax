import asyncio
from typing import Type

from solax.http_client import all_variations
from solax.inverter import Inverter, InverterError
from solax.inverters import (
    X1,
    X3,
    X3V34,
    X1Mini,
    X1MiniV34,
    X1Smart,
    X3HybridG4,
    XHybrid,
)

REGISTRY: list[Type[Inverter]] = [
    XHybrid,
    X3,
    X3V34,
    X3HybridG4,
    X1,
    X1Mini,
    X1MiniV34,
    X1Smart,
    # QVOLTHYBG33P,
    # X1Boost,
    # X1HybridGen4,
]


class DiscoveryError(Exception):
    """Raised when unable to discover inverter"""


async def discover(host, port, pwd="") -> Inverter:
    failures: list = []
    clients = all_variations(host, port, pwd)
    pending = set()

    async def identify_inverter(sleep, client_name, client):
        await asyncio.sleep(sleep)  # don't spam the inverter
        response = await client.request()
        for inverter_class in REGISTRY:
            await asyncio.sleep(0)
            try:
                inverter = inverter_class(client)

                if inverter.identify(response):
                    return inverter

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

    for sleep, (name, client) in enumerate(clients.items()):
        pending.add(
            asyncio.create_task(
                identify_inverter(sleep, name, client),
                name=name,
            )
        )

    while pending:
        done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)

        for task in done:
            if task.cancelled():
                continue

            try:
                inverter = await task

                for loser in pending:
                    loser.cancel()

                return inverter
            except RuntimeError as ex:
                failures.append(
                    (
                        task.get_name(),
                        ex,
                    )
                )

    raise DiscoveryError(
        (
            "Unable to connect to the inverter at "
            f"host={host} port={port}, or your inverter is not supported yet.\n"
            "Please see https://github.com/squishykid/solax/wiki/DiscoveryError\n"
            f"Failures={str(failures)}"
        )
    )
