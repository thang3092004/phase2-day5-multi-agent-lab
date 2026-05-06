# Failure Modes and Fixes

## Case 1: LLM API không khả dụng (OPENAI_API_KEY missing)

**Khi nào fail:** Nếu chưa set `OPENAI_API_KEY` trong `.env`

**Lý do:** LLMClient cố gọi OpenAI API nhưng không có key

**Cách fix:** 
- Mở `.env` và điền `OPENAI_API_KEY=sk-...` 
- Hoặc để trống, code sẽ fallback sang mock implementation (hiện tại không gọi API ngoài)

---

## Case 2: Workflow vượt quá max_iterations

**Khi nào fail:** Query quá phức tạp, supervisor router chưa quyết định dừng

**Lý do:** `max_iterations` (mặc định=6) được enforce trong SupervisorAgent

**Cách fix:**
- Tăng `MAX_ITERATIONS` trong `.env` (e.g., `MAX_ITERATIONS=10`)
- Hoặc cải thiện routing logic để detect "done" sớm hơn
- Hoặc simplify query thành các phần nhỏ hơn

---

## Case 3: Không có sources được trả về từ search

**Khi nào fail:** SearchClient trả về danh sách trống

**Lý do:** Nếu dùng mock, nó luôn trả 5 kết quả; nếu dùng real API (Tavily), API có thể trả 0 kết quả

**Cách fix:**
- Kiểm tra `state.sources` trước khi gọi Analyst
- Thêm validation: nếu `len(sources) == 0`, return early hoặc prompt user "No sources found"
- Hoặc retry search với query khác

---

## Case 4: LLM output quá dài/quá ngắn

**Khi nào fail:** Final answer dưới 50 từ (quality score = 3.0)

**Lý do:** LLM không được prompt rõ ràng về độ dài mong muốn

**Cách fix:**
- Thêm vào system prompt: "Viết 300-500 từ"
- Hoặc post-process: nếu output < 50 từ, gọi lại LLM với prompt "Mở rộng câu trả lời"
- Hoặc tăng temperature để output đa dạng hơn

---

## Case 5: Critic agent phát hiện "issues" và trả về errors

**Khi nào fail:** `state.errors` không trống

**Lý do:** Critic agent phát hiện final_answer quá ngắn hoặc bị lỗi khác

**Cách fix:**
- Nếu `len(state.errors) > 0`, log warning và có thể re-prompt Writer
- Hoặc bỏ qua Critic step nếu không cần kiểm tra chất lượng
- Hoặc implement Critic với heuristics tốt hơn (e.g., check citations, hallucination)

---

## Case 6: Timeout (quá lâu chạy)

**Khi nào fail:** Workflow chạy lâu hơn `TIMEOUT_SECONDS` (mặc định=60s)

**Lý do:** Network chậm, LLM API lag, hoặc logic agent yêu cầu nhiều calls

**Cách fix:**
- Tăng `TIMEOUT_SECONDS` trong `.env` (e.g., `TIMEOUT_SECONDS=120`)
- Hoặc tối ưu: dùng cache, batch calls, hay giảm số agents
- Hoặc optimize: giảm `max_sources`, giảm iterations

---

## Case 7: Agent chạy trong quá trình nhưng crash

**Khi nào fail:** Agent raise exception, workflow dừng

**Lý do:** Unexpected input, null reference, hoặc lỗi trong agent logic

**Cách fix:**
- Thêm try-catch block trong agent.run()
- Log error chi tiết vào `state.errors`
- Implement graceful fallback hoặc default output
- Hoặc skip agent đó và tiếp tục với agent tiếp theo

---

## Case 8: Memory leak từ vòng lặp agent không bao giờ kết thúc

**Khi nào fail:** Process chiếm dụng RAM ngày càng cao

**Lý do:** Routing policy chưa bao giờ return "done", `state.trace` hoặc `state.sources` tăng vô tận

**Cách fix:**
- Enforce `max_iterations` (đã làm)
- Hoặc implement memory tracking: nếu `len(state.trace) > threshold`, force stop
- Hoặc clear old traces: `state.trace = state.trace[-100:]` để giữ chỉ 100 trace gần nhất

---

## Summary

| Failure Mode | Severity | Mitigation |
|---|---|---|
| No API key | Medium | Use mock; document in README |
| Max iterations reached | Low | Acceptable; just log warning |
| No sources found | Medium | Validate + fallback; retry search |
| Output too short | Low | Add length constraints in prompt |
| Critic reports errors | Low | Log warning; continue or re-prompt |
| Timeout | High | Increase timeout; optimize workflow |
| Agent crash | High | Try-catch + graceful fallback |
| Memory leak | Critical | Enforce max iterations + trace limits |

