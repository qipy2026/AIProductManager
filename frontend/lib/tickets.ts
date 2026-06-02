/** 工单展示辅助 — 与 backend/api/tickets.py 对齐. */

export interface TicketItem {
  id: string;
  title: string;
  status: string;
  priority: string;
  created_at?: string;
}

export interface TicketListResponse {
  items: TicketItem[];
  total: number;
}

export const STATUS_LABEL: Record<string, string> = {
  new: "新建",
  in_progress: "处理中",
  closed: "已关闭",
  escalated: "已升级",
};

export const PRIORITY_LABEL: Record<string, string> = {
  urgent: "紧急",
  normal: "普通",
};

export const STATUS_COLORS: Record<string, string> = {
  new: "#2563eb",
  in_progress: "#d97706",
  closed: "#64748b",
  escalated: "#dc2626",
};

export const OPEN_STATUSES = new Set(["new", "in_progress", "escalated"]);

export function isOpenTicket(t: TicketItem): boolean {
  return OPEN_STATUSES.has(t.status);
}

export function formatTicketTime(iso?: string): string {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString("zh-CN");
  } catch {
    return iso;
  }
}

export function countByStatus(items: TicketItem[]): Record<string, number> {
  const out: Record<string, number> = {};
  for (const t of items) {
    out[t.status] = (out[t.status] ?? 0) + 1;
  }
  return out;
}
