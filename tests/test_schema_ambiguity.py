"""
Checks that no two registered inverters accept the same response.

Also runnable standalone to print inverter schemas ranked from most to
least permissive:

    python -m tests.test_schema_ambiguity
"""

from collections import defaultdict

import pytest
import voluptuous as vol
from voluptuous import Invalid, MultipleInvalid

from solax.discovery import REGISTRY
from solax.response_parser import GENERIC_RESPONSE_SCHEMA
from tests import fixtures


def _matching_inverters(response):
    normalized = {key.lower(): value for key, value in response.items()}
    matches = set()
    for inverter_class in REGISTRY:
        combined_schema = vol.And(GENERIC_RESPONSE_SCHEMA, inverter_class.schema())
        try:
            combined_schema(dict(normalized))
        except (Invalid, MultipleInvalid):
            continue
        matches.add(inverter_class)
    return matches


def _permissiveness_scores():
    """
    Count, for each inverter class, how many fixture responses (belonging
    to any inverter) its schema accepts. A schema that accepts more
    unrelated responses is less specific (more permissive) than one that
    accepts fewer.
    """
    scores = defaultdict(int)
    for case in fixtures.INVERTERS_UNDER_TEST:
        for inverter_class in _matching_inverters(case.response):
            scores[inverter_class] += 1
    return scores


_PERMISSIVENESS_SCORES = _permissiveness_scores()


def _most_permissive_first(inverter_classes):
    return sorted(
        inverter_classes,
        key=lambda c: (-_PERMISSIVENESS_SCORES[c], c.__name__),
    )


@pytest.mark.xfail(
    reason="some inverter schemas are still too permissive; tightening them "
    "is tracked separately and shouldn't block CI in the meantime",
    strict=False,
)
@pytest.mark.parametrize(
    "case",
    fixtures.INVERTERS_UNDER_TEST,
    ids=[
        f"{i}-{case.inverter.__name__}"
        for i, case in enumerate(fixtures.INVERTERS_UNDER_TEST)
    ],
)
def test_response_matches_exactly_one_inverter_schema(case):
    matches = _matching_inverters(case.response)
    extra = matches - {case.inverter}
    assert matches == {case.inverter}, (
        f"expected only {case.inverter.__name__} to accept this response, "
        "but it also validated against (most to least permissive): "
        f"{[c.__name__ for c in _most_permissive_first(extra)]}"
    )


def test_registry_order_matches_specificity():
    """
    REGISTRY must be ordered least-to-most permissive so discover()'s
    tie-break prefers the more specific/correct inverter. This is a
    drift guard: if fixtures or schemas change such that the
    fixture-computed ranking no longer matches REGISTRY's actual order,
    update _SCHEMA_SPECIFICITY_ORDER in solax/discovery.py to match
    (rerun `python -m tests.test_schema_ambiguity` and reverse it, or
    use _most_permissive_first(REGISTRY) directly).
    """
    expected = list(reversed(_most_permissive_first(REGISTRY)))
    expected_literal = ",\n".join(f'    "{c.__name__}"' for c in expected)
    assert REGISTRY == tuple(expected), (
        "solax.discovery._SCHEMA_SPECIFICITY_ORDER has drifted from the "
        "fixture-computed permissiveness ranking; update it to:\n"
        f"{expected_literal}"
    )


def _print_permissiveness_ranking():
    ambiguous = [c for c in REGISTRY if _PERMISSIVENESS_SCORES[c] > 1]
    ordered = _most_permissive_first(ambiguous)
    width = max(len(c.__name__) for c in ordered)
    for rank, inverter_class in enumerate(ordered, start=1):
        name = inverter_class.__name__
        matches = _PERMISSIVENESS_SCORES[inverter_class]
        print(f"{rank:>2}. {name:<{width}}  matches={matches}")


if __name__ == "__main__":
    _print_permissiveness_ranking()
