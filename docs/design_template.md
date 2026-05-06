# Design Template

## Problem

Xây dựng một research assistant có khả năng:
- Nhận query dài từ user
- Tìm kiếm thông tin từ nhiều nguồn
- Phân tích và trích xuất insights
- Viết câu trả lời cuối cùng có chất lượng cao

Mục đích: So sánh hiệu suất single-agent vs multi-agent để hiểu khi nào nên dùng orchestration.

## Why multi-agent?

**Single-agent chưa đủ vì:**
- Một agent phải xử lý tất cả logic (search, analysis, writing) → dễ bị overloaded
- Khó debug từng bước → nếu output sai, không biết agent nào phải chịu trách nhiệm
- Khó optimize từng phần → nếu muốn search tốt hơn, phải retrain toàn bộ model
- Khó trace → không rõ agent dành bao lâu cho search vs writing

**Multi-agent giải quyết bằng:**
- Mỗi agent có trách nhiệm rõ → dễ test và improve từng phần
- Routing decision rõ ràng → có thể kiểm soát luồng công việc
- Shared state → dễ debug vì mọi output đều được lưu
- Trace chi tiết → có thể thấy ai mất thời gian, ai mất chi phí

## Agent roles

| Agent | Responsibility | Input | Output | Failure mode |
|---|---|---|---|---|
| Supervisor | Quyết định bước tiếp theo, enforce max_iterations | request, current state | route (researcher/analyst/writer/done) | Vòng lặp vô hạn nếu routing logic sai |
| Researcher | Tìm thông tin từ web/DB, tổng hợp sources | query | sources[], research_notes | Không tìm được sources, hoặc sources không relevant |
| Analyst | Phân tích research notes, trích xuất claims | research_notes | analysis_notes | Analysis quá surface-level, miss insights |
| Writer | Tổng hợp thành final answer có citations | research_notes + analysis_notes | final_answer | Answer quá ngắn, citations không đúng |

## Shared state

**Fields cần thiết:**

| Field | Lý do |
|---|---|
| `request: ResearchQuery` | Lưu original query + metadata (max_sources, audience) |
| `sources: list[SourceDocument]` | Researcher tìm được sources gì → Writer có thể cite |
| `research_notes: str` | Output của Researcher → Analyst dùng để analysis |
| `analysis_notes: str` | Output của Analyst → Writer dùng để synthesis |
| `final_answer: str` | Output cuối cùng → user nhận được |
| `iteration: int` | Đếm lần routing → enforce max_iterations |
| `route_history: list[str]` | Trace ai đã chạy (researcher, analyst, writer, ...) |
| `trace: list[dict]` | Chi tiết mỗi bước (name, payload, duration) |
| `errors: list[str]` | Nếu agent fail, ghi lỗi vào đây |

## Routing policy

```
START
  ↓
SUPERVISOR checks state:
  - If no research_notes → route to RESEARCHER
  - Else if no analysis_notes → route to ANALYST
  - Else if no final_answer → route to WRITER
  - Else → mark DONE
  ↓
If iteration < max_iterations: run routed agent, go back to SUPERVISOR
Else: return final state
  ↓
END
```

## Guardrails

- **Max iterations:** 6 (configurable via `MAX_ITERATIONS` env var) — enforce in SupervisorAgent
- **Timeout:** 60 seconds (configurable via `TIMEOUT_SECONDS` env var) — enforced at run() level
- **Retry:** None (simplified; could add exponential backoff for failed agents)
- **Fallback:** If OpenAI API fails, use mock LLM implementation; if SearchClient fails, return empty sources
- **Validation:** Each agent checks input is not None before processing; supervisor checks iteration < max_iterations

## Benchmark plan

| Query | Metric | Baseline | Multi-Agent | Expected Winner |
|---|---|---|---|---|
| "Explain multi-agent systems" | Latency (s) | ~0.1 | ~0.3 | Baseline (fewer calls) |
| ^ | Cost ($) | ~$0.0001 | ~$0.0005 | Baseline (1 agent vs 4) |
| ^ | Quality (0-10) | 3-5 | 7-9 | Multi-agent (specialized agents) |
| ^ | Citation coverage | 0% | 80%+ | Multi-agent (Researcher finds sources) |
| ^ | Error rate | 0% | 0% | Tie (both implement errors list) |
| "Research GraphRAG vs RAG" | Latency (s) | ~0.1 | ~0.5 | Baseline |
| ^ | Quality (0-10) | 4-6 | 8-10 | Multi-agent (deeper analysis) |
| ^ | Citation coverage | 0% | 90%+ | Multi-agent (has research phase) |
