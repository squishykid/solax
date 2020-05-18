import pytest
from voluptuous import Invalid
from solax.inverter import startswith


def test_does_start_with():
    expected = "AAAA"
    actual = "AAAA"
    bingo = startswith(expected)(actual)
    assert bingo == actual


def test_does_not_start_with():
    expected = "AAAA"
    actual = "BBBB"
    with pytest.raises(Invalid):
        startswith(expected)(actual)


def test_is_not_str():
    expected = "AAAA"
    actual = 1
    with pytest.raises(Invalid):
        startswith(expected)(actual)
