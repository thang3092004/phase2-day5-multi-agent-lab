"""LangGraph workflow skeleton."""

import os
from datetime import datetime, timezone
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.core.config import get_settings
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
        settings = get_settings()
        langsmith_client = None
        root_run_id = None

        # Best-effort LangSmith run creation for dashboard visibility
        if settings.langsmith_api_key:
            try:
                from langsmith import Client

                langsmith_client = Client(api_key=settings.langsmith_api_key)
                root_run = langsmith_client.create_run(
                    name="multi-agent-workflow",
                    project_name=settings.langsmith_project,
                    inputs={"query": state.request.query},
                    run_type="chain",
                )
                root_run_id = getattr(root_run, "id", root_run)
            except Exception:
                langsmith_client = None
                root_run_id = None

        # Wrap entire workflow with tracing span
        with trace_span(
            "multi-agent-workflow",
            attributes={"query": state.request.query},
        ) as workflow_span:
            agents = self.build()
            current = state

            for agent in agents:
                child_run_id = None
                if langsmith_client and root_run_id:
                    try:
                        child_run = langsmith_client.create_run(
                            name=f"agent-{agent.name}",
                            project_name=settings.langsmith_project,
                            inputs={"agent": agent.name},
                            run_type="chain",
                            parent_run_id=root_run_id,
                        )
                        child_run_id = getattr(child_run, "id", child_run)
                    except Exception:
                        child_run_id = None

                with trace_span(
                    f"agent-{agent.name}",
                    attributes={"agent": agent.name},
                ) as agent_span:
                    current = agent.run(current)

                if langsmith_client and child_run_id:
                    try:
                        output_text = (
                            current.final_answer
                            or current.analysis_notes
                            or current.research_notes
                            or ""
                        )
                        langsmith_client.update_run(
                            child_run_id,
                            outputs={
                                "agent": agent.name,
                                "output": output_text,
                                "final_answer": current.final_answer or "",
                                "analysis_notes": current.analysis_notes or "",
                                "research_notes": current.research_notes or "",
                            },
                            end_time=datetime.now(timezone.utc),
                        )
                    except Exception:
                        pass

            if langsmith_client and root_run_id:
                try:
                    langsmith_client.update_run(
                        root_run_id,
                        outputs={
                            "output": current.final_answer or "",
                            "final_answer": current.final_answer or "",
                            "final_answer_len": len(current.final_answer or ""),
                            "analysis_notes": current.analysis_notes or "",
                            "research_notes": current.research_notes or "",
                        },
                        end_time=datetime.now(timezone.utc),
                    )
                except Exception:
                    pass

            return current
