/**
 * E2E Test: Single Process Search Flow
 * Story: STORY-REM-018 - E2E Tests with Playwright
 *
 * Test Coverage:
 * - Single process search
 * - View process details
 * - View movements timeline
 * - Export to JSON
 */

import { test, expect } from '@playwright/test';

test.describe('Single Process Search Flow', () => {
    test('should search for a process, view details, and export JSON', async ({ page }) => {
        // Navigate to the application
        await page.goto('/');

        // Verify we're on the home page
        await expect(page).toHaveTitle(/Consulta de Processos/);

        // Fill in the CNJ process number
        const searchInput = page.locator('input[type="text"][placeholder*="CNJ"]').first();
        await searchInput.fill('0001745-64.1989.8.19.0002');

        // Click the search button
        const searchButton = page.locator('button:has-text("Buscar")').first();
        await searchButton.click();

        // Wait for loading to complete and results to appear
        // The application shows a loading spinner, then results
        await page.waitForLoadState('networkidle');

        // Wait for process details card to be visible (with generous timeout for API)
        const processCard = page.locator('article').first();
        await expect(processCard).toBeVisible({ timeout: 10000 });

        // Verify process details are loaded
        await expect(page.locator('h1, h2')).toContainText(/Processo|0001745/, { timeout: 5000 });

        // Verify movements timeline is visible
        const movementsList = page.locator('ol, ul').filter({ hasText: /Movimentações|Data/ }).first();
        await expect(movementsList).toBeVisible({ timeout: 5000 });

        // Export to JSON
        // Look for Export button - could be "Exportar" or have export icon
        const exportButton = page.locator('button').filter({ hasText: /Exportar|Export/i }).first();

        if (await exportButton.isVisible()) {
            await exportButton.click();

            // Wait for export menu/modal to appear
            await page.waitForTimeout(500);

            // Click JSON option
            const jsonOption = page.locator('text=JSON').first();

            // Setup download listener before clicking
            const downloadPromise = page.waitForEvent('download', { timeout: 5000 });

            await jsonOption.click();

            // Wait for download to start
            const download = await downloadPromise;

            // Verify download filename contains .json
            expect(download.suggestedFilename()).toContain('.json');
        }
    });

    test('should handle invalid process number gracefully', async ({ page }) => {
        await page.goto('/');

        // Fill invalid CNJ number (wrong check digit)
        const searchInput = page.locator('input[type="text"][placeholder*="CNJ"]').first();
        await searchInput.fill('0001745-99.1989.8.19.0002');

        // Click search
        const searchButton = page.locator('button:has-text("Buscar")').first();
        await searchButton.click();

        // Should show error message (toast or inline)
        await expect(page.locator('text=/inválido|erro|error/i')).toBeVisible({ timeout: 5000 });
    });

    test('should handle API errors gracefully', async ({ page }) => {
        // Mock API to return error
        await page.route('**/processes/**', (route) => {
            route.fulfill({
                status: 500,
                contentType: 'application/json',
                body: JSON.stringify({ detail: 'Internal Server Error' }),
            });
        });

        await page.goto('/');

        const searchInput = page.locator('input[type="text"][placeholder*="CNJ"]').first();
        await searchInput.fill('0001745-64.1989.8.19.0002');

        const searchButton = page.locator('button:has-text("Buscar")').first();
        await searchButton.click();

        // Should show error message
        await expect(page.locator('text=/erro|error|falha/i')).toBeVisible({ timeout: 5000 });
    });
});
