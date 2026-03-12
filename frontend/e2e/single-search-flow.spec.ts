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

const FAKE_PROCESS = {
    number: '0001745-64.1989.8.19.0002',
    subject: 'Ação de Teste Processual',
    class_nature: 'Ação Ordinária',
    court: 'TJRJ - 1ª Vara Cível',
    distribution_date: '1989-01-01T00:00:00',
    phase: 'Conhecimento',
    phase_source: 'fusion',
    movements: [
        { id: 1, description: 'Distribuição do processo', code: '1', date: '1989-01-01T00:00:00' },
        { id: 2, description: 'Despacho inicial', code: '11010', date: '1989-02-01T00:00:00' },
    ],
    fusion_movements: [],
    raw_data: { number: '0001745-64.1989.8.19.0002' },
};

test.describe('Single Process Search Flow', () => {
    test('should search for a process, view details, and export JSON', async ({ page }) => {
        // Mock API to return fake process data
        await page.route(/\/processes\//, async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify(FAKE_PROCESS),
            });
        });

        // Navigate to the application
        await page.goto('/');

        // Verify we're on the home page
        await expect(page).toHaveTitle(/Consulta de Processos/);

        // Fill in the CNJ process number
        const searchInput = page.locator('#process-number-input');
        await searchInput.fill('0001745-64.1989.8.19.0002');

        // Click the search button
        const searchButton = page.locator('button').filter({ hasText: /Consultar/i }).first();
        await searchButton.click();

        // Wait for process details card to be visible
        const processCard = page.locator('article').first();
        await expect(processCard).toBeVisible({ timeout: 15000 });

        // Verify process number is shown
        await expect(page.locator('#process-title')).toContainText('0001745', { timeout: 5000 });

        // Verify movements heading is visible
        await expect(page.locator('#movements-heading')).toBeVisible({ timeout: 5000 });

        // Export to JSON (button with download icon inside the card header)
        const exportButton = page.locator('button').filter({ hasText: /Exportar|Export/i }).first();

        if (await exportButton.isVisible()) {
            await exportButton.click();
            await page.waitForTimeout(500);

            const jsonOption = page.locator('text=JSON').first();
            const downloadPromise = page.waitForEvent('download', { timeout: 5000 });
            await jsonOption.click();

            const download = await downloadPromise;
            expect(download.suggestedFilename()).toContain('.json');
        }
    });

    test('should handle invalid process number gracefully', async ({ page }) => {
        // Mock API to return 404 for invalid/not-found process
        await page.route(/\/processes\//, async (route) => {
            await route.fulfill({
                status: 404,
                contentType: 'application/json',
                body: JSON.stringify({ detail: 'Processo não encontrado' }),
            });
        });

        await page.goto('/');

        // Fill invalid CNJ number (wrong check digit — format is valid so form submits)
        const searchInput = page.locator('#process-number-input');
        await searchInput.fill('0001745-99.1989.8.19.0002');

        // Click search
        const searchButton = page.locator('button').filter({ hasText: /Consultar/i }).first();
        await searchButton.click();

        // Should show error message (toast from handleSearch catch block)
        await expect(page.locator('text=/inválido|erro|error|encontrado/i').first()).toBeVisible({ timeout: 8000 });
    });

    test('should handle API errors gracefully', async ({ page }) => {
        // Mock API to return 500 error
        await page.route(/\/processes\//, async (route) => {
            await route.fulfill({
                status: 500,
                contentType: 'application/json',
                body: JSON.stringify({ detail: 'Internal Server Error' }),
            });
        });

        await page.goto('/');

        const searchInput = page.locator('#process-number-input');
        await searchInput.fill('0001745-64.1989.8.19.0002');

        const searchButton = page.locator('button').filter({ hasText: /Consultar/i }).first();
        await searchButton.click();

        // Should show error message (toast)
        await expect(page.locator('text=/erro|error|falha/i').first()).toBeVisible({ timeout: 8000 });
    });
});
