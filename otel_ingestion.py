"""
OpenTelemetry Ingestion Module

Sets up an in-memory OpenTelemetry pipeline that collects finished spans
so latency analysis can be run without an external collector.
"""

from __future__ import annotations

import functools
import time
from contextlib import contextmanager
from typing import Any, Generator, Optional

from opentelemetry import trace
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

# ---------------------------------------------------------------------------
# Global in-memory pipeline
# ---------------------------------------------------------------------------

_exporter = InMemorySpanExporter()
_provider = TracerProvider()
_provider.add_span_processor(SimpleSpanProcessor(_exporter))
trace.set_tracer_provider(_provider)


def get_tracer(name: str = "otel-latency-demo") -> trace.Tracer:
    """Return a tracer bound to the in-memory pipeline."""
    return trace.get_tracer(name)


def get_finished_spans() -> tuple[ReadableSpan, ...]:
    """Return all spans collected since the last :func:`clear_spans` call."""
    return _exporter.get_finished_spans()


def clear_spans() -> None:
    """Discard all collected spans (useful between test runs)."""
    _exporter.clear()


# ---------------------------------------------------------------------------
# Convenience helpers
# ---------------------------------------------------------------------------

@contextmanager
def record_span(
    operation: str,
    tracer_name: str = "otel-latency-demo",
    attributes: Optional[dict[str, Any]] = None,
) -> Generator[trace.Span, None, None]:
    """Context manager that wraps a block of code in an OTel span.

    Example::

        with record_span("db.query", attributes={"db.table": "users"}) as span:
            result = db.execute(query)
    """
    tracer = get_tracer(tracer_name)
    with tracer.start_as_current_span(operation) as span:
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)
        yield span


def instrument(operation: str, tracer_name: str = "otel-latency-demo"):
    """Decorator that wraps a function in an OTel span named *operation*.

    Example::

        @instrument("payment.process")
        def process_payment(amount):
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with record_span(operation, tracer_name=tracer_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# Span → dict helpers used by the analyzer
# ---------------------------------------------------------------------------

def spans_to_records(spans: tuple[ReadableSpan, ...]) -> list[dict[str, Any]]:
    """Convert finished OTel spans into plain dicts for easy analysis.

    Each record contains:
    - ``name``         – span operation name
    - ``duration_ms``  – wall-clock duration in milliseconds
    - ``start_time``   – UNIX timestamp (seconds) of span start
    - ``status``       – "OK" | "ERROR" | "UNSET"
    - ``attributes``   – dict of span attributes
    """
    records = []
    for span in spans:
        if span.start_time is None or span.end_time is None:
            continue
        duration_ns = span.end_time - span.start_time
        records.append(
            {
                "name": span.name,
                "duration_ms": duration_ns / 1_000_000,
                "start_time": span.start_time / 1_000_000_000,
                "status": span.status.status_code.name,
                "attributes": dict(span.attributes or {}),
            }
        )
    return records
