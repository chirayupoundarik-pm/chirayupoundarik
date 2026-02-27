"""
OpenTelemetry Latency Demo

Simulates a small micro-service architecture with three operations:
  - api.request     — fast, normally distributed (~30 ms mean)
  - db.query        — moderate, log-normal tail (~60 ms mean)
  - cache.lookup    — very fast with occasional misses (~5 ms mean, spike to ~100 ms)

Runs N requests through the in-memory OTel pipeline, then prints a full
latency report with p50 / p95 / p99 breakdowns.

Usage:
    python demo_otel.py              # 500 requests (default)
    python demo_otel.py --count 200  # custom count
"""

from __future__ import annotations

import argparse
import random
import time

from otel_ingestion import clear_spans, get_finished_spans, record_span, spans_to_records
from latency_analyzer import print_report


# ---------------------------------------------------------------------------
# Latency generators (deterministic seed → reproducible results)
# ---------------------------------------------------------------------------

def _api_latency_ms(rng: random.Random) -> float:
    """Normal distribution centered at 30 ms with occasional slow tail."""
    base = max(5.0, rng.gauss(30, 10))
    # ~5 % of requests are slow (e.g. cold-start, GC pause)
    if rng.random() < 0.05:
        base += rng.uniform(100, 300)
    return base


def _db_latency_ms(rng: random.Random) -> float:
    """Log-normal — represents query plans with long tail."""
    # log-normal: mu=4 (≈54 ms median), sigma=0.5
    return rng.lognormvariate(4.0, 0.5)


def _cache_latency_ms(rng: random.Random) -> float:
    """Cache hit (~2 ms) vs cache miss (~80 ms), miss rate 10 %."""
    if rng.random() < 0.10:
        return rng.uniform(60, 120)   # cache miss
    return rng.uniform(1, 5)          # cache hit


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------

def simulate(count: int = 500, seed: int = 42) -> None:
    rng = random.Random(seed)
    clear_spans()

    print(f"\nSimulating {count} requests across 3 operations …")

    for i in range(count):
        # Each "request" touches cache → db → api handler (nested spans)
        with record_span("api.request", attributes={"http.method": "GET", "request.id": str(i)}) as api_span:
            time.sleep(_api_latency_ms(rng) / 1_000)

            with record_span("cache.lookup", attributes={"cache.key": f"user:{i % 100}"}):
                time.sleep(_cache_latency_ms(rng) / 1_000)

            with record_span("db.query", attributes={"db.statement": "SELECT * FROM users WHERE id = ?"}):
                time.sleep(_db_latency_ms(rng) / 1_000)

    print(f"Collected {len(get_finished_spans())} spans.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="OTel latency demo")
    parser.add_argument("--count", type=int, default=500, help="Number of simulated requests")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed for reproducibility")
    args = parser.parse_args()

    simulate(count=args.count, seed=args.seed)

    records = spans_to_records(get_finished_spans())
    print_report(records, title=f"OTel Latency Report — {args.count} simulated requests")


if __name__ == "__main__":
    main()
