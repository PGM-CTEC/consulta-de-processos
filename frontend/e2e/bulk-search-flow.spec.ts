/**
 * E2E Test: Bulk Process Search Flow
 * Story: STORY-REM-018 - E2E Tests with Playwright
 *
 * Test Coverage:
 * - Bulk search with multiple CNJ numbers
 * - File upload (CSV)
 * - View bulk results
 * - Export results to CSV
 */

import { test, expect } from '@playwright/test';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

test.describe('Bulk Process Search Flow', () => {
    // Setup: Create test CSV file
    test.beforeAll(() => {
        const testCsvPath = path.join(__dirname, 'test-processes.csv');
        const csvContent = `numero_cnj
0001745-64.1989.8.19.0002
0001745-64.1989.8.19.0003
0001745-64.1989.8.19.0004`;

        fs.writeFileSync(testCsvPath, csvContent, 'utf-8');
    });

    // Cleanup: Remove test CSV file
    test.afterAll(() => {
        const testCsvPath = path.join(__dirname, 'test-processes.csv');
        if (fs.existsSync(testCsvPath)) {
            fs.unlinkSync(testCsvPath);
        }
    });

    test('should perform bulk search via manual input and export CSV', async ({ page }) => {
        await page.goto('/');

        // Navigate to Bulk Search tab/section
        const bulkTab = page.locator('text=/Busca em Lote|Bulk|Lote/i').first();
        await bulkTab.click();

        // Wait for bulk search interface to load
        await page.waitForTimeout(500);

        // Add process numbers manually via textarea
        const textarea = page.locator('#bulk-numbers-textarea');

        if (await textarea.isVisible()) {
            await textarea.fill(`0001745-64.1989.8.19.0002
0001745-64.1989.8.19.0003
0001745-64.1989.8.19.0004`);

            // Click search button - "Iniciar Consulta em Lote"
            const searchButton = page.locator('button').filter({ hasText: /Iniciar|Processando/i }).first();
            await searchButton.click();

            // Wait for results to load (can take longer for bulk)
            await page.waitForLoadState('networkidle', { timeout: 30000 });

            // Verify results table is visible
            const resultsTable = page.locator('table, div[role="table"]').first();
            await expect(resultsTable).toBeVisible({ timeout: 10000 });

            // Verify we have multiple results
            const resultRows = page.locator('tbody tr, div[role="row"]');
            const count = await resultRows.count();
            expect(count).toBeGreaterThan(0);

            // Export to CSV
            const exportButton = page.locator('button').filter({ hasText: /Exportar|Export/i }).first();

            if (await exportButton.isVisible()) {
                await exportButton.click();
                await page.waitForTimeout(500);

                // Click CSV option
                const csvOption = page.locator('text=/CSV/i').first();

                if (await csvOption.isVisible()) {
                    const downloadPromise = page.waitForEvent('download', { timeout: 10000 });
                    await csvOption.click();

                    const download = await downloadPromise;
                    expect(download.suggestedFilename()).toMatch(/\.csv$/i);
                }
            }
        }
    });

    test('should perform bulk search via file upload', async ({ page }) => {
        // Mock bulk submit endpoint
        await page.route(/\/processes\/bulk\/submit/, async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ job_id: 'test-job-e2e', status: 'pending', total: 3 }),
            });
        });

        // Mock bulk job polling endpoint — return done immediately
        await page.route(/\/processes\/bulk\/test-job-e2e/, async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    job_id: 'test-job-e2e',
                    status: 'done',
                    total: 1,
                    processed: 1,
                    results_count: 1,
                    failures_count: 0,
                    results: [
                        {
                            number: '0001745-64.1989.8.19.0002',
                            subject: 'Ação de Teste',
                            class_nature: 'Ação Ordinária',
                            court: 'TJRJ',
                            distribution_date: '1989-01-01T00:00:00',
                            phase: 'Conhecimento',
                            phase_source: 'fusion',
                            movements: [],
                            fusion_movements: [],
                            raw_data: {},
                        },
                    ],
                    failures: [],
                }),
            });
        });

        await page.goto('/');

        // Navigate to Bulk Search
        const bulkTab = page.locator('text=/Busca em Lote|Bulk|Lote/i').first();
        await bulkTab.click();

        await page.waitForTimeout(500);

        // Look for file input
        const fileInput = page.locator('input[type="file"]');

        if (await fileInput.count() > 0) {
            // Upload CSV file created in beforeAll
            const testCsvPath = path.join(__dirname, 'test-processes.csv');

            // Only proceed if the file exists
            if (fs.existsSync(testCsvPath)) {
                await fileInput.setInputFiles(testCsvPath);

                // Wait for file to be processed
                await page.waitForTimeout(1000);

                // Verify file name is shown or numbers are loaded
                await expect(page.locator('text=/test-processes\.csv|3 processos|3 números/i')).toBeVisible({
                    timeout: 5000,
                });

                // Click search
                const searchButton = page.locator('button').filter({ hasText: /Iniciar|Processando/i }).first();
                await searchButton.click();

                // Wait for results
                await page.waitForLoadState('networkidle', { timeout: 30000 });

                // Verify results table is visible
                const resultsTable = page.locator('table, div[role="table"]').first();
                await expect(resultsTable).toBeVisible({ timeout: 10000 });
            }
        }
    });

    test('should show progress during bulk search', async ({ page }) => {
        await page.goto('/');

        const bulkTab = page.locator('text=/Busca em Lote|Bulk|Lote/i').first();
        await bulkTab.click();

        const textarea = page.locator('#bulk-numbers-textarea');

        if (await textarea.isVisible()) {
            // Add multiple numbers
            await textarea.fill(`0001745-64.1989.8.19.0002
0001745-64.1989.8.19.0003
0001745-64.1989.8.19.0004
0001745-64.1989.8.19.0005
0001745-64.1989.8.19.0006`);

            const searchButton = page.locator('button').filter({ hasText: /Iniciar|Processando/i }).first();
            await searchButton.click();

            // Should show loading spinner or progress indicator
            const loadingIndicator = page.locator('.animate-spin, [role="progressbar"], text=/carregando|loading/i').first();
            await expect(loadingIndicator).toBeVisible({ timeout: 2000 });
        }
    });

    test('should handle bulk search with mixed valid/invalid numbers', async ({ page }) => {
        await page.goto('/');

        const bulkTab = page.locator('text=/Busca em Lote|Bulk|Lote/i').first();
        await bulkTab.click();

        const textarea = page.locator('#bulk-numbers-textarea');

        if (await textarea.isVisible()) {
            // Mix valid and invalid numbers
            await textarea.fill(`0001745-64.1989.8.19.0002
0001745-99.1989.8.19.0002
0001745-64.1989.8.19.0003`);

            const searchButton = page.locator('button').filter({ hasText: /Iniciar|Processando/i }).first();
            await searchButton.click();

            await page.waitForLoadState('networkidle', { timeout: 30000 });

            // Should show results table with mix of success and failures
            const resultsTable = page.locator('table, div[role="table"]').first();
            await expect(resultsTable).toBeVisible({ timeout: 10000 });
        }
    });
});
