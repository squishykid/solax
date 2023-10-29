import pytest
from voluptuous import Invalid

from solax.utils import contains_none_zero_value, startswith


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


def test_contains_none_zero_value():
    with pytest.raises(Invalid):
        contains_none_zero_value([0])

    with pytest.raises(Invalid):
        contains_none_zero_value([0, 0])

    not_a_list = 1
    with pytest.raises(Invalid):
        contains_none_zero_value(not_a_list)

    expected = [1, 0]
    actual = contains_none_zero_value(expected)
    assert actual == expected

    expected = [-1, 1]
    actual = contains_none_zero_value(expected)
    assert actual == expected
