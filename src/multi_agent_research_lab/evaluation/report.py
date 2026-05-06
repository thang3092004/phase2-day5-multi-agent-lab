"""Benchmark report rendering."""

from multi_agent_research_lab.core.schemas import BenchmarkMetrics


def render_markdown_report(metrics: list[BenchmarkMetrics]) -> str:
    """Render benchmark metrics to markdown.

    TODO(student): Add richer analysis, examples, screenshots, and trace links.
    """
    lines = ["# Benchmark Report", "", "| Run | Latency (s) | Cost (USD) | Quality | Notes |", "|---|---:|---:|---:|---|"]
    for item in metrics:
        cost = "" if item.estimated_cost_usd is None else f"{item.estimated_cost_usd:.4f}"
        quality = "" if item.quality_score is None else f"{item.quality_score:.1f}"
        notes = item.notes or ""
        lines.append(f"| {item.run_name} | {item.latency_seconds:.2f} | {cost} | {quality} | {notes} |")

    # Summary section
    lines.append("")
    lines.append("## Summary")
    avg_latency = sum([m.latency_seconds for m in metrics]) / max(1, len(metrics))
    lines.append(f"- Average latency: {avg_latency:.2f}s")
    total_cost = sum([m.estimated_cost_usd or 0.0 for m in metrics])
    lines.append(f"- Total estimated cost: ${total_cost:.4f}")

    return "\n".join(lines) + "\n"
