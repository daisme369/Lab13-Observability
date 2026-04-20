# Oral/Written Debugging Q&A

This document contains sample debugging questions and answers designed to prepare for an oral review or provide written evidence of debugging competence for the Observability Lab.

## Q1: Tracking down a high latency request
**Q:** "You received an alert that P95 latency has spiked over 3000ms. How do you find the root cause using the observability tools implemented in this lab?"
**A:** 
1. **Alert to Dashboard:** Start from the alert notification to view the 6-panel dashboard. Look at the latency graph to confirm the time window of the spike.
2. **Dashboard to Traces:** Filter the logs or traces within that specific time window for requests where latency > 3000ms.
3. **Analyze the Trace Waterfall:** Open a specific trace ID that was slow. The trace waterfall will show all spans (e.g., HTTP request, `LabAgent.run`, `retrieve`, `llm.generate`).
4. **Identify Bottleneck:** Find the span that took the longest time. If `retrieve` is taking 2800ms, the issue is with the RAG module. If `llm.generate` is taking 2800ms, the LLM provider is slow. (For example, in our `rag_slow` incident, the `retrieve` span will be the bottleneck).

## Q2: Investigating a PII Leak
**Q:** "A customer reported that their passport number was visible in our logs. Walk me through the steps to verify and fix this."
**A:** 
1. **Search Logs:** Search our structured JSON logs for the specific passport number or the user's `session_id` / `user_id_hash` to isolate their requests.
2. **Verify Leak:** Check the `event` or `query_preview` fields to confirm if raw PII was logged without being redacted.
3. **Trace the Source:** Use the `correlation_id` of the leaky log to find the entire request trace. Check which function or module emitted the log (e.g., `LabAgent`).
4. **Fix the Scrubber:** Open `app/pii.py` and ensure the PII regex patterns (like passport numbers or Vietnamese ID cards) are correctly configured.
5. **Validate:** Write a unit test passing a passport number to the logger to ensure the `PIIScrubbingProcessor` replaces it with `[REDACTED_PASSPORT]`.

## Q3: Missing Correlation IDs
**Q:** "You notice that database logs and API logs for the same user interaction cannot be linked together. How would you troubleshoot the `correlation_id` propagation?"
**A:**
1. **Check Middleware:** Ensure `app/middleware.py` generates or extracts the `x-request-id` header correctly at the entry point of the FastAPI app.
2. **Context Variables:** Verify that the `correlation_id` is successfully set in the `contextvars` variable (`correlation_id_var.set(req_id)`).
3. **Structlog Binding:** Ensure that the structlog processor `bind_correlation_id` is active in `app/logging_config.py` and correctly pulling the value from `contextvars`.
4. **Leakage Check:** Confirm that the middleware clears the `contextvars` at the end of the request (`correlation_id_var.reset(token)`) to prevent cross-request leakage.

## Q4: Cost Optimization
**Q:** "Your 'cost budget spike' alert triggered. How do you find which feature is burning the most money?"
**A:**
1. **Dashboard:** Look at the 'Cost over time' and 'Tokens in/out' panels on the dashboard.
2. **Log Analytics:** Aggregate our structured logs by the `feature` and `model` enrichment tags, summing up the `cost_usd` field over the last hour.
3. **Actionable Insights:** If a specific feature (e.g., "summarization") is driving the cost due to massive `tokens_in`, we can mitigate this by switching to a cheaper model (e.g., Haiku instead of Sonnet), caching prompts, or reducing the context window size.
