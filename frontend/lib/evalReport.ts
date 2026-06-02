/** Eval 报告展示辅助 — 与 harness/eval/report_enrich.py 对齐. */

import { getAttribution, type AttributionLayer } from "@/lib/attributions";

export interface EvalCaseResult {
  case_id: string;
  layer: string;
  passed: boolean;
  failures: string[];
  description?: string;
  message?: string;
  input?: Record<string, unknown>;
  assertions?: Record<string, unknown>;
  attribution?: string;
  fix_hint?: string;
  yaml_path?: string;
}

export interface EvalCaseDetail {
  case_id: string;
  layer: string;
  description: string;
  input: Record<string, unknown>;
  assertions: Record<string, unknown>;
  yaml_path: string;
}

export interface LayerSummary {
  layer: string;
  label: string;
  desc: string;
  focus: string;
  passed: number;
  failed: number;
  total: number;
  pass_rate: number;
}

export interface EvalReport {
  total: number;
  passed: number;
  failed: number;
  pass_rate: number;
  gate?: number;
  gate_passed?: boolean;
  by_layer: Record<string, { passed: number; failed: number; total: number }>;
  layer_summary?: LayerSummary[];
  results?: EvalCaseResult[];
  failed_cases?: EvalCaseResult[];
  failure_by_attribution?: Record<string, number>;
  failure_by_assertion?: Record<string, number>;
  case_catalog_size?: number;
  error?: string;
}

export const LAYER_COLORS: Record<string, string> = {
  L1: "#0891b2",
  L2: "#d97706",
  L3: "#059669",
  L4: "#db2777",
  L5: "#7c3aed",
};

export function groupFailuresByAttribution(
  cases: EvalCaseResult[]
): { layer: AttributionLayer; items: EvalCaseResult[] }[] {
  const buckets = new Map<string, EvalCaseResult[]>();
  for (const c of cases) {
    const key = c.attribution || "skill";
    if (!buckets.has(key)) buckets.set(key, []);
    buckets.get(key)!.push(c);
  }
  const out: { layer: AttributionLayer; items: EvalCaseResult[] }[] = [];
  for (const [key, items] of buckets) {
    const layer = getAttribution(key);
    if (layer) out.push({ layer, items });
  }
  return out.sort((a, b) => b.items.length - a.items.length);
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
