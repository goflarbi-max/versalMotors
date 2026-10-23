import { defineConfig, devices, type PlaywrightTestConfig } from "@playwright/test";

const python = process.env.PYTHON_BIN ?? (
  process.platform === "win32" ? ".\\.venv\\Scripts\\python.exe" : "python"
);

const webServer: PlaywrightTestConfig["webServer"] = process.env.PLAYWRIGHT_EXTERNAL_SERVERS ? undefined : [
  {
    command: `${python} -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000`,
    cwd: "..",
    url: "http://127.0.0.1:8000/health/ready",
    reuseExistingServer: true,
    timeout: 120_000,
    env: {
      VERSALMOTORS_ALLOWED_ORIGINS: "http://127.0.0.1:3000",
      VERSALMOTORS_SECURE_COOKIES: "false",
      VERSALMOTORS_SESSION_SECRET: "phase-two-browser-test-secret",
    },
  },
  {
    command: "npm run start -- --hostname 127.0.0.1 --port 3000",
    cwd: ".",
    url: "http://127.0.0.1:3000",
    reuseExistingServer: true,
    timeout: 120_000,
    env: { BACKEND_URL: "http://127.0.0.1:8000" },
  },
];

export default defineConfig({
  testDir: "./playwright",
  fullyParallel: false,
  retries: 0,
  reporter: "list",
  use: {
    baseURL: "http://127.0.0.1:3000",
    trace: "retain-on-failure",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
  ],
  webServer,
});
