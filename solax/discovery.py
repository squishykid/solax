import asyncio
import logging
import sys
from asyncio import Future, Task
from collections import defaultdict
from typing import Dict, Literal, Sequence, Set, Tuple, Type, TypedDict, Union, cast

from solax.inverter import Inverter
from solax.inverter_http_client import InverterHttpClient

__all__ = ("discover", "DiscoveryKeywords", "DiscoveryError")

if sys.version_info >= (3, 10):
    from importlib.metadata import entry_points
else:
    from importlib_metadata import entry_points  # pragma: no cover

if sys.version_info >= (3, 11):
    from typing import Unpack
else:
    from typing_extensions import Unpack  # pragma: no cover

# Ranks inverter schemas from most-specific (least permissive) to
# least-specific (most permissive). REGISTRY is sorted by this table so
# that discover()'s tie-break (lowest rank wins) prefers the more
# tightly matching inverter when several schemas validate the same
# response.
#
# This is NOT derived from entry_points.txt order: setuptools
# alphabetizes entry points on install , so that ordering can't be
# relied on. This table is maintained by hand; drift is caught by
# tests/test_schema_ambiguity.py::test_registry_order_matches_specificity,
# which recomputes the expected order from tests/fixtures.py.
#
# Classes not listed here (e.g. a newly added inverter) rank last -- a
# conservative default that never lets an unranked schema outrank a
# known-specific one. The guardrail test forces new inverters to be
# ranked explicitly rather than silently relying on this default.
_SCHEMA_SPECIFICITY_ORDER: Tuple[str, ...] = (
    "X3Ultra",
    "X3MicProG2",
    "X3EVC",
    "X1Mini",
    "QVOLTHYBG33P",
    "XHybrid",
    "X3HybridG4",
    "X1Smart",
    "X1LiteLV",
    "X1HybridGen4",
    "X1G4Series",
    "X1",
    "X3V34",
    "X3",
    "X1MiniV34",
    "X1Boost",
)
_SCHEMA_SPECIFICITY_RANK: Dict[str, int] = {
    name: rank for rank, name in enumerate(_SCHEMA_SPECIFICITY_ORDER)
}


def _specificity_rank(inverter_class: Type[Inverter]) -> int:
    return _SCHEMA_SPECIFICITY_RANK.get(
        inverter_class.__name__, len(_SCHEMA_SPECIFICITY_ORDER)
    )


# registry of inverters
REGISTRY: Tuple[Type[Inverter], ...] = tuple(
    sorted(
        dict.fromkeys(
            loaded
            for ep in entry_points(group="solax.inverter")
            if issubclass(loaded := ep.load(), Inverter)
        ),
        key=_specificity_rank,
    )
)

logging.basicConfig(level=logging.INFO)


class DiscoveryKeywords(TypedDict, total=False):
    inverters: Sequence[Type[Inverter]]
    return_when: Literal["ALL_COMPLETED", "FIRST_COMPLETED"]


if sys.version_info >= (3, 9):
    _InverterTask = Task[Inverter]
else:
    _InverterTask = Task  # pragma: no cover


class _DiscoveryHttpClient:
    def __init__(
        self,
        inverter: Inverter,
        http_client: InverterHttpClient,
        request: Future,
    ):
        self._inverter = inverter
        self._http_client = http_client
        self._request: Future = request

    def __str__(self):
        return str(self._http_client)

    async def request(self):
        request = await self._request
        request.add_done_callback(self._restore_http_client)
        return await request

    def _restore_http_client(self, _: _InverterTask):
        self._inverter.http_client = self._http_client


async def _discovery_task(i) -> Inverter:
    logging.info("Trying inverter %s", i)
    await i.get_data()
    return i


async def discover(
    host, port, pwd="", **kwargs: Unpack[DiscoveryKeywords]
) -> Union[Inverter, Set[Inverter]]:
    # pylint: disable=too-many-locals
    done: Set[_InverterTask] = set()
    pending: Set[_InverterTask] = set()
    failures = set()
    requests: Dict[InverterHttpClient, Future] = defaultdict(
        asyncio.get_running_loop().create_future
    )

    # rank of the class each task was built from, in the order it was
    # offered to discover(); used to break ties deterministically when
    # several inverters' schemas match the same response
    priority: Dict[_InverterTask, int] = {}

    return_when = kwargs.get("return_when", asyncio.FIRST_COMPLETED)
    for rank, cls in enumerate(kwargs.get("inverters", REGISTRY)):
        for inverter in cls.build_all_variants(host, port, pwd):
            inverter.http_client = cast(
                InverterHttpClient,
                _DiscoveryHttpClient(
                    inverter, inverter.http_client, requests[inverter.http_client]
                ),
            )

            task = asyncio.create_task(_discovery_task(inverter), name=f"{inverter}")
            priority[task] = rank
            pending.add(task)

    if not pending:
        raise DiscoveryError("No inverters to try to discover")

    def cancel(pending: Set[_InverterTask]) -> Set[_InverterTask]:
        for task in pending:
            task.cancel()
        return pending

    def remove_failures_from(done: Set[_InverterTask]) -> None:
        for task in set(done):
            exc = task.exception()
            if exc:
                failures.add(exc)
                done.remove(task)

    # stagger HTTP request to prevent accidental Denial Of Service
    async def stagger() -> None:
        for http_client, future in requests.items():
            future.set_result(asyncio.create_task(http_client.request()))
            await asyncio.sleep(1)

    staggered = asyncio.create_task(stagger())

    while pending and (not done or return_when != asyncio.FIRST_COMPLETED):
        try:
            done, pending = await asyncio.wait(pending, return_when=return_when)
        except asyncio.CancelledError:
            staggered.cancel()
            await asyncio.gather(staggered, *cancel(pending), return_exceptions=True)
            raise

        remove_failures_from(done)

        if done and return_when == asyncio.FIRST_COMPLETED:
            break

        logging.debug("%d discovery tasks are still running...", len(pending))

        if pending and return_when != asyncio.FIRST_COMPLETED:
            pending.update(done)
            done.clear()

    remove_failures_from(done)
    staggered.cancel()
    await asyncio.gather(staggered, *cancel(pending), return_exceptions=True)

    if done:
        logging.info("Discovered inverters: %s", {task.result() for task in done})
        if return_when == asyncio.FIRST_COMPLETED:
            winner = min(done, key=priority.__getitem__)
            return await winner

        return {task.result() for task in done}

    raise DiscoveryError(
        "Unable to connect to the inverter at "
        f"host={host} port={port}, or your inverter is not supported yet.\n"
        "Please see https://github.com/squishykid/solax/wiki/DiscoveryError\n"
        f"Failures={str(failures)}"
    )


class DiscoveryError(Exception):
    """Raised when unable to discover inverter"""
