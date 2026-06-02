"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import TicketCatalogItem from "@/components/TicketCatalogItem";
import {
  countByStatus,
  isOpenTicket,
  STATUS_COLORS,
  STATUS_LABEL,
  type TicketItem,
} from "@/lib/tickets";

type TabId = "overview" | "all" | "open";
type StatusFilter = "all" | "new" | "in_progress" | "escalated" | "closed";

interface Props {
  /** 运营后台 Tab 内嵌：隐藏页头，保留 KPI + 列表 */
  embedded?: boolean;
  /** 深链 /tickets?id=T-001 自动展开 */
  initialExpandedId?: string;
}

export type { TicketItem };

export default function TicketsPanel({ embedded = false, initialExpandedId }: Props) {
  const [items, setItems] = useState<TicketItem[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<TabId>("all");
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");
  const [expandedId, setExpandedId] = useState<string | null>(initialExpandedId ?? null);

  const load = useCallback(async () => {
    setError("");
    setLoading(true);
    try {
      const res = await fetch("/api/tickets");
      if (res.status === 404) throw new Error("404");
      if (!res.ok) throw new Error(String(res.status));
      const data = await res.json();
      setItems(data.items ?? []);
    } catch (e) {
      const msg =
        e instanceof Error && e.message === "404"
          ? "工单接口未就绪，请重启后端（含 /api/tickets）"
          : "无法加载工单，请确认后端已启动（默认 :8002）";
      setError(msg);
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (initialExpandedId) {
      setExpandedId(initialExpandedId);
      setTab("all");
    }
  }, [initialExpandedId]);

  const statusCounts = useMemo(() => countByStatus(items), [items]);
  const openItems = useMemo(() => items.filter(isOpenTicket), [items]);
  const urgentCount = useMemo(() => items.filter((t) => t.priority === "urgent").length, [items]);

  const listSource = tab === "open" ? openItems : items;

  const filteredItems = useMemo(() => {
    return listSource.filter((t) => {
      if (statusFilter !== "all" && t.status !== statusFilter) return false;
      return true;
    });
  }, [listSource, statusFilter]);

  function toggleTicket(id: string) {
    setExpandedId((prev) => (prev === id ? null : id));
  }

  const kpiSection = (
    <section className="ops-kpi-grid">
      <div className="ops-kpi-card">
        <div className="ops-kpi-label">工单总数</div>
        <div className="ops-kpi-value">{items.length}</div>
        <div className="ops-kpi-hint">Agent ticket-create 写入</div>
      </div>
      <div className={`ops-kpi-card ${openItems.length > 0 ? "ops-kpi-warn" : ""}`}>
        <div className="ops-kpi-label">待处理</div>
        <div className="ops-kpi-value">{openItems.length}</div>
        <div className="ops-kpi-hint">新建 · 处理中 · 已升级</div>
      </div>
      <div className="ops-kpi-card">
        <div className="ops-kpi-label">处理中</div>
        <div className="ops-kpi-value">{statusCounts.in_progress ?? 0}</div>
        <div className="ops-kpi-hint">坐席可接手</div>
      </div>
      <div className={`ops-kpi-card ${urgentCount > 0 ? "ops-kpi-warn" : ""}`}>
        <div className="ops-kpi-label">紧急</div>
        <div className="ops-kpi-value">{urgentCount}</div>
        <div className="ops-kpi-hint">
          <a href="/chat">对话建单 →</a>
        </div>
      </div>
    </section>
  );

  const statusBar =
    items.length > 0 ? (
      <section className="ops-att-overview">
        <div className="ops-att-overview-head">
          <span className="ops-section-label">状态分布</span>
          {openItems.length > 0 && (
            <button type="button" className="ops-link-btn" onClick={() => setTab("open")}>
              查看 {openItems.length} 条待处理 →
            </button>
          )}
        </div>
        <div className="ops-att-bar">
          {(["new", "in_progress", "escalated", "closed"] as const).map((st) => {
            const n = statusCounts[st] ?? 0;
            if (!n) return null;
            return (
              <button
                key={st}
                type="button"
                className="ops-att-segment eval-layer-pass"
                style={{ flex: n, background: STATUS_COLORS[st] || "#94a3b8" }}
                title={`${STATUS_LABEL[st]} ${n}`}
                onClick={() => {
                  setStatusFilter(st);
                  setTab("all");
                }}
              />
            );
          })}
        </div>
        <div className="ops-att-legend">
          {(["new", "in_progress", "escalated", "closed"] as const).map((st) => {
            const n = statusCounts[st] ?? 0;
            if (!n) return null;
            return (
              <button
                key={st}
                type="button"
                className={`ops-att-legend-item ${statusFilter === st ? "active" : ""}`}
                onClick={() => setStatusFilter(statusFilter === st ? "all" : st)}
              >
                <span className="ops-att-dot" style={{ background: STATUS_COLORS[st] }} />
                {STATUS_LABEL[st]}
                <strong>{n}</strong>
              </button>
            );
          })}
        </div>
      </section>
    ) : null;

  const listSection = (
    <>
      <div className="ops-filter-row">
        <button
          type="button"
          className={`badcase-filter-chip ${statusFilter === "all" ? "active" : ""}`}
          onClick={() => setStatusFilter("all")}
        >
          全部 {listSource.length}
        </button>
        {(["new", "in_progress", "escalated", "closed"] as const).map((st) => {
          const n = listSource.filter((t) => t.status === st).length;
          if (!n) return null;
          return (
            <button
              key={st}
              type="button"
              className={`badcase-filter-chip ${statusFilter === st ? "active" : ""}`}
              onClick={() => setStatusFilter(st)}
            >
              {STATUS_LABEL[st]} {n}
            </button>
          );
        })}
      </div>
      <div className="eval-catalog-list" data-testid="ticket-list">
        {filteredItems.map((t) => (
          <TicketCatalogItem
            key={t.id}
            ticket={t}
            expanded={expandedId === t.id}
            onToggle={() => toggleTicket(t.id)}
          />
        ))}
      </div>
      {filteredItems.length === 0 && !loading && (
        <div className="ops-empty">
          <p>当前筛选下暂无工单。</p>
        </div>
      )}
    </>
  );

  return (
    <div className={`ops-page ticket-page ${embedded ? "ticket-page-embedded" : ""}`}>
      {!embedded && (
        <header className="ops-header">
          <div>
            <h1 className="ops-title">工单中心</h1>
            <p className="ops-subtitle">查看 Agent 建单 → 核对字段 → 对话查进度 → 运营 Trace 回归</p>
          </div>
          <div className="ops-header-actions">
            <button type="button" className="ops-btn ops-btn-secondary" onClick={load} disabled={loading}>
              刷新
            </button>
          </div>
        </header>
      )}

      {embedded && (
        <div className="ops-header-actions" style={{ marginBottom: 12 }}>
          <button type="button" className="ops-btn ops-btn-secondary" onClick={load} disabled={loading}>
            刷新
          </button>
        </div>
      )}

      {error && <div className="ops-alert ops-alert-error">{error}</div>}
      {loading && !error && <div className="ops-empty">加载中…</div>}

      {!loading && !error && (
        <>
          {kpiSection}
          {statusBar}

          <nav className="ops-tabs">
            {(
              [
                ["overview", "概览"],
                ["all", `全部工单 (${items.length})`],
                ["open", `待处理 (${openItems.length})`],
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
                {(["new", "in_progress", "escalated", "closed"] as const).map((st) => {
                  const n = statusCounts[st] ?? 0;
                  return (
                    <div key={st} className="eval-layer-card">
                      <div className="eval-layer-card-head">
                        <span className="ops-att-dot" style={{ background: STATUS_COLORS[st] }} />
                        <strong>{STATUS_LABEL[st]}</strong>
                        <span className={`eval-layer-rate ${st !== "closed" && n > 0 ? "warn" : ""}`}>
                          {n}
                        </span>
                      </div>
                      <p className="eval-layer-desc">
                        {st === "new" && "Agent 刚创建，待坐席分配"}
                        {st === "in_progress" && "处理中，可在对话查进度"}
                        {st === "escalated" && "已升级，需主管关注"}
                        {st === "closed" && "已关闭归档"}
                      </p>
                      {n > 0 && st !== "closed" && (
                        <button
                          type="button"
                          className="ops-link-btn"
                          onClick={() => {
                            setStatusFilter(st);
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
                <h3 className="eval-section-title">处理闭环</h3>
                <ol className="eval-workflow-steps">
                  <li>
                    在 <a href="/chat">对话页</a> 触发 ticket-create 或 ticket-query Skill
                  </li>
                  <li>本页展开工单核对 title / priority 是否完整</li>
                  <li>到 <a href="/ops">运营后台</a> 查 Trace 确认 Skill 链与 Tool 调用</li>
                  <li>状态变更由规则引擎执行，非 LLM 直接修改</li>
                </ol>
              </div>
            </section>
          )}

          {(tab === "all" || tab === "open") && (
            <section className="ops-panel">
              <p className="ops-section-desc">点击工单行展开明细；与评测报告「全量明细」同构手风琴交互。</p>
              {items.length === 0 ? (
                <div className="ops-empty">
                  <p>暂无工单。</p>
                  <p className="ops-hint">
                    在 <a href="/chat">对话页</a> 发送「服务器宕机请尽快处理」可触发建单。
                  </p>
                </div>
              ) : (
                listSection
              )}
            </section>
          )}
        </>
      )}
    </div>
  );
}
