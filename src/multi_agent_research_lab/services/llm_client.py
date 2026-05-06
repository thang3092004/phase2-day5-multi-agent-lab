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

        # If an OpenAI API key is configured and the openai package is available,
        # use the real API. Otherwise fall back to the local mock implementation.
        if settings.openai_api_key:
            try:
                import openai

                openai.api_key = settings.openai_api_key
                model = settings.openai_model
                resp = openai.ChatCompletion.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt or ""},
                        {"role": "user", "content": user_prompt or ""},
                    ],
                    timeout=settings.timeout_seconds,
                )
                # Extract text
                text = ""
                if resp and resp.choices:
                    first = resp.choices[0]
                    # Some SDKs return `message.content` for chat
                    if getattr(first, "message", None) is not None:
                        text = first.message.get("content", "")
                    else:
                        text = first.get("text", "")

                usage = resp.get("usage", {}) if isinstance(resp, dict) else getattr(resp, "usage", None) or {}
                total_tokens = usage.get("total_tokens") if isinstance(usage, dict) else None
                cost = None
                if total_tokens:
                    # very rough cost estimate (placeholder)
                    cost = float(total_tokens) * 0.000002

                input_tokens = total_tokens
                output_tokens = None
                return LLMResponse(content=text, input_tokens=input_tokens, output_tokens=output_tokens, cost_usd=cost)
            except Exception:
                # Fall back to mock on any import/runtime error
                pass

        # Fallback mock
        prompt = (system_prompt or "") + "\n\n" + (user_prompt or "")
        content = prompt.strip()

        # Very rough token estimate: 1 token ~= 4 chars
        token_estimate = max(1, len(content) // 4)
        # Tiny placeholder cost estimate
        cost = token_estimate * 0.000001

        return LLMResponse(content=content, input_tokens=token_estimate, output_tokens=token_estimate, cost_usd=cost)
