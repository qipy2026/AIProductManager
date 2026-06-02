"use client";

import { getAttribution } from "@/lib/attributions";
import { formatAssertionLines } from "@/lib/evalCaseDetail";
import { assertionLabel, type EvalCaseResult } from "@/lib/evalReport";

interface Props {
  c: EvalCaseResult;
  onReplay?: (c: EvalCaseResult) => void;
  onClose?: () => void;
  /** 行内展开模式：不重复展示标题栏 */
  embedded?: boolean;
}

export default function EvalCaseDetailPanel({ c, onReplay, onClose, embedded }: Props) {
  const att = c.attribution ? getAttribution(c.attribution) : undefined;
  const assertLines = formatAssertionLines(c.assertions as Record<string, unknown>);
  const inp = c.input || {};
  const memoryFixture = inp.memory_fixture as Record<string, unknown> | null | undefined;

  return (
    <section
      className={`eval-case-detail ${embedded ? "eval-case-detail-embedded" : ""}`}
      data-testid="eval-case-detail"
    >
      {!embedded && (
        <div className="eval-case-detail-head">
          <div>
            <h3 className="eval-case-detail-title">
              <code>{c.case_id}</code>
              <span className="eval-case-desc">{c.layer}</span>
              {c.passed ? (
                <span className="eval-status-pass">PASS</span>
              ) : (
                <span className="eval-status-fail">FAIL</span>
              )}
            </h3>
            {c.description && <p className="eval-case-detail-desc">{c.description}</p>}
          </div>
          {onClose && (
            <button type="button" className="ops-btn ops-btn-secondary" onClick={onClose}>
              关闭
            </button>
          )}
        </div>
      )}

      <div className="eval-case-detail-grid">
        <div className="eval-case-detail-block">
          <h4>输入</h4>
          {c.message && (
            <p className="eval-case-input">
              消息：<code>{c.message}</code>
            </p>
          )}
          {inp.user_id && (
            <p className="eval-case-meta">user_id：<code>{String(inp.user_id)}</code></p>
          )}
          {inp.session_id && (
            <p className="eval-case-meta">session_id：<code>{String(inp.session_id)}</code></p>
          )}
          {memoryFixture && (
            <pre className="eval-case-pre">{JSON.stringify(memoryFixture, null, 2)}</pre>
          )}
        </div>

        <div className="eval-case-detail-block">
          <h4>断言（YAML）</h4>
          {assertLines.length === 0 ? (
            <p className="ops-hint">无结构化断言</p>
          ) : (
            <ul className="eval-assert-list">
              {assertLines.map((line, i) => (
                <li key={i}>{line}</li>
              ))}
            </ul>
          )}
        </div>

        {!c.passed && c.failures.length > 0 && (
          <div className="eval-case-detail-block eval-case-detail-fail">
            <h4>本次失败</h4>
            <ul className="eval-failure-list">
              {c.failures.map((f, i) => (
                <li key={i}>
                  <span className="eval-assert-tag">{assertionLabel(f)}</span>
                  {f}
                </li>
              ))}
            </ul>
            {c.fix_hint && (
              <p className="eval-fix-hint">
                <strong>修复方向：</strong>
                {c.fix_hint}
              </p>
            )}
            {att && (
              <p className="eval-fix-hint eval-fix-meta">
                归因 · {att.label} — {att.action}
              </p>
            )}
          </div>
        )}

        <div className="eval-case-detail-block">
          <h4>源文件</h4>
          <p className="ops-hint-inline">{c.yaml_path}</p>
          {onReplay && c.message && (
            <button type="button" className="ops-link-btn" style={{ marginTop: 8 }} onClick={() => onReplay(c)}>
              Replay 本条
            </button>
          )}
        </div>
      </div>
    </section>
  );
}
