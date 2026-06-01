"""M3 自检 — Eval + API."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("AGENTOPS_STORAGE", "memory")
os.environ.setdefault("SEMANTIC_BACKEND", "keyword")
os.environ.setdefault("USE_LANGGRAPH", "0")


def main() -> int:
    ok = True

    from harness.eval.runner import run_eval

    report = run_eval(gate=0.85)
    print(f"[Eval] {report.passed}/{report.total} ({report.pass_rate:.1%}) gate={'PASS' if report.gate_passed else 'FAIL'}")
    if not report.gate_passed:
        ok = False

    prompts = list((ROOT / "skills" / "prompts").glob("*.md"))
    print(f"[Prompts] {len(prompts)} files")
    if len(prompts) < 12:
        ok = False

    ci = ROOT / ".github" / "workflows" / "eval.yml"
    print(f"[CI] {'exists' if ci.exists() else 'MISSING'}")
    if not ci.exists():
        ok = False

    report_path = ROOT / "evaluation" / "reports" / "latest.json"
    if report_path.exists():
        data = json.loads(report_path.read_text(encoding="utf-8"))
        print(f"[Report] pass_rate={data.get('pass_rate', 0):.1%}")

    print("\nM3 self-check:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
