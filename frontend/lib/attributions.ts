/** Bad Case 七层归因 — 中文说明与展示映射. */

export interface AttributionLayer {
  key: string;
  label: string;
  short: string;
  symptom: string;
  action: string;
  color: string;
}

export const ATTRIBUTION_LAYERS: AttributionLayer[] = [
  {
    key: "model",
    label: "模型层",
    short: "大模型本身",
    symptom: "回答胡编、风格漂移、理解偏差",
    action: "换模型 / 调温度 / Replay 对比",
    color: "#7c3aed",
  },
  {
    key: "prompt",
    label: "Prompt 层",
    short: "提示词模板",
    symptom: "某类问题稳定答错，换问法就好",
    action: "改 Prompt 版本、补 few-shot",
    color: "#2563eb",
  },
  {
    key: "skill",
    label: "Skill 层",
    short: "技能编排",
    symptom: "该查知识却建单、Skill 漏调或多调",
    action: "改 Skill 路由 / 补断言回归",
    color: "#0891b2",
  },
  {
    key: "knowledge",
    label: "知识层",
    short: "知识库内容",
    symptom: "检索到了，但文档内容本身过时或错误",
    action: "更新 FAQ / 文档版本审计",
    color: "#059669",
  },
  {
    key: "retrieval",
    label: "检索层",
    short: "RAG 召回",
    symptom: "找不到文档、引用了错误的条目",
    action: "调阈值 / 补文档 / 跑 L2 评测",
    color: "#d97706",
  },
  {
    key: "flow",
    label: "流程层",
    short: "业务状态机",
    symptom: "权限拒绝、状态跳转错误、Guardrail 误拦",
    action: "查 Trace 时间线、改流程规则",
    color: "#dc2626",
  },
  {
    key: "memory",
    label: "Memory 层",
    short: "记忆注入",
    symptom: "忘记上文、重复追问、用户画像冲突",
    action: "调 Memory Router / L4 回归",
    color: "#db2777",
  },
];

const BY_KEY = Object.fromEntries(ATTRIBUTION_LAYERS.map((l) => [l.key, l]));

/** 非标准 attribution 映射到七层 */
const ALIAS: Record<string, string> = {
  guardrail: "flow",
  流程: "flow",
  eval_failure: "other",
};

export const OTHER_ATTRIBUTION: AttributionLayer = {
  key: "other",
  label: "待归类",
  short: "评测失败或未映射",
  symptom: "Eval 自动写入或 attribution 不在七层内",
  action: "人工确认后改选正确层级",
  color: "#6b7280",
};

export function normalizeAttributionKey(key: string): string {
  const lower = key.toLowerCase();
  if (BY_KEY[lower]) return lower;
  if (ALIAS[lower]) return ALIAS[lower];
  if (ALIAS[key]) return ALIAS[key];
  return "other";
}

export function getAttribution(key: string): AttributionLayer | undefined {
  const norm = normalizeAttributionKey(key);
  if (norm === "other" && key && !BY_KEY[key.toLowerCase()] && !ALIAS[key.toLowerCase()] && !ALIAS[key]) {
    return OTHER_ATTRIBUTION;
  }
  return BY_KEY[norm] ?? (norm === "other" ? OTHER_ATTRIBUTION : undefined);
}

export function attributionLabel(key: string): string {
  return getAttribution(key)?.label ?? key;
}

export function groupByAttribution<T extends { attribution: string }>(
  items: T[]
): { layer: AttributionLayer; items: T[] }[] {
  const buckets = new Map<string, T[]>();
  for (const l of ATTRIBUTION_LAYERS) buckets.set(l.key, []);
  buckets.set("other", []);

  for (const item of items) {
    const key = normalizeAttributionKey(item.attribution);
    buckets.get(key)!.push(item);
  }

  const result: { layer: AttributionLayer; items: T[] }[] = [];
  for (const l of ATTRIBUTION_LAYERS) {
    const group = buckets.get(l.key)!;
    if (group.length > 0) result.push({ layer: l, items: group });
  }
  const other = buckets.get("other")!;
  if (other.length > 0) result.push({ layer: OTHER_ATTRIBUTION, items: other });
  return result;
}
