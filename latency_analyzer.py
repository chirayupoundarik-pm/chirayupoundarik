"""
Latency Analyzer

Computes percentile latency statistics (p50, p95, p99) from OpenTelemetry
span records collected by otel_ingestion.  No third-party math libraries
required — percentiles are computed with linear interpolation.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

# ---------------------------------------------------------------------------
# Pure-Python percentile (linear interpolation, same as numpy default)
# ---------------------------------------------------------------------------

def _percentile(sorted_data: list[float], p: float) -> float:
    """Return the *p*-th percentile of *sorted_data* using linear interpolation."""
    n = len(sorted_data)
    if n == 0:
        return 0.0
    if n == 1:
        return sorted_data[0]
    idx = (p / 100.0) * (n - 1)
    lower = int(idx)
    upper = lower + 1
    if upper >= n:
        return sorted_data[-1]
    frac = idx - lower
    return sorted_data[lower] + frac * (sorted_data[upper] - sorted_data[lower])


# ---------------------------------------------------------------------------
# Core analysis
# ---------------------------------------------------------------------------

def compute_stats(durations_ms: list[float]) -> dict[str, float]:
    """Return a dict of latency statistics for a list of durations (ms)."""
    if not durations_ms:
        return {}
    s = sorted(durations_ms)
    total = sum(s)
    n = len(s)
    return {
        "count": n,
        "min_ms": s[0],
        "max_ms": s[-1],
        "mean_ms": total / n,
        "p50_ms": _percentile(s, 50),
        "p95_ms": _percentile(s, 95),
        "p99_ms": _percentile(s, 99),
    }


def analyze(
    records: list[dict[str, Any]],
    group_by: str = "name",
) -> dict[str, dict[str, float]]:
    """Analyze latency from span records produced by :func:`otel_ingestion.spans_to_records`.

    Args:
        records:  List of span dicts (each must have ``duration_ms`` and the
                  field named by *group_by*).
        group_by: Key used to bucket spans — ``"name"`` (default) groups by
                  operation name; any span attribute key also works when the
                  attribute is stored in ``record["attributes"]``.

    Returns:
        A dict mapping group → stats dict (see :func:`compute_stats`).
    """
    buckets: dict[str, list[float]] = defaultdict(list)

    for rec in records:
        if group_by == "name":
            key = rec.get("name", "unknown")
        else:
            key = rec.get("attributes", {}).get(group_by, "unknown")
        buckets[key].append(rec["duration_ms"])

    return {key: compute_stats(vals) for key, vals in sorted(buckets.items())}


def analyze_overall(records: list[dict[str, Any]]) -> dict[str, float]:
    """Return aggregate stats across all spans regardless of operation name."""
    return compute_stats([r["duration_ms"] for r in records])


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

_COL = 14  # column width for numbers


def _fmt(value: float, decimals: int = 2) -> str:
    return f"{value:.{decimals}f}"


def print_report(
    records: list[dict[str, Any]],
    title: str = "Latency Report",
) -> None:
    """Print a formatted latency report to stdout.

    Shows per-operation stats followed by an overall summary row.
    The p95 column is highlighted with an arrow for quick scanning.
    """
    per_op = analyze(records)
    overall = analyze_overall(records)

    header = f"{'Operation':<35} {'Count':>{_COL}} {'Min':>{_COL}} {'Mean':>{_COL}} {'P50':>{_COL}} {'P95 -->':>{_COL}} {'P99':>{_COL}} {'Max':>{_COL}}"
    sep = "-" * len(header)

    print()
    print(f"  {title}")
    print(f"  {sep}")
    print(f"  {header}")
    print(f"  {sep}")

    for op, stats in per_op.items():
        print(
            f"  {op:<35}"
            f" {int(stats['count']):>{_COL}}"
            f" {_fmt(stats['min_ms']):>{_COL}}"
            f" {_fmt(stats['mean_ms']):>{_COL}}"
            f" {_fmt(stats['p50_ms']):>{_COL}}"
            f" {_fmt(stats['p95_ms']):>{_COL}}"
            f" {_fmt(stats['p99_ms']):>{_COL}}"
            f" {_fmt(stats['max_ms']):>{_COL}}"
        )

    print(f"  {sep}")
    print(
        f"  {'OVERALL':<35}"
        f" {int(overall['count']):>{_COL}}"
        f" {_fmt(overall['min_ms']):>{_COL}}"
        f" {_fmt(overall['mean_ms']):>{_COL}}"
        f" {_fmt(overall['p50_ms']):>{_COL}}"
        f" {_fmt(overall['p95_ms']):>{_COL}}"
        f" {_fmt(overall['p99_ms']):>{_COL}}"
        f" {_fmt(overall['max_ms']):>{_COL}}"
    )
    print(f"  {sep}")
    print(f"  All durations in milliseconds (ms)")
    print()

    # Highlight p95 violations
    threshold_ms = overall["p95_ms"]
    slow_ops = [
        (op, stats)
        for op, stats in per_op.items()
        if stats["p95_ms"] > threshold_ms * 1.5
    ]
    if slow_ops:
        print("  Operations with p95 > 1.5x overall p95 (potential bottlenecks):")
        for op, stats in slow_ops:
            print(f"    - {op}: p95 = {_fmt(stats['p95_ms'])} ms")
        print()
