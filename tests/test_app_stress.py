"""Whole-application resilience and performance smoke tests."""

from pathlib import Path
from time import perf_counter

from streamlit.testing.v1 import AppTest


APP = Path(__file__).resolve().parents[1] / "app.py"


def test_data_quality_page_loads_and_cached_rerun_is_fast():
    app = AppTest.from_file(APP, default_timeout=30).run()
    start = perf_counter()
    app.switch_page("pages/data_quality.py").run()
    cold_seconds = perf_counter() - start
    assert not app.exception

    start = perf_counter()
    app.run()
    cached_seconds = perf_counter() - start
    assert not app.exception
    assert cached_seconds < cold_seconds
    assert cached_seconds < 5.0
