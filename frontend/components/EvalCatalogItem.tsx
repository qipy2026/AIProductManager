"use client";

import EvalCaseDetailPanel from "@/components/EvalCaseDetailPanel";
import type { EvalCaseResult } from "@/lib/evalReport";

interface Props {
  c: EvalCaseResult;
  expanded: boolean;
  loading?: boolean;
  onToggle: () => void;
  onReplay: (c: EvalCaseResult) => void;
}

export default function EvalCatalogItem({ c, expanded, loading, onToggle, onReplay }: Props) {
  return (
    <div
      className={`eval-catalog-item ${expanded ? "expanded" : ""} ${c.passed ? "" : "eval-catalog-item-fail"}`}
      data-testid={`eval-catalog-item-${c.case_id}`}
    >
      <button type="button" className="eval-catalog-item-head" onClick={onToggle} aria-expanded={expanded}>
        <span className="eval-catalog-chevron" aria-hidden>
          {expanded ? "▾" : "▸"}
        </span>
        <code className="eval-catalog-case-id">{c.case_id}</code>
        <span className="eval-catalog-layer">{c.layer}</span>
        <span className="eval-catalog-summary">{c.description || "—"}</span>
        {c.passed ? (
          <span className="eval-status-pass">PASS</span>
        ) : (
          <span className="eval-status-fail" title={c.failures.join("; ")}>
            FAIL ({c.failures.length})
          </span>
        )}
      </button>
      {expanded && (
        <div className="eval-catalog-item-body">
          {loading ? (
            <p className="ops-hint">正在加载断言与输入…</p>
          ) : (
            <EvalCaseDetailPanel c={c} embedded onReplay={onReplay} />
          )}
        </div>
      )}
    </div>
  );
}
