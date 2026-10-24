import fs from "node:fs";
import path from "node:path";
import { expect, Page, test } from "@playwright/test";

const baselinePath = path.resolve(process.cwd(), "../tests/parity_baseline.json");
const baseline = JSON.parse(fs.readFileSync(baselinePath, "utf8")) as {
  ask_the_business: {
    summary: Record<string, number>;
    questions: Record<string, { question: string; answer: string; result: { row_count: number } }>;
  };
  management_brief: {
    start_date: string;
    end_date: string;
    evidence: { id: string; value: string; number: number }[];
  };
};

async function signIn(page: Page) {
  await page.goto("/login");
  await page.getByLabel("Email Address").fill("demo@versalmotors.com");
  await page.getByLabel("Password", { exact: true }).fill("VersalDemo2026!");
  await page.getByRole("button", { name: "Sign In" }).click();
  await expect(page).toHaveURL(/\/overview(?:\?.*)?$/);
}

test("Ask summary and deterministic data answer match the frozen baseline", async ({ page }) => {
  await signIn(page);
  await page.goto("/ask-the-business");
  await expect(page.getByRole("heading", { name: "Ask the Business" })).toBeVisible();
  await expect(page.locator(".ask-summary-card")).toHaveCount(4, { timeout: 60_000 });
  await expect(page.getByText("GHS 5.58B", { exact: true })).toBeVisible();
  await expect(page.getByText(baseline.ask_the_business.summary.completed_sales.toLocaleString("en-US"), { exact: true })).toBeVisible();
  await expect(page.getByText(String(baseline.ask_the_business.summary.branches), { exact: true })).toBeVisible();
  await expect(page.getByText(baseline.ask_the_business.summary.available_over_90_days.toLocaleString("en-US"), { exact: true })).toBeVisible();

  const expected = baseline.ask_the_business.questions.revenue_trend;
  await page.getByRole("button", { name: "Revenue trend" }).click();
  await expect(page.getByRole("heading", { name: "Facts" })).toBeVisible();
  await expect(page.getByText(expected.answer, { exact: true })).toBeVisible();
  await expect(page.getByText(/Supporting evidence \(32\)/)).toBeVisible();
  await expect(page.getByText(/SELECT |FROM sales|WITH /i)).toHaveCount(0);
});

test("Ask input submits with Enter and failures remain friendly", async ({ page }) => {
  await signIn(page);
  await page.goto("/ask-the-business");
  const input = page.getByLabel("Ask about the business");
  await input.fill("Why is our competitor doing better?");
  await input.press("Enter");
  await expect(page.getByText(/cannot support competitor comparisons/i)).toBeVisible();

  await page.route("**/api/v1/ask/questions", (route) => route.fulfill({ status: 503, contentType: "application/json", body: JSON.stringify({ message: "The question could not be answered safely." }) }));
  await input.fill("Which branch had the most valid complaints?");
  await input.press("Enter");
  await expect(page.locator(".ask-error")).toContainText("could not be answered safely");
  await expect(page.getByText(/503|UNAVAILABLE|Traceback/i)).toHaveCount(0);
});

test("Management Brief evidence and exact cached downloads match the baseline", async ({ page }) => {
  test.setTimeout(180_000);
  await signIn(page);
  await page.goto("/management-brief");
  await page.getByLabel("Start date").fill(baseline.management_brief.start_date);
  await page.getByLabel("End date").fill(baseline.management_brief.end_date);
  await page.getByRole("button", { name: "Generate Management Brief" }).click();
  await expect(page.getByText("Supporting Evidence", { exact: true })).toBeVisible({ timeout: 120_000 });
  for (const item of baseline.management_brief.evidence) {
    await expect(page.locator(".brief-evidence-summary").getByText(item.value, { exact: true })).toBeVisible();
  }

  const markdownDownload = page.waitForEvent("download");
  await page.getByRole("link", { name: "Download Markdown" }).click();
  const markdown = await markdownDownload;
  expect(markdown.suggestedFilename()).toMatch(/^management_brief_.+\.md$/);
  const markdownPath = await markdown.path();
  expect(markdownPath).not.toBeNull();
  expect(fs.readFileSync(markdownPath!, "utf8")).toContain("GHS 3,127,546,494.94");

  const pdfDownload = page.waitForEvent("download");
  await page.getByRole("link", { name: "Download PDF" }).click();
  const pdf = await pdfDownload;
  expect(pdf.suggestedFilename()).toMatch(/^management_brief_.+\.pdf$/);
  const pdfPath = await pdf.path();
  expect(pdfPath).not.toBeNull();
  expect(fs.readFileSync(pdfPath!).subarray(0, 5).toString()).toBe("%PDF-");
});

test("Ask and Brief remain usable at approved widths and in both themes", async ({ page }) => {
  await signIn(page);
  for (const route of ["/ask-the-business", "/management-brief"]) {
    for (const width of [375, 768, 1280]) {
      await page.setViewportSize({ width, height: 900 });
      await page.goto(route);
      await expect(page.locator("h1")).toBeVisible();
      const open = page.getByRole("button", { name: "Open navigation menu" });
      if (await open.isVisible()) await open.click();
      const dark = page.getByRole("button", { name: "Dark mode" });
      if (await dark.isVisible()) await dark.click();
      await expect(page.locator(".app-shell")).toHaveCSS("background-color", "rgb(15, 23, 42)");
      const dimensions = await page.evaluate(() => ({ scroll: document.documentElement.scrollWidth, inner: window.innerWidth }));
      expect(dimensions.scroll).toBeLessThanOrEqual(dimensions.inner);
    }
  }
});
