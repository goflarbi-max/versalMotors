"""Phase 0 golden-baseline and future API parity gates."""

from __future__ import annotations

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
    # This field records the source commit that Phase 0 captured. It is immutable
    # provenance, not a value expected to follow HEAD through later phases.
    actual["metadata"]["source_git_commit"] = expected["metadata"]["source_git_commit"]
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


def test_phase_one_backend_parity_gate_is_implemented() -> None:
    """The full endpoint matrix is exercised in backend/tests/test_overview_api.py."""
    from backend.app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/overview/kpis" in paths
    assert "/api/v1/overview/revenue-trend" in paths
    assert "/api/v1/overview/revenue-by-branch" in paths
    assert "/api/v1/overview/margin-by-model" in paths
