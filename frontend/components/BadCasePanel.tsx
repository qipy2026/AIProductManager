"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import BadCaseCatalogItem from "@/components/BadCaseCatalogItem";
import {
  ATTRIBUTION_LAYERS,
  countAllAttributions,
  getAttribution,
  groupByAttribution,
  normalizeAttributionKey,
  OTHER_ATTRIBUTION,
  type BadCaseItem,
} from "@/lib/badcase";

type TabId = "overview" | "all" | "pending";
type AttFilter = "all" | string;
type EvalFilter = "all" | string;

interface Props {
  embedded?: boolean;
  /** 父级刷新时递增，触发 Bad Case 列表重载 */
  refreshKey?: number;
  onTraceClick?: (traceId: string) => void;
  onCountChange?: (count: number) => void;
}

export default function BadCasePanel({
  embedded = false,
  refreshKey,
  onTraceClick,
  onCountChange,
}: Props) {
  const [items, setItems] = useState<BadCaseItem[]>([]);
  const [error, setError] = useState("");
  const [reclassifyMsg, setReclassifyMsg] = useState("");
  const [loading, setLoading] = useState(true);
  const [reclassifying, setReclassifying] = useState(false);
  const [tab, setTab] = useState<TabId>("all");
  const [attFilter, setAttFilter] = useState<AttFilter>("all");
  const [evalFilter, setEvalFilter] = useState<EvalFilter>("all");
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [seeding, setSeeding] = useState(false);
  const [seedMsg, setSeedMsg] = useState("");
  const [form, setForm] = useState({ trace_id: "", case_id: "", layer: "", attribution: "skill", note: "" });

  const selectedLayer = getAttribution(form.attribution);

  const load = useCallback(async () => {
    setError("");
    setLoading(true);
    try {
      const res = await fetch("/api/ops/badcases?limit=500");
      if (!res.ok) throw new Error(String(res.status));
      const data = await res.json();
      const list = data.items ?? [];
      setItems(list);
      onCountChange?.(list.length);
    } catch {
      setError("加载 Bad Case 失败，请确认后端已启动且 OPS_DB 已配置");
      setItems([]);
      onCountChange?.(0);
    } finally {
      setLoading(false);
    }
  }, [onCountChange]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (refreshKey !== undefined && refreshKey > 0) {
      load();
    }
  }, [refreshKey, load]);

  async function seedDemo() {
    setSeeding(true);
    setSeedMsg("");
    setError("");
    try {
      const res = await fetch("/api/ops/badcases/seed-demo", { method: "POST" });
      const data = await res.json();
      if (!res.ok || !data.ok) {
        setError(data.error || "载入演示数据失败");
        return;
      }
      setSeedMsg(`已载入七层演示 ${data.added} 条（${Object.keys(data.by_attribution || {}).length} 个归因层）`);
      setAttFilter("all");
      setTab("all");
      load();
    } catch {
      setError("载入演示数据请求失败");
    } finally {
      setSeeding(false);
    }
  }

  async function submitBadcase() {
    if (!form.attribution) return;
    const res = await fetch("/api/ops/badcases", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });
    const data = await res.json();
    if (!res.ok || !data.ok) {
      setError(data.error || "提交失败");
      return;
    }
    setForm({ trace_id: "", case_id: "", layer: "", attribution: "skill", note: "" });
    setFormOpen(false);
    load();
  }

  async function reclassifyAll() {
    setReclassifying(true);
    setReclassifyMsg("");
    try {
      const res = await fetch("/api/ops/badcases/reclassify", { method: "POST" });
      const data = await res.json();
      if (!res.ok || !data.ok) {
        setError(data.error || "归类失败");
        return;
      }
      setReclassifyMsg(`已归类 ${data.total} 条，更新 ${data.updated} 条`);
      setAttFilter("all");
      load();
    } catch {
      setError("归类请求失败");
    } finally {
      setReclassifying(false);
    }
  }

  async function updateAttribution(id: number, attribution: string) {
    const res = await fetch(`/api/ops/badcases/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ attribution }),
    });
    const data = await res.json();
    if (!res.ok || !data.ok) {
      setError(data.error || "更新归因失败");
      return;
    }
    load();
  }

  const attCounts = useMemo(() => countAllAttributions(items), [items]);
  const grouped = useMemo(() => groupByAttribution(items), [items]);
  const pendingItems = useMemo(
    () => items.filter((b) => normalizeAttributionKey(b.attribution) === "other"),
    [items]
  );
  const pendingCount = pendingItems.length;

  const listSource = tab === "pending" ? pendingItems : items;

  const filteredItems = useMemo(() => {
    return listSource.filter((b) => {
      if (attFilter !== "all" && normalizeAttributionKey(b.attribution) !== attFilter) return false;
      if (evalFilter !== "all" && b.layer !== evalFilter) return false;
      return true;
    });
  }, [listSource, attFilter, evalFilter]);

  const evalLayers = useMemo(() => {
    const s = new Set<string>();
    for (const b of items) if (b.layer) s.add(b.layer);
    return [...s].sort();
  }, [items]);

  const topAtt = useMemo(() => {
    if (!grouped.length) return null;
    return [...grouped].sort((a, b) => b.items.length - a.items.length)[0];
  }, [grouped]);

  const totalBad = items.length || 1;

  function toggleExpand(id?: number) {
    if (!id) return;
    setExpandedId((prev) => (prev === id ? null : id));
  }

  const statusBar =
    items.length > 0 ? (
      <section className="ops-att-overview">
        <div className="ops-att-overview-head">
          <span className="ops-section-label">七层归因分布</span>
          <button
            type="button"
            className="ops-link-btn"
            disabled={reclassifying}
            onClick={reclassifyAll}
          >
            {reclassifying ? "归类中…" : "一键归类"}
          </button>
        </div>
        <div className="ops-att-bar">
          {ATTRIBUTION_LAYERS.map((l) => {
            const n = attCounts[l.key] ?? 0;
            if (!n) return null;
            return (
              <button
                key={l.key}
                type="button"
                className="ops-att-segment"
                style={{ flex: n, background: l.color }}
                title={`${l.label} ${n}`}
                onClick={() => {
                  setAttFilter(l.key);
                  setTab("all");
                }}
              />
            );
          })}
        </div>
        <div className="ops-att-legend">
          {ATTRIBUTION_LAYERS.map((l) => {
            const n = attCounts[l.key] ?? 0;
            return (
              <button
                key={l.key}
                type="button"
                className={`ops-att-legend-item ${attFilter === l.key ? "active" : ""} ${n === 0 ? "muted" : ""}`}
                onClick={() => setAttFilter(attFilter === l.key ? "all" : l.key)}
                disabled={n === 0}
              >
                <span className="ops-att-dot" style={{ background: l.color }} />
                {l.label}
                <strong>{n}</strong>
                {n > 0 && (
                  <span className="ops-att-pct">{Math.round((n / totalBad) * 100)}%</span>
                )}
              </button>
            );
          })}
          {pendingCount > 0 && (
            <button
              type="button"
              className={`ops-att-legend-item ${attFilter === "other" ? "active" : ""}`}
              onClick={() => {
                setAttFilter("other");
                setTab("pending");
              }}
            >
              <span className="ops-att-dot" style={{ background: OTHER_ATTRIBUTION.color }} />
              {OTHER_ATTRIBUTION.label}
              <strong>{pendingCount}</strong>
            </button>
          )}
        </div>
      </section>
    ) : null;

  const listSection = (
    <>
      <div className="ops-filter-row">
        <button
          type="button"
          className={`badcase-filter-chip ${attFilter === "all" ? "active" : ""}`}
          onClick={() => setAttFilter("all")}
        >
          全部归因 {listSource.length}
        </button>
        {ATTRIBUTION_LAYERS.map((l) => {
          const n = listSource.filter((b) => normalizeAttributionKey(b.attribution) === l.key).length;
          return (
            <button
              key={l.key}
              type="button"
              className={`badcase-filter-chip ${attFilter === l.key ? "active" : ""}`}
              onClick={() => setAttFilter(l.key)}
              disabled={n === 0}
            >
              <span className="ops-att-dot" style={{ background: l.color }} />
              {l.label} {n}
            </button>
          );
        })}
      </div>
      {evalLayers.length > 0 && (
        <div className="ops-filter-row">
          <button
            type="button"
            className={`badcase-filter-chip ${evalFilter === "all" ? "active" : ""}`}
            onClick={() => setEvalFilter("all")}
          >
            全部评测层
          </button>
          {evalLayers.map((l) => {
            const n = listSource.filter((b) => b.layer === l).length;
            return (
              <button
                key={l}
                type="button"
                className={`badcase-filter-chip ${evalFilter === l ? "active" : ""}`}
                onClick={() => setEvalFilter(l)}
              >
                {l} {n}
              </button>
            );
          })}
        </div>
      )}
      <div className="eval-catalog-list" data-testid="badcase-list">
        {filteredItems.map((b) => (
          <BadCaseCatalogItem
            key={b.id ?? `${b.case_id}-${b.trace_id}`}
            item={b}
            expanded={expandedId === b.id}
            onToggle={() => toggleExpand(b.id)}
            onTraceClick={onTraceClick}
            onAttributionChange={updateAttribution}
          />
        ))}
      </div>
      {filteredItems.length === 0 && !loading && (
        <div className="ops-empty">
          <p>当前筛选下暂无 Bad Case。</p>
        </div>
      )}
    </>
  );

  return (
    <div className={`badcase-panel ${embedded ? "badcase-panel-embedded" : ""}`}>
      {!embedded && (
        <header className="ops-header">
          <div>
            <h1 className="ops-title">Bad Case · 七层归因</h1>
            <p className="ops-subtitle">Eval 失败自动入库 → 七层归类 → 查 Trace → 修复回归</p>
          </div>
          <div className="ops-header-actions">
            <button type="button" className="ops-btn ops-btn-secondary" onClick={load} disabled={loading}>
              刷新
            </button>
          </div>
        </header>
      )}

      {error && <div className="ops-alert ops-alert-error">{error}</div>}
      {reclassifyMsg && <div className="ops-alert ops-alert-success">{reclassifyMsg}</div>}
      {seedMsg && <div className="ops-alert ops-alert-success">{seedMsg}</div>}

      {loading && !error && <div className="ops-empty">加载中…</div>}

      {!loading && (
        <>
          {!embedded && (
            <section className="ops-kpi-grid">
              <div className={`ops-kpi-card ${items.length > 0 ? "ops-kpi-warn" : ""}`}>
                <div className="ops-kpi-label">Bad Case 总数</div>
                <div className="ops-kpi-value">{items.length}</div>
                <div className="ops-kpi-hint">Eval 失败 + 人工登记</div>
              </div>
              <div className={`ops-kpi-card ${pendingCount > 0 ? "ops-kpi-warn" : ""}`}>
                <div className="ops-kpi-label">待归类</div>
                <div className="ops-kpi-value">{pendingCount}</div>
                <div className="ops-kpi-hint">需一键归类或人工确认</div>
              </div>
              <div className="ops-kpi-card">
                <div className="ops-kpi-label">主要归因</div>
                <div className="ops-kpi-value ops-kpi-value-sm">{topAtt?.layer.label ?? "—"}</div>
                <div className="ops-kpi-hint">
                  {topAtt ? `${topAtt.items.length} 条` : "暂无异常"}
                </div>
              </div>
              <div className="ops-kpi-card">
                <div className="ops-kpi-label">关联评测</div>
                <div className="ops-kpi-value">{items.filter((b) => b.case_id).length}</div>
                <div className="ops-kpi-hint">
                  <a href="/eval">评测报告 →</a>
                </div>
              </div>
            </section>
          )}

          {statusBar}

          {pendingCount > 0 && (
            <div className="ops-alert ops-alert-warn">
              有 {pendingCount} 条待归类，点击「一键归类」或展开后手动调整归因。
            </div>
          )}

          <nav className="ops-tabs">
            {(
              [
                ["overview", "概览"],
                ["all", `全部 Bad Case (${items.length})`],
                ["pending", `待归类 (${pendingCount})`],
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
                {ATTRIBUTION_LAYERS.map((l) => {
                  const n = attCounts[l.key] ?? 0;
                  return (
                    <div key={l.key} className="eval-layer-card">
                      <div className="eval-layer-card-head">
                        <span className="ops-att-dot" style={{ background: l.color }} />
                        <strong>{l.label}</strong>
                        <span className={`eval-layer-rate ${n > 0 ? "warn" : ""}`}>{n}</span>
                      </div>
                      <p className="eval-layer-desc">{l.symptom}</p>
                      <p className="eval-layer-focus">处理：{l.action}</p>
                      {n > 0 && (
                        <button
                          type="button"
                          className="ops-link-btn"
                          onClick={() => {
                            setAttFilter(l.key);
                            setTab("all");
                          }}
                        >
                          查看 {n} 条 →
                        </button>
                      )}
                    </div>
                  );
                })}
              </div>
              <div className="eval-workflow">
                <h3 className="eval-section-title">归因闭环</h3>
                <ol className="eval-workflow-steps">
                  <li>
                    <a href="/eval">运行全量评测</a>，失败用例自动写入 Bad Case
                  </li>
                  <li>「一键归类」将 eval_failure 映射到七层</li>
                  <li>展开条目查看 fix_hint，跳转 Trace 定位链路</li>
                  <li>修复后重跑 Eval，确认 Bad Case 清空</li>
                </ol>
                <button
                  type="button"
                  className="ops-btn ops-btn-secondary"
                  style={{ marginTop: 12 }}
                  disabled={seeding}
                  onClick={seedDemo}
                >
                  {seeding ? "载入中…" : "载入七层演示（每层 1 条）"}
                </button>
              </div>
            </section>
          )}

          {(tab === "all" || tab === "pending") && (
            <section className="ops-panel">
              <p className="ops-section-desc">
                点击行展开失败断言、七层归因与修复建议；可手动调整归因层级。
              </p>
              {items.length === 0 ? (
                <div className="ops-empty">
                  <p>暂无 Bad Case，系统运行正常。</p>
                  <p className="ops-hint">
                    在 <a href="/chat">对话页</a> 测试，或到 <a href="/eval">评测页</a> 运行 120 条用例。
                  </p>
                  <button
                    type="button"
                    className="ops-btn ops-btn-secondary"
                    style={{ marginTop: 12 }}
                    disabled={seeding}
                    onClick={seedDemo}
                  >
                    {seeding ? "载入中…" : "载入七层演示（每层 1 条）"}
                  </button>
                </div>
              ) : (
                listSection
              )}
            </section>
          )}

          <section className="ops-tools">
            <details open={formOpen} onToggle={(e) => setFormOpen((e.target as HTMLDetailsElement).open)}>
              <summary className="ops-tools-summary">登记新 Bad Case</summary>
              <div className="ops-tools-body">
                <div className="ops-form-row">
                  <input
                    className="ops-input"
                    placeholder="trace_id（可选）"
                    value={form.trace_id}
                    onChange={(e) => setForm({ ...form, trace_id: e.target.value })}
                  />
                  <input
                    className="ops-input"
                    placeholder="case_id（可选）"
                    value={form.case_id}
                    onChange={(e) => setForm({ ...form, case_id: e.target.value })}
                  />
                  <select
                    className="ops-input"
                    value={form.attribution}
                    onChange={(e) => setForm({ ...form, attribution: e.target.value })}
                  >
                    {ATTRIBUTION_LAYERS.map((l) => (
                      <option key={l.key} value={l.key}>
                        {l.label}
                      </option>
                    ))}
                  </select>
                  <input
                    className="ops-input ops-input-grow"
                    placeholder="备注：现象与期望"
                    value={form.note}
                    onChange={(e) => setForm({ ...form, note: e.target.value })}
                  />
                  <button type="button" className="ops-btn ops-btn-primary" onClick={submitBadcase}>
                    提交
                  </button>
                </div>
                {selectedLayer && (
                  <p className="ops-form-hint" style={{ borderColor: selectedLayer.color }}>
                    {selectedLayer.symptom} → {selectedLayer.action}
                  </p>
                )}
              </div>
            </details>
          </section>
        </>
      )}
    </div>
  );
}
