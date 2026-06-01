#!/usr/bin/env python3
"""M2 里程碑自检 — Memory + Orchestrator + MVP 四场景."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

ARTIFACTS = [
    ("memory/stores/working.py", "Working Memory"),
    ("memory/stores/episodic.py", "Episodic Memory"),
    ("memory/stores/profile.py", "Profile Memory"),
    ("memory/stores/semantic.py", "Semantic / RAG Mock"),
    ("memory/router/router.py", "Memory Router"),
    ("harness/runtime/memory_injector.py", "Harness Injector"),
    ("skills/orchestrator/orchestrator.py", "Skill Orchestrator"),
    ("skills/orchestrator/graph.yaml", "编排有向图"),
    ("skills/handlers/business.py", "业务 Skill Handlers"),
    ("knowledge-base/faq.json", "知识库 Mock"),
    ("backend/tools/ticket_mock.py", "工单 Mock API"),
    ("tests/test_memory.py", "UT-M-001~008"),
    ("tests/test_orchestrator.py", "UT-S-005~007"),
]


def main() -> int:
    print("=" * 60)
    print("M2 自检 — Memory + Orchestrator MVP")
    print("=" * 60)
    passed = 0
    for rel, desc in ARTIFACTS:
        p = ROOT / rel
        ok = p.is_file() and p.stat().st_size > 20
        print(f"  {'PASS' if ok else 'FAIL'}  {desc}")
        if ok:
            passed += 1

    chat = (ROOT / "backend/api/chat.py").read_text(encoding="utf-8")
    ok_orch = "SkillOrchestrator" in chat
    print(f"  {'PASS' if ok_orch else 'FAIL'}  chat.py 使用 Orchestrator")
    if ok_orch:
        passed += 1

    print("\n[pytest]")
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=no"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(r.stdout.strip())
    ok = r.returncode == 0
    print(f"  {'PASS' if ok else 'FAIL'}  exit={r.returncode}")

    print("\n[MVP 四场景 smoke]")
    from fastapi.testclient import TestClient
    from backend.main import app
    from backend.tools.ticket_mock import ticket_api
    from memory.router.router import working_store
    from harness.runtime.trace_store import clear_traces

    client = TestClient(app)
    scenarios = [
        ("咨询+RAG", {"message": "企业版和专业版区别？"}),
        ("建单", {"message": "服务器宕机请处理"}),
        ("查单", {"message": "查 T-001 进度"}),
        ("升级", {"message": "太差了三次没解决要投诉"}),
    ]
    for name, body in scenarios:
        clear_traces()
        ticket_api.clear()
        working_store.clear()
        body = {**body, "session_id": f"m2-{name}"}
        resp = client.post("/api/chat", json=body)
        ok_s = resp.status_code == 200 and len(resp.json().get("response", "")) > 5
        print(f"  {'PASS' if ok_s else 'FAIL'}  {name}")
        if ok_s:
            passed += 1

    total = len(ARTIFACTS) + 1 + len(scenarios)
    print(f"\n合计: {passed}/{total}  artifacts+smoke | pytest: {'PASS' if ok else 'FAIL'}")
    return 0 if ok and passed >= total - 1 else 1


if __name__ == "__main__":
    sys.exit(main())
