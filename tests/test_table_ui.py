"""Tests for the presentation-only table preparation helpers."""

import pandas as pd

from src.ui.components import (
    _build_table_payload,
    _paginate_table_frame,
    _sort_table_frame,
)


def test_table_sorting_uses_numeric_and_text_dtypes() -> None:
    numeric = pd.DataFrame({"value": [10, 2, 1]})
    text = pd.DataFrame({"value": ["10", "2", "1"]})

    assert _sort_table_frame(numeric, "value", "asc")["value"].tolist() == [1, 2, 10]
    assert _sort_table_frame(text, "value", "asc")["value"].tolist() == ["1", "10", "2"]


def test_table_sorting_keeps_nulls_last_in_both_directions() -> None:
    frame = pd.DataFrame({"value": [2.0, None, 1.0]})

    ascending = _sort_table_frame(frame, "value", "asc")["value"].tolist()
    descending = _sort_table_frame(frame, "value", "desc")["value"].tolist()

    assert ascending[:2] == [1.0, 2.0]
    assert pd.isna(ascending[-1])
    assert descending[:2] == [2.0, 1.0]
    assert pd.isna(descending[-1])


def test_table_pagination_clamps_to_valid_boundaries() -> None:
    frame = pd.DataFrame({"value": range(23)})

    first, page, total_pages, start, end = _paginate_table_frame(frame, 0, 10)
    assert (page, total_pages, start, end) == (1, 3, 1, 10)
    assert first["value"].tolist() == list(range(10))

    last, page, total_pages, start, end = _paginate_table_frame(frame, 99, 10)
    assert (page, total_pages, start, end) == (3, 3, 21, 23)
    assert last["value"].tolist() == [20, 21, 22]


def test_empty_table_payload_has_friendly_state() -> None:
    payload = _build_table_payload(pd.DataFrame(columns=["name"]), theme={})

    assert payload["empty"] is True
    assert payload["rows"] == []
    assert payload["showing_text"] == "Showing 0 to 0 of 0 entries"
    assert payload["empty_message"] == "No records match the current filters"


def test_table_payload_escapes_script_markup() -> None:
    payload = _build_table_payload(
        pd.DataFrame({"comment": ["<script>alert('x')</script>"]}),
        theme={},
    )

    rendered = payload["rows"][0][0]
    assert "<script>" not in rendered
    assert "&lt;script&gt;" in rendered
    assert "&#x27;x&#x27;" in rendered


def test_table_helpers_do_not_modify_original_dataframe() -> None:
    original = pd.DataFrame({"value": [3, 1, 2], "label": ["c", "a", "b"]})
    expected = original.copy(deep=True)

    _build_table_payload(
        original,
        sort_column="value",
        sort_direction="asc",
        page=1,
        page_size=10,
        theme={},
    )

    pd.testing.assert_frame_equal(original, expected)
