# M3 验收清单（6/5–6/6）— Eval Harness + CI

## 交付项

| ID | 项 | 状态 |
|----|-----|------|
| M3-01 | Eval Runner 120 条五维断言 | ✅ |
| M3-02 | L1~L5 YAML 评测集 | ✅ |
| M3-03 | 通过率门禁 ≥85% | ✅（见 latest.json） |
| M3-04 | `scripts/run_eval.py` + CI workflow | ✅ |
| M3-05 | POST `/api/eval/run` + GET `/api/eval/report` | ✅ |
| M3-06 | 前端 `/eval` 报告页联调 | ✅ |
| M3-07 | Trace Replay Diff API + 前端 | ✅ |
| M3-08 | 12 Skill Prompt 骨架 | ✅ |
| M3-09 | `agent/` 薄封装模块 | ✅ |

## 验收命令

```bash
python scripts/generate_l1_cases.py
python scripts/generate_all_eval_cases.py
python scripts/run_eval.py --gate 0.85
pytest tests/test_eval_runner.py -q
```

## 通过标准

- 120 条评测通过率 ≥ 85%
- L4 Memory 20/20、L5 E2E 25/25
- CI workflow `.github/workflows/eval.yml` 可跑通

## 备注

- 评测在本地内存 Mock 环境运行，不依赖 LLM API
- 前端需 `BACKEND_URL` 指向 uvicorn 端口（默认 8000，Windows 冲突可用 8002）
