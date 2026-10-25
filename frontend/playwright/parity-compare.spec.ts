import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { Browser, Page, test } from "@playwright/test";

const nextBase = process.env.PARITY_NEXT_URL ?? "http://127.0.0.1:3000";
const streamlitBase = process.env.PARITY_STREAMLIT_URL ?? "http://127.0.0.1:8501";
const email = process.env.PARITY_EMAIL ?? "demo@versalmotors.com";
const password = process.env.PARITY_PASSWORD ?? "VersalDemo2026!";
const root = path.resolve(process.cwd(), "..");
const output = path.join(root, "docs", "screenshots", "parity");
const python = process.env.PYTHON_BIN ?? (process.platform === "win32" ? path.join(root, ".venv", "Scripts", "python.exe") : "python");
const diffScript = path.join(root, "tests", "visual", "image_diff.py");

type App = "streamlit" | "nextjs";
type Theme = "light" | "dark";
type DiffResult = { changed_pixels: number; total_pixels: number; difference_pct: number; width: number; height: number };

async function settle(page: Page) {
  await page.waitForLoadState("domcontentloaded");
  await page.evaluate(() => Promise.race([
    document.fonts.ready,
    new Promise((resolve) => window.setTimeout(resolve, 2_000)),
  ]));
  await page.waitForTimeout(450);
}

async function signIn(page: Page, app: App) {
  await page.goto(`${app === "nextjs" ? nextBase : streamlitBase}/login`);
  await page.getByLabel("Email Address").fill(email);
  await page.getByLabel("Password", { exact: true }).fill(password);
  await page.getByRole("button", { name: "Sign In" }).click();
  await page.waitForTimeout(app === "streamlit" ? 8_000 : 2_000);
}

async function ensureStreamlitSidebar(page: Page, open: boolean) {
  const closeControl = page.locator(
    'button[data-testid="stSidebarCollapseButton"], [data-testid="stSidebarCollapseButton"] button',
  ).first();
  const expanded = await closeControl.isVisible().catch(() => false);
  if (expanded === open) return;
  const control = open
    ? page.locator('button[data-testid="stExpandSidebarButton"], [data-testid="stExpandSidebarButton"] button, [data-testid="stSidebarCollapsedControl"] button, button[aria-label*="open sidebar" i], button[aria-label*="expand sidebar" i]').first()
    : closeControl;
  await control.click({ force: true });
  await page.waitForTimeout(250);
}

async function clearBrokenStreamlitMobileOverlay(page: Page) {
  await page.evaluate(() => {
    document.documentElement.classList.remove("versal-mobile-nav-open");
    document.querySelectorAll(".versal-sidebar-backdrop").forEach((element) => element.remove());
  });
}

async function closeStreamlitMobileDrawer(page: Page) {
  if ((page.viewportSize()?.width ?? 1280) > 640) return;
  const closeControl = page.locator(
    'button[data-testid="stSidebarCollapseButton"], [data-testid="stSidebarCollapseButton"] button',
  ).first();
  if ((await closeControl.count()) > 0) {
    await closeControl.evaluate((button: HTMLElement) => button.click()).catch(() => undefined);
    await page.waitForTimeout(300);
  }
  await clearBrokenStreamlitMobileOverlay(page);
}

async function setTheme(page: Page, app: App, theme: Theme) {
  if (app === "nextjs") {
    const current = await page.locator("html").getAttribute("data-theme");
    if (current !== theme) {
      const open = page.getByRole("button", { name: "Open navigation menu" });
      if (await open.isVisible().catch(() => false)) await open.click();
      await page.getByRole("button", { name: theme === "dark" ? "Dark mode" : "Light mode" }).click();
    }
    return;
  }
  let toggle = page
    .getByRole("checkbox", { name: /Dark mode|Light mode/i })
    .or(page.getByRole("switch", { name: /Dark mode|Light mode/i }))
    .first();
  if ((await toggle.count()) === 0) {
    await ensureStreamlitSidebar(page, true);
    toggle = page
      .getByRole("checkbox", { name: /Dark mode|Light mode/i })
      .or(page.getByRole("switch", { name: /Dark mode|Light mode/i }))
      .first();
  }
  await toggle.waitFor({ state: "attached", timeout: 30_000 });
  const checked = await toggle.isChecked();
  if (checked !== (theme === "dark")) {
    await toggle.click({ force: true });
    await page.waitForTimeout(700);
  }
}

async function visit(page: Page, app: App, nextPath: string, streamlitPath: string) {
  process.stdout.write(`parity: visit ${app} ${app === "nextjs" ? nextPath : streamlitPath}\n`);
  if (app === "nextjs") {
    await page.goto(`${nextBase}${nextPath}`);
    if (await page.getByLabel("Email Address").isVisible().catch(() => false)) await signIn(page, app);
    await settle(page);
    return;
  }

  if (await page.getByLabel("Email Address").isVisible().catch(() => false)) await signIn(page, app);
  const labels: Record<string, string> = {
    "/overview": "Overview",
    "/investigate": "Investigate",
    "/ask_the_business": "Ask the Business",
    "/management_brief": "Management Brief",
    "/data_quality": "Data Quality",
  };
  const label = labels[streamlitPath];
  if (label) {
    await page.getByRole("link", { name: new RegExp(`${label}$`, "i") }).evaluate((link: HTMLElement) => link.click());
    await page.waitForTimeout(2_000);
    await closeStreamlitMobileDrawer(page);
  }
  await settle(page);
  process.stdout.write(`parity: ready ${app} ${app === "nextjs" ? nextPath : streamlitPath}\n`);
}

async function capturePair(streamlit: Page, nextjs: Page, state: string, width: number, theme: Theme, results: Record<string, DiffResult>) {
  if (state !== "sidebar-open") await clearBrokenStreamlitMobileOverlay(streamlit);
  await settle(streamlit); await settle(nextjs);
  const stem = `${state}-${width}-${theme}`;
  const streamlitPath = path.join(output, `${stem}-streamlit.png`);
  const nextPath = path.join(output, `${stem}-nextjs.png`);
  const diffPath = path.join(output, `${stem}-diff.png`);
  await streamlit.screenshot({ path: streamlitPath, fullPage: true, animations: "disabled" });
  await nextjs.screenshot({ path: nextPath, fullPage: true, animations: "disabled" });
  const raw = execFileSync(python, [diffScript, streamlitPath, nextPath, diffPath], { encoding: "utf8" });
  results[stem] = JSON.parse(raw.trim()) as DiffResult;
  fs.writeFileSync(path.join(output, "visual-diff-summary.json"), JSON.stringify(results, null, 2));
}

async function selectStreamlitMulti(page: Page, label: string, value: string) {
  const input = page.getByRole("combobox", { name: label });
  await input.waitFor({ state: "attached", timeout: 60_000 });
  await input.evaluate((element: HTMLElement) => element.click());
  await input.fill(value);
  await page.getByRole("option", { name: value, exact: true }).evaluate((option: HTMLElement) => option.click());
  await page.waitForTimeout(500);
}

async function prepareInvestigate(page: Page, app: App, level: "models" | "branches" | "claims") {
  if (app === "nextjs") {
    const params = new URLSearchParams({ start_date: "2025-04-02", end_date: "2025-06-30" });
    if (level !== "models") params.set("focus_model", "Hilux");
    if (level === "claims") params.set("focus_branch", "Kumasi");
    await visit(page, app, `/investigate?${params}`, "/investigate");
    return;
  }
  await visit(page, app, "/investigate", "/investigate");
  if (level === "models") {
    const reset = page.getByRole("button", { name: "Warranty cost", exact: true });
    if (await reset.isVisible().catch(() => false)) {
      await reset.evaluate((button: HTMLElement) => button.click());
    }
    await page.getByRole("heading", { name: "Warranty cost by model" }).waitFor();
    return;
  }
  const modelPicker = page.getByLabel("Choose a model to investigate");
  if (await modelPicker.isVisible().catch(() => false)) {
    if ((await modelPicker.inputValue()) !== "Hilux") {
      await modelPicker.click();
      await modelPicker.fill("Hilux");
      await modelPicker.press("ArrowDown");
      await modelPicker.press("Enter");
    }
    await page.getByRole("button", { name: /View branches/ }).evaluate((button: HTMLElement) => button.click());
  }
  await page.getByRole("heading", { name: /Hilux: warranty cost by branch/ }).waitFor();
  if (level === "branches") return;
  const branchPicker = page.getByLabel("Choose a branch to inspect");
  if (await branchPicker.isVisible().catch(() => false)) {
    if ((await branchPicker.inputValue()) !== "Kumasi") {
      await branchPicker.click();
      await branchPicker.fill("Kumasi");
      await branchPicker.press("ArrowDown");
      await branchPicker.press("Enter");
    }
    await page.getByRole("button", { name: /View claims/ }).evaluate((button: HTMLElement) => button.click());
  }
  await page.getByRole("heading", { name: /Hilux claims at Kumasi/ }).waitFor();
}

async function prepareAskAfter(page: Page, app: App) {
  await visit(page, app, "/ask-the-business", "/ask_the_business");
  if (app === "streamlit") {
    await page.getByText("Revenue trend", { exact: true }).last().evaluate((label: HTMLElement) => {
      label.closest("button")?.click();
    });
  } else {
    await page.getByRole("button", { name: "Revenue trend" }).click();
  }
  if (app === "nextjs") await page.locator(".assistant-answer").last().waitFor({ timeout: 60_000 });
  else await page.locator('[data-testid="stChatMessage"]').last().waitFor({ timeout: 60_000 });
}

async function prepareBrief(page: Page, app: App) {
  await visit(page, app, "/management-brief", "/management_brief");
  const generate = page.getByRole("button", { name: /Generate/ });
  if (app === "streamlit") {
    await generate.evaluate((button: HTMLElement) => button.click());
  } else {
    await generate.click();
  }
  await page.getByRole("heading", { name: "Supporting Evidence" }).waitFor({ timeout: 90_000 });
}

async function newAuditPage(browser: Browser, width: number) {
  const context = await browser.newContext({ viewport: { width, height: 900 }, reducedMotion: "reduce" });
  return { context, page: await context.newPage() };
}

test("capture Streamlit and Next.js parity screenshots and diffs", async ({ browser }) => {
  fs.mkdirSync(output, { recursive: true });
  const results: Record<string, DiffResult> = {};
  const widths = (process.env.PARITY_WIDTHS ?? "375,768,1280").split(",").map(Number);
  const themes = (process.env.PARITY_THEMES ?? "light,dark").split(",") as Theme[];
  for (const width of widths) {
    for (const theme of themes) {
      const oldApp = await newAuditPage(browser, width);
      const newApp = await newAuditPage(browser, width);
      await oldApp.page.goto(streamlitBase); await newApp.page.goto(nextBase);
      await capturePair(oldApp.page, newApp.page, "landing", width, theme, results);
      await oldApp.page.goto(`${streamlitBase}/login`); await newApp.page.goto(`${nextBase}/login`);
      await capturePair(oldApp.page, newApp.page, "login", width, theme, results);

      await signIn(oldApp.page, "streamlit"); await signIn(newApp.page, "nextjs");
      await setTheme(oldApp.page, "streamlit", theme); await setTheme(newApp.page, "nextjs", theme);
      await capturePair(oldApp.page, newApp.page, "overview", width, theme, results);

      for (const level of ["models", "branches", "claims"] as const) {
        await prepareInvestigate(oldApp.page, "streamlit", level);
        await prepareInvestigate(newApp.page, "nextjs", level);
        await setTheme(oldApp.page, "streamlit", theme); await setTheme(newApp.page, "nextjs", theme);
        await capturePair(oldApp.page, newApp.page, `investigate-${level}`, width, theme, results);
      }

      await visit(oldApp.page, "streamlit", "/ask-the-business", "/ask_the_business");
      await visit(newApp.page, "nextjs", "/ask-the-business", "/ask_the_business");
      await setTheme(oldApp.page, "streamlit", theme); await setTheme(newApp.page, "nextjs", theme);
      await capturePair(oldApp.page, newApp.page, "ask-before", width, theme, results);
      await prepareAskAfter(oldApp.page, "streamlit"); await prepareAskAfter(newApp.page, "nextjs");
      await setTheme(oldApp.page, "streamlit", theme); await setTheme(newApp.page, "nextjs", theme);
      await capturePair(oldApp.page, newApp.page, "ask-after", width, theme, results);

      await prepareBrief(oldApp.page, "streamlit"); await prepareBrief(newApp.page, "nextjs");
      await setTheme(oldApp.page, "streamlit", theme); await setTheme(newApp.page, "nextjs", theme);
      await capturePair(oldApp.page, newApp.page, "management-brief", width, theme, results);

      await visit(oldApp.page, "streamlit", "/data-quality", "/data_quality");
      await visit(newApp.page, "nextjs", "/data-quality", "/data_quality");
      await setTheme(oldApp.page, "streamlit", theme); await setTheme(newApp.page, "nextjs", theme);
      await capturePair(oldApp.page, newApp.page, "data-quality", width, theme, results);

      await visit(oldApp.page, "streamlit", "/overview", "/overview");
      await selectStreamlitMulti(oldApp.page, "Branch", "Kasoa");
      await selectStreamlitMulti(oldApp.page, "Model", "Yaris");
      await visit(newApp.page, "nextjs", "/overview?start_date=2025-04-02&end_date=2025-06-30&branch=Kasoa&model=Yaris", "/overview");
      await setTheme(oldApp.page, "streamlit", theme); await setTheme(newApp.page, "nextjs", theme);
      await capturePair(oldApp.page, newApp.page, "empty-filter", width, theme, results);

      await ensureStreamlitSidebar(oldApp.page, true);
      const nextOpen = newApp.page.getByRole("button", { name: "Open navigation menu" });
      if (await nextOpen.isVisible().catch(() => false)) {
        await nextOpen.click({ force: true, noWaitAfter: true });
      }
      await capturePair(oldApp.page, newApp.page, "sidebar-open", width, theme, results);

      await clearBrokenStreamlitMobileOverlay(oldApp.page);
      await ensureStreamlitSidebar(oldApp.page, false);
      const finalNextClose = newApp.page.getByRole("button", { name: "Close navigation menu" });
      if (await finalNextClose.isVisible().catch(() => false)) {
        await finalNextClose.evaluate((button: HTMLElement) => button.click());
      }
      await capturePair(oldApp.page, newApp.page, "sidebar-closed", width, theme, results);
      await oldApp.context.close(); await newApp.context.close();
    }
  }
  fs.writeFileSync(path.join(output, "visual-diff-summary.json"), JSON.stringify(results, null, 2));
});
