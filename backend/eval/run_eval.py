#!/usr/bin/env python3
"""Evaluation harness for the clinical-trials visualization pipeline.

Runs all eval cases against the live backend API in parallel and prints a
pass/fail report with latency and failure details.

Usage:
    python eval/run_eval.py [--base-url URL] [--workers N] [--timeout S] [--case ID]

Defaults:
    --base-url  http://localhost:8000
    --workers   4
    --timeout   120
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path

import httpx

try:
    from tqdm import tqdm
except ImportError:
    print("tqdm not found — install with: pip install tqdm", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).parent
CASES_FILE = ROOT / "cases" / "clinical_trials_eval_cases.json"

# Validators live next to this file
sys.path.insert(0, str(ROOT))
from validators.deterministic import validate  # noqa: E402


@dataclass
class Result:
    case_id: str
    description: str
    passed: bool
    failures: list[str] = field(default_factory=list)
    latency_s: float = 0.0
    actual_status: str | None = None
    actual_viz_type: str | None = None
    http_status: int | None = None
    error: str | None = None


def run_case(case: dict, base_url: str, timeout: float) -> Result:
    case_id = case["id"]
    description = case.get("description", case_id)
    expected = case["expected"]
    request_body = case["request"]

    t0 = time.monotonic()
    try:
        resp = httpx.post(
            f"{base_url}/visualizations",
            json=request_body,
            timeout=timeout,
        )
        latency = time.monotonic() - t0

        if resp.status_code != 200:
            return Result(
                case_id=case_id,
                description=description,
                passed=False,
                failures=[f"HTTP {resp.status_code}: {resp.text[:200]}"],
                latency_s=latency,
                http_status=resp.status_code,
            )

        data = resp.json()
        failures = validate(data, expected)

        viz = data.get("visualization") or {}
        return Result(
            case_id=case_id,
            description=description,
            passed=len(failures) == 0,
            failures=failures,
            latency_s=latency,
            actual_status=data.get("status"),
            actual_viz_type=viz.get("type"),
            http_status=resp.status_code,
        )

    except Exception as exc:
        latency = time.monotonic() - t0
        return Result(
            case_id=case_id,
            description=description,
            passed=False,
            failures=[f"Exception: {exc}"],
            latency_s=latency,
            error=str(exc),
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Clinical trials eval harness")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Backend base URL")
    parser.add_argument("--workers", type=int, default=4, help="Parallel workers")
    parser.add_argument("--timeout", type=float, default=120.0, help="Request timeout (s)")
    parser.add_argument("--case", help="Run only this case ID")
    args = parser.parse_args()

    cases = json.loads(CASES_FILE.read_text())
    if args.case:
        cases = [c for c in cases if c["id"] == args.case]
        if not cases:
            print(f"No case with id {args.case!r}", file=sys.stderr)
            sys.exit(1)

    print(f"\n  Clinical Trials Eval Harness")
    print(f"  Backend : {args.base_url}")
    print(f"  Cases   : {len(cases)}")
    print(f"  Workers : {args.workers}")
    print(f"  Timeout : {args.timeout}s")
    print()

    results: list[Result] = []

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(run_case, case, args.base_url, args.timeout): case["id"]
            for case in cases
        }

        bar = tqdm(as_completed(futures), total=len(futures), unit="case", ncols=72)
        for fut in bar:
            result = fut.result()
            results.append(result)
            icon = "✓" if result.passed else "✗"
            bar.set_postfix_str(f"{icon} {result.case_id} ({result.latency_s:.1f}s)")

    # Sort by original case order
    order = {c["id"]: i for i, c in enumerate(cases)}
    results.sort(key=lambda r: order.get(r.case_id, 999))

    # ── Report ──────────────────────────────────────────────────────────────
    passed = [r for r in results if r.passed]
    failed = [r for r in results if not r.passed]

    print("\n" + "─" * 72)
    print(f"  Results: {len(passed)}/{len(results)} passed")
    print("─" * 72)

    col_id = 20
    col_desc = 36
    col_type = 14
    col_lat = 6

    header = (
        f"{'ID':<{col_id}} {'DESCRIPTION':<{col_desc}} "
        f"{'TYPE':<{col_type}} {'LAT':>{col_lat}}  STATUS"
    )
    print(header)
    print("─" * 72)

    for r in results:
        icon = "PASS" if r.passed else "FAIL"
        viz_type = r.actual_viz_type or r.actual_status or "—"
        desc = r.description[:col_desc]
        print(
            f"{r.case_id:<{col_id}} {desc:<{col_desc}} "
            f"{viz_type:<{col_type}} {r.latency_s:>{col_lat}.1f}s  {icon}"
        )
        for failure in r.failures:
            print(f"  {'':>{col_id}}  ↳ {failure}")

    print("─" * 72)
    avg_lat = sum(r.latency_s for r in results) / len(results) if results else 0
    print(f"  Average latency: {avg_lat:.1f}s")
    print()

    if failed:
        print(f"  {len(failed)} case(s) FAILED")
        sys.exit(1)
    else:
        print("  All cases passed.")


if __name__ == "__main__":
    main()
