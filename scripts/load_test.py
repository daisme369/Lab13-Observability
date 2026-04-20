import argparse
import concurrent.futures
import json
import time
from pathlib import Path
from typing import Any

import httpx

BASE_URL = "http://127.0.0.1:8000"
QUERIES = Path("data/sample_queries.jsonl")


def send_request(client: httpx.Client, payload: dict[str, Any]) -> None:
    try:
        case_id = str(payload.get("_case", "UNNAMED_CASE"))
        api_payload = {k: v for k, v in payload.items() if not str(k).startswith("_")}
        start = time.perf_counter()
        r = client.post(f"{BASE_URL}/chat", json=api_payload)
        latency = (time.perf_counter() - start) * 1000
        response_body = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        print(
            f"[{r.status_code}] {case_id} | {response_body.get('correlation_id')} | "
            f"{api_payload.get('feature', 'n/a')} | {latency:.1f}ms"
        )
    except Exception as e:
        print(f"Error in {payload.get('_case', 'UNNAMED_CASE')}: {e}")


def handle_control(client: httpx.Client, record: dict[str, Any]) -> None:
    control_type = record.get("_control")
    if control_type != "incident":
        print(f"[SKIP] Unknown control: {control_type}")
        return

    scenario = record.get("scenario")
    enabled = bool(record.get("enabled", True))
    if scenario not in {"rag_slow", "tool_fail", "cost_spike"}:
        print(f"[SKIP] Unknown incident scenario: {scenario}")
        return

    action = "enable" if enabled else "disable"
    r = client.post(f"{BASE_URL}/incidents/{scenario}/{action}", timeout=10.0)
    print(f"[CONTROL {r.status_code}] {action} {scenario}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--concurrency", type=int, default=1, help="Number of concurrent requests")
    parser.add_argument("--file", type=Path, default=QUERIES, help="Path to JSONL test cases")
    args = parser.parse_args()

    lines = [line for line in args.file.read_text(encoding="utf-8").splitlines() if line.strip()]
    records = [json.loads(line) for line in lines]
    has_control = any(isinstance(record, dict) and "_control" in record for record in records)
    
    with httpx.Client(timeout=30.0) as client:
        if args.concurrency > 1 and not has_control:
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as executor:
                futures = [executor.submit(send_request, client, record) for record in records if isinstance(record, dict)]
                concurrent.futures.wait(futures)
        else:
            if args.concurrency > 1 and has_control:
                print("[INFO] Control records detected. Falling back to sequential execution to preserve order.")
            for record in records:
                if not isinstance(record, dict):
                    print("[SKIP] Invalid record type, expected object")
                    continue
                if "_control" in record:
                    handle_control(client, record)
                else:
                    send_request(client, record)


if __name__ == "__main__":
    main()
