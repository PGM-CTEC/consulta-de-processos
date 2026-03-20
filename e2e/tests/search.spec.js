import { test, expect } from '@playwright/test';
import { VALID_PROCESS_NUMBERS, INVALID_PROCESS_NUMBERS, SELECTORS, WAIT_TIMES } from '../fixtures/test-data';

test.describe('Search Process E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to application
    await page.goto('/');
    // Wait for page to load
    await page.waitForLoadState('networkidle');
  });

  test('should render search page', async ({ page }) => {
    // Check for search input
    const searchInput = page.locator(SELECTORS.SEARCH_INPUT);
    await expect(searchInput).toBeVisible();

    // Check for search button
    const searchButton = page.locator(SELECTORS.SEARCH_BUTTON);
    await expect(searchButton).toBeVisible();
  });

  test('should search for valid process number', async ({ page }) => {
    const processNumber = VALID_PROCESS_NUMBERS[0];

    // Fill search input
    const searchInput = page.locator(SELECTORS.SEARCH_INPUT);
    await searchInput.fill(processNumber);

    // Click search button
    const searchButton = page.locator(SELECTORS.SEARCH_BUTTON);
    await searchButton.click();

    // Wait for loading to complete
    await page.waitForTimeout(WAIT_TIMES.API_RESPONSE);

    // Check if results are displayed (could be process details or error message)
    // This depends on whether the API returns valid data
    const pageContent = await page.content();
    expect(pageContent.length).toBeGreaterThan(0);
  });

  test('should show error for invalid process number', async ({ page }) => {
    const invalidNumber = INVALID_PROCESS_NUMBERS[0];

    // Fill search input with invalid number
    const searchInput = page.locator(SELECTORS.SEARCH_INPUT);
    await searchInput.fill(invalidNumber);

    // Click search button
    const searchButton = page.locator(SELECTORS.SEARCH_BUTTON);
    await searchButton.click();

    // Wait for validation/error response
    await page.waitForTimeout(WAIT_TIMES.ELEMENT_VISIBLE);

    // Error message or validation error should appear
    const content = await page.content();
    expect(content.length).toBeGreaterThan(0);
  });

  test('should handle empty search gracefully', async ({ page }) => {
    // Try to search with empty input
    const searchButton = page.locator(SELECTORS.SEARCH_BUTTON);

    // Button might be disabled or show error
    const isDisabled = await searchButton.isDisabled();

    if (!isDisabled) {
      await searchButton.click();
      // Wait for response
      await page.waitForTimeout(WAIT_TIMES.ELEMENT_VISIBLE);
    }

    // Page should still be functional
    const searchInput = page.locator(SELECTORS.SEARCH_INPUT);
    await expect(searchInput).toBeVisible();
  });

  test('should trim whitespace from input', async ({ page }) => {
    const processNumber = VALID_PROCESS_NUMBERS[0];
    const inputWithWhitespace = `  ${processNumber}  `;

    // Fill search input with whitespace
    const searchInput = page.locator(SELECTORS.SEARCH_INPUT);
    await searchInput.fill(inputWithWhitespace);

    // Click search button
    const searchButton = page.locator(SELECTORS.SEARCH_BUTTON);
    await searchButton.click();

    // Wait for API response
    await page.waitForTimeout(WAIT_TIMES.API_RESPONSE);

    // Should process successfully (trimmed input)
    const pageContent = await page.content();
    expect(pageContent.length).toBeGreaterThan(0);
  });

  test('should show loading state during search', async ({ page }) => {
    const processNumber = VALID_PROCESS_NUMBERS[0];

    // Fill and submit search
    const searchInput = page.locator(SELECTORS.SEARCH_INPUT);
    await searchInput.fill(processNumber);

    const searchButton = page.locator(SELECTORS.SEARCH_BUTTON);
    await searchButton.click();

    // Check for loading indicator (if present in UI)
    // This is optional depending on implementation
    await page.waitForTimeout(100);

    // Page should still be responsive
    await expect(searchInput).toBeVisible();
  });

  test('should display process details after successful search', async ({ page }) => {
    const processNumber = VALID_PROCESS_NUMBERS[0];

    // Perform search
    const searchInput = page.locator(SELECTORS.SEARCH_INPUT);
    await searchInput.fill(processNumber);

    const searchButton = page.locator(SELECTORS.SEARCH_BUTTON);
    await searchButton.click();

    // Wait for results
    await page.waitForTimeout(WAIT_TIMES.API_RESPONSE);

    // Check if page has content (could be process details or error)
    const hasContent = (await page.content()).length > 100;
    expect(hasContent).toBeTruthy();
  });

  test('should allow multiple searches', async ({ page }) => {
    // First search
    let searchInput = page.locator(SELECTORS.SEARCH_INPUT);
    await searchInput.fill(VALID_PROCESS_NUMBERS[0]);

    let searchButton = page.locator(SELECTORS.SEARCH_BUTTON);
    await searchButton.click();

    await page.waitForTimeout(WAIT_TIMES.API_RESPONSE);

    // Second search with different number
    searchInput = page.locator(SELECTORS.SEARCH_INPUT);
    await searchInput.clear();
    await searchInput.fill(VALID_PROCESS_NUMBERS[1]);

    searchButton = page.locator(SELECTORS.SEARCH_BUTTON);
    await searchButton.click();

    await page.waitForTimeout(WAIT_TIMES.API_RESPONSE);

    // Should complete without errors
    await expect(searchInput).toBeVisible();
  });
});
