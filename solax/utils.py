from typing import Protocol, Tuple
from voluptuous import Invalid


class Packer(Protocol):  # pragma: no cover
    # pylint: disable=R0903
    """
    Pack multiple raw values from the inverter
     data into one raw value
    """

    def __call__(self, *vals: float) -> float:
        ...


PackerBuilderResult = Tuple[Tuple[int, ...], Packer]


class PackerBuilder(Protocol):  # pragma: no cover
    # pylint: disable=R0903
    """
    Build a packer by identifying the indexes of the
    raw values to be fed to the packer
    """

    def __call__(self, *indexes: int) -> PackerBuilderResult:
        ...


def __u16_packer(*values: float) -> float:
    accumulator = 0.0
    stride = 1
    for value in values:
        accumulator += value * stride
        stride *= 2**16
    return accumulator


def pack_u16(*indexes: int) -> PackerBuilderResult:
    """
    Some values are expressed over 2 (or potentially
    more 16 bit [aka "short"] registers). Here we combine
    them, in order of least to most significant.
    """
    return (indexes, __u16_packer)


def startswith(something):
    def inner(actual):
        if isinstance(actual, str):
            if actual.startswith(something):
                return actual
        raise Invalid(f"{str(actual)} does not start with {something}")

    return inner


def div10(val):
    return val / 10


def div100(val):
    return val / 100


INT16_MAX = 0x7FFF


def to_signed(val):
    if val > INT16_MAX:
        val -= 2**16
    return val


def twoway_div10(val):
    return to_signed(val) / 10


def twoway_div100(val):
    return to_signed(val) / 100
