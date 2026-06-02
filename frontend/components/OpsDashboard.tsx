"use client";

import { useCallback, useEffect, useState } from "react";
import BadCasePanel from "@/components/BadCasePanel";
import TracePanel from "@/components/TracePanel";

interface SkillHealth {
  skill_id: string;
  version: string;
  invocations: number;
  success_rate: string;
}

interface OpsSummary {
  db_backend: string;
  trace_count: number;
  badcase_count: number;
}

type TabId = "badcases" | "trace" | "skills";

export default function OpsDashboard() {
  const [skills, setSkills] = useState<SkillHealth[]>([]);
  const [summary, setSummary] = useState<OpsSummary | null>(null);
  const [badcaseCount, setBadcaseCount] = useState(0);
  const [error, setError] = useState("");
  const [tab, setTab] = useState<TabId>("badcases");
  const [activeTraceId, setActiveTraceId] = useState("");
  const [refreshKey, setRefreshKey] = useState(0);

  const loadMeta = useCallback(async () => {
    setError("");
    try {
      const [sRes, sumRes] = await Promise.all([
        fetch("/api/ops/skills"),
        fetch("/api/ops/summary"),
      ]);
      if (sRes.ok) setSkills((await sRes.json()).skills || []);
      if (sumRes.ok) {
        const sum = await sumRes.json();
        setSummary(sum);
        setBadcaseCount(sum.badcase_count ?? 0);
      }
    } catch {
      setError("加载运营数据失败，请确认后端已启动");
    }
  }, []);

  useEffect(() => {
    loadMeta();
  }, [loadMeta]);

  function handleRefresh() {
    loadMeta();
    setRefreshKey((k) => k + 1);
  }

  function openTrace(id: string) {
    setActiveTraceId(id);
    setTab("trace");
    setTimeout(() => document.getElementById("ops-trace-section")?.scrollIntoView({ behavior: "smooth" }), 50);
  }

  const activeSkills = skills.filter((s) => s.invocations > 0);
  const idleCount = skills.filter((s) => s.invocations === 0).length;

  return (
    <div className="ops-page">
      <header className="ops-header">
        <div>
          <h1 className="ops-title">运营后台</h1>
          <p className="ops-subtitle">Bad Case 七层归因 → Trace 诊断 → Skill 健康度</p>
        </div>
        <div className="ops-header-actions">
          <button type="button" className="ops-btn ops-btn-secondary" onClick={handleRefresh}>
            刷新
          </button>
        </div>
      </header>

      {error && <div className="ops-alert ops-alert-error">{error}</div>}

      <section className="ops-kpi-grid">
        <div className={`ops-kpi-card ${badcaseCount > 0 ? "ops-kpi-warn" : ""}`}>
          <div className="ops-kpi-label">Bad Case</div>
          <div className="ops-kpi-value">{badcaseCount}</div>
          <div className="ops-kpi-hint">七层归因 · Eval 自动入库</div>
        </div>
        <div className="ops-kpi-card">
          <div className="ops-kpi-label">Harness Trace</div>
          <div className="ops-kpi-value">{summary?.trace_count ?? "—"}</div>
          <div className="ops-kpi-hint">对话/评测自动写入</div>
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

      <nav className="ops-tabs">
        {(
          [
            ["badcases", `Bad Case (${badcaseCount})`],
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

      {tab === "badcases" && (
        <BadCasePanel
          embedded
          refreshKey={refreshKey}
          onTraceClick={openTrace}
          onCountChange={setBadcaseCount}
        />
      )}

      {tab === "trace" && (
        <section id="ops-trace-section" className="ops-panel">
          <p className="ops-section-desc">
            查看单次请求的 Guardrail → Memory → Skill 全链路，定位卡在哪一步。
          </p>
          <TracePanel traceId={activeTraceId} onTraceIdChange={setActiveTraceId} />
        </section>
      )}

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
                    <td>
                      <code>{s.skill_id}</code>
                    </td>
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
    </div>
  );
}
