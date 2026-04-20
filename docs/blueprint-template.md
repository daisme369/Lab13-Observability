# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: Nhóm C401-B5
- [REPO_URL]: https://github.com/daisme369/Lab13-Observability
- [MEMBERS]:
  - Member A: Nguyễn Ngọc Tân (2A202600190) | Role: Logging + PII Scrubbing
  - Member B: Nguyễn Đăng Hải (2A202600390) | Role: Correlation ID + Middleware
  - Member C: Lê Đức Anh (2A202600092) | Role: SLO + Alerting
  - Member D: Trần Trung Hậu (2A202600317) | Role: Tracing + Load Test
  - Member E: Nguyễn Tuấn Hưng (2A202600230) | Role: Dashboard + Report

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: 209
- [PII_LEAKS_FOUND]: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: ![Correlation ID](screenshots/correlation_id.png)
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: ![PII Redaction](screenshots/pii_redaction.png)
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: ![Trace Waterfall](screenshots/trace_waterfall.png)
- [TRACE_WATERFALL_EXPLANATION]: Trong biểu đồ trace waterfall, có thể quan sát thấy span gọi LLM API hoặc Database chiếm phần lớn thời gian phản hồi (latency bottleneck). Việc gắn correlation ID giúp liên kết tất cả các span con vào một luồng request duy nhất.

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: ![Dashboard](screenshots/dashboard.png)
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | 150.0ms |
| Error Rate | < 2% | 28d | 0.0% |
| Cost Budget | < $2.5/day | 1d | $0.46 |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: ![Alert Rules](screenshots/alert_rules.png)
- [SAMPLE_RUNBOOK_LINK]: [docs/alerts.md]

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: rag_slow
- [SYMPTOMS_OBSERVED]: Độ trễ (latency) của hệ thống tăng vọt trên Dashboard, đồng thời nhận được Alert cảnh báo `high_latency_p95`.
- [ROOT_CAUSE_PROVED_BY]: ![Incident Trace](screenshots/incident_trace.png) (Trace cho thấy module RAG bị nghẽn)
- [FIX_ACTION]: Chạy lệnh disable incident để khôi phục: `python scripts/inject_incident.py --scenario rag_slow --disable`
- [PREVENTIVE_MEASURE]: Thêm timeout cho RAG module, cấu hình cảnh báo sớm trên Alerting/SLO.

---

## 5. Individual Contributions & Evidence

### Nguyễn Ngọc Tân
- [TASKS_COMPLETED]: Đăng ký PII scrubbing processor, Thêm patterns PII (passport, địa chỉ VN...), Enrich logs với request context.
- [EVIDENCE_LINK]: (Link commit/PR liên quan đến `app/logging_config.py`, `app/pii.py`, `app/main.py`)

### Nguyễn Đăng Hải
- [TASKS_COMPLETED]: Clear contextvars tránh leak, Extract/generate x-request-id, Bind correlation_id vào structlog, Add correlation_id + processing_time vào response headers.
- [EVIDENCE_LINK]: (Link commit/PR liên quan đến `app/middleware.py`)

### Lê Đức Anh
- [TASKS_COMPLETED]: Hoàn thiện SLO definitions, Configure alert rules, Viết runbook + alert worksheet.
- [EVIDENCE_LINK]: (Link commit/PR liên quan đến `config/slo.yaml`, `config/alert_rules.yaml`, `docs/alerts.md`)

### Trần Trung Hậu
- [TASKS_COMPLETED]: Kiểm tra observe decorator được dùng, Chạy load test (concurrency 5), Inject incidents khi cần, Validate progress.
- [EVIDENCE_LINK]: (Link commit/PR liên quan đến chạy script `load_test.py`, `inject_incident.py`, `validate_logs.py`)

### Nguyễn Tuấn Hưng
- [TASKS_COMPLETED]: Build 6-panel dashboard checklist, Viết team submission template, Thu thập evidence, Oral/written debugging Q&A.
- [EVIDENCE_LINK]: (Link commit/PR liên quan đến `docs/blueprint-template.md`, `docs/dashboard-spec.md`, `docs/grading-evidence.md`, `docs/mock-debug-qa.md`)

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: (Description + Evidence)
- [BONUS_AUDIT_LOGS]: (Description + Evidence)
- [BONUS_CUSTOM_METRIC]: (Description + Evidence)
