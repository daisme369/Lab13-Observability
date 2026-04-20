from __future__ import annotations

from collections import Counter
from statistics import mean, pstdev

ANOMALY_WINDOW = 20
ANOMALY_MIN_SAMPLES = 5
ANOMALY_HIGH_RATIO = 2.0
ANOMALY_LOW_RATIO = 0.5
ANOMALY_ZSCORE_THRESHOLD = 3.0

REQUEST_LATENCIES: list[int] = []
REQUEST_COSTS: list[float] = []
REQUEST_TOKENS_IN: list[int] = []
REQUEST_TOKENS_OUT: list[int] = []
ERRORS: Counter[str] = Counter()
TRAFFIC: int = 0
QUALITY_SCORES: list[float] = []
TOKENS_IN_ANOMALIES: int = 0
TOKENS_OUT_ANOMALIES: int = 0
LAST_TOKENS_IN_ANOMALY: bool = False
LAST_TOKENS_OUT_ANOMALY: bool = False


def _is_token_anomaly(value: int, history: list[int]) -> bool:
    baseline = history[-ANOMALY_WINDOW:]
    if len(baseline) < ANOMALY_MIN_SAMPLES:
        return False

    baseline_mean = mean(baseline)
    if baseline_mean <= 0:
        return False

    ratio = value / baseline_mean
    if ratio >= ANOMALY_HIGH_RATIO or ratio <= ANOMALY_LOW_RATIO:
        return True

    spread = pstdev(baseline)
    if spread <= 0:
        return False

    z_score = abs(value - baseline_mean) / spread
    return z_score >= ANOMALY_ZSCORE_THRESHOLD


def record_request(
    latency_ms: int,
    cost_usd: float,
    tokens_in: int,
    tokens_out: int,
    quality_score: float,
) -> None:
    global TRAFFIC, TOKENS_IN_ANOMALIES, TOKENS_OUT_ANOMALIES, LAST_TOKENS_IN_ANOMALY, LAST_TOKENS_OUT_ANOMALY

    tokens_in_anomaly = _is_token_anomaly(tokens_in, REQUEST_TOKENS_IN)
    tokens_out_anomaly = _is_token_anomaly(tokens_out, REQUEST_TOKENS_OUT)

    if tokens_in_anomaly:
        TOKENS_IN_ANOMALIES += 1
    if tokens_out_anomaly:
        TOKENS_OUT_ANOMALIES += 1

    TRAFFIC += 1
    REQUEST_LATENCIES.append(latency_ms)
    REQUEST_COSTS.append(cost_usd)
    REQUEST_TOKENS_IN.append(tokens_in)
    REQUEST_TOKENS_OUT.append(tokens_out)
    QUALITY_SCORES.append(quality_score)
    LAST_TOKENS_IN_ANOMALY = tokens_in_anomaly
    LAST_TOKENS_OUT_ANOMALY = tokens_out_anomaly

def current_token_anomalies() -> dict[str, bool]:
    return {
        "tokens_in_anomaly": LAST_TOKENS_IN_ANOMALY,
        "tokens_out_anomaly": LAST_TOKENS_OUT_ANOMALY,
    }



def record_error(error_type: str) -> None:
    ERRORS[error_type] += 1



def percentile(values: list[int], p: int) -> float:
    if not values:
        return 0.0
    items = sorted(values)
    idx = max(0, min(len(items) - 1, round((p / 100) * len(items) + 0.5) - 1))
    return float(items[idx])



def snapshot() -> dict:
    tokens_in_avg = round(mean(REQUEST_TOKENS_IN), 2) if REQUEST_TOKENS_IN else 0.0
    tokens_out_avg = round(mean(REQUEST_TOKENS_OUT), 2) if REQUEST_TOKENS_OUT else 0.0
    tokens_in_anomaly_rate = round((TOKENS_IN_ANOMALIES / TRAFFIC) * 100, 2) if TRAFFIC else 0.0
    tokens_out_anomaly_rate = round((TOKENS_OUT_ANOMALIES / TRAFFIC) * 100, 2) if TRAFFIC else 0.0

    return {
        "traffic": TRAFFIC,
        "latency_p50": percentile(REQUEST_LATENCIES, 50),
        "latency_p95": percentile(REQUEST_LATENCIES, 95),
        "latency_p99": percentile(REQUEST_LATENCIES, 99),
        "avg_cost_usd": round(mean(REQUEST_COSTS), 4) if REQUEST_COSTS else 0.0,
        "total_cost_usd": round(sum(REQUEST_COSTS), 4),
        "tokens_in_total": sum(REQUEST_TOKENS_IN),
        "tokens_out_total": sum(REQUEST_TOKENS_OUT),
        "tokens_in_avg": tokens_in_avg,
        "tokens_out_avg": tokens_out_avg,
        "tokens_in_anomaly_count": TOKENS_IN_ANOMALIES,
        "tokens_out_anomaly_count": TOKENS_OUT_ANOMALIES,
        "tokens_in_anomaly_rate": tokens_in_anomaly_rate,
        "tokens_out_anomaly_rate": tokens_out_anomaly_rate,
        "last_tokens_in_anomaly": LAST_TOKENS_IN_ANOMALY,
        "last_tokens_out_anomaly": LAST_TOKENS_OUT_ANOMALY,
        "error_breakdown": dict(ERRORS),
        "quality_avg": round(mean(QUALITY_SCORES), 4) if QUALITY_SCORES else 0.0,
    }
