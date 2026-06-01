"use client";

import Link from "next/link";
import { useState } from "react";
import type { ChatMessage } from "@/components/ChatPanel";
import { MarkdownBody, parseAssistantContent } from "@/lib/chatContent";

interface Props {
  message: ChatMessage;
  index: number;
}

function ChatAvatar({ role }: { role: "user" | "assistant" }) {
  const isUser = role === "user";
  return (
    <div
      className={`chat-avatar ${isUser ? "chat-avatar-user" : "chat-avatar-agent"}`}
      aria-label={isUser ? "用户" : "Agent"}
      title={isUser ? "你" : "Agent"}
    >
      {isUser ? (
        <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden>
          <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
        </svg>
      ) : (
        <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden>
          <path d="M12 2l1.2 4.2L17.5 7.5 13.2 8.7 12 13l-1.2-4.3L6.5 7.5l4.3-1.3L12 2z" />
          <path d="M19 13l.7 2.3L22 16l-2.3.7L19 19l-.7-2.3L16 16l2.3-.7L19 13z" opacity="0.9" />
          <path d="M5 14l.6 2.1L7.7 17l-2.1.6L5 20l-.6-2.4L2.3 17l2.1-.6L5 14z" opacity="0.85" />
        </svg>
      )}
    </div>
  );
}

function ThinkingBlock({ content }: { content: string }) {
  const [open, setOpen] = useState(true);
  if (!content.trim()) return null;

  return (
    <div className="chat-thinking" data-testid="thinking-block">
      <button
        type="button"
        className="chat-thinking-toggle"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
      >
        <span className="chat-thinking-icon">{open ? "▼" : "▶"}</span>
        思考过程
      </button>
      {open && (
        <div className="chat-thinking-body">
          {content.split("\n").map((line, i) => (
            <p key={i}>{line || "\u00a0"}</p>
          ))}
        </div>
      )}
    </div>
  );
}

function sourceHref(source: { id?: string; title?: string; url?: string }): string {
  const url = source.url?.trim();
  if (url?.startsWith("http://") || url?.startsWith("https://")) return url;
  if (url?.startsWith("/")) return url;
  if (source.id) return `/kb/${source.id}`;
  return "";
}

function SourceTags({ sources }: { sources: NonNullable<ChatMessage["sources"]> }) {
  if (!sources.length) return null;
  return (
    <div className="chat-sources">
      <span className="chat-sources-label">📎 来源</span>
      {sources.map((s, i) => {
        const href = sourceHref(s);
        const label = s.title || s.id || "文档";
        if (!href) {
          return (
            <span key={s.id ?? i} className="chat-source-tag">
              {label}
            </span>
          );
        }
        const external = href.startsWith("http");
        if (external) {
          return (
            <a
              key={s.id ?? i}
              href={href}
              className="chat-source-tag chat-source-link"
              target="_blank"
              rel="noopener noreferrer"
            >
              {label}
            </a>
          );
        }
        return (
          <Link key={s.id ?? i} href={href} className="chat-source-tag chat-source-link">
            {label}
          </Link>
        );
      })}
    </div>
  );
}

function MetaLine({ message }: { message: ChatMessage }) {
  if (!message.traceId) return null;
  return (
    <div className="chat-meta">
      trace: {message.traceId.slice(0, 8)}…
      {message.intent && (
        <>
          {" · "}
          intent: {message.intent}
          {message.confidence != null && message.confidence > 0
            ? ` (${(message.confidence * 100).toFixed(0)}%)`
            : ""}
        </>
      )}
    </div>
  );
}

export default function ChatMessageView({ message, index }: Props) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="chat-row chat-row-user" data-testid={`chat-msg-${index}`}>
        <div className="chat-bubble chat-bubble-user">
          <div className="chat-label">你</div>
          <div className="chat-text">{message.content}</div>
        </div>
        <ChatAvatar role="user" />
      </div>
    );
  }

  const { thinking, body } = parseAssistantContent(message.content);
  const displayBody = body || message.content;

  return (
    <div className="chat-row chat-row-agent" data-testid={`chat-msg-${index}`}>
      <ChatAvatar role="assistant" />
      <div className="chat-bubble chat-bubble-agent">
        <div className="chat-label">Agent</div>
        {thinking && <ThinkingBlock content={thinking} />}
        <div className="chat-answer">
          <MarkdownBody text={displayBody} />
        </div>
        {message.sources && message.sources.length > 0 && (
          <SourceTags sources={message.sources} />
        )}
        <MetaLine message={message} />
      </div>
    </div>
  );
}
