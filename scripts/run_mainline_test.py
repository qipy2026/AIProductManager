#!/usr/bin/env python3
"""主线用例 — E2E-001 知识咨询带引用."""

from __future__ import annotations

import json
import sys
import urllib.request

API = "http://localhost:8002/api/chat"
MESSAGE = "企业版和专业版有什么区别？"


def main() -> int:
    req = urllib.request.Request(
        API,
        data=json.dumps({"message": MESSAGE, "session_id": "mainline-001"}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode())

    print("=== E2E-001 主线：知识咨询带引用 ===")
    print(f"intent: {data['intent']} ({data['confidence']:.0%})")
    print(f"skills: {' -> '.join(data['skills_invoked'])}")
    print(f"trace: {data['trace_id']}")
    print(f"sources: {len(data.get('sources') or [])} 条")
    text = data["response"].replace("\U0001f4ce", "[来源]")
    print("--- Agent 回复 ---")
    print(text)
    print("--- 断言 ---")
    ok = (
        ("企业版" in data["response"] or "专业版" in data["response"])
        and "knowledge-retrieve" in data["skills_invoked"]
    )
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
