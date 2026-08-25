"""Trend engine unit tests."""
from datetime import datetime, timedelta

from app.services.trends import TrendPoint, analyze_trend


def base_date():
    return datetime(2026, 1, 1)


def test_insufficient_data():
    result = analyze_trend([TrendPoint(base_date(), 5.6)])
    assert result.direction == "insufficient_data"


def test_stable_series():
    points = [TrendPoint(base_date() + timedelta(days=7 * i), 5.5 + (i % 2) * 0.05) for i in range(6)]
    result = analyze_trend(points)
    assert result.direction == "stable"
    assert result.stability in ("stable", "variable")


def test_increasing_series():
    values = [70.0, 71.0, 72.5, 74.0, 76.0]
    points = [TrendPoint(base_date() + timedelta(days=14 * i), v) for i, v in enumerate(values)]
    result = analyze_trend(points)
    assert result.direction == "increasing"
    assert result.rate_of_change > 0
    assert result.change_since_first == pytest_approx(values[-1] - values[0])


def test_decreasing_series():
    values = [80.0, 78.0, 76.5, 74.0, 72.0]
    points = [TrendPoint(base_date() + timedelta(days=10 * i), v) for i, v in enumerate(values)]
    result = analyze_trend(points)
    assert result.direction == "decreasing"
    assert result.rate_of_change < 0


def test_sudden_change_detected():
    # long stable stretch then a jump
    values = [100.0] * 6 + [130.0]
    points = [TrendPoint(base_date() + timedelta(days=i), v) for i, v in enumerate(values)]
    result = analyze_trend(points)
    assert result.direction in ("sudden_change", "increasing")


def test_outlier_flagged():
    values = [100.0, 101.0, 100.5, 160.0, 100.2, 99.8]
    points = [TrendPoint(base_date() + timedelta(days=i * 7), v) for i, v in enumerate(values)]
    result = analyze_trend(points)
    assert result.possible_outlier is True


def test_never_labels_disease():
    """Direction vocabulary must stay non-diagnostic."""
    allowed = {"stable", "increasing", "decreasing", "sudden_change", "insufficient_data"}
    values = [1, 2, 3, 4, 5]
    points = [TrendPoint(base_date() + timedelta(days=i), float(v)) for i, v in enumerate(values)]
    assert analyze_trend(points).direction in allowed


def pytest_approx(value):
    class _Approx:
        def __eq__(self, other):
            return abs(other - value) < 1e-6

        def __repr__(self):
            return f"approx({value})"

    return _Approx()
