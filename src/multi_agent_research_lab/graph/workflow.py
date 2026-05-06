"""LangGraph workflow skeleton."""

import os
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.agents.researcher import ResearcherAgent
from multi_agent_research_lab.agents.analyst import AnalystAgent
from multi_agent_research_lab.agents.writer import WriterAgent
from multi_agent_research_lab.agents.critic import CriticAgent
from multi_agent_research_lab.observability.tracing import trace_span


class MultiAgentWorkflow:
    """Builds and runs the multi-agent graph.

    Keep orchestration here; keep agent internals in `agents/`.
    """

    def build(self) -> object:
        """Create a LangGraph graph.

        TODO(student): Implement nodes, edges, conditional routing, and stop condition.
        Suggested nodes: supervisor, researcher, analyst, writer, optional critic.
        """
        # For the starter implementation we return a simple sequence of agent instances.
        return [ResearcherAgent(), AnalystAgent(), WriterAgent(), CriticAgent()]

    def run(self, state: ResearchState) -> ResearchState:
        """Execute the graph and return final state.

        TODO(student): Compile graph, invoke it, and convert result back to ResearchState.
        """
        # Wrap entire workflow with tracing span
        with trace_span(
            "multi-agent-workflow",
            attributes={"query": state.request.query},
        ) as workflow_span:
            agents = self.build()
            current = state

            for agent in agents:
                with trace_span(
                    f"agent-{agent.name}",
                    attributes={"agent": agent.name},
                ) as agent_span:
                    current = agent.run(current)

            return current
