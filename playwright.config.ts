import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "e2e",
  timeout: 60_000,
  expect: { timeout: 15_000 },
  use: {
    baseURL: "http://127.0.0.1:3001",
    viewport: { width: 1280, height: 720 },
    screenshot: "off",
    trace: "off",
  },
  webServer: {
    command: "cd frontend && npm run dev -- --port 3001",
    url: "http://127.0.0.1:3001",
    reuseExistingServer: true,
    timeout: 120_000,
  },
});

