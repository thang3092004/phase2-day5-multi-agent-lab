# Trace Example

## Query

"Explain multi-agent systems and their advantages"

## Execution Flow

### Agent execution sequence:
1. **Supervisor** → routes to "researcher" (no research_notes yet)
2. **Researcher** → fetches 5 sources, creates research_notes
3. **Supervisor** → routes to "analyst" (has research_notes but no analysis_notes)
4. **Analyst** → analyzes research_notes, creates analysis_notes
5. **Supervisor** → routes to "writer" (has research notes & analysis but no final_answer)
6. **Writer** → synthesizes final_answer with citations
7. **Critic** → checks final_answer quality (no issues found)
8. **Supervisor** → detects all done, workflow completes

---

## State Output (JSON format)

```json
{
  "request": {
    "query": "Explain multi-agent systems and their advantages",
    "max_sources": 5,
    "audience": "technical learners"
  },
  "iteration": 4,
  "route_history": ["researcher", "analyst", "writer", "critic"],
  "sources": [
    {
      "title": "Mock result 1 for: Explain multi-agent systems and their advantages",
      "url": "https://example.com/search/1",
      "snippet": "This is a mocked snippet for 'Explain multi-agent systems and their advantages' (result 1).",
      "metadata": {"rank": 1}
    },
    {
      "title": "Mock result 2 for: Explain multi-agent systems and their advantages",
      "url": "https://example.com/search/2",
      "snippet": "This is a mocked snippet for 'Explain multi-agent systems and their advantages' (result 2).",
      "metadata": {"rank": 2}
    },
    {
      "title": "Mock result 3 for: Explain multi-agent systems and their advantages",
      "url": "https://example.com/search/3",
      "snippet": "This is a mocked snippet for 'Explain multi-agent systems and their advantages' (result 3).",
      "metadata": {"rank": 3}
    },
    {
      "title": "Mock result 4 for: Explain multi-agent systems and their advantages",
      "url": "https://example.com/search/4",
      "snippet": "This is a mocked snippet for 'Explain multi-agent systems and their advantages' (result 4).",
      "metadata": {"rank": 4}
    },
    {
      "title": "Mock result 5 for: Explain multi-agent systems and their advantages",
      "url": "https://example.com/search/5",
      "snippet": "This is a mocked snippet for 'Explain multi-agent systems and their advantages' (result 5).",
      "metadata": {"rank": 5}
    }
  ],
  "research_notes": "Mock result 1 for: Explain multi-agent systems and their advantages: This is a mocked snippet...\n\nMock result 2 for: Explain multi-agent systems and their advantages: This is a mocked snippet...\n\n(etc., 5 sources concatenated)",
  "analysis_notes": "You are an analyst. Extract key claims and weaknesses.\n\nMock result 1 for: Explain multi-agent systems and their advantages: This is a mocked snippet...\n\n(analyst summary of the research notes)",
  "final_answer": "You are a helpful writer. Produce a concise final answer with citations when available.\n\nResearch:\n(research notes)\n\nAnalysis:\n(analysis notes)\n\nPlease write a clear answer for the user.",
  "agent_results": [
    {
      "agent": "researcher",
      "content": "(research notes concatenated from 5 sources)",
      "metadata": {
        "num_sources": 5
      }
    },
    {
      "agent": "analyst",
      "content": "(analysis summary)",
      "metadata": {
        "input_tokens": 163,
        "cost_usd": 0.000326
      }
    },
    {
      "agent": "writer",
      "content": "(final synthesized answer)",
      "metadata": {
        "output_tokens": 351,
        "cost_usd": 0.000702
      }
    }
  ],
  "trace": [
    {
      "name": "researcher_run",
      "payload": {
        "num_sources": 5
      }
    },
    {
      "name": "analyst_run",
      "payload": {
        "summary_len": 654
      }
    },
    {
      "name": "writer_run",
      "payload": {
        "final_len": 1406
      }
    },
    {
      "name": "critic_run",
      "payload": {
        "issues": []
      }
    },
    {
      "name": "supervisor",
      "payload": {
        "action": "complete"
      }
    }
  ],
  "errors": []
}
```

---

## Trace Analysis

### ✅ Success Metrics

| Metric | Value | Status |
|---|---|---|
| **Researcher** | Found 5 sources | ✅ Complete |
| **Analyst** | Analyzed 654 chars | ✅ Complete |
| **Writer** | Generated 1406 chars | ✅ Complete |
| **Critic** | 0 issues detected | ✅ Pass |
| **Total iterations** | 4 / max 6 | ✅ Safe (67% used) |
| **Errors** | 0 | ✅ No errors |
| **Latency** | ~0.5s | ✅ Fast (mock) |
| **Cost** | ~$0.001 | ✅ Cheap (mock cost) |

### 📊 Flow Diagram

```
START
  ↓
[Supervisor: No research_notes → Route RESEARCHER]
  ↓
[Researcher: Find 5 sources, create research_notes]
  ↓
[Supervisor: Has research_notes, no analysis → Route ANALYST]
  ↓
[Analyst: Analyze notes, create analysis_notes]
  ↓
[Supervisor: Has both notes, no final_answer → Route WRITER]
  ↓
[Writer: Synthesize final_answer with citations]
  ↓
[Critic: Check final_answer (0 issues)]
  ↓
[Supervisor: All done → STOP]
  ↓
END
```

### 📝 Key Observations

1. **Routing is deterministic** — each agent's output triggers next routing decision
2. **Shared state grows** — each agent adds to state without clearing (by design, for tracing)
3. **Cost tracking** — agent_results include token counts and cost estimates
4. **No loops** — supervisor enforces max_iterations=6, we only used 4
5. **Trace is rich** — each step recorded in `trace[]` for debugging

---

## How to Capture Your Own Trace

Run this command in PowerShell:

```powershell
python -m multi_agent_research_lab.cli multi-agent `
  --query "Your question here"
```

The CLI outputs the full state as JSON. Copy the output and save to a file:

```powershell
python -m multi_agent_research_lab.cli multi-agent `
  --query "Your question" | Out-File "my_trace.json"
```

Or run benchmark:

```powershell
python scripts/run_benchmark.py
```

This generates `reports/benchmark_report.md` with metrics.

