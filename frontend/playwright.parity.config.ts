import { defineConfig, type PlaywrightTestConfig } from "@playwright/test";

const python = process.env.PYTHON_BIN ?? (
  process.platform === "win32" ? ".\\.venv\\Scripts\\python.exe" : "python"
);

const webServer: PlaywrightTestConfig["webServer"] = process.env.PARITY_EXTERNAL_SERVERS ? undefined : [
  {
    command: `${python} -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000`,
    cwd: "..",
    url: "http://127.0.0.1:8000/health/ready",
    reuseExistingServer: true,
    timeout: 180_000,
    env: {
      VERSALMOTORS_ALLOWED_ORIGINS: "http://127.0.0.1:3000",
      VERSALMOTORS_SECURE_COOKIES: "false",
      VERSALMOTORS_SESSION_SECRET: "parity-audit-only-secret",
      GEMINI_API_KEY: "",
      GOOGLE_API_KEY: "",
    },
  },
  {
    command: "npm run dev -- --hostname 127.0.0.1 --port 3000",
    cwd: ".",
    url: "http://127.0.0.1:3000",
    reuseExistingServer: true,
    timeout: 180_000,
    env: { API_ORIGIN: "http://127.0.0.1:8000" },
  },
  {
    command: `${python} -m streamlit run app.py --server.headless true --server.port 8501 --browser.gatherUsageStats false`,
    cwd: "..",
    url: "http://127.0.0.1:8501",
    reuseExistingServer: true,
    timeout: 180_000,
  },
];

export default defineConfig({
  testDir: "./playwright",
  testMatch: "parity-compare.spec.ts",
  fullyParallel: false,
  workers: 1,
  timeout: 1_800_000,
  reporter: "list",
  use: {
    trace: "retain-on-failure",
    reducedMotion: "reduce",
    actionTimeout: 20_000,
    navigationTimeout: 60_000,
  },
  expect: { timeout: 15_000 },
  webServer,
});
