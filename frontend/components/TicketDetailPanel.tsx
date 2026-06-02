"use client";

import Link from "next/link";
import {
  formatTicketTime,
  PRIORITY_LABEL,
  STATUS_LABEL,
  type TicketItem,
} from "@/lib/tickets";

interface Props {
  ticket: TicketItem;
  embedded?: boolean;
}

export default function TicketDetailPanel({ ticket, embedded }: Props) {
  const chatQuery = encodeURIComponent(`帮我查一下工单 ${ticket.id} 的处理进度`);

  return (
    <section
      className={`ticket-detail-panel ${embedded ? "ticket-detail-embedded" : ""}`}
      data-testid="ticket-detail-panel"
    >
      {!embedded && (
        <header className="ticket-detail-head">
          <h3 className="eval-case-detail-title">
            <code>{ticket.id}</code>
            <span className={`ticket-status ticket-status-${ticket.status}`}>
              {STATUS_LABEL[ticket.status] ?? ticket.status}
            </span>
          </h3>
        </header>
      )}

      <div className="eval-case-detail-grid">
        <div className="eval-case-detail-block">
          <h4>基本信息</h4>
          <p className="eval-case-meta">
            标题：<strong>{ticket.title}</strong>
          </p>
          <p className="eval-case-meta">
            状态：{STATUS_LABEL[ticket.status] ?? ticket.status}
          </p>
          <p className="eval-case-meta">
            优先级：{PRIORITY_LABEL[ticket.priority] ?? ticket.priority}
          </p>
          <p className="eval-case-meta">创建时间：{formatTicketTime(ticket.created_at)}</p>
        </div>

        <div className="eval-case-detail-block">
          <h4>操作</h4>
          <div className="eval-case-actions">
            <Link href={`/chat?q=${chatQuery}`} className="ops-link-btn">
              在对话中查进度
            </Link>
            <Link href="/ops" className="ops-link-btn">
              运营后台 Trace
            </Link>
          </div>
          <p className="ops-hint" style={{ marginTop: 8 }}>
            工单由 Agent <code>ticket-create</code> Skill 写入；状态流转由规则引擎执行，LLM 不可直接改状态。
          </p>
        </div>
      </div>
    </section>
  );
}
