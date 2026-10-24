import fs from "node:fs";
import path from "node:path";
import { expect, Page, test } from "@playwright/test";

type BaselineSection = { row_count: number; records: Record<string, unknown>[] };
type Scenario = {
  filters: Record<string, string | string[]>;
  kpi_display: { metric: string; value: string; change: string | null }[];
  kpis: BaselineSection;
  revenue_trend: BaselineSection;
  revenue_by_branch: BaselineSection;
  gross_margin_by_model: BaselineSection;
};

const baselinePath = path.resolve(process.cwd(), "../tests/parity_baseline.json");
const baseline = JSON.parse(fs.readFileSync(baselinePath, "utf8")) as { scenarios: Record<string, Scenario> };

async function signIn(page: Page) {
  await page.goto("/login");
  await page.getByLabel("Email Address").fill("demo@versalmotors.com");
  await page.getByLabel("Password", { exact: true }).fill("VersalDemo2026!");
  await page.getByRole("button", { name: "Sign In" }).click();
  await expect(page).toHaveURL(/\/overview(?:\?.*)?$/);
}

function queryFor(filters: Scenario["filters"]) {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (Array.isArray(value)) value.forEach((item) => params.append(key, item));
    else if (value !== null) params.set(key, value);
  }
  return params.toString();
}

test("every Overview display value and API record matches the frozen baseline", async ({ page }) => {
  test.setTimeout(300_000);
  await signIn(page);
  const endpoints = {
    kpis: "/api/v1/overview/kpis",
    revenue_trend: "/api/v1/overview/revenue-trend",
    revenue_by_branch: "/api/v1/overview/revenue-by-branch",
    gross_margin_by_model: "/api/v1/overview/margin-by-model",
  } as const;

  for (const [scenarioName, scenario] of Object.entries(baseline.scenarios)) {
    const query = queryFor(scenario.filters);
    await page.goto(`/overview?${query}`);
    if (scenarioName === "empty_result") {
      await expect(page.getByRole("heading", { name: "No records match these filters" })).toBeVisible();
    } else {
      for (const expected of scenario.kpi_display) {
        const card = page.locator(`[data-metric="${expected.metric}"]`);
        await expect(card).toBeVisible();
        await expect(card.locator(".kpi-value-row > strong")).toHaveText(expected.value);
        if (expected.change) await expect(card.locator("footer")).toContainText(expected.change);
        else await expect(card.locator("footer")).toContainText("Prior-period comparison unavailable");
      }
      await expect(page.locator('[aria-label^="Revenue trend chart"]')).toHaveAttribute("aria-label", `Revenue trend chart with ${scenario.revenue_trend.row_count} periods`);
      await expect(page.locator('[aria-label^="Revenue by branch chart"]')).toHaveAttribute("aria-label", `Revenue by branch chart with ${scenario.revenue_by_branch.row_count} branches`);
      await expect(page.locator('[aria-label^="Gross margin by model chart"]')).toHaveAttribute("aria-label", `Gross margin by model chart with ${scenario.gross_margin_by_model.row_count} models`);
    }
    for (const [section, endpoint] of Object.entries(endpoints) as [keyof typeof endpoints, string][]) {
      const response = await page.request.get(`${endpoint}?${query}`);
      expect(response.ok(), `${scenarioName}.${section}`).toBeTruthy();
      const payload = await response.json() as { data: Record<string, unknown>[] };
      expect(payload.data, `${scenarioName}.${section}`).toEqual(scenario[section].records);
    }
  }
});

test("shared filters use the URL and persist across protected pages", async ({ page }) => {
  await signIn(page);
  await expect(page).toHaveURL(/start_date=2025-04-02/);
  await expect(page).toHaveURL(/end_date=2025-06-30/);
  await page.getByLabel("Branch").selectOption("Accra");
  await expect(page).toHaveURL(/branch=Accra/);
  await page.getByRole("link", { name: "Investigate" }).click();
  await expect(page).toHaveURL(/\/investigate\?.*branch=Accra/);
  await page.getByRole("link", { name: "Overview" }).click();
  await expect.poll(() => page.getByLabel("Branch").evaluate((element) => Array.from((element as HTMLSelectElement).selectedOptions, (option) => option.value))).toEqual(["Accra"]);
  await expect(page.locator('[data-metric="Revenue"] .kpi-value-row > strong')).toHaveText("GHS 277,136,681");
});

test("Overview shows loading, error, and empty states without crashing", async ({ page }) => {
  test.setTimeout(120_000);
  await page.route("**/api/v1/overview/kpis?**", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 350));
    await route.continue();
  });
  await signIn(page);
  await expect(page.getByLabel("Loading business overview")).toBeVisible();
  await expect(page.locator('[data-metric="Revenue"]')).toBeVisible();
  await page.unroute("**/api/v1/overview/kpis?**");

  await page.route("**/api/v1/overview/revenue-trend?**", (route) => route.fulfill({ status: 503, contentType: "application/json", body: JSON.stringify({ message: "unavailable" }) }));
  await page.goto(`/overview?${queryFor(baseline.scenarios.full_range.filters)}`);
  await expect(page.locator(".overview-state[role=alert]")).toContainText("Overview data is temporarily unavailable");
  await page.unroute("**/api/v1/overview/revenue-trend?**");

  await page.goto(`/overview?${queryFor(baseline.scenarios.empty_result.filters)}`);
  await expect(page.getByRole("heading", { name: "No records match these filters" })).toBeVisible();
});

test("Overview is responsive and theme-complete at approved widths", async ({ page }) => {
  await signIn(page);
  for (const width of [375, 768, 1280]) {
    await page.setViewportSize({ width, height: 900 });
    const open = page.getByRole("button", { name: "Open navigation menu" });
    if (await open.isVisible()) await open.click();
    const dark = page.getByRole("button", { name: "Dark mode" });
    if (await dark.isVisible()) await dark.click();
    await expect(page.locator("body")).toHaveCSS("background-color", "rgb(15, 23, 42)");
    await expect(page.locator(".overview-kpi").first()).toBeVisible();
    const dimensions = await page.evaluate(() => ({ scroll: document.documentElement.scrollWidth, inner: window.innerWidth }));
    expect(dimensions.scroll).toBeLessThanOrEqual(dimensions.inner);
    const light = page.getByRole("button", { name: "Light mode" });
    if (await light.isVisible()) await light.click();
  }
});
