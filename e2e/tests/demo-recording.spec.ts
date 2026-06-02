import { test, expect, type Page, type Locator } from "@playwright/test";

async function pause(page: Page, ms: number) {
  await page.waitForTimeout(ms);
}

function lastAgentReply(page: Page): Locator {
  return page.locator(".chat-row-agent .chat-bubble-agent").last();
}

async function sendChat(page: Page, message: string) {
  await page.getByPlaceholder("请输入问题").fill(message);
  await page.getByRole("button", { name: "发送" }).click();
}

/** 5 分钟产品演示 — 单条连续录屏（对应 docs/DEMO.md 动线） */
test("demo walkthrough for assets/demo.mp4", async ({ page }) => {
  test.setTimeout(300000);

  await page.goto("/chat");
  await pause(page, 2000);

  await test.step("E2E-001 知识咨询", async () => {
    await sendChat(page, "企业版和专业版区别");
    await expect(lastAgentReply(page)).toContainText("企业版", { timeout: 25000 });
    await pause(page, 3000);
  });

  await test.step("E2E-002 创建工单", async () => {
    await sendChat(page, "服务器宕机请尽快处理");
    await expect(lastAgentReply(page)).toContainText("T-", { timeout: 25000 });
    await pause(page, 3000);
  });

  await test.step("E2E-003 查进度", async () => {
    await sendChat(page, "查 T-001 进度");
    await expect(lastAgentReply(page)).toContainText("T-001", { timeout: 25000 });
    await pause(page, 3000);
  });

  await test.step("E2E-004 投诉转人工", async () => {
    await page.getByRole("button", { name: "新对话" }).click();
    await pause(page, 1000);
    await sendChat(page, "三次没解决要投诉");
    await expect(lastAgentReply(page)).toContainText(/转接|人工/, { timeout: 30000 });
    await pause(page, 2500);
  });

  await test.step("E2E-007 Guardrail", async () => {
    await page.getByRole("button", { name: "新对话" }).click();
    await pause(page, 1000);
    await sendChat(page, "我的密码是abc123");
    await expect(lastAgentReply(page)).toContainText("敏感", { timeout: 25000 });
    await pause(page, 3000);
  });

  await test.step("工单中心", async () => {
    await page.goto("/tickets");
    await expect(page.locator("body")).toContainText("工单", { timeout: 15000 });
    await pause(page, 3000);
  });

  await test.step("业务 ROI", async () => {
    await page.goto("/roi");
    await expect(page.locator("body")).toContainText("业务 ROI 看板", { timeout: 15000 });
    await expect(page.locator("body")).toContainText("总览", { timeout: 15000 });
    await pause(page, 2500);
    const metricBtn = page.locator(".roi-metric-card-btn").first();
    if (await metricBtn.isVisible()) {
      await metricBtn.click();
      await pause(page, 3000);
    }
    const highlightBtn = page.locator(".roi-overview-item").first();
    if (await highlightBtn.isVisible()) {
      await highlightBtn.click();
      await pause(page, 2000);
    }
  });

  await test.step("Bad Case 七层", async () => {
    await page.goto("/ops");
    await expect(page.locator("body")).toContainText("运营后台", { timeout: 15000 });
    await pause(page, 2000);
    const seedBtn = page.getByRole("button", { name: /载入七层演示/ });
    if (await seedBtn.isVisible()) {
      await seedBtn.click();
      await pause(page, 4000);
    }
  });

  await test.step("评测报告", async () => {
    await page.goto("/eval");
    await expect(page.locator("body")).toContainText("Eval Harness", { timeout: 15000 });
    await pause(page, 4000);
  });
});
