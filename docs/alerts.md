# Alert Rules and Runbooks

## 1. High latency P95
- Severity: P2
- Trigger: `latency_p95_ms > 3000 for 10m`
- Impact: tail latency breaches SLO
- First checks:
  1. Open top slow traces in the last 1h
  2. Compare RAG span vs LLM span
  3. Check if incident toggle `rag_slow` is enabled
- Mitigation:
  - truncate long queries
  - fallback retrieval source
  - lower prompt size
- Escalation/Exit:
  - Escalate to platform owner if breach lasts more than 30m
  - Close alert after 3 consecutive healthy windows

## 2. High error rate
- Severity: P1
- Trigger: `error_rate_pct > 2 for 5m`
- Impact: users receive failed responses
- First checks:
  1. Group logs by `error_type`
  2. Inspect failed traces
  3. Determine whether failures are LLM, tool, or schema related
- Mitigation:
  - rollback latest change
  - disable failing tool
  - retry with fallback model
- Escalation/Exit:
  - Escalate immediately to incident commander if error rate exceeds 10%
  - Close alert after error rate stays below 1% for 15m

## 3. Cost budget spike
- Severity: P2
- Trigger: `daily_cost_usd > 2.5 for 60m`
- Impact: burn rate exceeds budget
- First checks:
  1. Split traces by feature and model
  2. Compare tokens_in/tokens_out
  3. Check if `cost_spike` incident was enabled
- Mitigation:
  - shorten prompts
  - route easy requests to cheaper model
  - apply prompt cache
- Escalation/Exit:
  - Escalate to FinOps owner if cost remains above budget for 2h
  - Close alert after daily projected burn returns below threshold

## 4. High latency P99
- Severity: P2
- Trigger: `latency_p99_ms > 5000 for 10m`
- Impact: worst-case response time degrades user trust
- First checks:
  1. Inspect top 1% slow traces and identify dominant span
  2. Compare incident state with normal baseline
  3. Verify whether a specific feature drives tail latency
- Mitigation:
  - cap max input size
  - reduce retrieved context size
  - route heavy requests to async fallback
- Escalation/Exit:
  - Escalate to platform owner if P99 remains above threshold for 30m
  - Close alert after 3 healthy 10m windows

## 5. High TTFT P95
- Severity: P2
- Trigger: `ttft_p95_ms > 1200 for 10m`
- Impact: users feel system is unresponsive before first token
- First checks:
  1. Compare request queue time and model compute span
  2. Check concurrency and saturation indicators
  3. Verify whether prompt size has increased recently
- Mitigation:
  - reduce prompt pre-processing overhead
  - lower retrieval fan-out
  - scale worker replicas if available
- Escalation/Exit:
  - Escalate to platform owner if TTFT remains high for 30m
  - Close alert after TTFT stays below threshold for 20m

## 6. High timeout rate
- Severity: P1
- Trigger: `timeout_rate_pct > 0.5 for 10m`
- Impact: requests fail without usable responses
- First checks:
  1. Filter logs for timeout-related `error_type`
  2. Identify endpoint and feature with highest timeout share
  3. Check upstream dependency latency trend
- Mitigation:
  - increase timeout only as temporary mitigation
  - apply circuit breaker for unstable dependency
  - fail fast with fallback response
- Escalation/Exit:
  - Escalate immediately if timeout rate exceeds 2%
  - Close alert after timeout rate is below 0.2% for 20m

## 7. PII leak detected
- Severity: P1
- Trigger: `pii_leak_rate > 0 for 1m`
- Impact: potential compliance and privacy breach
- First checks:
  1. Locate leaked fields and sample records in logs
  2. Confirm scrubber processor and config are enabled
  3. Identify source event and code path
- Mitigation:
  - stop affected logging path immediately
  - rotate or quarantine leaked log files
  - patch scrub patterns and redeploy
- Escalation/Exit:
  - Escalate to security-oncall immediately
  - Close alert only after no leaks are found for 24h and patch is verified

## 8. Low correlation coverage
- Severity: P2
- Trigger: `correlation_coverage_pct < 99.9 for 15m`
- Impact: incident triage slows down due to broken request tracing
- First checks:
  1. Check middleware adds and propagates request ID
  2. Verify downstream logs preserve correlation ID
  3. Inspect load balancer or gateway header forwarding
- Mitigation:
  - enforce request ID generation at edge and app middleware
  - add fallback ID if header is missing
  - add CI validation for log context fields
- Escalation/Exit:
  - Escalate to observability-owner if below threshold for 1h
  - Close alert after coverage is above 99.95% for 30m

## 9. Low structured log compliance
- Severity: P2
- Trigger: `structured_log_compliance_pct < 99.5 for 15m`
- Impact: dashboards and alerts become unreliable
- First checks:
  1. Validate records against required schema fields
  2. Identify services or event types producing invalid logs
  3. Check serializer or logging processor regressions
- Mitigation:
  - enforce structured logger wrapper usage
  - block raw print or unstructured logger paths
  - add schema validation in CI for representative logs
- Escalation/Exit:
  - Escalate to observability-owner if compliance remains low for 1h
  - Close alert after compliance is above 99.7% for 30m

## Alert Worksheet Template
- Alert name:
- Trigger time:
- Current metric value:
- Threshold:
- Impact summary:
- Suspected root cause:
- Checks performed:
- Mitigation applied:
- Recovery time:
- Follow-up actions:
