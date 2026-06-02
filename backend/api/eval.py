"""Eval + Ops API."""

from __future__ import annotations

from fastapi import APIRouter

from harness.eval.runner import run_eval, save_report

router = APIRouter()


@router.post("/eval/run")
def eval_run(gate: float = 0.85) -> dict:
    report = run_eval(gate=gate)
    path = save_report(report)
    return {
        "total": report.total,
        "passed": report.passed,
        "failed": report.failed,
        "pass_rate": round(report.pass_rate, 4),
        "gate_passed": report.gate_passed,
        "by_layer": report.by_layer,
        "report_path": str(path),
    }


@router.get("/eval/report")
def eval_report_latest(gate: float = 0.85) -> dict:
    from pathlib import Path
    import json

    from harness.eval.report_enrich import enrich_report

    p = Path(__file__).resolve().parents[2] / "evaluation" / "reports" / "latest.json"
    if not p.exists():
        return {"error": "no report yet", "hint": "POST /api/eval/run"}
    raw = json.loads(p.read_text(encoding="utf-8"))
    return enrich_report(raw, gate=gate)


@router.get("/eval/cases/{case_id}")
def eval_case_detail(case_id: str) -> dict:
    from fastapi import HTTPException

    from harness.eval.report_enrich import get_case_detail

    detail = get_case_detail(case_id)
    if not detail:
        raise HTTPException(status_code=404, detail=f"用例 {case_id} 不存在")
    return detail


@router.post("/eval/replay")
def eval_replay(body: dict) -> dict:
    from harness.eval.replay import replay_diff
    from harness.runtime.trace_store import get_trace

    message = body.get("message", "")
    trace_id = body.get("trace_id", "")
    baseline = None
    if trace_id:
        tr = get_trace(trace_id)
        if tr:
            baseline = {
                "skills_invoked": tr.get("skills_invoked", []),
                "response": tr.get("response", ""),
                "intent": tr.get("intent", ""),
            }
    return replay_diff(
        message,
        session_id=body.get("session_id", "replay"),
        user_id=body.get("user_id", ""),
        baseline=baseline,
    )
