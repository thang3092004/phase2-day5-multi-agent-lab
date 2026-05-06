"""Analyst agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.core.schemas import AgentResult, AgentName


class AnalystAgent(BaseAgent):
    """Turns research notes into structured insights."""

    name = "analyst"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.analysis_notes`.

        TODO(student): Extract key claims, compare viewpoints, and flag weak evidence.
        """

        # Lightweight analyst: summarize research_notes using LLMClient mock.
        notes = state.research_notes or ""
        llm = LLMClient()
        system = "You are an analyst. Extract key claims and weaknesses."
        response = llm.complete(system_prompt=system, user_prompt=notes)
        analysis = response.content[:2000]
        state.analysis_notes = analysis

        state.agent_results.append(
            AgentResult(
                agent=AgentName.ANALYST,
                content=analysis,
                metadata={
                    "input_tokens": response.input_tokens,
                    "cost_usd": response.cost_usd,
                },
            )
        )

        state.record_route(self.name)
        state.add_trace_event("analyst_run", {"summary_len": len(analysis)})
        return state
