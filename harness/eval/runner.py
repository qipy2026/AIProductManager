"""Eval Runner — 批量跑 120 条评测集."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

from backend.tools.ticket_mock import ticket_api
from harness.eval.assertions import EvalResult, check_case
from harness.runtime.context import HarnessContext
from harness.runtime.pipeline import RuntimeHarness
from memory.router.router import episodic_store, profile_store, working_store
from skills.orchestrator.orchestrator import SkillOrchestrator

CASES_ROOT = Path(__file__).resolve().parents[2] / "evaluation" / "test_cases"
REPORT_DIR = Path(__file__).resolve().parents[2] / "evaluation" / "reports"


@dataclass
class EvalReport:
    total: int = 0
    passed: int = 0
    failed: int = 0
    pass_rate: float = 0.0
    by_layer: dict[str, dict[str, int]] = field(default_factory=dict)
    results: list[dict] = field(default_factory=list)
    gate_passed: bool = False


def _reset_state() -> None:
    ticket_api.clear()
    working_store.clear()
    episodic_store.clear()
    profile_store.clear()


def _apply_fixture(case: dict) -> None:
    fx = case.get("input", {}).get("memory_fixture")
    if not fx:
        return
    uid = fx.get("user_id", case.get("input", {}).get("user_id", ""))
    for rec in fx.get("episodic", []) or []:
        episodic_store.write(uid, rec.get("summary", ""), rec.get("ticket_ids", []))
    prof = fx.get("profile")
    if prof and uid:
        from memory.stores.profile import UserProfile
        profile_store.set(UserProfile(user_id=uid, **prof))


def _run_case(case: dict, orchestrator: SkillOrchestrator, harness: RuntimeHarness) -> EvalResult:
    _reset_state()
    _apply_fixture(case)
    inp = case.get("input", {})
    message = inp.get("message", "")
    session_id = inp.get("session_id", f"eval-{case['id']}")
    user_id = inp.get("user_id", "")

    if not user_id and case.get("input", {}).get("memory_fixture"):
        user_id = case["input"]["memory_fixture"].get("user_id", "")

    def handler(ctx: HarnessContext) -> HarnessContext:
        return orchestrator.run(ctx)

    ctx = harness.run(message, session_id=session_id, user_id=user_id, skill_handler=handler)
    intent = ctx.memory_context.get("intent_result", {}).get("intent", "")
    return check_case(
        case,
        skills=ctx.trace.skills_invoked,
        memory_injected=ctx.trace.memory_injected,
        response=ctx.response,
        blocked=ctx.blocked,
        intent=intent,
    )


def load_cases(layers: list[str] | None = None) -> list[dict]:
    cases: list[dict] = []
    layer_dirs = {
        "L1": "L1_skill",
        "L2": "L2_rag",
        "L3": "L3_tool",
        "L4": "L4_memory",
        "L5": "L5_e2e",
    }
    for layer, dirname in layer_dirs.items():
        if layers and layer not in layers:
            continue
        d = CASES_ROOT / dirname
        if not d.exists():
            continue
        for path in sorted(d.glob("*.yaml")):
            with path.open(encoding="utf-8") as f:
                data = yaml.safe_load(f)
            cases.append(data)
    return cases


def run_eval(layers: list[str] | None = None, gate: float = 0.85) -> EvalReport:
    import os

    prev_eval = os.environ.get("EVAL_HARNESS")
    os.environ["EVAL_HARNESS"] = "1"
    try:
        return _run_eval_body(layers, gate)
    finally:
        if prev_eval is None:
            os.environ.pop("EVAL_HARNESS", None)
        else:
            os.environ["EVAL_HARNESS"] = prev_eval


def _run_eval_body(layers: list[str] | None = None, gate: float = 0.85) -> EvalReport:
    cases = load_cases(layers)
    orchestrator = SkillOrchestrator()
    harness = RuntimeHarness()
    report = EvalReport(total=len(cases))

    for case in cases:
        result = _run_case(case, orchestrator, harness)
        layer = result.layer
        report.by_layer.setdefault(layer, {"passed": 0, "failed": 0, "total": 0})
        report.by_layer[layer]["total"] += 1
        if result.passed:
            report.passed += 1
            report.by_layer[layer]["passed"] += 1
        else:
            report.failed += 1
            report.by_layer[layer]["failed"] += 1
            try:
                from backend.db.store import get_ops_store

                store = get_ops_store()
                if store:
                    from backend.badcase.attribution_infer import infer_attribution_from_badcase

                    payload = {
                        "layer": result.layer,
                        "note": "; ".join(result.failures),
                        "failures": result.failures,
                        "attribution": "eval_failure",
                    }
                    store.badcase_add(
                        case_id=result.case_id,
                        layer=result.layer,
                        attribution=infer_attribution_from_badcase(payload),
                        note=payload["note"],
                        failures=result.failures,
                    )
            except Exception:
                pass
        report.results.append(asdict(result))

    report.pass_rate = report.passed / report.total if report.total else 0.0
    report.gate_passed = report.pass_rate >= gate
    return report


def save_report(report: EvalReport) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORT_DIR / "latest.json"
    path.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Eval Harness Runner")
    parser.add_argument("--all", action="store_true", help="Run all layers")
    parser.add_argument("--layer", action="append", help="L1,L2,...")
    parser.add_argument("--gate", type=float, default=0.85)
    args = parser.parse_args()
    layers = args.layer
    if args.all or not layers:
        layers = None
    report = run_eval(layers=layers, gate=args.gate)
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
