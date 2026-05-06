"""Supervisor / router skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.core.config import get_settings




class SupervisorAgent(BaseAgent):
    """Decides which worker should run next and when to stop."""

    name = "supervisor"

    def run(self, state: ResearchState) -> ResearchState:
        """Update `state.route_history` with the next route.

        The routing policy implemented here is simple and deterministic:
        - If there are no `research_notes` -> route to `researcher`.
        - Else if there are research notes but no `analysis_notes` -> route to `analyst`.
        - Else if there is analysis but no `final_answer` -> route to `writer`.
        - Otherwise no-op (workflow considered complete).

        The method enforces `max_iterations` from settings by stopping routing when
        the state's `iteration` reaches the configured limit.
        """

        settings = get_settings()
        # Respect guardrail
        if state.iteration >= settings.max_iterations:
            state.add_trace_event("supervisor", {"action": "max_iterations_reached"})
            return state

        # Decide next worker
        if not state.research_notes:
            next_route = "researcher"
        elif not state.analysis_notes:
            next_route = "analyst"
        elif not state.final_answer:
            next_route = "writer"
        else:
            # nothing to do
            state.add_trace_event("supervisor", {"action": "complete"})
            return state

        state.record_route(next_route)
        state.add_trace_event("supervisor", {"next": next_route})
        return state
