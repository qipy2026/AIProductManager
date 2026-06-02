"""Eval Harness 集成测试."""

from harness.eval.runner import run_eval


def test_eval_gate_passes():
    report = run_eval(gate=0.85)
    assert report.total == 122
    assert report.pass_rate >= 0.85, f"pass_rate={report.pass_rate:.1%}"


def test_eval_l4_l5_perfect():
    report = run_eval(layers=["L4", "L5"], gate=1.0)
    assert report.passed == report.total
