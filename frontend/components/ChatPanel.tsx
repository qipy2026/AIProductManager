"use client";

import { useCallback, useEffect, useState } from "react";
import ChatMessageView from "@/components/ChatMessageView";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  traceId?: string;
  intent?: string;
  confidence?: number;
  sources?: { id?: string; title?: string; url?: string }[];
}

interface SessionItem {
  session_id: string;
  title: string;
  updated_at: string;
  message_count: number;
}

function newSessionId() {
  return `sess-${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}`;
}

export default function ChatPanel() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState("");
  const [sessions, setSessions] = useState<SessionItem[]>([]);
  const [loadingSession, setLoadingSession] = useState(false);

  const loadSessions = useCallback(async () => {
    try {
      const res = await fetch("/api/sessions?limit=50");
      if (!res.ok) return;
      const data = await res.json();
      setSessions(data.sessions ?? []);
    } catch {
      /* ignore */
    }
  }, []);

  useEffect(() => {
    setSessionId(newSessionId());
    loadSessions();
  }, [loadSessions]);

  async function loadSession(sid: string) {
    if (sid === sessionId && messages.length > 0) return;
    setLoadingSession(true);
    try {
      const res = await fetch(`/api/sessions/${encodeURIComponent(sid)}`);
      if (!res.ok) {
        setSessionId(sid);
        setMessages([]);
        return;
      }
      const data = await res.json();
      setSessionId(data.session_id);
      setMessages(
        (data.messages ?? []).map(
          (m: {
            role: string;
            content: string;
            trace_id?: string;
            intent?: string;
            confidence?: number;
            sources?: ChatMessage["sources"];
          }) => ({
            role: m.role as "user" | "assistant",
            content: m.content,
            traceId: m.trace_id,
            intent: m.intent,
            confidence: m.confidence,
            sources: m.sources,
          })
        )
      );
    } catch {
      setSessionId(sid);
      setMessages([]);
    } finally {
      setLoadingSession(false);
    }
  }

  function startNewChat() {
    const sid = newSessionId();
    setSessionId(sid);
    setMessages([]);
    setInput("");
  }

  async function send() {
    if (!input.trim() || loading || loadingSession || !sessionId) return;
    const userMsg = input.trim();
    setInput("");
    setMessages((m) => [...m, { role: "user", content: userMsg }]);
    setLoading(true);
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg, session_id: sessionId }),
      });
      const data = await res.json();
      if (data.session_id && data.session_id !== sessionId) {
        setSessionId(data.session_id);
      }
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: data.response,
          traceId: data.trace_id,
          intent: data.intent,
          confidence: data.confidence,
          sources: data.sources,
        },
      ]);
      await loadSessions();
    } catch {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: "连接后端失败，请确认 uvicorn 已启动（:8000）。" },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ display: "flex", gap: 16, alignItems: "stretch" }}>
      <aside
        data-testid="session-sidebar"
        style={{
          width: 220,
          flexShrink: 0,
          border: "1px solid #eee",
          borderRadius: 8,
          padding: 12,
          background: "#fafafa",
        }}
      >
        <button
          type="button"
          data-testid="new-chat-btn"
          onClick={startNewChat}
          style={{
            width: "100%",
            padding: "8px 12px",
            marginBottom: 12,
            borderRadius: 6,
            border: "1px solid #0066cc",
            background: "#0066cc",
            color: "#fff",
            cursor: "pointer",
          }}
        >
          新对话
        </button>
        <div data-testid="session-list" style={{ fontSize: 13 }}>
          {sessions.length === 0 && (
            <p style={{ color: "#999", margin: 0 }}>暂无历史对话</p>
          )}
          {sessions.map((s) => (
            <button
              key={s.session_id}
              type="button"
              data-testid={`session-item-${s.session_id}`}
              onClick={() => loadSession(s.session_id)}
              style={{
                display: "block",
                width: "100%",
                textAlign: "left",
                padding: "8px 10px",
                marginBottom: 4,
                borderRadius: 6,
                border: "none",
                background: s.session_id === sessionId ? "#e8f0fe" : "transparent",
                cursor: "pointer",
                color: "#333",
              }}
            >
              <div
                style={{
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                  fontWeight: s.session_id === sessionId ? 600 : 400,
                }}
              >
                {s.title || "未命名对话"}
              </div>
              <div style={{ fontSize: 11, color: "#888" }}>{s.message_count} 条消息</div>
            </button>
          ))}
        </div>
      </aside>

      <div style={{ flex: 1, minWidth: 0 }}>
        <p style={{ color: "#666" }} suppressHydrationWarning>
          Harness 通路 · Session: {sessionId || "…"}
        </p>
        <div className="panel" data-testid="chat-messages" style={{ minHeight: 360, marginBottom: 16 }}>
          {loadingSession && <p style={{ color: "#999" }}>加载历史消息…</p>}
          {!loadingSession && messages.length === 0 && (
            <p style={{ color: "#999" }}>输入消息开始对话…</p>
          )}
          {messages.map((m, i) => (
            <ChatMessageView key={i} message={m} index={i} />
          ))}
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
            placeholder="请输入问题…"
            style={{ flex: 1, padding: 8, borderRadius: 4, border: "1px solid #ccc" }}
          />
          <button onClick={send} disabled={loading || loadingSession || !sessionId} style={{ padding: "8px 16px" }}>
            {loading ? "…" : "发送"}
          </button>
        </div>
      </div>
    </div>
  );
}
