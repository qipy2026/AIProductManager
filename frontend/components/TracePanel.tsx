"use client";

import { useCallback, useEffect, useState } from "react";

export interface TraceStep {
  name: string;
  layer: string;
  duration_ms?: number;
  output_summary?: string;
}

export interface TraceData {
  trace_id: string;
  session_id: string;
  duration_ms: number;
  skills_invoked: string[];
  steps: TraceStep[];
  intent?: string;
  response?: string;
}

interface Props {
  traceId?: string;
  onTraceIdChange?: (id: string) => void;
  compact?: boolean;
}

export default function TracePanel({ traceId: externalId, onTraceIdChange, compact }: Props) {
  const [traceId, setTraceId] = useState(externalId ?? "");
  const [trace, setTrace] = useState<TraceData | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (externalId?.trim()) {
      setTraceId(externalId);
      queryTrace(externalId.trim());
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [externalId]);

  const updateId = useCallback(
    (id: string) => {
      setTraceId(id);
      onTraceIdChange?.(id);
    },
    [onTraceIdChange]
  );

  async function queryTrace(id: string) {
    if (!id) return;
    setLoading(true);
    setError("");
    setTrace(null);
    try {
      const res = await fetch(`/api/traces/${encodeURIComponent(id)}`);
      if (!res.ok) {
        setError(res.status === 404 ? "未找到该 trace_id" : `查询失败 (${res.status})`);
        return;
      }
      setTrace(await res.json());
    } catch {
      setError("连接后端失败，请确认 uvicorn 已启动");
    } finally {
      setLoading(false);
    }
  }

  function query() {
    queryTrace(traceId.trim());
  }

  return (
    <div className={compact ? "ops-trace-compact" : ""}>
      <div className="ops-trace-search">
        <input
          className="ops-input"
          value={traceId}
          onChange={(e) => updateId(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && query()}
          placeholder="粘贴 trace_id 诊断链路…"
        />
        <button type="button" className="ops-btn ops-btn-primary" onClick={query} disabled={loading}>
          {loading ? "…" : "查询"}
        </button>
      </div>
      {error && <p className="ops-error">{error}</p>}
      {trace && (
        <div className="ops-trace-result">
          <div className="ops-trace-meta">
            <code>{trace.trace_id.slice(0, 8)}…</code>
            <span>{trace.duration_ms}ms</span>
            {trace.intent && <span>intent: {trace.intent}</span>}
          </div>
          {trace.skills_invoked.length > 0 && (
            <div className="ops-trace-skills">
              {trace.skills_invoked.map((s) => (
                <span key={s} className="ops-skill-chip">
                  {s}
                </span>
              ))}
            </div>
          )}
          <ol className="ops-trace-timeline">
            {trace.steps.map((s, i) => (
              <li key={i} className="ops-trace-step">
                <span className="ops-trace-step-layer">{s.layer}</span>
                <span className="ops-trace-step-name">{s.name}</span>
                {s.duration_ms != null && s.duration_ms > 0 && (
                  <span className="ops-trace-step-ms">{s.duration_ms.toFixed(0)}ms</span>
                )}
                {s.output_summary && (
                  <div className="ops-trace-step-out">{s.output_summary}</div>
                )}
              </li>
            ))}
          </ol>
        </div>
      )}
      {!trace && !error && (
        <p className="ops-hint">从下方问题清单点击 trace，或从对话页复制 trace_id 粘贴查询</p>
      )}
    </div>
  );
}
