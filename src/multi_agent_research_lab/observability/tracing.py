"""Tracing hooks.

This file intentionally avoids binding to one provider. Students can plug in LangSmith,
Langfuse, OpenTelemetry, or simple JSON traces.
"""

import os
from collections.abc import Iterator
from contextlib import contextmanager
from time import perf_counter
from typing import Any

from multi_agent_research_lab.core.config import get_settings


@contextmanager
def trace_span(name: str, attributes: dict[str, Any] | None = None) -> Iterator[dict[str, Any]]:
    """Minimal span context used by the skeleton.

    If LangSmith is configured, uses LangSmith client for tracing.
    Otherwise falls back to local timing span.
    """

    settings = get_settings()
    started = perf_counter()
    span: dict[str, Any] = {"name": name, "attributes": attributes or {}, "duration_seconds": None}

    # Try to use LangSmith if configured
    if settings.langsmith_api_key and os.environ.get("LANGSMITH_TRACING") == "true":
        try:
            from langsmith import Client

            client = Client(api_key=settings.langsmith_api_key)
            with client.span(
                name=name,
                inputs=attributes or {},
                project_name=settings.langsmith_project,
            ) as provider_span:
                span["provider"] = "langsmith"
                span["span_id"] = str(provider_span.id) if hasattr(provider_span, "id") else None
                yield span
            span["duration_seconds"] = perf_counter() - started
            return
        except Exception as e:
            # Fall through to local span on any error
            pass

    # Fallback: local timing span
    try:
        yield span
    finally:
        span["duration_seconds"] = perf_counter() - started
