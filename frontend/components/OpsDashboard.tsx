"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import TracePanel from "@/components/TracePanel";
import { Button } from "@/components/ui/button";
import {
  ATTRIBUTION_LAYERS,
  getAttribution,
  groupByAttribution,
  normalizeAttributionKey,
  OTHER_ATTRIBUTION,
} from "@/lib/attributions";

interface SkillHealth {
  skill_id: string;
  version: string;
  invocations: number;
  success_rate: string;
}

interface BadCase {
  id?: number;
  trace_id?: string;
  case_id?: string;
  layer?: string;
  attribution: string;
  note?: string;
  failures?: string[];
}

interface OpsSummary {
  db_backend: string;
  trace_count: number;
  badcase_count: number;
}

type TabId = "problems" | "trace" | "skills";

function BadCaseItem({
  b,
  onTraceClick,
}: {
  b: BadCase;
  onTraceClick: (id: string) => void;
}) {
  const layer = getAttribution(b.attribution);
  const summary =
    b.note ||
    (b.failures && b.failures.length > 0 ? b.failures[0] : layer?.symptom) ||
    "无备注";

  return (
    <div className="ops-problem-item">
      <div className="ops-problem-head">
        {b.case_id && <span className="ops-problem-case">{b.case_id}</span>}
        {b.layer && <span className="ops-problem-eval">评测 {b.layer}</span>}
      </div>
      <p className="ops-problem-summary">{summary}</p>
      {b.failures && b.failures.length > 1 && (
        <p className="ops-problem-fail">+{b.failures.length - 1} 项失败断言</p>
      )}
      {b.trace_id ? (
        <button type="button" className="ops-trace-link" onClick={() => onTraceClick(b.trace_id!)}>
          查看 Trace · {b.trace_id.slice(0, 8)}…
        </button>
      ) : (
        <span className="ops-hint-inline">Eval 自动录入 · 无 Trace</span>
      )}
    </div>
  );
}

export default function OpsDashboard() {
  const [skills, setSkills] = useState<SkillHealth[]>([]);
  const [badcases, setBadcases] = useState<BadCase[]>([]);
  const [summary, setSummary] = useState<OpsSummary | null>(null);
  const [error, setError] = useState("");
  const [tab, setTab] = useState<TabId>("problems");
  const [filterLayer, setFilterLayer] = useState("all");
  const [activeTraceId, setActiveTraceId] = useState("");
  const [guideOpen, setGuideOpen] = useState(false);
  const [formOpen, setFormOpen] = useState(false);
  const [reclassifyMsg, setReclassifyMsg] = useState("");
  const [reclassifying, setReclassifying] = useState(false);
  const [form, setForm] = useState({ trace_id: "", attribution: "skill", note: "" });

  const selectedLayer = getAttribution(form.attribution);

  const load = useCallback(async () => {
    setError("");
    try {
      const [sRes, bRes, sumRes] = await Promise.all([
        fetch("/api/ops/skills"),
        fetch("/api/ops/badcases?limit=500"),
        fetch("/api/ops/summary"),
      ]);
      if (sRes.ok) setSkills((await sRes.json()).skills || []);
      if (bRes.ok) setBadcases((await bRes.json()).items || []);
      if (sumRes.ok) setSummary(await sumRes.json());
    } catch {
      setError("加载运营数据失败，请确认后端已启动");
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

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
    setForm({ trace_id: "", attribution: "skill", note: "" });
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
      setFilterLayer("all");
      load();
    } catch {
      setError("归类请求失败");
    } finally {
      setReclassifying(false);
    }
  }

  function openTrace(id: string) {
    setActiveTraceId(id);
    setTab("trace");
    setTimeout(() => document.getElementById("ops-trace-section")?.scrollIntoView({ behavior: "smooth" }), 50);
  }

  const activeSkills = skills.filter((s) => s.invocations > 0);
  const idleCount = skills.filter((s) => s.invocations === 0).length;
  const groupedBadcases = groupByAttribution(badcases);
  const pendingOther = badcases.filter(
    (b) => normalizeAttributionKey(b.attribution) === "other"
  ).length;

  const topLayer = useMemo(() => {
    if (!groupedBadcases.length) return null;
    return [...groupedBadcases].sort((a, b) => b.items.length - a.items.length)[0];
  }, [groupedBadcases]);

  const filteredGroups =
    filterLayer === "all"
      ? groupedBadcases
      : groupedBadcases.filter((g) => g.layer.key === filterLayer);

  const totalBad = badcases.length || 1;

  return (
    <div className="ops-page">
      {/* 页头 */}
      <header className="ops-header">
        <div>
          <h1 className="ops-title">运营后台</h1>
          <p className="ops-subtitle">发现问题 → 查 Trace → 确认归因 → 修复回归</p>
        </div>
        <div className="ops-header-actions">
          <Button
            className="text-xs h-9 bg-white text-gray-700 border border-gray-300 hover:bg-gray-50"
            onClick={load}
          >
            刷新
          </Button>
        </div>
      </header>

      {error && <div className="ops-alert ops-alert-error">{error}</div>}
      {reclassifyMsg && <div className="ops-alert ops-alert-success">{reclassifyMsg}</div>}

      {/* 概览 KPI */}
      <section className="ops-kpi-grid">
        <div className="ops-kpi-card">
          <div className="ops-kpi-label">Harness Trace</div>
          <div className="ops-kpi-value">{summary?.trace_count ?? "—"}</div>
          <div className="ops-kpi-hint">对话/评测自动写入</div>
        </div>
        <div className={`ops-kpi-card ${badcases.length > 0 ? "ops-kpi-warn" : ""}`}>
          <div className="ops-kpi-label">待处理 Bad Case</div>
          <div className="ops-kpi-value">{summary?.badcase_count ?? badcases.length}</div>
          <div className="ops-kpi-hint">
            {topLayer ? `主要集中：${topLayer.layer.label}` : "暂无异常记录"}
          </div>
        </div>
        <div className="ops-kpi-card">
          <div className="ops-kpi-label">Skill 活跃</div>
          <div className="ops-kpi-value">{activeSkills.length}</div>
          <div className="ops-kpi-hint">{idleCount} 个尚未调用</div>
        </div>
        <div className="ops-kpi-card">
          <div className="ops-kpi-label">存储</div>
          <div className="ops-kpi-value ops-kpi-value-sm">{summary?.db_backend ?? "—"}</div>
          <div className="ops-kpi-hint">OPS_DB 后端</div>
        </div>
      </section>

      {/* 七层分布 */}
      {badcases.length > 0 && (
        <section className="ops-att-overview">
          <div className="ops-att-overview-head">
            <span className="ops-section-label">问题分布（七层归因）</span>
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
            {groupedBadcases.map((g) => (
              <button
                key={g.layer.key}
                type="button"
                className="ops-att-segment"
                style={{
                  flex: g.items.length,
                  background: g.layer.color,
                }}
                title={`${g.layer.label} ${g.items.length} 条`}
                onClick={() => {
                  setFilterLayer(g.layer.key);
                  setTab("problems");
                }}
              />
            ))}
          </div>
          <div className="ops-att-legend">
            {groupedBadcases.map((g) => (
              <button
                key={g.layer.key}
                type="button"
                className={`ops-att-legend-item ${filterLayer === g.layer.key ? "active" : ""}`}
                onClick={() => setFilterLayer(filterLayer === g.layer.key ? "all" : g.layer.key)}
              >
                <span className="ops-att-dot" style={{ background: g.layer.color }} />
                {g.layer.label}
                <strong>{g.items.length}</strong>
                <span className="ops-att-pct">{Math.round((g.items.length / totalBad) * 100)}%</span>
              </button>
            ))}
          </div>
        </section>
      )}

      {/* Tab 导航 */}
      <nav className="ops-tabs">
        {(
          [
            ["problems", `问题清单 (${badcases.length})`],
            ["trace", "Trace 诊断"],
            ["skills", `Skill 健康度 (${activeSkills.length})`],
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

      {/* 问题清单 */}
      {tab === "problems" && (
        <section className="ops-panel">
          {badcases.length === 0 ? (
            <div className="ops-empty">
              <p>暂无 Bad Case，系统运行正常。</p>
              <p className="ops-hint">
                在 <a href="/chat">对话页</a> 测试，或到 <a href="/eval">评测页</a> 运行 120 条用例。
              </p>
            </div>
          ) : (
            <>
              {pendingOther > 0 && (
                <div className="ops-alert ops-alert-warn">
                  有 {pendingOther} 条待归类，点击上方「一键归类」自动分配到七层。
                </div>
              )}
              <div className="ops-filter-row">
                <button
                  type="button"
                  className={`badcase-filter-chip ${filterLayer === "all" ? "active" : ""}`}
                  onClick={() => setFilterLayer("all")}
                >
                  全部 {badcases.length}
                </button>
                {groupedBadcases.map((g) => (
                  <button
                    key={g.layer.key}
                    type="button"
                    className={`badcase-filter-chip ${filterLayer === g.layer.key ? "active" : ""}`}
                    onClick={() => setFilterLayer(g.layer.key)}
                  >
                    {g.layer.label} {g.items.length}
                  </button>
                ))}
              </div>
              {filteredGroups.map((group) => (
                <div key={group.layer.key} className="ops-problem-group">
                  <div className="ops-problem-group-head">
                    <span className="ops-att-dot" style={{ background: group.layer.color }} />
                    <div>
                      <strong>{group.layer.label}</strong>
                      <span className="ops-problem-group-sub">{group.layer.short} · {group.layer.action}</span>
                    </div>
                    <span className="ops-problem-group-count">{group.items.length}</span>
                  </div>
                  <div className="ops-problem-list">
                    {group.items.slice(0, filterLayer === "all" ? 5 : undefined).map((b, i) => (
                      <BadCaseItem key={b.id ?? i} b={b} onTraceClick={openTrace} />
                    ))}
                    {filterLayer === "all" && group.items.length > 5 && (
                      <button
                        type="button"
                        className="ops-link-btn"
                        onClick={() => setFilterLayer(group.layer.key)}
                      >
                        查看全部 {group.items.length} 条 →
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </>
          )}
        </section>
      )}

      {/* Trace 诊断 */}
      {tab === "trace" && (
        <section id="ops-trace-section" className="ops-panel">
          <p className="ops-section-desc">
            查看单次请求的 Guardrail → Memory → Skill 全链路，定位卡在哪一步。
          </p>
          <TracePanel traceId={activeTraceId} onTraceIdChange={setActiveTraceId} />
        </section>
      )}

      {/* Skill 监控 */}
      {tab === "skills" && (
        <section className="ops-panel">
          {activeSkills.length === 0 ? (
            <div className="ops-empty">
              <p>暂无 Skill 调用数据。</p>
              <p className="ops-hint">发送对话或运行评测后自动生成统计。</p>
            </div>
          ) : (
            <table className="ops-skill-table">
              <thead>
                <tr>
                  <th>Skill</th>
                  <th>版本</th>
                  <th>调用次数</th>
                  <th>成功率</th>
                </tr>
              </thead>
              <tbody>
                {activeSkills.map((s) => (
                  <tr key={s.skill_id}>
                    <td><code>{s.skill_id}</code></td>
                    <td>v{s.version}</td>
                    <td>{s.invocations}</td>
                    <td>
                      <span className="ops-skill-rate">{s.success_rate}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          {idleCount > 0 && (
            <details className="ops-idle-skills">
              <summary>{idleCount} 个 Skill 尚未被调用</summary>
              <p>{skills.filter((s) => s.invocations === 0).map((s) => s.skill_id).join(" · ")}</p>
            </details>
          )}
        </section>
      )}

      {/* 底部工具区 */}
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

        <details open={guideOpen} onToggle={(e) => setGuideOpen((e.target as HTMLDetailsElement).open)}>
          <summary className="ops-tools-summary">七层归因参考表</summary>
          <div className="ops-tools-body ops-guide-table-wrap">
            <table className="ops-guide-table">
              <thead>
                <tr>
                  <th>层级</th>
                  <th>含义</th>
                  <th>典型症状</th>
                  <th>处理建议</th>
                </tr>
              </thead>
              <tbody>
                {[...ATTRIBUTION_LAYERS, OTHER_ATTRIBUTION].map((l) => (
                  <tr key={l.key}>
                    <td>
                      <span className="ops-att-dot" style={{ background: l.color }} /> {l.label}
                    </td>
                    <td>{l.short}</td>
                    <td>{l.symptom}</td>
                    <td className="text-muted">{l.action}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </details>
      </section>
    </div>
  );
}
