import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.route("**/api/auth/demo/citizen", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        access_token: "browser-test-token",
        user: { name: "Demo Citizen", role: "citizen" },
      }),
    });
  });
  await page.route("**/api/complaints", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ cases: [], disclaimer: "Not a government service or legal advice." }),
    });
  });
});

test("presents the demo boundary and primary navigation", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { level: 1 })).toHaveText(
    "Your cases, clearly organized.",
  );
  await expect(page.getByText("Not a government service or legal advice.")).toBeVisible();
  await expect(page.getByText("Demo mode")).toBeVisible();

  await page.getByRole("link", { name: "Find an agency" }).click();
  await expect(page).toHaveURL(/\/directory$/);
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
});

test("supports keyboard navigation to the agency directory", async ({ page }) => {
  await page.goto("/");

  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: "Skip to main content" })).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: "Citizen Karen home" }).first()).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: "Command Center" })).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: "Find an agency" })).toBeFocused();
  await page.keyboard.press("Enter");

  await expect(page).toHaveURL(/\/directory$/);
});
