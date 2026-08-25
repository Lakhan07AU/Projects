"""Trend analysis engine.

Pure functions — no DB access. Given a series of (date, value) points, returns
direction / rate of change / stability / outlier signal with a confidence.
A trend is never labelled as a disease.
"""
import statistics
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TrendPoint:
    date: datetime
    value: float


@dataclass
class TrendResult:
    direction: str  # stable | increasing | decreasing | sudden_change | insufficient_data
    rate_of_change: float | None  # units per day (least-squares slope)
    stability: str  # stable | variable | highly_variable | unknown
    possible_outlier: bool
    confidence: float
    first_value: float | None = None
    last_value: float | None = None
    change_since_first: float | None = None
    data_points: int = 0

    def as_dict(self) -> dict:
        return {
            "direction": self.direction,
            "rate_of_change": self.rate_of_change,
            "stability": self.stability,
            "possible_outlier": self.possible_outlier,
            "confidence": self.confidence,
            "first_value": self.first_value,
            "last_value": self.last_value,
            "change_since_first": self.change_since_first,
            "data_points": self.data_points,
        }


def analyze_trend(points: list[TrendPoint], relative_sudden_change: float = 0.25) -> TrendResult:
    if len(points) < 2:
        return TrendResult(
            direction="insufficient_data", rate_of_change=None, stability="unknown",
            possible_outlier=False, confidence=0.5, last_value=points[0].value if points else None,
            data_points=len(points),
        )

    pts = sorted(points, key=lambda p: p.date)
    values = [p.value for p in pts]
    times = [p.date.timestamp() for p in pts]
    n = len(values)

    # Least-squares slope over time (units/day)
    mean_t = statistics.fmean(times)
    mean_v = statistics.fmean(values)
    denom = sum((t - mean_t) ** 2 for t in times)
    slope = (sum((t - mean_t) * (v - mean_v) for t, v in zip(times, values)) / denom) * 86400 if denom else 0.0

    # Relative variability
    stdev = statistics.pstdev(values) if n > 1 else 0.0
    rel_var = stdev / abs(mean_v) if mean_v else 0.0
    if rel_var < 0.05:
        stability = "stable"
        stab_conf = 0.9
    elif rel_var < 0.15:
        stability = "variable"
        stab_conf = 0.75
    else:
        stability = "highly_variable"
        stab_conf = 0.6

    # Outlier detection via modified z-score on residuals from the trend line
    predicted = [mean_v + (t - mean_t) * (slope / 86400) for t in times]
    residuals = [v - p for v, p in zip(values, predicted)]
    mad = statistics.median([abs(r - statistics.median(residuals)) for r in residuals]) or 1e-9
    possible_outlier = any(abs(0.6745 * r / mad) > 3.5 for r in residuals)

    # Direction decision combines slope significance with total change
    total_change = values[-1] - values[0]
    span_days = max((times[-1] - times[0]) / 86400, 1e-6)
    change_rate_total = abs(total_change) / max(abs(mean_v), 1e-9)

    if abs(total_change) < 1e-9 and abs(slope) < 1e-12:
        direction = "stable"
        conf = 0.85
    elif change_rate_total > relative_sudden_change and span_days < 30 and abs(slope) > 0:
        direction = "sudden_change"
        conf = 0.7
    elif abs(total_change) <= max(abs(mean_v) * 0.03, 1e-9):
        direction = "stable"
        conf = 0.8
    elif total_change > 0:
        direction = "increasing"
        conf = min(0.9, 0.55 + stab_conf * 0.4)
    else:
        direction = "decreasing"
        conf = min(0.9, 0.55 + stab_conf * 0.4)

    return TrendResult(
        direction=direction,
        rate_of_change=round(slope, 8),
        stability=stability,
        possible_outlier=possible_outlier,
        confidence=round(conf, 2),
        first_value=values[0],
        last_value=values[-1],
        change_since_first=round(total_change, 6),
        data_points=n,
    )
