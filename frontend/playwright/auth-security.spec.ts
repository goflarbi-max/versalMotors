import { expect, test } from "@playwright/test";

test("login is accessible and safe return paths stay same-site", async ({ page }) => {
  await page.goto("/login?next=https://evil.example/steal");
  await expect(page.getByLabel("Email Address")).toHaveAttribute("autocomplete", "username");
  await expect(page.getByLabel("Password", { exact: true })).toHaveAttribute("autocomplete", "current-password");
  await page.getByLabel("Email Address").fill("  DEMO@VERSALMOTORS.COM  ");
  await page.getByLabel("Password", { exact: true }).fill("VersalDemo2026!");
  await page.getByLabel("Password", { exact: true }).press("Enter");
  await expect(page).toHaveURL(/\/overview$/);
});

test("login controls preserve entered email and expose password safely", async ({ page }) => {
  await page.goto("/login");
  const email = page.getByLabel("Email Address");
  const password = page.getByLabel("Password", { exact: true });
  await email.fill("demo@versalmotors.com");
  await password.fill("wrong-password");
  await page.getByRole("button", { name: "Show password" }).click();
  await expect(password).toHaveAttribute("type", "text");
  await page.getByRole("button", { name: "Sign In" }).click();
  await expect(page.locator(".login-message")).toHaveText("Invalid email or password");
  await expect(email).toHaveValue("demo@versalmotors.com");
  await page.getByRole("button", { name: "Forgot Password?" }).click();
  await expect(page.locator(".login-message")).toHaveText("Please contact the system administrator to reset your password.");
});

test("session cookie is HTTP-only and login stays light and responsive", async ({ page, context }) => {
  await page.emulateMedia({ colorScheme: "dark" });
  for (const width of [375, 768, 1280]) {
    await page.setViewportSize({ width, height: 900 });
    await page.goto("/login");
    await expect(page.locator(".login-page")).toHaveCSS("background-color", "rgb(248, 250, 252)");
    const dimensions = await page.evaluate(() => ({ inner: window.innerWidth, scroll: document.documentElement.scrollWidth }));
    expect(dimensions.scroll).toBeLessThanOrEqual(dimensions.inner);
  }

  await page.getByLabel("Email Address").fill("demo@versalmotors.com");
  await page.getByLabel("Password", { exact: true }).fill("VersalDemo2026!");
  await page.getByLabel("Remember me").check();
  await page.getByRole("button", { name: "Sign In" }).click();
  await expect(page).toHaveURL(/\/overview$/);
  const session = (await context.cookies()).find((cookie) => cookie.name === "versal_session");
  expect(session?.httpOnly).toBe(true);
  expect(session?.sameSite).toBe("Lax");
  expect(session?.expires ?? 0).toBeGreaterThan(Date.now() / 1000 + 29 * 24 * 3600);
  expect(await page.evaluate(() => document.cookie)).not.toContain("versal_session");
});

test("login posts safely when JavaScript has not hydrated", async ({ browser }) => {
  const context = await browser.newContext({ javaScriptEnabled: false });
  const page = await context.newPage();
  await page.goto("/login");
  await page.getByLabel("Email Address").fill("demo@versalmotors.com");
  await page.getByLabel("Password", { exact: true }).fill("VersalDemo2026!");
  await Promise.all([
    page.waitForURL(/\/overview$/, { waitUntil: "commit" }),
    page.locator("form").evaluate((form: HTMLFormElement) => form.requestSubmit()),
  ]);
  expect(page.url()).not.toContain("VersalDemo2026");
  await context.close();
});
