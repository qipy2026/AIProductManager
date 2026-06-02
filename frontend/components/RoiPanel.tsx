"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  buildRoiOverview,
  formatDelta,
  formatDeltaShort,
  formatMetricValue,
  formatProgress,
  gapToTarget,
  METRIC_DETAILS,
  progressPct,
  targetStatus,
  targetStatusLabel,
  type RoiMetric,
  type RoiOverview,
  type RoiSnapshot,
} from "@/lib/roi";

interface Props {
  embedded?: boolean;
  refreshKey?: number;
}

interface MetricCardProps {
  m: RoiMetric;
  expanded: boolean;
  onToggle: () => void;
  cardRef?: (el: HTMLElement | null) => void;
}

function RoiOverviewSection({
  overview,
  onSelectMetric,
}: {
  overview: RoiOverview;
  onSelectMetric: (key: string) => void;
}) {
  return (
    <section className="roi-overview">
      <h3 className="eval-section-title">总览</h3>
      <p className="roi-overview-summary">{overview.summary}</p>

      <div className="ops-kpi-grid roi-overview-kpi">
        <div className="ops-kpi-card">
          <div className="ops-kpi-label">已达标</div>
          <div className="ops-kpi-value">{overview.doneCount}</div>
          <div className="ops-kpi-hint">/ {overview.total} 项</div>
        </div>
        <div className="ops-kpi-card">
          <div className="ops-kpi-label">接近目标</div>
          <div className="ops-kpi-value">{overview.nearCount}</div>
          <div className="ops-kpi-hint">完成度 ≥75%</div>
        </div>
        <div className={`ops-kpi-card ${overview.pendingCount > 0 ? "ops-kpi-warn" : ""}`}>
          <div className="ops-kpi-label">待提升</div>
          <div className="ops-kpi-value">{overview.pendingCount}</div>
          <div className="ops-kpi-hint">完成度 &lt;75%</div>
        </div>
        <div className="ops-kpi-card">
          <div className="ops-kpi-label">较基线改善</div>
          <div className="ops-kpi-value">{overview.improvedCount}</div>
          <div className="ops-kpi-hint">/ {overview.total} 项</div>
        </div>
      </div>

      <div className="roi-overview-columns">
        <div className="roi-overview-col roi-overview-highlights">
          <h4 className="roi-overview-col-title">亮点</h4>
          {overview.highlights.length === 0 ? (
            <p className="ops-hint">暂无突出亮点，继续观察试点数据。</p>
          ) : (
            <ul className="roi-overview-list">
              {overview.highlights.map(({ metric, reason }) => (
                <li key={metric.key}>
                  <button
                    type="button"
                    className="roi-overview-item roi-overview-item-good"
                    onClick={() => onSelectMetric(metric.key)}
                  >
                    <span className="roi-overview-item-name">{metric.label}</span>
                    <span className="roi-overview-item-value">{formatMetricValue(metric.current, metric.unit)}</span>
                    <span className="roi-overview-item-reason">{reason}</span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="roi-overview-col roi-overview-issues">
          <h4 className="roi-overview-col-title">需关注</h4>
          {overview.issues.length === 0 ? (
            <p className="ops-hint">暂无待跟进项，各指标进展良好。</p>
          ) : (
            <ul className="roi-overview-list">
              {overview.issues.map(({ metric, reason }) => (
                <li key={metric.key}>
                  <button
                    type="button"
                    className="roi-overview-item roi-overview-item-warn"
                    onClick={() => onSelectMetric(metric.key)}
                  >
                    <span className="roi-overview-item-name">{metric.label}</span>
                    <span className="roi-overview-item-value">{formatMetricValue(metric.current, metric.unit)}</span>
                    <span className="roi-overview-item-reason">{reason}</span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </section>
  );
}

function MetricDetail({ m }: { m: RoiMetric }) {
  const detail = METRIC_DETAILS[m.key];
  const status = targetStatus(m);

  return (
    <div className="roi-metric-detail">
      {detail && <p className="roi-metric-desc">{detail.desc}</p>}
      <div className="roi-metric-detail-compare">
        <div className="roi-metric-detail-cell">
          <span className="roi-metric-detail-label">基线</span>
          <span className="roi-metric-detail-value">{formatMetricValue(m.baseline, m.unit)}</span>
        </div>
        <div className="roi-metric-detail-cell roi-metric-detail-current">
          <span className="roi-metric-detail-label">当前</span>
          <span className="roi-metric-detail-value">{formatMetricValue(m.current, m.unit)}</span>
        </div>
        <div className="roi-metric-detail-cell">
          <span className="roi-metric-detail-label">目标</span>
          <span className="roi-metric-detail-value">{formatMetricValue(m.target, m.unit)}</span>
        </div>
      </div>
      <dl className="roi-metric-detail-meta">
        <div>
          <dt>较基线</dt>
          <dd className={m.improved ? "eval-status-pass" : "eval-status-fail"}>{formatDelta(m)}</dd>
        </div>
        <div>
          <dt>达成进度</dt>
          <dd>{formatProgress(m)}</dd>
        </div>
        <div>
          <dt>距目标</dt>
          <dd>{gapToTarget(m)}</dd>
        </div>
        <div>
          <dt>状态</dt>
          <dd>
            <span className={`roi-status-tag roi-status-${status}`}>{targetStatusLabel(m)}</span>
          </dd>
        </div>
        {detail && (
          <div className="roi-metric-detail-source">
            <dt>数据来源</dt>
            <dd>{detail.source}</dd>
          </div>
        )}
      </dl>
    </div>
  );
}

function MetricCard({ m, expanded, onToggle, cardRef }: MetricCardProps) {
  const pct = progressPct(m);

  return (
    <article
      ref={cardRef}
      className={`roi-metric-card ${m.improved ? "roi-metric-card-good" : "roi-metric-card-warn"} ${
        expanded ? "roi-metric-card-expanded" : ""
      }`}
    >
      <button
        type="button"
        className="roi-metric-card-btn"
        onClick={onToggle}
        aria-expanded={expanded}
      >
        <span className="roi-metric-chevron" aria-hidden>
          {expanded ? "▾" : "▸"}
        </span>
        <div className="roi-metric-card-body">
          <div className="roi-metric-card-top">
            <h4 className="roi-metric-card-title">{m.label}</h4>
            <span className={`roi-metric-card-badge ${m.improved ? "roi-badge-good" : "roi-badge-warn"}`}>
              较基线 {formatDeltaShort(m)}
            </span>
          </div>
          <div className="roi-metric-card-value">{formatMetricValue(m.current, m.unit)}</div>
          <div className="roi-metric-card-compare">
            <span>基线 {formatMetricValue(m.baseline, m.unit)}</span>
            <span className="roi-metric-card-arrow">→</span>
            <span>目标 {formatMetricValue(m.target, m.unit)}</span>
          </div>
          <div className="roi-metric-card-progress">
            <div className="roi-progress-cell">
              <span className="roi-progress-bar" style={{ width: `${pct}%` }} />
            </div>
            <span className="roi-metric-card-pct">完成 {formatProgress(m)}</span>
          </div>
        </div>
      </button>
      {expanded && <MetricDetail m={m} />}
    </article>
  );
}

export default function RoiPanel({ embedded = false, refreshKey }: Props) {
  const [data, setData] = useState<RoiSnapshot | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [expandedKey, setExpandedKey] = useState<string | null>(null);
  const cardRefMap = useRef(new Map<string, HTMLElement>());

  const load = useCallback(async () => {
    setError("");
    setLoading(true);
    try {
      const res = await fetch("/api/ops/roi");
      if (!res.ok) throw new Error(String(res.status));
      setData(await res.json());
    } catch {
      setError("无法加载 ROI 快照，请确认后端已启动");
      setData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (refreshKey !== undefined && refreshKey > 0) load();
  }, [refreshKey, load]);

  function toggleMetric(key: string) {
    setExpandedKey((prev) => (prev === key ? null : key));
  }

  function selectMetric(key: string) {
    setExpandedKey(key);
    setTimeout(() => {
      cardRefMap.current.get(key)?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }, 50);
  }

  if (loading && !data) {
    return <p className="ops-hint">正在加载…</p>;
  }

  if (error && !data) {
    return <div className="ops-alert ops-alert-error">{error}</div>;
  }

  if (!data) return null;

  const overview = buildRoiOverview(data.metrics);

  return (
    <div className={`roi-panel ${embedded ? "roi-panel-embedded" : ""}`}>
      {!embedded && (
        <header className="ops-header">
          <div>
            <h1 className="ops-title">业务 ROI 看板</h1>
            <p className="ops-subtitle">{data.period} · 基线期 {data.baseline_period}</p>
          </div>
          <div className="ops-header-actions">
            <button type="button" className="ops-btn ops-btn-secondary" onClick={load}>
              刷新
            </button>
          </div>
        </header>
      )}

      <RoiOverviewSection overview={overview} onSelectMetric={selectMetric} />

      <section className="roi-metrics-panel">
        <h3 className="eval-section-title">核心业务指标</h3>
        <p className="ops-hint roi-metrics-hint">点击指标卡片查看说明与明细</p>
        <div className="roi-metric-cards">
          {data.metrics.map((m) => (
            <MetricCard
              key={m.key}
              m={m}
              expanded={expandedKey === m.key}
              onToggle={() => toggleMetric(m.key)}
              cardRef={(el) => {
                if (el) cardRefMap.current.set(m.key, el);
                else cardRefMap.current.delete(m.key);
              }}
            />
          ))}
        </div>
      </section>
    </div>
  );
}
