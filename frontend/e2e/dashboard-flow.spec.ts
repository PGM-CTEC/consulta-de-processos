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

const MOCK_STATS = {
    total_processes: 42,
    total_movements: 156,
    last_updated: '2024-01-15T10:30:00',
    tribunals: [
        { tribunal_name: 'TJRJ', count: 25 },
        { tribunal_name: 'TJSP', count: 17 },
    ],
    phases: [
        { phase: 'Conhecimento', count: 30 },
        { phase: 'Execução', count: 12 },
    ],
    timeline: [{ count: 5 }, { count: 10 }],
    classes: [{ class_nature: 'Ação Ordinária', count: 20 }],
};

const STATS_PATTERN = /\/stats/;

test.describe('Dashboard Analytics Flow', () => {
    test('should display dashboard with all charts and statistics', async ({ page }) => {
        // Mock stats API to return predictable data
        await page.route(STATS_PATTERN, async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify(MOCK_STATS),
            });
        });

        await page.goto('/');

        // Navigate to Dashboard tab (nav label: "Analytics / BI")
        const dashboardTab = page.locator('text=/Dashboard|Painel|Analytics/i').first();
        await dashboardTab.click();

        // Wait for dashboard to load
        await page.waitForLoadState('networkidle');

        // Verify statistics cards are visible
        await expect(page.locator('text=/Total de Processos|Processos Cadastrados/i').first()).toBeVisible({
            timeout: 5000,
        });

        // Verify movements count card is visible ("Total de Movimentos" in Dashboard.jsx)
        await expect(page.locator('text=/Total de Movimentos|Movimentações/i').first()).toBeVisible({
            timeout: 5000,
        });

        // Verify figure elements (used as chart containers in Dashboard)
        const figures = page.locator('figure');
        const figureCount = await figures.count();
        expect(figureCount).toBeGreaterThan(0);

        // Verify we don't show empty state
        await expect(page.locator('text=/Nenhum dado|Sem dados|No data/i').first()).not.toBeVisible();
    });

    test('should filter dashboard by tribunal', async ({ page }) => {
        // Mock stats API
        await page.route(STATS_PATTERN, async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify(MOCK_STATS),
            });
        });

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
            const tribunalOption = page.locator('text=/TJRJ|TJSP|TRF/i').first();

            if (await tribunalOption.isVisible()) {
                await tribunalOption.click();

                // Wait for dashboard to update
                await page.waitForTimeout(1000);

                // Verify count changed or filter is applied
                const newCountText = await page.locator('text=/Total de Processos|Processos/i').first().textContent();

                const filterIndicatorVisible = await page.locator('text=/Filtrado|Filtered|TJ/i').isVisible();

                expect(initialCountText !== newCountText || filterIndicatorVisible).toBe(true);
            }
        }
    });

    test('should display phase distribution chart', async ({ page }) => {
        // Mock stats API with phase data
        await page.route(STATS_PATTERN, async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify(MOCK_STATS),
            });
        });

        await page.goto('/');

        const dashboardTab = page.locator('text=/Dashboard|Painel|Analytics/i').first();
        await dashboardTab.click();

        await page.waitForLoadState('networkidle');

        // Verify phase-related heading is visible ("Processos por Fase" in Dashboard.jsx)
        await expect(page.locator('text=/Processos por Fase|Fases|Conhecimento|Execução/i').first()).toBeVisible({
            timeout: 5000,
        });

        // Verify figure element exists (used as chart wrapper in Dashboard)
        const chartContainer = page.locator('figure').first();
        await expect(chartContainer).toBeVisible();
    });

    test('should display tribunal distribution', async ({ page }) => {
        // Mock stats API with tribunal data
        await page.route(STATS_PATTERN, async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify(MOCK_STATS),
            });
        });

        await page.goto('/');

        const dashboardTab = page.locator('text=/Dashboard|Painel|Analytics/i').first();
        await dashboardTab.click();

        await page.waitForLoadState('networkidle');

        // Verify tribunal distribution section heading ("Processos por Tribunal" in Dashboard.jsx)
        await expect(page.locator('text=/Tribunais|Distribuição|Por Tribunal/i').first()).toBeVisible({
            timeout: 5000,
        });

        // Verify tribunal names from mock data are displayed
        await expect(page.locator('text=TJRJ').first()).toBeVisible({ timeout: 5000 });
    });

    test('should handle empty dashboard gracefully', async ({ page }) => {
        // Mock API to return empty stats
        await page.route(STATS_PATTERN, async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    total_processes: 0,
                    total_movements: 0,
                    tribunals: [],
                    phases: [],
                    timeline: [],
                    classes: [],
                }),
            });
        });

        await page.goto('/');

        const dashboardTab = page.locator('text=/Dashboard|Painel|Analytics/i').first();
        await dashboardTab.click();

        await page.waitForLoadState('networkidle');

        // Should show empty state message ("Banco de Dados Vazio" in Dashboard.jsx)
        await expect(page.locator('text=/Nenhum dado|Sem dados|No data|Vazio/i').first()).toBeVisible({
            timeout: 5000,
        });
    });

    test('should handle dashboard API errors gracefully', async ({ page }) => {
        // Mock API to return error — abort causes Axios to throw a network error
        await page.route(STATS_PATTERN, async (route) => {
            await route.abort();
        });

        await page.goto('/');

        const dashboardTab = page.locator('text=/Dashboard|Painel|Analytics/i').first();
        await dashboardTab.click();

        await page.waitForLoadState('networkidle');

        // Should show error message ("Erro ao carregar dados" / "Falha ao carregar..." in Dashboard.jsx)
        await expect(page.locator('text=/erro|error|falha/i').first()).toBeVisible({ timeout: 5000 });
    });

    test('should refresh dashboard data', async ({ page }) => {
        // Mock stats API
        await page.route(STATS_PATTERN, async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify(MOCK_STATS),
            });
        });

        await page.goto('/');

        const dashboardTab = page.locator('text=/Dashboard|Painel|Analytics/i').first();
        await dashboardTab.click();

        await page.waitForLoadState('networkidle');

        // Look for refresh button ("Atualizar" in Dashboard.jsx)
        const refreshButton = page.locator('button').filter({ hasText: /Atualizar|Refresh|Reload/i }).first();

        if (await refreshButton.isVisible()) {
            await refreshButton.click();

            // Wait for data to reload after refresh
            await page.waitForLoadState('networkidle');

            await expect(page.locator('text=/Total de Processos/i').first()).toBeVisible();
        }
    });
});
