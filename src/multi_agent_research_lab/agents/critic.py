"""Optional critic agent skeleton for bonus work."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState


class CriticAgent(BaseAgent):
    """Optional fact-checking and safety-review agent."""

    name = "critic"

    def run(self, state: ResearchState) -> ResearchState:
        """Validate final answer and append findings.

        TODO(student): Add fact-check, citation coverage, or hallucination checks.
        """

        # Basic critic that checks for overly short answers or missing citations.
        issues: list[str] = []
        final = state.final_answer or ""
        if not final:
            issues.append("final_answer is empty")
        if len(final.split()) < 20:
            issues.append("final_answer is very short")

        if issues:
            state.errors.extend(issues)

        state.record_route(self.name)
        state.add_trace_event("critic_run", {"issues": issues})
        return state
