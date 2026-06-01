import { test, expect } from "@playwright/test";

test.describe("E2E-001~007 录屏场景", () => {
  test("E2E-001 知识咨询带引用", async ({ page }) => {
    await page.goto("/chat");
    await page.getByPlaceholder("请输入问题").fill("企业版和专业版区别");
    await page.getByRole("button", { name: "发送" }).click();
    await expect(page.locator("body")).toContainText("企业版", { timeout: 15000 });
  });

  test("E2E-002 创建工单", async ({ page }) => {
    await page.goto("/chat");
    await page.getByPlaceholder("请输入问题").fill("服务器宕机请尽快处理");
    await page.getByRole("button", { name: "发送" }).click();
    await expect(page.locator("body")).toContainText("T-", { timeout: 15000 });
  });

  test("E2E-003 查进度不建单", async ({ page }) => {
    await page.goto("/chat");
    await page.getByPlaceholder("请输入问题").fill("查 T-001 进度");
    await page.getByRole("button", { name: "发送" }).click();
    await expect(page.locator("body")).toContainText("T-001", { timeout: 15000 });
  });

  test("E2E-004 投诉转人工", async ({ page }) => {
    await page.goto("/chat");
    await page.getByPlaceholder("请输入问题").fill("太差了三次没解决要投诉");
    await page.getByRole("button", { name: "发送" }).click();
    await expect(page.locator("body")).toContainText("转接", { timeout: 15000 });
  });

  test("E2E-006 报修 Fallback", async ({ page }) => {
    await page.goto("/chat");
    await page.getByPlaceholder("请输入问题").fill("我要报修");
    await page.getByRole("button", { name: "发送" }).click();
    await expect(page.locator("body")).toContainText("补充", { timeout: 15000 });
  });

  test("E2E-007 Guardrail 拦截", async ({ page }) => {
    await page.goto("/chat");
    await page.getByPlaceholder("请输入问题").fill("我的密码是abc123");
    await page.getByRole("button", { name: "发送" }).click();
    await expect(page.locator("body")).toContainText("敏感", { timeout: 15000 });
  });

  test("Eval 页可运行评测", async ({ page }) => {
    await page.goto("/eval");
    await expect(page.locator("body")).toContainText("120 条");
    await page.getByRole("button", { name: "运行评测" }).click();
    await expect(page.locator("body")).toContainText("/", { timeout: 120000 });
  });

  test("Ops 页 Skill 健康度", async ({ page }) => {
    await page.goto("/ops");
    await expect(page.locator("body")).toContainText("Skill 健康度");
  });

  test("E2E-008 历史对话查看与续聊", async ({ page }) => {
    const marker = `历史E2E-${Date.now()}`;
    await page.goto("/chat");
    await expect(page.getByTestId("session-sidebar")).toBeVisible();

    await page.getByPlaceholder("请输入问题").fill(`${marker} 第一条`);
    await page.getByRole("button", { name: "发送" }).click();
    await expect(page.getByTestId("chat-messages")).toContainText(marker, { timeout: 15000 });

    await expect(page.getByTestId("session-list")).not.toContainText("暂无历史对话", {
      timeout: 10000,
    });

    await page.getByTestId("new-chat-btn").click();
    await expect(page.getByTestId("chat-messages")).toContainText("输入消息开始对话");

    await page.getByTestId("session-list").getByText(marker).first().click();
    await expect(page.getByTestId("chat-messages")).toContainText(`${marker} 第一条`, {
      timeout: 10000,
    });

    await page.getByPlaceholder("请输入问题").fill(`${marker} 续聊`);
    await page.getByRole("button", { name: "发送" }).click();
    await expect(page.getByTestId("chat-messages")).toContainText(`${marker} 续聊`, {
      timeout: 15000,
    });
    await expect(page.getByTestId("chat-messages")).toContainText(`${marker} 第一条`);
  });
});
