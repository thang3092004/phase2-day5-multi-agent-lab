"""Researcher agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.search_client import SearchClient
from multi_agent_research_lab.core.schemas import AgentResult, AgentName


class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.sources` and `state.research_notes`.

        TODO(student): Implement search, source filtering, citation capture, and notes.
        """

        # Simple researcher implementation using the local SearchClient mock.
        searcher = SearchClient()
        max_results = state.request.max_sources
        sources = searcher.search(state.request.query, max_results=max_results)

        state.sources = sources

        notes = "\n\n".join([f"{s.title}: {s.snippet}" for s in sources])
        state.research_notes = notes

        state.agent_results.append(
            AgentResult(agent=AgentName.RESEARCHER, content=notes, metadata={"num_sources": len(sources)})
        )

        state.record_route(self.name)
        state.add_trace_event("researcher_run", {"num_sources": len(sources)})
        return state
