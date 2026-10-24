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

test("browser traffic stays same-origin and rendered pages contain no Streamlit branding", async ({ page }) => {
  const foreignRequests: string[] = [];
  const sensitiveRequests: string[] = [];
  const sensitiveNames = /GEMINI_API_KEY|VERSALMOTORS_SESSION_SECRET|VERSALMOTORS_AUTH_USERS_JSON/i;
  page.on("request", (request) => {
    const url = new URL(request.url());
    if (url.protocol === "http:" || url.protocol === "https:") {
      const expectedOrigin = new URL(process.env.PLAYWRIGHT_BASE_URL ?? "http://127.0.0.1:3000").origin;
      if (url.origin !== expectedOrigin) foreignRequests.push(request.url());
    }
    if (sensitiveNames.test(`${request.url()} ${request.postData() ?? ""}`)) sensitiveRequests.push(request.url());
  });

  await signIn(page);
  for (const path of ["/overview", "/investigate", "/ask-the-business", "/management-brief", "/data-quality"]) {
    await page.goto(path);
    await expect(page.locator("body")).not.toContainText(/streamlit/i);
  }
  expect(foreignRequests).toEqual([]);
  expect(sensitiveRequests).toEqual([]);
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
