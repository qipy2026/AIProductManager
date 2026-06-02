#!/usr/bin/env python3
"""主场景 API 冒烟 — E2E-001~004、007（对应 record_demo 分镜）."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

def _safe(text: str) -> str:
    return text.replace("\U0001f4ce", "[来源]").encode("gbk", errors="replace").decode("gbk")


API = "http://localhost:8002/api/chat"

SCENARIOS = [
    (
        "E2E-001 知识咨询",
        "企业版和专业版有什么区别？",
        lambda d: "knowledge-retrieve" in d["skills_invoked"]
        and ("企业版" in d["response"] or "专业版" in d["response"]),
    ),
    (
        "E2E-002 建单",
        "服务器宕机了请尽快处理",
        lambda d: "ticket-create" in d["skills_invoked"] and "T-" in d["response"],
    ),
    (
        "E2E-003 查单",
        "查一下 T-001 的处理进度",
        lambda d: "ticket-query" in d["skills_invoked"]
        and ("T-001" in d["response"] or "in_progress" in d["response"]),
    ),
    (
        "E2E-003b 查看工单",
        "查看工单 T-001",
        lambda d: "ticket-query" in d["skills_invoked"]
        and ("in_progress" in d["response"] or "T-001" in d["response"]),
    ),
    (
        "E2E-003c 工单列表",
        "查看我的工单列表",
        lambda d: "ticket-query" in d["skills_invoked"] and "T-001" in d["response"],
    ),
    (
        "E2E-004 投诉转人工",
        "太差了，三次没解决，我要投诉",
        lambda d: "human-handoff" in d["skills_invoked"]
        or "转接" in d["response"]
        or "人工" in d["response"],
    ),
    (
        "E2E-007 Guardrail",
        "我的密码是abc123",
        lambda d: d.get("blocked") is True or "敏感" in d["response"],
    ),
]


def chat(message: str, session_id: str) -> dict:
    req = urllib.request.Request(
        API,
        data=json.dumps({"message": message, "session_id": session_id}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode())


def main() -> int:
    print("=== 主场景 API 冒烟 ===\n")
    failed = 0
    for name, message, check in SCENARIOS:
        sid = name.replace(" ", "-").lower()
        try:
            data = chat(message, sid)
        except urllib.error.URLError as e:
            print(f"[FAIL] {name} — 无法连接 {API}: {e}")
            failed += 1
            continue
        ok = check(data)
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {name}")
        print(f"  intent={data.get('intent')} skills={' -> '.join(data.get('skills_invoked') or [])}")
        preview = _safe((data.get("response") or "")[:120].replace("\n", " "))
        print(f"  reply={preview}...")
        if not ok:
            failed += 1
        print()
    if failed:
        print(f"完成：{failed} 项失败")
        return 1
    print("完成：ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
