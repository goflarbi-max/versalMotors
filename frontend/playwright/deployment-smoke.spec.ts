import { expect, Page, test } from "@playwright/test";

async function signIn(page: Page) {
  await page.goto("/login");
  await page.getByLabel("Email Address").fill(process.env.SMOKE_EMAIL ?? "demo@versalmotors.com");
  await page.getByLabel("Password", { exact: true }).fill(process.env.SMOKE_PASSWORD ?? "VersalDemo2026!");
  await page.getByRole("button", { name: "Sign In" }).click();
  await expect(page).toHaveURL(/\/overview(?:\?.*)?$/);
}

test("same-origin API proxy and browser security headers are healthy", async ({ page }) => {
  const response = await page.goto("/");
  expect(response?.ok()).toBeTruthy();
  expect(response?.headers()["x-content-type-options"]).toBe("nosniff");
  expect(response?.headers()["x-frame-options"]).toBe("DENY");
  expect(response?.headers()["content-security-policy"]).toContain("frame-ancestors 'none'");

  const proxiedApi = await page.request.get("/api/v1/auth/csrf");
  expect(proxiedApi.ok()).toBeTruthy();
  expect((await proxiedApi.json()).csrf_token).toBeTruthy();
});

for (const viewport of [{ name: "mobile", width: 375, height: 800 }, { name: "desktop", width: 1280, height: 800 }]) {
  test(`${viewport.name} deployment smoke reaches every protected page`, async ({ page }) => {
    await page.setViewportSize({ width: viewport.width, height: viewport.height });
    await signIn(page);
    for (const [label, path] of [
      ["Overview", "/overview"],
      ["Investigate", "/investigate"],
      ["Ask the Business", "/ask-the-business"],
      ["Management Brief", "/management-brief"],
      ["Data Quality", "/data-quality"],
    ] as const) {
      await page.goto(path);
      await expect(page).toHaveURL(new RegExp(`${path}(?:\\?.*)?$`));
      await expect(page.getByRole("link", { name: label })).toHaveAttribute("aria-current", "page");
      const dimensions = await page.evaluate(() => ({ scroll: document.documentElement.scrollWidth, inner: window.innerWidth }));
      expect(dimensions.scroll).toBeLessThanOrEqual(dimensions.inner);
    }
  });
}
