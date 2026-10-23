"""Phase 0 golden-baseline and future API parity gates."""

from __future__ import annotations

import importlib.util

import pytest

from tests.parity_support import (
    assert_nested_equal,
    capture_current_baseline,
    capture_direct_sql_verification,
    load_baseline,
)


def test_committed_baseline_matches_current_public_functions() -> None:
    """The committed baseline must move only through an intentional regeneration."""
    expected = load_baseline()
    actual = capture_current_baseline()
    assert_nested_equal(actual, expected)


def test_every_baseline_business_number_matches_direct_sql() -> None:
    """Independently verify Overview, Ask, Brief, and Data Quality numbers."""
    expected = load_baseline()
    sql_actual = capture_direct_sql_verification()
    for section in (
        "scenarios",
        "investigate",
        "ask_the_business",
        "management_brief",
        "data_quality",
    ):
        assert_nested_equal(sql_actual[section], expected[section], path=section)


@pytest.mark.skipif(
    importlib.util.find_spec("backend") is None,
    reason="FastAPI backend is introduced in Phase 1; Phase 0 preserves the contract.",
)
def test_future_api_matches_committed_baseline() -> None:
    """Phase 1 replaces this skip with TestClient calls for every API endpoint."""
    pytest.fail("Phase 1 must implement API TestClient parity assertions")
