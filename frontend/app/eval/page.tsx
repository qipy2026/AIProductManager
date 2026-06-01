import EvalPanel from "@/components/EvalPanel";

export default function EvalPage() {
  return (
    <div>
      <h1>Eval Harness 报告</h1>
      <p style={{ color: "#666" }}>120 条评测集 · 目标通过率 ≥85% · CI 门禁已配置</p>
      <EvalPanel />
    </div>
  );
}
