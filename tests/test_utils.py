import struct

import pytest

from solax import utils


@pytest.mark.parametrize(
    "val_to_check",
    [
        0,
        1,
        0x7FFF,  # int16 max
        0x8000,  # - 2**15
        0xFFFF,  # -1
    ],
)
def test_to_signed(val_to_check):
    # Take input as an int so can bit-twiddle reliably
    actual = utils.to_signed(val_to_check)
    expected = struct.unpack("<h", struct.pack("<H", val_to_check))[0]
    assert actual == expected


@pytest.mark.parametrize(
    "val_to_check_32",
    [
        0,
        1,
        0x8000,  # 32768
        0xFFFF,  # 65535
        0x7FFFFFFF,  # int32 max
        0x80000000,  # - 2**31
        0x7FFFFFFF,  # -1
    ],
)
def test_to_signed32(val_to_check_32):
    # Take input as an int so can bit-twiddle reliably
    actual = utils.to_signed32(val_to_check_32)
    expected = struct.unpack("<i", struct.pack("<I", val_to_check_32))[0]
    assert actual == expected
