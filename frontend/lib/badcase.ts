/** Bad Case 展示辅助 — 与 backend/badcase/enrich.py 对齐. */

import {
  ATTRIBUTION_LAYERS,
  getAttribution,
  groupByAttribution,
  normalizeAttributionKey,
  OTHER_ATTRIBUTION,
} from "@/lib/attributions";

export interface BadCaseItem {
  id?: number;
  trace_id?: string;
  case_id?: string;
  layer?: string;
  attribution: string;
  attribution_label?: string;
  attribution_focus?: string;
  note?: string;
  failures?: string[];
  fix_hint?: string;
}

export interface BadCaseListResponse {
  items: BadCaseItem[];
  total: number;
  by_attribution?: Record<string, number>;
}

export { ATTRIBUTION_LAYERS, getAttribution, groupByAttribution, normalizeAttributionKey, OTHER_ATTRIBUTION };

export function countAllAttributions(items: BadCaseItem[]): Record<string, number> {
  const out: Record<string, number> = {};
  for (const l of ATTRIBUTION_LAYERS) out[l.key] = 0;
  out.other = 0;
  for (const b of items) {
    const key = normalizeAttributionKey(b.attribution);
    out[key] = (out[key] ?? 0) + 1;
  }
  return out;
}

export function assertionLabel(failure: string): string {
  if (failure.startsWith("must_invoke")) return "Skill 路由";
  if (failure.startsWith("must_not_invoke")) return "Skill 越界";
  if (failure.startsWith("response must")) return "回复内容";
  if (failure.startsWith("must_inject")) return "Memory 注入";
  if (failure.startsWith("intent expected")) return "意图识别";
  if (failure.includes("source")) return "来源引用";
  if (failure.includes("blocked")) return "Guardrail";
  return "其他断言";
}
