"""Run benchmark and save report."""
import sys
from time import perf_counter

from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.evaluation.benchmark import run_benchmark
from multi_agent_research_lab.evaluation.report import render_markdown_report
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow


def baseline_runner(query: str) -> ResearchState:
    """Single-agent baseline: just echoes the query."""
    request = ResearchQuery(query=query)
    state = ResearchState(request=request)
    state.final_answer = f"Baseline answer for: {query}"
    return state


def multiagent_runner(query: str) -> ResearchState:
    """Multi-agent workflow."""
    state = ResearchState(request=ResearchQuery(query=query))
    workflow = MultiAgentWorkflow()
    return workflow.run(state)


if __name__ == "__main__":
    test_query = "Explain multi-agent systems and their advantages"
    
    print("Running baseline...")
    baseline_state, baseline_metrics = run_benchmark("baseline", test_query, baseline_runner)
    
    print("Running multi-agent...")
    multiagent_state, multiagent_metrics = run_benchmark("multi-agent", test_query, multiagent_runner)
    
    # Render and save report
    report = render_markdown_report([baseline_metrics, multiagent_metrics])
    
    report_path = "reports/benchmark_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\n✅ Benchmark report saved to {report_path}")
    print("\n" + report)