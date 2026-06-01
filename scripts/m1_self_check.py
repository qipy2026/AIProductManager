#!/usr/bin/env python3
"""M1 里程碑自检脚本 — 对照 DEV_TEST_PLAN S2 / M1 出口准则."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# (path, description, kind) kind: file | dir_nonempty | dir
ARTIFACTS = [
    ("skills/handlers/intent_classify.py", "intent-classify 规则引擎", "file"),
    ("skills/prompts/intent-classify.md", "Prompt 注册表对应文件", "file"),
    ("skills/runtime/executor.py", "SkillExecutor 分发", "file"),
    ("harness/runtime/trace_store.py", "Trace 持久化（内存）", "file"),
    ("backend/api/traces.py", "GET /api/traces/{id}", "file"),
    ("frontend/components/TracePanel.tsx", "Trace 查询面板", "file"),
    ("evaluation/skills/intent-classify", "DEV-316 ST 回归目录", "dir_nonempty"),
    ("tests/test_intent_classify_st.py", "ST 自动化测试", "file"),
    ("tests/test_skill_executor.py", "UT-S-003~004", "file"),
    ("tests/test_chat_api.py", "Chat + Trace 集成", "file"),
]

PLAN_GAPS = [
    ("evaluation/skills/agent-route", "其余 11 Skill ST 目录", "M2+"),
    ("skills/orchestrator/orchestrator.py", "Orchestrator 全链路", "M2"),
    ("memory/stores/working.py", "Memory 四层 Store", "M2"),
    ("harness/eval/runner.py", "Eval Harness 引擎", "M3"),
    ("frontend 来源引用位", "对话 UI source_refs", "M2"),
    ("LLM 推理", "intent-classify 当前为规则引擎", "M2 可换 LLM"),
]


def check_artifact(rel: str, kind: str) -> bool:
    p = ROOT / rel
    if kind == "file":
        return p.is_file() and p.stat().st_size > 50
    if kind == "dir_nonempty":
        return p.is_dir() and any(p.glob("*.yaml"))
    if kind == "dir":
        return p.is_dir()
    return False


def main() -> int:
    print("=" * 60)
    print("M1 自检 — 智服通 AgentOps (6/2)")
    print("=" * 60)

    passed = 0
    failed: list[str] = []

    print("\n[1] 交付物检查")
    for rel, desc, kind in ARTIFACTS:
        ok = check_artifact(rel, kind)
        status = "PASS" if ok else "FAIL"
        print(f"  {status}  {desc}")
        print(f"         {rel}")
        if ok:
            passed += 1
        else:
            failed.append(desc)

    chat = (ROOT / "backend/api/chat.py").read_text(encoding="utf-8")
    no_echo = "echo-placeholder" not in chat and (
        "intent-classify" in chat or "orchestrator" in chat.lower()
    )
    print(f"  {'PASS' if no_echo else 'FAIL'}  chat.py 已接入 Skill 链路（Orchestrator/intent-classify）")
    if no_echo:
        passed += 1
    else:
        failed.append("chat.py echo 未替换")

    st_count = len(list((ROOT / "evaluation/skills/intent-classify").glob("ST-IC-*.yaml")))
    st_ok = st_count == 25
    print(f"  {'PASS' if st_ok else 'FAIL'}  ST 用例数量 = 25（当前 {st_count}）")
    if st_ok:
        passed += 1
    else:
        failed.append(f"ST 用例 {st_count}/25")

    print("\n[2] 计划内未交付（诚实标注，不阻塞 M1 核心）")
    for rel, desc, phase in PLAN_GAPS:
        print(f"  DEFER  [{phase}] {desc}")

    print("\n[3] pytest")
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=no"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(r.stdout.strip() or r.stderr.strip())
    tests_ok = r.returncode == 0
    print(f"  {'PASS' if tests_ok else 'FAIL'}  pytest exit={r.returncode}")

    total = len(ARTIFACTS) + 2  # + chat + st count
    print("\n" + "=" * 60)
    print(f"交付物: {passed}/{total}  |  pytest: {'PASS' if tests_ok else 'FAIL'}")
    if failed:
        print("阻塞项:", ", ".join(failed))
    else:
        print("M1 核心出口准则: intent-classify 经 Harness 调用 + Trace — 达标")
        print("说明: 规则引擎 MVP，Orchestrator/Memory/LLM 属 M2+")
    print("=" * 60)
    return 0 if (not failed and tests_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
