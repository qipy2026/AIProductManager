"use client";

import Link from "next/link";
import { useState } from "react";
import {
  ATTRIBUTION_LAYERS,
  assertionLabel,
  getAttribution,
  type BadCaseItem,
} from "@/lib/badcase";

interface Props {
  item: BadCaseItem;
  embedded?: boolean;
  onTraceClick?: (traceId: string) => void;
  onAttributionChange?: (id: number, attribution: string) => Promise<void>;
}

export default function BadCaseDetailPanel({
  item,
  embedded,
  onTraceClick,
  onAttributionChange,
}: Props) {
  const att = getAttribution(item.attribution);
  const [attribution, setAttribution] = useState(item.attribution);
  const [saving, setSaving] = useState(false);

  async function saveAttribution() {
    if (!item.id || !onAttributionChange || attribution === item.attribution) return;
    setSaving(true);
    try {
      await onAttributionChange(item.id, attribution);
    } finally {
      setSaving(false);
    }
  }

  return (
    <section
      className={`ticket-detail-panel ${embedded ? "ticket-detail-embedded" : ""}`}
      data-testid="badcase-detail-panel"
    >
      <div className="eval-case-detail-grid">
        <div className="eval-case-detail-block">
          <h4>现象</h4>
          <p className="eval-case-meta">
            {item.note || (item.failures?.[0] ?? "无备注")}
          </p>
          {item.failures && item.failures.length > 0 && (
            <ul className="eval-failure-list">
              {item.failures.map((f, i) => (
                <li key={i}>
                  <span className="eval-assert-tag">{assertionLabel(f)}</span>
                  {f}
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="eval-case-detail-block eval-case-detail-fail">
          <h4>七层归因 · 修复方向</h4>
          {att && (
            <p className="eval-fix-hint eval-fix-meta">
              <span className="ops-att-dot" style={{ background: att.color }} />
              {att.label} — {att.symptom}
            </p>
          )}
          {item.fix_hint && (
            <p className="eval-fix-hint">
              <strong>建议：</strong>
              {item.fix_hint}
            </p>
          )}
          {item.attribution_focus && (
            <p className="ops-hint">关注：{item.attribution_focus}</p>
          )}
        </div>

        <div className="eval-case-detail-block">
          <h4>关联</h4>
          {item.case_id && (
            <p className="eval-case-meta">
              评测用例：<code>{item.case_id}</code>
              {item.layer && <span> · {item.layer}</span>}
            </p>
          )}
          <div className="eval-case-actions">
            {item.trace_id && onTraceClick ? (
              <button
                type="button"
                className="ops-link-btn"
                onClick={() => onTraceClick(item.trace_id!)}
              >
                查看 Trace · {item.trace_id.slice(0, 12)}…
              </button>
            ) : (
              <span className="ops-hint-inline">Eval 自动录入 · 无 Trace</span>
            )}
            {item.case_id && (
              <Link href="/eval" className="ops-link-btn">
                评测报告
              </Link>
            )}
          </div>
        </div>

        {item.id && onAttributionChange && (
          <div className="eval-case-detail-block">
            <h4>调整归因</h4>
            <div className="ops-form-row">
              <select
                className="ops-input"
                value={attribution}
                onChange={(e) => setAttribution(e.target.value)}
              >
                {ATTRIBUTION_LAYERS.map((l) => (
                  <option key={l.key} value={l.key}>
                    {l.label}
                  </option>
                ))}
              </select>
              <button
                type="button"
                className="ops-btn ops-btn-primary"
                disabled={saving || attribution === item.attribution}
                onClick={saveAttribution}
              >
                {saving ? "保存中…" : "保存归因"}
              </button>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
