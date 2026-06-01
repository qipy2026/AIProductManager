/** 解析 LLM 回复：分离思考过程与正文，轻量 Markdown 渲染. */

import type React from "react";

export interface ParsedAssistantContent {
  thinking: string;
  body: string;
}

const THINKING_BLOCK =
  /<(?:think|redacted_thinking)(?:\s[^>]*)?>[\s\S]*?<\/(?:think|redacted_thinking)>/gi;

const THINKING_INNER =
  /<(?:think|redacted_thinking)(?:\s[^>]*)?>([\s\S]*?)<\/(?:think|redacted_thinking)>/gi;

/** 从 Agent 原始回复中提取思考过程与对用户可见的正文. */
export function parseAssistantContent(raw: string): ParsedAssistantContent {
  const thinkingParts: string[] = [];
  let m: RegExpExecArray | null;
  const innerRe = new RegExp(THINKING_INNER.source, "gi");
  while ((m = innerRe.exec(raw)) !== null) {
    const t = m[1].trim();
    if (t) thinkingParts.push(t);
  }
  const body = raw.replace(THINKING_BLOCK, "").trim();
  return { thinking: thinkingParts.join("\n\n"), body };
}

/** 修复 LLM 输出的单行表格（| a | b || c | d |） */
export function normalizeMarkdown(text: string): string {
  return text
    .replace(/\|\|/g, "|\n|")
    .replace(/\n{3,}/g, "\n\n");
}

type Block =
  | { type: "paragraph"; lines: string[] }
  | { type: "table"; headers: string[]; rows: string[][] };

function isTableSeparator(line: string): boolean {
  return /^\|[\s\-:|]+\|$/.test(line.trim());
}

function parseTableRow(line: string): string[] {
  return line
    .trim()
    .replace(/^\|/, "")
    .replace(/\|$/, "")
    .split("|")
    .map((c) => c.trim());
}

function splitIntoBlocks(text: string): Block[] {
  const blocks: Block[] = [];
  const chunks = normalizeMarkdown(text).split(/\n{2,}/);

  for (const chunk of chunks) {
    const lines = chunk.split("\n").filter((l) => l.trim());
    if (lines.length >= 2 && lines.every((l) => l.trim().startsWith("|"))) {
      const headers = parseTableRow(lines[0]);
      const dataLines = lines.slice(1).filter((l) => !isTableSeparator(l));
      blocks.push({
        type: "table",
        headers,
        rows: dataLines.map(parseTableRow),
      });
    } else if (lines.length > 0) {
      blocks.push({ type: "paragraph", lines });
    }
  }
  return blocks;
}

/** 行内 **粗体** */
function renderInline(text: string): React.ReactNode[] {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    return part;
  });
}

export function MarkdownBody({ text }: { text: string }) {
  const blocks = splitIntoBlocks(text.trim());
  if (blocks.length === 0) return null;

  return (
    <div className="chat-md">
      {blocks.map((block, bi) => {
        if (block.type === "table") {
          return (
            <div key={bi} className="chat-table-wrap">
              <table className="chat-table">
                <thead>
                  <tr>
                    {block.headers.map((h, hi) => (
                      <th key={hi}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {block.rows.map((row, ri) => (
                    <tr key={ri}>
                      {row.map((cell, ci) => (
                        <td key={ci}>{cell === "-" ? "—" : cell}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
        }
        return (
          <p key={bi} className="chat-paragraph">
            {block.lines.map((line, li) => (
              <span key={li}>
                {li > 0 && <br />}
                {renderInline(line)}
              </span>
            ))}
          </p>
        );
      })}
    </div>
  );
}
