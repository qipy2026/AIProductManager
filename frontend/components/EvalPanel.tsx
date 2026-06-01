"use client";

import { useCallback, useEffect, useState } from "react";

interface LayerStats {
  passed: number;
  failed: number;
  total: number;
}

interface EvalReport {
  total: number;
  passed: number;
  failed: number;
  pass_rate: number;
  gate_passed?: boolean;
  by_layer: Record<string, LayerStats>;
  results?: { case_id: string; layer: string; passed: boolean; failures: string[] }[];
  error?: string;
}

interface ReplayDiff {
  has_diff: boolean;
  changes: { field: string; before: unknown; after: unknown }[];
  current: { skills_invoked: string[]; response: string; intent: string };
}

export default function EvalPanel() {
  const [report, setReport] = useState<EvalReport | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");
  const [replayMsg, setReplayMsg] = useState("企业版和专业版区别");
  const [replayTrace, setReplayTrace] = useState("");
  const [replay, setReplay] = useState<ReplayDiff | null>(null);

  const loadReport = useCallback(async () => {
    try {
      const res = await fetch("/api/eval/report");
      const data = await res.json();
      if (data.error) {
        setReport(null);
        return;
      }
      setReport(data);
    } catch {
      setError("无法加载评测报告");
    }
  }, []);

  useEffect(() => {
    loadReport();
  }, [loadReport]);

  async function runEval() {
    setRunning(true);
    setError("");
    try {
      const res = await fetch("/api/eval/run", { method: "POST" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadReport();
    } catch {
      setError("评测运行失败，请确认后端已启动");
    } finally {
      setRunning(false);
    }
  }

  async function doReplay() {
    setReplay(null);
    try {
      const res = await fetch("/api/eval/replay", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: replayMsg, trace_id: replayTrace.trim() || undefined }),
      });
      if (!res.ok) throw new Error("replay failed");
      setReplay(await res.json());
    } catch {
      setError("Replay 失败");
    }
  }

  const rate = report ? `${(report.pass_rate * 100).toFixed(1)}%` : "—";
  const gateOk = report?.gate_passed ?? report?.pass_rate >= 0.85;

  return (
    <div>
      <div className="card" style={{ display: "flex", alignItems: "center", gap: 16 }}>
        <div style={{ flex: 1 }}>
          <strong>总通过率</strong>
          <div style={{ fontSize: 28, marginTop: 8 }}>
            {report ? `${report.passed}/${report.total}` : "—"}{" "}
            <span style={{ fontSize: 18, color: gateOk ? "#080" : "#c00" }}>({rate})</span>
          </div>
        </div>
        <button onClick={runEval} disabled={running} style={{ padding: "10px 20px" }}>
          {running ? "运行中…" : "运行评测"}
        </button>
      </div>

      {error && <p style={{ color: "#c00" }}>{error}</p>}

      {report?.by_layer && (
        <>
          <h2>分层结果</h2>
          {Object.entries(report.by_layer)
            .sort(([a], [b]) => a.localeCompare(b))
            .map(([layer, s]) => (
              <div key={layer} className="card">
                {layer} · {s.passed}/{s.total}{" "}
                <span className="badge">{s.total ? `${((s.passed / s.total) * 100).toFixed(0)}%` : "—"}</span>
                {s.failed > 0 && (
                  <span style={{ marginLeft: 8, fontSize: 13, color: "#888" }}>{s.failed} 失败</span>
                )}
              </div>
            ))}
        </>
      )}

      {report?.results && report.results.some((r) => !r.passed) && (
        <>
          <h2>失败用例</h2>
          <div className="panel" style={{ maxHeight: 240, overflow: "auto", fontSize: 13 }}>
            {report.results
              .filter((r) => !r.passed)
              .map((r) => (
                <div key={r.case_id} style={{ marginBottom: 8 }}>
                  <strong>{r.case_id}</strong> ({r.layer}): {r.failures.join("; ")}
                </div>
              ))}
          </div>
        </>
      )}

      <h2>Trace Replay Diff</h2>
      <div className="panel">
        <div style={{ display: "flex", gap: 8, marginBottom: 8, flexWrap: "wrap" }}>
          <input
            value={replayMsg}
            onChange={(e) => setReplayMsg(e.target.value)}
            placeholder="重跑消息"
            style={{ flex: 2, minWidth: 200, padding: 8, borderRadius: 4, border: "1px solid #ccc" }}
          />
          <input
            value={replayTrace}
            onChange={(e) => setReplayTrace(e.target.value)}
            placeholder="可选 baseline trace_id"
            style={{ flex: 1, minWidth: 160, padding: 8, borderRadius: 4, border: "1px solid #ccc" }}
          />
          <button onClick={doReplay} style={{ padding: "8px 16px" }}>
            Replay
          </button>
        </div>
        {replay && (
          <div style={{ fontSize: 13 }}>
            <p>
              差异：<strong>{replay.has_diff ? "有" : "无"}</strong> · Skills:{" "}
              {replay.current.skills_invoked.join(", ")}
            </p>
            {replay.changes.map((c, i) => (
              <div key={i} style={{ marginTop: 8, color: "#444" }}>
                <code>{c.field}</code>: {JSON.stringify(c.before)} → {JSON.stringify(c.after)}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
