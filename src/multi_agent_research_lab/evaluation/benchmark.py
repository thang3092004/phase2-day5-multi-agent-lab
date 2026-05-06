"""Benchmark skeleton for single-agent vs multi-agent."""

from time import perf_counter
from typing import Callable

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState


Runner = Callable[[str], ResearchState]


def run_benchmark(run_name: str, query: str, runner: Runner) -> tuple[ResearchState, BenchmarkMetrics]:
    """Measure latency and return a placeholder metric object.

    TODO(student): Add quality scoring, estimated token cost, citation coverage, and error rate.
    """

    started = perf_counter()
    state = runner(query)
    latency = perf_counter() - started

    # Estimate cost from agent metadata where available
    estimated_cost = 0.0
    total_token_est = 0
    for ar in state.agent_results:
        meta = ar.metadata or {}
        if meta.get("cost_usd"):
            estimated_cost += float(meta["cost_usd"])
        else:
            # try to estimate from tokens
            toks = meta.get("input_tokens") or meta.get("output_tokens")
            if toks:
                total_token_est += int(toks)

    if estimated_cost == 0.0 and total_token_est:
        estimated_cost = float(total_token_est) * 0.000002

    # Quality heuristic: prefer longer final answers and presence of analysis
    quality = None
    final = state.final_answer or ""
    word_count = len(final.split())
    if word_count > 400:
        quality = 9.0
    elif word_count > 200:
        quality = 7.0
    elif word_count > 50:
        quality = 5.0
    else:
        quality = 3.0

    # Citation coverage: fraction of sources used
    citation_coverage = 0.0
    if state.request and state.request.max_sources:
        citation_coverage = len(state.sources) / float(state.request.max_sources)

    error_rate = len(state.errors) / max(1, len(state.agent_results))

    notes = f"citation_coverage={citation_coverage:.2f}; errors={len(state.errors)}"

    metrics = BenchmarkMetrics(
        run_name=run_name,
        latency_seconds=latency,
        estimated_cost_usd=estimated_cost,
        quality_score=quality,
        notes=notes,
    )

    return state, metrics
