import fs from "node:fs";
import path from "node:path";
import { expect, Page, test } from "@playwright/test";

type Snapshot = { row_count: number; records: Record<string, unknown>[] };
type InvestigateBaseline = {
  filters: Record<string, string | string[]>;
  selected_model: string;
  selected_branch: string;
  models: Snapshot;
  branches: Snapshot;
  claims: Snapshot;
};

const baselinePath = path.resolve(process.cwd(), "../tests/parity_baseline.json");
const baseline = (JSON.parse(fs.readFileSync(baselinePath, "utf8")) as { investigate: InvestigateBaseline }).investigate;

async function signIn(page: Page) {
  await page.goto("/login");
  await page.getByLabel("Email Address").fill("demo@versalmotors.com");
  await page.getByLabel("Password", { exact: true }).fill("VersalDemo2026!");
  await page.getByRole("button", { name: "Sign In" }).click();
  await expect(page).toHaveURL(/\/overview(?:\?.*)?$/);
}

function filterQuery() {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(baseline.filters)) {
    if (Array.isArray(value)) value.forEach((item) => params.append(key, item));
    else if (value !== null && key !== "period") params.set(key, value);
  }
  return params.toString();
}

test("warranty drill-down preserves baseline rows, breadcrumbs, sorting, and paging", async ({ page }) => {
  await signIn(page);
  await page.goto(`/investigate?${filterQuery()}`);

  await expect(page.getByRole("heading", { name: "Warranty cost by model" })).toBeVisible();
  await expect(page.getByText(`Showing 1 to ${baseline.models.row_count} of ${baseline.models.row_count} entries`)).toBeVisible();
  const firstModel = baseline.models.records[0];
  const firstModelRow = page.locator("tbody tr").first();
  await expect(firstModelRow).toContainText(String(firstModel.model));
  await expect(firstModelRow).toContainText(`GHS ${Number(firstModel.claim_cost).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`);
  await page.getByLabel("Choose a model to investigate").selectOption(baseline.selected_model);
  await page.getByRole("button", { name: "View branches" }).click();

  await expect(page).toHaveURL(new RegExp(`focus_model=${baseline.selected_model}`));
  await expect(page.getByRole("heading", { name: `${baseline.selected_model} warranty cost by branch` })).toBeVisible();
  await expect(page.getByText(`Showing 1 to 10 of ${baseline.branches.row_count} entries`)).toBeVisible();
  await page.getByRole("button", { name: "Next page" }).click();
  await expect(page.getByText(`Showing 11 to ${baseline.branches.row_count} of ${baseline.branches.row_count} entries`)).toBeVisible();
  await expect(page.getByRole("button", { name: "Page 2" })).toHaveAttribute("aria-current", "page");
  await page.getByRole("button", { name: "Previous page" }).click();

  const firstBranchRow = page.locator("tbody tr").first();
  await expect(firstBranchRow).toContainText(baseline.selected_branch);
  await page.getByLabel("Choose a branch to inspect").selectOption(baseline.selected_branch);
  await page.getByRole("button", { name: "View claims" }).click();
  await expect(page).toHaveURL(new RegExp(`focus_branch=${baseline.selected_branch}`));
  await expect(page.getByText(`Showing 1 to 10 of ${baseline.claims.row_count} entries`)).toBeVisible();
  await expect(page.getByRole("navigation", { name: "Breadcrumb" })).toContainText(`Overview›Warranty cost›${baseline.selected_model}›${baseline.selected_branch}`);

  await page.getByRole("button", { name: /Sort Approved amount/ }).click();
  await expect(page).toHaveURL(/sort_by=approved_amount/);
  await expect(page).toHaveURL(/sort_dir=asc/);
  await expect(page.locator("tbody tr").first()).toContainText("GHS 0.00");
});

test("claim downloads contain the full filtered data, not only the visible page", async ({ page }) => {
  await signIn(page);
  const query = new URLSearchParams(filterQuery());
  query.set("focus_model", baseline.selected_model);
  query.set("focus_branch", baseline.selected_branch);
  await page.goto(`/investigate?${query.toString()}`);
  await expect(page.getByText(`Showing 1 to 10 of ${baseline.claims.row_count} entries`)).toBeVisible();

  const csvPromise = page.waitForEvent("download");
  await page.getByRole("link", { name: "Download CSV" }).click();
  const csv = await csvPromise;
  const csvPath = await csv.path();
  expect(csvPath).not.toBeNull();
  const lines = fs.readFileSync(csvPath!, "utf8").trimEnd().split(/\r?\n/);
  expect(lines).toHaveLength(baseline.claims.row_count + 1);
  expect(lines[0]).toContain("claim_id,claim_date,model,branch");

  const pdfPromise = page.waitForEvent("download");
  await page.getByRole("link", { name: "Download PDF" }).click();
  const pdf = await pdfPromise;
  const pdfPath = await pdf.path();
  expect(pdfPath).not.toBeNull();
  expect(fs.readFileSync(pdfPath!).subarray(0, 4).toString()).toBe("%PDF");
});

test("Investigate is responsive, theme-complete, and keeps filters at approved widths", async ({ page }) => {
  test.setTimeout(120_000);
  await signIn(page);
  for (const width of [375, 768, 1280]) {
    await page.setViewportSize({ width, height: 900 });
    await page.goto(`/investigate?${filterQuery()}`);
    await expect(page.getByRole("heading", { name: "Warranty cost by model" })).toBeVisible();
    const open = page.getByRole("button", { name: "Open navigation menu" });
    if (await open.isVisible()) await open.click();
    const dark = page.getByRole("button", { name: "Dark mode" });
    if (await dark.isVisible()) await dark.click();
    await expect(page.locator("body")).toHaveCSS("background-color", "rgb(15, 23, 42)");
    await expect(page.getByLabel("From")).toHaveValue("2025-04-02");
    const dimensions = await page.evaluate(() => ({ scroll: document.documentElement.scrollWidth, inner: window.innerWidth }));
    expect(dimensions.scroll).toBeLessThanOrEqual(dimensions.inner);
    const light = page.getByRole("button", { name: "Light mode" });
    if (await light.isVisible()) await light.click();
  }
});
