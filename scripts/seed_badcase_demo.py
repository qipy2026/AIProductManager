"""写入七层归因演示 Bad Case."""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main() -> int:
    from backend.badcase.demo_samples import DEMO_BADCASES, seed_demo_badcases
    from backend.badcase.attribution_infer import infer_attribution_from_badcase
    from backend.db.store import get_ops_store

    print(">>> 校验七层归因推断 …")
    expected = {s["attribution"] for s in DEMO_BADCASES}
    for s in DEMO_BADCASES:
        got = infer_attribution_from_badcase(s, force=True)
        ok = got == s["attribution"]
        mark = "OK" if ok else "MISMATCH"
        print(f"  [{mark}] {s['attribution']:10} -> {got:10}  {s['case_id']}")
        if not ok:
            return 1
    if len(expected) != 7:
        print(f"ERROR: 期望 7 个不同归因，实际 {len(expected)}")
        return 1

    store = get_ops_store()
    if not store:
        print("ERROR: 未配置 OPS_DB，请设置 OPS_DB=sqlite 或 mysql")
        return 1
    store.init_db()
    result = seed_demo_badcases(store)
    print(f">>> 已写入 {result['added']} 条演示 Bad Case（清除旧演示 {result['deleted']} 条）")
    for k, v in sorted(result["by_attribution"].items()):
        print(f"    {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
