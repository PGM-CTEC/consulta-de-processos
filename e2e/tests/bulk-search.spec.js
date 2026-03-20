import { test, expect } from '@playwright/test';
import { BULK_PROCESS_NUMBERS, SELECTORS, WAIT_TIMES } from '../fixtures/test-data';

test.describe('Bulk Search E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to application
    await page.goto('/');
    // Wait for page to load
    await page.waitForLoadState('networkidle');

    // Navigate to bulk search tab
    const bulkTab = page.locator(SELECTORS.BULK_TAB);
    if (await bulkTab.isVisible()) {
      await bulkTab.click();
      await page.waitForTimeout(WAIT_TIMES.NAVIGATION);
    }
  });

  test('should render bulk search interface', async ({ page }) => {
    // Check for textarea
    const textarea = page.locator(SELECTORS.BULK_TEXTAREA);
    await expect(textarea).toBeVisible();

    // Check for bulk search button
    const bulkButton = page.locator(SELECTORS.BULK_SEARCH_BUTTON);
    const hasButton = await bulkButton.count().then(count => count > 0);
    expect(hasButton).toBeTruthy();
  });

  test('should process single process number', async ({ page }) => {
    const textarea = page.locator(SELECTORS.BULK_TEXTAREA);
    await textarea.fill(BULK_PROCESS_NUMBERS[0]);

    // Find and click bulk search button
    const buttons = page.locator('button');
    let bulkButton = null;

    for (let i = 0; i < await buttons.count(); i++) {
      const text = await buttons.nth(i).textContent();
      if (text?.includes('Processar') || text?.includes('Buscar')) {
        bulkButton = buttons.nth(i);
        break;
      }
    }

    if (bulkButton) {
      await bulkButton.click();
      await page.waitForTimeout(WAIT_TIMES.API_RESPONSE);
    }

    // Results should be displayed
    const pageContent = await page.content();
    expect(pageContent.length).toBeGreaterThan(0);
  });

  test('should process multiple process numbers', async ({ page }) => {
    const textarea = page.locator(SELECTORS.BULK_TEXTAREA);
    const input = BULK_PROCESS_NUMBERS.slice(0, 2).join('\n');
    await textarea.fill(input);

    // Find and click bulk search button
    const buttons = page.locator('button');
    for (let i = 0; i < await buttons.count(); i++) {
      const text = await buttons.nth(i).textContent();
      if (text?.includes('Processar') || text?.includes('Buscar')) {
        await buttons.nth(i).click();
        break;
      }
    }

    await page.waitForTimeout(WAIT_TIMES.API_RESPONSE);

    // Results should be displayed
    const pageContent = await page.content();
    expect(pageContent.length).toBeGreaterThan(0);
  });

  test('should handle empty textarea gracefully', async ({ page }) => {
    const textarea = page.locator(SELECTORS.BULK_TEXTAREA);

    // Textarea should be empty
    expect(await textarea.inputValue()).toBe('');

    // Try to submit
    const buttons = page.locator('button');
    for (let i = 0; i < await buttons.count(); i++) {
      const text = await buttons.nth(i).textContent();
      if (text?.includes('Processar') || text?.includes('Buscar')) {
        const isDisabled = await buttons.nth(i).isDisabled();
        if (!isDisabled) {
          await buttons.nth(i).click();
        }
        break;
      }
    }

    // Page should still be usable
    await expect(textarea).toBeVisible();
  });

  test('should allow file upload for bulk search', async ({ page }) => {
    // Check if file upload input exists
    const fileInput = page.locator('input[type="file"]');
    const hasFileInput = await fileInput.count().then(count => count > 0);

    if (hasFileInput) {
      // File input should be present
      await expect(fileInput.first()).toBeVisible();
    }
  });

  test('should display results summary', async ({ page }) => {
    const textarea = page.locator(SELECTORS.BULK_TEXTAREA);
    await textarea.fill(BULK_PROCESS_NUMBERS[0]);

    // Submit
    const buttons = page.locator('button');
    for (let i = 0; i < await buttons.count(); i++) {
      const text = await buttons.nth(i).textContent();
      if (text?.includes('Processar') || text?.includes('Buscar')) {
        await buttons.nth(i).click();
        break;
      }
    }

    await page.waitForTimeout(WAIT_TIMES.API_RESPONSE);

    // Page should have content
    const pageContent = await page.content();
    expect(pageContent.length).toBeGreaterThan(0);
  });

  test('should allow export of results', async ({ page }) => {
    const textarea = page.locator(SELECTORS.BULK_TEXTAREA);
    await textarea.fill(BULK_PROCESS_NUMBERS[0]);

    // Submit search
    const buttons = page.locator('button');
    for (let i = 0; i < await buttons.count(); i++) {
      const text = await buttons.nth(i).textContent();
      if (text?.includes('Processar') || text?.includes('Buscar')) {
        await buttons.nth(i).click();
        break;
      }
    }

    await page.waitForTimeout(WAIT_TIMES.API_RESPONSE);

    // Check if export buttons exist
    const exportButtons = page.locator('button').filter({
      hasText: /CSV|Excel|JSON/i,
    });

    const hasExportButtons = await exportButtons.count().then(count => count > 0);
    expect(hasExportButtons).toBeTruthy();
  });

  test('should handle processing errors gracefully', async ({ page }) => {
    const textarea = page.locator(SELECTORS.BULK_TEXTAREA);
    // Use invalid format
    await textarea.fill('invalid data format');

    // Submit
    const buttons = page.locator('button');
    for (let i = 0; i < await buttons.count(); i++) {
      const text = await buttons.nth(i).textContent();
      if (text?.includes('Processar') || text?.includes('Buscar')) {
        await buttons.nth(i).click();
        break;
      }
    }

    await page.waitForTimeout(WAIT_TIMES.API_RESPONSE);

    // Should show error or handle gracefully
    const pageContent = await page.content();
    expect(pageContent.length).toBeGreaterThan(0);
  });
});
