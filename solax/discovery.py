import asyncio
import logging
import typing

from solax.inverter import Inverter, InverterError
from solax.inverters import (
    QVOLTHYBG33P,
    X1,
    X3,
    X3V34,
    X1Boost,
    X1HybridGen4,
    X1Mini,
    X1MiniV34,
    X1Smart,
    X3HybridG4,
    X3MicProG2,
    XHybrid,
)

# registry of inverters
REGISTRY = [
    XHybrid,
    X3,
    X3V34,
    X3HybridG4,
    X1,
    X1Mini,
    X1MiniV34,
    X1Smart,
    QVOLTHYBG33P,
    X1Boost,
    X1HybridGen4,
    X3MicProG2,
]


logging.basicConfig(level=logging.INFO)


class DiscoveryState:
    _discovered_inverter: typing.Optional[Inverter]
    _tasks: typing.Set[asyncio.Task]
    _failures: list

    def __init__(self):
        self._discovered_inverter = None
        self._tasks = set()
        self._failures = []

    def get_discovered_inverter(self):
        return self._discovered_inverter

    def _task_handler(self, task):
        try:
            self._tasks.remove(task)
            result = task.result()
            self._discovered_inverter = result
            for a_task in self._tasks:
                a_task.cancel()
        except asyncio.CancelledError:
            logging.debug("task %s canceled", task.get_name())
        except InverterError as ex:
            self._failures.append(ex)

    @classmethod
    async def _discovery_task(cls, i) -> Inverter:
        logging.info("Trying inverter %s", i)
        await i.get_data()
        return i

    async def discover(self, host, port, pwd="", model="") -> Inverter:       
        for inverter in REGISTRY:
            logging.warning("Model: %s Inverter: %s", model, inverter.__name__)
            if model == "" or inverter.__name__ == model:
                logging.warning("Found inverter for model %s", model)
                for i in inverter.build_all_variants(host, port, pwd):
                    task = asyncio.create_task(self._discovery_task(i), name=f"{i}")
                    task.add_done_callback(self._task_handler)
                    self._tasks.add(task)

        while len(self._tasks) > 0:
            logging.debug("%d discovery tasks are still running...", len(self._tasks))
            await asyncio.sleep(0.5)

        if self._discovered_inverter is not None:
            logging.info("Discovered inverter: %s", self._discovered_inverter)
            return self._discovered_inverter

        msg = (
            "Unable to connect to the inverter at "
            f"host={host} port={port}, or your inverter is not supported yet.\n"
            "Please see https://github.com/squishykid/solax/wiki/DiscoveryError\n"
            f"Failures={str(self._failures)}"
        )
        raise DiscoveryError(msg)


class DiscoveryError(Exception):
    """Raised when unable to discover inverter"""


async def discover(host, port, pwd="", model="") -> Inverter:
    discover_state = DiscoveryState()
    await discover_state.discover(host, port, pwd, model)
    return discover_state.get_discovered_inverter()
