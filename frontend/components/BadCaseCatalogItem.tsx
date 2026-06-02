"use client";

import BadCaseDetailPanel from "@/components/BadCaseDetailPanel";
import { getAttribution, type BadCaseItem } from "@/lib/badcase";

interface Props {
  item: BadCaseItem;
  expanded: boolean;
  onToggle: () => void;
  onTraceClick?: (traceId: string) => void;
  onAttributionChange?: (id: number, attribution: string) => Promise<void>;
}

export default function BadCaseCatalogItem({
  item,
  expanded,
  onToggle,
  onTraceClick,
  onAttributionChange,
}: Props) {
  const att = getAttribution(item.attribution);
  const summary =
    item.note ||
    (item.failures && item.failures.length > 0 ? item.failures[0] : att?.symptom) ||
    "无备注";

  return (
    <div
      className={`eval-catalog-item ${expanded ? "expanded" : ""} badcase-catalog-item`}
      data-testid={item.id ? `badcase-item-${item.id}` : undefined}
    >
      <button type="button" className="eval-catalog-item-head" onClick={onToggle} aria-expanded={expanded}>
        <span className="eval-catalog-chevron" aria-hidden>
          {expanded ? "▾" : "▸"}
        </span>
        {item.case_id ? (
          <code className="eval-catalog-case-id">{item.case_id}</code>
        ) : item.trace_id ? (
          <code className="eval-catalog-case-id">{item.trace_id.slice(0, 10)}…</code>
        ) : (
          <span className="eval-catalog-case-id">手动登记</span>
        )}
        {att && (
          <span
            className="badcase-att-badge"
            style={{ background: `${att.color}18`, color: att.color, borderColor: `${att.color}40` }}
          >
            {att.label}
          </span>
        )}
        {item.layer && <span className="eval-catalog-layer">{item.layer}</span>}
        <span className="eval-catalog-summary">{summary}</span>
        {item.failures && item.failures.length > 1 && (
          <span className="eval-status-fail">{item.failures.length} 项</span>
        )}
      </button>
      {expanded && (
        <div className="eval-catalog-item-body">
          <BadCaseDetailPanel
            item={item}
            embedded
            onTraceClick={onTraceClick}
            onAttributionChange={onAttributionChange}
          />
        </div>
      )}
    </div>
  );
}
