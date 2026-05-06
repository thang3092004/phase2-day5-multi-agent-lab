"""Search client abstraction for ResearcherAgent."""

from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import SourceDocument


class SearchClient:
    """Provider-agnostic search client skeleton."""

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search for documents relevant to a query.

        TODO(student): Implement with Tavily, Bing, SerpAPI, internal docs, or a local mock.
        """

        # Minimal local mock search that returns placeholder SourceDocument objects.
        results: list[SourceDocument] = []
        for i in range(1, max_results + 1):
            results.append(
                SourceDocument(
                    title=f"Mock result {i} for: {query}",
                    url=f"https://example.com/search/{i}",
                    snippet=f"This is a mocked snippet for '{query}' (result {i}).",
                    metadata={"rank": i},
                )
            )
        return results
