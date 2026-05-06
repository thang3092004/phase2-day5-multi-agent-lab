"""Writer agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.core.schemas import AgentResult, AgentName


class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer`.

        TODO(student): Synthesize a clear response with citations or source references.
        """

        # Produce a final answer by combining research and analysis using LLMClient mock.
        research = state.research_notes or ""
        analysis = state.analysis_notes or ""
        llm = LLMClient()
        system = "You are a helpful writer. Produce a concise final answer with citations when available."
        prompt = f"Research:\n{research}\n\nAnalysis:\n{analysis}\n\nPlease write a clear answer for the user."
        response = llm.complete(system_prompt=system, user_prompt=prompt)
        final = response.content
        state.final_answer = final

        state.agent_results.append(
            AgentResult(
                agent=AgentName.WRITER,
                content=final,
                metadata={
                    "output_tokens": response.output_tokens,
                    "cost_usd": response.cost_usd,
                },
            )
        )

        state.record_route(self.name)
        state.add_trace_event("writer_run", {"final_len": len(final)})
        return state
