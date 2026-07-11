"""
Structural invariants every inverter schema must satisfy, regardless of
whether responses are currently ambiguous (see test_schema_ambiguity.py):

* "type" must be pinned to a specific value/pattern, never a bare
  int/str type check -- an unconstrained type field is the single
  biggest source of accidental cross-inverter matches.
* every length constraint must be exact (min == max), possibly with
  several exact alternatives via vol.Any -- never an open range, which
  silently accepts lengths nobody has ever observed for that inverter.
"""

import pytest
import voluptuous as vol

from solax.discovery import REGISTRY


def _iter_length_validators(node):
    if isinstance(node, vol.Length):
        yield node
    elif isinstance(node, vol.Schema):
        yield from _iter_length_validators(node.schema)
    elif isinstance(node, (vol.All, vol.Any)):
        for validator in node.validators:
            yield from _iter_length_validators(validator)
    elif isinstance(node, list):
        for validator in node:
            yield from _iter_length_validators(validator)


@pytest.mark.parametrize("inverter_class", REGISTRY, ids=lambda c: c.__name__)
def test_type_field_is_pinned(inverter_class):
    type_validator = inverter_class.schema().schema["type"]
    assert not isinstance(type_validator, type), (
        f"{inverter_class.__name__}'s schema leaves 'type' unconstrained "
        f"({type_validator!r}); pin it to the exact literal/pattern seen "
        "in tests/samples/responses.py"
    )


@pytest.mark.xfail(
    reason="some inverter schemas still use length ranges instead of exact "
    "lengths; tightening them is tracked separately and shouldn't block CI "
    "in the meantime",
    strict=False,
)
@pytest.mark.parametrize("inverter_class", REGISTRY, ids=lambda c: c.__name__)
def test_length_constraints_are_exact(inverter_class):
    schema_dict = inverter_class.schema().schema
    for key in ("data", "information"):
        if key not in schema_dict:
            continue
        for length in _iter_length_validators(schema_dict[key]):
            assert length.min == length.max, (
                f"{inverter_class.__name__}'s '{key}' schema accepts a "
                f"range of lengths ({length.min}-{length.max}); replace it "
                "with vol.Any(vol.Length(x), vol.Length(y), ...) using the "
                "exact lengths observed in tests/samples/responses.py"
            )
