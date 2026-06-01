"""Eval 门禁脚本 — CI / 本地一键跑评测."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("AGENTOPS_STORAGE", "memory")
os.environ.setdefault("SEMANTIC_BACKEND", "keyword")
os.environ.setdefault("LLM_MODE", "mock")
os.environ.setdefault("USE_LANGGRAPH", "0")

from harness.eval.runner import run_eval, save_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Eval Harness with gate")
    parser.add_argument("--gate", type=float, default=0.85, help="Pass rate threshold")
    parser.add_argument("--layer", action="append", help="Optional layer filter L1,L2,...")
    args = parser.parse_args()

    report = run_eval(layers=args.layer, gate=args.gate)
    path = save_report(report)
    print(f"Eval: {report.passed}/{report.total} ({report.pass_rate:.1%}) gate={'PASS' if report.gate_passed else 'FAIL'}")
    for layer, stats in sorted(report.by_layer.items()):
        t = stats["total"]
        p = stats["passed"]
        print(f"  {layer}: {p}/{t} ({p/t:.0%})" if t else f"  {layer}: 0")
    print(f"Report: {path}")
    return 0 if report.gate_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
