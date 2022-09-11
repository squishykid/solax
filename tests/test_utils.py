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
