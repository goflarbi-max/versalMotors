import { expect, Page, test } from "@playwright/test";

async function signIn(page: Page) {
  await page.goto("/login");
  await page.getByLabel("Email Address").fill("demo@versalmotors.com");
  await page.getByLabel("Password", { exact: true }).fill("VersalDemo2026!");
  await page.getByRole("button", { name: "Sign In" }).click();
  await expect(page).toHaveURL(/\/overview(?:\?.*)?$/);
}

test("landing and login preserve the approved public flow", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Analyze Your Data with Precision" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Sign in" })).toBeVisible();
  await expect(page.getByText("Pricing")).toHaveCount(0);
  await expect(page.getByText("Features", { exact: true })).toHaveCount(0);
  await page.getByRole("link", { name: "Sign in" }).click();
  await expect(page).toHaveURL(/\/login$/);
  await expect(page.getByRole("heading", { name: "VersalMotors Business Intelligence" })).toBeVisible();
});

for (const path of ["overview", "investigate", "ask-the-business", "management-brief", "data-quality"]) {
  test(`signed-out direct /${path} access redirects to login`, async ({ page }) => {
    await page.goto(`/${path}`);
    await expect(page).toHaveURL(new RegExp(`/login\\?next=%2F${path}$`));
  });
}

test("login locks the same session after five failed attempts", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Email Address").fill(`lockout-${Date.now()}@example.com`);
  await page.getByLabel("Password", { exact: true }).fill("incorrect-password");
  for (let attempt = 1; attempt <= 5; attempt += 1) {
    await page.getByRole("button", { name: "Sign In" }).click();
    if (attempt < 5) await expect(page.getByRole("status")).toHaveText("Invalid email or password");
  }
  await expect(page.getByRole("status")).toContainText("Too many failed attempts. Try again in 60 seconds.");
});

test("login rewrite preserves the backend session cookie and protects the shell", async ({ page }) => {
  await signIn(page);
  await expect(page.getByText("demo@versalmotors.com")).toBeVisible();
  await expect(page.getByRole("link", { name: "Overview" })).toHaveAttribute("aria-current", "page");
  await page.goto("/");
  await page.getByRole("link", { name: "Sign in" }).click();
  await expect(page).toHaveURL(/\/overview(?:\?.*)?$/);
});

test("desktop hamburger, theme, navigation, and sign out retain behavior", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 800 });
  await signIn(page);
  const menu = page.getByRole("button", { name: "Close navigation menu" });
  await expect(menu).toHaveAttribute("aria-expanded", "true");
  await menu.click();
  await expect(page.getByRole("button", { name: "Open navigation menu" })).toHaveAttribute("aria-expanded", "false");
  await page.getByRole("button", { name: "Open navigation menu" }).click();
  await page.getByRole("button", { name: "Dark mode" }).click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await page.getByRole("link", { name: "Investigate" }).click();
  await expect(page).toHaveURL(/\/investigate(?:\?.*)?$/);
  await expect(page.getByRole("link", { name: "Investigate" })).toHaveAttribute("aria-current", "page");
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await page.getByRole("button", { name: "Sign out" }).click();
  await expect(page).toHaveURL(/\/login$/);
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
});

test("mobile drawer starts closed and closes after navigation", async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 780 });
  await signIn(page);
  await expect(page.getByRole("button", { name: "Open navigation menu" })).toBeVisible();
  await page.getByRole("button", { name: "Open navigation menu" }).click();
  await expect(page.getByRole("button", { name: "Close navigation menu" })).toBeVisible();
  await page.getByRole("link", { name: "Data Quality" }).click();
  await expect(page).toHaveURL(/\/data-quality(?:\?.*)?$/);
  await expect(page.getByRole("button", { name: "Open navigation menu" })).toBeVisible();
});

test("tablet keeps the sidebar open and every protected destination updates its active item", async ({ page }) => {
  await page.setViewportSize({ width: 768, height: 900 });
  await signIn(page);
  await expect(page.getByRole("button", { name: "Close navigation menu" })).toBeVisible();
  const destinations = [
    ["Investigate", "/investigate"],
    ["Ask the Business", "/ask-the-business"],
    ["Management Brief", "/management-brief"],
    ["Data Quality", "/data-quality"],
    ["Overview", "/overview"],
  ] as const;
  for (const [label, path] of destinations) {
    await page.getByRole("link", { name: label }).click();
    await expect(page).toHaveURL(new RegExp(`${path}(?:\\?.*)?$`));
    await expect(page.getByRole("link", { name: label })).toHaveAttribute("aria-current", "page");
  }
  const dimensions = await page.evaluate(() => ({ scroll: document.documentElement.scrollWidth, inner: window.innerWidth }));
  expect(dimensions.scroll).toBeLessThanOrEqual(dimensions.inner);
});

test("business filters appear only on Overview and Investigate", async ({ page }) => {
  await signIn(page);
  for (const path of ["/overview", "/investigate"]) {
    await page.goto(path);
    await expect(page.getByRole("region", { name: "Business filters" })).toBeVisible();
  }
  for (const path of ["/ask-the-business", "/management-brief", "/data-quality"]) {
    await page.goto(path);
    await expect(page.getByRole("region", { name: "Business filters" })).toHaveCount(0);
  }
});

test("responsive public pages do not create page-level horizontal scrolling", async ({ page }) => {
  for (const width of [375, 768, 1280]) {
    await page.setViewportSize({ width, height: 800 });
    for (const path of ["/", "/login"]) {
      await page.goto(path);
      const dimensions = await page.evaluate(() => ({ scroll: document.documentElement.scrollWidth, inner: window.innerWidth }));
      expect(dimensions.scroll).toBeLessThanOrEqual(dimensions.inner);
    }
  }
});

test("protected light and dark shells remain readable at all approved widths", async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 800 });
  await signIn(page);
  for (const width of [375, 768, 1280]) {
    await page.setViewportSize({ width, height: 800 });
    const openButton = page.getByRole("button", { name: "Open navigation menu" });
    if (await openButton.isVisible()) await openButton.click();
    const lightButton = page.getByRole("button", { name: "Light mode" });
    if (await lightButton.isVisible()) await lightButton.click();
    await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
    await page.getByRole("button", { name: "Dark mode" }).click();
    await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
    await expect(page.locator("body")).toHaveCSS("background-color", "rgb(15, 23, 42)");
    const dimensions = await page.evaluate(() => ({ scroll: document.documentElement.scrollWidth, inner: window.innerWidth }));
    expect(dimensions.scroll).toBeLessThanOrEqual(dimensions.inner);
  }
});

test("landing and login retain their fixed designs when stored app theme is dark", async ({ page }) => {
  await page.goto("/");
  await page.evaluate(() => {
    localStorage.setItem("versal_theme", "dark");
    document.cookie = "versal_theme=dark; Path=/; SameSite=Lax";
  });
  await page.reload();
  await expect(page.locator(".landing-hero")).toHaveCSS("background-image", /linear-gradient/);
  await page.goto("/login");
  await expect(page.locator(".login-page")).toHaveCSS("background-color", "rgb(248, 250, 252)");
});

test.use({ reducedMotion: "reduce" });
test("reduced motion leaves landing content visible without animation", async ({ page }) => {
  await page.goto("/");
  const heading = page.getByRole("heading", { name: "Analyze Your Data with Precision" });
  await expect(heading).toBeVisible();
  await expect(heading).toHaveCSS("animation-name", "none");
});
