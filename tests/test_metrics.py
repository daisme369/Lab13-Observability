import importlib

from app import metrics as metrics_module
from app.metrics import percentile


def test_percentile_basic() -> None:
    assert percentile([100, 200, 300, 400], 50) >= 100


def test_snapshot_exposes_token_anomaly_metrics() -> None:
    metrics = importlib.reload(metrics_module)

    for _ in range(6):
        metrics.record_request(latency_ms=100, cost_usd=0.001, tokens_in=100, tokens_out=120, quality_score=0.9)
        result = metrics.current_token_anomalies()
        assert result["tokens_in_anomaly"] is False
        assert result["tokens_out_anomaly"] is False

    metrics.record_request(latency_ms=120, cost_usd=0.003, tokens_in=260, tokens_out=420, quality_score=0.8)
    spike = metrics.current_token_anomalies()
    assert spike["tokens_in_anomaly"] is True
    assert spike["tokens_out_anomaly"] is True

    snapshot = metrics.snapshot()
    assert snapshot["tokens_in_anomaly_count"] >= 1
    assert snapshot["tokens_out_anomaly_count"] >= 1
    assert snapshot["tokens_in_anomaly_rate"] > 0
    assert snapshot["tokens_out_anomaly_rate"] > 0
    assert snapshot["last_tokens_in_anomaly"] is True
    assert snapshot["last_tokens_out_anomaly"] is True
