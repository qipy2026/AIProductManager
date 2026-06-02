"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import EvalCatalogItem from "@/components/EvalCatalogItem";
import TracePanel from "@/components/TracePanel";
import { getAttribution } from "@/lib/attributions";
import {
  assertionLabel,
  groupFailuresByAttribution,
  LAYER_COLORS,
  type EvalCaseResult,
  type EvalReport,
} from "@/lib/evalReport";

interface OpsSummary {
  badcase_count: number;
  trace_count: number;
  db_backend: string;
}

interface ReplayDiff {
  has_diff: boolean;
  changes: { field: string; before: unknown; after: unknown }[];
  current: { skills_invoked: string[]; response: string; intent: string };
}

type TabId = "overview" | "failures" | "catalog" | "replay";

function FailureItem({
  c,
  onReplay,
}: {
  c: EvalCaseResult;
  onReplay: (c: EvalCaseResult) => void;
}) {
  const att = getAttribution(c.attribution || "skill");
  return (
    <div className="ops-problem-item">
      <div className="ops-problem-head">
        <span className="ops-problem-case">{c.case_id}</span>
        <span className="ops-problem-eval">{c.layer}</span>
        {c.description && <span className="eval-case-desc">{c.description}</span>}
      </div>
      {c.message && (
        <p className="eval-case-input">
          输入：<code>{c.message}</code>
        </p>
      )}
      <ul className="eval-failure-list">
        {c.failures.map((f, i) => (
          <li key={i}>
            <span className="eval-assert-tag">{assertionLabel(f)}</span>
            {f}
          </li>
        ))}
      </ul>
      {c.fix_hint && (
        <p className="eval-fix-hint">
          <strong>修复方向：</strong>
          {c.fix_hint}
        </p>
      )}
      {att && (
        <p className="eval-fix-hint eval-fix-meta">
          归因 · {att.label} — {att.action}
        </p>
      )}
      <div className="eval-case-actions">
        <button type="button" className="ops-link-btn" onClick={() => onReplay(c)}>
          Replay 本条
        </button>
        {c.yaml_path && (
          <span className="ops-hint-inline">{c.yaml_path}</span>
        )}
      </div>
    </div>
  );
}

export default function EvalPanel() {
  const [report, setReport] = useState<EvalReport | null>(null);
  const [ops, setOps] = useState<OpsSummary | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");
  const [tab, setTab] = useState<TabId>("overview");
  const [filterLayer, setFilterLayer] = useState("all");
  const [filterAtt, setFilterAtt] = useState("all");
  const [catalogFilter, setCatalogFilter] = useState("all");
  const [expandedCaseId, setExpandedCaseId] = useState<string | null>(null);
  const [caseDetailCache, setCaseDetailCache] = useState<Record<string, Partial<EvalCaseResult>>>({});
  const [caseDetailLoading, setCaseDetailLoading] = useState(false);
  const [replayMsg, setReplayMsg] = useState("企业版和专业版有什么区别？");
  const [replayTrace, setReplayTrace] = useState("");
  const [replay, setReplay] = useState<ReplayDiff | null>(null);

  const load = useCallback(async () => {
    setError("");
    try {
      const [rRes, oRes] = await Promise.all([
        fetch("/api/eval/report"),
        fetch("/api/ops/summary"),
      ]);
      const data = await rRes.json();
      if (data.error) {
        setReport(null);
        setError("暂无评测报告，请点击「运行全量评测」");
        return;
      }
      setReport(data);
      if (oRes.ok) setOps(await oRes.json());
    } catch {
      setError("无法加载评测报告，请确认后端已启动");
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (!expandedCaseId) {
      setCaseDetailLoading(false);
      return;
    }
    const row = report?.results?.find((r) => r.case_id === expandedCaseId);
    if (row?.assertions && row?.input) {
      setCaseDetailLoading(false);
      return;
    }
    if (caseDetailCache[expandedCaseId]) {
      setCaseDetailLoading(false);
      return;
    }
    let cancelled = false;
    setCaseDetailLoading(true);
    (async () => {
      try {
        const res = await fetch(`/api/eval/cases/${encodeURIComponent(expandedCaseId)}`);
        if (cancelled) return;
        if (res.ok) {
          const detail = await res.json();
          setCaseDetailCache((prev) => ({ ...prev, [expandedCaseId]: detail }));
        }
      } catch {
        /* 降级为 report 行内数据 */
      } finally {
        if (!cancelled) setCaseDetailLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps -- 仅随展开 id 拉取，cache 命中时不重复请求
  }, [expandedCaseId, report?.results]);

  async function runEval() {
    setRunning(true);
    setError("");
    try {
      const res = await fetch("/api/eval/run", { method: "POST" });
      const data = await res.json();
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await load();
      if ((data.failed ?? 0) > 0) setTab("failures");
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
        body: JSON.stringify({
          message: replayMsg,
          trace_id: replayTrace.trim() || undefined,
        }),
      });
      if (!res.ok) throw new Error("replay failed");
      setReplay(await res.json());
    } catch {
      setError("Replay 失败");
    }
  }

  function openReplayCase(c: EvalCaseResult) {
    if (c.message) setReplayMsg(c.message);
    setReplayTrace("");
    setReplay(null);
    setTab("replay");
    setTimeout(
      () => document.getElementById("eval-replay-section")?.scrollIntoView({ behavior: "smooth" }),
      80
    );
  }

  const gate = report?.gate ?? 0.85;
  const gateOk = report?.gate_passed ?? (report ? report.pass_rate >= gate : false);
  const ratePct = report ? `${(report.pass_rate * 100).toFixed(1)}%` : "—";
  const failedCases = report?.failed_cases ?? report?.results?.filter((r) => !r.passed) ?? [];
  const groupedFailures = useMemo(() => groupFailuresByAttribution(failedCases), [failedCases]);

  const filteredFailures =
    filterAtt === "all"
      ? failedCases.filter((c) => filterLayer === "all" || c.layer === filterLayer)
      : failedCases.filter(
          (c) =>
            (c.attribution || "skill") === filterAtt &&
            (filterLayer === "all" || c.layer === filterLayer)
        );

  const catalogRows = (report?.results ?? []).filter(
    (r) => catalogFilter === "all" || r.layer === catalogFilter
  );

  function mergeCaseDetail(row: EvalCaseResult): EvalCaseResult {
    const cached = caseDetailCache[row.case_id];
    if (!cached) return row;
    return {
      ...row,
      description: cached.description ?? row.description,
      message:
        (cached.input?.message as string | undefined) ??
        row.message ??
        (row.input?.message as string | undefined),
      input: cached.input ?? row.input,
      assertions: cached.assertions ?? row.assertions,
      yaml_path: cached.yaml_path ?? row.yaml_path,
      layer: row.layer || cached.layer || "",
    };
  }

  function toggleCatalogCase(caseId: string) {
    setExpandedCaseId((prev) => (prev === caseId ? null : caseId));
  }

  const worstLayer = useMemo(() => {
    const ls = report?.layer_summary ?? [];
    return [...ls].filter((l) => l.total > 0).sort((a, b) => a.pass_rate - b.pass_rate)[0];
  }, [report]);

  return (
    <div className="ops-page eval-page">
      <header className="ops-header">
        <div>
          <h1 className="ops-title">Eval Harness 报告</h1>
          <p className="ops-subtitle">
            看全量现状 → 定位失败用例 → Replay 对比 → 运营后台回归
          </p>
        </div>
        <div className="ops-header-actions">
          <button type="button" className="ops-btn ops-btn-secondary" onClick={load}>
            刷新
          </button>
          <button
            type="button"
            className="ops-btn ops-btn-primary"
            disabled={running}
            onClick={runEval}
          >
            {running ? "评测中…" : "运行全量评测"}
          </button>
        </div>
      </header>

      {error && <div className="ops-alert ops-alert-error">{error}</div>}

      {!report && !error && <div className="ops-empty">加载中…</div>}

      {report && (
        <>
          <section className="ops-kpi-grid">
            <div className={`ops-kpi-card ${gateOk ? "" : "ops-kpi-warn"}`}>
              <div className="ops-kpi-label">总通过率</div>
              <div className="ops-kpi-value">
                {report.passed}/{report.total}
              </div>
              <div className="ops-kpi-hint">
                <span className={gateOk ? "eval-gate-ok" : "eval-gate-fail"}>{ratePct}</span>
                {" · "}门禁 ≥{(gate * 100).toFixed(0)}% {gateOk ? "PASS" : "FAIL"}
              </div>
            </div>
            <div className={`ops-kpi-card ${report.failed > 0 ? "ops-kpi-warn" : ""}`}>
              <div className="ops-kpi-label">失败用例</div>
              <div className="ops-kpi-value">{report.failed}</div>
              <div className="ops-kpi-hint">
                {worstLayer
                  ? `最弱层 ${worstLayer.label} ${(worstLayer.pass_rate * 100).toFixed(0)}%`
                  : "全部分层通过"}
              </div>
            </div>
            <div className="ops-kpi-card">
              <div className="ops-kpi-label">评测集规模</div>
              <div className="ops-kpi-value">{report.case_catalog_size ?? report.total}</div>
              <div className="ops-kpi-hint">L1~L5 共 {Object.keys(report.by_layer).length} 层</div>
            </div>
            <div className="ops-kpi-card">
              <div className="ops-kpi-label">同步运营后台</div>
              <div className="ops-kpi-value ops-kpi-value-sm">{ops?.badcase_count ?? "—"}</div>
              <div className="ops-kpi-hint">
                Bad Case · <a href="/ops">去运营后台 →</a>
              </div>
            </div>
          </section>

          {(report.layer_summary?.length ?? 0) > 0 && (
            <section className="ops-att-overview">
              <div className="ops-att-overview-head">
                <span className="ops-section-label">分层通过率（L1 → L5）</span>
                {report.failed > 0 && (
                  <button type="button" className="ops-link-btn" onClick={() => setTab("failures")}>
                    查看 {report.failed} 条失败 →
                  </button>
                )}
              </div>
              <div className="ops-att-bar">
                {(report.layer_summary ?? []).map((l) => {
                  const failW = l.total ? l.failed : 0;
                  const passW = l.total ? l.passed : 0;
                  return (
                    <div key={l.layer} className="eval-layer-segment-wrap" style={{ flex: l.total || 1 }}>
                      {passW > 0 && (
                        <button
                          type="button"
                          className="ops-att-segment eval-layer-pass"
                          style={{ flex: passW, background: LAYER_COLORS[l.layer] || "#94a3b8" }}
                          title={`${l.label} 通过 ${l.passed}`}
                          onClick={() => {
                            setCatalogFilter(l.layer);
                            setTab("catalog");
                          }}
                        />
                      )}
                      {failW > 0 && (
                        <button
                          type="button"
                          className="ops-att-segment eval-layer-fail"
                          style={{ flex: failW }}
                          title={`${l.label} 失败 ${l.failed}`}
                          onClick={() => {
                            setFilterLayer(l.layer);
                            setTab("failures");
                          }}
                        />
                      )}
                    </div>
                  );
                })}
              </div>
              <div className="ops-att-legend">
                {(report.layer_summary ?? []).map((l) => (
                  <button
                    key={l.layer}
                    type="button"
                    className={`ops-att-legend-item ${filterLayer === l.layer ? "active" : ""}`}
                    onClick={() =>
                      setFilterLayer(filterLayer === l.layer ? "all" : l.layer)
                    }
                  >
                    <span className="ops-att-dot" style={{ background: LAYER_COLORS[l.layer] }} />
                    {l.label}
                    <strong>
                      {l.passed}/{l.total}
                    </strong>
                    <span className="ops-att-pct">{(l.pass_rate * 100).toFixed(0)}%</span>
                  </button>
                ))}
              </div>
            </section>
          )}

          <nav className="ops-tabs">
            {(
              [
                ["overview", "概览"],
                ["failures", `失败用例 (${failedCases.length})`],
                ["catalog", `全量明细 (${report.total})`],
                ["replay", "Replay 诊断"],
              ] as const
            ).map(([id, label]) => (
              <button
                key={id}
                type="button"
                className={`ops-tab ${tab === id ? "active" : ""}`}
                onClick={() => setTab(id)}
              >
                {label}
              </button>
            ))}
          </nav>

          {tab === "overview" && (
            <section className="ops-panel">
              <div className="eval-overview-grid">
                {(report.layer_summary ?? []).map((l) => (
                  <div key={l.layer} className="eval-layer-card">
                    <div className="eval-layer-card-head">
                      <span className="ops-att-dot" style={{ background: LAYER_COLORS[l.layer] }} />
                      <strong>{l.label}</strong>
                      <span className={`eval-layer-rate ${l.failed > 0 ? "warn" : ""}`}>
                        {l.passed}/{l.total}
                      </span>
                    </div>
                    <p className="eval-layer-desc">{l.desc}</p>
                    <p className="eval-layer-focus">关注：{l.focus}</p>
                    {l.failed > 0 && (
                      <button
                        type="button"
                        className="ops-link-btn"
                        onClick={() => {
                          setFilterLayer(l.layer);
                          setTab("failures");
                        }}
                      >
                        {l.failed} 条失败 →
                      </button>
                    )}
                  </div>
                ))}
              </div>

              {Object.keys(report.failure_by_assertion ?? {}).length > 0 && (
                <div className="eval-assert-overview">
                  <h3 className="eval-section-title">失败断言分布</h3>
                  <div className="ops-filter-row">
                    {Object.entries(report.failure_by_assertion ?? {})
                      .sort((a, b) => b[1] - a[1])
                      .map(([k, n]) => (
                        <span key={k} className="badcase-filter-chip">
                          {k} <strong>{n}</strong>
                        </span>
                      ))}
                  </div>
                </div>
              )}

              <div className="eval-workflow">
                <h3 className="eval-section-title">修复闭环</h3>
                <ol className="eval-workflow-steps">
                  <li>在「失败用例」按归因层查看 fix_hint</li>
                  <li>改 Skill / Prompt / 知识库后点 Replay 对比</li>
                  <li>运行全量评测确认门禁 PASS</li>
                  <li>
                    到 <a href="/ops">运营后台</a> 确认 Bad Case 已归类并清空
                  </li>
                </ol>
              </div>
            </section>
          )}

          {tab === "failures" && (
            <section className="ops-panel">
              {failedCases.length === 0 ? (
                <div className="ops-empty">
                  <p>全部用例通过，门禁 OK。</p>
                </div>
              ) : (
                <>
                  <div className="ops-filter-row">
                    <button
                      type="button"
                      className={`badcase-filter-chip ${filterLayer === "all" ? "active" : ""}`}
                      onClick={() => setFilterLayer("all")}
                    >
                      全部 {failedCases.length}
                    </button>
                    {(report.layer_summary ?? [])
                      .filter((l) => l.failed > 0)
                      .map((l) => (
                        <button
                          key={l.layer}
                          type="button"
                          className={`badcase-filter-chip ${filterLayer === l.layer ? "active" : ""}`}
                          onClick={() => setFilterLayer(l.layer)}
                        >
                          {l.layer} {l.failed}
                        </button>
                      ))}
                  </div>
                  <div className="ops-filter-row">
                    <button
                      type="button"
                      className={`badcase-filter-chip ${filterAtt === "all" ? "active" : ""}`}
                      onClick={() => setFilterAtt("all")}
                    >
                      全部归因
                    </button>
                    {groupedFailures.map((g) => (
                      <button
                        key={g.layer.key}
                        type="button"
                        className={`badcase-filter-chip ${filterAtt === g.layer.key ? "active" : ""}`}
                        onClick={() => setFilterAtt(g.layer.key)}
                      >
                        <span className="ops-att-dot" style={{ background: g.layer.color }} />
                        {g.layer.label} {g.items.length}
                      </button>
                    ))}
                  </div>

                  {filterAtt === "all"
                    ? groupedFailures.map((group) => {
                        const items = group.items.filter(
                          (c) => filterLayer === "all" || c.layer === filterLayer
                        );
                        if (!items.length) return null;
                        return (
                          <div key={group.layer.key} className="ops-problem-group">
                            <div className="ops-problem-group-head">
                              <span className="ops-att-dot" style={{ background: group.layer.color }} />
                              <div>
                                <strong>{group.layer.label}</strong>
                                <span className="ops-problem-group-sub">
                                  {group.layer.symptom} · {group.layer.action}
                                </span>
                              </div>
                              <span className="ops-problem-group-count">{items.length}</span>
                            </div>
                            <div className="ops-problem-list">
                              {items.map((c) => (
                                <FailureItem key={c.case_id} c={c} onReplay={openReplayCase} />
                              ))}
                            </div>
                          </div>
                        );
                      })
                    : (
                        <div className="ops-problem-list">
                          {filteredFailures.map((c) => (
                            <FailureItem key={c.case_id} c={c} onReplay={openReplayCase} />
                          ))}
                        </div>
                      )}
                </>
              )}
            </section>
          )}

          {tab === "catalog" && (
            <section className="ops-panel">
              <p className="ops-section-desc">点击用例行展开输入、YAML 断言与失败原因；与「失败用例」Tab 同构。</p>
              <div className="ops-filter-row">
                {["all", "L1", "L2", "L3", "L4", "L5"].map((l) => (
                  <button
                    key={l}
                    type="button"
                    className={`badcase-filter-chip ${catalogFilter === l ? "active" : ""}`}
                    onClick={() => setCatalogFilter(l)}
                  >
                    {l === "all" ? `全部 ${report.total}` : l}
                  </button>
                ))}
              </div>
              <div className="eval-catalog-list">
                {catalogRows.map((r) => (
                  <EvalCatalogItem
                    key={r.case_id}
                    c={mergeCaseDetail(r)}
                    expanded={expandedCaseId === r.case_id}
                    loading={expandedCaseId === r.case_id && caseDetailLoading}
                    onToggle={() => toggleCatalogCase(r.case_id)}
                    onReplay={openReplayCase}
                  />
                ))}
              </div>
            </section>
          )}

          {tab === "replay" && (
            <section id="eval-replay-section" className="ops-panel">
              <p className="ops-section-desc">
                用相同输入重跑 Harness，对比 Skills / 回复是否与 baseline Trace 一致。
              </p>
              <div className="eval-replay-form">
                <input
                  className="ops-input ops-input-grow"
                  value={replayMsg}
                  onChange={(e) => setReplayMsg(e.target.value)}
                  placeholder="重跑消息"
                />
                <input
                  className="ops-input"
                  value={replayTrace}
                  onChange={(e) => setReplayTrace(e.target.value)}
                  placeholder="baseline trace_id（可选）"
                />
                <button type="button" className="ops-btn ops-btn-primary" onClick={doReplay}>
                  Replay
                </button>
              </div>
              {replay && (
                <div className="eval-replay-result">
                  <p>
                    差异：<strong>{replay.has_diff ? "有" : "无"}</strong>
                    {" · "}Skills: {replay.current.skills_invoked.join(" → ") || "—"}
                  </p>
                  <p className="eval-replay-response">{replay.current.response.slice(0, 400)}</p>
                  {replay.changes.map((c, i) => (
                    <div key={i} className="eval-replay-change">
                      <code>{c.field}</code>: {JSON.stringify(c.before)} → {JSON.stringify(c.after)}
                    </div>
                  ))}
                </div>
              )}
              <div className="eval-replay-trace">
                <TracePanel traceId={replayTrace} onTraceIdChange={setReplayTrace} />
              </div>
            </section>
          )}
        </>
      )}
    </div>
  );
}
