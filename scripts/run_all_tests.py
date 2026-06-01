#!/usr/bin/env python3
"""一键跑全量测试 — pytest + Eval + M1/M2/M3 自检 + Playwright（可选）."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E2E_DIR = ROOT / "e2e"


def run(cmd: list[str] | str, *, cwd: Path | None = None, env: dict | None = None, shell: bool = False) -> int:
    if isinstance(cmd, list):
        label = " ".join(cmd[:3])
    else:
        label = cmd[:40]
    print(f"\n{'='*60}\n>>> {label}...\n{'='*60}")
    merged = {**os.environ, **(env or {})}
    return subprocess.call(cmd, cwd=cwd or ROOT, env=merged, shell=shell)


def frontend_up() -> bool:
    try:
        import httpx

        with httpx.Client(trust_env=False, timeout=3.0) as client:
            r = client.get("http://localhost:3000", follow_redirects=False)
        return r.status_code in (200, 307, 308)
    except Exception:
        return False


def main() -> int:
    env = {
        "AGENTOPS_STORAGE": "memory",
        "SEMANTIC_BACKEND": "keyword",
        "LLM_MODE": "mock",
        "USE_LANGGRAPH": "0",
    }
    failed = 0

    steps: list[tuple[str, list[str], Path | None]] = [
        ("Eval Harness 120 条", [sys.executable, "scripts/run_eval.py", "--gate", "0.85"], None),
        ("pytest 全量", [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=line"], None),
        ("M1 自检", [sys.executable, "scripts/m1_self_check.py"], None),
        ("M2 自检", [sys.executable, "scripts/m2_self_check.py"], None),
        ("M3 自检", [sys.executable, "scripts/m3_self_check.py"], None),
    ]

    for name, cmd, cwd in steps:
        code = run(cmd, cwd=cwd, env=env)
        status = "PASS" if code == 0 else "FAIL"
        print(f"[{status}] {name}")
        if code != 0:
            failed += 1

    if frontend_up():
        if not (E2E_DIR / "node_modules").exists():
            run("npm install", cwd=E2E_DIR, shell=True)
        pw_env = {**env, "E2E_SKIP_SERVER": "1"}
        code = run("npx playwright test", cwd=E2E_DIR, env=pw_env, shell=True)
        status = "PASS" if code == 0 else "FAIL"
        print(f"[{status}] Playwright E2E (9 场景)")
        if code != 0:
            failed += 1
    else:
        print("[SKIP] Playwright — 前端 :3000 未启动，跳过 E2E")

    print(f"\n{'='*60}")
    if failed:
        print(f"全量测试完成：{failed} 项失败")
        return 1
    print("全量测试完成：ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
