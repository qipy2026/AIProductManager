/** ROI 快照 — 与 backend/ops/roi.py 对齐 */

export interface RoiMetric {
  key: string;
  label: string;
  unit: string;
  baseline: number;
  current: number;
  target: number;
  delta: number;
  improved: boolean;
  lower_is_better?: boolean;
}

export interface RoiSnapshot {
  period: string;
  baseline_period: string;
  headline: string;
  metrics: RoiMetric[];
  eval: {
    total: number;
    passed: number;
    pass_rate: number | null;
    gate: number;
    gate_passed: boolean;
  };
  ops: {
    trace_count: number;
    badcase_count: number;
  };
  skills: { skill_id: string; invocations: number; success_rate: string }[];
}

function formatNum(n: number): string {
  if (Number.isInteger(n) || Math.abs(n - Math.round(n)) < 0.05) {
    return String(Math.round(n));
  }
  return n.toFixed(1);
}

/** 指标数值 + 中文单位，如 72%、34 单/天、2.2 秒 */
export function formatMetricValue(value: number, unit: string): string {
  switch (unit) {
    case "%":
      return `${formatNum(value)}%`;
    case "单":
      return `${formatNum(value)} 单/天`;
    case "轮":
      return `${formatNum(value)} 轮`;
    case "s":
      return `${formatNum(value)} 秒`;
    default:
      return `${formatNum(value)} ${unit}`;
  }
}

/** 较基线变化 — 避免「+21%」在「越低越好」指标上产生歧义 */
export function formatDelta(m: RoiMetric): string {
  const abs = formatNum(Math.abs(m.delta));
  if (m.delta === 0) return "与基线持平";

  if (m.unit === "%") {
    return m.lower_is_better ? `降低 ${abs} 个百分点` : `提升 ${abs} 个百分点`;
  }
  if (m.unit === "单") return m.delta > 0 ? `增加 ${abs} 单/天` : `减少 ${abs} 单/天`;
  if (m.unit === "轮") return m.delta > 0 ? `减少 ${abs} 轮` : `增加 ${abs} 轮`;
  if (m.unit === "s") return m.delta > 0 ? `缩短 ${abs} 秒` : `增加 ${abs} 秒`;
  return m.delta > 0 ? `+${abs}` : `-${abs}`;
}

export function progressPct(m: RoiMetric): number {
  const { baseline, current, target, lower_is_better } = m;
  if (lower_is_better) {
    const span = baseline - target;
    if (span <= 0) return 100;
    return Math.min(100, Math.max(0, ((baseline - current) / span) * 100));
  }
  const span = target - baseline;
  if (span <= 0) return 100;
  return Math.min(100, Math.max(0, ((current - baseline) / span) * 100));
}

export function formatProgress(m: RoiMetric): string {
  return `${Math.round(progressPct(m))}%`;
}

/** 卡片用简短变化描述 */
export function formatDeltaShort(m: RoiMetric): string {
  const abs = formatNum(Math.abs(m.delta));
  if (m.delta === 0) return "持平";
  if (m.unit === "%") {
    return m.lower_is_better ? `↓${abs}pp` : `↑${abs}pp`;
  }
  if (m.unit === "单") return m.delta > 0 ? `+${abs}单` : `-${abs}单`;
  if (m.unit === "轮") return m.delta > 0 ? `-${abs}轮` : `+${abs}轮`;
  if (m.unit === "s") return m.delta > 0 ? `-${abs}秒` : `+${abs}秒`;
  return m.delta > 0 ? `+${abs}` : `-${abs}`;
}

/** 指标说明 — 业务口径 */
export const METRIC_DETAILS: Record<string, { desc: string; source: string }> = {
  first_contact_resolution: {
    desc: "用户问题在首次对话中即得到解决的比例，越高说明「一次搞定」能力越强。",
    source: "工单系统结案记录 + 会话回访",
  },
  tickets_per_agent_day: {
    desc: "每位客服每天可闭环处理的工单数量，反映整体产能提升。",
    source: "工单系统日统计",
  },
  repeat_description_rate: {
    desc: "用户需重复描述同一问题的比例，越低说明上下文理解与记忆越有效。",
    source: "会话质检抽样",
  },
  kb_hit_rate: {
    desc: "咨询问题能命中知识库并给出有效回答的比例。",
    source: "RAG 检索日志 + 人工抽检",
  },
  human_handoff_rate: {
    desc: "对话最终转接人工的比例，越低说明智能解决覆盖面越广。",
    source: "路由与转人工日志",
  },
  avg_turns: {
    desc: "完成一次咨询所需的平均对话轮次，越少说明交互越高效。",
    source: "会话 Trace 统计",
  },
  avg_response_sec: {
    desc: "用户发出消息后收到回复的平均等待时间。",
    source: "会话 Trace 统计",
  },
};

export function targetStatus(m: RoiMetric): "done" | "near" | "pending" {
  const pct = progressPct(m);
  if (pct >= 100) return "done";
  if (pct >= 75) return "near";
  return "pending";
}

export function targetStatusLabel(m: RoiMetric): string {
  const s = targetStatus(m);
  if (s === "done") return "已达标";
  if (s === "near") return "接近目标";
  return "待提升";
}

/** 距目标差距文案 */
export function gapToTarget(m: RoiMetric): string {
  const { current, target, unit, lower_is_better } = m;
  if (lower_is_better) {
    if (current <= target) return "已达 MVP 目标";
    const gap = current - target;
    return `距目标还差 ${formatMetricValue(gap, unit)}`;
  }
  if (current >= target) return "已达 MVP 目标";
  const gap = target - current;
  return `距目标还差 ${formatMetricValue(gap, unit)}`;
}

export interface RoiOverviewItem {
  metric: RoiMetric;
  reason: string;
}

export interface RoiOverview {
  total: number;
  doneCount: number;
  nearCount: number;
  pendingCount: number;
  improvedCount: number;
  highlights: RoiOverviewItem[];
  issues: RoiOverviewItem[];
  summary: string;
}

function highlightReason(m: RoiMetric): string {
  if (targetStatus(m) === "done") {
    return `已达标 · 当前 ${formatMetricValue(m.current, m.unit)}`;
  }
  return `${formatDelta(m)} · 完成 ${formatProgress(m)}`;
}

function issueReason(m: RoiMetric): string {
  if (!m.improved) {
    return `较基线未改善 · 当前 ${formatMetricValue(m.current, m.unit)}`;
  }
  return `${gapToTarget(m)} · 完成 ${formatProgress(m)}`;
}

/** 从指标列表生成总览：亮点 + 需关注 */
export function buildRoiOverview(metrics: RoiMetric[]): RoiOverview {
  const doneCount = metrics.filter((m) => targetStatus(m) === "done").length;
  const nearCount = metrics.filter((m) => targetStatus(m) === "near").length;
  const pendingCount = metrics.filter((m) => targetStatus(m) === "pending").length;
  const improvedCount = metrics.filter((m) => m.improved).length;

  const highlights = metrics
    .filter((m) => targetStatus(m) === "done" || (m.improved && progressPct(m) >= 75))
    .sort((a, b) => progressPct(b) - progressPct(a))
    .slice(0, 3)
    .map((metric) => ({ metric, reason: highlightReason(metric) }));

  const issues = metrics
    .filter((m) => targetStatus(m) === "pending" || !m.improved)
    .sort((a, b) => progressPct(a) - progressPct(b))
    .slice(0, 3)
    .map((metric) => ({ metric, reason: issueReason(metric) }));

  let summary: string;
  if (doneCount === metrics.length) {
    summary = `全部 ${metrics.length} 项指标已达标，试点成效显著。`;
  } else if (issues.length === 0) {
    summary = `${improvedCount}/${metrics.length} 项较基线改善，${doneCount} 项已达标，整体向好。`;
  } else if (highlights.length === 0) {
    summary = `${issues.length} 项需重点关注，建议优先排查未改善指标。`;
  } else {
    summary = `${improvedCount}/${metrics.length} 项较基线改善，${doneCount} 项已达标，${issues.length} 项待跟进。`;
  }

  return {
    total: metrics.length,
    doneCount,
    nearCount,
    pendingCount,
    improvedCount,
    highlights,
    issues,
    summary,
  };
}
