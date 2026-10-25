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
});
