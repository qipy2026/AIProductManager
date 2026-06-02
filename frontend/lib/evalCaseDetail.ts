/** 格式化评测断言为可读列表. */

export function formatAssertionLines(assertions: Record<string, unknown> | undefined): string[] {
  if (!assertions) return [];
  const lines: string[] = [];

  const skill = assertions.skill as Record<string, unknown> | undefined;
  if (skill) {
    for (const s of (skill.must_invoke as string[]) || []) {
      lines.push(`Skill 必须调用：${s}`);
    }
    for (const s of (skill.must_not_invoke as string[]) || []) {
      lines.push(`Skill 禁止调用：${s}`);
    }
  }

  const intent = assertions.intent as Record<string, unknown> | undefined;
  if (intent?.equals) {
    lines.push(`意图等于：${intent.equals}`);
  }

  const mem = assertions.memory as Record<string, unknown> | undefined;
  if (mem) {
    for (const m of (mem.must_inject as string[]) || []) {
      lines.push(`Memory 必须注入：${m}`);
    }
    for (const m of (mem.must_not_inject as string[]) || []) {
      lines.push(`Memory 禁止注入：${m}`);
    }
  }

  const resp = assertions.response as Record<string, unknown> | undefined;
  if (resp) {
    for (const k of (resp.must_contain as string[]) || []) {
      lines.push(`回复须包含：${k}`);
    }
    for (const k of (resp.must_not_contain as string[]) || []) {
      lines.push(`回复禁止包含：${k}`);
    }
  }

  const src = assertions.source as Record<string, unknown> | undefined;
  if (src?.min_count) {
    lines.push(`来源引用最少：${src.min_count} 条`);
  }

  if (assertions.blocked === true) {
    lines.push("须被 Guardrail 拦截");
  }
  if (assertions.blocked === false) {
    lines.push("不得被 Guardrail 拦截");
  }

  return lines;
}
