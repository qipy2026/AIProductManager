"use client";

import TicketDetailPanel from "@/components/TicketDetailPanel";
import { PRIORITY_LABEL, STATUS_LABEL, type TicketItem } from "@/lib/tickets";

interface Props {
  ticket: TicketItem;
  expanded: boolean;
  onToggle: () => void;
}

export default function TicketCatalogItem({ ticket, expanded, onToggle }: Props) {
  const isOpen = ticket.status !== "closed";
  const isUrgent = ticket.priority === "urgent";

  return (
    <div
      className={`eval-catalog-item ${expanded ? "expanded" : ""} ${
        isOpen ? "ticket-catalog-item-open" : ""
      }`}
      data-testid={`ticket-item-${ticket.id}`}
    >
      <button type="button" className="eval-catalog-item-head" onClick={onToggle} aria-expanded={expanded}>
        <span className="eval-catalog-chevron" aria-hidden>
          {expanded ? "▾" : "▸"}
        </span>
        <code className="eval-catalog-case-id">{ticket.id}</code>
        <span className={`ticket-status ticket-status-${ticket.status}`}>
          {STATUS_LABEL[ticket.status] ?? ticket.status}
        </span>
        <span className="eval-catalog-summary">{ticket.title}</span>
        {isUrgent ? (
          <span className="ticket-priority-urgent">{PRIORITY_LABEL.urgent}</span>
        ) : (
          <span className="ops-hint-inline">{PRIORITY_LABEL.normal}</span>
        )}
      </button>
      {expanded && (
        <div className="eval-catalog-item-body">
          <TicketDetailPanel ticket={ticket} embedded />
        </div>
      )}
    </div>
  );
}
