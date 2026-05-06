"""LLM client abstraction.

Production note: agents should depend on this interface instead of importing an SDK directly.
"""

from dataclasses import dataclass

from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.config import get_settings


@dataclass(frozen=True)
class LLMResponse:
    content: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None


class LLMClient:
    """Provider-agnostic LLM client skeleton."""

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Return a model completion.

        TODO(student): Connect OpenAI, Azure OpenAI, or another provider.
        Keep retry, timeout, and token logging here rather than inside agents.
        """

        settings = get_settings()

        if not settings.openai_api_key:
            raise StudentTodoError("OPENAI_API_KEY is required; no fallback is allowed.")

        try:
            from openai import OpenAI
        except Exception as exc:
            raise StudentTodoError("openai package is required; install with `pip install -e .[llm]`.") from exc

        client = OpenAI(api_key=settings.openai_api_key)
        model = settings.openai_model

        try:
            resp = client.responses.create(
                model=model,
                input=[
                    {"role": "system", "content": system_prompt or ""},
                    {"role": "user", "content": user_prompt or ""},
                ],
                timeout=settings.timeout_seconds,
            )
        except Exception as exc:
            raise StudentTodoError(f"OpenAI call failed: {exc}") from exc

        # Extract text
        content = ""
        if getattr(resp, "output_text", None):
            content = resp.output_text
        elif getattr(resp, "output", None):
            # Fallback to first output item content if available
            try:
                content = resp.output[0].content[0].text
            except Exception:
                content = ""

        usage = getattr(resp, "usage", None)
        input_tokens = getattr(usage, "input_tokens", None) if usage else None
        output_tokens = getattr(usage, "output_tokens", None) if usage else None
        total_tokens = getattr(usage, "total_tokens", None) if usage else None
        cost = None
        if total_tokens:
            cost = float(total_tokens) * 0.000002

        return LLMResponse(content=content, input_tokens=input_tokens, output_tokens=output_tokens, cost_usd=cost)
