import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { expect, Page, test } from "@playwright/test";

const baselinePath = path.resolve(process.cwd(), "../tests/parity_baseline.json");
const baseline = JSON.parse(fs.readFileSync(baselinePath, "utf8")) as {
  data_quality: {
    summary: { issues_found: number; tables_affected: number; total_affected: number; highest_share: number };
    checks: { row_count: number; records: Record<string, unknown>[] };
    cleaning_log: { row_count: number; records: Record<string, unknown>[] };
    csv_bytes: number;
    csv_sha256: string;
  };
};

async function signIn(page: Page) {
  await page.goto("/login");
  await page.getByLabel("Email Address").fill("demo@versalmotors.com");
  await page.getByLabel("Password", { exact: true }).fill("VersalDemo2026!");
  await page.getByRole("button", { name: "Sign In" }).click();
  await expect(page).toHaveURL(/\/overview(?:\?.*)?$/);
}

async function allRecords(page: Page, endpoint: string) {
  const records: Record<string, unknown>[] = [];
  for (let index = 1; ; index += 1) {
    const response = await page.request.get(`${endpoint}?page=${index}&page_size=50`);
    expect(response.ok()).toBeTruthy();
    const payload = await response.json() as { data: { records: Record<string, unknown>[]; total: number } };
    records.push(...payload.data.records);
    if (records.length >= payload.data.total) return records;
  }
}

test("Data Quality summary and checks match the frozen baseline", async ({ page }) => {
  await signIn(page);
  await page.goto("/data-quality");
  const expected = baseline.data_quality;
  await expect(page.locator(".quality-summary-card")).toHaveCount(4);
  for (const value of [expected.summary.issues_found, expected.summary.tables_affected, expected.summary.total_affected]) {
    await expect(page.locator(".quality-summary-grid").getByText(value.toLocaleString("en-US"), { exact: true })).toBeVisible();
  }
  await expect(page.locator(".quality-summary-grid").getByText(`${expected.summary.highest_share.toFixed(1)}%`, { exact: true })).toBeVisible();
  await expect(page.getByText(`Showing 1 to 10 of ${expected.checks.row_count} entries`, { exact: true })).toBeVisible();
  await expect(page.getByText("No cleaning log file found - showing live checks only (acceptable).")).toBeVisible();
  await expect(page.locator(".quality-details details")).toHaveCount(25);

  expect(await allRecords(page, "/api/v1/data-quality/checks")).toEqual(expected.checks.records);
  expect(await allRecords(page, "/api/v1/data-quality/cleaning-log")).toEqual(expected.cleaning_log.records);
});

test("Data Quality sorting, paging, expanders, and complete downloads work", async ({ page }) => {
  await signIn(page);
  await page.goto("/data-quality");
  await expect(page).toHaveURL(/start_date=/);
  const checks = page.locator(".quality-section").first();
  await checks.getByRole("button", { name: /Sort Count/ }).click();
  await expect(page).toHaveURL(/quality_sort=count/);
  await checks.getByRole("button", { name: /Next/ }).click();
  await expect(page).toHaveURL(/quality_page=2/);
  await checks.locator(".quality-details details").first().locator("summary").click();
  await expect(checks.locator(".quality-details details").first().getByText("Impact:")).toBeVisible();
  await expect(checks.locator(".quality-details details").first().getByRole("progressbar")).toBeVisible();

  const csvDownload = page.waitForEvent("download");
  await page.getByRole("link", { name: "Download CSV" }).click();
  const csv = await csvDownload;
  const csvPath = await csv.path();
  expect(csvPath).not.toBeNull();
  const csvBytes = fs.readFileSync(csvPath!);
  expect(csvBytes.length).toBe(baseline.data_quality.csv_bytes);
  expect(crypto.createHash("sha256").update(csvBytes).digest("hex")).toBe(baseline.data_quality.csv_sha256);

  const pdfDownload = page.waitForEvent("download");
  await page.getByRole("link", { name: "Download PDF" }).click();
  const pdf = await pdfDownload;
  const pdfPath = await pdf.path();
  expect(pdfPath).not.toBeNull();
  expect(fs.readFileSync(pdfPath!).subarray(0, 5).toString()).toBe("%PDF-");
});

test("Data Quality has safe failure and empty states", async ({ page }) => {
  await signIn(page);
  await page.route("**/api/v1/data-quality/summary", (route) => route.fulfill({ status: 503, contentType: "application/json", body: JSON.stringify({ message: "unavailable" }) }));
  await page.goto("/data-quality");
  await expect(page.getByRole("heading", { name: "We could not load Data Quality" })).toBeVisible();
  await expect(page.getByText(/503|Traceback|UNAVAILABLE/)).toHaveCount(0);
  await page.unroute("**/api/v1/data-quality/summary");

  await page.route("**/api/v1/data-quality/summary", (route) => route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ data: { issues_found: 0, tables_affected: 0, total_affected: 0, highest_share: 0 }, meta: { filters: {}, data_version: "test", generated_at: "2026-10-24T00:00:00Z" } }) }));
  await page.goto("/data-quality");
  await expect(page.getByRole("heading", { name: "No issues found" })).toBeVisible();
});

test("Data Quality is responsive and theme-complete at approved widths", async ({ page }) => {
  await signIn(page);
  for (const width of [375, 768, 1280]) {
    await page.setViewportSize({ width, height: 900 });
    await page.goto("/data-quality");
    await expect(page.getByRole("heading", { name: "Data Quality Report" })).toBeVisible();
    const open = page.getByRole("button", { name: "Open navigation menu" });
    if (await open.isVisible()) await open.click();
    const dark = page.getByRole("button", { name: "Dark mode" });
    if (await dark.isVisible()) await dark.click();
    await expect(page.locator(".app-shell")).toHaveCSS("background-color", "rgb(15, 23, 42)");
    await expect(page.locator(".quality-summary-card").first()).toBeVisible();
    const dimensions = await page.evaluate(() => ({ scroll: document.documentElement.scrollWidth, inner: window.innerWidth }));
    expect(dimensions.scroll).toBeLessThanOrEqual(dimensions.inner);
  }
});
