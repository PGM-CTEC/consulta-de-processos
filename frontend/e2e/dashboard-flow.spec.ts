/**
 * E2E Test: Dashboard Analytics Flow
 * Story: STORY-REM-018 - E2E Tests with Playwright
 *
 * Test Coverage:
 * - View dashboard with charts
 * - Verify statistics display
 * - Filter by tribunal
 * - Verify chart updates after filtering
 */

import { test, expect } from '@playwright/test';

test.describe('Dashboard Analytics Flow', () => {
    test('should display dashboard with all charts and statistics', async ({ page }) => {
        await page.goto('/');

        // Navigate to Dashboard tab
        const dashboardTab = page.locator('text=/Dashboard|Painel|Analytics/i').first();
        await dashboardTab.click();

        // Wait for dashboard to load
        await page.waitForLoadState('networkidle');

        // Verify statistics cards are visible
        // Looking for total processes count
        await expect(page.locator('text=/Total de Processos|Processos Cadastrados/i')).toBeVisible({
            timeout: 5000,
        });

        // Verify movements count
        await expect(page.locator('text=/Total de Movimentações|Movimentações/i')).toBeVisible({
            timeout: 5000,
        });

        // Verify charts are visible
        // Dashboard typically shows: Processes by Tribunal, Processes by Phase
        const charts = page.locator('canvas, svg[class*="recharts"], [role="img"]');
        const chartCount = await charts.count();
        expect(chartCount).toBeGreaterThan(0);

        // Verify we have data (not empty state)
        await expect(page.locator('text=/Nenhum dado|Sem dados|No data/i')).not.toBeVisible();
    });

    test('should filter dashboard by tribunal', async ({ page }) => {
        await page.goto('/');

        // Navigate to Dashboard
        const dashboardTab = page.locator('text=/Dashboard|Painel|Analytics/i').first();
        await dashboardTab.click();

        await page.waitForLoadState('networkidle');

        // Look for tribunal filter (could be dropdown, buttons, or filter section)
        const tribunalFilter = page.locator('select, button').filter({
            hasText: /Tribunal|TJ|TRF|Filtrar/i,
        }).first();

        if (await tribunalFilter.isVisible()) {
            // Get initial process count
            const initialCountText = await page.locator('text=/Total de Processos|Processos/i').first().textContent();

            // Click on a specific tribunal filter
            // Try to find TJRJ, TJSP, or any tribunal option
            const tribunalOption = page.locator('text=/TJRJ|TJSP|TRF/i').first();

            if (await tribunalOption.isVisible()) {
                await tribunalOption.click();

                // Wait for dashboard to update
                await page.waitForTimeout(1000);

                // Verify count changed or filter is applied
                const newCountText = await page.locator('text=/Total de Processos|Processos/i').first().textContent();

                // Either count changed or a filter indicator is visible
                const filterIndicatorVisible = await page.locator('text=/Filtrado|Filtered|TJ/i').isVisible();

                expect(initialCountText !== newCountText || filterIndicatorVisible).toBe(true);
            }
        }
    });

    test('should display phase distribution chart', async ({ page }) => {
        await page.goto('/');

        const dashboardTab = page.locator('text=/Dashboard|Painel|Analytics/i').first();
        await dashboardTab.click();

        await page.waitForLoadState('networkidle');

        // Verify phase-related content is visible
        // Dashboard shows phases like "Conhecimento", "Execução", etc.
        await expect(page.locator('text=/Fases|Processuais|Conhecimento|Execução/i').first()).toBeVisible({
            timeout: 5000,
        });

        // Verify chart/visualization exists for phases
        const chartContainer = page.locator('[class*="chart"], canvas, svg').first();
        await expect(chartContainer).toBeVisible();
    });

    test('should display tribunal distribution', async ({ page }) => {
        await page.goto('/');

        const dashboardTab = page.locator('text=/Dashboard|Painel|Analytics/i').first();
        await dashboardTab.click();

        await page.waitForLoadState('networkidle');

        // Verify tribunal distribution section
        await expect(page.locator('text=/Tribunais|Distribuição|Por Tribunal/i').first()).toBeVisible({
            timeout: 5000,
        });

        // Verify we have tribunal names displayed (TJRJ, TJSP, etc.)
        const tribunalNames = page.locator('text=/TJ[A-Z]{2}|TRF\d|TRT\d/');
        const tribunalCount = await tribunalNames.count();

        expect(tribunalCount).toBeGreaterThan(0);
    });

    test('should handle empty dashboard gracefully', async ({ page }) => {
        // Mock API to return empty stats
        await page.route('**/stats**', (route) => {
            route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    total_processes: 0,
                    total_movements: 0,
                    tribunals: [],
                    phases: [],
                }),
            });
        });

        await page.goto('/');

        const dashboardTab = page.locator('text=/Dashboard|Painel|Analytics/i').first();
        await dashboardTab.click();

        await page.waitForLoadState('networkidle');

        // Should show empty state message
        await expect(page.locator('text=/Nenhum dado|Sem dados|No data|vazio/i')).toBeVisible({
            timeout: 5000,
        });

        // Counts should be 0
        await expect(page.locator('text=/0 processos|0 movimentações/i').first()).toBeVisible({
            timeout: 5000,
        });
    });

    test('should handle dashboard API errors gracefully', async ({ page }) => {
        // Mock API to return error
        await page.route('**/stats**', (route) => {
            route.fulfill({
                status: 500,
                contentType: 'application/json',
                body: JSON.stringify({ detail: 'Internal Server Error' }),
            });
        });

        await page.goto('/');

        const dashboardTab = page.locator('text=/Dashboard|Painel|Analytics/i').first();
        await dashboardTab.click();

        await page.waitForLoadState('networkidle');

        // Should show error message
        await expect(page.locator('text=/erro|error|falha/i')).toBeVisible({ timeout: 5000 });
    });

    test('should refresh dashboard data', async ({ page }) => {
        await page.goto('/');

        const dashboardTab = page.locator('text=/Dashboard|Painel|Analytics/i').first();
        await dashboardTab.click();

        await page.waitForLoadState('networkidle');

        // Look for refresh button (if exists)
        const refreshButton = page.locator('button').filter({ hasText: /Atualizar|Refresh|Reload/i }).first();

        if (await refreshButton.isVisible()) {
            await refreshButton.click();

            // Should show loading state briefly
            const loadingIndicator = page.locator('.animate-spin, [role="progressbar"]').first();
            await expect(loadingIndicator).toBeVisible({ timeout: 2000 });

            // Then data should reload
            await page.waitForLoadState('networkidle');

            await expect(page.locator('text=/Total de Processos/i')).toBeVisible();
        }
    });
});
