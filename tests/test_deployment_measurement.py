from deployment.measure_api import percentile


def test_percentile_is_stable_at_boundaries() -> None:
    values = [40.0, 10.0, 30.0, 20.0]
    assert percentile(values, 0.0) == 10.0
    assert percentile(values, 0.5) == 30.0
    assert percentile(values, 0.95) == 40.0
    assert percentile([], 0.95) == 0.0
