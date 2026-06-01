import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  timeout: 60000,
  use: {
    baseURL: process.env.E2E_BASE_URL || "http://localhost:3000",
    trace: "on-first-retry",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: process.env.E2E_SKIP_SERVER
    ? undefined
    : [
        {
          command: "python -m uvicorn backend.main:app --host 127.0.0.1 --port 8002",
          cwd: "..",
          url: "http://127.0.0.1:8002/health",
          reuseExistingServer: true,
          env: {
            AGENTOPS_STORAGE: "memory",
            SEMANTIC_BACKEND: "keyword",
            USE_LANGGRAPH: "0",
            OPS_DB: "sqlite",
            AGENTOPS_DB: "data/e2e_agentops.db",
          },
        },
        {
          command: "npm run dev",
          cwd: "../frontend",
          url: "http://localhost:3000",
          reuseExistingServer: true,
          env: { BACKEND_URL: "http://127.0.0.1:8002" },
        },
      ],
});
