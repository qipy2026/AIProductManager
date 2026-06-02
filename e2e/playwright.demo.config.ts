import { defineConfig, devices } from "@playwright/test";

/** 5 分钟 Demo 录屏专用 — 输出 video.webm，由 scripts/record_demo_video.ps1 转为 assets/demo.mp4 */
export default defineConfig({
  testDir: "./tests",
  timeout: 300000,
  outputDir: "./demo-output",
  use: {
    baseURL: process.env.E2E_BASE_URL || "http://localhost:3000",
    ...devices["Desktop Chrome"],
    viewport: { width: 1280, height: 720 },
    video: { mode: "on", size: { width: 1280, height: 720 } },
    launchOptions: { slowMo: 400 },
  },
  projects: [{ name: "demo", use: {} }],
  webServer: process.env.E2E_SKIP_SERVER
    ? undefined
    : [
        {
          command: "python -m uvicorn backend.main:app --host 127.0.0.1 --port 8002",
          cwd: "..",
          url: "http://127.0.0.1:8002/health",
          reuseExistingServer: true,
          timeout: 120000,
          env: {
            AGENTOPS_STORAGE: "memory",
            SEMANTIC_BACKEND: "keyword",
            USE_LANGGRAPH: "0",
            OPS_DB: "sqlite",
            AGENTOPS_DB: "data/demo_record.db",
          },
        },
        {
          command: "npm run dev",
          cwd: "../frontend",
          url: "http://localhost:3000",
          reuseExistingServer: true,
          timeout: 120000,
          env: { BACKEND_URL: "http://127.0.0.1:8002" },
        },
      ],
});
