import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { expect, Page, test } from "@playwright/test";

const root = path.resolve(process.cwd(), "..");
const output = path.join(root, "docs", "screenshots", "parity");
const afterDir = path.join(output, "high-after");
const diffDir = path.join(output, "high-diff");
const beforeDir = path.join(output, "high-before");
const python = process.env.PYTHON_BIN ?? (process.platform === "win32" ? path.join(root, ".venv", "Scripts", "python.exe") : "python");
const diffScript = path.join(root, "tests", "visual", "image_diff.py");

async function signIn(page: Page) {
  await page.goto("/login");
  await page.getByLabel("Email Address").fill("demo@versalmotors.com");
  await page.getByLabel("Password", { exact: true }).fill("VersalDemo2026!");
  await page.getByRole("button", { name: "Sign In" }).click();
  await expect(page).toHaveURL(/\/overview(?:\?.*)?$/);
}

async function setTheme(page: Page, theme: "light" | "dark") {
  await page.evaluate((next) => {
    localStorage.setItem("versal_theme", next);
    document.cookie = `versal_theme=${next}; Max-Age=31536000; Path=/; SameSite=Lax`;
    document.documentElement.dataset.theme = next;
  }, theme);
}

async function capture(page: Page, state: string, width: number, theme: "light" | "dark") {
  const filename = `${state}-${width}-${theme}-nextjs.png`;
  const after = path.join(afterDir, filename);
  await page.screenshot({ path: after, fullPage: true, animations: "disabled" });
  const before = path.join(beforeDir, filename);
  if (fs.existsSync(before)) {
    execFileSync(python, [diffScript, before, after, path.join(diffDir, `${state}-${width}-${theme}-before-after.png`)]);
  }
}

async function openWithReadyState(page: Page, route: string, readyText: string) {
  for (let attempt = 0; attempt < 3; attempt += 1) {
    await page.goto(route);
    try {
      await expect(page.getByText(readyText, { exact: true }).first()).toBeVisible({ timeout: 30_000 });
      return;
    } catch {
      if (attempt === 2) throw new Error(`${route} did not reach its ready state after three attempts`);
    }
  }
}

test("capture High-severity parity fixes after implementation", async ({ page }) => {
  test.setTimeout(600_000);
  fs.mkdirSync(afterDir, { recursive: true });
  fs.mkdirSync(diffDir, { recursive: true });
  await signIn(page);
  for (const width of [375, 768, 1280]) {
    await page.setViewportSize({ width, height: 900 });
    for (const theme of ["light", "dark"] as const) {
      await setTheme(page, theme);
      await page.goto("/overview");
      await expect(page.getByRole("link", { name: "Investigate warranty costs" })).toBeVisible({ timeout: 60_000 });
      await capture(page, "overview", width, theme);

      await openWithReadyState(page, "/ask-the-business", "Available over 90 days");
      await page.getByRole("button", { name: "Revenue trend" }).click();
      await expect(page.getByRole("table", { name: /Evidence for:/ })).toBeVisible({ timeout: 60_000 });
      await capture(page, "ask-after", width, theme);

      await openWithReadyState(page, "/data-quality", "Highest Share");
      await expect(page.getByText("No cleaning log file found - showing live checks only (acceptable).")).toBeVisible({ timeout: 60_000 });
      await capture(page, "data-quality", width, theme);
    }
  }
});
